#!/usr/bin/env python3
"""Uncertainty-stratified, base-aware quota-CUR selection for RSS structures."""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from ase.io import read, write
from scipy.linalg import svd
from scipy.optimize import Bounds, LinearConstraint, milp

SCRIPT_DIR = Path(globals().get("__file__", sys.argv[0])).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from CUR import build_feature_matrix, normalize_columns, read_structures  # noqa: E402
from uncertainty_selection import (  # noqa: E402
    build_calculators,
    uncertainty_and_max_force,
)


DEFAULT_QUOTAS = {"Q1": 38, "Q2": 38, "Q3": 37, "Q4": 37, "Q5": 0}
SCORE_INTEGER_FIELDS = ("orig_index", "natoms")
SCORE_FLOAT_FIELDS = (
    "volume_A3",
    "volume_per_atom_A3",
    "cell_angle_min_deg",
    "cell_angle_max_deg",
    "interplanar_height_min_A",
    "min_pair_distance_A",
    "uncertainty_eVA",
    "max_force_eVA",
)
SCORE_REQUIRED_FIELDS = {
    "source_file",
    "source_path",
    "pressure_index",
    *SCORE_INTEGER_FIELDS,
    *SCORE_FLOAT_FIELDS,
}


def sorted_jnn_paths(root: Path) -> list[Path]:
    def key(path: Path) -> tuple[int, str]:
        match = re.search(r"train-(\d+)", str(path.parent))
        return (int(match.group(1)) if match else sys.maxsize, str(path))

    paths = sorted(root.glob("train-*/*.jnn"), key=key)
    if len(paths) < 2:
        raise ValueError(f"Expected at least two committee JNN files under {root}, found {len(paths)}")
    return paths


def parse_quotas(text: str) -> dict[str, int]:
    quotas: dict[str, int] = {}
    for item in text.split(","):
        label, value = item.split("=", 1)
        label = label.strip()
        count = int(value)
        if not label or count < 0:
            raise argparse.ArgumentTypeError("quotas must look like Q1=38,Q2=38")
        quotas[label] = count
    if not quotas or sum(quotas.values()) <= 0:
        raise argparse.ArgumentTypeError("at least one quota must be positive")
    return quotas


def parse_natoms_pressure_quotas(text: str) -> dict[tuple[int, str], int]:
    """Parse exact joint targets such as ``3:0=2,3:1=3``."""
    targets: dict[tuple[int, str], int] = {}
    try:
        items = [item.strip() for item in text.split(",") if item.strip()]
        for item in items:
            group, value = item.split("=", 1)
            natoms_text, pressure = group.split(":", 1)
            key = (int(natoms_text), pressure.strip())
            target = int(value)
            if key[0] <= 0 or not key[1] or target <= 0 or key in targets:
                raise ValueError
            targets[key] = target
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "joint quotas must look like 3:0=2,3:1=3 with unique positive targets"
        ) from exc
    if not targets:
        raise argparse.ArgumentTypeError("at least one joint quota is required")
    return targets


