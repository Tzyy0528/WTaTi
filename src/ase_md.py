import argparse
import filecmp
import logging
import shutil
import sys
from dataclasses import dataclass
from math import isfinite
from pathlib import Path

from ase.io import read, write

from CUR import cur_select_structures, list_structure_files
from dbselectandtrain import db_select_and_train
from dft_calculation import (
    DEFAULT_DFT_ENCUT,
    DEFAULT_DFT_ENCUT_FACTOR,
    run_dft_and_update_database,
    run_seed_dft_calculation,
)
from initial_perturbation import generate_seed_structures
from md_worker import build_md_jobs, run_md_jobs
from temperature_table import get_temperature_window, make_temperatures
from uncertainty_selection import select_structures
from workflow_utils import (
    normalize_symbols,
    system_name,
)


LOGGER = logging.getLogger("ase_md")


@dataclass
class WorkflowContext:
    """保存工作流各步骤共享的路径和状态。"""
    symbols: tuple[str, ...]
    project_dir: Path
    current_db: Path
    poscar: Path
    worker_script: Path
    schedule: list[tuple[str, int, float]]


def configure_workflow_logging(project_dir):
    """配置终端和项目日志文件输出。"""
    LOGGER.setLevel(logging.INFO)
    LOGGER.propagate = False
    for handler in list(LOGGER.handlers):
        LOGGER.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    log_path = Path(project_dir) / "workflow.log"
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    stream_handler = logging.StreamHandler(sys.stdout)
    for handler in (file_handler, stream_handler):
        handler.setFormatter(formatter)
        LOGGER.addHandler(handler)


def symbols_from_structure(structure_path):
    """从初始结构文件读取元素种类。"""
    structure_path = Path(structure_path).resolve()
    if not structure_path.exists():
        raise FileNotFoundError(
            f"Initial structure file not found: {structure_path}"
        )
    atoms = read(str(structure_path))
    symbols = normalize_symbols(atoms.get_chemical_symbols())
    if not symbols:
        raise ValueError(f"No chemical symbols found in {structure_path}")
    return symbols


def structures_match(left_path, right_path, tolerance=1e-8):
    """判断两个结构文件是否表示同一初始结构。"""
    try:
        from numpy import allclose, array_equal
        left = read(str(left_path))
        right = read(str(right_path))
    except Exception:
        return False

    if left.get_chemical_symbols() != right.get_chemical_symbols():
        return False
    return (
        allclose(left.get_positions(), right.get_positions(), atol=tolerance)
        and allclose(left.get_cell().array, right.get_cell().array,
                     atol=tolerance)
        and array_equal(left.get_pbc(), right.get_pbc())
    )


def copy_initial_structure(src, dst, overwrite=False):
    """将初始结构写成项目 POSCAR；避免静默复用旧结构。"""
    src = Path(src).resolve()
    dst = Path(dst).resolve()
    if src == dst:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        if filecmp.cmp(src, dst, shallow=False) or structures_match(src, dst):
            return
        if not overwrite:
            raise FileExistsError(
                f"{dst} already exists and differs from {src}. "
                "Use --seed-overwrite or choose a new --work-dir."
            )
    atoms = read(str(src))
    write(str(dst), atoms, format="vasp")


def remove_generated_database(path, overwrite):
    """按需删除自动生成的数据库。"""
    if path.exists():
        if not overwrite:
            raise FileExistsError(
                f"{path} already exists. This workflow no longer accepts an "
                "initial database; use --seed-overwrite or choose a new "
                "--work-dir to regenerate it from the structure file."
            )
        path.unlink()


