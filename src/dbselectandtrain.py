from ase.db import connect
from ase.data import chemical_symbols
from collections import defaultdict
import random
import os
import sqlite3
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


ENERGY = {"H": -1.1121, "He": -0.0090, "Li": -1.9089, "Be": -3.7394, "B": -6.6794, "C": -9.2268, "N": -7.2997, "O": -4.7475, "F": -1.6342, "Ne": -0.0258,
          "Na": -1.3122, "Mg": -1.5969, "Al": -3.7456, "Si": -5.4234, "P": -5.4133, "S": -4.1364, "Cl": -1.8482, "Ar": -0.0688, "K": -1.1104, "Ca": -1.9995,
          "Sc": -6.3325, "Ti": -7.8951, "V": -9.0824, "Cr": -9.6530, "Mn": -9.1617, "Fe": -8.4693, "Co": -7.1083, "Ni": -5.7798, "Cu": -3.5100, "Zn": -1.2595,
          "Ga": -2.9136, "Ge": -4.6175, "As": -4.6585, "Se": -3.4959, "Br": -1.6369, "Kr": -0.0567, "Rb": -0.9805, "Sr": -1.6895, "Y": -6.4661, "Zr": -8.0475,
          "Nb": -10.1013, "Mo": -10.8456, "Tc": -10.3606, "Ru": -9.2744, "Rh": -7.3385, "Pd": -5.1765, "Ag": -2.8325, "Cd": -0.9062, "In": -2.7517, "Sn": -3.9923,
          "Sb": -4.1290, "Te": -3.1433, "I": -1.5240, "Xe": -0.0362, "Cs": -0.8954, "Ba": -1.9190, "La": -4.9360, "Ce": -5.9315, "Pr": -4.7809, "Nd": -4.7681,
          "Pm": -4.7505, "Sm": -4.7177, "Eu": -10.2920, "Gd": -14.0761, "Tb": -4.6344, "Dy": -4.6068, "Ho": -4.5683, "Er": -4.5674, "Tm": -4.4751, "Yb": -1.5396,
          "Lu": -4.5210, "Hf": -9.9572, "Ta": -11.8578, "W": -12.9581, "Re": -12.4445, "Os": -11.2273, "Ir": -8.8384, "Pt": -6.0709, "Au": -3.2739, "Hg": -0.3036,
          "Tl": -2.3617, "Pb": -3.7126, "Bi": -3.8864, "Po": None, "At": None, "Rn": None, "Fr": None, "Ra": None, "Ac": -4.1212, "Th": -7.4139, "Pa": -9.5147,
          "U": -11.2914, "Np": -12.9478, "Pu": -14.2678, "Am": None, "Cm": None, "Bk": None, "Cf": None, "Es": None, "Fm": None, "Md": None, "No": None, "Lr": None, "Rf": None,
          "Db": None, "Sg": None, "Bh": None, "Hs": None, "Mt": None, "Ds": None, "Rg": None, "Cn": None, "Nh": None, "Fl": None, "Mc": None, "Lv": None, "Ts": None, "Og": None}


def get_db_symbols(input_db):
    """返回训练数据库中出现的元素符号。"""
    if str(input_db).endswith(".db"):
        with sqlite3.connect(input_db) as con:
            try:
                rows = con.execute("SELECT DISTINCT Z FROM species ORDER BY Z").fetchall()
            except sqlite3.OperationalError:
                rows = []
        symbols = [chemical_symbols[z] for (z,) in rows if z]
        if symbols:
            missing = [symbol for symbol in symbols if ENERGY.get(symbol) is None]
            if missing:
                raise ValueError(f"Missing reference energies for: {missing}")
            return symbols

    symbols = []
    with connect(input_db) as db:
        for row in db.select():
            for symbol in row.symbols:
                if symbol not in symbols:
                    symbols.append(symbol)
    missing = [symbol for symbol in symbols if ENERGY.get(symbol) is None]
    if missing:
        raise ValueError(f"Missing reference energies for: {missing}")
    return symbols


def get_species_key(row):
    """返回 ASE DB 行对应的元素组成键。"""
    return tuple(sorted(set(row.symbols)))


def make_species_stratified_folds(input_db, k=10, seed=42):
    """按元素组成将数据库行划分为分层 folds。"""
    groups = defaultdict(list)

    if str(input_db).endswith(".db"):
        with sqlite3.connect(input_db) as con:
            try:
                rows = con.execute("""
                    SELECT s.id, GROUP_CONCAT(s.Z, ',') AS zs
                    FROM species s
                    GROUP BY s.id
                    ORDER BY s.id
                """).fetchall()
            except sqlite3.OperationalError:
                rows = []
        if rows:
            for row_id, zs in rows:
                key = tuple(chemical_symbols[int(z)] for z in sorted(map(int, zs.split(","))))
                groups[key].append(row_id)
    if not groups:
        with connect(input_db) as db:
            for row in db.select():
                groups[get_species_key(row)].append(row.id)

    total = sum(len(ids) for ids in groups.values())
    if total == 0:
        raise ValueError(f"No structures found in database: {input_db}")
    if k < 2:
        raise ValueError("number must be at least 2")
    if k > total:
        raise ValueError(f"number ({k}) cannot be larger than dataset size ({total})")

    rng = random.Random(seed)
    folds = [[] for _ in range(k)]

    for key, ids in sorted(groups.items()):
        rng.shuffle(ids)
        if len(ids) < k:
            print(f"Warning: species group {key} has only {len(ids)} structures, fewer than {k} folds")
        for i, row_id in enumerate(ids):
            folds[i % k].append(row_id)

    return folds