def read_manifest(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    result: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            result[row["new_name"]] = row["original_path"]
    return result


def pressure_index(source_path: str) -> str:
    match = re.search(r"-(\d+)\.(?:poscar|vasp)$", Path(source_path).name, re.IGNORECASE)
    return match.group(1) if match else ""


def geometry_diagnostics(atoms) -> dict[str, float]:
    volume = float(atoms.get_volume())
    natoms = len(atoms)
    angles = np.asarray(atoms.cell.angles(), dtype=float)
    vectors = np.asarray(atoms.cell.array, dtype=float)
    heights = []
    for i in range(3):
        other = [j for j in range(3) if j != i]
        area = float(np.linalg.norm(np.cross(vectors[other[0]], vectors[other[1]])))
        heights.append(volume / area if area > 0.0 else 0.0)

    min_pair = float("nan")
    if natoms > 1:
        distances = np.asarray(atoms.get_all_distances(mic=True), dtype=float)
        np.fill_diagonal(distances, np.inf)
        min_pair = float(np.min(distances))

    return {
        "natoms": natoms,
        "volume_A3": volume,
        "volume_per_atom_A3": volume / natoms,
        "cell_angle_min_deg": float(np.min(angles)),
        "cell_angle_max_deg": float(np.max(angles)),
        "interplanar_height_min_A": float(np.min(heights)),
        "min_pair_distance_A": min_pair,
    }


def orthogonal_base_projection(
    x_candidates: np.ndarray,
    x_base: np.ndarray,
    variance_fraction: float,
) -> tuple[np.ndarray, np.ndarray, int, float]:
    if not 0.0 < variance_fraction <= 1.0:
        raise ValueError("variance_fraction must be in (0, 1]")
    max_base_similarity = np.max(x_base.T @ x_candidates, axis=0)
    u_matrix, singular_values, _ = svd(x_base, full_matrices=False)
    if len(singular_values) == 0 or singular_values[0] <= 0.0:
        return x_candidates.copy(), max_base_similarity, 0, 0.0
    tolerance = max(x_base.shape) * np.finfo(float).eps * singular_values[0]
    numerical_rank = int(np.sum(singular_values > tolerance))
    if numerical_rank == 0:
        return x_candidates.copy(), max_base_similarity, 0, 0.0
    variance = singular_values[:numerical_rank] ** 2
    cumulative = np.cumsum(variance) / np.sum(variance)
    rank = min(int(np.searchsorted(cumulative, variance_fraction) + 1), numerical_rank)
    captured = float(cumulative[rank - 1])
    basis = u_matrix[:, :rank]
    residual = x_candidates - basis @ (basis.T @ x_candidates)
    return residual, max_base_similarity, rank, captured


def assign_layers(
    rows: list[dict],
    layer_count: int,
    mode: str = "global",
) -> dict[str, list[int]]:
    if layer_count <= 0:
        raise ValueError("layer_count must be positive")
    if mode not in {"global", "natoms-pressure"}:
        raise ValueError(f"Unknown layer mode: {mode}")

    layers = {f"Q{layer_index}": [] for layer_index in range(1, layer_count + 1)}
    if mode == "global":
        groups = {"all": list(range(len(rows)))}
    else:
        groups: dict[tuple[int, str], list[int]] = {}
        for idx, row in enumerate(rows):
            key = (int(row["natoms"]), str(row["pressure_index"]))
            groups.setdefault(key, []).append(idx)

    for group, indices in sorted(groups.items(), key=lambda item: str(item[0])):
        if len(indices) < layer_count:
            raise ValueError(
                f"Layer group {group} has {len(indices)} candidates, fewer than "
                f"--layer-count={layer_count}"
            )
        ranked = sorted(
            indices,
            key=lambda idx: (
                float(rows[idx]["uncertainty_eVA"]),
                int(rows[idx]["orig_index"]),
            ),
        )
        chunks = np.array_split(np.asarray(ranked, dtype=int), layer_count)
        for layer_index, chunk in enumerate(chunks, start=1):
            label = f"Q{layer_index}"
            layer_indices = [int(value) for value in chunk]
            layers[label].extend(layer_indices)
            for idx in layer_indices:
                rows[idx]["uncertainty_layer"] = label
    return layers


def filter_rows_by_uncertainty(
    rows: list[dict],
    u_min: float | None,
    u_max: float | None,
) -> list[int]:
    retained: list[int] = []
    for idx, row in enumerate(rows):
        uncertainty = float(row["uncertainty_eVA"])
        keep = (u_min is None or uncertainty >= u_min) and (
            u_max is None or uncertainty <= u_max
        )
        row["retained_by_u_filter"] = keep
        if keep:
            retained.append(idx)
    return retained


def load_score_rows(
    score_csv: Path,
    files: list[Path],
    structures: list,
    manifest: dict[str, str],
) -> list[dict]:
    if not score_csv.is_file():
        raise FileNotFoundError(f"Saved score CSV does not exist: {score_csv}")
    with score_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Saved score CSV has no header: {score_csv}")
        missing = SCORE_REQUIRED_FIELDS.difference(reader.fieldnames)
        if missing:
            raise ValueError(
                f"Saved score CSV is missing required columns: {sorted(missing)}"
            )
        score_rows = list(reader)
    if len(score_rows) != len(files):
        raise ValueError(
            f"Saved score CSV has {len(score_rows)} rows, expected {len(files)}"
        )

    rows: list[dict] = []
    geometry_fields = (
        "volume_A3",
        "volume_per_atom_A3",
        "cell_angle_min_deg",
        "cell_angle_max_deg",
        "interplanar_height_min_A",
        "min_pair_distance_A",
    )
    for index, (score_row, path, atoms) in enumerate(
        zip(score_rows, files, structures), start=1
    ):
        try:
            orig_index = int(score_row["orig_index"])
            natoms = int(score_row["natoms"])
            numeric = {
                field: float(score_row[field])
                for field in SCORE_FLOAT_FIELDS
            }
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Saved score CSV has non-numeric data in row {index}: {score_csv}"
            ) from exc
        if orig_index != index or score_row["source_file"] != path.name:
            raise ValueError(
                f"Saved score CSV does not match input file order at row {index}: "
                f"expected {path.name}, found {score_row['source_file']}"
            )
        expected_source_path = manifest.get(path.name, str(path))
        if score_row["source_path"] != expected_source_path:
            raise ValueError(
                f"Saved score CSV source path mismatch for {path.name}: "
                f"expected {expected_source_path}, found {score_row['source_path']}"
            )
        expected_pressure = pressure_index(expected_source_path)
        if str(score_row["pressure_index"]) != expected_pressure:
            raise ValueError(
                f"Saved score CSV Mini-pressure mismatch for {path.name}: "
                f"expected {expected_pressure}, found {score_row['pressure_index']}"
            )
        if natoms != len(atoms):
            raise ValueError(
                f"Saved score CSV natoms mismatch for {path.name}: "
                f"expected {len(atoms)}, found {natoms}"
            )
        if not all(np.isfinite(value) for value in numeric.values()):
            raise ValueError(f"Saved score CSV has non-finite diagnostics in row {index}")
        diagnostics = geometry_diagnostics(atoms)
        for field in geometry_fields:
            if not np.isclose(
                numeric[field],
                diagnostics[field],
                rtol=1.0e-10,
                atol=1.0e-10,
            ):
                raise ValueError(
                    f"Saved score CSV geometry mismatch for {path.name}, field {field}"
                )
        rows.append(
            {
                "orig_index": orig_index,
                "source_file": path.name,
                "source_path": expected_source_path,
                "natoms": natoms,
                **numeric,
                "pressure_index": expected_pressure,
                "uncertainty_layer": "",
                "retained_by_u_filter": True,
                "cur_rank": "",
                "cur_pass": "",
                "cur_score": "",
                "singular_value": "",
                "residual_norm": "",
                "max_similarity_selected": "",
                "max_similarity_base": "",
                "final_selected": False,
                "selected_file": "",
            }
        )
    return rows


