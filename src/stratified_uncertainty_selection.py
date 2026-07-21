#!/usr/bin/env python3
"""Build uncertainty-stratified candidate pools from MD trajectories."""

from __future__ import annotations

import argparse
import csv
import math
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from ase import units
from ase.geometry import wrap_positions
from ase.io import iread, write

SCRIPT_DIR = Path(globals().get("__file__", sys.argv[0])).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from uncertainty_selection import build_calculators, committee_forces, set_default_thread_limits


DEFAULT_BINS = (
    ("0-40", 0.00, 0.40),
    ("40-70", 0.40, 0.70),
    ("70-90", 0.70, 0.90),
    ("90-98", 0.90, 0.98),
    ("98-100", 0.98, 1.00),
)


@dataclass(frozen=True)
class TrajectorySpec:
    label: str
    path: Path
    source_type: str
    source_value: float | None = None
    pressure_gpa: float | None = None
    scale_factor: float | None = None


def parse_values(text: str) -> list[float]:
    values = []
    for item in text.split(","):
        item = item.strip()
        if item:
            values.append(float(item))
    if not values:
        raise ValueError("At least one numeric value is required")
    return values


def format_value(value: float) -> str:
    return ("%g" % value).replace("-", "m").replace(".", "p")


def parse_label_value(text: str) -> float | None:
    try:
        return float(text.replace("m", "-").replace("p", "."))
    except ValueError:
        return None


def infer_source(label: str, path: Path) -> TrajectorySpec:
    if label.startswith("P-") and label.endswith("GPa"):
        value = parse_label_value(label[2:-3])
        return TrajectorySpec(
            label=label,
            path=path,
            source_type="npt_pressure",
            source_value=value,
            pressure_gpa=value,
        )
    if label.startswith("scale-"):
        value = parse_label_value(label[len("scale-"):])
        return TrajectorySpec(
            label=label,
            path=path,
            source_type="nvt_scale",
            source_value=value,
            scale_factor=value,
        )
    return TrajectorySpec(label=label, path=path, source_type="generic")


def source_sort_key(spec: TrajectorySpec) -> tuple[str, float, str]:
    value = spec.source_value if spec.source_value is not None else float("inf")
    return (spec.source_type, value, spec.label)


def labels_from_text(text: str) -> list[str]:
    labels = [item.strip() for item in text.split(",") if item.strip()]
    if not labels:
        raise ValueError("At least one source label is required")
    return labels


def find_trajectories(
    round_dir: Path,
    mode: str,
    pressures: list[float],
    scales: list[float],
    source_labels: list[str] | None,
    trajectory_name: str,
) -> list[TrajectorySpec]:
    specs = []
    if source_labels:
        for label in source_labels:
            path = round_dir / "md" / label / trajectory_name
            if not path.exists():
                raise FileNotFoundError(f"Missing trajectory for {label}: {path}")
            specs.append(infer_source(label, path))
        return sorted(specs, key=source_sort_key)

    if mode == "npt":
        labels = [f"P-{format_value(pressure)}GPa" for pressure in pressures]
    elif mode == "nvt":
        labels = [f"scale-{format_value(scale)}" for scale in scales]
    elif mode == "auto":
        md_root = round_dir / "md"
        if not md_root.exists():
            raise FileNotFoundError(f"Missing MD directory: {md_root}")
        labels = [
            path.parent.name
            for path in md_root.glob(f"*/{trajectory_name}")
            if path.is_file()
        ]
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    for label in labels:
        path = round_dir / "md" / label / trajectory_name
        if not path.exists():
            raise FileNotFoundError(f"Missing trajectory for {label}: {path}")
        specs.append(infer_source(label, path))
    return sorted(specs, key=source_sort_key)


def sorted_jnn_paths(pattern: str) -> list[Path]:
    paths = sorted(Path().glob(pattern))
    if len(paths) < 2:
        raise ValueError(f"Committee uncertainty requires at least two .jnn files from: {pattern}")
    return paths


