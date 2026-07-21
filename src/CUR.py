import argparse
from pathlib import Path

import numpy as np
from ase import Atoms
from ase.db import connect
from ase.io import iread, read, write
from ase.neighborlist import neighbor_list
from scipy.linalg import svd
from scipy.special import eval_chebyt, sph_harm_y

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        """tqdm 不可用时的简易进度包装器。"""
        return iterable


STRUCTURE_SUFFIXES = {".poscar", ".vasp", ".xyz", ".extxyz", ".traj", ".cif"}
STRUCTURE_PREFIXES = ("POSCAR", "CONTCAR")

def compute_spherical_chebyshev_features(atoms: Atoms, r_c: float = 6.0, n_max: int = 5, l_max: int = 6):

    """计算结构的球谐-Chebyshev 全局旋转不变描述符。"""

    N_atoms = len(atoms)
    i_list, j_list, d_list, D_list = neighbor_list('ijdD', atoms, r_c)
    c_i_nlm = np.zeros((N_atoms, n_max, l_max, 2 * l_max + 1), dtype=complex)

    for i in range(N_atoms):
        mask = (i_list == i)
        r_ij = d_list[mask]
        vec_ij = D_list[mask]

        if len(r_ij) == 0:
            continue

        x_ij = 2.0 * (r_ij / r_c) - 1.0
        f_c = (1-(r_ij/r_c)**2)**4
        z = vec_ij[:, 2]
        phi_ij = np.arccos(np.clip(z / r_ij, -1.0, 1.0))
        theta_ij = np.arctan2(vec_ij[:, 1], vec_ij[:, 0])
        theta_ij[theta_ij < 0] += 2 * np.pi

        for n in range(n_max):
            R_n = eval_chebyt(n, x_ij)

            for l in range(l_max):
                for m_idx, m in enumerate(range(-l, l + 1)):
                    Y_lm = sph_harm_y(m, l, theta_ij, phi_ij)
                    c_i_nlm[i, n, l, m_idx] = np.sum(R_n * Y_lm * f_c)

    invariant_features = []

    for n in range(n_max):
        for n_prime in range(n, n_max):
            for l in range(l_max):
                c_1 = c_i_nlm[:, n, l, :2*l+1]
                c_2 = c_i_nlm[:, n_prime, l, :2*l+1]
                p_i = (4*np.pi/(2*l+1))*np.real(np.sum(np.conj(c_1) * c_2, axis=1))
                invariant_features.append(p_i)

    atomic_descriptors = np.column_stack(invariant_features)
    global_descriptor = np.mean(atomic_descriptors, axis=0)

    return global_descriptor


def is_db_path(path):
    """判断路径是否为 ASE 数据库文件。"""
    return Path(path).suffix.lower() == ".db"


def list_structure_files(directory):
    """列出目录中支持的结构文件。"""
    files = []
    for path in sorted(Path(directory).iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() in STRUCTURE_SUFFIXES:
            files.append(path)
            continue
        if path.name.upper().startswith(STRUCTURE_PREFIXES):
            files.append(path)
    return files


def read_structure_file(path):
    """读取单个结构文件，并尽量保留多帧结构。"""
    try:
        return list(iread(str(path), index=":"))
    except Exception:
        return [read(str(path))]


def read_structures(input_path):
    """从数据库、文件或目录读取结构及来源标签。"""
    path = Path(input_path)
    structures = []
    labels = []

    if is_db_path(path):
        with connect(str(path)) as db:
            for row in db.select():
                structures.append(row.toatoms())
                labels.append(f"{path.name}:id={row.id}")
    elif path.is_dir():
        files = list_structure_files(path)
        if not files:
            raise FileNotFoundError(f"No structure files found in {path}")
        for file_path in files:
            frames = read_structure_file(file_path)
            for frame_id, atoms in enumerate(frames):
                structures.append(atoms)
                if len(frames) == 1:
                    labels.append(file_path.name)
                else:
                    labels.append(f"{file_path.name}:{frame_id}")
    elif path.is_file():
        frames = read_structure_file(path)
        for frame_id, atoms in enumerate(frames):
            structures.append(atoms)
            if len(frames) == 1:
                labels.append(path.name)
            else:
                labels.append(f"{path.name}:{frame_id}")
    else:
        raise FileNotFoundError(f"Input path does not exist: {path}")

    return structures, labels


def _format_summary_value(value):
    if value is None:
        return "nan"
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.8g}"
    return str(value)


