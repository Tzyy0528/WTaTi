#!/bin/bash
#SBATCH -J unary_projected_cur
#SBATCH -o slurm-%x-%j.out
#SBATCH -e slurm-%x-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
##SBATCH --partition=your_partition
##SBATCH --account=your_account

# Apply an approved absolute-U cutoff and current-DB-projected CUR.
set -euo pipefail

usage() {
    cat >&2 <<'EOF'
Usage:
  sbatch --output <round_dir>/slurm_logs/cur-%j.out \
    scripts/slurm/run_absolute_u_projected_cur.slurm \
    --round-dir <X>-potential/<round> \
    --base <X>-potential/current.db \
    --output-root <round_dir>/absolute-u-projected-cur \
    --u-min <calibrated-U-min> \
    --target <approved-DFT-budget>

The job refuses to overwrite the CUR output root. Source balancing, frame
gaps, and tail caps are intentionally absent unless explicitly requested.
EOF
}

for arg in "$@"; do
    if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
        usage
        exit 0
    fi
done

if [[ -z "${SLURM_JOB_ID:-}" ]]; then
    echo "Submit CUR selection with sbatch; do not run it on a login node." >&2
    usage
    exit 2
fi

REPO_DIR="${SLURM_SUBMIT_DIR:-$PWD}"
cd "$REPO_DIR"

ROUND_DIR=""
ALL_FRAMES=""
BASE=""
OUTPUT_ROOT=""
U_MIN=""
TARGET=""
R_C="6.0"
N_MAX="5"
L_MAX="6"
SIMILARITY_THRESHOLD="0.99999"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --round-dir) ROUND_DIR="$2"; shift 2 ;;
        --all-frames) ALL_FRAMES="$2"; shift 2 ;;
        --base) BASE="$2"; shift 2 ;;
        --output-root) OUTPUT_ROOT="$2"; shift 2 ;;
        --u-min) U_MIN="$2"; shift 2 ;;
        --target) TARGET="$2"; shift 2 ;;
        --r-c) R_C="$2"; shift 2 ;;
        --n-max) N_MAX="$2"; shift 2 ;;
        --l-max) L_MAX="$2"; shift 2 ;;
        --similarity-threshold) SIMILARITY_THRESHOLD="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

if [[ -z "$ROUND_DIR" || -z "$BASE" || -z "$OUTPUT_ROOT" || -z "$U_MIN" || -z "$TARGET" ]]; then
    echo "--round-dir, --base, --output-root, --u-min, and --target are required." >&2
    usage
    exit 2
fi
if [[ -z "$ALL_FRAMES" ]]; then
    ALL_FRAMES="$ROUND_DIR/uncertainty_all_frames.csv"
fi
if [[ ! -d "$ROUND_DIR" || ! -f "$ALL_FRAMES" || ! -f "$BASE" ]]; then
    echo "Missing round directory, all-frame CSV, or base database." >&2
    exit 1
fi
if [[ -e "$OUTPUT_ROOT" ]]; then
    echo "Refusing to overwrite existing CUR output: $OUTPUT_ROOT" >&2
    exit 1
fi

module load jse
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

mkdir -p "$ROUND_DIR/slurm_logs"
cmd=(
    python3 src/absolute_u_projected_cur_selection.py
    --round-dir "$ROUND_DIR"
    --all-frames "$ALL_FRAMES"
    --base "$BASE"
    --output-root "$OUTPUT_ROOT"
    --u-min "$U_MIN"
    --candidate-frame-gap 0
    --target "$TARGET"
    --final-frame-gap 0
    --r-c "$R_C"
    --n-max "$N_MAX"
    --l-max "$L_MAX"
    --similarity-threshold "$SIMILARITY_THRESHOLD"
)
printf '%q ' "${cmd[@]}" > "$ROUND_DIR/slurm_logs/cur-command-${SLURM_JOB_ID}.sh"
printf '\n' >> "$ROUND_DIR/slurm_logs/cur-command-${SLURM_JOB_ID}.sh"

exec srun --exclusive -N1 -n1 "${cmd[@]}"