def instant_pressure_gpa(atoms) -> float | None:
    stress = atoms.info.get("stress")
    if stress is None:
        try:
            # extxyz trajectories commonly restore calculator stress; include
            # the kinetic contribution to match NPT thermodynamic pressure.
            stress = atoms.get_stress(voigt=True, include_ideal_gas=True)
        except (AttributeError, RuntimeError):
            return None
    arr = np.asarray(stress, dtype=float)
    if not np.isfinite(arr).all():
        return None
    if arr.shape == (3, 3):
        pressure_ev_a3 = -float(np.trace(arr)) / 3.0
    elif arr.size >= 3:
        pressure_ev_a3 = -float(arr.reshape(-1)[:3].sum()) / 3.0
    else:
        return None
    return pressure_ev_a3 / units.GPa


def score_atoms(atoms, calculators) -> tuple[float, float, float]:
    forces = committee_forces(atoms, calculators)
    model_count = forces.shape[0]
    if model_count < 2:
        raise ValueError("Committee uncertainty requires at least two calculators")
    force_mean = forces.mean(axis=0)
    force_diff = forces - force_mean[None, :, :]
    covariance_trace = np.sum(force_diff * force_diff, axis=(0, 2)) / (model_count - 1)
    uncertainty = float(np.sqrt(covariance_trace).max())
    max_force = float(np.linalg.norm(force_mean, axis=1).max())
    max_force_model0 = float(np.linalg.norm(forces[0], axis=1).max())
    return uncertainty, max_force, max_force_model0


def score_trajectory(spec: TrajectorySpec, calculators, progress_interval: int) -> list[dict]:
    records = []
    frame_count = 0
    for frame, atoms in enumerate(iread(str(spec.path), index=":")):
        frame_count += 1
        positions = wrap_positions(atoms.get_positions(), atoms.get_cell(), atoms.get_pbc())
        atoms.set_positions(positions)
        uncertainty, max_force, max_force_model0 = score_atoms(atoms, calculators)
        records.append(
            {
                "pressure_gpa": spec.pressure_gpa,
                "scale_factor": spec.scale_factor,
                "source_type": spec.source_type,
                "source_value": spec.source_value,
                "trajectory": spec.label,
                "trajectory_path": str(spec.path),
                "frame": frame,
                "uncertainty": uncertainty,
                "uncertainty_bin": "",
                "volume_per_atom": float(atoms.get_volume() / len(atoms)),
                "max_force": max_force,
                "max_force_model0": max_force_model0,
                "instant_pressure_gpa": instant_pressure_gpa(atoms),
                "discarded_equilibration": False,
                "selected_candidate": False,
                "candidate_id": "",
                "candidate_file": "",
                "selection_rank_in_bin": "",
                "cur_score": "",
                "final_selected": False,
            }
        )
        if progress_interval and frame_count % progress_interval == 0:
            print(
                f"scored {spec.label}: frames={frame_count} "
                f"last_uncertainty={uncertainty:.8f}",
                flush=True,
            )
    print(f"scored {spec.label}: frames={frame_count} done", flush=True)
    return records


def assign_bins(production_records: list[dict]) -> dict[str, list[dict]]:
    sorted_records = sorted(production_records, key=lambda item: item["uncertainty"])
    n_records = len(sorted_records)
    bins: dict[str, list[dict]] = {}
    for label, low, high in DEFAULT_BINS:
        start = int(math.floor(low * n_records))
        stop = n_records if high >= 1.0 else int(math.floor(high * n_records))
        bin_records = sorted_records[start:stop]
        for record in bin_records:
            record["uncertainty_bin"] = label
        bins[label] = bin_records
    return bins


def pick_spaced_random(
    records: list[dict],
    n_select: int,
    min_frame_gap: int,
    rng: np.random.Generator,
    blocked_frames: list[int],
) -> list[dict]:
    best: list[dict] = []
    attempts = 200
    for _ in range(attempts):
        order = list(range(len(records)))
        rng.shuffle(order)
        selected: list[dict] = []
        local_frames: list[int] = []
        for index in order:
            record = records[index]
            frame = int(record["frame"])
            all_blocked = blocked_frames + local_frames
            if all(abs(frame - other) >= min_frame_gap for other in all_blocked):
                selected.append(record)
                local_frames.append(frame)
                if len(selected) >= n_select:
                    return selected
        if len(selected) > len(best):
            best = selected
    return best