def quota_cur_select(
    x_residual: np.ndarray,
    x_similarity: np.ndarray,
    candidate_layers: list[str],
    candidate_natoms: list[int],
    candidate_pressures: list[str],
    quotas: dict[str, int],
    natoms_targets: dict[int, int],
    pressure_targets: dict[str, int],
    max_base_similarity: np.ndarray,
    similarity_threshold: float | None,
    natoms_pressure_targets: dict[tuple[int, str], int] | None = None,
) -> tuple[list[int], list[dict], set[int]]:
    x_initial = x_residual.copy()
    selected: list[int] = []
    rejected: set[int] = set()
    records: list[dict] = []
    counts: Counter = Counter()
    natoms_counts: Counter = Counter()
    pressure_counts: Counter = Counter()
    natoms_pressure_counts: Counter = Counter()
    natoms_pressure_targets = natoms_pressure_targets or {}
    cur_pass = 1
    pass_start_count = 0

    while len(selected) < sum(quotas.values()):
        _, singular_values, vh_matrix = svd(x_residual, full_matrices=False)
        if len(singular_values) == 0 or singular_values[0] <= 1e-12:
            if len(selected) == pass_start_count:
                raise RuntimeError(
                    f"CUR pass {cur_pass} made no progress before residual exhaustion"
                )
            cur_pass += 1
            pass_start_count = len(selected)
            x_residual = x_initial.copy()
            x_residual[:, selected] = 0.0
            if rejected:
                x_residual[:, sorted(rejected)] = 0.0
            print(
                f"Starting CUR pass {cur_pass}; selected={len(selected)}/"
                f"{sum(quotas.values())}",
                flush=True,
            )
            continue
        scores = vh_matrix[0, :] ** 2
        for idx, layer in enumerate(candidate_layers):
            natoms = candidate_natoms[idx]
            pressure = candidate_pressures[idx]
            natoms_pressure = (natoms, pressure)
            if (
                idx in selected
                or idx in rejected
                or counts[layer] >= quotas.get(layer, 0)
                or (
                    natoms_targets
                    and natoms_counts[natoms] >= natoms_targets[natoms]
                )
                or (
                    pressure_targets
                    and pressure_counts[pressure] >= pressure_targets[pressure]
                )
                or (
                    natoms_pressure_targets
                    and natoms_pressure_counts[natoms_pressure]
                    >= natoms_pressure_targets[natoms_pressure]
                )
            ):
                scores[idx] = -1.0

        accepted = False
        while float(np.max(scores)) >= 0.0:
            idx = int(np.argmax(scores))
            max_selected_similarity = 0.0
            if similarity_threshold is not None and selected:
                similarities = x_similarity[:, selected].T @ x_similarity[:, idx]
                max_selected_similarity = float(np.max(similarities))
                if max_selected_similarity >= similarity_threshold:
                    rejected.add(idx)
                    scores[idx] = -1.0
                    x_residual[:, idx] = 0.0
                    continue

            vector = x_residual[:, idx].copy()
            norm_sq = float(np.dot(vector, vector))
            if norm_sq <= 1e-18:
                rejected.add(idx)
                scores[idx] = -1.0
                x_residual[:, idx] = 0.0
                continue

            selected.append(idx)
            layer = candidate_layers[idx]
            counts[layer] += 1
            natoms_counts[candidate_natoms[idx]] += 1
            pressure_counts[candidate_pressures[idx]] += 1
            natoms_pressure_counts[
                (candidate_natoms[idx], candidate_pressures[idx])
            ] += 1
            records.append(
                {
                    "cur_rank": len(selected),
                    "cur_pass": cur_pass,
                    "cur_score": float(scores[idx]),
                    "singular_value": float(singular_values[0]),
                    "residual_norm": float(np.sqrt(norm_sq)),
                    "max_similarity_selected": max_selected_similarity,
                    "max_similarity_base": float(max_base_similarity[idx]),
                }
            )
            projections = np.dot(vector, x_residual) / norm_sq
            x_residual -= np.outer(vector, projections)
            accepted = True
            break

        if not accepted:
            raise RuntimeError(f"Could not fill CUR quotas; current counts={dict(counts)}")

    expected = {label: count for label, count in quotas.items() if count > 0}
    actual = {label: counts[label] for label in expected}
    if actual != expected:
        raise RuntimeError(f"Final quota mismatch: expected={expected}, actual={actual}")
    if natoms_targets and dict(natoms_counts) != natoms_targets:
        raise RuntimeError(
            f"Final natoms quota mismatch: expected={natoms_targets}, "
            f"actual={dict(natoms_counts)}"
        )
    if pressure_targets and dict(pressure_counts) != pressure_targets:
        raise RuntimeError(
            f"Final pressure quota mismatch: expected={pressure_targets}, "
            f"actual={dict(pressure_counts)}"
        )
    if (
        natoms_pressure_targets
        and dict(natoms_pressure_counts) != natoms_pressure_targets
    ):
        raise RuntimeError(
            "Final natoms-pressure quota mismatch: "
            f"expected={natoms_pressure_targets}, "
            f"actual={dict(natoms_pressure_counts)}"
        )
    return selected, records, rejected


