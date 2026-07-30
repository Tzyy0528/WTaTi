#!/bin/bash
#SBATCH -J unary_rss_select
#SBATCH -o slurm-%x-%j.out
#SBATCH -e slurm-%x-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
##SBATCH --partition=your_partition
##SBATCH --account=your_account

# Run the approved RSS all-frame score, geometry audit, and projected CUR
# sequence for one element. It never labels, merges, trains, or evaluates.
set -euo pipefail

usage() {
    cat >&2 <<'EOF'
Usage:
  sbatch --output <round>/slurm_logs/rss-select-%j.out \
    --error <round>/slurm_logs/rss-select-%j.err \
    scripts/slurm/run_rss_selection_pipeline.slurm \
    --element W|Ta|Ti \
    --round-dir <X>-potential/fcc-restart/05-rss-round-1 \
    --base <X>-potential/fcc-restart/current.db \
    --jnn-glob '<X>-potential/fcc-restart/model_versions/M4_from_D4/train-committee/train-*/*.jnn' \
    --target 100 \
    --min-distance <A> \
    --max-normalized-void <R_void/(V/N)^(1/3)> \
    --r-c 6.0 --n-max 5 --l-max 6 --similarity-threshold 0.99999 \
    [--mini-failure-log <round>/rss/logs/unary-<X>.log]

The retained RSS pool must have passed raw/minimized/flat provenance validation.
This template uses the frozen D5 card: atom counts 9,10,12,15,18,20,22,25;
50 raw structures/count; Mini pressures 0,200000,400000 bar; zero frame
gaps; p99 tail; and tail cap floor(target/20). It writes only beneath the new
protected <round>/rss-selection/ root and refuses existing output.

When --mini-failure-log is supplied, only the explicit exit=1 records in its
final JSE `LMP FAIL LIST` are excluded. The scorer retains a failure-exclusion
CSV and still requires complete valid provenance for every nonfailed source.
EOF
}

for arg in "$@"; do
    if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
        usage
        exit 0
    fi
done
if [[ -z "${SLURM_JOB_ID:-}" ]]; then
    echo "Submit RSS selection with sbatch; do not run full-committee scoring on a login node." >&2
    usage
    exit 2
fi

ELEMENT=""
ROUND_DIR=""
BASE=""
JNN_GLOB=""
TARGET=""
MIN_DISTANCE=""
MAX_NORMALIZED_VOID=""
R_C=""
N_MAX=""
L_MAX=""
SIMILARITY_THRESHOLD=""
MINI_FAILURE_LOG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --element) ELEMENT="${2:-}"; shift 2 ;;
        --round-dir) ROUND_DIR="${2:-}"; shift 2 ;;
        --base) BASE="${2:-}"; shift 2 ;;
        --jnn-glob) JNN_GLOB="${2:-}"; shift 2 ;;
        --target) TARGET="${2:-}"; shift 2 ;;
        --min-distance) MIN_DISTANCE="${2:-}"; shift 2 ;;
        --max-normalized-void) MAX_NORMALIZED_VOID="${2:-}"; shift 2 ;;
        --r-c) R_C="${2:-}"; shift 2 ;;
        --n-max) N_MAX="${2:-}"; shift 2 ;;
        --l-max) L_MAX="${2:-}"; shift 2 ;;
        --similarity-threshold) SIMILARITY_THRESHOLD="${2:-}"; shift 2 ;;
        --mini-failure-log) MINI_FAILURE_LOG="${2:-}"; shift 2 ;;
        *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

if [[ "$ELEMENT" != "W" && "$ELEMENT" != "Ta" && "$ELEMENT" != "Ti" ]]; then
    echo "--element must be W, Ta, or Ti." >&2
    exit 2
fi
for name in ROUND_DIR BASE JNN_GLOB TARGET MIN_DISTANCE MAX_NORMALIZED_VOID R_C N_MAX L_MAX SIMILARITY_THRESHOLD; do
    if [[ -z "${!name}" ]]; then
        echo "Missing required option: $name" >&2
        usage
        exit 2
    fi
done
if [[ ! "$TARGET" =~ ^[1-9][0-9]*$ ]]; then
    echo "--target must be a positive integer." >&2
    exit 2
fi

REPO_DIR="${SLURM_SUBMIT_DIR:-$PWD}"
cd "$REPO_DIR"

