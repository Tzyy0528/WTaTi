#!/usr/bin/env python3
"""Repeatedly check a trained `.jnn` model against the fixed Al EOS set.

The script searches a committee directory for `.jnn` files, parses each sibling
`log` file for train/test error values, excludes models with large train/test
mismatch, then selects the lowest eligible test metric. Pass `--best-jnn` to
override automatic selection when needed.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from ase.io import read

NUMBER_RE = r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?"
TRAIN_PATTERNS = [
    re.compile(rf"\btrain(?:ing)?[_\s-]*(?:rmse|mae|mse|loss|err(?:or)?)\b\s*[:=]?\s*({NUMBER_RE})", re.I),
    re.compile(rf"\b(?:rmse|mae|mse|loss|err(?:or)?)[_\s-]*train(?:ing)?\b\s*[:=]?\s*({NUMBER_RE})", re.I),
    re.compile(rf"\btrain(?:ing)?\b\s*[:=]\s*({NUMBER_RE})", re.I),
]
LOSS_PAIR_RE = re.compile(rf"\bloss\b\s*:\s*({NUMBER_RE})(?:\s*\|\s*({NUMBER_RE}))?", re.I)
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
    metric = None
    text = log_path.read_text(encoding="utf-8", errors="ignore")
    for raw_line in text.splitlines():
        line = ANSI_RE.sub("", raw_line)
        if "train" not in line.lower():
            continue
        for pattern in TRAIN_PATTERNS:
            match = pattern.search(line)
            if match:
                metric = TrainingMetric(train=float(match.group(1)))
                break
        loss_match = LOSS_PAIR_RE.search(line)
        if loss_match:
            train = float(loss_match.group(1))
            test = float(loss_match.group(2)) if loss_match.group(2) is not None else None
            metric = TrainingMetric(train=train, test=test)
    return metric


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
        rows.append({
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


def predict_eos(metadata_rows: list[dict[str, str]], jnn_path: Path, train_metric: float | None) -> list[dict[str, str]]:
    from jsex.nnap import NNAP

    potential = NNAP(str(jnn_path))
    calc = potential.ase() if hasattr(potential, "ase") else potential.asAseCalculator()
    out_rows = []
    for meta in normalize_prediction_rows(metadata_rows):
        atoms = read(meta["poscar_path"])
        atoms.calc = calc
        energy = float(atoms.get_potential_energy())
        natoms = int(meta["natoms"])
        out = {
            "structure": meta["structure"],
            "scale": meta["scale"],
            "natoms": str(natoms),
            "volume_A3": meta["volume_A3"],
            "volume_per_atom_A3": meta["volume_per_atom_A3"],
            "volume_ratio": meta.get("volume_ratio", ""),
            "nnap_energy_eV": f"{energy:.12f}",
            "nnap_energy_per_atom_eV": f"{energy / natoms:.12f}",
            "jnn_path": str(jnn_path),
            "train_metric": "" if train_metric is None else f"{train_metric:.12g}",
        }
        out_rows.append(out)
    return out_rows


def merge_reference(pred_rows: list[dict[str, str]], ref_rows: list[dict[str, str]] | None) -> list[dict[str, str]]:
    if not ref_rows:
        return pred_rows
    ref_map = {
        (row["structure"], row["scale"]): row
        for row in ref_rows
    }
    merged = []
    for row in pred_rows:
        out = dict(row)
        ref = ref_map.get((row["structure"], row["scale"]))
        if ref:
            out["dft_energy_eV"] = ref.get("dft_energy_eV", "")
            out["dft_energy_per_atom_eV"] = ref.get("dft_energy_per_atom_eV", "")
        else:
            out["dft_energy_eV"] = ""
            out["dft_energy_per_atom_eV"] = ""
        merged.append(out)
    return merged


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
            "Check Al fcc/bcc/hcp EOS with the lowest eligible test-error .jnn "
            "after filtering large train/test mismatch."
        )
    )
    parser.add_argument(
        "--metadata",
        default="results/al_eos_benchmark/eos_reference/eos_structures.csv",
        help="EOS structures metadata CSV.",
    )
    parser.add_argument(
        "--reference-csv",
        default="results/al_eos_benchmark/eos_reference/eos_reference.csv",
        help="Optional DFT EOS reference CSV. Used when present unless --no-reference is set.",
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
        default="results/al_eos_benchmark/evaluations",
        help="Root output directory for EOS prediction results.",
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

    selection_rows: list[dict[str, str]] = []
    train_metric = None
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
        train_metric = selected_metric.selection

    out_dir = Path(args.output_dir) / args.model_id
    out_dir.mkdir(parents=True, exist_ok=True)

    if selection_rows:
        write_csv(
            out_dir / "jnn_selection.csv",
            selection_rows,
            [
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

    metadata_rows = read_csv(Path(args.metadata))
    pred_rows = predict_eos(metadata_rows, best_jnn, train_metric)

    ref_rows = None
    reference_path = Path(args.reference_csv)
    if not args.no_reference and reference_path.exists():
        ref_rows = read_csv(reference_path)
    merged_rows = merge_reference(pred_rows, ref_rows)

    fieldnames = [
        "structure",
        "scale",
        "natoms",
        "volume_A3",
        "volume_per_atom_A3",
        "volume_ratio",
        "nnap_energy_eV",
        "nnap_energy_per_atom_eV",
        "dft_energy_eV",
        "dft_energy_per_atom_eV",
        "jnn_path",
        "train_metric",
    ]
    write_csv(out_dir / "eos_predictions.csv", merged_rows, fieldnames)
    (out_dir / "best_jnn.txt").write_text(str(best_jnn) + "\n", encoding="utf-8")
    plot_eos(merged_rows, out_dir / "eos_energy_vs_volume.png", f"Al EOS: {args.model_id}")
    plot_eos_error(
        merged_rows,
        out_dir / "eos_energy_error_vs_volume.png",
        f"Al EOS error: {args.model_id}",
    )
    print(f"best_jnn: {best_jnn}")
    if selected_metric is not None:
        print(f"train_metric: {format_optional(selected_metric.train)}")
        print(f"test_metric: {format_optional(selected_metric.test)}")
        print(f"selection_metric: {selected_metric.selection:.12g}")
        print(f"train_test_gap: {format_optional(selected_metric.gap)}")
        print(f"train_test_ratio: {format_optional(selected_metric.ratio)}")
    elif train_metric is not None:
        print(f"train_metric: {train_metric:.12g}")
    print(f"predictions: {out_dir / 'eos_predictions.csv'}")


if __name__ == "__main__":
    main()
