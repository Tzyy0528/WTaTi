import shutil
from pathlib import Path

from ase.io import read

from workflow_utils import run_logged_command


def poscar_elems_string(poscar):
    """从 POSCAR 统计元素数量并生成 nninit 元素字符串。"""
    atoms = read(str(poscar))
    counts = {}
    for symbol in atoms.get_chemical_symbols():
        counts[symbol] = counts.get(symbol, 0) + 1
    if not counts:
        raise ValueError(f"No chemical symbols found in {poscar}")
    return ",".join(
        f"{symbol}:{counts[symbol]}"
        for symbol in sorted(counts)
    )


def generate_seed_structures(args, poscar, input_dir):
    """调用 nninit 生成初始微扰 POSCAR 结构。"""
    seed_root = input_dir / "seed-generation"
    seed_root.mkdir(parents=True, exist_ok=True)
    nninit_dir = seed_root / "nninit-poscars"

    if args.seed_overwrite and nninit_dir.exists():
        shutil.rmtree(nninit_dir)

    elems = poscar_elems_string(poscar)
    rep = [str(value) for value in args.seed_rep]
    nninit_cmd = [
        args.seed_init_runner,
        elems,
        str(nninit_dir.resolve()),
        str(args.seed_nstructs),
        str(Path(poscar).resolve()),
        "_",
        rep[0],
        rep[1],
        rep[2],
        args.seed_scales,
        str(args.seed_disturb),
    ]
    run_logged_command(
        nninit_cmd,
        seed_root,
        seed_root / "nninit.log",
        command_path=seed_root / "nninit_command.sh",
        module_name=args.dft_module,
    )
    return seed_root, nninit_dir
