#!/bin/bash
#SBATCH -J unary_vasp_batch
#SBATCH -o slurm-%x-%j.out
#SBATCH -e slurm-%x-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=64
## No explicit --time by default; the cluster partition may still impose a limit.
##SBATCH --partition=your_partition
##SBATCH --account=your_account

# Submit from the repository root, for example:
#   sbatch scripts/slurm/run_vasp_batch_dft.slurm \
#     <X>-potential/<round>/absolute-u-projected-cur/<selected-poscar-dir> \
#     <X>-potential/<round>/<X>_selected_labeled.db \
#     <approved-magmom> <approved-kspacing> <approved-encut>
# ENCUT defaults to 1.3 * max(ENMAX) from the selected POTCARs if omitted:
#   sbatch scripts/slurm/run_vasp_batch_dft.slurm <input_dir> <output.db> _ 0.2 [encut]
# To replace an existing output DB explicitly:
#   OVERWRITE=1 FORCE_PREPARE=1 sbatch scripts/slurm/run_vasp_batch_dft.slurm <input_dir> <output.db> [magmom] [kspacing] [encut]
#
# Optional environment overrides:
#   WORK_DIR=...       default: <output_db_dir>/dft/vasp_<output_stem without _labeled>
#   CORES_PER_JOB=8    MPI ranks per VASP task
#   MAX_WORKERS=...    concurrent VASP tasks; default is SLURM_NTASKS / CORES_PER_JOB
#   VASP_COMMAND=...   default: vasp_std
#   ENCUT_FACTOR=1.3   default ENCUT factor multiplied by max POTCAR ENMAX
#   NCORE=2            default VASP NCORE written to future INCAR files
#   PROGRESS_INTERVAL=60
#                     seconds between live progress-bar snapshots; 0 disables periodic updates
#   PREPARE_ONLY=1     prepare/reuse input folders only; do not launch VASP
#   FORCE_PREPARE=1    rewrite existing prepared task inputs
#   KEEP_CHGCAR=1      keep CHGCAR files after each VASP task

set -euo pipefail

