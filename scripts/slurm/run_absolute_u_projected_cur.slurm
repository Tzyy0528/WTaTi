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
    --target <approved-DFT-budget> \
    [--candidate-frame-gap <frames>] [--final-frame-gap <frames>] \
    [--balance-sources] [--require-all-sources] \
    [--tail-threshold <U> | --tail-quantile <0..1>] [--tail-max <count>] \
    [--min-volume-per-atom <A3>] [--max-volume-per-atom <A3>] \
    [--max-force <eV/A>] [--min-distance <A>] \
    [--max-normalized-void <R_void/(V/N)^(1/3)>]

The job refuses to overwrite the CUR output root. Enabled physical/risk gates
write `physical_gate_rejections.csv` alongside candidate and CUR provenance.

For a pre-selection geometry audit only:
  sbatch --output <round_dir>/slurm_logs/geometry-audit-%j.out \
    scripts/slurm/run_absolute_u_projected_cur.slurm \
    --audit-only --round-dir <X>-potential/<round> \
    --u-min <calibrated-U-min> \
    --min-distance <limit> --max-normalized-void <limit> \
    --audit-output <round_dir>/geometry_audit.csv

Audit-only mode refuses to overwrite its CSV and applies only absolute-U and
the periodic distance/normalized-void gates; it writes neither POSCARs nor
CUR output.
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
AUDIT_ONLY="0"
AUDIT_OUTPUT=""
U_MIN=""
TARGET=""
R_C="6.0"
N_MAX="5"
L_MAX="6"
SIMILARITY_THRESHOLD="0.99999"
CANDIDATE_FRAME_GAP="0"
FINAL_FRAME_GAP="0"
BALANCE_SOURCES="0"
REQUIRE_ALL_SOURCES="0"
TAIL_THRESHOLD=""
TAIL_QUANTILE=""
TAIL_MAX=""
MIN_VOLUME_PER_ATOM=""
MAX_VOLUME_PER_ATOM=""
MAX_FORCE=""
MIN_DISTANCE=""
MAX_NORMALIZED_VOID=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --round-dir) ROUND_DIR="$2"; shift 2 ;;
        --all-frames) ALL_FRAMES="$2"; shift 2 ;;
        --base) BASE="$2"; shift 2 ;;
        --output-root) OUTPUT_ROOT="$2"; shift 2 ;;
        --audit-only) AUDIT_ONLY="1"; shift ;;
        --audit-output) AUDIT_OUTPUT="$2"; shift 2 ;;
        --u-min) U_MIN="$2"; shift 2 ;;
        --target) TARGET="$2"; shift 2 ;;
        --r-c) R_C="$2"; shift 2 ;;
        --n-max) N_MAX="$2"; shift 2 ;;
        --l-max) L_MAX="$2"; shift 2 ;;
        --similarity-threshold) SIMILARITY_THRESHOLD="$2"; shift 2 ;;
        --candidate-frame-gap) CANDIDATE_FRAME_GAP="$2"; shift 2 ;;
        --final-frame-gap) FINAL_FRAME_GAP="$2"; shift 2 ;;
        --balance-sources) BALANCE_SOURCES="1"; shift ;;
        --require-all-sources) REQUIRE_ALL_SOURCES="1"; shift ;;
        --tail-threshold) TAIL_THRESHOLD="$2"; shift 2 ;;
        --tail-quantile) TAIL_QUANTILE="$2"; shift 2 ;;
        --tail-max) TAIL_MAX="$2"; shift 2 ;;
        --min-volume-per-atom) MIN_VOLUME_PER_ATOM="$2"; shift 2 ;;
        --max-volume-per-atom) MAX_VOLUME_PER_ATOM="$2"; shift 2 ;;
        --max-force) MAX_FORCE="$2"; shift 2 ;;
        --min-distance) MIN_DISTANCE="$2"; shift 2 ;;
        --max-normalized-void) MAX_NORMALIZED_VOID="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

