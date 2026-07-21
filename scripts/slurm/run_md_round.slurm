#!/bin/bash
#SBATCH -J unary_md_round
#SBATCH -o slurm-%x-%j.out
#SBATCH -e slurm-%x-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
##SBATCH --partition=your_partition
##SBATCH --account=your_account
##SBATCH --gres=gpu:1

# Submit one NVT/NPT round as multiple one-core MD jobs in one allocation.
# Required explicit inputs:
#   NVT --scale-factors: approved scale list
#   NPT --pressures:     approved pressure list in GPa
#   --rep:               approved supercell repetition
#
# Recommended auto-sizing mode: run this script directly from the repository
# root. It counts --scale-factors or --pressures and submits itself with
# sbatch -n <count>.
#   bash scripts/slurm/run_md_round.slurm --ensemble nvt ... --jnn-paths ...
#
# If you call sbatch directly, pass -n yourself:
#   sbatch -n 6 scripts/slurm/run_md_round.slurm --ensemble nvt ... --jnn-paths ...
#
# NVT example:
#   bash scripts/slurm/run_md_round.slurm \
#     --ensemble nvt \
#     --round-dir <X>-potential/01-nvt-round-1 \
#     --poscar structures/<X>_benchmark/<X>-seed.poscar \
#     --rep <NX> <NY> <NZ> \
#     --temperature <approved-temperature-K> \
#     --steps <approved-steps> \
#     --write-interval <approved-write-interval> \
#     --log-interval <approved-log-interval> \
#     --jnn-paths path/to/0.jnn path/to/1.jnn path/to/2.jnn
#
# NPT example:
#   bash scripts/slurm/run_md_round.slurm \
#     --ensemble npt --round-dir <X>-potential/02-npt-round-1 \
#     --poscar structures/<X>_benchmark/<X>-seed.poscar \
#     --temperature <approved-temperature-K> \
#     --jnn-paths path/to/0.jnn path/to/1.jnn path/to/2.jnn

set -euo pipefail

