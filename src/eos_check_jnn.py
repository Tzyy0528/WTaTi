#!/usr/bin/env python3
"""Check a trained unary `.jnn` model against a fixed DFT EOS reference.

The script searches a committee directory for `.jnn` files, parses each sibling
`log` file for train/test error values, excludes models with large train/test
mismatch, then selects the lowest eligible test energy MAE.  NNAP inference is
performed by ``src/eos_predict_jnn.groovy`` through the installed JSE runtime;
the Python ``jsex`` module is not required.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import re
import shutil
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

NUMBER_RE = r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?"
TRAIN_PATTERNS = [
    re.compile(rf"\btrain(?:ing)?[_\s-]*(?:rmse|mae|mse|loss|err(?:or)?)\b\s*[:=]?\s*({NUMBER_RE})", re.I),
    re.compile(rf"\b(?:rmse|mae|mse|loss|err(?:or)?)[_\s-]*train(?:ing)?\b\s*[:=]?\s*({NUMBER_RE})", re.I),
    re.compile(rf"\btrain(?:ing)?\b\s*[:=]\s*({NUMBER_RE})", re.I),
]
LOSS_PAIR_RE = re.compile(rf"\bloss\b\s*:\s*({NUMBER_RE})(?:\s*\|\s*({NUMBER_RE}))?", re.I)
MAE_ENERGY_PAIR_RE = re.compile(
    rf"\bMAE[-_\s]*E\b\s*:\s*({NUMBER_RE})\s*meV/atom\s*\|\s*({NUMBER_RE})\s*meV/atom",
    re.I,
)
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


@dataclass(frozen=True)
class TrainingMetric:
    train: float | None = None
    test: float | None = None

    @property
    def selection(self) -> float:
        if self.test is not None:
            return self.test
        if self.train is not None:
            return self.train
        raise ValueError("TrainingMetric has neither train nor test value")

    @property
    def gap(self) -> float | None:
        if self.train is None or self.test is None:
            return None
        return abs(self.train - self.test)

    @property
    def ratio(self) -> float | None:
        if self.train is None or self.test is None:
            return None
        low = min(abs(self.train), abs(self.test))
        high = max(abs(self.train), abs(self.test))
        if low == 0.0:
            return 1.0 if high == 0.0 else float("inf")
        return high / low


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def find_log_for_jnn(jnn_path: Path) -> Path | None:
    candidates = [jnn_path.parent / "log", jnn_path.parent / "train.log"]
    candidates.extend(sorted(jnn_path.parent.glob("*.log")))
    for path in candidates:
        if path.exists() and path.is_file():
            return path
    return None


def parse_training_metric(log_path: Path) -> TrainingMetric | None:
    fallback_metric = None
    energy_metric = None
    text = log_path.read_text(encoding="utf-8", errors="ignore")
    for raw_line in text.splitlines():
        line = ANSI_RE.sub("", raw_line)
        energy_match = MAE_ENERGY_PAIR_RE.search(line)
        if energy_match:
            energy_metric = TrainingMetric(
                train=float(energy_match.group(1)),
                test=float(energy_match.group(2)),
            )
            continue
        if "train" not in line.lower():
            continue
        for pattern in TRAIN_PATTERNS:
            match = pattern.search(line)
            if match:
                fallback_metric = TrainingMetric(train=float(match.group(1)))
                break
        loss_match = LOSS_PAIR_RE.search(line)
        if loss_match:
            train = float(loss_match.group(1))
            test = float(loss_match.group(2)) if loss_match.group(2) is not None else None
            fallback_metric = TrainingMetric(train=train, test=test)
    return energy_metric or fallback_metric


def find_jnn_candidates(root: Path) -> list[Path]:
    if root.is_file() and root.suffix == ".jnn":
        return [root]
    return sorted(root.rglob("*.jnn"))


def format_optional(value: float | None) -> str:
    return "" if value is None else f"{value:.12g}"


def exclusion_reason(
    metric: TrainingMetric,
    max_train_test_ratio: float | None,
    max_train_test_gap: float | None,
) -> str:
    reasons = []
    ratio = metric.ratio
    gap = metric.gap
    if ratio is not None and max_train_test_ratio is not None and ratio > max_train_test_ratio:
        reasons.append(f"train/test ratio {ratio:.6g} > {max_train_test_ratio:.6g}")
    if gap is not None and max_train_test_gap is not None and gap > max_train_test_gap:
        reasons.append(f"train/test gap {gap:.6g} > {max_train_test_gap:.6g}")
    return "; ".join(reasons)


def select_best_jnn(
    jnn_root: Path,
    max_train_test_ratio: float | None = 1.25,
    max_train_test_gap: float | None = None,
) -> tuple[Path, TrainingMetric, list[dict[str, str]]]:
    candidates = find_jnn_candidates(jnn_root)
    if not candidates:
        raise FileNotFoundError(f"No .jnn files found under {jnn_root}")

    rows = []
    parsed = []
    for jnn_path in candidates:
        log_path = find_log_for_jnn(jnn_path)
        metric = parse_training_metric(log_path) if log_path else None
        reason = exclusion_reason(metric, max_train_test_ratio, max_train_test_gap) if metric else ""
        eligible = bool(metric and not reason)
        fold_match = re.fullmatch(r"train-(\d+)", jnn_path.parent.name)
        rows.append({
            "fold": fold_match.group(1) if fold_match else "",
            "metric_name": "energy_mae",
            "metric_unit": "meV/atom",
            "jnn_path": str(jnn_path),
            "log_path": str(log_path) if log_path else "",
            "train_metric": "" if metric is None else format_optional(metric.train),
            "test_metric": "" if metric is None else format_optional(metric.test),
            "selection_metric": "" if metric is None else f"{metric.selection:.12g}",
            "train_test_gap": "" if metric is None else format_optional(metric.gap),
            "train_test_ratio": "" if metric is None else format_optional(metric.ratio),
            "eligible": "yes" if eligible else "no",
            "exclude_reason": reason,
        })
        if eligible:
            parsed.append((metric.selection, metric.gap if metric.gap is not None else 0.0, jnn_path, metric))

    if not parsed:
        raise ValueError(
            "Could not find an eligible .jnn from committee logs. "
            "Pass --best-jnn explicitly, adjust parsing, or relax "
            "--max-train-test-ratio/--max-train-test-gap."
        )
    parsed.sort(key=lambda item: (item[0], item[1]))
    _, _, best, metric = parsed[0]
    return best, metric, rows


def normalize_prediction_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    required = ["structure", "scale", "natoms", "volume_A3", "volume_per_atom_A3", "poscar_path"]
    missing = [key for key in required if rows and key not in rows[0]]
    if missing:
        raise ValueError(f"EOS metadata is missing required columns: {missing}")
    return rows


def predict_eos(
    metadata_path: Path,
    jnn_path: Path,
    output_path: Path,
) -> list[dict[str, str]]:
    """Run the JSE/Groovy evaluator and return its validated prediction rows."""
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing prediction output: {output_path}")
    evaluator = Path(__file__).with_name("eos_predict_jnn.groovy")
    if not evaluator.exists():
        raise FileNotFoundError(f"Missing JSE EOS evaluator: {evaluator}")
    jse = shutil.which("jse")
    if jse is None:
        raise RuntimeError(
            "The JSE executable is unavailable. Load the jse module before EOS evaluation."
        )

    subprocess.run(
        [jse, str(evaluator), str(metadata_path), str(jnn_path), str(output_path)],
        check=True,
    )
    rows = read_csv(output_path)
    normalized = normalize_prediction_rows(rows)
    if not normalized:
        raise ValueError("JSE EOS evaluator produced no prediction rows")
    return normalized


def merge_reference(pred_rows: list[dict[str, str]], ref_rows: list[dict[str, str]] | None) -> list[dict[str, str]]:
    if not ref_rows:
        return pred_rows
    pred_keys = [(row["structure"], row["scale"]) for row in pred_rows]
    ref_keys = [(row["structure"], row["scale"]) for row in ref_rows]
    if len(set(pred_keys)) != len(pred_keys):
        raise ValueError("Duplicate structure/scale keys in NNAP EOS predictions")
    if len(set(ref_keys)) != len(ref_keys):
        raise ValueError("Duplicate structure/scale keys in DFT EOS reference")
    if set(pred_keys) != set(ref_keys):
        missing = sorted(set(ref_keys) - set(pred_keys))
        extra = sorted(set(pred_keys) - set(ref_keys))
        raise ValueError(
            "NNAP/DFT EOS structure-scale keys differ; "
            f"missing predictions={missing[:3]}, extra predictions={extra[:3]}"
        )
    ref_map = {
        (row["structure"], row["scale"]): row
        for row in ref_rows
    }
    merged = []
    for row in pred_rows:
        out = dict(row)
        ref = ref_map.get((row["structure"], row["scale"]))
        assert ref is not None
        if int(out["natoms"]) != int(ref["natoms"]):
            raise ValueError(
                f"NNAP/DFT atom-count mismatch for {out['structure']} scale {out['scale']}"
            )
        out["dft_energy_eV"] = ref.get("dft_energy_eV", "")
        out["dft_energy_per_atom_eV"] = ref.get("dft_energy_per_atom_eV", "")
        if not out["dft_energy_per_atom_eV"]:
            raise ValueError(
                f"DFT EOS reference lacks energy for {out['structure']} scale {out['scale']}"
            )
        merged.append(out)
    return merged


def enrich_phase_aligned_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Add raw and per-phase zero-aligned energy errors to DFT-labelled rows."""
    if not rows or not all(row.get("dft_energy_per_atom_eV") for row in rows):
        return rows

    by_structure: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_structure[row["structure"]].append(row)

    for structure_rows in by_structure.values():
        dft_min = min(float(row["dft_energy_per_atom_eV"]) for row in structure_rows)
        nnap_min = min(float(row["nnap_energy_per_atom_eV"]) for row in structure_rows)
        for row in structure_rows:
            dft = float(row["dft_energy_per_atom_eV"])
            nnap = float(row["nnap_energy_per_atom_eV"])
            dft_relative = dft - dft_min
            nnap_relative = nnap - nnap_min
            row["raw_energy_error_per_atom_eV"] = f"{nnap - dft:.12f}"
            row["dft_relative_energy_per_atom_eV"] = f"{dft_relative:.12f}"
            row["nnap_relative_energy_per_atom_eV"] = f"{nnap_relative:.12f}"
            row["phase_aligned_energy_error_per_atom_eV"] = (
                f"{nnap_relative - dft_relative:.12f}"
            )
    return rows


