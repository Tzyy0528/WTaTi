#!/usr/bin/env python3
"""Generate fixed unary EOS reference structures and collect their DFT CSV."""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
from pathlib import Path

from ase.db import connect
from ase.io import read

from dft_calculation import (
    DEFAULT_DFT_ENCUT,
    DEFAULT_DFT_ENCUT_FACTOR,
    run_eos_dft_calculation,
)

REFERENCE_ROOT = Path("results/eos_reference")
DEFAULT_STRUCTURES: dict[str, Path] = {}
DEFAULT_SCALES = [0.97 + i * (1.03 - 0.97) / 18 for i in range(19)]
DEFAULT_METADATA = REFERENCE_ROOT / "eos_structures.csv"
DEFAULT_INPUT_DIR = REFERENCE_ROOT / "nncalc_input"
DEFAULT_SPLIT_INPUT_ROOT = REFERENCE_ROOT / "nncalc_input_by_structure"
DEFAULT_DFT_DB = REFERENCE_ROOT / "eos_dft.db"
DEFAULT_SPLIT_DFT_DBS: dict[str, Path] = {}
DEFAULT_DFT_WORK_DIR = REFERENCE_ROOT / "dft"
DEFAULT_REFERENCE_CSV = REFERENCE_ROOT / "eos_reference.csv"


def format_scale(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text.replace("-", "m").replace(".", "p")


def read_poscar_scale(path: Path) -> float:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 2:
        raise ValueError(f"POSCAR is too short: {path}")
    try:
        return float(lines[1].split()[0])
    except Exception as exc:
        raise ValueError(f"Cannot parse POSCAR scale line in {path}: {lines[1]!r}") from exc


def write_scaled_poscar(src: Path, dst: Path, lattice_scale: float) -> float:
    lines = src.read_text(encoding="utf-8").splitlines()
    if len(lines) < 2:
        raise ValueError(f"POSCAR is too short: {src}")
    base_scale = read_poscar_scale(src)
    output_scale = base_scale * lattice_scale
    lines[1] = f"{output_scale:.16g}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_scale


def parse_structure_specs(values: list[str] | None) -> dict[str, Path]:
    if not values:
        raise ValueError("At least one --structure label=path argument is required")
    specs: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise argparse.ArgumentTypeError(
                f"Structure spec must be label=path, got {value!r}"
            )
        label, path = value.split("=", 1)
        label = label.strip()
        if not label:
            raise argparse.ArgumentTypeError(f"Empty structure label in {value!r}")
        specs[label] = Path(path)
    return specs


def generate_eos_structures(args: argparse.Namespace) -> Path:
    structures = parse_structure_specs(args.structure)
    out_root = Path(args.output_dir)
    structure_root = out_root / "structures"
    nncalc_input = out_root / "nncalc_input"
    split_input_root = out_root / "nncalc_input_by_structure"
    metadata_path = Path(args.metadata)

    if args.overwrite:
        for path in (structure_root, nncalc_input, split_input_root):
            if path.exists():
                shutil.rmtree(path)
        if metadata_path.exists():
            metadata_path.unlink()

    structure_root.mkdir(parents=True, exist_ok=True)
    nncalc_input.mkdir(parents=True, exist_ok=True)
    split_input_root.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for label, src in sorted(structures.items()):
        src = src.resolve()
        if not src.exists():
            raise FileNotFoundError(f"Missing source POSCAR for {label}: {src}")
        base_atoms = read(str(src))
        symbols = sorted(set(base_atoms.get_chemical_symbols()))
        if len(symbols) != 1:
            raise ValueError(
                f"EOS source must be unary, got {symbols} in {src}"
            )
        element = symbols[0]
        base_volume = float(base_atoms.get_volume())
        natoms = len(base_atoms)
        input_scale = read_poscar_scale(src)

        for scale in args.scales:
            scale_tag = format_scale(scale)
            structure_name = f"{element}_{label}_scale_{scale_tag}.poscar"
            case_dir = structure_root / label / f"scale_{scale_tag}"
            poscar_path = case_dir / structure_name
            flat_path = nncalc_input / structure_name
            split_path = split_input_root / label / structure_name

            output_scale = write_scaled_poscar(src, poscar_path, scale)
            shutil.copy2(poscar_path, flat_path)
            split_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(poscar_path, split_path)

            atoms = read(str(poscar_path))
            volume = float(atoms.get_volume())
            rows.append({
                "structure": label,
                "scale": f"{scale:.12g}",
                "input_poscar_scale": f"{input_scale:.12g}",
                "output_poscar_scale": f"{output_scale:.12g}",
                "natoms": str(natoms),
                "base_volume_A3": f"{base_volume:.12f}",
                "volume_A3": f"{volume:.12f}",
                "volume_per_atom_A3": f"{volume / natoms:.12f}",
                "volume_ratio": f"{volume / base_volume:.12f}",
                "source_path": str(src),
                "poscar_path": str(poscar_path),
                "nncalc_path": str(flat_path),
                "nncalc_structure_path": str(split_path),
            })

    fieldnames = [
        "structure",
        "scale",
        "input_poscar_scale",
        "output_poscar_scale",
        "natoms",
        "base_volume_A3",
        "volume_A3",
        "volume_per_atom_A3",
        "volume_ratio",
        "source_path",
        "poscar_path",
        "nncalc_path",
        "nncalc_structure_path",
    ]
    with metadata_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} EOS structures")
    print(f"metadata: {metadata_path}")
    print(f"nncalc input: {nncalc_input}")
    print(f"split nncalc input: {split_input_root}")
    return metadata_path