def select_records_for_trajectory(
    records: list[dict],
    per_bin: int,
    min_frame_gap: int,
    spacing_scope: str,
    seed: int,
    source_index: int,
    equilibration_fraction: float,
) -> tuple[list[dict], list[dict]]:
    n_total = len(records)
    n_equil = int(math.floor(n_total * equilibration_fraction))
    for record in records[:n_equil]:
        record["discarded_equilibration"] = True
    production_records = records[n_equil:]
    bins = assign_bins(production_records)

    selected: list[dict] = []
    summary_rows = []
    global_blocked: list[int] = []

    # Select sparse/high-uncertainty strata first if global spacing is requested.
    bin_order = list(reversed(DEFAULT_BINS)) if spacing_scope == "global" else list(DEFAULT_BINS)
    for bin_position, (label, low, high) in enumerate(bin_order):
        bin_records = bins[label]
        rng = np.random.default_rng(seed + 1009 * source_index + 9173 * bin_position)
        blocked = global_blocked if spacing_scope == "global" else []
        chosen = pick_spaced_random(bin_records, per_bin, min_frame_gap, rng, blocked)
        for rank, record in enumerate(chosen, start=1):
            record["selected_candidate"] = True
            record["selection_rank_in_bin"] = rank
        selected.extend(chosen)
        if spacing_scope == "global":
            global_blocked.extend(int(record["frame"]) for record in chosen)

        uncertainties = [item["uncertainty"] for item in bin_records]
        summary_rows.append(
            {
                "pressure_gpa": records[0]["pressure_gpa"] if records else "",
                "scale_factor": records[0]["scale_factor"] if records else "",
                "source_type": records[0]["source_type"] if records else "",
                "source_value": records[0]["source_value"] if records else "",
                "trajectory": records[0]["trajectory"] if records else "",
                "uncertainty_bin": label,
                "percentile_low": low * 100.0,
                "percentile_high": high * 100.0,
                "available_frames": len(bin_records),
                "requested": per_bin,
                "selected": len(chosen),
                "uncertainty_min": min(uncertainties) if uncertainties else "",
                "uncertainty_max": max(uncertainties) if uncertainties else "",
                "uncertainty_mean": float(np.mean(uncertainties)) if uncertainties else "",
                "equilibration_frames_discarded": n_equil,
                "production_frames": len(production_records),
                "min_frame_gap": min_frame_gap,
                "spacing_scope": spacing_scope,
            }
        )

    selected.sort(key=lambda item: (item["trajectory"], item["uncertainty_bin"], item["frame"]))
    return selected, summary_rows


def write_selected_poscars(spec: TrajectorySpec, selected_records: list[dict], output_dir: Path, start_index: int) -> int:
    frame_to_record = {int(record["frame"]): record for record in selected_records}
    counter = start_index
    for frame, atoms in enumerate(iread(str(spec.path), index=":")):
        record = frame_to_record.get(frame)
        if record is None:
            continue
        candidate_id = f"{counter:06d}"
        out_name = (
            f"{candidate_id}_{spec.label}_bin{record['uncertainty_bin']}"
            f"_frame{frame:08d}.poscar"
        )
        out_path = output_dir / out_name
        positions = wrap_positions(atoms.get_positions(), atoms.get_cell(), atoms.get_pbc())
        atoms.set_positions(positions)
        write(out_path, atoms, format="vasp")
        record["candidate_id"] = candidate_id
        record["candidate_file"] = out_name
        counter += 1
    missing = [record["frame"] for record in selected_records if not record["candidate_file"]]
    if missing:
        raise RuntimeError(f"Failed to write selected frames for {spec.label}: {missing[:10]}")
    return counter


