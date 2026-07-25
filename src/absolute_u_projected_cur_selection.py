#!/usr/bin/env python3
"""Select absolute-uncertainty MD candidates with current-DB-projected CUR."""

from __future__ import annotations

import argparse
import csv
import math
import os
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from ase.geometry import wrap_positions
from ase.io import iread, write
from scipy.linalg import svd

SCRIPT_DIR = Path(globals().get("__file__", sys.argv[0])).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from CUR import build_feature_matrix, normalize_columns, read_structures, write_selected_structures
from quota_cur_selection import project_base_space, source_sort_key


CANDIDATE_FIELDS = (
    "source_type",
    "source_value",
    "scale_factor",
    "trajectory",
    "trajectory_path",
    "frame",
    "uncertainty",
    "volume_per_atom",
    "max_force",
    "max_force_model0",
    "instant_pressure_gpa",
    "natoms",
    "min_distance_A",
    "physical_gate_status",
    "candidate_rank_source",
    "candidate_file",
    "final_selected",
    "cur_rank",
    "cur_phase",
    "cur_score",
    "selected_file",
    "singular_value",
    "residual_norm",
    "max_similarity_selected",
    "max_similarity_base",
)

PHYSICAL_GATE_REJECTION_FIELDS = (
    "source_type",
    "source_value",
    "scale_factor",
    "trajectory",
    "trajectory_path",
    "frame",
    "uncertainty",
    "volume_per_atom",
    "max_force",
    "max_force_model0",
    "candidate_rank_source",
    "min_distance_A",
    "physical_gate_reasons",
)


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: tuple[str, ...] | list[str]) -> None:
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def finite_float(row: dict, key: str) -> float:
    try:
        value = float(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {key!r} in frame metadata: {row.get(key)!r}") from exc
    if not math.isfinite(value):
        raise ValueError(f"Non-finite {key!r} in frame metadata: {value}")
    return value


def select_spaced_candidates(
    all_frame_rows: list[dict],
    u_min: float,
    min_frame_gap: int,
    min_volume_per_atom: float | None,
    max_volume_per_atom: float | None,
    max_force: float | None,
) -> tuple[dict[str, list[dict]], list[dict]]:
    by_source: defaultdict[str, list[dict]] = defaultdict(list)
    gate_rejections: list[dict] = []
    for row in all_frame_rows:
        if row.get("discarded_equilibration", "").strip().lower() != "false":
            continue
        uncertainty = finite_float(row, "uncertainty")
        if uncertainty < u_min:
            continue
        reasons = []
        volume_per_atom = finite_float(row, "volume_per_atom")
        force = finite_float(row, "max_force")
        if min_volume_per_atom is not None and volume_per_atom < min_volume_per_atom:
            reasons.append(f"volume_per_atom<{min_volume_per_atom:g}")
        if max_volume_per_atom is not None and volume_per_atom > max_volume_per_atom:
            reasons.append(f"volume_per_atom>{max_volume_per_atom:g}")
        if max_force is not None and force > max_force:
            reasons.append(f"max_force>{max_force:g}")
        if reasons:
            rejected = dict(row)
            rejected["candidate_rank_source"] = ""
            rejected["min_distance_A"] = ""
            rejected["physical_gate_reasons"] = ";".join(reasons)
            gate_rejections.append(rejected)
            continue
        source = row.get("trajectory", "")
        if not source:
            raise ValueError("All-frame metadata is missing trajectory")
        by_source[source].append(dict(row))

    selected: dict[str, list[dict]] = {}
    for source in sorted(by_source, key=source_sort_key):
        records = sorted(by_source[source], key=lambda row: int(row["frame"]))
        keep: list[dict] = []
        for row in records:
            frame = int(row["frame"])
            if not keep or frame - int(keep[-1]["frame"]) >= min_frame_gap:
                keep.append(row)
        if not keep:
            raise RuntimeError(f"No gap-valid candidates for source {source}")
        for rank, row in enumerate(keep, start=1):
            row["candidate_rank_source"] = rank
        selected[source] = keep
    return selected, gate_rejections


def minimum_distance(atoms) -> float:
    distances = atoms.get_all_distances(mic=True)
    for index in range(len(atoms)):
        distances[index, index] = np.inf
    return float(np.min(distances))


def write_candidate_poscars(
    selected_by_source: dict[str, list[dict]],
    candidate_dir: Path,
    min_distance_limit: float | None,
) -> tuple[list[dict], list[dict]]:
    candidate_dir.mkdir()
    rows: list[dict] = []
    gate_rejections: list[dict] = []

    for source in sorted(selected_by_source, key=source_sort_key):
        records = selected_by_source[source]
        trajectory_paths = {row.get("trajectory_path", "") for row in records}
        if len(trajectory_paths) != 1:
            raise ValueError(f"Source {source} maps to multiple trajectory paths")
        trajectory_path = Path(next(iter(trajectory_paths)))
        if not trajectory_path.is_file():
            raise FileNotFoundError(f"Missing trajectory for {source}: {trajectory_path}")

        by_frame = {int(row["frame"]): row for row in records}
        written_frames: set[int] = set()
        for frame, atoms in enumerate(iread(str(trajectory_path), index=":")):
            row = by_frame.get(frame)
            if row is None:
                continue

            if len(atoms) == 0 or not np.isfinite(atoms.cell.array).all():
                raise ValueError(f"Invalid cell/atom count for {source} frame {frame}")
            volume_per_atom = float(atoms.get_volume() / len(atoms))
            if not math.isfinite(volume_per_atom) or volume_per_atom <= 0.0:
                raise ValueError(f"Invalid volume per atom for {source} frame {frame}")
            if not np.isfinite(atoms.get_positions()).all():
                raise ValueError(f"Non-finite positions for {source} frame {frame}")

            positions = wrap_positions(atoms.get_positions(), atoms.get_cell(), atoms.get_pbc())
            atoms.set_positions(positions)
            minimum_distance_value = minimum_distance(atoms)
            if not math.isfinite(minimum_distance_value) or minimum_distance_value <= 0.0:
                raise ValueError(f"Invalid minimum distance for {source} frame {frame}")
            if (
                min_distance_limit is not None
                and minimum_distance_value < min_distance_limit
            ):
                rejected = dict(row)
                rejected["min_distance_A"] = minimum_distance_value
                rejected["physical_gate_reasons"] = f"min_distance_A<{min_distance_limit:g}"
                gate_rejections.append(rejected)
                continue

            uncertainty = finite_float(row, "uncertainty")
            candidate_file = (
                f"{source}_frame{frame:08d}_U{uncertainty:.6f}.poscar"
            )
            write(candidate_dir / candidate_file, atoms, format="vasp", direct=True, vasp5=True)

            result = {
                "source_type": row.get("source_type", ""),
                "source_value": row.get("source_value", ""),
                "scale_factor": row.get("scale_factor", ""),
                "trajectory": source,
                "trajectory_path": str(trajectory_path),
                "frame": frame,
                "uncertainty": uncertainty,
                "volume_per_atom": volume_per_atom,
                "max_force": finite_float(row, "max_force"),
                "max_force_model0": finite_float(row, "max_force_model0"),
                "instant_pressure_gpa": row.get("instant_pressure_gpa", ""),
                "natoms": len(atoms),
                "min_distance_A": minimum_distance_value,
                "physical_gate_status": "passed",
                "candidate_rank_source": row["candidate_rank_source"],
                "candidate_file": candidate_file,
                "final_selected": "False",
                "cur_rank": "",
                "cur_phase": "",
                "cur_score": "",
                "selected_file": "",
                "singular_value": "",
                "residual_norm": "",
                "max_similarity_selected": "",
                "max_similarity_base": "",
            }
            rows.append(result)
            written_frames.add(frame)

        rejected_frames = {
            int(row["frame"])
            for row in gate_rejections
            if row.get("trajectory") == source
        }
        unresolved = sorted(set(by_frame) - written_frames - rejected_frames)
        if unresolved:
            raise RuntimeError(f"Failed to write requested {source} frames: {unresolved[:10]}")

    return (
        sorted(rows, key=lambda row: (source_sort_key(row["trajectory"]), int(row["frame"]))),
        gate_rejections,
    )


class SourceTailCurSelector:
    """Greedy projected CUR with optional source balancing and tail cap."""

    def __init__(
        self,
        x_current: np.ndarray,
        x_similarity: np.ndarray,
        metadata: list[dict],
        max_base_similarity: np.ndarray,
        source_min: int,
        source_max: int,
        target: int,
        tail_threshold: float | None,
        tail_max: int | None,
        similarity_threshold: float | None,
        min_frame_gap: int,
    ) -> None:
        self.x_current = x_current
        self.x_similarity = x_similarity
        self.metadata = metadata
        self.max_base_similarity = max_base_similarity
        self.source_min = source_min
        self.source_max = source_max
        self.target = target
        self.tail_threshold = tail_threshold
        self.tail_max = tail_max
        self.similarity_threshold = similarity_threshold
        self.min_frame_gap = min_frame_gap
        self.sources = sorted({row["trajectory"] for row in metadata}, key=source_sort_key)

        self.selected_indices: list[int] = []
        self.rejected_indices: set[int] = set()
        self.records: list[dict] = []
        self.source_counts: Counter = Counter()
        self.selected_frames: defaultdict[str, list[int]] = defaultdict(list)
        self.tail_count = 0

    def is_tail(self, idx: int) -> bool:
        return (
            self.tail_threshold is not None
            and float(self.metadata[idx]["uncertainty"]) >= self.tail_threshold
        )

    def can_use(self, idx: int) -> bool:
        if idx in self.selected_indices or idx in self.rejected_indices:
            return False
        row = self.metadata[idx]
        source = row["trajectory"]
        if self.source_counts[source] >= self.source_max:
            return False
        if (
            self.is_tail(idx)
            and self.tail_max is not None
            and self.tail_count >= self.tail_max
        ):
            return False
        if self.min_frame_gap > 0:
            frame = int(row["frame"])
            if any(abs(frame - old_frame) < self.min_frame_gap for old_frame in self.selected_frames[source]):
                return False
        return True

    def accept(self, idx: int, phase: str, cur_score: float, singular_value: float,
               max_selected_similarity: float) -> None:
        row = self.metadata[idx]
        source = row["trajectory"]
        self.selected_indices.append(idx)
        self.source_counts[source] += 1
        self.selected_frames[source].append(int(row["frame"]))
        if self.is_tail(idx):
            self.tail_count += 1

        x_column = self.x_current[:, idx]
        norm_sq = float(np.dot(x_column, x_column))
        self.records.append(
            {
                "cur_rank": len(self.selected_indices),
                "cur_phase": phase,
                "cur_score": cur_score,
                "singular_value": singular_value,
                "residual_norm": float(np.sqrt(max(norm_sq, 0.0))),
                "max_similarity_selected": max_selected_similarity,
                "max_similarity_base": float(self.max_base_similarity[idx]),
            }
        )
        if norm_sq > 1e-12:
            projections = np.dot(x_column, self.x_current) / norm_sq
            self.x_current = self.x_current - np.outer(x_column, projections)

    def select_one(self, phase: str, source_only: str | None = None) -> bool:
        _, singular_values, vh_matrix = svd(self.x_current, full_matrices=False)
        if len(singular_values) == 0 or singular_values[0] <= 1e-12:
            return False
        scores = vh_matrix[0, :] ** 2
        allowed = np.array(
            [
                self.can_use(idx)
                and (source_only is None or self.metadata[idx]["trajectory"] == source_only)
                for idx in range(len(scores))
            ],
            dtype=bool,
        )
        scores[~allowed] = -1.0

        while float(np.max(scores)) >= 0.0:
            idx = int(np.argmax(scores))
            cur_score = float(scores[idx])
            max_selected_similarity = 0.0
            if self.similarity_threshold is not None and self.selected_indices:
                similarity = self.x_similarity[:, self.selected_indices].T @ self.x_similarity[:, idx]
                max_selected_similarity = float(np.max(similarity))
                if max_selected_similarity >= self.similarity_threshold:
                    self.rejected_indices.add(idx)
                    self.x_current[:, idx] = 0.0
                    scores[idx] = -1.0
                    continue

            self.accept(
                idx,
                phase,
                cur_score,
                float(singular_values[0]),
                max_selected_similarity,
            )
            return True
        return False

    def run(self) -> tuple[list[int], list[dict]]:
        if self.source_min > 0:
            print(
                f"Phase 1: enforcing source minimum quotas ({self.source_min}/source)...",
                flush=True,
            )
            for source in self.sources:
                while self.source_counts[source] < self.source_min:
                    if not self.select_one("source-min", source_only=source):
                        raise RuntimeError(
                            f"Could not satisfy source minimum quota for {source}"
                        )

        print("Filling projected CUR selection...", flush=True)
        while len(self.selected_indices) < self.target:
            if not self.select_one("cur-fill"):
                raise RuntimeError("Could not fill the projected CUR target")

        if any(self.source_counts[source] < self.source_min for source in self.sources):
            raise RuntimeError("Final selection violates a source minimum quota")
        return self.selected_indices, self.records


def update_metadata(
    rows: list[dict],
    labels: list[str],
    selected_indices: list[int],
    records: list[dict],
    max_base_similarity: np.ndarray,
) -> list[dict]:
    index_by_label = {label: index for index, label in enumerate(labels)}
    selected = {
        idx: record for idx, record in zip(selected_indices, records)
    }
    updated = []
    for row in rows:
        result = dict(row)
        idx = index_by_label[row["candidate_file"]]
        result["max_similarity_base"] = f"{float(max_base_similarity[idx]):.10g}"
        if idx in selected:
            record = selected[idx]
            result["final_selected"] = "True"
            result["selected_file"] = f"{record['cur_rank']:06d}.poscar"
            for key, value in record.items():
                result[key] = f"{value:.10g}" if isinstance(value, float) else str(value)
        updated.append(result)
    return updated


def distribution_rows(
    rows: list[dict],
    tail_threshold: float | None,
) -> list[dict]:
    selected = [row for row in rows if row["final_selected"] == "True"]
    source_counts = Counter(row["trajectory"] for row in selected)
    output = []
    for source, count in sorted(source_counts.items(), key=lambda item: source_sort_key(item[0])):
        output.append({"group": "source", "source": source, "uncertainty_layer": "", "count": count})
    if tail_threshold is None:
        return output

    layer_counts = Counter(
        "U-ge-tail" if float(row["uncertainty"]) >= tail_threshold else "U-below-tail"
        for row in selected
    )
    source_layer_counts = Counter(
        (
            row["trajectory"],
            "U-ge-tail" if float(row["uncertainty"]) >= tail_threshold else "U-below-tail",
        )
        for row in selected
    )
    for layer in ("U-below-tail", "U-ge-tail"):
        output.append({
            "group": "uncertainty_layer",
            "source": "",
            "uncertainty_layer": layer,
            "count": layer_counts[layer],
        })
    for (source, layer), count in sorted(
        source_layer_counts.items(),
        key=lambda item: (source_sort_key(item[0][0]), item[0][1]),
    ):
        output.append({
            "group": "source_layer",
            "source": source,
            "uncertainty_layer": layer,
            "count": count,
        })
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Absolute-U MD candidate extraction plus current-DB-projected CUR."
    )
    parser.add_argument("--round-dir", required=True, help="NVT/NPT round directory")
    parser.add_argument("--all-frames", default=None, help="Saved uncertainty_all_frames.csv")
    parser.add_argument("--base", required=True, help="Current training ASE DB for projection")
    parser.add_argument("--output-root", required=True, help="New protected selection output directory")
    parser.add_argument("--u-min", type=float, default=0.3)
    parser.add_argument("--candidate-frame-gap", type=int, default=0)
    parser.add_argument("--target", type=int, default=100)
    parser.add_argument("--balance-sources", action="store_true")
    parser.add_argument(
        "--require-all-sources",
        action="store_true",
        help="Require at least one physical-gate-valid candidate from every production source.",
    )
    parser.add_argument("--tail-threshold", type=float)
    parser.add_argument("--tail-max", type=int)
    parser.add_argument("--final-frame-gap", type=int, default=0)
    parser.add_argument(
        "--min-volume-per-atom",
        type=float,
        help="Reject candidate frames below this physical volume gate in A^3/atom.",
    )
    parser.add_argument(
        "--max-volume-per-atom",
        type=float,
        help="Reject candidate frames above this physical volume gate in A^3/atom.",
    )
    parser.add_argument(
        "--max-force",
        type=float,
        help="Reject candidate frames above this committee-mean force gate in eV/A.",
    )
    parser.add_argument(
        "--min-distance",
        type=float,
        help="Reject candidate frames below this minimum pair-distance gate in A.",
    )
    parser.add_argument("--r-c", type=float, default=6.0)
    parser.add_argument("--n-max", type=int, default=5)
    parser.add_argument("--l-max", type=int, default=6)
    parser.add_argument("--similarity-threshold", type=float, default=0.99999)
    parser.add_argument("--no-similarity-threshold", action="store_true")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if not math.isfinite(args.u_min):
        raise ValueError("--u-min must be finite")
    if args.tail_max is not None:
        if args.tail_threshold is None:
            raise ValueError("--tail-max requires --tail-threshold")
        if not math.isfinite(args.tail_threshold) or args.tail_threshold < args.u_min:
            raise ValueError("--tail-threshold must be finite and >= --u-min")
    if args.candidate_frame_gap < 0 or args.final_frame_gap < 0:
        raise ValueError("Frame gaps must be >= 0")
    if args.target <= 0 or (args.tail_max is not None and args.tail_max < 0):
        raise ValueError("--target must be > 0 and --tail-max must be >= 0")
    if args.r_c <= 0 or args.n_max <= 0 or args.l_max <= 0:
        raise ValueError("Descriptor parameters must be positive")
    if not args.no_similarity_threshold and not 0.0 <= args.similarity_threshold <= 1.0:
        raise ValueError("--similarity-threshold must be in [0, 1]")
    for name in (
        "min_volume_per_atom",
        "max_volume_per_atom",
        "max_force",
        "min_distance",
    ):
        value = getattr(args, name)
        if value is not None and (not math.isfinite(value) or value <= 0.0):
            raise ValueError(f"--{name.replace('_', '-')} must be finite and positive")
    if (
        args.min_volume_per_atom is not None
        and args.max_volume_per_atom is not None
        and args.min_volume_per_atom >= args.max_volume_per_atom
    ):
        raise ValueError("--min-volume-per-atom must be below --max-volume-per-atom")