def quota_cur_select_milp(
    x_residual: np.ndarray,
    x_similarity: np.ndarray,
    candidate_layers: list[str],
    candidate_natoms: list[int],
    candidate_pressures: list[str],
    quotas: dict[str, int],
    natoms_targets: dict[int, int],
    pressure_targets: dict[str, int],
    max_base_similarity: np.ndarray,
    similarity_threshold: float | None,
    natoms_pressure_targets: dict[tuple[int, str], int] | None = None,
) -> tuple[list[int], list[dict], set[int]]:
    _, singular_values, vh_matrix = svd(x_residual, full_matrices=False)
    if len(singular_values) == 0 or singular_values[0] <= 1e-12:
        raise RuntimeError("Projected candidate matrix has no usable CUR modes")
    tolerance = max(x_residual.shape) * np.finfo(float).eps * singular_values[0]
    rank = int(np.sum(singular_values > tolerance))
    leverage = np.sum(vh_matrix[:rank, :] ** 2, axis=0)

    constraint_rows: list[np.ndarray] = []
    targets: list[float] = []

    def add_exact(values: list, target_map: dict) -> None:
        for value, target in target_map.items():
            constraint_rows.append(
                np.asarray([1.0 if item == value else 0.0 for item in values])
            )
            targets.append(float(target))

    add_exact(candidate_layers, {key: value for key, value in quotas.items() if value > 0})
    add_exact(candidate_natoms, natoms_targets)
    add_exact(candidate_pressures, pressure_targets)
    add_exact(
        list(zip(candidate_natoms, candidate_pressures)),
        natoms_pressure_targets or {},
    )
    matrix = np.vstack(constraint_rows)
    bounds = np.asarray(targets)
    result = milp(
        c=-leverage,
        integrality=np.ones(len(leverage), dtype=int),
        bounds=Bounds(np.zeros(len(leverage)), np.ones(len(leverage))),
        constraints=LinearConstraint(matrix, bounds, bounds),
        options={"disp": False},
    )
    if not result.success or result.x is None:
        raise RuntimeError(f"Quota-CUR MILP failed: {result.message}")

    selected = [int(idx) for idx in np.flatnonzero(result.x > 0.5)]
    expected_count = sum(quotas.values())
    if len(selected) != expected_count:
        raise RuntimeError(
            f"Quota-CUR MILP selected {len(selected)}, expected {expected_count}"
        )
    selected.sort(key=lambda idx: (-float(leverage[idx]), idx))

    records: list[dict] = []
    for rank_index, idx in enumerate(selected, start=1):
        max_selected_similarity = 0.0
        if rank_index > 1:
            previous = selected[: rank_index - 1]
            max_selected_similarity = float(
                np.max(x_similarity[:, previous].T @ x_similarity[:, idx])
            )
        records.append(
            {
                "cur_rank": rank_index,
                "cur_pass": "leverage-milp",
                "cur_score": float(leverage[idx]),
                "singular_value": float(singular_values[0]),
                "residual_norm": float(np.linalg.norm(x_residual[:, idx])),
                "max_similarity_selected": max_selected_similarity,
                "max_similarity_base": float(max_base_similarity[idx]),
            }
        )

    if similarity_threshold is not None:
        max_similarity = max(
            (float(record["max_similarity_selected"]) for record in records),
            default=0.0,
        )
        if max_similarity >= similarity_threshold:
            raise RuntimeError(
                f"Balanced quota-CUR maximum selected similarity {max_similarity:.8g} "
                f"exceeds threshold {similarity_threshold:.8g}"
            )
    return selected, records, set()