def prepare_project(args, symbols):
    """从初始结构创建项目输入、seed.db 和 current.db。"""
    name = system_name(symbols)
    input_structure = Path(args.poscar).resolve()
    if not input_structure.exists():
        raise FileNotFoundError(
            f"Initial structure file not found: {input_structure}"
        )

    project_dir = Path(args.work_dir or f"{name}-potential").resolve()
    input_dir = project_dir / "00-input"
    input_dir.mkdir(parents=True, exist_ok=True)
    configure_workflow_logging(project_dir)

    poscar = input_dir / "POSCAR"
    copy_initial_structure(input_structure, poscar,
                           overwrite=args.seed_overwrite)

    seed_db = input_dir / "seed.db"
    current_db = project_dir / "current.db"
    if not args.init_only:
        remove_generated_database(seed_db, args.seed_overwrite)
        remove_generated_database(current_db, args.seed_overwrite)
        LOGGER.info("Generating seed.db from the initial structure file.")
        seed_root, nninit_dir = generate_seed_structures(args, poscar, input_dir)
        seed_db = run_seed_dft_calculation(args, seed_root, nninit_dir, seed_db)
        shutil.copy2(seed_db, current_db)

    readme = project_dir / "README.txt"
    if not readme.exists():
        tm, tb = get_temperature_window(symbols)
        init_note = (
            "Initialization only: seed.db and current.db were not generated.\n"
            if args.init_only
            else "Initial database: 00-input/seed.db -> current.db.\n"
        )
        readme.write_text(
            f"System: {name}\n"
            f"Initial structure: {poscar}\n"
            f"Temperature window: {tm:.1f} K - {tb:.1f} K\n"
            f"{init_note}"
            "Workflow: structure -> nninit/nncalc seed -> train committee -> "
            "biased MD -> uncertainty selection -> CUR diversity selection "
            "-> nncalc DFT -> update current.db\n",
            encoding="utf-8",
        )

    return project_dir, current_db, poscar


def make_round_schedule(args, symbols):
    """按顺序生成 NVT 和 NPT 温度轮次。"""
    schedule = []
    nvt_temps = make_temperatures(symbols, args.nvt_rounds,
                                  margin=args.temperature_margin)
    npt_temps = make_temperatures(symbols, args.npt_rounds,
                                  margin=args.temperature_margin)

    for i, temperature in enumerate(nvt_temps, start=1):
        schedule.append(("nvt", i, temperature))
    for i, temperature in enumerate(npt_temps, start=1):
        schedule.append(("npt", i, temperature))

    if not schedule:
        raise ValueError("At least one NVT or NPT round is required")
    return schedule


def initialize_workflow_step(args):
    """根据命令行参数初始化工作流上下文。"""
    symbols = symbols_from_structure(args.poscar)
    project_dir, current_db, poscar = prepare_project(args, symbols)
    worker_script = Path(__file__).with_name("md_worker.py").resolve()
    return WorkflowContext(
        symbols=symbols,
        project_dir=project_dir,
        current_db=current_db,
        poscar=poscar,
        worker_script=worker_script,
        schedule=[],
    )


def stop_after_initialization_step(args):
    """处理仅初始化模式，并返回是否停止。"""
    if args.init_only:
        LOGGER.info("Initialized project directory only.")
        return True
    return False


def prepare_round_schedule_step(context, args):
    """生成轮次计划并写入工作流上下文。"""
    context.schedule = make_round_schedule(args, context.symbols)


def make_round_directory_step(project_dir, round_index, ensemble, stage_round):
    """创建单个主动学习轮次目录。"""
    round_dir = project_dir / f"{round_index:02d}-{ensemble}-round-{stage_round}"
    round_dir.mkdir(parents=True, exist_ok=True)
    return round_dir


def report_round_step(round_index, ensemble, stage_round, temperature):
    """打印当前轮次信息。"""
    LOGGER.info("=" * 72)
    LOGGER.info(
        "Round %d: %s round %d, T = %.1f K",
        round_index, ensemble.upper(), stage_round, temperature
    )
    LOGGER.info("=" * 72)