usage() {
    cat >&2 <<'EOF'
Usage:
  bash scripts/slurm/run_md_round.slurm \
    --ensemble nvt|npt \
    --round-dir <round_dir> \
    --poscar <POSCAR> \
    --rep NX NY NZ \
    --temperature <K> \
    --scale-factors s1 s2 ...  (required for NVT) \
    --pressures p1 p2 ...      (required for NPT) \
    [MD options] \
    --jnn-paths <model1.jnn> <model2.jnn> ...

NVT requires an explicit --scale-factors list. NPT requires an explicit
--pressures list and either --bulk-modulus-gpa or --pfactor. All runs require
an explicit --rep.

Direct execution auto-submits with sbatch -n <number of scales/pressures>.
If calling sbatch directly, provide -n manually.
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

count_round_jobs() {
    local ensemble=""
    local scale_count=0
    local pressure_count=0

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --ensemble)
                ensemble="${2:-}"
                shift 2
                ;;
            --scale-factors|--scales)
                shift
                while [[ $# -gt 0 && "$1" != --* ]]; do
                    scale_count=$((scale_count + 1))
                    shift
                done
                ;;
            --pressures)
                shift
                while [[ $# -gt 0 && "$1" != --* ]]; do
                    pressure_count=$((pressure_count + 1))
                    shift
                done
                ;;
            --jnn-paths)
                shift
                while [[ $# -gt 0 && "$1" != --* ]]; do
                    shift
                done
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ "$ensemble" == "nvt" ]]; then
        echo "$scale_count"
    elif [[ "$ensemble" == "npt" ]]; then
        echo "$pressure_count"
    elif (( scale_count > 0 )); then
        echo "$scale_count"
    else
        echo "$pressure_count"
    fi
}

if [[ -z "${SLURM_JOB_ID:-}" && "${MD_ROUND_NO_SELF_SUBMIT:-0}" != "1" ]]; then
    ntasks="$(count_round_jobs "$@")"
    if (( ntasks < 1 )); then
        echo "Could not infer task count from --scale-factors or --pressures." >&2
        usage
        exit 2
    fi
    script_path="$(realpath "$0")"
    echo "Auto-submitting MD round with $ntasks SLURM tasks:"
    echo "  sbatch --nodes=1 --ntasks=$ntasks $script_path $*"
    exec sbatch --nodes=1 --ntasks="$ntasks" "$script_path" "$@"
fi

REPO_DIR="${SLURM_SUBMIT_DIR:-$PWD}"
cd "$REPO_DIR"

ENSEMBLE=""
ROUND_DIR=""
POSCAR=""
TEMPERATURE=""
SCALES=()
PRESSURES=()
JNN_PATHS=()
TAU_R="0.1"
STEPS="50000"
TIMESTEP="1.0"
WRITE_INTERVAL="10"
LOG_INTERVAL="1"
TRAJECTORY="multi_nnap_md.xyz"
SUMMARY="energy_forces_summary.dat"
FRICTION="0.02"
TTIME="75.0"
PTIME="75.0"
BULK_MODULUS_GPA=""
PFACTOR=""
FRAC_TRACELESS="0.05"
MD_REP=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --ensemble) ENSEMBLE="$2"; shift 2 ;;
        --round-dir) ROUND_DIR="$2"; shift 2 ;;
        --poscar) POSCAR="$2"; shift 2 ;;
        --rep)
            if [[ $# -lt 4 ]]; then
                echo "--rep requires NX NY NZ" >&2
                exit 2
            fi
            MD_REP=("$2" "$3" "$4")
            shift 4
            ;;
        --temperature) TEMPERATURE="$2"; shift 2 ;;
        --scale-factors|--scales)
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
        --jnn-paths)
            shift
            while [[ $# -gt 0 && "$1" != --* ]]; do
                JNN_PATHS+=("$1")
                shift
            done
            ;;
        --tau-r) TAU_R="$2"; shift 2 ;;
        --steps) STEPS="$2"; shift 2 ;;
        --timestep) TIMESTEP="$2"; shift 2 ;;
        --write-interval) WRITE_INTERVAL="$2"; shift 2 ;;
        --log-interval) LOG_INTERVAL="$2"; shift 2 ;;
        --trajectory) TRAJECTORY="$2"; shift 2 ;;
        --summary) SUMMARY="$2"; shift 2 ;;
        --friction) FRICTION="$2"; shift 2 ;;
        --ttime) TTIME="$2"; shift 2 ;;
        --ptime) PTIME="$2"; shift 2 ;;
        --bulk-modulus-gpa) BULK_MODULUS_GPA="$2"; shift 2 ;;
        --pfactor) PFACTOR="$2"; shift 2 ;;
        --frac-traceless) FRAC_TRACELESS="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

if [[ "$ENSEMBLE" != "nvt" && "$ENSEMBLE" != "npt" ]]; then
    echo "--ensemble must be nvt or npt" >&2
    exit 2
fi
if [[ -z "$ROUND_DIR" || -z "$POSCAR" || -z "$TEMPERATURE" ]]; then
    echo "--round-dir, --poscar, and --temperature are required" >&2
    exit 2
fi
if [[ ! -f "$POSCAR" ]]; then
    echo "Missing POSCAR: $POSCAR" >&2
    exit 1
