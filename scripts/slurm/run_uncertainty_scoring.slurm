#!/bin/bash
#SBATCH -J unary_uncertainty_score
#SBATCH -o slurm-%x-%j.out
#SBATCH -e slurm-%x-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
##SBATCH --partition=your_partition
##SBATCH --account=your_account

# Score every trajectory frame with one element-local NNAP committee.
set -euo pipefail

usage() {
    cat >&2 <<'EOF'
Usage:
  sbatch --output <round_dir>/slurm_logs/score-%j.out \
    scripts/slurm/run_uncertainty_scoring.slurm \
    --round-dir <X>-potential/<round> \
    --jnn-glob '<X>-potential/model_versions/.../train-*/*.jnn' \
    --mode nvt --scales 0.90 0.95 1.00 1.05 1.100

The job writes only uncertainty_all_frames.csv. It refuses to overwrite it
and never creates percentile-bin candidates.
EOF
}

for arg in "$@"; do
    if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
        usage
        exit 0
    fi
done

if [[ -z "${SLURM_JOB_ID:-}" ]]; then
    echo "Submit this scorer with sbatch; do not run full-committee scoring on a login node." >&2
    usage
    exit 2
fi

REPO_DIR="${SLURM_SUBMIT_DIR:-$PWD}"
cd "$REPO_DIR"

ROUND_DIR=""
JNN_GLOB=""
MODE=""
TRAJECTORY="multi_nnap_md.xyz"
ALL_FRAMES_CSV=""
EQUILIBRATION_FRACTION="0.10"
PROGRESS_INTERVAL="500"
SCALES=()
PRESSURES=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --round-dir) ROUND_DIR="$2"; shift 2 ;;
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
        --trajectory-name) TRAJECTORY="$2"; shift 2 ;;
        --all-frames-csv) ALL_FRAMES_CSV="$2"; shift 2 ;;
        --equilibration-fraction) EQUILIBRATION_FRACTION="$2"; shift 2 ;;
        --progress-interval) PROGRESS_INTERVAL="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

if [[ -z "$ROUND_DIR" || -z "$JNN_GLOB" || -z "$MODE" ]]; then
    echo "--round-dir, --jnn-glob, and --mode are required." >&2
    usage
    exit 2
fi
if [[ "$MODE" != "nvt" && "$MODE" != "npt" ]]; then
    echo "--mode must be nvt or npt." >&2
    exit 2
fi
if [[ ! -d "$ROUND_DIR" ]]; then
    echo "Missing round directory: $ROUND_DIR" >&2
    exit 1
fi

if [[ "$MODE" == "nvt" && ${#SCALES[@]} -eq 0 ]]; then
    echo "NVT scoring requires --scales." >&2
    exit 2
fi
if [[ "$MODE" == "npt" && ${#PRESSURES[@]} -eq 0 ]]; then
    echo "NPT scoring requires --pressures." >&2
    exit 2
fi

if [[ -z "$ALL_FRAMES_CSV" ]]; then
    ALL_FRAMES_CSV="$ROUND_DIR/uncertainty_all_frames.csv"
fi
if [[ -e "$ALL_FRAMES_CSV" ]]; then
    echo "Refusing to overwrite existing all-frame CSV: $ALL_FRAMES_CSV" >&2
    exit 1
fi

shopt -s nullglob
JNN_PATHS=($JNN_GLOB)
if (( ${#JNN_PATHS[@]} < 2 )); then
    echo "Need at least two JNN files from: $JNN_GLOB" >&2
    exit 1
fi

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

module load jse
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

if [[ "$MODE" == "nvt" ]]; then
    source_values="$(IFS=,; echo "${SCALES[*]}")"
    source_option=(--scales "$source_values")
else
    source_values="$(IFS=,; echo "${PRESSURES[*]}")"
    source_option=(--pressures "$source_values")
fi

mkdir -p "$ROUND_DIR/slurm_logs"
cmd=(
    jse src/stratified_uncertainty_selection.py
    --round-dir "$ROUND_DIR"
    --jnn-glob "$JNN_GLOB"
    --mode "$MODE"
    "${source_option[@]}"
    --trajectory-name "$TRAJECTORY"
    --equilibration-fraction "$EQUILIBRATION_FRACTION"
    --all-frames-csv "$ALL_FRAMES_CSV"
    --progress-interval "$PROGRESS_INTERVAL"
    --score-only
)
printf '%q ' "${cmd[@]}" > "$ROUND_DIR/slurm_logs/score-command-${SLURM_JOB_ID}.sh"
printf '\n' >> "$ROUND_DIR/slurm_logs/score-command-${SLURM_JOB_ID}.sh"

exec srun --exclusive -N1 -n1 "${cmd[@]}"