def _quote_sql_name(name):
    """安全地引用 SQLite 标识符。"""
    return '"' + name.replace('"', '""') + '"'


def copy_ase_db_rows_fast(input_db, output_db, ids):
    """直接复制 ASE SQLite 行，避免逐行转换为 Atoms。"""
    if os.path.exists(output_db):
        os.remove(output_db)

    # Create the destination ASE schema using ASE itself.
    with connect(output_db) as db:
        db.count()

    with sqlite3.connect(output_db) as con:
        con.execute("PRAGMA journal_mode = OFF")
        con.execute("PRAGMA synchronous = OFF")
        con.execute("PRAGMA temp_store = MEMORY")
        con.execute("ATTACH DATABASE ? AS src", (input_db,))

        src_tables = con.execute("""
            SELECT name, sql
            FROM src.sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """).fetchall()
        dst_tables = {
            name for (name,) in con.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
        }

        for name, sql in src_tables:
            if name not in dst_tables and sql:
                con.execute(sql)

        con.execute("CREATE TEMP TABLE selected_ids(id INTEGER PRIMARY KEY)")
        con.executemany("INSERT INTO selected_ids(id) VALUES (?)",
                        [(int(i),) for i in ids])

        con.execute("DELETE FROM information")
        con.execute("INSERT INTO information SELECT * FROM src.information")

        for name, _ in src_tables:
            if name == "information":
                continue
            qname = _quote_sql_name(name)
            cols = [r[1] for r in con.execute(f"PRAGMA src.table_info({qname})")]
            if name == "systems":
                con.execute(f"INSERT INTO {qname} SELECT * FROM src.{qname} "
                            "WHERE id IN (SELECT id FROM selected_ids)")
            elif "id" in cols:
                con.execute(f"INSERT INTO {qname} SELECT * FROM src.{qname} "
                            "WHERE id IN (SELECT id FROM selected_ids)")

        con.commit()
        con.execute("DETACH DATABASE src")


def db_select_and_train(input_db, out_dir, number=10, seed=42, max_parallel=5,
                        epochs=5000):
    """创建训练/测试 folds 并启动 committee 模型训练。"""
    if epochs <= 0:
        raise ValueError("epochs must be positive")
    symbols = get_db_symbols(input_db)
    ref_engs = [ENERGY[symbol] for symbol in symbols]

    os.makedirs(out_dir, exist_ok=True)
    chunks = make_species_stratified_folds(input_db, k=number, seed=seed)

    for fold_id in range(number):
        work_dir = f"{out_dir}/train-{fold_id}"
        os.makedirs(work_dir, exist_ok=True)
        train_db = f"{work_dir}/train.db"
        test_db = f"{work_dir}/test.db"
        test_ids = chunks[fold_id]
        train_ids = [i for j, block in enumerate(chunks) if j != fold_id for i in block]

        if str(input_db).endswith(".db"):
            copy_ase_db_rows_fast(input_db, test_db, test_ids)
            copy_ase_db_rows_fast(input_db, train_db, train_ids)
        else:
            for path in (test_db, train_db):
                if os.path.exists(path):
                    os.remove(path)
            with connect(input_db) as db_in, connect(test_db) as db_out:
                for i in test_ids:
                    row = db_in.get(id=i)
                    db_out.write(row.toatoms(), key_value_pairs=row.key_value_pairs)

            with connect(input_db) as db_in, connect(train_db) as db_out:
                for i in train_ids:
                    row = db_in.get(id=i)
                    db_out.write(row.toatoms(), key_value_pairs=row.key_value_pairs)

        symbols_groovy = str(symbols)
        ref_engs_groovy = '[' + ', '.join(f'{eng:.4f}D' for eng in ref_engs) + ']'

        trainer = """
import jnn.core.TrainJse
import jse.code.Conf

TrainJse.Conf.THREAD_NUMBER = 8

def train = new TrainJse()

train.trainDbPath = 'train.db'
train.testDbPath = 'test.db'
train.nnpotPath = '__FOLD_ID__.jnn'
train.symbols = __SYMBOLS__
train.refEngs = __REF_ENGS__
train.modelSetting.hidden_dims = [64, 32]
train.basis = [
    type: 'merge',
    basis: [
        [type: 'chebyshev', nmax: 6, rcut: 6],
        [type: 'spherical_chebyshev', nmax: 6, lmax: 6, rcut: 6]
    ]
]
train.nepochs = __EPOCHS__
train.l2Weight = 0

train.run()
"""

        trainer = (trainer
                   .replace("__SYMBOLS__", symbols_groovy)
                   .replace("__REF_ENGS__", ref_engs_groovy)
                   .replace("__FOLD_ID__", str(fold_id))
                   .replace("__EPOCHS__", str(int(epochs))))
        train_path = os.path.join(work_dir, "Trainer.groovy")
        with open(train_path, 'w') as f:
            f.write(trainer.strip())

    def run_train(l):
        """运行一个生成好的 JSE 训练任务。"""
        work_dir = f"{out_dir}/train-{l}"
        command = "jse Trainer.groovy > log 2>&1"
        subprocess.run(command, shell=True, cwd=work_dir, text=True, check=True)
        return l

    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        futures = [executor.submit(run_train, l) for l in range(number)]
        for future in as_completed(futures):
            l = future.result()
            print(f"CuSi-{l}.jnn trained successfully")


if __name__ == "__main__":
    input = f"Au.db"
    outdir = f"Au"
    db_select_and_train(input, outdir)
