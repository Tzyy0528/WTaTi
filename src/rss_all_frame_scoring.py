#!/usr/bin/env python3
"""Validate and score a flat unary RSS/Mini POSCAR pool with a committee."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import os
import re
import shutil
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from ase.geometry import wrap_positions
from ase.io import read, write

SCRIPT_DIR = Path(globals().get("__file__", sys.argv[0])).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from stratified_uncertainty_selection import score_atoms
from uncertainty_selection import build_calculators, set_default_thread_limits


ALL_FRAME_FIELDS = (
    "pressure_gpa",
    "scale_factor",
    "source_type",
    "source_value",
    "trajectory",
    "trajectory_path",
    "frame",
    "uncertainty",
    "uncertainty_bin",
    "volume_per_atom",
    "max_force",
    "max_force_model0",
    "instant_pressure_gpa",
    "discarded_equilibration",
    "selected_candidate",
    "candidate_id",
    "candidate_file",
    "selection_rank_in_bin",
    "cur_score",
    "final_selected",
    "natoms",
    "mini_pressure_bar",
    "pressure_index",
    "raw_index",
    "rss_source_file",
    "rss_source_path",
    "minimized_source_path",
    "raw_source_path",
    "flat_sha256",
    "minimized_sha256",
)

PROVENANCE_FIELDS = (
    "trajectory",
    "trajectory_path",
    "frame",
    "natoms",
    "mini_pressure_bar",
    "pressure_index",
    "raw_index",
    "rss_source_file",
    "rss_source_path",
    "minimized_source_path",
    "raw_source_path",
    "flat_sha256",
    "minimized_sha256",
)

MINI_FAILURE_FIELDS = (
    "raw_index",
    "pressure_index",
    "mini_pressure_bar",
    "raw_source_path",
    "raw_natoms",
    "minimized_source_path",
    "minimized_natoms",
    "minimized_read_error",
    "rss_source_file",
    "rss_source_path",
    "flat_natoms",
    "flat_read_error",
    "flat_sha256",
    "minimized_sha256",
    "flat_matches_minimized",
    "failure_log",
    "exclusion_reason",
)


@dataclass(frozen=True)
class PoolEntry:
    flat_path: Path
    rss_source_path: str
    minimized_path: Path
    raw_path: Path
    raw_index: int
    pressure_index: int
    natoms: int
    mini_pressure_bar: float
    flat_sha256: str
    minimized_sha256: str


@dataclass(frozen=True)
class MiniFailure:
    raw_index: int
    pressure_index: int
    mini_pressure_bar: float
    log_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a retained unary RSS/Mini pool, materialize auditable "
            "source archives, and score every minimized structure with a committee."
        )
    )
    parser.add_argument("--element", required=True, choices=("W", "Ta", "Ti"))
    parser.add_argument("--pool-dir", required=True, help="rss/rss-minimized-poscar")
    parser.add_argument("--manifest", required=True, help="Flat-pool manifest.tsv")
    parser.add_argument("--minimized-dir", required=True, help="rss/minimized/unary-<X>")
    parser.add_argument("--raw-dir", required=True, help="rss/raw/unary-<X>")
    parser.add_argument(
        "--mini-failure-log",
        help=(
            "Retained JSE Mini log whose explicit LMP FAIL LIST entries are "
            "excluded and recorded; all nonfailed sources remain mandatory"
        ),
    )
    parser.add_argument("--jnn-glob", required=True, help="Exactly ten matching M4 JNNs")
    parser.add_argument("--output-root", required=True, help="New protected RSS selection root")
    parser.add_argument("--natoms-list", required=True, help="Expected comma-separated atom counts")
    parser.add_argument(
        "--mini-press-list",
        required=True,
        help="Expected comma-separated Mini pressures in bar, ordered by pressure index",
    )
    parser.add_argument("--raw-count-per-natoms", type=positive_int, default=50)
    parser.add_argument("--progress-interval", type=positive_int, default=100)
    return parser.parse_args()


def positive_int(text: str) -> int:
    value = int(text)
    if value <= 0:
        raise argparse.ArgumentTypeError("expected a positive integer")
    return value


def parse_int_list(text: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in text.split(",") if item.strip())
    if not values or any(value <= 0 for value in values) or len(set(values)) != len(values):
        raise ValueError("expected unique positive comma-separated integers")
    return values


def parse_float_list(text: str) -> tuple[float, ...]:
    values = tuple(float(item.strip()) for item in text.split(",") if item.strip())
    if not values or any(not math.isfinite(value) or value < 0.0 for value in values):
        raise ValueError("expected finite nonnegative comma-separated values")
    return values


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def format_bar(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:g}".replace("-", "m").replace(".", "p")


def sorted_jnns(pattern: str) -> list[Path]:
    paths = [path for path in Path().glob(pattern) if path.is_file()]

    def key(path: Path) -> tuple[int, str]:
        match = re.search(r"train-(\d+)", str(path.parent))
        return (int(match.group(1)) if match else sys.maxsize, str(path))

    paths.sort(key=key)
    if len(paths) != 10:
        raise ValueError(f"RSS selection requires exactly ten JNNs from {pattern}, found {len(paths)}")
    return paths


def read_unary_atoms(path: Path, element: str):
    atoms = read(path, format="vasp")
    if len(atoms) == 0:
        raise ValueError(f"Empty RSS structure: {path}")
    if set(atoms.get_chemical_symbols()) != {element}:
        raise ValueError(f"Non-{element} RSS structure: {path}")
    if not np.all(atoms.pbc):
        raise ValueError(f"RSS structure is not 3D periodic: {path}")
    if not np.isfinite(atoms.positions).all():
        raise ValueError(f"Non-finite RSS positions: {path}")
    if not np.isfinite(atoms.cell.array).all() or atoms.cell.volume <= 0.0:
        raise ValueError(f"Invalid RSS cell: {path}")
    return atoms


def safe_child(parent: Path, relative_text: str) -> Path:
    candidate = (parent / relative_text).resolve()
    try:
        candidate.relative_to(parent.resolve())
    except ValueError as exc:
        raise ValueError(f"Manifest path escapes minimized root: {relative_text}") from exc
    return candidate


def load_raw_sources(
    raw_dir: Path,
    element: str,
    natoms_list: tuple[int, ...],
    raw_count_per_natoms: int,
) -> dict[int, tuple[Path, int]]:
    pattern = re.compile(rf"^{re.escape(element)}-(\d{{5}})\.poscar$")
    sources: dict[int, tuple[Path, int]] = {}
    for path in sorted(raw_dir.glob(f"{element}-*.poscar")):
        match = pattern.match(path.name)
        if not match:
            raise ValueError(f"Unexpected raw RSS file name: {path}")
        raw_index = int(match.group(1))
        if raw_index in sources:
            raise ValueError(f"Duplicate raw RSS index: {raw_index}")
        natoms = len(read_unary_atoms(path, element))
        if natoms not in natoms_list:
            raise ValueError(f"Unexpected raw atom count {natoms} in {path}")
        sources[raw_index] = (path, natoms)
    expected_count = len(natoms_list) * raw_count_per_natoms
    if len(sources) != expected_count or set(sources) != set(range(expected_count)):
        raise ValueError(
            f"Raw RSS index coverage is incomplete: expected {expected_count} contiguous files, "
            f"found {len(sources)}"
        )
    counts = Counter(natoms for _, natoms in sources.values())
    if counts != Counter({natoms: raw_count_per_natoms for natoms in natoms_list}):
        raise ValueError(f"Raw RSS atom-count coverage mismatch: {dict(sorted(counts.items()))}")
    return sources


def mini_pressure_index(value: float, pressures_bar: tuple[float, ...]) -> int:
    matches = [
        index
        for index, pressure in enumerate(pressures_bar)
        if math.isclose(value, pressure, rel_tol=0.0, abs_tol=1.0e-6)
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Mini failure log pressure {value:g} is not one configured Mini pressure"
        )
    return matches[0]


def parse_mini_failures(
    log_path: Path,
    element: str,
    raw_sources: dict[int, tuple[Path, int]],
    pressures_bar: tuple[float, ...],
) -> dict[tuple[int, int], MiniFailure]:
    if not log_path.is_file():
        raise FileNotFoundError(f"Missing Mini failure log: {log_path}")
    text = log_path.read_text(encoding="utf-8", errors="replace").replace("\r", "\n")
    marker = "LMP FAIL LIST:"
    marker_index = text.rfind(marker)
    if marker_index < 0:
        raise ValueError(f"Missing {marker!r} in Mini failure log: {log_path}")
    pattern = re.compile(
        rf"data:\s*.*?/{re.escape(element)}-(\d{{5}})\.poscar,\s*"
        r"press:\s*([0-9.+\-Ee]+),\s*exit:\s*1\b"
    )
    failures: dict[tuple[int, int], MiniFailure] = {}
    for match in pattern.finditer(text[marker_index:]):
        raw_index = int(match.group(1))
        if raw_index not in raw_sources:
            raise ValueError(
                f"Mini failure log references an unknown raw RSS index: {raw_index}"
            )
        pressure_value = float(match.group(2))
        pressure_index = mini_pressure_index(pressure_value, pressures_bar)
        key = (raw_index, pressure_index)
        if key in failures:
            raise ValueError(f"Duplicate Mini failure record for raw/pressure {key}")
        failures[key] = MiniFailure(
            raw_index=raw_index,
            pressure_index=pressure_index,
            mini_pressure_bar=pressures_bar[pressure_index],
            log_path=log_path,
        )
    if not failures:
        raise ValueError(f"No exit=1 records found after {marker!r} in {log_path}")
    return failures


def observed_natoms(path: Path | None) -> tuple[int | str, str]:
    if path is None or not path.is_file():
        return "", ""
    try:
        return len(read(path, format="vasp")), ""
    except Exception as exc:  # A logged Mini failure is retained but never scored.
        return "", f"{type(exc).__name__}: {exc}"


def mini_failure_row(
    failure: MiniFailure,
    raw_path: Path,
    raw_natoms: int,
    minimized_path: Path,
    flat_path: Path | None,
    rss_source_path: str,
) -> dict:
    minimized_natoms, minimized_error = observed_natoms(minimized_path)
    flat_natoms, flat_error = observed_natoms(flat_path)
    minimized_sha = sha256(minimized_path) if minimized_path.is_file() else ""
    flat_sha = sha256(flat_path) if flat_path is not None and flat_path.is_file() else ""
    return {
        "raw_index": failure.raw_index,
        "pressure_index": failure.pressure_index,
        "mini_pressure_bar": failure.mini_pressure_bar,
        "raw_source_path": str(raw_path),
        "raw_natoms": raw_natoms,
        "minimized_source_path": str(minimized_path),
        "minimized_natoms": minimized_natoms,
        "minimized_read_error": minimized_error,
        "rss_source_file": flat_path.name if flat_path is not None else "",
        "rss_source_path": rss_source_path,
        "flat_natoms": flat_natoms,
        "flat_read_error": flat_error,
        "flat_sha256": flat_sha,
        "minimized_sha256": minimized_sha,
        "flat_matches_minimized": str(bool(flat_sha and flat_sha == minimized_sha)),
        "failure_log": str(failure.log_path),
        "exclusion_reason": "mini_lammps_exit_1",
    }


def load_entries(
    element: str,
    pool_dir: Path,
    manifest_path: Path,
    minimized_dir: Path,
    raw_sources: dict[int, tuple[Path, int]],
    natoms_list: tuple[int, ...],
    pressures_bar: tuple[float, ...],
    raw_count_per_natoms: int,
    mini_failures: dict[tuple[int, int], MiniFailure] | None = None,
    exclusion_rows: list[dict] | None = None,
) -> list[PoolEntry]:
    mini_failures = mini_failures or {}
    if exclusion_rows is None:
        exclusion_rows = []
    minimized_dir = minimized_dir.resolve()
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Missing RSS manifest: {manifest_path}")
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows or set(rows[0]) != {"new_name", "original_path"}:
        raise ValueError(f"Unexpected RSS manifest schema: {manifest_path}")

    flat_files = {path.name: path for path in pool_dir.glob("*.poscar")}
    if len(rows) != len(flat_files):
        raise ValueError(
            f"Manifest/flat-pool count mismatch: manifest={len(rows)} flat={len(flat_files)}"
        )
    source_pattern = re.compile(rf"^{re.escape(element)}-(\d{{5}})-(\d+)\.poscar$")
    entries: list[PoolEntry] = []
    seen_flat: set[str] = set()
    seen_minimized: set[Path] = set()
    seen_raw_pressure: set[tuple[int, int]] = set()

    for row in rows:
        flat_name = row["new_name"]
        rss_source_path = row["original_path"]
        flat_path = flat_files.get(flat_name)
        if flat_path is None or flat_name in seen_flat:
            raise ValueError(f"Invalid or duplicate flat RSS file in manifest: {flat_name}")
        minimized_path = safe_child(minimized_dir.parent, rss_source_path)
        if not minimized_path.is_file() or minimized_path in seen_minimized:
            raise ValueError(f"Invalid or duplicate minimized RSS source: {rss_source_path}")
        if minimized_path.parent != minimized_dir:
            raise ValueError(f"Manifest source does not belong to {minimized_dir}: {rss_source_path}")
        match = source_pattern.match(minimized_path.name)
        if not match:
            raise ValueError(f"Unexpected minimized RSS file name: {minimized_path.name}")
        raw_index, pressure_index = map(int, match.groups())
        if pressure_index >= len(pressures_bar):
            raise ValueError(f"Unknown Mini pressure index in {minimized_path.name}")
        raw_path, raw_natoms = raw_sources.get(raw_index, (None, None))
        if raw_path is None:
            raise ValueError(f"Minimized source has no raw RSS source: {minimized_path.name}")
        key = (raw_index, pressure_index)
        if key in seen_raw_pressure:
            raise ValueError(f"Duplicate raw/pressure source: {minimized_path.name}")
        seen_flat.add(flat_name)
        seen_minimized.add(minimized_path)
        seen_raw_pressure.add(key)
        flat_digest = sha256(flat_path)
        minimized_digest = sha256(minimized_path)
        if key in mini_failures:
            exclusion_rows.append(
                mini_failure_row(
                    mini_failures[key],
                    raw_path,
                    raw_natoms,
                    minimized_path,
                    flat_path,
                    rss_source_path,
                )
            )
            continue
        flat_atoms = read_unary_atoms(flat_path, element)
        minimized_atoms = read_unary_atoms(minimized_path, element)
        if len(flat_atoms) != len(minimized_atoms):
            raise ValueError(f"Flat/minimized atom-count mismatch: {flat_path.name}")
        if len(minimized_atoms) != raw_natoms:
            raise ValueError(
                f"Minimized/raw atom-count mismatch: {minimized_path.name} has "
                f"{len(minimized_atoms)} atoms but {raw_path.name} has {raw_natoms}"
            )
        if flat_digest != minimized_digest:
            raise ValueError(f"Flat/minimized content mismatch: {flat_path.name}")
        entries.append(
            PoolEntry(
                flat_path=flat_path,
                rss_source_path=rss_source_path,
                minimized_path=minimized_path,
                raw_path=raw_path,
                raw_index=raw_index,
                pressure_index=pressure_index,
                natoms=raw_natoms,
                mini_pressure_bar=pressures_bar[pressure_index],
                flat_sha256=flat_digest,
                minimized_sha256=minimized_digest,
            )
        )

    if seen_flat != set(flat_files):
        raise ValueError("Manifest does not cover every flat RSS POSCAR")
    expected_keys = {(raw_index, pressure_index) for raw_index in raw_sources for pressure_index in range(len(pressures_bar))}
    unknown_failure_keys = set(mini_failures) - expected_keys
    if unknown_failure_keys:
        raise ValueError(f"Mini failure log has invalid raw/pressure keys: {sorted(unknown_failure_keys)[:10]}")
    missing_nonfailed = expected_keys - seen_raw_pressure - set(mini_failures)
    if missing_nonfailed:
        raise ValueError(
            "Minimized RSS raw/pressure provenance is incomplete outside the "
            f"logged Mini failures: {sorted(missing_nonfailed)[:10]}"
        )
    for key in sorted(set(mini_failures) - seen_raw_pressure):
        raw_index, pressure_index = key
        raw_path, raw_natoms = raw_sources[raw_index]
        minimized_path = minimized_dir / f"{element}-{raw_index:05d}-{pressure_index}.poscar"
        exclusion_rows.append(
            mini_failure_row(
                mini_failures[key],
                raw_path,
                raw_natoms,
                minimized_path,
                None,
                "",
            )
        )
    counts = Counter((entry.natoms, entry.pressure_index) for entry in entries)
    expected_counts = Counter(
        (raw_sources[raw_index][1], pressure_index)
        for raw_index, pressure_index in expected_keys - set(mini_failures)
    )
    if counts != expected_counts:
        raise ValueError(f"RSS atom-count/pressure coverage mismatch: {dict(sorted(counts.items()))}")
    return sorted(entries, key=lambda entry: (entry.natoms, entry.pressure_index, entry.raw_index))


def write_csv(path: Path, rows: list[dict], fields: tuple[str, ...]) -> None:
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def materialize_and_score(
    entries: list[PoolEntry],
    element: str,
    output_root: Path,
    jnn_paths: list[Path],
    progress_interval: int,
    exclusion_rows: list[dict] | None = None,
    mini_failure_log: Path | None = None,
) -> None:
    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite RSS selection root: {output_root}")
    if not output_root.parent.is_dir():
        raise FileNotFoundError(f"Missing RSS selection parent directory: {output_root.parent}")
    temporary = output_root.parent / f".{output_root.name}.tmp-{os.getpid()}"
    if temporary.exists():
        raise FileExistsError(f"Refusing existing temporary RSS selection root: {temporary}")
    exclusion_rows = exclusion_rows or []

    try:
        temporary.mkdir()
        archive_dir = temporary / "source-frames"
        archive_dir.mkdir()
        calculators = build_calculators(jnn_paths)
        all_rows: list[dict] = []
        provenance_rows: list[dict] = []
        grouped: dict[tuple[int, int, float], list[PoolEntry]] = {}
        for entry in entries:
            grouped.setdefault(
                (entry.natoms, entry.pressure_index, entry.mini_pressure_bar), []
            ).append(entry)

        total = 0
        for (natoms, pressure_index, pressure_bar), source_entries in sorted(grouped.items()):
            pressure_label = format_bar(pressure_bar)
            trajectory = f"rss-n{natoms}-p{pressure_label}bar"
            archive_path = archive_dir / f"{trajectory}.xyz"
            # The temporary archive is moved atomically; records must name its final path.
            recorded_archive_path = output_root / "source-frames" / archive_path.name
            pressure_gpa = pressure_bar / 10000.0
            for frame, entry in enumerate(source_entries):
                atoms = read_unary_atoms(entry.flat_path, element)
                positions = wrap_positions(atoms.get_positions(), atoms.get_cell(), atoms.get_pbc())
                atoms.set_positions(positions)
                uncertainty, max_force, max_force_model0 = score_atoms(atoms, calculators)
                write(archive_path, atoms, format="extxyz", append=frame > 0)
                base = {
                    "trajectory": trajectory,
                    "trajectory_path": str(recorded_archive_path),
                    "frame": frame,
                    "natoms": entry.natoms,
                    "mini_pressure_bar": pressure_bar,
                    "pressure_index": pressure_index,
                    "raw_index": entry.raw_index,
                    "rss_source_file": entry.flat_path.name,
                    "rss_source_path": entry.rss_source_path,
                    "minimized_source_path": str(entry.minimized_path),
                    "raw_source_path": str(entry.raw_path),
                    "flat_sha256": entry.flat_sha256,
                    "minimized_sha256": entry.minimized_sha256,
                }
                provenance_rows.append(base)
                all_rows.append(
                    {
                        "pressure_gpa": pressure_gpa,
                        "scale_factor": "",
                        "source_type": "rss_mini",
                        "source_value": pressure_gpa,
                        **base,
                        "uncertainty": uncertainty,
                        "uncertainty_bin": "",
                        "volume_per_atom": float(atoms.get_volume() / len(atoms)),
                        "max_force": max_force,
                        "max_force_model0": max_force_model0,
                        "instant_pressure_gpa": "",
                        "discarded_equilibration": False,
                        "selected_candidate": False,
                        "candidate_id": "",
                        "candidate_file": "",
                        "selection_rank_in_bin": "",
                        "cur_score": "",
                        "final_selected": False,
                    }
                )
                total += 1
                if progress_interval and total % progress_interval == 0:
                    print(
                        f"RSS all-frame scoring: structures={total}/{len(entries)} "
                        f"last_U={uncertainty:.8f}",
                        flush=True,
                    )

        if total != len(entries):
            raise RuntimeError(f"Scored {total} RSS structures, expected {len(entries)}")
        write_csv(temporary / "uncertainty_all_frames.csv", all_rows, ALL_FRAME_FIELDS)
        write_csv(temporary / "rss_frame_provenance.csv", provenance_rows, PROVENANCE_FIELDS)
        write_csv(
            temporary / "mini_failure_exclusions.csv",
            exclusion_rows,
            MINI_FAILURE_FIELDS,
        )
        with (temporary / "score_parameters.txt").open("x", encoding="utf-8") as handle:
            handle.write(f"element={element}\n")
            handle.write(f"committee_size={len(jnn_paths)}\n")
            handle.write(f"scored_structures={total}\n")
            handle.write(f"source_archives={len(grouped)}\n")
            handle.write(f"mini_failure_exclusions={len(exclusion_rows)}\n")
            if mini_failure_log is not None:
                handle.write(
                    f"mini_failure_log={mini_failure_log}; "
                    f"sha256={sha256(mini_failure_log)}\n"
                )
            for path in jnn_paths:
                handle.write(f"jnn={path}; sha256={sha256(path)}\n")
        os.replace(temporary, output_root)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def main() -> None:
    args = parse_args()
    set_default_thread_limits()
    natoms_list = parse_int_list(args.natoms_list)
    pressures_bar = parse_float_list(args.mini_press_list)
    pool_dir = Path(args.pool_dir)
    manifest_path = Path(args.manifest)
    minimized_dir = Path(args.minimized_dir)
    raw_dir = Path(args.raw_dir)
    output_root = Path(args.output_root)
    if not pool_dir.is_dir() or not minimized_dir.is_dir() or not raw_dir.is_dir():
        raise FileNotFoundError("Missing RSS flat-pool, minimized, or raw directory")
    jnn_paths = sorted_jnns(args.jnn_glob)
    raw_sources = load_raw_sources(
        raw_dir, args.element, natoms_list, args.raw_count_per_natoms
    )
    mini_failure_log = Path(args.mini_failure_log) if args.mini_failure_log else None
    mini_failures = (
        parse_mini_failures(mini_failure_log, args.element, raw_sources, pressures_bar)
        if mini_failure_log is not None
        else {}
    )
    exclusion_rows: list[dict] = []
    entries = load_entries(
        args.element,
        pool_dir,
        manifest_path,
        minimized_dir,
        raw_sources,
        natoms_list,
        pressures_bar,
        args.raw_count_per_natoms,
        mini_failures,
        exclusion_rows,
    )
    print(
        f"RSS pool validated: element={args.element} raw={len(raw_sources)} "
        f"eligible_minimized_flat={len(entries)} "
        f"excluded_mini_failures={len(exclusion_rows)} committee={len(jnn_paths)}",
        flush=True,
    )
    materialize_and_score(
        entries,
        args.element,
        output_root,
        jnn_paths,
        args.progress_interval,
        exclusion_rows,
        mini_failure_log,
    )
    print(
        f"RSS all-frame scoring complete: {output_root / 'uncertainty_all_frames.csv'}",
        flush=True,
    )


if __name__ == "__main__":
    main()