def write_selected_structures(output_path, structures, selected_indices, labels,
                              selection_records=None):
    """将选中结构写入 ASE 数据库或 POSCAR 目录。"""
    path = Path(output_path)
    if is_db_path(path):
        if path.exists():
            path.unlink()
        path.parent.mkdir(parents=True, exist_ok=True)
        with connect(str(path)) as db_out:
            for idx in selected_indices:
                db_out.write(structures[idx])
        return [path]

    if path.exists() and path.is_file():
        raise ValueError(f"Output path is a file, expected directory: {path}")
    path.mkdir(parents=True, exist_ok=True)
    for old_file in path.iterdir():
        if old_file.is_file():
            old_file.unlink()

    written = []
    summary_path = path.with_name(f"{path.name}_summary.dat")
    extra_keys = []
    if selection_records:
        for record in selection_records:
            for key in record:
                if key not in extra_keys:
                    extra_keys.append(key)

    with open(summary_path, "w", encoding="utf-8") as summary:
        header = "# selected_file source index"
        if extra_keys:
            header += " " + " ".join(extra_keys)
        summary.write(header + "\n")
        for out_id, idx in enumerate(selected_indices, start=1):
            out_path = path / f"{out_id:06d}.poscar"
            write(str(out_path), structures[idx], format="vasp")
            written.append(out_path)
            summary.write(f"{out_path.name} {labels[idx]} {idx}")
            if extra_keys:
                record = selection_records[out_id - 1]
                values = [
                    _format_summary_value(record.get(key))
                    for key in extra_keys
                ]
                summary.write(" " + " ".join(values))
            summary.write("\n")
    return written


