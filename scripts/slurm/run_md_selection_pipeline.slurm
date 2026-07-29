#!/bin/bash
#SBATCH -J unary_md_select
#SBATCH -o slurm-%x-%j.out
#SBATCH -e slurm-%x-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
##SBATCH --partition=your_partition
##SBATCH --account=your_account

# Run score-only uncertainty, geometry audit, and projected CUR sequentially
# for one element-local, already-approved MD selection card.
set -euo pipefail

usage() {
    cat >&2 <<'EOF'
Usage:
  sbatch --output <round_dir>/slurm_logs/select-%j.out \
    scripts/slurm/run_md_selection_pipeline.slurm \
    --element W|Ta|Ti \
    --round-dir <X>-potential/<round> \
    --base <X>-potential/current.db \
    --jnn-glob '<X>-potential/.../train-*/*.jnn' \
    --mode nvt --scales s1 s2 ... \
    --mode npt --pressures p1 p2 ... \
    --target <approved-DFT-budget> \
    --min-distance <A> \
    --max-normalized-void <R_void/(V/N)^(1/3)> \
    --r-c 6.0 --n-max 5 --l-max 6 --similarity-threshold 0.99999 \
    [--trajectory-name multi_nnap_md.xyz] \
    [--equilibration-fraction 0.10] [--progress-interval 500]

This one allocation runs, in order:
  1. full-committee score-only uncertainty -> uncertainty_all_frames.csv
  2. absolute-U/geometry audit             -> geometry_audit.csv
  3. current.db-projected CUR              -> absolute-u-projected-cur/

It derives U_min from the final test MAE-F value of every supplied model log,
records the ten values in slurm_logs/selection-u-min-<jobid>.txt, uses the
fixed p99 tail quantile, and derives tail_max=floor(0.05*target).  It enforces
zero candidate/final frame gaps and no source, volume, or force hard gates.

Every output is protected: the all-frame CSV, audit CSV, and CUR root must all
be absent before the job starts.  This runner executes only an already-approved
element-local selection card; it does not authorize DFT, merge, or training.
EOF
}

if [[ $# -eq 0 ]]; then
    usage
    exit 2
fi
for arg in "$@"; do
    if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
        usage
        exit 0
    fi
done

if [[ -z "${SLURM_JOB_ID:-}" ]]; then
    echo "Submit the combined selection pipeline with sbatch; do not run it on a login node." >&2
    usage
    exit 2
fi

REPO_DIR="${SLURM_SUBMIT_DIR:-$PWD}"
cd "$REPO_DIR"

ELEMENT=""
ROUND_DIR=""
BASE=""
JNN_GLOB=""
MODE=""
SCALES=()
PRESSURES=()
TARGET=""
MIN_DISTANCE=""
MAX_NORMALIZED_VOID=""
R_C=""
N_MAX=""
L_MAX=""
SIMILARITY_THRESHOLD=""
TRAJECTORY="multi_nnap_md.xyz"
EQUILIBRATION_FRACTION="0.10"
PROGRESS_INTERVAL="500"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --element) ELEMENT="$2"; shift 2 ;;
        --round-dir) ROUND_DIR="$2"; shift 2 ;;
        --base) BASE="$2"; shift 2 ;;
        --jnn-glob) JNN_GLOB="$2"; shift 2 ;;
        --mode) MODE="$2"; shift 2 ;;
        --scales)
            shift
            while [[ $# -gt 0 && "$1" != --* ]]; do
                SCALES+=("$1")
                shift
            done
            ;;
        --pressures)
            shift
            while [[ $# -gt 0 && "$1" != --* ]]; do
                PRESSURES+=("$1")
                shift
            done
            ;;
        --target) TARGET="$2"; shift 2 ;;
        --min-distance) MIN_DISTANCE="$2"; shift 2 ;;
        --max-normalized-void) MAX_NORMALIZED_VOID="$2"; shift 2 ;;
        --r-c) R_C="$2"; shift 2 ;;
        --n-max) N_MAX="$2"; shift 2 ;;
        --l-max) L_MAX="$2"; shift 2 ;;
        --similarity-threshold) SIMILARITY_THRESHOLD="$2"; shift 2 ;;
        --trajectory-name) TRAJECTORY="$2"; shift 2 ;;
        --equilibration-fraction) EQUILIBRATION_FRACTION="$2"; shift 2 ;;
        --progress-interval) PROGRESS_INTERVAL="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

if [[ "$ELEMENT" != "W" && "$ELEMENT" != "Ta" && "$ELEMENT" != "Ti" ]]; then
    echo "--element must be W, Ta, or Ti." >&2
    exit 2
fi
if [[ "$MODE" != "nvt" && "$MODE" != "npt" ]]; then
    echo "--mode must be nvt or npt." >&2
    exit 2