if [[ "$AUDIT_ONLY" == "1" ]]; then
    if [[ -z "$ROUND_DIR" || -z "$U_MIN" || -z "$AUDIT_OUTPUT" ]]; then
        echo "--audit-only requires --round-dir, --u-min, and --audit-output." >&2
        usage
        exit 2
    fi
elif [[ -z "$ROUND_DIR" || -z "$BASE" || -z "$OUTPUT_ROOT" || -z "$U_MIN" || -z "$TARGET" ]]; then
    echo "--round-dir, --base, --output-root, --u-min, and --target are required." >&2
    usage
    exit 2
fi
if [[ -z "$ALL_FRAMES" ]]; then
    ALL_FRAMES="$ROUND_DIR/uncertainty_all_frames.csv"
fi
if [[ ! -d "$ROUND_DIR" || ! -f "$ALL_FRAMES" ]]; then
    echo "Missing round directory or all-frame CSV." >&2
    exit 1
fi
if [[ "$AUDIT_ONLY" == "1" ]]; then
    if [[ -e "$AUDIT_OUTPUT" ]]; then
        echo "Refusing to overwrite existing geometry audit: $AUDIT_OUTPUT" >&2
        exit 1
    fi
elif [[ ! -f "$BASE" ]]; then
    echo "Missing base database: $BASE" >&2
    exit 1
elif [[ -e "$OUTPUT_ROOT" ]]; then
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
    --u-min "$U_MIN"
    --candidate-frame-gap "$CANDIDATE_FRAME_GAP"
    --final-frame-gap "$FINAL_FRAME_GAP"
)
if [[ "$AUDIT_ONLY" == "1" ]]; then
    cmd+=(--audit-only --audit-output "$AUDIT_OUTPUT")
else
    cmd+=(
        --base "$BASE"
        --output-root "$OUTPUT_ROOT"
        --target "$TARGET"
        --r-c "$R_C"
        --n-max "$N_MAX"
        --l-max "$L_MAX"
        --similarity-threshold "$SIMILARITY_THRESHOLD"
    )
fi
if [[ "$BALANCE_SOURCES" == "1" ]]; then
    cmd+=(--balance-sources)
fi
if [[ "$REQUIRE_ALL_SOURCES" == "1" ]]; then
    cmd+=(--require-all-sources)
fi
if [[ -n "$TAIL_THRESHOLD" ]]; then
    cmd+=(--tail-threshold "$TAIL_THRESHOLD")
fi
if [[ -n "$TAIL_QUANTILE" ]]; then
    cmd+=(--tail-quantile "$TAIL_QUANTILE")
fi
if [[ -n "$TAIL_MAX" ]]; then
    cmd+=(--tail-max "$TAIL_MAX")
fi
if [[ -n "$MIN_VOLUME_PER_ATOM" ]]; then
    cmd+=(--min-volume-per-atom "$MIN_VOLUME_PER_ATOM")
fi
if [[ -n "$MAX_VOLUME_PER_ATOM" ]]; then
    cmd+=(--max-volume-per-atom "$MAX_VOLUME_PER_ATOM")
fi
if [[ -n "$MAX_FORCE" ]]; then
    cmd+=(--max-force "$MAX_FORCE")
fi
if [[ -n "$MIN_DISTANCE" ]]; then
    cmd+=(--min-distance "$MIN_DISTANCE")
fi
if [[ -n "$MAX_NORMALIZED_VOID" ]]; then
    cmd+=(--max-normalized-void "$MAX_NORMALIZED_VOID")
fi
printf '%q ' "${cmd[@]}" > "$ROUND_DIR/slurm_logs/cur-command-${SLURM_JOB_ID}.sh"
printf '\n' >> "$ROUND_DIR/slurm_logs/cur-command-${SLURM_JOB_ID}.sh"

exec srun --exclusive -N1 -n1 "${cmd[@]}"