def build_feature_matrix(structures, r_c, n_max, l_max, description):
    """为 CUR 筛选构建归一化描述符矩阵。"""
    features = []
    for atoms in tqdm(structures, desc=description, unit="struct", ncols=150):
        features.append(compute_spherical_chebyshev_features(
            atoms, r_c=r_c, n_max=n_max, l_max=l_max
        ))
    matrix = np.vstack(features).T
    norms = np.linalg.norm(matrix, axis=0, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


def normalize_columns(matrix):
    """返回列归一化矩阵，用于余弦相似度。"""
    norms = np.linalg.norm(matrix, axis=0, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


def cur_select_structures(db_in_path, db_out_path, n_select, db_based_path=None,
                          r_c=6.0, n_max=5, l_max=6,
                          similarity_threshold=0.9995):
    """使用确定性 CUR 分解选择具有代表性和多样性的结构。"""
    if similarity_threshold is not None:
        if not np.isfinite(similarity_threshold):
            raise ValueError("similarity_threshold must be finite or None")
        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError("similarity_threshold must be in [0, 1]")

    print(f"Reading candidate structures from {db_in_path}...")
    structures_in, labels_in = read_structures(db_in_path)
    n_in_total = len(structures_in)

    if n_in_total == 0:
        raise ValueError("No candidate structures found")
    if n_select <= 0:
        raise ValueError("n_select must be positive")
    if Path(db_in_path).resolve() == Path(db_out_path).resolve():
        raise ValueError("Input and output paths must be different")
    if n_select >= n_in_total and similarity_threshold is None:
        print("Target selection size is not smaller than candidate pool; keeping all structures.")
        selected_indices = list(range(n_in_total))
        write_selected_structures(db_out_path, structures_in,
                                  selected_indices, labels_in)
        return selected_indices
    n_select = min(n_select, n_in_total)

    print("Constructing feature matrix X for candidates...")
    X_current = build_feature_matrix(
        structures_in, r_c, n_max, l_max, "Feature Extraction (Candidates)"
    )
    X_raw = X_current.copy()
    max_base_similarity = np.full(n_in_total, np.nan)

    if db_based_path is not None:
        print(f"Reading base structures from {db_based_path}...")
        structures_base, _ = read_structures(db_based_path)

        if len(structures_base) > 0:
            print("Projecting out known information from candidate space...")

            X_base = build_feature_matrix(
                structures_base, r_c, n_max, l_max, "Feature Extraction (Base)"
            )
            max_base_similarity = np.max(X_base.T @ X_raw, axis=0)

            for i in range(X_base.shape[1]):
                X_base_col = X_base[:, i]
                norm_sq = np.dot(X_base_col, X_base_col)
                if norm_sq > 1e-12:
                    projections = np.dot(X_base_col, X_current) / norm_sq
                    X_current = X_current - np.outer(X_base_col, projections)

            print("Base space projection complete. Remaining features contain pure novelty.")

    selected_indices = []
    selection_records = []
    rejected_by_similarity = []
    X_similarity = normalize_columns(X_current.copy())

    print(f"Starting CUR decomposition to select up to {n_select} structures out of {n_in_total}...")
    if similarity_threshold is not None:
        print(f"Adaptive similarity threshold enabled: max cosine = {similarity_threshold:g}")
    for step in tqdm(range(n_select), desc="CUR Selection", unit="struct", ncols=150):

        U, s, Vh = svd(X_current, full_matrices=False)
        if len(s) == 0 or s[0] <= 1e-12:
            print("Stopping CUR: residual feature matrix is numerically exhausted.")
            break
        pi_scores = (Vh[0, :])**2

        for idx in selected_indices:
            pi_scores[idx] = -1.0
        for idx in rejected_by_similarity:
            pi_scores[idx] = -1.0

        accepted = False
        while np.max(pi_scores) >= 0.0:
            l_idx = int(np.argmax(pi_scores))
            cur_score = float(pi_scores[l_idx])

            max_selected_similarity = np.nan
            if similarity_threshold is not None and selected_indices:
                similarities = (
                    X_similarity[:, selected_indices].T @ X_similarity[:, l_idx]
                )
                max_selected_similarity = float(np.max(similarities))
                if max_selected_similarity >= similarity_threshold:
                    rejected_by_similarity.append(l_idx)
                    pi_scores[l_idx] = -1.0
                    X_current[:, l_idx] = 0.0
                    continue
            elif similarity_threshold is not None:
                max_selected_similarity = 0.0

            selected_indices.append(l_idx)

            X_l = X_current[:, l_idx]
            norm_X_l_sq = float(np.dot(X_l, X_l))
            selection_records.append({
                "cur_rank": len(selected_indices),
                "cur_score": cur_score,
                "singular_value": float(s[0]),
                "residual_norm": float(np.sqrt(max(norm_X_l_sq, 0.0))),
                "max_similarity_selected": max_selected_similarity,
                "max_similarity_base": float(max_base_similarity[l_idx]),
            })

            if norm_X_l_sq > 1e-12:
                projections = np.dot(X_l, X_current) / norm_X_l_sq
                X_current = X_current - np.outer(X_l, projections)
            accepted = True
            break

        if not accepted:
            print("Stopping CUR: no remaining candidate satisfies the similarity threshold.")
            break

    print(f"Saving selected configurations to {db_out_path}...")
    write_selected_structures(db_out_path, structures_in,
                              selected_indices, labels_in,
                              selection_records=selection_records)
    if rejected_by_similarity:
        print(f"Rejected {len(rejected_by_similarity)} near-duplicate candidates by similarity threshold.")

    print(f"Done! Active learning structure selection completed with {len(selected_indices)} structures.")
    return selected_indices


def parse_args():
    """解析独立 CUR 筛选命令行参数。"""
    parser = argparse.ArgumentParser(
        description="CUR diversity selection for ASE DBs or POSCAR directories"
    )
    parser.add_argument("input", help="Input ASE .db, structure file, or POSCAR directory")
    parser.add_argument("output", help="Output ASE .db or POSCAR directory")
    parser.add_argument("n_select", type=int, help="Number of structures to select")
    parser.add_argument("--base", help="Existing training set for novelty projection")
    parser.add_argument("--r-c", type=float, default=6.0)
    parser.add_argument("--n-max", type=int, default=5)
    parser.add_argument("--l-max", type=int, default=6)
    parser.add_argument("--similarity-threshold", type=float, default=0.9995,
                        help="Maximum post-projection cosine similarity between selected structures")
    parser.add_argument("--no-similarity-threshold", action="store_true",
                        help="Disable adaptive similarity rejection")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    similarity_threshold = (
        None if args.no_similarity_threshold else args.similarity_threshold
    )
    cur_select_structures(args.input, args.output, args.n_select,
                          db_based_path=args.base, r_c=args.r_c,
                          n_max=args.n_max, l_max=args.l_max,
                          similarity_threshold=similarity_threshold)