fi
if [[ ${#MD_REP[@]} -ne 3 ]]; then
    echo "--rep NX NY NZ is required" >&2
    exit 2
fi
for value in "${MD_REP[@]}"; do
    if [[ ! "$value" =~ ^[1-9][0-9]*$ ]]; then
        echo "--rep values must be positive integers" >&2
        exit 2
    fi
done
if [[ ${#JNN_PATHS[@]} -eq 0 ]]; then
    echo "--jnn-paths is required" >&2
    exit 2
fi
for jnn in "${JNN_PATHS[@]}"; do
    if [[ ! -f "$jnn" ]]; then
        echo "Missing .jnn file: $jnn" >&2
        exit 1
    fi
done

VALUES=()
if [[ "$ENSEMBLE" == "nvt" ]]; then
    if [[ ${#SCALES[@]} -eq 0 ]]; then
        echo "NVT requires --scale-factors" >&2
        exit 2
    fi
    VALUES=("${SCALES[@]}")
else
    if [[ ${#PRESSURES[@]} -eq 0 ]]; then
        echo "NPT requires --pressures" >&2
        exit 2
    fi
    if [[ -z "$BULK_MODULUS_GPA" && -z "$PFACTOR" ]]; then
        echo "NPT requires --bulk-modulus-gpa or --pfactor" >&2
        exit 2
    fi
    VALUES=("${PRESSURES[@]}")
fi

AVAILABLE_TASKS="${SLURM_NTASKS:-${#VALUES[@]}}"
if (( ${#VALUES[@]} > AVAILABLE_TASKS )); then
    echo "This round has ${#VALUES[@]} MD jobs but SLURM allocated only $AVAILABLE_TASKS tasks." >&2
    echo "Run directly for auto-sizing: bash scripts/slurm/run_md_round.slurm ..." >&2
    echo "Or submit manually with: sbatch -n ${#VALUES[@]} scripts/slurm/run_md_round.slurm ..." >&2
    exit 1
fi

format_value() {
    python3 - "$1" <<'PY'
import sys
print(f"{float(sys.argv[1]):g}".replace('-', 'm').replace('.', 'p'))
PY
}

mkdir -p "$ROUND_DIR/slurm_logs"
ROUND_LOG_DIR="$(cd "$ROUND_DIR/slurm_logs" && pwd)"

module load jse

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

PIDS=()
LABELS=()
for value in "${VALUES[@]}"; do
    tag="$(format_value "$value")"
    if [[ "$ENSEMBLE" == "nvt" ]]; then
        label="scale-$tag"
        work_dir="$ROUND_DIR/md/$label"
        extra=(--scale-factor "$value" --friction "$FRICTION")
    else
        label="P-${tag}GPa"
        work_dir="$ROUND_DIR/md/$label"
        extra=(
            --pressure "$value"
            --ttime "$TTIME"
            --ptime "$PTIME"
            --frac-traceless "$FRAC_TRACELESS"
        )
        if [[ -n "$BULK_MODULUS_GPA" ]]; then
            extra+=(--bulk-modulus-gpa "$BULK_MODULUS_GPA")
        fi
        if [[ -n "$PFACTOR" ]]; then
            extra+=(--pfactor "$PFACTOR")
        fi
    fi

    mkdir -p "$work_dir"
    cmd=(
        jse src/md_worker.py
        --ensemble "$ENSEMBLE"
        --work-dir "$work_dir"
        --poscar "$POSCAR"
        --rep "${MD_REP[@]}"
        --temperature "$TEMPERATURE"
        --tau-r "$TAU_R"
        --steps "$STEPS"
        --timestep "$TIMESTEP"
        --write-interval "$WRITE_INTERVAL"
        --log-interval "$LOG_INTERVAL"
        --trajectory "$TRAJECTORY"
        --summary "$SUMMARY"
        "${extra[@]}"
        --jnn-paths "${JNN_PATHS[@]}"
    )

    printf '%q ' "${cmd[@]}" > "$work_dir/command.sh"
    printf '\n' >> "$work_dir/command.sh"

    echo "Launching $ENSEMBLE MD: $label -> $work_dir"
    srun --exclusive -N1 -n1 "${cmd[@]}" > "$work_dir/log" 2>&1 &
    PIDS+=("$!")
    LABELS+=("$label")
done

failed=0
for i in "${!PIDS[@]}"; do
    if wait "${PIDS[$i]}"; then
        echo "Finished ${LABELS[$i]}"
    else
        echo "FAILED ${LABELS[$i]}" >&2
        failed=1
    fi
done

if (( failed != 0 )); then
    echo "One or more MD jobs failed. Check $ROUND_DIR/md/*/log" >&2
    exit 1
fi

echo "Finished all $ENSEMBLE MD jobs for round: $ROUND_DIR"