def error_statistics(errors: list[float]) -> tuple[float, float, float]:
    if not errors:
        raise ValueError("Cannot calculate EOS error statistics with no errors")
    mae = sum(abs(value) for value in errors) / len(errors)
    rmse = math.sqrt(sum(value * value for value in errors) / len(errors))
    return mae, rmse, max(abs(value) for value in errors)


def format_metric(value: float | None) -> str:
    return "" if value is None else f"{value:.12g}"


def calculate_eos_metrics(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return raw and phase-aligned energy metrics with grid-minimum locations."""
    if not rows or not all(row.get("dft_energy_per_atom_eV") for row in rows):
        return []

    by_structure: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_structure[row["structure"]].append(row)

    metrics: list[dict[str, str]] = []
    all_raw_errors: list[float] = []
    all_aligned_errors: list[float] = []
    ordered_structures = [name for name in ("bcc", "fcc", "hcp") if name in by_structure]
    ordered_structures += sorted(set(by_structure) - set(ordered_structures))
    for structure in ordered_structures:
        structure_rows = by_structure[structure]
        raw_errors = [float(row["raw_energy_error_per_atom_eV"]) for row in structure_rows]
        aligned_errors = [
            float(row["phase_aligned_energy_error_per_atom_eV"])
            for row in structure_rows
        ]
        raw_mae, raw_rmse, raw_max = error_statistics(raw_errors)
        aligned_mae, aligned_rmse, aligned_max = error_statistics(aligned_errors)
        dft_min_row = min(
            structure_rows,
            key=lambda row: float(row["dft_energy_per_atom_eV"]),
        )
        nnap_min_row = min(
            structure_rows,
            key=lambda row: float(row["nnap_energy_per_atom_eV"]),
        )
        dft_min_volume = float(dft_min_row["volume_per_atom_A3"])
        nnap_min_volume = float(nnap_min_row["volume_per_atom_A3"])
        metrics.append({
            "structure": structure,
            "n_points": str(len(structure_rows)),
            **metric_error_fields("raw_energy", raw_mae, raw_rmse, raw_max),
            **metric_error_fields(
                "phase_aligned_relative_energy",
                aligned_mae,
                aligned_rmse,
                aligned_max,
            ),
            "dft_grid_min_scale": dft_min_row["scale"],
            "nnap_grid_min_scale": nnap_min_row["scale"],
            "dft_grid_min_volume_per_atom_A3": format_metric(dft_min_volume),
            "nnap_grid_min_volume_per_atom_A3": format_metric(nnap_min_volume),
            "grid_min_volume_shift_A3_per_atom": format_metric(
                nnap_min_volume - dft_min_volume
            ),
            "dft_grid_min_energy_per_atom_eV": dft_min_row["dft_energy_per_atom_eV"],
            "nnap_grid_min_energy_per_atom_eV": nnap_min_row["nnap_energy_per_atom_eV"],
        })
        all_raw_errors.extend(raw_errors)
        all_aligned_errors.extend(aligned_errors)

    raw_mae, raw_rmse, raw_max = error_statistics(all_raw_errors)
    aligned_mae, aligned_rmse, aligned_max = error_statistics(all_aligned_errors)
    metrics.append({
        "structure": "all",
        "n_points": str(len(rows)),
        **metric_error_fields("raw_energy", raw_mae, raw_rmse, raw_max),
        **metric_error_fields(
            "phase_aligned_relative_energy",
            aligned_mae,
            aligned_rmse,
            aligned_max,
        ),
        "dft_grid_min_scale": "",
        "nnap_grid_min_scale": "",
        "dft_grid_min_volume_per_atom_A3": "",
        "nnap_grid_min_volume_per_atom_A3": "",
        "grid_min_volume_shift_A3_per_atom": "",
        "dft_grid_min_energy_per_atom_eV": "",
        "nnap_grid_min_energy_per_atom_eV": "",
    })
    return metrics


def metric_error_fields(
    prefix: str,
    mae_eV: float,
    rmse_eV: float,
    max_eV: float,
) -> dict[str, str]:
    return {
        f"{prefix}_mae_eV_per_atom": format_metric(mae_eV),
        f"{prefix}_rmse_eV_per_atom": format_metric(rmse_eV),
        f"{prefix}_max_abs_eV_per_atom": format_metric(max_eV),
        f"{prefix}_mae_meV_per_atom": format_metric(1000.0 * mae_eV),
        f"{prefix}_rmse_meV_per_atom": format_metric(1000.0 * rmse_eV),
        f"{prefix}_max_abs_meV_per_atom": format_metric(1000.0 * max_eV),
    }


def apply_eos_plot_style(plt) -> None:
    from matplotlib import font_manager

    try:
        font_manager.findfont("Times New Roman", fallback_to_default=False)
        font_family = "Times New Roman"
    except ValueError:
        font_family = "DejaVu Serif"

    plt.rcParams["font.family"] = font_family
    plt.rcParams["mathtext.fontset"] = "stix"


def plot_eos(rows: list[dict[str, str]], out_path: Path, title: str) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    by_structure: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_structure[row["structure"]].append(row)

    structures = [name for name in ("bcc", "fcc", "hcp") if name in by_structure]
    structures += [name for name in sorted(by_structure) if name not in structures]
    if not structures:
        raise ValueError("No EOS rows to plot")

    apply_eos_plot_style(plt)

    colors = {
        "bcc": "blue",
        "fcc": "red",
        "hcp": "green",
    }
    markers = {
        "bcc": "o",
        "fcc": "s",
        "hcp": "^",
    }

    fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)
    has_reference = any(row.get("dft_energy_per_atom_eV") for row in rows)

    for structure in structures:
        data = sorted(by_structure[structure], key=lambda row: float(row["volume_per_atom_A3"]))
        x = [float(row["volume_per_atom_A3"]) for row in data]
        y_nnap = [float(row["nnap_energy_per_atom_eV"]) for row in data]
        color = colors.get(structure, None)
        marker = markers.get(structure, "o")
        label = structure.upper()

        if has_reference:
            dft_pairs = [
                (float(row["volume_per_atom_A3"]), float(row["dft_energy_per_atom_eV"]))
                for row in data
                if row.get("dft_energy_per_atom_eV")
            ]
            if dft_pairs:
                xd, yd = zip(*dft_pairs)
                ax.scatter(
                    xd,
                    yd,
                    color=color,
                    s=90,
                    alpha=0.8,
                    marker=marker,
                    edgecolors="none",
                    linewidth=0,
                    label=label,
                    zorder=3,
                )
            ax.plot(x, y_nnap, color=color, linewidth=2.5, zorder=2)
        else:
            ax.scatter(
                x,
                y_nnap,
                color=color,
                s=90,
                alpha=0.8,
                marker=marker,
                edgecolors="none",
                linewidth=0,
                label=label,
                zorder=3,
            )
            ax.plot(x, y_nnap, color=color, linewidth=2.5, zorder=2)

    ax.set_xlabel(r"Volume/atom ($\mathrm{\AA^3/atom}$)", fontsize=18, fontweight="bold")
    ax.set_ylabel("Energy/atom (eV/atom)", fontsize=18, fontweight="bold")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=10)
    ax.grid(False)
    ax.tick_params(direction="in", axis="both", labelsize=14)

    structure_legend = ax.legend(loc="best", fontsize=12, frameon=False, title="Structure")
    ax.add_artist(structure_legend)

    if has_reference:
        style_handles = [
            Line2D([0], [0], marker="o", color="black", linestyle="none", markersize=8, label="DFT"),
            Line2D([0], [0], color="black", linewidth=2.5, label="NNAP"),
        ]
        ax.legend(
            handles=style_handles,
            loc="center right",
            bbox_to_anchor=(1.0, 0.58),
            fontsize=12,
            frameon=False,
            title="Data",
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print({"saved": str(out_path), "size_bytes": os.path.getsize(out_path)})


def plot_eos_error(rows: list[dict[str, str]], out_path: Path, title: str) -> bool:
    import matplotlib.pyplot as plt

    if not any(row.get("dft_energy_per_atom_eV") for row in rows):
        return False

    by_structure: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("dft_energy_per_atom_eV"):
            by_structure[row["structure"]].append(row)

    structures = [name for name in ("bcc", "fcc", "hcp") if name in by_structure]
    structures += [name for name in sorted(by_structure) if name not in structures]
    if not structures:
        return False

    apply_eos_plot_style(plt)

    colors = {"bcc": "blue", "fcc": "red", "hcp": "green"}
    markers = {"bcc": "o", "fcc": "s", "hcp": "^"}

    fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=True)
    for structure in structures:
        data = sorted(by_structure[structure], key=lambda row: float(row["volume_per_atom_A3"]))
        x = [float(row["volume_per_atom_A3"]) for row in data]
        y = [
            1000.0 * (
                float(row["nnap_energy_per_atom_eV"]) - float(row["dft_energy_per_atom_eV"])
            )
            for row in data
        ]
        ax.plot(
            x,
            y,
            color=colors.get(structure),
            marker=markers.get(structure, "o"),
            linewidth=2.0,
            markersize=6,
            label=structure.upper(),
        )

    ax.axhline(0.0, color="black", linewidth=1.0, linestyle="--", alpha=0.7)
    ax.set_xlabel(r"Volume/atom ($\mathrm{\AA^3/atom}$)", fontsize=16, fontweight="bold")
    ax.set_ylabel("NNAP - DFT (meV/atom)", fontsize=16, fontweight="bold")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=10)
    ax.tick_params(direction="in", axis="both", labelsize=12)
    ax.grid(True, alpha=0.2)
    ax.legend(frameon=False, fontsize=12)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print({"saved": str(out_path), "size_bytes": os.path.getsize(out_path)})
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check a unary bcc/fcc/hcp EOS set with the lowest eligible "
            "test-energy-MAE .jnn after filtering train/test mismatch."
        )
    )
    parser.add_argument(
        "--metadata",
        required=True,
        help="EOS structures metadata CSV.",
    )
    parser.add_argument(
        "--reference-csv",
        help="Optional DFT EOS reference CSV. Required unless --no-reference is set.",
    )
    parser.add_argument(
        "--jnn-root",
        help="Committee/model directory to search for .jnn files.",
    )
    parser.add_argument(
        "--best-jnn",
        help="Direct .jnn path. Overrides automatic lowest-training-error selection.",
    )
    parser.add_argument(
        "--model-id",
        default="model",
        help="Model label used in output filenames and plot title.",
    )
    parser.add_argument(
        "--output-dir",
        help="Root output directory for EOS prediction results.",
        required=True,
    )
    parser.add_argument(
        "--element",
        default="Unary",
        help="Element label used in plot titles.",
    )
    parser.add_argument(
        "--max-train-test-ratio",
        type=float,
        default=1.25,
        help=(
            "Exclude automatic candidates when max(train,test)/min(train,test) exceeds this value. "
            "Use <=0 to disable. Default: 1.25."
        ),
    )
    parser.add_argument(
        "--max-train-test-gap",
        type=float,
        help="Optional absolute train/test metric gap cutoff for automatic candidate filtering.",
    )
    parser.add_argument("--no-reference", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.best_jnn and not args.jnn_root:
        raise SystemExit("Either --jnn-root or --best-jnn is required")
    if not args.no_reference and not args.reference_csv:
        raise SystemExit("--reference-csv is required unless --no-reference is set")

    selection_rows: list[dict[str, str]] = []
    selected_metric: TrainingMetric | None = None
    if args.best_jnn:
        best_jnn = Path(args.best_jnn).resolve()
        if not best_jnn.exists():
            raise FileNotFoundError(f"Missing --best-jnn: {best_jnn}")
    else:
        max_ratio = None if args.max_train_test_ratio <= 0 else args.max_train_test_ratio
        selected_metric_path = Path(args.jnn_root).resolve()
        best_jnn, selected_metric, selection_rows = select_best_jnn(
            selected_metric_path,
            max_train_test_ratio=max_ratio,
            max_train_test_gap=args.max_train_test_gap,
        )

    out_dir = Path(args.output_dir) / args.model_id
    if out_dir.exists():
        raise FileExistsError(f"Refusing to overwrite existing EOS evaluation: {out_dir}")

    metadata_path = Path(args.metadata)
    metadata_rows = normalize_prediction_rows(read_csv(metadata_path))
    if not metadata_rows:
        raise ValueError(f"EOS metadata has no data rows: {metadata_path}")
    reference_path = Path(args.reference_csv) if args.reference_csv else None
    ref_rows = None
    if not args.no_reference:
        assert reference_path is not None
        if not reference_path.exists():
            raise FileNotFoundError(f"Missing DFT EOS reference: {reference_path}")
        ref_rows = read_csv(reference_path)
        if not ref_rows:
            raise ValueError(f"DFT EOS reference has no data rows: {reference_path}")

    out_dir.mkdir(parents=True)

    if selection_rows:
        write_csv(
            out_dir / "jnn_selection.csv",
            selection_rows,
            [
                "fold",
                "metric_name",
                "metric_unit",
                "jnn_path",
                "log_path",
                "train_metric",
                "test_metric",
                "selection_metric",
                "train_test_gap",
                "train_test_ratio",
                "eligible",
                "exclude_reason",
            ],
        )

    pred_rows = predict_eos(
        metadata_path,
        best_jnn,
        out_dir / "eos_nnap_predictions_raw.csv",
    )
    merged_rows = merge_reference(pred_rows, ref_rows)
    for row in merged_rows:
        row["committee_test_energy_mae_meV_per_atom"] = (
            "" if selected_metric is None else format_optional(selected_metric.test)
        )
    merged_rows = enrich_phase_aligned_rows(merged_rows)
    metric_rows = calculate_eos_metrics(merged_rows)

    fieldnames = [
        "structure",
        "scale",
        "natoms",
        "volume_A3",
        "volume_per_atom_A3",
        "volume_ratio",
        "poscar_path",
        "jnn_path",
        "nnap_energy_eV",
        "nnap_energy_per_atom_eV",
        "dft_energy_eV",
        "dft_energy_per_atom_eV",
        "raw_energy_error_per_atom_eV",
        "dft_relative_energy_per_atom_eV",
        "nnap_relative_energy_per_atom_eV",
        "phase_aligned_energy_error_per_atom_eV",
        "committee_test_energy_mae_meV_per_atom",
    ]
    write_csv(out_dir / "eos_predictions.csv", merged_rows, fieldnames)
    if metric_rows:
        metric_fields = [
            "structure",
            "n_points",
            "raw_energy_mae_eV_per_atom",
            "raw_energy_rmse_eV_per_atom",
            "raw_energy_max_abs_eV_per_atom",
            "raw_energy_mae_meV_per_atom",
            "raw_energy_rmse_meV_per_atom",
            "raw_energy_max_abs_meV_per_atom",
            "phase_aligned_relative_energy_mae_eV_per_atom",
            "phase_aligned_relative_energy_rmse_eV_per_atom",
            "phase_aligned_relative_energy_max_abs_eV_per_atom",
            "phase_aligned_relative_energy_mae_meV_per_atom",
            "phase_aligned_relative_energy_rmse_meV_per_atom",
            "phase_aligned_relative_energy_max_abs_meV_per_atom",
            "dft_grid_min_scale",
            "nnap_grid_min_scale",
            "dft_grid_min_volume_per_atom_A3",
            "nnap_grid_min_volume_per_atom_A3",
            "grid_min_volume_shift_A3_per_atom",
            "dft_grid_min_energy_per_atom_eV",
            "nnap_grid_min_energy_per_atom_eV",
        ]
        write_csv(out_dir / "eos_metrics.csv", metric_rows, metric_fields)
    (out_dir / "best_jnn.txt").write_text(str(best_jnn) + "\n", encoding="utf-8")
    plot_eos(merged_rows, out_dir / "eos_energy_vs_volume.png", f"{args.element} EOS: {args.model_id}")
    plot_eos_error(
        merged_rows,
        out_dir / "eos_energy_error_vs_volume.png",
        f"{args.element} EOS error: {args.model_id}",
    )
    print(f"best_jnn: {best_jnn}")
    if selected_metric is not None:
        print(f"train_metric: {format_optional(selected_metric.train)}")
        print(f"test_metric: {format_optional(selected_metric.test)}")
        print(f"selection_metric: {selected_metric.selection:.12g}")
        print(f"train_test_gap: {format_optional(selected_metric.gap)}")
        print(f"train_test_ratio: {format_optional(selected_metric.ratio)}")
    print(f"predictions: {out_dir / 'eos_predictions.csv'}")
    if metric_rows:
        print(f"metrics: {out_dir / 'eos_metrics.csv'}")


if __name__ == "__main__":
    main()