def equal_targets(values: list, target: int, label: str) -> dict:
    unique = sorted(set(values))
    if not unique:
        raise ValueError(f"No values available for {label} balancing")
    if target % len(unique) != 0:
        raise ValueError(
            f"Target {target} is not divisible by {len(unique)} {label} groups"
        )
    per_group = target // len(unique)
    return {value: per_group for value in unique}


def explicit_targets(values: list, targets: dict, target: int, label: str) -> dict:
    available = set(values)
    supplied = set(targets)
    missing = available - supplied
    extra = supplied - available
    if missing or extra:
        raise ValueError(
            f"Explicit {label} targets do not match candidates: "
            f"missing={sorted(missing)}, extra={sorted(extra)}"
        )
    if sum(targets.values()) != target:
        raise ValueError(
            f"Explicit {label} targets sum to {sum(targets.values())}, "
            f"expected {target}"
        )
    return dict(targets)


def validate_target_capacity(
    values: list,
    targets: dict,
    label: str,
) -> None:
    available = Counter(values)
    for value, target in targets.items():
        if available[value] < target:
            raise ValueError(
                f"{label} group {value} has {available[value]} candidates, "
                f"fewer than required {target}"
            )


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def distribution_rows(rows: list[dict]) -> list[dict]:
    selected = [row for row in rows if row["final_selected"]]
    output: list[dict] = []
    groups = (
        ("uncertainty_layer", "uncertainty_layer"),
        ("natoms", "natoms"),
        ("pressure_index", "pressure_index"),
        (
            "natoms_pressure",
            lambda row: f"{row['natoms']}:{row['pressure_index']}",
        ),
    )
    for group, key in groups:
        if callable(key):
            counts = Counter(key(row) for row in selected)
        else:
            counts = Counter(str(row[key]) for row in selected)
        for value, count in sorted(counts.items()):
            output.append({"group": group, "value": value, "count": count})
    return output


