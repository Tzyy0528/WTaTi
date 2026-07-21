#!/bin/bash
#SBATCH -J unary_md
#SBATCH -o slurm-%x-%j.out
#SBATCH -e slurm-%x-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=24:00:00
##SBATCH --partition=your_partition
##SBATCH --account=your_account
##SBATCH --gres=gpu:1

# Submit from the repository root and pass the normal src/md_worker.py options.
# Example NVT job:
#   sbatch scripts/slurm/run_md_worker.slurm \
#     --ensemble nvt \
#     --work-dir <X>-potential/md/M0_nvt_scale_1 \
#     --poscar structures/<X>_benchmark/<X>-seed.poscar \
#     --rep <NX> <NY> <NZ> \
#     --temperature <approved-temperature-K> \
#     --scale-factor 1.0 \
#     --tau-r 0.1 \
#     --steps 50000 \
#     --write-interval 10 \
#     --log-interval 1 \
#     --jnn-paths path/to/train-0/0.jnn path/to/train-1/1.jnn path/to/train-2/2.jnn
# Example NPT job: add --ensemble npt --pressure <GPa> and NPT parameters as needed.

set -euo pipefail

if [[ $# -eq 0 ]]; then
    echo "Usage: sbatch $0 <all src/md_worker.py arguments>" >&2
    echo "Run: python3 src/md_worker.py --help" >&2
    exit 2
fi

REPO_DIR="${SLURM_SUBMIT_DIR:-$PWD}"
cd "$REPO_DIR"

ARGS=("$@")
WORK_DIR=""
for ((i = 0; i < ${#ARGS[@]}; i++)); do
    case "${ARGS[$i]}" in
        --work-dir)
            if (( i + 1 < ${#ARGS[@]} )); then
                WORK_DIR="${ARGS[$((i + 1))]}"
            fi
            ;;
        --work-dir=*)
            WORK_DIR="${ARGS[$i]#--work-dir=}"
            ;;
    esac
done

if [[ -z "$WORK_DIR" ]]; then
    echo "Missing --work-dir in MD arguments" >&2
    exit 1
fi

mkdir -p "$WORK_DIR/slurm_logs"
LOG_DIR="$(cd "$WORK_DIR/slurm_logs" && pwd)"

exec > >(tee -a "$LOG_DIR/md-${SLURM_JOB_ID:-manual}.out") 2>&1

module load jse

COMMAND_FILE="$LOG_DIR/md_command-${SLURM_JOB_ID:-manual}.sh"
printf 'jse src/md_worker.py ' > "$COMMAND_FILE"
printf '%q ' "${ARGS[@]}" >> "$COMMAND_FILE"
printf '\n' >> "$COMMAND_FILE"

echo "Running MD worker"
echo "Work dir: $WORK_DIR"
echo "Command log: $COMMAND_FILE"

jse src/md_worker.py "${ARGS[@]}"

echo "Finished MD worker: $WORK_DIR"
