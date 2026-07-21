#!/usr/bin/env python3
"""Global uncertainty-window and CUR-leverage selection for MD trajectories."""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from ase.geometry import wrap_positions
from ase.io import iread, write
from scipy.linalg import svd

SCRIPT_DIR = Path(globals().get("__file__", sys.argv[0])).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from CUR import compute_spherical_chebyshev_features, normalize_columns  # noqa: E402
from uncertainty_selection import (  # noqa: E402
    build_calculators,
    uncertainty_and_max_force,
)


SCORE_FIELDS = [
    "candidate_local_index",
    "source_label",
    "phase",
    "pressure_gpa",
    "trajectory",
    "frame",
    "uncertainty_eVA",
    "uncertainty_meVA",
    "max_force_eVA",
    "natoms",
    "volume_A3",
    "volume_per_atom_A3",
]


def sorted_jnn_paths(root: Path) -> list[Path]:
    def sort_key(path: Path) -> tuple[int, str]:
        match = re.search(r"train-(\d+)", str(path.parent))
        return (int(match.group(1)) if match else sys.maxsize, str(path))

    paths = sorted(root.glob("train-*/*.jnn"), key=sort_key)
    if len(paths) < 2:
        raise ValueError(
            f"Expected at least two committee JNN files under {root}, found {len(paths)}"
        )
    return paths


def safe_label(text: str) -> str:
    label = re.sub(r"[^A-Za-z0-9_.-]+", "_", text.strip())
    if not label:
        raise ValueError("source-label must contain a path-safe character")
    return label