def scoring_summary_rows(rows: list[dict]) -> list[dict]:
    output: list[dict] = []
    groups = (
        ("all", lambda row: "all"),
        ("natoms", lambda row: str(row["natoms"])),
        ("pressure_index", lambda row: str(row["pressure_index"])),
        (
            "natoms_pressure",
            lambda row: f"{row['natoms']}:{row['pressure_index']}",
        ),
    )
    for group, key_fn in groups:
        grouped: dict[str, list[dict]] = {}
        for row in rows:
            grouped.setdefault(key_fn(row), []).append(row)
        for value, group_rows in sorted(grouped.items()):
            uncertainty = [float(row["uncertainty_eVA"]) for row in group_rows]
            max_force = [float(row["max_force_eVA"]) for row in group_rows]
            output.append(
                {
                    "group": group,
                    "value": value,
                    "count": len(group_rows),
                    "u_min": min(uncertainty),
                    "u_median": float(np.median(uncertainty)),
                    "u_max": max(uncertainty),
                    "max_force_max": max(max_force),
                }
            )
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score RSS structures and select them with base-aware uncertainty-quota CUR."
    )
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--jnn-root", type=Path, required=True)
    parser.add_argument("--base-db", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument(
        "--score-csv",
        type=Path,
        help=(
            "Reuse a saved uncertainty_all_frames.csv after validating its "
            "file order, manifest provenance, and geometry diagnostics."
        ),
    )
    parser.add_argument("--expected-count", type=int, default=1500)
    parser.add_argument("--layer-count", type=int, default=5)
    parser.add_argument(
        "--layer-mode",
        choices=("global", "natoms-pressure"),
        default="global",
        help="Assign uncertainty layers globally or separately per natoms x Mini-pressure group.",
    )
    parser.add_argument(
        "--quotas",
        type=parse_quotas,
        default=DEFAULT_QUOTAS,
        help="Final exact layer quotas, for example Q1=38,Q2=38,Q3=37,Q4=37,Q5=0.",
    )
    parser.add_argument("--r-c", type=float, default=6.0)
    parser.add_argument("--n-max", type=int, default=5)
    parser.add_argument("--l-max", type=int, default=6)
    parser.add_argument(
        "--base-variance",
        type=float,
        default=0.9999,
        help="Fraction of base-DB descriptor variance removed by truncated-SVD projection.",
    )
    parser.add_argument("--similarity-threshold", type=float, default=0.9995)
    parser.add_argument("--no-similarity-threshold", action="store_true")
    parser.add_argument(
        "--cur-method",
        choices=("iterative", "leverage-milp"),
        default="iterative",
        help="Greedy multi-pass CUR or leverage-score CUR with exact MILP quotas.",
    )
    parser.add_argument(
        "--balance-natoms",
        action="store_true",
        help="Enforce equal final counts across atom-count groups.",
    )
    parser.add_argument(
        "--balance-pressure",
        action="store_true",
        help="Enforce equal final counts across Mini-pressure source indices.",
    )
    parser.add_argument(
        "--balance-natoms-pressure",
        action="store_true",
        help="Enforce equal final counts across natoms x Mini-pressure groups.",
    )
    parser.add_argument(
        "--natoms-pressure-quotas",
        type=parse_natoms_pressure_quotas,
        help=(
            "Exact nonuniform natoms:Mini-pressure targets, for example "
            "3:0=2,3:1=3. Must cover every retained joint group and sum to "
            "the final layer quota total."
        ),
    )
    parser.add_argument(
        "--u-min",
        type=float,
        help="Inclusive minimum uncertainty retained before layer assignment and CUR.",
    )
    parser.add_argument(
        "--u-max",
        type=float,
        help="Inclusive maximum uncertainty retained before layer assignment and CUR.",
    )
    parser.add_argument("--progress-interval", type=int, default=100)
    parser.add_argument(
        "--score-only",
        action="store_true",
        help=(
            "Write full-committee uncertainty/force/geometry diagnostics and "
            "stop before uncertainty layers, descriptors, and CUR selection."
        ),
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.expected_count <= 0:
        raise ValueError("--expected-count must be positive")
    if args.layer_count != len(args.quotas):
        raise ValueError("--layer-count must match the number of quota labels")
    for option, value in (("--u-min", args.u_min), ("--u-max", args.u_max)):
        if value is not None and not np.isfinite(value):
            raise ValueError(f"{option} must be finite")
    if args.u_min is not None and args.u_max is not None and args.u_min > args.u_max:
        raise ValueError("--u-min must be less than or equal to --u-max")
    if args.natoms_pressure_quotas and (
        args.balance_natoms
        or args.balance_pressure
        or args.balance_natoms_pressure
    ):
        raise ValueError(
            "--natoms-pressure-quotas cannot be combined with --balance-natoms, "
            "--balance-pressure, or --balance-natoms-pressure"
        )
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        if not args.overwrite:
            raise FileExistsError(f"Output directory exists and is non-empty: {args.output_dir}")
        shutil.rmtree(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(args.input_dir.glob("*.poscar"))
    if len(files) != args.expected_count:
        raise ValueError(f"Expected {args.expected_count} POSCARs, found {len(files)}")
    manifest = read_manifest(args.manifest)
    jnn_paths = sorted_jnn_paths(args.jnn_root)
    structures = [read(path) for path in files]
    if args.score_csv is not None:
        rows = load_score_rows(args.score_csv, files, structures, manifest)
        print(
            f"loaded_saved_scores={len(rows)} committee_models={len(jnn_paths)}",
            flush=True,
        )
    else:
        calculators = build_calculators(jnn_paths)
        rows: list[dict] = []
        for index, (path, atoms) in enumerate(zip(files, structures), start=1):
            diagnostics = geometry_diagnostics(atoms)
            uncertainty, max_force = uncertainty_and_max_force(atoms, calculators)
            source_path = manifest.get(path.name, str(path))
            rows.append(
                {
                    "orig_index": index,
                    "source_file": path.name,
                    "source_path": source_path,
                    **diagnostics,
                    "pressure_index": pressure_index(source_path),
                    "uncertainty_eVA": float(uncertainty),
                    "max_force_eVA": float(max_force),
                    "uncertainty_layer": "",
                    "retained_by_u_filter": True,
                    "cur_rank": "",
                    "cur_pass": "",
                    "cur_score": "",
                    "singular_value": "",
                    "residual_norm": "",
                    "max_similarity_selected": "",
                    "max_similarity_base": "",
                    "final_selected": False,
                    "selected_file": "",
                }
            )
            if args.progress_interval and index % args.progress_interval == 0:
                print(f"scored={index}/{len(files)}", flush=True)

    fieldnames = list(rows[0].keys())
    if args.score_only:
        write_csv(args.output_dir / "uncertainty_all_frames.csv", rows, fieldnames)
        write_csv(
            args.output_dir / "uncertainty_score_summary.csv",
            scoring_summary_rows(rows),
            [
                "group",
                "value",
                "count",
                "u_min",
                "u_median",
                "u_max",
                "max_force_max",
            ],
        )
        print(f"scored={len(rows)} selection_skipped=true", flush=True)
        print(f"output={args.output_dir}", flush=True)
        return

    retained_global_indices = filter_rows_by_uncertainty(rows, args.u_min, args.u_max)
    if not retained_global_indices:
        raise ValueError("Uncertainty filtering retained no candidates")
    retained_rows = [rows[idx] for idx in retained_global_indices]
    layers = assign_layers(retained_rows, args.layer_count, args.layer_mode)
    for label, quota in args.quotas.items():
        if label not in layers:
            raise ValueError(f"Quota label is not an uncertainty layer: {label}")
        if quota > len(layers[label]):
            raise ValueError(f"Quota {label}={quota} exceeds layer size {len(layers[label])}")

    candidate_global_indices = [
        retained_global_indices[idx]
        for label in sorted(layers, key=lambda value: int(value[1:]))
        if args.quotas.get(label, 0) > 0
        for idx in layers[label]
    ]
    candidate_structures = [structures[idx] for idx in candidate_global_indices]
    candidate_layers = [rows[idx]["uncertainty_layer"] for idx in candidate_global_indices]
    candidate_natoms = [int(rows[idx]["natoms"]) for idx in candidate_global_indices]
    candidate_pressures = [str(rows[idx]["pressure_index"]) for idx in candidate_global_indices]
    target = sum(args.quotas.values())
    natoms_targets = (
        equal_targets(candidate_natoms, target, "natoms")
        if args.balance_natoms
        else {}
    )
    pressure_targets = (
        equal_targets(candidate_pressures, target, "pressure")
        if args.balance_pressure
        else {}
    )
    natoms_pressure_values = list(zip(candidate_natoms, candidate_pressures))
    natoms_pressure_targets = (
        explicit_targets(
            natoms_pressure_values,
            args.natoms_pressure_quotas,
            target,
            "natoms-pressure",
        )
        if args.natoms_pressure_quotas
        else (
            equal_targets(natoms_pressure_values, target, "natoms-pressure")
            if args.balance_natoms_pressure
            else {}
        )
    )
    validate_target_capacity(
        candidate_layers,
        {label: quota for label, quota in args.quotas.items() if quota > 0},
        "uncertainty layer",
    )
    validate_target_capacity(candidate_natoms, natoms_targets, "natoms")
    validate_target_capacity(candidate_pressures, pressure_targets, "Mini-pressure")
    validate_target_capacity(
        natoms_pressure_values,
        natoms_pressure_targets,
        "natoms-pressure",
    )

    print(
        f"retained_after_u_filter={len(retained_rows)} "
        f"cur_candidates={len(candidate_structures)}",
        flush=True,
    )
    print(f"Building descriptors for {len(candidate_structures)} retained candidates...", flush=True)
    x_candidates = build_feature_matrix(
        candidate_structures, args.r_c, args.n_max, args.l_max, "RSS Candidates"
    )
    print(f"Building descriptors for base DB {args.base_db}...", flush=True)
    base_structures, _ = read_structures(args.base_db)
    x_base = build_feature_matrix(base_structures, args.r_c, args.n_max, args.l_max, "Base DB")
    x_residual, max_base_similarity, base_rank, captured = orthogonal_base_projection(
        x_candidates, x_base, args.base_variance
    )
    print(
        f"Projected base modes={base_rank}, captured_variance={captured:.8f}; "
        "starting quota-CUR...",
        flush=True,
    )
    x_similarity = normalize_columns(x_residual.copy())
    threshold = None if args.no_similarity_threshold else args.similarity_threshold
    selector = (
        quota_cur_select_milp
        if args.cur_method == "leverage-milp"
        else quota_cur_select
    )
    selected_local, records, rejected = selector(
        x_residual=x_residual,
        x_similarity=x_similarity,
        candidate_layers=candidate_layers,
        candidate_natoms=candidate_natoms,
        candidate_pressures=candidate_pressures,
        quotas=args.quotas,
        natoms_targets=natoms_targets,
        pressure_targets=pressure_targets,
        max_base_similarity=max_base_similarity,
        similarity_threshold=threshold,
        natoms_pressure_targets=natoms_pressure_targets,
    )

    for rank, (local_idx, record) in enumerate(zip(selected_local, records), start=1):
        global_idx = candidate_global_indices[local_idx]
        row = rows[global_idx]
        row.update(record)
        row["final_selected"] = True
        selected_name = (
            f"selected_{rank:06d}_{row['uncertainty_layer']}_from_{row['source_file']}"
        )
        row["selected_file"] = selected_name
        write(args.output_dir / selected_name, structures[global_idx], format="vasp")

    write_csv(args.output_dir / "selection_summary.csv", rows, fieldnames)
    write_csv(
        args.output_dir / "selected_summary.csv",
        [row for row in rows if row["final_selected"]],
        fieldnames,
    )
    bin_rows = []
    for label in sorted(layers, key=lambda value: int(value[1:])):
        layer_rows = [retained_rows[idx] for idx in layers[label]]
        values = [float(row["uncertainty_eVA"]) for row in layer_rows]
        bin_rows.append(
            {
                "uncertainty_layer": label,
                "total": len(values),
                "selected": sum(1 for row in layer_rows if row["final_selected"]),
                "u_min": min(values),
                "u_max": max(values),
            }
        )
    write_csv(
        args.output_dir / "uncertainty_bin_summary.csv",
        bin_rows,
        ["uncertainty_layer", "total", "selected", "u_min", "u_max"],
    )
    write_csv(
        args.output_dir / "selected_distribution.csv",
        distribution_rows(rows),
        ["group", "value", "count"],
    )

    print(f"selected={len(selected_local)} rejected_by_similarity={len(rejected)}", flush=True)
    print(f"output={args.output_dir}", flush=True)
    for row in bin_rows:
        print(
            f"{row['uncertainty_layer']}: total={row['total']} selected={row['selected']} "
            f"U=[{row['u_min']:.8g},{row['u_max']:.8g}]",
            flush=True,
        )


if __name__ == "__main__":
    main()