def csv_value(value):
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.10g}"
    return value


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: csv_value(row.get(name, "")) for name in fieldnames})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score MD trajectories and write uncertainty-stratified POSCAR candidates."
    )
    parser.add_argument("--round-dir", default="Al-potential/04-npt-round-2")
    parser.add_argument(
        "--jnn-glob",
        default="results/al_eos_benchmark/model_versions/M3_from_D3/train-committee-5000/train-*/*.jnn",
    )
    parser.add_argument(
        "--mode",
        choices=("npt", "nvt", "auto"),
        default="npt",
        help="Trajectory source mode: NPT pressure labels, NVT scale labels, or auto-discover md/* trajectories.",
    )
    parser.add_argument("--pressures", default="1,5,10,20,30,40,50")
    parser.add_argument("--scales", default="0.85,0.9,0.95,1.0,1.05,1.1")
    parser.add_argument(
        "--source-labels",
        default=None,
        help="Comma-separated explicit trajectory labels under round_dir/md, overriding --mode.",
    )
    parser.add_argument("--trajectory-name", default="multi_nnap_md.xyz")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--all-frames-csv", default=None)
    parser.add_argument("--selection-csv", default=None)
    parser.add_argument("--bin-summary-csv", default=None)
    parser.add_argument("--per-bin", type=int, default=20)
    parser.add_argument("--min-frame-gap", type=int, default=50)
    parser.add_argument(
        "--spacing-scope",
        choices=("bin", "global"),
        default="bin",
        help=(
            "Frame spacing scope. Strict global spacing may be unable to select "
            "the requested number of frames from short production segments; bin scope keeps "
            "the requested 20 candidates per uncertainty stratum."
        ),
    )
    parser.add_argument("--equilibration-fraction", type=float, default=0.10)
    parser.add_argument("--seed", type=int, default=20260708)
    parser.add_argument("--progress-interval", type=int, default=500)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    set_default_thread_limits()

    round_dir = Path(args.round_dir)
    output_dir = Path(args.output_dir) if args.output_dir else round_dir / "uncertainty-stratified-candidates-poscar"
    all_frames_csv = Path(args.all_frames_csv) if args.all_frames_csv else round_dir / "uncertainty_all_frames.csv"
    selection_csv = Path(args.selection_csv) if args.selection_csv else round_dir / "selection_summary.csv"
    bin_summary_csv = Path(args.bin_summary_csv) if args.bin_summary_csv else round_dir / "uncertainty_bin_summary.csv"

    if output_dir.exists():
        if not args.overwrite:
            raise FileExistsError(f"Output directory exists; use --overwrite: {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    for path in (all_frames_csv, selection_csv, bin_summary_csv):
        if path.exists() and not args.overwrite:
            raise FileExistsError(f"Output file exists; use --overwrite: {path}")

    pressures = parse_values(args.pressures)
    scales = parse_values(args.scales)
    source_labels = labels_from_text(args.source_labels) if args.source_labels else None
    trajectories = find_trajectories(
        round_dir,
        args.mode,
        pressures,
        scales,
        source_labels,
        args.trajectory_name,
    )
    jnn_paths = sorted_jnn_paths(args.jnn_glob)
    print(
        f"stratified uncertainty selection: trajectories={len(trajectories)} "
        f"committee={len(jnn_paths)} per_bin={args.per_bin} seed={args.seed}",
        flush=True,
    )
    if args.spacing_scope == "global":
        print(
            "warning: global frame spacing may produce fewer than requested "
            "candidates for these trajectory lengths",
            flush=True,
        )

    calculators = build_calculators(jnn_paths)
    all_records: list[dict] = []
    selected_records: list[dict] = []
    bin_summary_rows: list[dict] = []
    next_index = 1

    for source_index, spec in enumerate(trajectories):
        records = score_trajectory(spec, calculators, args.progress_interval)
        selected, summary_rows = select_records_for_trajectory(
            records,
            args.per_bin,
            args.min_frame_gap,
            args.spacing_scope,
            args.seed,
            source_index,
            args.equilibration_fraction,
        )
        next_index = write_selected_poscars(spec, selected, output_dir, next_index)
        all_records.extend(records)
        selected_records.extend(selected)
        bin_summary_rows.extend(summary_rows)
        print(
            f"selected {spec.label}: candidates={len(selected)} "
            f"from frames={len(records)}",
            flush=True,
        )

    record_fields = [
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
    ]
    write_csv(all_frames_csv, all_records, record_fields)
    write_csv(selection_csv, selected_records, record_fields)
    write_csv(
        bin_summary_csv,
        bin_summary_rows,
        [
            "pressure_gpa",
            "scale_factor",
            "source_type",
            "source_value",
            "trajectory",
            "uncertainty_bin",
            "percentile_low",
            "percentile_high",
            "available_frames",
            "requested",
            "selected",
            "uncertainty_min",
            "uncertainty_max",
            "uncertainty_mean",
            "equilibration_frames_discarded",
            "production_frames",
            "min_frame_gap",
            "spacing_scope",
        ],
    )
    print(
        f"done: candidates={len(selected_records)} output_dir={output_dir} "
        f"selection_csv={selection_csv}",
        flush=True,
    )


if __name__ == "__main__":
    main()
