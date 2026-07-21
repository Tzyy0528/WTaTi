import shutil
from pathlib import Path

from vasp_batch_dft import (
    DEFAULT_ENCUT_FACTOR,
    DEFAULT_POTCAR_ROOT,
    PotcarProvider,
    parse_poscar_species,
)
from workflow_utils import command_with_optional_module, run_logged_command


DEFAULT_DFT_ENCUT = None
DEFAULT_DFT_ENCUT_FACTOR = DEFAULT_ENCUT_FACTOR


def _format_encut(value):
    return f"{value:.10g}"


def infer_encut_from_poscar_dir(poscar_dir, encut_factor=DEFAULT_DFT_ENCUT_FACTOR):
    """Infer ENCUT as factor * max(POTCAR ENMAX) for POSCARs in a directory."""
    poscar_dir = Path(poscar_dir)
    provider = PotcarProvider(DEFAULT_POTCAR_ROOT)
    species = set()
    for poscar in sorted(poscar_dir.glob("*.poscar")):
        species.update(parse_poscar_species(poscar))
    if not species:
        poscar = poscar_dir / "POSCAR"
        if poscar.exists():
            species.update(parse_poscar_species(poscar))
    if not species:
        raise RuntimeError(f"Cannot infer ENCUT: no POSCAR species found in {poscar_dir}")
    return max(provider.enmax(symbol) for symbol in species) * encut_factor


def effective_dft_encut(args_or_value, poscar_dir, encut_factor=None):
    explicit = getattr(args_or_value, "dft_encut", args_or_value)
    if explicit is not None:
        return explicit
    factor = encut_factor
    if factor is None:
        factor = getattr(args_or_value, "dft_encut_factor", DEFAULT_DFT_ENCUT_FACTOR)
    return infer_encut_from_poscar_dir(poscar_dir, factor)


def seed_dft_command(args, nninit_dir, seed_db):
    """构建用于标注种子结构的 nncalc 命令。"""
    encut = effective_dft_encut(args, nninit_dir)
    cmd = [
        args.dft_runner,
        str(Path(nninit_dir).resolve()),
        str(Path(seed_db).resolve()),
        args.dft_magmom,
        str(args.dft_kspacing),
        _format_encut(encut),
    ]
    return cmd


def run_seed_dft_calculation(args, seed_root, nninit_dir, seed_db):
    """对种子结构运行 nncalc 并返回 seed.db 路径。"""
    if args.seed_overwrite and Path(seed_db).exists():
        Path(seed_db).unlink()

    cmd = seed_dft_command(args, nninit_dir, seed_db)
    run_logged_command(
        cmd,
        seed_root,
        Path(seed_root) / "nncalc.log",
        command_path=Path(seed_root) / "nncalc_command.sh",
        module_name=args.dft_module,
    )

    seed_db = Path(seed_db)
    if not seed_db.exists():
        raise FileNotFoundError(f"nncalc did not create seed database: {seed_db}")
    return seed_db.resolve()


def run_eos_dft_calculation(
    eos_input_dir,
    eos_db,
    work_dir,
    dft_runner="nncalc",
    dft_module="jse",
    dft_magmom="_",
    dft_kspacing=0.2,
    dft_encut=DEFAULT_DFT_ENCUT,
    dft_encut_factor=DEFAULT_DFT_ENCUT_FACTOR,
    overwrite=False,
):
    """对 EOS 验证结构运行 nncalc，并返回 EOS DFT 数据库路径。"""
    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    eos_db = Path(eos_db)
    eos_db.parent.mkdir(parents=True, exist_ok=True)
    if overwrite and eos_db.exists():
        eos_db.unlink()

    encut = effective_dft_encut(dft_encut, eos_input_dir, dft_encut_factor)
    cmd = [
        dft_runner,
        str(Path(eos_input_dir).resolve()),
        str(Path(eos_db).resolve()),
        dft_magmom,
        str(dft_kspacing),
        _format_encut(encut),
    ]

    run_logged_command(
        cmd,
        work_dir,
        work_dir / "nncalc.log",
        command_path=work_dir / "nncalc_command.sh",
        module_name=dft_module,
    )

    if not eos_db.exists():
        raise FileNotFoundError(f"nncalc did not create EOS database: {eos_db}")
    return eos_db.resolve()


def dft_command(current_db, selected_dir, updated_db, args):
    """构建用于标注筛选结构的 nncalc 命令。"""
    encut = effective_dft_encut(args, selected_dir)
    input_spec = ":".join([
        str(Path(current_db).resolve()),
        str(Path(selected_dir).resolve()),
    ])
    cmd = [
        args.dft_runner,
        input_spec,
        str(Path(updated_db).resolve()),
        args.dft_magmom,
        str(args.dft_kspacing),
        _format_encut(encut),
    ]
    return cmd


def run_dft_and_update_database(current_db, round_dir, selected_dir,
                                selected_structures, args):
    """对筛选结构做 DFT 标注并生成本轮数据库。"""
    dft_dir = round_dir / "dft"
    dft_dir.mkdir(parents=True, exist_ok=True)
    updated_db = round_dir / "updated.db"

    if not selected_structures:
        shutil.copy2(current_db, updated_db)
        (dft_dir / "README.txt").write_text(
            "No structures were selected, so DFT labeling was skipped.\n"
            f"updated.db was copied from {current_db}.\n",
            encoding="utf-8",
        )
        return updated_db

    encut = effective_dft_encut(args, selected_dir)
    cmd = dft_command(current_db, selected_dir, updated_db, args)
    _, command_text = command_with_optional_module(cmd, args.dft_module)
    (dft_dir / "command.sh").write_text(command_text + "\n", encoding="utf-8")
    (dft_dir / "README.txt").write_text(
        "DFT labeling is run by nncalc.\n"
        f"Selected structures: {len(selected_structures)}\n"
        f"Structure directory: {selected_dir}\n"
        f"Magmom setting: {args.dft_magmom}\n"
        f"KSPACING: {args.dft_kspacing:g}\n"
        f"ENCUT: {_format_encut(encut)}\n"
        f"Output database: {updated_db}\n",
        encoding="utf-8",
    )

    run_logged_command(cmd, dft_dir, dft_dir / "log",
                       module_name=args.dft_module)

    if not updated_db.exists():
        raise FileNotFoundError(f"nncalc did not create {updated_db}")
    return updated_db