def train_committee_step(current_db, round_dir, args):
    """使用当前数据库训练 committee 势模型。"""
    train_dir = round_dir / "train-committee"
    train_dir.mkdir(parents=True, exist_ok=True)
    db_select_and_train(str(current_db), str(train_dir),
                        number=args.committee_size,
                        max_parallel=args.train_workers,
                        epochs=args.train_epochs)

    jnn_paths = [
        (train_dir / f"train-{i}" / f"{i}.jnn").resolve()
        for i in range(args.committee_size)
    ]
    missing = [str(path) for path in jnn_paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing trained jnn files: " + ", ".join(missing))
    return jnn_paths


def run_md_sampling_step(round_dir, ensemble, temperature, args,
                         worker_script, poscar, jnn_paths):
    """构建并执行当前轮次的所有 MD 任务。"""
    jobs = build_md_jobs(round_dir, ensemble, temperature, args)
    run_md_jobs(jobs, args, worker_script, poscar, jnn_paths)
    return jobs


def select_uncertain_structures_step(round_dir, jobs, jnn_paths, args):
    """对 MD 轨迹执行不确定度筛选。"""
    return select_structures(round_dir, jobs, jnn_paths, args)


def select_diverse_structures_step(current_db, round_dir, committee_selected,
                                   args):
    """在 DFT 标注前执行可选 CUR 多样性筛选。"""
    selected_dir = round_dir / "selected-poscar"
    if not committee_selected:
        return selected_dir, committee_selected
    if args.no_cur or args.cur_n_select <= 0:
        return selected_dir, committee_selected

    cur_dir = round_dir / "cur-selected-poscar"
    n_select = min(args.cur_n_select, len(committee_selected))
    base_path = None if args.cur_no_base_projection else current_db

    cur_select_structures(
        selected_dir,
        cur_dir,
        n_select,
        db_based_path=base_path,
        r_c=args.cur_r_c,
        n_max=args.cur_n_max,
        l_max=args.cur_l_max,
        similarity_threshold=(
            None if args.cur_no_sim_threshold else args.cur_sim_threshold
        ),
    )
    cur_selected = list_structure_files(cur_dir)
    if not cur_selected:
        raise FileNotFoundError(f"CUR did not write selected structures in {cur_dir}")
    LOGGER.info("CUR kept %d structures in %s", len(cur_selected), cur_dir)
    return cur_dir, cur_selected


def label_structures_step(current_db, round_dir, selected_dir,
                          selected_structures, args):
    """对筛选出的结构执行 DFT 标注。"""
    return run_dft_and_update_database(
        current_db, round_dir, selected_dir, selected_structures, args
    )


def update_current_database_step(project_dir, updated_db):
    """将本轮 updated.db 复制为项目 current.db。"""
    current_db = project_dir / "current.db"
    shutil.copy2(updated_db, current_db)
    return current_db


def run_active_learning_round_step(context, round_index, ensemble,
                                   stage_round, temperature, args):
    """执行一个完整主动学习轮次。"""
    round_dir = make_round_directory_step(
        context.project_dir, round_index, ensemble, stage_round
    )
    report_round_step(round_index, ensemble, stage_round, temperature)

    jnn_paths = train_committee_step(context.current_db, round_dir, args)
    jobs = run_md_sampling_step(
        round_dir, ensemble, temperature, args,
        context.worker_script, context.poscar, jnn_paths
    )
    committee_selected = select_uncertain_structures_step(
        round_dir, jobs, jnn_paths, args
    )
    diverse_selected_dir, diverse_selected = select_diverse_structures_step(
        context.current_db, round_dir, committee_selected, args
    )
    updated_db = label_structures_step(
        context.current_db, round_dir, diverse_selected_dir,
        diverse_selected, args
    )
    return update_current_database_step(context.project_dir, updated_db)


def run_round_schedule_step(context, args):
    """依次执行所有计划轮次。"""
    for round_index, (ensemble, stage_round, temperature) in enumerate(context.schedule, start=1):
        context.current_db = run_active_learning_round_step(context, round_index, ensemble, stage_round, temperature, args)


def run_workflow(args):
    """运行完整主动学习工作流。"""
    context = initialize_workflow_step(args)
    LOGGER.info("Project directory: %s", context.project_dir)
    if stop_after_initialization_step(args):
        return

    prepare_round_schedule_step(context, args)
    run_round_schedule_step(context, args)
    LOGGER.info("Workflow finished.")


def validate_args(args, parser):
    """在启动长任务前检查命令行参数。"""
    def require_finite(value, option):
        if not isfinite(value):
            parser.error(f"{option} must be finite")

    positive_ints = [
        "seed_nstructs",
        "committee_size",
        "train_workers",
        "max_md_workers",
        "steps",
        "write_interval",
        "log_interval",
        "cur_n_max",
        "cur_l_max",
    ]
    for name in positive_ints:
        if getattr(args, name) <= 0:
            parser.error(f"--{name.replace('_', '-')} must be positive")

    if args.committee_size < 2:
        parser.error("--committee-size must be at least 2")
    if args.nvt_rounds < 0 or args.npt_rounds < 0:
        parser.error("--nvt-rounds and --npt-rounds must be non-negative")
    if args.nvt_rounds + args.npt_rounds <= 0:
        parser.error("At least one NVT or NPT round is required")
    if any(value <= 0 for value in args.seed_rep):
        parser.error("--seed-rep values must be positive")
    if any(value <= 0 for value in args.md_rep):
        parser.error("--md-rep values must be positive")

    positive_floats = [
        "timestep",
        "ttime",
        "ptime",
        "bulk_modulus_gpa",
        "uncertainty_eps",
        "cur_r_c",
        "dft_kspacing",
    ]
    for name in positive_floats:
        require_finite(getattr(args, name), f"--{name.replace('_', '-')}")
        if getattr(args, name) <= 0:
            parser.error(f"--{name.replace('_', '-')} must be positive")

    for name in [
        "tau_r",
        "friction",
        "seed_disturb",
        "temperature_margin",
        "frac_traceless",
        "u_min",
        "u_max",
    ]:
        require_finite(getattr(args, name), f"--{name.replace('_', '-')}")

    if args.pfactor is not None:
        require_finite(args.pfactor, "--pfactor")
        if args.pfactor <= 0:
            parser.error("--pfactor must be positive")
    if args.dft_encut is not None:
        require_finite(args.dft_encut, "--dft-encut")
        if args.dft_encut <= 0:
            parser.error("--dft-encut must be positive")
    require_finite(args.dft_encut_factor, "--dft-encut-factor")
    if args.dft_encut_factor <= 0:
        parser.error("--dft-encut-factor must be positive")
    if args.tau_r < 0:
        parser.error("--tau-r must be non-negative")
    if args.friction < 0:
        parser.error("--friction must be non-negative")
    if args.seed_disturb < 0:
        parser.error("--seed-disturb must be non-negative")
    if not 0.0 <= args.temperature_margin < 0.5:
        parser.error("--temperature-margin must be in [0, 0.5)")
    if not 0.0 <= args.frac_traceless <= 1.0:
        parser.error("--frac-traceless must be in [0, 1]")
    if args.u_min < 0 or args.u_max < args.u_min:
        parser.error("--u-max must be greater than or equal to --u-min >= 0")
    if args.cur_n_select < 0:
        parser.error("--cur-n-select must be non-negative")
    if args.selection_workers < 0:
        parser.error("--selection-workers must be non-negative")
    if args.train_epochs <= 0:
        parser.error("--train-epochs must be positive")
    if not args.cur_no_sim_threshold:
        require_finite(args.cur_sim_threshold, "--cur-sim-threshold")
        if not 0.0 <= args.cur_sim_threshold <= 1.0:
            parser.error("--cur-sim-threshold must be in [0, 1]")
    if not args.scale_factors:
        parser.error("--scale-factors must contain at least one value")
    if any(not isfinite(value) or value <= 0 for value in args.scale_factors):
        parser.error("--scale-factors values must be positive")
    if not args.pressures:
        parser.error("--pressures must contain at least one value")
    if any(not isfinite(value) for value in args.pressures):
        parser.error("--pressures values must be finite")

    try:
        seed_scales = [
            float(value.strip())
            for value in args.seed_scales.split(",")
            if value.strip()
        ]
    except ValueError:
        parser.error("--seed-scales must be comma-separated numbers")
    if not seed_scales or any(not isfinite(value) or value <= 0
                              for value in seed_scales):
        parser.error("--seed-scales values must be positive")


def parse_args():
    """解析主工作流命令行参数。"""
    parser = argparse.ArgumentParser(
        description="Fixed active-learning workflow for NNAP potential sampling"
    )
    parser.add_argument("poscar",
                        help="Initial structure file; elements are read from it")
    parser.add_argument("--work-dir",
                        help="Project directory. Default: <system>-potential")
    parser.add_argument("--init-only", action="store_true",
                        help="Only create the project directory skeleton")
    parser.add_argument("--seed-overwrite", action="store_true",
                        help="Overwrite generated 00-input/seed.db, "
                             "current.db, POSCAR, and nninit structures")
    parser.add_argument("--seed-init-runner", default="nninit",
                        help="Initial perturbation command, default: nninit")
    parser.add_argument("--seed-nstructs", type=int, default=20,
                        help="nninit nstructs per scale")
    parser.add_argument("--seed-rep", nargs=3, type=int, default=[2, 2, 2],
                        metavar=("NX", "NY", "NZ"),
                        help="nninit repeat numbers for POSCAR input")
    parser.add_argument("--seed-scales", default="0.90,0.95,1.00,1.05,1.10",
                        help="Comma-separated nninit scaleList")
    parser.add_argument("--seed-disturb", type=float, default=0.03,
                        help="nninit disturb amplitude")
    parser.add_argument("--md-rep", nargs=3, type=int, default=[2, 2, 2],
                        metavar=("NX", "NY", "NZ"),
                        help="Repeat the MD starting POSCAR before sampling")

    parser.add_argument("--nvt-rounds", type=int, default=3)
    parser.add_argument("--npt-rounds", type=int, default=3)
    parser.add_argument("--temperature-margin", type=float, default=0.1)

    parser.add_argument("--committee-size", type=int, default=10)
    parser.add_argument("--train-workers", type=int, default=5)
    parser.add_argument("--train-epochs", type=int, default=1000)
    parser.add_argument("--max-md-workers", type=int, default=1)

    parser.add_argument("--scale-factors", nargs="+", type=float,
                        default=[0.85, 0.9, 0.95, 1.0, 1.05, 1.1])
    parser.add_argument("--pressures", nargs="+", type=float,
                        default=[1, 5, 10, 20, 30, 40, 50])

    parser.add_argument("--steps", type=int, default=50000)
    parser.add_argument("--timestep", type=float, default=1.0)
    parser.add_argument("--write-interval", type=int, default=10)
    parser.add_argument("--log-interval", type=int, default=1)
    parser.add_argument("--tau-r", type=float, default=0.1)
    parser.add_argument("--friction", type=float, default=0.02,
                        help="Langevin friction in fs^-1")
    parser.add_argument("--ttime", type=float, default=75.0,
                        help="NPT thermostat time in fs")
    parser.add_argument("--ptime", type=float, default=75.0,
                        help="NPT barostat time in fs")
    parser.add_argument("--bulk-modulus-gpa", type=float, default=100.0,
                        help="Bulk modulus used to derive NPT pfactor")
    parser.add_argument("--pfactor", type=float,
                        help="Optional direct ASE NPT pfactor override")
    parser.add_argument("--frac-traceless", type=float, default=0.05)

    parser.add_argument("--u-min", type=float, default=0.3,
                        help="Temporary lower bound for covariance uncertainty; "
                             "threshold calibration is not implemented yet")
    parser.add_argument("--u-max", type=float, default=1.0,
                        help="Temporary upper bound for covariance uncertainty; "
                             "threshold calibration is not implemented yet")
    parser.add_argument("--uncertainty-eps", type=float, default=0.1,
                        help="Legacy option from relative uncertainty; "
                             "unused by covariance uncertainty")
    parser.add_argument("--selection-workers", type=int, default=1,
                        help="Uncertainty-selection workers; "
                             "1=serial, 0=auto from trajectory count when not running under JSE/JVM")
    parser.add_argument("--cur-n-select", type=int, default=100,
                        help="Maximum committee-selected structures kept by CUR per round")
    parser.add_argument("--cur-sim-threshold", type=float, default=0.9995,
                        help="Maximum post-projection cosine similarity between CUR-selected structures")
    parser.add_argument("--cur-no-sim-threshold", action="store_true",
                        help="Disable adaptive CUR similarity rejection")
    parser.add_argument("--no-cur", action="store_true",
                        help="Disable CUR diversity selection before DFT")
    parser.add_argument("--cur-no-base-projection", action="store_true",
                        help="Disable projection against current.db in CUR")
    parser.add_argument("--cur-r-c", type=float, default=6.0,
                        help="CUR descriptor cutoff radius")
    parser.add_argument("--cur-n-max", type=int, default=5,
                        help="CUR Chebyshev radial order")
    parser.add_argument("--cur-l-max", type=int, default=6,
                        help="CUR spherical harmonic angular order")
    parser.add_argument("--runner", default="jse",
                        help="Runner for md_worker.py, default: jse")
    parser.add_argument("--dft-runner", default="nncalc",
                        help="DFT labeling command, default: nncalc")
    parser.add_argument("--dft-module", default="jse",
                        help="Module loaded before DFT; empty string "
                             "disables module load")
    parser.add_argument("--dft-magmom", default="_",
                        help="nncalc magmom argument. Default '_' means non-magnetic")
    parser.add_argument("--dft-kspacing", type=float, default=0.2,
                        help="nncalc KSPACING argument")
    parser.add_argument("--dft-encut", type=float, default=DEFAULT_DFT_ENCUT,
                        help="Explicit nncalc ENCUT argument; default is auto.")
    parser.add_argument("--dft-encut-factor", type=float,
                        default=DEFAULT_DFT_ENCUT_FACTOR,
                        help="Default DFT ENCUT is this factor times max ENMAX from POTCAR.")
    args = parser.parse_args()
    validate_args(args, parser)
    return args


def main():
    """主工作流命令行入口。"""
    try:
        run_workflow(parse_args())
    except Exception as exc:
        if LOGGER.handlers:
            LOGGER.exception("Workflow failed")
        else:
            print(f"Workflow failed: {exc}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
