#!/usr/bin/env python3
"""Quota-constrained CUR selection for stratified active-learning candidates."""

from __future__ import annotations

import argparse
import csv
import math
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.linalg import svd

SCRIPT_DIR = Path(globals().get("__file__", sys.argv[0])).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from CUR import (  # noqa: E402
    build_feature_matrix,
    normalize_columns,
    read_structures,
    write_selected_structures,
)


DEFAULT_BINS = ("0-40", "40-70", "70-90", "90-98", "98-100")


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_source_value(label: str) -> float:
    text = label
    if text.startswith("P-") and text.endswith("GPa"):
        text = text[2:-3]
    elif text.startswith("scale-"):
        text = text[len("scale-"):]
    try:
        return float(text.replace("m", "-").replace("p", "."))
    except ValueError:
        return float("inf")


def source_type_rank(label: str) -> int:
    if label.startswith("scale-"):
        return 0
    if label.startswith("P-") and label.endswith("GPa"):
        return 1
    return 2


def source_sort_key(label: str) -> tuple[int, float, str]:
    return (source_type_rank(label), parse_source_value(label), label)


def sorted_sources(metadata: list[dict]) -> list[str]:
    labels = sorted({row["trajectory"] for row in metadata}, key=source_sort_key)
    if not labels:
        raise ValueError("No trajectory/source labels found in metadata")
    return labels


def pressure_label_or_blank(source_label: str) -> str:
    return source_label if source_label.startswith("P-") and source_label.endswith("GPa") else ""


def metadata_by_candidate(metadata: list[dict]) -> dict[str, dict]:
    result = {}
    for row in metadata:
        candidate_file = row.get("candidate_file", "")
        if not candidate_file:
            raise ValueError("Metadata row is missing candidate_file")
        if candidate_file in result:
            raise ValueError(f"Duplicate candidate_file in metadata: {candidate_file}")
        result[candidate_file] = row
    return result


def project_base_space(
    x_current: np.ndarray,
    x_raw: np.ndarray,
    base_path: str | None,
    r_c: float,
    n_max: int,
    l_max: int,
) -> tuple[np.ndarray, np.ndarray]:
    max_base_similarity = np.full(x_current.shape[1], np.nan)
    if base_path is None:
        return x_current, max_base_similarity

    print(f"Reading base structures from {base_path}...", flush=True)
    base_structures, _ = read_structures(base_path)
    if not base_structures:
        return x_current, max_base_similarity

    print("Projecting current DB feature space out of candidate space...", flush=True)
    x_base = build_feature_matrix(
        base_structures, r_c, n_max, l_max, "Feature Extraction (Base)"
    )
    max_base_similarity = np.max(x_base.T @ x_raw, axis=0)

    for i in range(x_base.shape[1]):
        x_base_col = x_base[:, i]
        norm_sq = float(np.dot(x_base_col, x_base_col))
        if norm_sq > 1e-12:
            projections = np.dot(x_base_col, x_current) / norm_sq
            x_current = x_current - np.outer(x_base_col, projections)

    return x_current, max_base_similarity