assert_element_path() {
    local label="$1"
    local path="$2"
    if [[ "$path" != "$ELEMENT-potential/"* ]]; then
        echo "$label must be below $ELEMENT-potential/: $path" >&2
        exit 2
    fi
    for other in W Ta Ti; do
        if [[ "$other" != "$ELEMENT" && "$path" == *"$other-potential"* ]]; then
            echo "$label mixes $ELEMENT with $other: $path" >&2
            exit 2
        fi
    done
}

assert_element_path "--round-dir" "$ROUND_DIR"
assert_element_path "--base" "$BASE"
assert_element_path "--jnn-glob" "$JNN_GLOB"
if [[ -n "$MINI_FAILURE_LOG" ]]; then
    assert_element_path "--mini-failure-log" "$MINI_FAILURE_LOG"
fi
if [[ ! -d "$ROUND_DIR" || ! -f "$BASE" ]]; then
    echo "Missing RSS round directory or D4 base database." >&2
    exit 1
fi

RSS_ROOT="$ROUND_DIR/rss"
POOL_DIR="$RSS_ROOT/rss-minimized-poscar"
MANIFEST="$POOL_DIR/manifest.tsv"
MINIMIZED_DIR="$RSS_ROOT/minimized/unary-$ELEMENT"
RAW_DIR="$RSS_ROOT/raw/unary-$ELEMENT"
SELECTION_ROOT="$ROUND_DIR/rss-selection"
for path in \
    "$POOL_DIR" "$MANIFEST" "$POOL_DIR/.rss_done" \
    "$MINIMIZED_DIR" "$MINIMIZED_DIR/.rss_done" "$RAW_DIR"; do
    if [[ ! -e "$path" ]]; then
        echo "Missing retained RSS input: $path" >&2
        exit 1
    fi
done
if [[ -n "$MINI_FAILURE_LOG" && ! -f "$MINI_FAILURE_LOG" ]]; then
    echo "Missing retained Mini failure log: $MINI_FAILURE_LOG" >&2
    exit 1
fi
if [[ -e "$SELECTION_ROOT" ]]; then
    echo "Refusing existing RSS selection output: $SELECTION_ROOT" >&2
    exit 1
fi