def feature_count(n_max: int, l_max: int) -> int:
    return (n_max * (n_max + 1) // 2) * l_max


def write_csv_atomic(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    tmp_path = path.with_name(f".{path.name}.tmp")
    with tmp_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp_path, path)


def save_features_atomic(path: Path, features: np.ndarray) -> None:
    tmp_path = path.with_name(f".{path.name}.tmp")
    with tmp_path.open("wb") as handle:
        np.savez_compressed(handle, features=features)
    os.replace(tmp_path, path)


def score_trajectory(args: argparse.Namespace) -> None:
    trajectory = args.trajectory.resolve()
    if not trajectory.is_file():
        raise FileNotFoundError(f"Missing trajectory: {trajectory}")
    if not 0.0 <= args.u_min <= args.u_max:
        raise ValueError("Require 0 <= u-min <= u-max")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = safe_label(args.source_label)
    csv_path = args.output_dir / f"{stem}.csv"
    feature_path = args.output_dir / f"{stem}.npz"
    done_path = args.output_dir / f"{stem}.done"
    outputs = (csv_path, feature_path, done_path)

    if done_path.exists() and not args.overwrite:
        print(f"score skip complete source={args.source_label}", flush=True)
        return
    existing = [path for path in outputs if path.exists()]
    if existing and not args.overwrite:
        raise FileExistsError(
            "Partial score outputs already exist; use --overwrite after review: "
            + ", ".join(str(path) for path in existing)
        )
    if args.overwrite:
        for path in outputs:
            path.unlink(missing_ok=True)

    jnn_paths = sorted_jnn_paths(args.jnn_root)
    calculators = build_calculators(jnn_paths)
    rows: list[dict] = []
    descriptors: list[np.ndarray] = []
    frames_seen = 0

    for frame, atoms in enumerate(iread(str(trajectory), index=":")):
        positions = wrap_positions(
            atoms.get_positions(), atoms.get_cell(), atoms.get_pbc()
        )
        atoms.set_positions(positions)
        uncertainty, max_force = uncertainty_and_max_force(atoms, calculators)
        if args.u_min <= uncertainty <= args.u_max:
            descriptor = compute_spherical_chebyshev_features(
                atoms, r_c=args.r_c, n_max=args.n_max, l_max=args.l_max
            )
            descriptors.append(descriptor)
            volume = float(atoms.get_volume())
            natoms = len(atoms)
            rows.append(
                {
                    "candidate_local_index": len(rows),
                    "source_label": args.source_label,
                    "phase": args.phase,
                    "pressure_gpa": args.pressure_gpa,
                    "trajectory": str(trajectory),
                    "frame": frame,
                    "uncertainty_eVA": float(uncertainty),
                    "uncertainty_meVA": 1000.0 * float(uncertainty),
                    "max_force_eVA": float(max_force),
                    "natoms": natoms,
                    "volume_A3": volume,
                    "volume_per_atom_A3": volume / natoms,
                }
            )
        frames_seen += 1
        if args.progress_interval and frames_seen % args.progress_interval == 0:
            print(
                f"score progress source={args.source_label} frames={frames_seen} "
                f"candidates={len(rows)}",
                flush=True,
            )
        if args.max_frames and frames_seen >= args.max_frames:
            break

    n_features = feature_count(args.n_max, args.l_max)
    feature_matrix = (
        np.column_stack(descriptors)
        if descriptors
        else np.empty((n_features, 0), dtype=float)
    )
    if feature_matrix.shape != (n_features, len(rows)):
        raise RuntimeError(
            f"Feature shape mismatch: {feature_matrix.shape}, rows={len(rows)}"
        )

    write_csv_atomic(csv_path, rows, SCORE_FIELDS)
    save_features_atomic(feature_path, feature_matrix)
    done_path.write_text(
        f"frames_seen={frames_seen}\ncandidates={len(rows)}\n",
        encoding="utf-8",
    )
    print(
        f"score complete source={args.source_label} frames={frames_seen} "
        f"candidates={len(rows)}",
        flush=True,
    )


def read_score_outputs(scores_dir: Path) -> tuple[list[dict], np.ndarray]:
    rows: list[dict] = []
    matrices: list[np.ndarray] = []
    csv_paths = sorted(scores_dir.glob("*.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"No score CSV files found in {scores_dir}")

    for csv_path in csv_paths:
        feature_path = csv_path.with_suffix(".npz")
        done_path = csv_path.with_suffix(".done")
        if not feature_path.is_file() or not done_path.is_file():
            raise FileNotFoundError(f"Incomplete score output for {csv_path.stem}")
        with csv_path.open(newline="", encoding="utf-8") as handle:
            source_rows = list(csv.DictReader(handle))
        with np.load(feature_path) as data:
            matrix = np.asarray(data["features"], dtype=float)
        if matrix.ndim != 2 or matrix.shape[1] != len(source_rows):
            raise ValueError(
                f"Score feature mismatch for {csv_path}: "
                f"shape={matrix.shape}, rows={len(source_rows)}"
            )
        for expected, row in enumerate(source_rows):
            if int(row["candidate_local_index"]) != expected:
                raise ValueError(f"Non-contiguous candidate index in {csv_path}")
            row["candidate_global_index"] = len(rows)
            rows.append(row)
        matrices.append(matrix)

    feature_dims = {matrix.shape[0] for matrix in matrices}
    if len(feature_dims) != 1:
        raise ValueError(f"Inconsistent feature dimensions: {sorted(feature_dims)}")
    return rows, np.hstack(matrices)


def geometry_diagnostics(atoms) -> dict[str, float]:
    volume = float(atoms.get_volume())
    natoms = len(atoms)
    angles = np.asarray(atoms.cell.angles(), dtype=float)
    vectors = np.asarray(atoms.cell.array, dtype=float)
    heights = []
    for axis in range(3):
        other = [value for value in range(3) if value != axis]
        area = float(np.linalg.norm(np.cross(vectors[other[0]], vectors[other[1]])))
        heights.append(volume / area if area > 0.0 else 0.0)

    min_pair = float("nan")
    if natoms > 1:
        distances = np.asarray(atoms.get_all_distances(mic=True), dtype=float)
        np.fill_diagonal(distances, np.inf)
        min_pair = float(np.min(distances))
    return {
        "cell_angle_min_deg": float(np.min(angles)),
        "cell_angle_max_deg": float(np.max(angles)),
        "interplanar_height_min_A": float(np.min(heights)),
        "min_pair_distance_A": min_pair,
    }


def selected_atoms(rows: list[dict]) -> dict[int, object]:
    wanted: dict[str, dict[int, int]] = defaultdict(dict)
    for row in rows:
        wanted[row["trajectory"]][int(row["frame"])] = int(row["selected_rank"])

    atoms_by_rank: dict[int, object] = {}
    for trajectory, frame_to_rank in wanted.items():
        remaining = set(frame_to_rank)
        for frame, atoms in enumerate(iread(trajectory, index=":")):
            if frame not in remaining:
                continue
            atoms_by_rank[frame_to_rank[frame]] = atoms
            remaining.remove(frame)
            if not remaining:
                break
        if remaining:
            raise RuntimeError(
                f"Missing selected frames in {trajectory}: {sorted(remaining)}"
            )
    return atoms_by_rank


def distribution_rows(rows: list[dict]) -> list[dict]:
    output: list[dict] = []
    group_specs = (
        ("phase", lambda row: row["phase"]),
        ("pressure_gpa", lambda row: row["pressure_gpa"]),
        (
            "phase_pressure",
            lambda row: f"{row['phase']}_P-{row['pressure_gpa']}GPa",
        ),
        ("trajectory", lambda row: row["source_label"]),
    )
    total = len(rows)
    for group_name, value_fn in group_specs:
        counts = Counter(value_fn(row) for row in rows)
        for value, count in sorted(counts.items()):
            output.append(
                {
                    "group": group_name,
                    "value": value,
                    "count": count,
                    "fraction": count / total,
                }
            )
    return output


def select_global(args: argparse.Namespace) -> None:
    if args.target <= 0:
        raise ValueError("target must be positive")
    rows, feature_matrix = read_score_outputs(args.scores_dir)
    candidate_count = len(rows)
    if candidate_count < args.target:
        raise ValueError(
            f"Only {candidate_count} candidates are available for target {args.target}"
        )
    if feature_matrix.shape[1] != candidate_count:
        raise RuntimeError("Candidate/feature count mismatch")

    output_dir = args.output_dir
    selected_dir = output_dir / "cur-selected-poscar"
    generated_paths = (
        selected_dir,
        output_dir / "uncertainty_candidates.csv",
        output_dir / "selected_summary.csv",
        output_dir / "selected_distribution.csv",
        output_dir / "selection_metadata.txt",
    )
    existing = [path for path in generated_paths if path.exists()]
    if existing and not args.overwrite:
        raise FileExistsError(
            "Selection outputs already exist; use --overwrite after review: "
            + ", ".join(str(path) for path in existing)
        )
    if args.overwrite:
        for path in generated_paths:
            if path.is_dir():
                for child in path.iterdir():
                    if child.is_file():
                        child.unlink()
                path.rmdir()
            else:
                path.unlink(missing_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    selected_dir.mkdir()

    x_normalized = normalize_columns(feature_matrix)
    _, singular_values, vh_matrix = svd(x_normalized, full_matrices=False)
    if not len(singular_values) or singular_values[0] <= 0.0:
        raise RuntimeError("Candidate descriptor matrix has no usable CUR modes")
    tolerance = (
        max(x_normalized.shape) * np.finfo(float).eps * singular_values[0]
    )
    rank = int(np.sum(singular_values > tolerance))
    leverage = np.sum(vh_matrix[:rank, :] ** 2, axis=0)
    selected_indices = sorted(
        range(candidate_count), key=lambda idx: (-float(leverage[idx]), idx)
    )[: args.target]

    selected_rows: list[dict] = []
    selected_rank = {idx: rank_id for rank_id, idx in enumerate(selected_indices, 1)}
    for idx, row in enumerate(rows):
        row["cur_leverage_score"] = float(leverage[idx])
        row["final_selected"] = 1 if idx in selected_rank else 0
        row["selected_rank"] = selected_rank.get(idx, "")
        if idx in selected_rank:
            selected_rows.append(row)
    selected_rows.sort(key=lambda row: int(row["selected_rank"]))

    x_selected = x_normalized[:, selected_indices]
    similarities = x_selected.T @ x_selected
    np.fill_diagonal(similarities, -np.inf)
    max_selected_similarity = float(np.max(similarities))

    atoms_by_rank = selected_atoms(selected_rows)
    for row in selected_rows:
        rank_id = int(row["selected_rank"])
        atoms = atoms_by_rank[rank_id]
        positions = wrap_positions(
            atoms.get_positions(), atoms.get_cell(), atoms.get_pbc()
        )
        atoms.set_positions(positions)
        row.update(geometry_diagnostics(atoms))
        pressure_text = str(row["pressure_gpa"]).replace(".", "p")
        out_name = (
            f"{rank_id:06d}_{row['phase']}_P-{pressure_text}GPa_"
            f"frame-{int(row['frame']):06d}.poscar"
        )
        row["selected_file"] = out_name
        write(selected_dir / out_name, atoms, format="vasp")

    candidate_fields = list(SCORE_FIELDS) + [
        "candidate_global_index",
        "cur_leverage_score",
        "final_selected",
        "selected_rank",
    ]
    selected_fields = candidate_fields + [
        "selected_file",
        "cell_angle_min_deg",
        "cell_angle_max_deg",
        "interplanar_height_min_A",
        "min_pair_distance_A",
    ]
    write_csv_atomic(
        output_dir / "uncertainty_candidates.csv", rows, candidate_fields
    )
    write_csv_atomic(
        output_dir / "selected_summary.csv", selected_rows, selected_fields
    )
    distributions = distribution_rows(selected_rows)
    write_csv_atomic(
        output_dir / "selected_distribution.csv",
        distributions,
        ["group", "value", "count", "fraction"],
    )

    uncertainty_values = np.asarray(
        [float(row["uncertainty_eVA"]) for row in rows], dtype=float
    )
    selected_uncertainty = np.asarray(
        [float(row["uncertainty_eVA"]) for row in selected_rows], dtype=float
    )
    metadata = (
        f"candidate_count={candidate_count}\n"
        f"selected_count={len(selected_rows)}\n"
        f"descriptor_shape={x_normalized.shape[0]}x{x_normalized.shape[1]}\n"
        f"descriptor_rank={rank}\n"
        f"cur_method=deterministic_full_rank_leverage\n"
        f"max_selected_descriptor_similarity={max_selected_similarity:.10g}\n"
        f"candidate_uncertainty_eVA_min={uncertainty_values.min():.10g}\n"
        f"candidate_uncertainty_eVA_max={uncertainty_values.max():.10g}\n"
        f"selected_uncertainty_eVA_min={selected_uncertainty.min():.10g}\n"
        f"selected_uncertainty_eVA_max={selected_uncertainty.max():.10g}\n"
    )
    (output_dir / "selection_metadata.txt").write_text(metadata, encoding="utf-8")

    print(metadata, end="", flush=True)
    for row in distributions:
        if row["group"] == "phase_pressure":
            print(
                f"source {row['value']}: {row['count']} "
                f"({100.0 * float(row['fraction']):.1f}%)",
                flush=True,
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Filter MD frames by committee uncertainty, then apply one global "
            "unstratified CUR-leverage selection."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    score = subparsers.add_parser("score", help="Score one trajectory")
    score.add_argument("--trajectory", type=Path, required=True)
    score.add_argument("--source-label", required=True)
    score.add_argument("--phase", required=True)
    score.add_argument("--pressure-gpa", type=float, required=True)
    score.add_argument("--jnn-root", type=Path, required=True)
    score.add_argument("--output-dir", type=Path, required=True)
    score.add_argument("--u-min", type=float, required=True)
    score.add_argument("--u-max", type=float, required=True)
    score.add_argument("--r-c", type=float, default=6.0)
    score.add_argument("--n-max", type=int, default=5)
    score.add_argument("--l-max", type=int, default=6)
    score.add_argument("--progress-interval", type=int, default=500)
    score.add_argument("--max-frames", type=int, default=0)
    score.add_argument("--overwrite", action="store_true")
    score.set_defaults(func=score_trajectory)

    select = subparsers.add_parser(
        "select", help="Combine all scored candidates and run global CUR"
    )
    select.add_argument("--scores-dir", type=Path, required=True)
    select.add_argument("--output-dir", type=Path, required=True)
    select.add_argument("--target", type=int, default=200)
    select.add_argument("--overwrite", action="store_true")
    select.set_defaults(func=select_global)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