def quota_targets(sources: list[str], bins: tuple[str, ...], target: int) -> dict:
    if target % len(bins) != 0:
        raise ValueError("target must be divisible by the number of uncertainty bins")
    source_min = target // len(sources)
    source_max = int(math.ceil(target / len(sources)))
    return {
        "pressure_min": source_min,
        "pressure_max": source_max,
        "bin_target": {label: target // len(bins) for label in bins},
    }


class QuotaCurSelector:
    def __init__(
        self,
        x_current: np.ndarray,
        x_similarity: np.ndarray,
        labels: list[str],
        metadata: list[dict],
        max_base_similarity: np.ndarray,
        target: int,
        pressures: list[str],
        bins: tuple[str, ...],
        cell_min: int,
        cell_max: int,
        pressure_min: int,
        pressure_max: int,
        bin_target: dict[str, int],
        similarity_threshold: float | None,
        min_frame_gap: int,
    ) -> None:
        self.x_current = x_current
        self.x_similarity = x_similarity
        self.labels = labels
        self.metadata = metadata
        self.max_base_similarity = max_base_similarity
        self.target = target
        self.pressures = pressures
        self.bins = bins
        self.cell_min = cell_min
        self.cell_max = cell_max
        self.pressure_min = pressure_min
        self.pressure_max = pressure_max
        self.bin_target = bin_target
        self.similarity_threshold = similarity_threshold
        self.min_frame_gap = min_frame_gap

        self.selected_indices: list[int] = []
        self.rejected_indices: set[int] = set()
        self.records: list[dict] = []
        self.pressure_counts: Counter = Counter()
        self.bin_counts: Counter = Counter()
        self.cell_counts: Counter = Counter()
        self.selected_frames: defaultdict[str, list[int]] = defaultdict(list)

    def candidate_pressure(self, idx: int) -> str:
        return self.metadata[idx]["trajectory"]

    def candidate_bin(self, idx: int) -> str:
        return self.metadata[idx]["uncertainty_bin"]

    def candidate_frame(self, idx: int) -> int:
        return int(self.metadata[idx]["frame"])

    def can_use_common(self, idx: int) -> bool:
        if idx in self.selected_indices or idx in self.rejected_indices:
            return False
        pressure = self.candidate_pressure(idx)
        bin_label = self.candidate_bin(idx)
        if self.pressure_counts[pressure] >= self.pressure_max:
            return False
        if self.bin_counts[bin_label] >= self.bin_target[bin_label]:
            return False
        if self.cell_counts[(pressure, bin_label)] >= self.cell_max:
            return False
        if self.min_frame_gap > 0:
            frame = self.candidate_frame(idx)
            if any(abs(frame - old_frame) < self.min_frame_gap for old_frame in self.selected_frames[pressure]):
                return False
        return True

    def pressure_deficit(self) -> int:
        return sum(max(0, self.pressure_min - self.pressure_counts[p]) for p in self.pressures)

    def allowed_phase_min_cell(self, idx: int) -> bool:
        if not self.can_use_common(idx):
            return False
        pressure = self.candidate_pressure(idx)
        bin_label = self.candidate_bin(idx)
        return self.cell_counts[(pressure, bin_label)] < self.cell_min

    def allowed_phase_fill(self, idx: int) -> bool:
        if not self.can_use_common(idx):
            return False
        remaining_slots = self.target - len(self.selected_indices)
        deficit = self.pressure_deficit()
        if deficit >= remaining_slots:
            pressure = self.candidate_pressure(idx)
            return self.pressure_counts[pressure] < self.pressure_min
        return True

    def accept(self, idx: int, phase: str, cur_score: float, singular_value: float,
               max_selected_similarity: float) -> None:
        pressure = self.candidate_pressure(idx)
        bin_label = self.candidate_bin(idx)
        self.selected_indices.append(idx)
        self.pressure_counts[pressure] += 1
        self.bin_counts[bin_label] += 1
        self.cell_counts[(pressure, bin_label)] += 1
        self.selected_frames[pressure].append(self.candidate_frame(idx))

        x_l = self.x_current[:, idx]
        norm_x_l_sq = float(np.dot(x_l, x_l))
        self.records.append(
            {
                "cur_rank": len(self.selected_indices),
                "cur_phase": phase,
                "cur_score": cur_score,
                "singular_value": float(singular_value),
                "residual_norm": float(np.sqrt(max(norm_x_l_sq, 0.0))),
                "max_similarity_selected": max_selected_similarity,
                "max_similarity_base": float(self.max_base_similarity[idx]),
            }
        )

        if norm_x_l_sq > 1e-12:
            projections = np.dot(x_l, self.x_current) / norm_x_l_sq
            self.x_current = self.x_current - np.outer(x_l, projections)

    def select_one(self, phase: str, allowed_fn) -> bool:
        u_matrix, singular_values, vh_matrix = svd(self.x_current, full_matrices=False)
        del u_matrix
        if len(singular_values) == 0 or singular_values[0] <= 1e-12:
            return False
        scores = (vh_matrix[0, :]) ** 2
        allowed = np.array([allowed_fn(idx) for idx in range(len(scores))], dtype=bool)
        scores[~allowed] = -1.0

        while float(np.max(scores)) >= 0.0:
            idx = int(np.argmax(scores))
            cur_score = float(scores[idx])
            max_selected_similarity = 0.0
            if self.similarity_threshold is not None and self.selected_indices:
                similarities = self.x_similarity[:, self.selected_indices].T @ self.x_similarity[:, idx]
                max_selected_similarity = float(np.max(similarities))
                if max_selected_similarity >= self.similarity_threshold:
                    self.rejected_indices.add(idx)
                    scores[idx] = -1.0
                    self.x_current[:, idx] = 0.0
                    continue

            self.accept(idx, phase, cur_score, float(singular_values[0]), max_selected_similarity)
            return True
        return False

    def run(self) -> tuple[list[int], list[dict]]:
        required_min = len(self.pressures) * len(self.bins) * self.cell_min
        if required_min > self.target:
            raise ValueError("cell_min quotas exceed target selection size")

        print("Phase 1: enforcing minimum source/bin cell quotas...", flush=True)
        while any(
            self.cell_counts[(pressure, bin_label)] < self.cell_min
            for pressure in self.pressures
            for bin_label in self.bins
        ):
            if not self.select_one("cell-min", self.allowed_phase_min_cell):
                raise RuntimeError("Could not satisfy source/bin minimum quotas")

        print("Phase 2: filling remaining slots with balanced global CUR...", flush=True)
        while len(self.selected_indices) < self.target:
            if not self.select_one("balanced-fill", self.allowed_phase_fill):
                raise RuntimeError("Could not fill target under quota constraints")

        return self.selected_indices, self.records


def validate_quota_inputs(metadata: list[dict], pressures: list[str], bins: tuple[str, ...],
                          target: int, cell_min: int, cell_max: int) -> None:
    counts = Counter((row["trajectory"], row["uncertainty_bin"]) for row in metadata)
    missing = [
        (pressure, bin_label)
        for pressure in pressures
        for bin_label in bins
        if counts[(pressure, bin_label)] < cell_min
    ]
    if missing:
        raise ValueError(f"Some source/bin cells cannot satisfy cell_min={cell_min}: {missing}")
    if cell_max < cell_min:
        raise ValueError("cell_max must be >= cell_min")
    if len(pressures) * len(bins) * cell_min > target:
        raise ValueError("cell_min quotas exceed target")
    if target > len(metadata):
        raise ValueError("target exceeds candidate count")


def update_metadata_rows(
    original_rows: list[dict],
    labels: list[str],
    selected_indices: list[int],
    selection_records: list[dict],
    max_base_similarity: np.ndarray,
) -> list[dict]:
    selected_by_label = {
        labels[idx]: (rank, record)
        for rank, (idx, record) in enumerate(zip(selected_indices, selection_records), start=1)
    }
    selected_set = set(selected_indices)
    rows = []
    selection_keys = (
        "cur_rank",
        "cur_phase",
        "cur_score",
        "selected_file",
        "singular_value",
        "residual_norm",
        "max_similarity_selected",
    )
    for row in original_rows:
        new_row = dict(row)
        candidate_file = new_row["candidate_file"]
        idx = labels.index(candidate_file)
        for key in selection_keys:
            new_row[key] = ""
        new_row["max_similarity_base"] = f"{float(max_base_similarity[idx]):.10g}"
        if idx in selected_set:
            rank, record = selected_by_label[candidate_file]
            new_row["final_selected"] = "True"
            new_row["selected_file"] = f"{rank:06d}.poscar"
            for key, value in record.items():
                if isinstance(value, float):
                    new_row[key] = f"{value:.10g}"
                else:
                    new_row[key] = str(value)
        else:
            new_row["final_selected"] = "False"
        rows.append(new_row)
    return rows


def distribution_rows(rows: list[dict]) -> list[dict]:
    selected = [row for row in rows if row.get("final_selected") == "True"]
    source_counts = Counter(row["trajectory"] for row in selected)
    bin_counts = Counter(row["uncertainty_bin"] for row in selected)
    cell_counts = Counter((row["trajectory"], row["uncertainty_bin"]) for row in selected)
    output = []
    for source, count in sorted(source_counts.items(), key=lambda item: source_sort_key(item[0])):
        output.append({
            "group": "source",
            "source": source,
            "pressure": pressure_label_or_blank(source),
            "uncertainty_bin": "",
            "count": count,
        })
    for bin_label in DEFAULT_BINS:
        output.append({
            "group": "uncertainty_bin",
            "source": "",
            "pressure": "",
            "uncertainty_bin": bin_label,
            "count": bin_counts[bin_label],
        })
    for (source, bin_label), count in sorted(cell_counts.items(), key=lambda item: (source_sort_key(item[0][0]), DEFAULT_BINS.index(item[0][1]))):
        output.append({
            "group": "source_bin",
            "source": source,
            "pressure": pressure_label_or_blank(source),
            "uncertainty_bin": bin_label,
            "count": count,
        })
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Quota-constrained CUR selection with base-DB projection."
    )
    parser.add_argument("--candidates", default="Al-potential/04-npt-round-2/uncertainty-stratified-candidates-poscar")
    parser.add_argument("--metadata", default="Al-potential/04-npt-round-2/selection_summary.csv")
    parser.add_argument("--base", default="Al-potential/current.db")
    parser.add_argument("--output", default="Al-potential/04-npt-round-2/cur-selected-poscar_stratified700_cur100")
    parser.add_argument("--updated-metadata", default="Al-potential/04-npt-round-2/selection_summary.csv")
    parser.add_argument("--distribution-csv", default="Al-potential/04-npt-round-2/cur_selected_distribution.csv")
    parser.add_argument("--target", type=int, default=100)
    parser.add_argument("--cell-min", type=int, default=2)
    parser.add_argument("--cell-max", type=int, default=4)
    parser.add_argument("--r-c", type=float, default=6.0)
    parser.add_argument("--n-max", type=int, default=5)
    parser.add_argument("--l-max", type=int, default=6)
    parser.add_argument("--similarity-threshold", type=float, default=0.99999)
    parser.add_argument("--no-similarity-threshold", action="store_true")
    parser.add_argument("--min-frame-gap", type=int, default=50,
                        help="Minimum frame separation between final selections from the same trajectory")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidate_path = Path(args.candidates)
    metadata_path = Path(args.metadata)
    output_path = Path(args.output)
    updated_metadata_path = Path(args.updated_metadata)
    distribution_path = Path(args.distribution_csv)

    if output_path.exists():
        if not args.overwrite:
            raise FileExistsError(f"Output exists; use --overwrite: {output_path}")
        if output_path.is_dir():
            shutil.rmtree(output_path)
        else:
            output_path.unlink()
    if distribution_path.exists() and not args.overwrite:
        raise FileExistsError(f"Distribution CSV exists; use --overwrite: {distribution_path}")

    original_rows = read_csv(metadata_path)
    metadata_map = metadata_by_candidate(original_rows)
    pressures = sorted_sources(original_rows)
    bins = DEFAULT_BINS
    targets = quota_targets(pressures, bins, args.target)
    validate_quota_inputs(original_rows, pressures, bins, args.target, args.cell_min, args.cell_max)

    print(f"Reading candidate structures from {candidate_path}...", flush=True)
    structures, labels = read_structures(candidate_path)
    if len(structures) != len(original_rows):
        raise ValueError(f"Structure/metadata count mismatch: {len(structures)} vs {len(original_rows)}")
    metadata = []
    for label in labels:
        if label not in metadata_map:
            raise ValueError(f"Missing metadata for candidate file: {label}")
        metadata.append(metadata_map[label])

    print("Constructing feature matrix X for candidates...", flush=True)
    x_current = build_feature_matrix(
        structures, args.r_c, args.n_max, args.l_max, "Feature Extraction (Candidates)"
    )
    x_raw = x_current.copy()
    x_current, max_base_similarity = project_base_space(
        x_current, x_raw, args.base, args.r_c, args.n_max, args.l_max
    )
    x_similarity = normalize_columns(x_current.copy())
    similarity_threshold = None if args.no_similarity_threshold else args.similarity_threshold

    selector = QuotaCurSelector(
        x_current=x_current,
        x_similarity=x_similarity,
        labels=labels,
        metadata=metadata,
        max_base_similarity=max_base_similarity,
        target=args.target,
        pressures=pressures,
        bins=bins,
        cell_min=args.cell_min,
        cell_max=args.cell_max,
        pressure_min=targets["pressure_min"],
        pressure_max=targets["pressure_max"],
        bin_target=targets["bin_target"],
        similarity_threshold=similarity_threshold,
        min_frame_gap=args.min_frame_gap,
    )
    selected_indices, selection_records = selector.run()

    print(f"Saving selected configurations to {output_path}...", flush=True)
    write_selected_structures(
        output_path,
        structures,
        selected_indices,
        labels,
        selection_records=selection_records,
    )

    updated_rows = update_metadata_rows(
        original_rows,
        labels,
        selected_indices,
        selection_records,
        max_base_similarity,
    )
    fieldnames = list(original_rows[0].keys())
    for key in (
        "cur_rank",
        "cur_phase",
        "selected_file",
        "singular_value",
        "residual_norm",
        "max_similarity_selected",
        "max_similarity_base",
    ):
        if key not in fieldnames:
            fieldnames.append(key)
    write_csv(updated_metadata_path, updated_rows, fieldnames)
    dist_rows = distribution_rows(updated_rows)
    write_csv(distribution_path, dist_rows, ["group", "source", "pressure", "uncertainty_bin", "count"])

    print(f"Done: selected {len(selected_indices)} structures.", flush=True)
    print(f"Source counts: {dict(selector.pressure_counts)}", flush=True)
    print(f"Bin counts: {dict(selector.bin_counts)}", flush=True)
    print(f"Rejected by similarity: {len(selector.rejected_indices)}", flush=True)


if __name__ == "__main__":
    main()