shopt -s nullglob
JNN_PATHS=($JNN_GLOB)
if (( ${#JNN_PATHS[@]} != 10 )); then
    echo "Need exactly ten matching committee JNNs from: $JNN_GLOB" >&2
    exit 1
fi
for jnn in "${JNN_PATHS[@]}"; do
    assert_element_path "JNN path" "$jnn"
    if [[ ! -s "$jnn" || ! -f "$(dirname "$jnn")/log" ]]; then
        echo "Missing nonempty JNN or trainer log: $jnn" >&2
        exit 1
    fi
done

LOG_DIR="$ROUND_DIR/slurm_logs"
mkdir -p "$LOG_DIR"
U_MIN_RECORD="$LOG_DIR/rss-selection-u-min-${SLURM_JOB_ID}.txt"
INPUT_RECORD="$LOG_DIR/rss-selection-inputs-${SLURM_JOB_ID}.txt"
for path in \
    "$U_MIN_RECORD" "$INPUT_RECORD" \
    "$LOG_DIR/rss-score-command-${SLURM_JOB_ID}.sh" \
    "$LOG_DIR/rss-audit-command-${SLURM_JOB_ID}.sh" \
    "$LOG_DIR/rss-cur-command-${SLURM_JOB_ID}.sh"; do
    if [[ -e "$path" ]]; then
        echo "Refusing existing selection record: $path" >&2
        exit 1
    fi
done

module load jse
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

python3 - "$BASE" "$ELEMENT" <<'PY'
import math
import sys
import numpy as np
from ase.db import connect

path, element = sys.argv[1:]
rows = list(connect(path).select())
if len(rows) != 500:
    raise RuntimeError(f"Expected 500 D4 rows, found {len(rows)}")
for row in rows:
    atoms = row.toatoms()
    if len(atoms) != 32 or set(atoms.get_chemical_symbols()) != {element}:
        raise RuntimeError(f"Invalid D4 composition/size at row {row.id}")
    if not np.all(atoms.pbc) or not math.isfinite(float(row.energy)):
        raise RuntimeError(f"Invalid D4 PBC/energy at row {row.id}")
print(f"Validated D4 base: rows={len(rows)} element={element} natoms=32")
PY

{
    printf 'base=%s; sha256=%s\n' "$BASE" "$(sha256sum "$BASE" | awk '{print $1}')"
    if [[ -n "$MINI_FAILURE_LOG" ]]; then
        printf 'mini_failure_log=%s; sha256=%s\n' \
            "$MINI_FAILURE_LOG" "$(sha256sum "$MINI_FAILURE_LOG" | awk '{print $1}')"
    fi
    for jnn in "${JNN_PATHS[@]}"; do
        printf 'jnn=%s; sha256=%s\n' "$jnn" "$(sha256sum "$jnn" | awk '{print $1}')"
    done
} > "$INPUT_RECORD"

U_MIN="$(
    python3 - "$U_MIN_RECORD" "${JNN_PATHS[@]}" <<'PY'
import re
import sys
from pathlib import Path

record_path = Path(sys.argv[1])
values = []
for jnn_path in map(Path, sys.argv[2:]):
    log_path = jnn_path.parent / "log"
    text = log_path.read_text(encoding="utf-8", errors="replace").replace("\r", "\n")
    matches = re.findall(
        r"MAE-F:\s*([0-9]+(?:\.[0-9]+)?)\s+meV/A\s*\|\s*"
        r"([0-9]+(?:\.[0-9]+)?)\s+meV/A",
        text,
    )
    if not matches:
        raise RuntimeError(f"Could not find final MAE-F train/test pair in {log_path}")
    values.append((jnn_path, log_path, float(matches[-1][1])))

u_min = sum(value[2] for value in values) / (1000.0 * len(values))
with record_path.open("x", encoding="utf-8") as handle:
    handle.write("aggregation=mean(final_test_MAE-F_meV_per_A)/1000\n")
    handle.write(f"model_count={len(values)}\n")
    for jnn_path, log_path, test_mae in values:
        handle.write(
            f"jnn={jnn_path}; log={log_path}; "
            f"final_test_mae_f_meV_per_A={test_mae:.10g}\n"
        )
    handle.write(f"u_min_eV_per_A={u_min:.12g}\n")
print(f"{u_min:.12g}")
PY
)"
TAIL_MAX=$(( TARGET / 20 ))
echo "Derived U_min=${U_MIN} eV/A from ten M4 test-force MAEs; tail_max=${TAIL_MAX}."

write_command() {
    local path="$1"
    shift
    printf '%q ' "$@" > "$path"
    printf '\n' >> "$path"
}

score_cmd=(
    jse src/rss_all_frame_scoring.py
    --element "$ELEMENT"
    --pool-dir "$POOL_DIR"
    --manifest "$MANIFEST"
    --minimized-dir "$MINIMIZED_DIR"
    --raw-dir "$RAW_DIR"
    --jnn-glob "$JNN_GLOB"
    --output-root "$SELECTION_ROOT"
    --natoms-list 9,10,12,15,18,20,22,25
    --mini-press-list 0,200000,400000
    --raw-count-per-natoms 50
    --progress-interval 100
)
if [[ -n "$MINI_FAILURE_LOG" ]]; then
    score_cmd+=(--mini-failure-log "$MINI_FAILURE_LOG")
fi
write_command "$LOG_DIR/rss-score-command-${SLURM_JOB_ID}.sh" "${score_cmd[@]}"
echo "Stage 1/3: validate and score every RSS/Mini POSCAR."
"${score_cmd[@]}"

ALL_FRAMES="$SELECTION_ROOT/uncertainty_all_frames.csv"
AUDIT_OUTPUT="$SELECTION_ROOT/geometry_audit.csv"
CUR_ROOT="$SELECTION_ROOT/absolute-u-projected-cur"
if [[ ! -s "$ALL_FRAMES" || ! -s "$SELECTION_ROOT/rss_frame_provenance.csv" ]]; then
    echo "RSS scorer did not produce required all-frame provenance artifacts." >&2
    exit 1
fi

audit_cmd=(
    python3 src/absolute_u_projected_cur_selection.py
    --round-dir "$ROUND_DIR"
    --all-frames "$ALL_FRAMES"
    --u-min "$U_MIN"
    --candidate-frame-gap 0
    --final-frame-gap 0
    --audit-only
    --audit-output "$AUDIT_OUTPUT"
    --min-distance "$MIN_DISTANCE"
    --max-normalized-void "$MAX_NORMALIZED_VOID"
)
write_command "$LOG_DIR/rss-audit-command-${SLURM_JOB_ID}.sh" "${audit_cmd[@]}"
echo "Stage 2/3: complete post-U RSS geometry audit."
"${audit_cmd[@]}"

python3 - "$ALL_FRAMES" "$AUDIT_OUTPUT" "$U_MIN" "$TARGET" <<'PY'
import csv
import math
import sys
from pathlib import Path

all_frames_path, audit_path = map(Path, sys.argv[1:3])
u_min = float(sys.argv[3])
target = int(sys.argv[4])
with all_frames_path.open(newline="", encoding="utf-8") as handle:
    all_rows = list(csv.DictReader(handle))
with audit_path.open(newline="", encoding="utf-8") as handle:
    audit_rows = list(csv.DictReader(handle))

required_all = {"trajectory", "trajectory_path", "frame", "uncertainty", "discarded_equilibration"}
required_audit = {"trajectory", "frame", "uncertainty", "min_distance_A", "normalized_void", "geometry_gate_status"}
if not all_rows or not required_all.issubset(all_rows[0]):
    raise RuntimeError("RSS all-frame CSV has an unexpected schema")
if not audit_rows or not required_audit.issubset(audit_rows[0]):
    raise RuntimeError("RSS geometry-audit CSV has an unexpected schema")
expected = {
    (row["trajectory"], int(row["frame"]))
    for row in all_rows
    if row["discarded_equilibration"].strip().lower() == "false"
    and float(row["uncertainty"]) >= u_min
}
actual = set()
valid_uncertainties = []
for row in audit_rows:
    key = (row["trajectory"], int(row["frame"]))
    if key in actual:
        raise RuntimeError(f"Duplicate RSS geometry-audit record: {key}")
    actual.add(key)
    if row["geometry_gate_status"] not in {"passed", "rejected"}:
        raise RuntimeError(f"Invalid RSS geometry-gate status for {key}")
    for field in ("uncertainty", "min_distance_A", "normalized_void"):
        value = float(row[field])
        if not math.isfinite(value) or value <= 0.0:
            raise RuntimeError(f"Invalid {field} for {key}: {row[field]}")
    if row["geometry_gate_status"] == "passed":
        valid_uncertainties.append(float(row["uncertainty"]))
if actual != expected:
    raise RuntimeError(f"RSS geometry-audit coverage mismatch: expected={len(expected)} actual={len(actual)}")
if len(valid_uncertainties) < target:
    raise RuntimeError(f"Only {len(valid_uncertainties)} geometry-valid RSS candidates for target {target}")
valid_uncertainties.sort()
position = (len(valid_uncertainties) - 1) * 0.99
lower, upper = math.floor(position), math.ceil(position)
weight = position - lower
p99 = valid_uncertainties[lower] if lower == upper else (
    valid_uncertainties[lower] * (1.0 - weight) + valid_uncertainties[upper] * weight
)
print(f"RSS audit gate passed: post_U={len(expected)} geometry_valid={len(valid_uncertainties)} p99_U={p99:.12g}")
PY

cur_cmd=(
    python3 src/absolute_u_projected_cur_selection.py
    --round-dir "$ROUND_DIR"
    --all-frames "$ALL_FRAMES"
    --base "$BASE"
    --output-root "$CUR_ROOT"
    --u-min "$U_MIN"
    --candidate-frame-gap 0
    --final-frame-gap 0
    --target "$TARGET"
    --tail-quantile 0.99
    --tail-max "$TAIL_MAX"
    --min-distance "$MIN_DISTANCE"
    --max-normalized-void "$MAX_NORMALIZED_VOID"
    --r-c "$R_C"
    --n-max "$N_MAX"
    --l-max "$L_MAX"
    --similarity-threshold "$SIMILARITY_THRESHOLD"
)
write_command "$LOG_DIR/rss-cur-command-${SLURM_JOB_ID}.sh" "${cur_cmd[@]}"
echo "Stage 3/3: current-D4-projected CUR."
"${cur_cmd[@]}"

echo "Completed protected RSS selection pipeline: $CUR_ROOT"