def run_dft_reference(args: argparse.Namespace) -> Path:
    input_dir = Path(args.input_dir)
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Missing nncalc input structure folder: {input_dir}")
    output = run_eos_dft_calculation(
        input_dir,
        args.dft_db,
        args.work_dir,
        dft_runner=args.dft_runner,
        dft_module=args.dft_module,
        dft_magmom=args.dft_magmom,
        dft_kspacing=args.dft_kspacing,
        dft_encut=args.dft_encut,
        dft_encut_factor=args.dft_encut_factor,
        overwrite=args.overwrite,
    )
    print(f"Wrote EOS DFT DB: {output}")
    return output


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def row_energy(row) -> float:
    for attr in ("energy", "free_energy"):
        value = getattr(row, attr, None)
        if value is not None:
            return float(value)
    atoms = row.toatoms()
    try:
        return float(atoms.get_potential_energy())
    except Exception as exc:
        raise ValueError(f"Cannot find energy for DB row id={row.id}") from exc


def collect_db_rows(db_path: Path, structure_label: str | None = None) -> list[dict[str, str | float | int]]:
    if not db_path.is_file():
        raise FileNotFoundError(f"Missing EOS DFT database: {db_path}")
    rows = []
    with connect(str(db_path)) as db:
        for row in db.select():
            atoms = row.toatoms()
            rows.append({
                "db_id": int(row.id),
                "dft_db": str(db_path),
                "structure": structure_label or "",
                "natoms": len(atoms),
                "volume_A3": float(atoms.get_volume()),
                "energy_eV": row_energy(row),
            })
    if not rows:
        raise ValueError(f"No rows found in EOS DFT database: {db_path}")
    return rows


def match_rows(metadata: list[dict[str, str]], db_rows, volume_tol: float):
    unmatched = list(db_rows)
    out_rows = []
    for meta in metadata:
        natoms = int(meta["natoms"])
        volume = float(meta["volume_A3"])
        candidates = [
            (abs(float(row["volume_A3"]) - volume), idx, row)
            for idx, row in enumerate(unmatched)
            if int(row["natoms"]) == natoms
            and (not row.get("structure") or row["structure"] == meta["structure"])
            and abs(float(row["volume_A3"]) - volume) <= volume_tol
        ]
        if not candidates:
            raise ValueError(
                "Could not match EOS metadata row to DFT DB row: "
                f"structure={meta['structure']} scale={meta['scale']} "
                f"natoms={natoms} volume={volume:.12f}"
            )
        _, idx, row = min(candidates, key=lambda item: item[0])
        unmatched.pop(idx)
        energy = float(row["energy_eV"])
        out = dict(meta)
        out.update({
            "db_id": str(row["db_id"]),
            "dft_db": str(row.get("dft_db", "")),
            "dft_volume_A3": f"{float(row['volume_A3']):.12f}",
            "dft_energy_eV": f"{energy:.12f}",
            "dft_energy_per_atom_eV": f"{energy / natoms:.12f}",
        })
        out_rows.append(out)
    if unmatched:
        print(f"Warning: {len(unmatched)} DFT DB rows were not matched", file=sys.stderr)
    return out_rows


def write_reference(rows: list[dict[str, str]], output_csv: Path) -> None:
    if not rows:
        raise ValueError("No EOS reference rows to write")
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    preferred = [
        "structure", "scale", "natoms", "volume_A3", "volume_per_atom_A3",
        "volume_ratio", "dft_db", "db_id", "dft_volume_A3", "dft_energy_eV",
        "dft_energy_per_atom_eV", "poscar_path", "nncalc_path", "source_path",
    ]
    extras = [key for key in rows[0] if key not in preferred]
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=preferred + extras)
        writer.writeheader()
        writer.writerows(rows)