def main() -> None:
    args = parse_args()
    validate_args(args)
    round_dir = Path(args.round_dir)
    all_frames_path = Path(args.all_frames) if args.all_frames else round_dir / "uncertainty_all_frames.csv"
    base_path = Path(args.base)
    output_root = Path(args.output_root)
    if output_root.exists():
        raise FileExistsError(f"Output exists; refusing to overwrite: {output_root}")
    if not all_frames_path.is_file():
        raise FileNotFoundError(f"Missing all-frame uncertainty CSV: {all_frames_path}")
    if not base_path.is_file():
        raise FileNotFoundError(f"Missing base database: {base_path}")

    all_rows = read_csv(all_frames_path)
    expected_sources = {
        row.get("trajectory", "")
        for row in all_rows
        if row.get("discarded_equilibration", "").strip().lower() == "false"
    }
    expected_sources.discard("")
    selected_by_source, physical_gate_rejections = select_spaced_candidates(
        all_rows,
        args.u_min,
        args.candidate_frame_gap,
        args.min_volume_per_atom,
        args.max_volume_per_atom,
        args.max_force,
    )

    tmp_root = output_root.parent / f".{output_root.name}.tmp-{os.getpid()}"
    if tmp_root.exists():
        raise FileExistsError(f"Temporary output path exists: {tmp_root}")
    try:
        tmp_root.mkdir(parents=True)
        u_tag = f"{args.u_min:.6g}".replace("-", "m").replace(".", "p")
        candidate_dir = tmp_root / f"u{u_tag}-gap{args.candidate_frame_gap}-candidates-poscar"
        candidate_rows, distance_rejections = write_candidate_poscars(
            selected_by_source, candidate_dir, args.min_distance
        )
        physical_gate_rejections.extend(distance_rejections)
        candidate_count = len(candidate_rows)
        sources = sorted({row["trajectory"] for row in candidate_rows}, key=source_sort_key)
        if args.require_all_sources:
            missing_sources = sorted(expected_sources - set(sources), key=source_sort_key)
            if missing_sources:
                raise RuntimeError(
                    "Physical/U gates removed all candidates for required sources: "
                    + ", ".join(missing_sources)
                )
        if args.balance_sources and args.target < len(sources):
            raise ValueError(
                f"Target {args.target} must be at least the source count {len(sources)}"
            )
        if args.balance_sources:
            source_min = args.target // len(sources)
            source_max = int(math.ceil(args.target / len(sources)))
        else:
            source_min = 0
            source_max = args.target
        if candidate_count < args.target:
            raise ValueError(f"Only {candidate_count} candidates for target {args.target}")
        print(
            f"Candidates: sources={len(sources)} count={candidate_count} "
            f"u_min={args.u_min:g} candidate_gap={args.candidate_frame_gap}",
            flush=True,
        )
        if args.balance_sources:
            print(
                f"Source quotas: min={source_min} max={source_max} target={args.target}",
                flush=True,
            )
        print(
            "Candidate counts by source: "
            + str({source: sum(row["trajectory"] == source for row in candidate_rows) for source in sources}),
            flush=True,
        )
        write_csv(
            tmp_root / "physical_gate_rejections.csv",
            physical_gate_rejections,
            PHYSICAL_GATE_REJECTION_FIELDS,
        )

        print("Constructing feature matrix for candidates...", flush=True)
        structures, labels = read_structures(candidate_dir)
        if len(structures) != len(candidate_rows):
            raise RuntimeError(
                f"Candidate structure/metadata mismatch: {len(structures)} vs {len(candidate_rows)}"
            )
        metadata_map = {row["candidate_file"]: row for row in candidate_rows}
        metadata = [metadata_map[label] for label in labels]
        x_current = build_feature_matrix(
            structures, args.r_c, args.n_max, args.l_max, "Feature Extraction (Candidates)"
        )
        x_raw = x_current.copy()
        x_current, max_base_similarity = project_base_space(
            x_current, x_raw, str(base_path), args.r_c, args.n_max, args.l_max
        )
        x_similarity = normalize_columns(x_current.copy())
        similarity_threshold = None if args.no_similarity_threshold else args.similarity_threshold

        selector = SourceTailCurSelector(
            x_current=x_current,
            x_similarity=x_similarity,
            metadata=metadata,
            max_base_similarity=max_base_similarity,
            source_min=source_min,
            source_max=source_max,
            target=args.target,
            tail_threshold=args.tail_threshold,
            tail_max=args.tail_max,
            similarity_threshold=similarity_threshold,
            min_frame_gap=args.final_frame_gap,
        )
        selected_indices, selection_records = selector.run()
        if len(selected_indices) != args.target:
            raise RuntimeError(f"Selected {len(selected_indices)}, expected {args.target}")

        selected_dir = tmp_root / f"cur-selected-poscar_absolute_u{u_tag}_cur{args.target}"
        write_selected_structures(
            selected_dir, structures, selected_indices, labels, selection_records=selection_records
        )
        updated_rows = update_metadata(
            candidate_rows, labels, selected_indices, selection_records, max_base_similarity
        )
        write_csv(tmp_root / "selection_summary.csv", updated_rows, CANDIDATE_FIELDS)
        write_csv(
            tmp_root / "cur_selected_distribution.csv",
            distribution_rows(updated_rows, args.tail_threshold),
            ("group", "source", "uncertainty_layer", "count"),
        )
        (tmp_root / "selection_parameters.txt").write_text(
            "\n".join(
                [
                    f"u_min={args.u_min}",
                    f"candidate_frame_gap={args.candidate_frame_gap}",
                    f"target={args.target}",
                    f"source_count={len(sources)}",
                    f"balance_sources={args.balance_sources}",
                    f"require_all_sources={args.require_all_sources}",
                    f"source_min={source_min}",
                    f"source_max={source_max}",
                    f"tail_threshold={args.tail_threshold}",
                    f"tail_max={args.tail_max}",
                    f"final_frame_gap={args.final_frame_gap}",
                    f"r_c={args.r_c}",
                    f"n_max={args.n_max}",
                    f"l_max={args.l_max}",
                    f"similarity_threshold={similarity_threshold}",
                    f"min_volume_per_atom={args.min_volume_per_atom}",
                    f"max_volume_per_atom={args.max_volume_per_atom}",
                    f"max_force={args.max_force}",
                    f"min_distance={args.min_distance}",
                    f"physical_gate_rejection_count={len(physical_gate_rejections)}",
                    f"base={base_path}",
                    f"all_frames={all_frames_path}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        os.replace(tmp_root, output_root)
    except Exception:
        shutil.rmtree(tmp_root, ignore_errors=True)
        raise

    print(f"Done: selected {args.target} structures into {output_root}", flush=True)
    print(f"Source counts: {dict(selector.source_counts)}", flush=True)
    if args.tail_threshold is not None:
        print(f"Tail U >= {args.tail_threshold:g}: {selector.tail_count}", flush=True)
    print(f"Rejected by similarity: {len(selector.rejected_indices)}", flush=True)


if __name__ == "__main__":
    main()
