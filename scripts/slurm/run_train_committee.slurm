#!/bin/bash
#SBATCH -J unary_train
#SBATCH -o slurm-%x-%j.out
#SBATCH -e slurm-%x-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=5
#SBATCH --cpus-per-task=8
#SBATCH --time=48:00:00
##SBATCH --partition=your_partition
##SBATCH --account=your_account

# Submit from the repository root, for example:
#   sbatch scripts/slurm/run_train_committee.slurm \
#     <X>-potential/current.db \
#     <X>-potential/model_versions/M0_from_D0/train-committee \
#     <committee-size> <train-workers> <epochs>
# Arguments:
#   <input_db> <train_dir> [committee_size=10] [train_workers=5] [epochs=5000]
#
# Default resource logic:
#   - train 10 committee potentials total;
#   - train 5 potentials concurrently;
#   - each potential uses 8 cores via Trainer.groovy:
#       TrainJse.Conf.THREAD_NUMBER = 8
#   - total allocation: 5 concurrent trainings x 8 cores = 40 cores.
#
# To replace an existing non-empty train_dir explicitly:
#   OVERWRITE=1 sbatch scripts/slurm/run_train_committee.slurm <input_db> <train_dir> [committee_size] [train_workers] [epochs]

set -euo pipefail

usage() {
    echo "Usage: sbatch $0 <input_db> <train_dir> [committee_size=10] [train_workers=5] [epochs=5000]" >&2
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

INPUT_DB_ARG="$1"
TRAIN_DIR_ARG="$2"
COMMITTEE_SIZE="${3:-10}"
TRAIN_WORKERS="${4:-5}"
EPOCHS="${5:-5000}"

if [[ ! -f "$INPUT_DB_ARG" ]]; then
    echo "Missing input DB: $INPUT_DB_ARG" >&2
    exit 1
fi
if (( COMMITTEE_SIZE < 2 )); then
    echo "committee_size must be at least 2 for db_select_and_train: $COMMITTEE_SIZE" >&2
    exit 1
fi
if (( TRAIN_WORKERS < 1 )); then
    echo "train_workers must be at least 1: $TRAIN_WORKERS" >&2
    exit 1
fi
if (( EPOCHS < 1 )); then
    echo "epochs must be positive: $EPOCHS" >&2
    exit 1
fi
ALLOCATED_TASKS="${SLURM_NTASKS:-5}"
CORES_PER_WORKER="${SLURM_CPUS_PER_TASK:-8}"
if (( TRAIN_WORKERS > ALLOCATED_TASKS )); then
    echo "train_workers=$TRAIN_WORKERS but only $ALLOCATED_TASKS SLURM tasks are allocated." >&2
    echo "Submit with: sbatch -n $TRAIN_WORKERS scripts/slurm/run_train_committee.slurm ..." >&2
    exit 1
fi
if (( CORES_PER_WORKER != 8 )); then
    echo "Warning: SLURM_CPUS_PER_TASK=$CORES_PER_WORKER, but Trainer.groovy uses 8 threads per potential." >&2
fi

INPUT_DB="$(realpath "$INPUT_DB_ARG")"
TRAIN_PARENT="$(dirname "$TRAIN_DIR_ARG")"
mkdir -p "$TRAIN_PARENT"
TRAIN_DIR="$(cd "$TRAIN_PARENT" && pwd)/$(basename "$TRAIN_DIR_ARG")"

if [[ -d "$TRAIN_DIR" && -n "$(ls -A "$TRAIN_DIR" 2>/dev/null)" ]]; then
    if [[ "${OVERWRITE:-0}" == "1" ]]; then
        rm -rf "$TRAIN_DIR"
    else
        echo "Training directory already exists and is non-empty: $TRAIN_DIR" >&2
        echo "Set OVERWRITE=1 before sbatch if you intentionally want to replace it." >&2
        exit 1
    fi
fi
mkdir -p "$TRAIN_DIR/slurm_logs"
LOG_DIR="$TRAIN_DIR/slurm_logs"

exec > >(tee -a "$LOG_DIR/train-${SLURM_JOB_ID:-manual}.out") 2>&1

module load jse

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

COMMAND_FILE="$LOG_DIR/train_command-${SLURM_JOB_ID:-manual}.sh"
cat > "$COMMAND_FILE" <<EOF
PYTHONPATH=src python3 - <<'PY'
from dbselectandtrain import db_select_and_train
db_select_and_train('$INPUT_DB', '$TRAIN_DIR', number=$COMMITTEE_SIZE, max_parallel=$TRAIN_WORKERS, epochs=$EPOCHS)
PY
EOF

echo "Running committee training"
echo "Input DB: $INPUT_DB"
echo "Train dir: $TRAIN_DIR"
echo "Committee size: $COMMITTEE_SIZE"
echo "Train workers: $TRAIN_WORKERS"
echo "Epochs: $EPOCHS"
echo "Cores per training worker: ${SLURM_CPUS_PER_TASK:-8}"
echo "Allocated SLURM tasks: ${SLURM_NTASKS:-5}"
echo "Command log: $COMMAND_FILE"

PYTHONPATH="$REPO_DIR/src:${PYTHONPATH:-}" python3 - "$INPUT_DB" "$TRAIN_DIR" "$COMMITTEE_SIZE" "$TRAIN_WORKERS" "$EPOCHS" <<'PY'
import sys
from dbselectandtrain import db_select_and_train

input_db = sys.argv[1]
train_dir = sys.argv[2]
committee_size = int(sys.argv[3])
train_workers = int(sys.argv[4])
epochs = int(sys.argv[5])

db_select_and_train(
    input_db,
    train_dir,
    number=committee_size,
    max_parallel=train_workers,
    epochs=epochs,
)
PY

echo "Finished committee training: $TRAIN_DIR"