fi
for name in ROUND_DIR BASE JNN_GLOB TARGET MIN_DISTANCE MAX_NORMALIZED_VOID R_C N_MAX L_MAX SIMILARITY_THRESHOLD; do
    if [[ -z "${!name}" ]]; then
        echo "Missing required selection-card input: $name" >&2
        usage
        exit 2
    fi
done
if [[ "$MODE" == "nvt" && ${#SCALES[@]} -eq 0 ]]; then
    echo "NVT selection requires --scales." >&2
    exit 2
fi
if [[ "$MODE" == "npt" && ${#PRESSURES[@]} -eq 0 ]]; then
    echo "NPT selection requires --pressures." >&2
    exit 2
fi
if [[ ! "$TARGET" =~ ^[1-9][0-9]*$ ]]; then
    echo "--target must be a positive integer." >&2
    exit 2
fi

assert_element_path() {
    local label="$1"
    local path="$2"
    local other
    case "$path" in
        "$ELEMENT-potential/"*) ;;
        *)
            echo "$label must be below $ELEMENT-potential/: $path" >&2
            exit 2
            ;;
    esac
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

if [[ ! -d "$ROUND_DIR" || ! -f "$BASE" ]]; then
    echo "Missing round directory or base database." >&2
    exit 1
fi

ALL_FRAMES="$ROUND_DIR/uncertainty_all_frames.csv"
AUDIT_OUTPUT="$ROUND_DIR/geometry_audit.csv"
OUTPUT_ROOT="$ROUND_DIR/absolute-u-projected-cur"
for path in "$ALL_FRAMES" "$AUDIT_OUTPUT" "$OUTPUT_ROOT"; do
    if [[ -e "$path" ]]; then
        echo "Refusing to overwrite existing selection output: $path" >&2
        exit 1
    fi
done

shopt -s nullglob
JNN_PATHS=($JNN_GLOB)
if (( ${#JNN_PATHS[@]} != 10 )); then
    echo "Need exactly ten matching committee JNNs from: $JNN_GLOB" >&2
    exit 1
fi
for jnn in "${JNN_PATHS[@]}"; do
    assert_element_path "JNN path" "$jnn"
    if [[ ! -s "$jnn" || ! -f "$(dirname "$jnn")/log" ]]; then
        echo "Missing nonempty JNN or its trainer log: $jnn" >&2
        exit 1
    fi
done

format_value() {
    python3 - "$1" <<'PY'
import sys
print(f"{float(sys.argv[1]):g}".replace("-", "m").replace(".", "p"))
PY
}

VALUES=()
if [[ "$MODE" == "nvt" ]]; then
    VALUES=("${SCALES[@]}")
else
    VALUES=("${PRESSURES[@]}")
fi
for value in "${VALUES[@]}"; do
    tag="$(format_value "$value")"
    if [[ "$MODE" == "nvt" ]]; then
        source_dir="$ROUND_DIR/md/scale-$tag"
    else
        source_dir="$ROUND_DIR/md/P-${tag}GPa"
    fi
    if [[ ! -s "$source_dir/$TRAJECTORY" ]]; then
        echo "Missing or empty trajectory: $source_dir/$TRAJECTORY" >&2
        exit 1
    fi
done

mkdir -p "$ROUND_DIR/slurm_logs"
LOG_DIR="$ROUND_DIR/slurm_logs"
U_MIN_RECORD="$LOG_DIR/selection-u-min-${SLURM_JOB_ID}.txt"
for path in \
    "$U_MIN_RECORD" \
    "$LOG_DIR/combined-score-command-${SLURM_JOB_ID}.sh" \
    "$LOG_DIR/combined-audit-command-${SLURM_JOB_ID}.sh" \
    "$LOG_DIR/combined-cur-command-${SLURM_JOB_ID}.sh"; do
    if [[ -e "$path" ]]; then
        echo "Refusing to overwrite existing pipeline record: $path" >&2
        exit 1
    fi
done

module load jse
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

U_MIN="$(
    python3 - "$U_MIN_RECORD" "${JNN_PATHS[@]}" <<'PY'
import re
import sys
from pathlib import Path

record_path = Path(sys.argv[1])
values = []
for text_path in map(Path, sys.argv[2:]):
    log_path = text_path.parent / "log"
    text = log_path.read_text(encoding="utf-8", errors="replace").replace("\r", "\n")
    matches = re.findall(
        r"MAE-F:\s*([0-9]+(?:\.[0-9]+)?)\s+meV/A\s*\|\s*"
        r"([0-9]+(?:\.[0-9]+)?)\s+meV/A",
        text,
    )
    if not matches:
        raise RuntimeError(f"Could not find final MAE-F train/test pair in {log_path}")
    test_mae = float(matches[-1][1])
    values.append((text_path, log_path, test_mae))

u_min = sum(value[2] for value in values) / (1000.0 * len(values))
if record_path.exists():
    raise FileExistsError(f"Refusing to overwrite U_min record: {record_path}")
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
echo "Derived U_min=${U_MIN} eV/A from 10 final test MAE-F values; tail_max=${TAIL_MAX}."

write_command() {
    local path="$1"
    shift
    printf '%q ' "$@" > "$path"
    printf '\n' >> "$path"
}

if [[ "$MODE" == "nvt" ]]; then
    source_values="$(IFS=,; echo "${SCALES[*]}")"
    source_option=(--scales "$source_values")
else
    source_values="$(IFS=,; echo "${PRESSURES[*]}")"
    source_option=(--pressures "$source_values")
fi

score_cmd=(
    jse src/stratified_uncertainty_selection.py
    --round-dir "$ROUND_DIR"
    --jnn-glob "$JNN_GLOB"
    --mode "$MODE"
    "${source_option[@]}"
    --trajectory-name "$TRAJECTORY"
    --equilibration-fraction "$EQUILIBRATION_FRACTION"
    --all-frames-csv "$ALL_FRAMES"
    --progress-interval "$PROGRESS_INTERVAL"
    --score-only
)
write_command "$LOG_DIR/combined-score-command-${SLURM_JOB_ID}.sh" "${score_cmd[@]}"
echo "Stage 1/3: full-committee score-only uncertainty."
srun --exclusive -N1 -n1 "${score_cmd[@]}"

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
write_command "$LOG_DIR/combined-audit-command-${SLURM_JOB_ID}.sh" "${audit_cmd[@]}"
echo "Stage 2/3: complete post-U geometry audit."
srun --exclusive -N1 -n1 "${audit_cmd[@]}"

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

required_all = {"trajectory", "frame", "uncertainty", "discarded_equilibration"}
required_audit = {
    "trajectory", "frame", "uncertainty", "min_distance_A",
    "normalized_void", "geometry_gate_status",
}
if not required_all.issubset(all_rows[0] if all_rows else {}):
    raise RuntimeError("All-frame CSV has an unexpected schema")
if not required_audit.issubset(audit_rows[0] if audit_rows else {}):
    raise RuntimeError("Geometry-audit CSV has an unexpected schema")

expected = set()
for row in all_rows:
    if row["discarded_equilibration"].strip().lower() != "false":
        continue
    if float(row["uncertainty"]) >= u_min:
        expected.add((row["trajectory"], int(row["frame"])))

actual = set()
qualified_uncertainties = []
for row in audit_rows:
    key = (row["trajectory"], int(row["frame"]))
    if key in actual:
        raise RuntimeError(f"Duplicate geometry-audit record: {key}")
    actual.add(key)
    if row["geometry_gate_status"] not in {"passed", "rejected"}:
        raise RuntimeError(f"Invalid geometry-gate status: {row['geometry_gate_status']}")
    for field in ("uncertainty", "min_distance_A", "normalized_void"):
        value = float(row[field])
        if not math.isfinite(value) or value <= 0.0:
            raise RuntimeError(f"Invalid {field} for {key}: {row[field]}")
    if row["geometry_gate_status"] == "passed":
        qualified_uncertainties.append(float(row["uncertainty"]))

if actual != expected:
    raise RuntimeError(
        f"Geometry-audit coverage mismatch: expected={len(expected)} actual={len(actual)}"
    )
if len(qualified_uncertainties) < target:
    raise RuntimeError(
        f"Only {len(qualified_uncertainties)} geometry-valid candidates for target {target}"
    )
qualified_uncertainties.sort()
position = (len(qualified_uncertainties) - 1) * 0.99
lower = math.floor(position)
upper = math.ceil(position)
weight = position - lower
tail_p99 = (
    qualified_uncertainties[lower]
    if lower == upper
    else qualified_uncertainties[lower] * (1.0 - weight) + qualified_uncertainties[upper] * weight
)
print(
    "Audit gate passed: "
    f"post_U={len(expected)} geometry_valid={len(qualified_uncertainties)} "
    f"p99_U={tail_p99:.12g}",
    flush=True,
)
PY

cur_cmd=(
    python3 src/absolute_u_projected_cur_selection.py
    --round-dir "$ROUND_DIR"
    --all-frames "$ALL_FRAMES"
    --base "$BASE"
    --output-root "$OUTPUT_ROOT"
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
write_command "$LOG_DIR/combined-cur-command-${SLURM_JOB_ID}.sh" "${cur_cmd[@]}"
echo "Stage 3/3: current-DB-projected CUR."
srun --exclusive -N1 -n1 "${cur_cmd[@]}"

echo "Completed combined MD selection pipeline: $OUTPUT_ROOT"