def default_dft_db_specs() -> list[tuple[str | None, Path]]:
    split_specs = [(label, path) for label, path in DEFAULT_SPLIT_DFT_DBS.items()]
    if all(path.exists() for _, path in split_specs):
        return split_specs
    if DEFAULT_DFT_DB.exists():
        return [(None, DEFAULT_DFT_DB)]
    raise ValueError("Pass one or more explicit --dft-db arguments")


def parse_dft_db_specs(values: list[str] | None) -> list[tuple[str | None, Path]]:
    if not values:
        return default_dft_db_specs()
    specs: list[tuple[str | None, Path]] = []
    for value in values:
        if "=" in value:
            label, path = value.split("=", 1)
            label = label.strip()
            if not label:
                raise argparse.ArgumentTypeError(f"Empty structure label in {value!r}")
            specs.append((label, Path(path)))
        else:
            specs.append((None, Path(value)))
    return specs


def collect_eos_reference(metadata_csv: Path, dft_dbs: Path | list[tuple[str | None, Path]],
                          output_csv: Path,
                          volume_tol: float = 1e-5) -> Path:
    metadata = read_csv(metadata_csv)
    if isinstance(dft_dbs, Path):
        dft_db_specs = [(None, dft_dbs)]
    else:
        dft_db_specs = dft_dbs
    db_rows = []
    for label, dft_db in dft_db_specs:
        db_rows.extend(collect_db_rows(dft_db, structure_label=label))
    rows = match_rows(metadata, db_rows, volume_tol)
    write_reference(rows, output_csv)
    return output_csv


def collect_reference(args: argparse.Namespace) -> Path:
    dft_db_specs = parse_dft_db_specs(args.dft_db)
    output = collect_eos_reference(
        Path(args.metadata), dft_db_specs, Path(args.output_csv), args.volume_tol
    )
    print(f"Wrote EOS DFT reference CSV: {output}")
    return output


def add_common_reference_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--metadata",
        default=str(DEFAULT_METADATA),
        help="EOS structure metadata CSV.",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fixed unary EOS reference workflow."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser(
        "generate", help="Generate fixed EOS POSCARs and nncalc input folder."
    )
    generate.add_argument(
        "--structure",
        action="append",
        help="Required structure spec label=path. Can be repeated.",
    )
    generate.add_argument(
        "--scales",
        nargs="+",
        type=float,
        default=DEFAULT_SCALES,
        help="POSCAR line-2 lattice scale factors.",
    )
    generate.add_argument(
        "--output-dir",
        default=str(REFERENCE_ROOT),
        help="Output root for EOS reference assets.",
    )
    add_common_reference_args(generate)
    generate.add_argument(
        "--overwrite",
        action="store_true",
        help="Remove existing generated EOS structures and metadata before writing.",
    )
    generate.set_defaults(func=generate_eos_structures)

    run_dft = subparsers.add_parser(
        "run-dft",
        help=(
            "Legacy: run nncalc directly on the generated EOS input folder "
            "inside a compute allocation. For new DFT labeling, prefer "
            "src/vasp_batch_dft.py and scripts/slurm/run_vasp_batch_dft.slurm."
        ),
    )
    run_dft.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    run_dft.add_argument("--dft-db", default=str(DEFAULT_DFT_DB))
    run_dft.add_argument("--work-dir", default=str(DEFAULT_DFT_WORK_DIR))
    run_dft.add_argument("--dft-runner", default="nncalc")
    run_dft.add_argument("--dft-module", default="jse")
    run_dft.add_argument("--dft-magmom", default="_")
    run_dft.add_argument("--dft-kspacing", type=float, default=0.2)
    run_dft.add_argument("--dft-encut", type=float, default=DEFAULT_DFT_ENCUT)
    run_dft.add_argument("--dft-encut-factor", type=float, default=DEFAULT_DFT_ENCUT_FACTOR)
    run_dft.add_argument("--overwrite", action="store_true")
    run_dft.set_defaults(func=run_dft_reference)

    collect = subparsers.add_parser(
        "collect", help="Collect EOS DFT DB rows into eos_reference.csv."
    )
    add_common_reference_args(collect)
    collect.add_argument(
        "--dft-db",
        action="append",
        default=None,
        help=(
            "DFT DB path, or label=path for split DBs. Can be repeated. "
            "Required unless the generic default eos_dft.db exists."
        ),
    )
    collect.add_argument("--output-csv", default=str(DEFAULT_REFERENCE_CSV))
    collect.add_argument("--volume-tol", type=float, default=1e-5)
    collect.set_defaults(func=collect_reference)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
