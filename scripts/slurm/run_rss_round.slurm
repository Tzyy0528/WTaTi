#!/bin/bash
#SBATCH -J unary_rss_round
#SBATCH -o slurm-%x-%j.out
#SBATCH -e slurm-%x-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
##SBATCH --partition=your_partition
##SBATCH --account=your_account

# Generate one protected unary RSS/Mini candidate pool. This template performs
# generation only; it does not score, select, label, train, or evaluate.
# JSE must run directly inside the sbatch allocation, not under srun.
set -euo pipefail

usage() {
    cat >&2 <<'EOF'
Usage:
  sbatch --output <round>/slurm_logs/rss-%j.out \
    --error <round>/slurm_logs/rss-%j.err \
    scripts/slurm/run_rss_round.slurm \
    --element <W|Ta|Ti> \
    --jnn <X>-potential/.../train-N/N.jnn \
    --out-dir <X>-potential/<round>/rss \
    --atomic-volume <A3-per-atom> \
    --nstructs <positive-int> \
    --natoms-list 9,10,12,15,18,20,22,25 \
    --mini-press-list 0,200000,400000 \
    --mini-keyword tri \
    --mini-loop 10 \
    --mini-etol 1e-4 \
    --mini-ftol 1e-8

The output directory must not exist. Raw and minimized work are retained.
Do not add --overwrite. Submit through SLURM; do not run RSS on a login node.
EOF
}

for arg in "$@"; do
    if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
        usage
        exit 0
    fi
done

if [[ -z "${SLURM_JOB_ID:-}" ]]; then
    echo "Submit RSS generation with sbatch; do not run it on a login node." >&2
    usage
    exit 2
fi

ELEMENT=""
JNN=""
OUT_DIR=""
ATOMIC_VOLUME=""
NSTRUCTS=""
NATOMS_LIST=""
MINI_PRESS_LIST=""
MINI_KEYWORD=""
MINI_LOOP=""
MINI_ETOL=""
MINI_FTOL=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --element) ELEMENT="${2:-}"; shift 2 ;;
        --jnn) JNN="${2:-}"; shift 2 ;;
        --out-dir) OUT_DIR="${2:-}"; shift 2 ;;
        --atomic-volume) ATOMIC_VOLUME="${2:-}"; shift 2 ;;
        --nstructs) NSTRUCTS="${2:-}"; shift 2 ;;
        --natoms-list) NATOMS_LIST="${2:-}"; shift 2 ;;
        --mini-press-list) MINI_PRESS_LIST="${2:-}"; shift 2 ;;
        --mini-keyword) MINI_KEYWORD="${2:-}"; shift 2 ;;
        --mini-loop) MINI_LOOP="${2:-}"; shift 2 ;;
        --mini-etol) MINI_ETOL="${2:-}"; shift 2 ;;
        --mini-ftol) MINI_FTOL="${2:-}"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

for name in ELEMENT JNN OUT_DIR ATOMIC_VOLUME NSTRUCTS NATOMS_LIST \
    MINI_PRESS_LIST MINI_KEYWORD MINI_LOOP MINI_ETOL MINI_FTOL; do
    if [[ -z "${!name}" ]]; then
        echo "Missing required option: ${name}" >&2
        usage
        exit 2
    fi
done

REPO_DIR="${SLURM_SUBMIT_DIR:-$PWD}"
cd "$REPO_DIR"

if [[ ! -f "$JNN" ]]; then
    echo "Missing RSS/Mini JNN: $JNN" >&2
    exit 1
fi
if [[ -e "$OUT_DIR" ]]; then
    echo "Refusing existing RSS output directory: $OUT_DIR" >&2
    exit 1
fi

ROUND_DIR="$(dirname "$OUT_DIR")"
LOG_DIR="$ROUND_DIR/slurm_logs"
mkdir -p "$LOG_DIR"

module load jse
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
unset OVERWRITE

cmd=(
    python3 src/rss_sampling_embedded.py
    --elems "$ELEMENT"
    --jnn "$JNN"
    --out-dir "$OUT_DIR"
    --atomic-volume "$ATOMIC_VOLUME"
    --nstructs "$NSTRUCTS"
    --natoms-list "$NATOMS_LIST"
    --jobs 1
    --mini-press-list "$MINI_PRESS_LIST"
    --mini-keyword "$MINI_KEYWORD"
    --mini-loop "$MINI_LOOP"
    --mini-etol "$MINI_ETOL"
    --mini-ftol "$MINI_FTOL"
    --keep-raw
    --keep-minimized-work
)

command_file="$LOG_DIR/rss-command-${SLURM_JOB_ID}.sh"
printf '%q ' "${cmd[@]}" > "$command_file"
printf '\n' >> "$command_file"

echo "Generating RSS/Mini pool for $ELEMENT"
echo "JNN: $JNN"
echo "Output: $OUT_DIR"
echo "Command record: $command_file"

exec "${cmd[@]}"