usage() {
    echo "Usage: sbatch $0 <input_structure_dir> <output_db> [magmom=_] [kspacing=0.2] [encut=auto]" >&2
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
fi

if [[ $# -lt 2 || $# -gt 5 ]]; then
    usage
    exit 2
fi

REPO_DIR="${SLURM_SUBMIT_DIR:-$PWD}"
cd "$REPO_DIR"

INPUT_DIR_ARG="$1"
OUTPUT_DB_ARG="$2"
MAGMOM="${3:-_}"
KSPACING="${4:-0.2}"
ENCUT="${5:-}"

CORES_PER_JOB="${CORES_PER_JOB:-8}"
VASP_COMMAND="${VASP_COMMAND:-vasp_std}"
ENCUT_FACTOR="${ENCUT_FACTOR:-1.3}"
NCORE="${NCORE:-2}"
PROGRESS_INTERVAL="${PROGRESS_INTERVAL:-60}"

if [[ ! "$CORES_PER_JOB" =~ ^[0-9]+$ || "$CORES_PER_JOB" -lt 1 ]]; then
    echo "CORES_PER_JOB must be a positive integer: $CORES_PER_JOB" >&2
    exit 1
fi
if [[ ! "$NCORE" =~ ^[0-9]+$ || "$NCORE" -lt 1 ]]; then
    echo "NCORE must be a positive integer: $NCORE" >&2
    exit 1
fi

if [[ ! -d "$INPUT_DIR_ARG" ]]; then
    echo "Missing input structure directory: $INPUT_DIR_ARG" >&2
    exit 1
fi

INPUT_DIR="$(realpath "$INPUT_DIR_ARG")"
OUTPUT_PARENT="$(dirname "$OUTPUT_DB_ARG")"
mkdir -p "$OUTPUT_PARENT"
OUTPUT_DB="$(cd "$OUTPUT_PARENT" && pwd)/$(basename "$OUTPUT_DB_ARG")"

if [[ -z "${WORK_DIR:-}" ]]; then
    OUTPUT_STEM="$(basename "$OUTPUT_DB")"
    OUTPUT_STEM="${OUTPUT_STEM%.*}"
    OUTPUT_STEM="${OUTPUT_STEM%_labeled}"
    WORK_DIR="$(dirname "$OUTPUT_DB")/dft/vasp_${OUTPUT_STEM}"
fi
mkdir -p "$(dirname "$WORK_DIR")"
WORK_DIR="$(cd "$(dirname "$WORK_DIR")" && pwd)/$(basename "$WORK_DIR")"

LOG_DIR="$(dirname "$OUTPUT_DB")/slurm_logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/vasp-batch-${SLURM_JOB_ID:-manual}.out"

exec > "$LOG_FILE" 2>&1

if [[ -z "${SLURM_JOB_ID:-}" && "${PREPARE_ONLY:-0}" != "1" && "${DRY_RUN:-0}" != "1" ]]; then
    echo "This script should be submitted with sbatch for actual VASP execution." >&2
    echo "Use PREPARE_ONLY=1 for a safe local preparation test." >&2
    exit 1
fi

if [[ -e "$OUTPUT_DB" && "${OVERWRITE:-0}" != "1" && "${PREPARE_ONLY:-0}" != "1" ]]; then
    echo "Output DB already exists: $OUTPUT_DB" >&2
    echo "Set OVERWRITE=1 before sbatch if you intentionally want to replace it." >&2
    exit 1
fi

ALLOCATED_TASKS="${SLURM_NTASKS:-}"
if [[ -z "${MAX_WORKERS:-}" && -n "$ALLOCATED_TASKS" ]]; then
    MAX_WORKERS="$((ALLOCATED_TASKS / CORES_PER_JOB))"
    if (( MAX_WORKERS < 1 )); then
        echo "SLURM_NTASKS=$ALLOCATED_TASKS is smaller than CORES_PER_JOB=$CORES_PER_JOB." >&2
        exit 1
    fi
fi

if [[ -n "${MAX_WORKERS:-}" ]]; then
    if [[ ! "$MAX_WORKERS" =~ ^[0-9]+$ || "$MAX_WORKERS" -lt 1 ]]; then
        echo "MAX_WORKERS must be a positive integer: $MAX_WORKERS" >&2
        exit 1
    fi
    if [[ -n "$ALLOCATED_TASKS" && $((MAX_WORKERS * CORES_PER_JOB)) -gt "$ALLOCATED_TASKS" ]]; then
        echo "MAX_WORKERS * CORES_PER_JOB exceeds allocated SLURM tasks:" >&2
        echo "  $MAX_WORKERS * $CORES_PER_JOB > $ALLOCATED_TASKS" >&2
        exit 1
    fi
fi

CMD=(python3 -u src/vasp_batch_dft.py label "$INPUT_DIR" "$OUTPUT_DB")
CMD+=(--work-dir "$WORK_DIR")
CMD+=(--magmom "$MAGMOM" --kspacing "$KSPACING")
CMD+=(--encut-factor "$ENCUT_FACTOR")
CMD+=(--set "NCORE=$NCORE")
CMD+=(--cores-per-job "$CORES_PER_JOB" --vasp-command "$VASP_COMMAND")
CMD+=(--progress-interval "$PROGRESS_INTERVAL")

if [[ -n "$ENCUT" ]]; then
    CMD+=(--encut "$ENCUT")
fi
if [[ -n "${MAX_WORKERS:-}" ]]; then
    CMD+=(--max-workers "$MAX_WORKERS")
fi
if [[ "${OVERWRITE:-0}" == "1" ]]; then
    CMD+=(--overwrite)
fi
if [[ "${PREPARE_ONLY:-0}" == "1" ]]; then
    CMD+=(--prepare-only)
fi
if [[ "${FORCE_PREPARE:-0}" == "1" ]]; then
    CMD+=(--force)
fi
if [[ "${KEEP_CHGCAR:-0}" == "1" ]]; then
    CMD+=(--keep-chgcar)
fi

COMMAND_LOG="$LOG_DIR/vasp_batch_command-${SLURM_JOB_ID:-manual}.sh"
printf '%q ' "${CMD[@]}" > "$COMMAND_LOG"
printf '\n' >> "$COMMAND_LOG"

echo "Running VASP batch DFT labeling"
echo "Input directory: $INPUT_DIR"
echo "Output DB: $OUTPUT_DB"
echo "Work directory: $WORK_DIR"
echo "SLURM tasks: ${SLURM_NTASKS:-unset}"
echo "Cores per VASP task: $CORES_PER_JOB"
echo "Max concurrent VASP tasks: ${MAX_WORKERS:-auto}"
echo "VASP command: $VASP_COMMAND"
echo "Progress interval: $PROGRESS_INTERVAL seconds"
echo "MAGMOM: $MAGMOM"
echo "KSPACING: $KSPACING"
echo "ENCUT: ${ENCUT:-auto (${ENCUT_FACTOR} * max POTCAR ENMAX)}"
echo "NCORE: $NCORE"
echo "Command log: $COMMAND_LOG"

if [[ "${DRY_RUN:-0}" == "1" ]]; then
    echo "DRY_RUN=1; command was not executed."
    exit 0
fi

module load jse

"${CMD[@]}"

if [[ "${PREPARE_ONLY:-0}" != "1" ]]; then
    test -s "$OUTPUT_DB"
    echo "Finished VASP batch DFT labeling: $OUTPUT_DB"
fi
