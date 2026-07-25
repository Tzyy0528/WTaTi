#!/usr/bin/env python3
"""Python RSS driver with an embedded Groovy/JSE Rss+Mini runner."""

import argparse
import os
import shlex
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path


GROOVY_RUNNER = r"""#!/usr/bin/env jse
import jnn.core.*

elems = args[0].split(',') as String[]
weights = args[1].split(',').collect({ it as double }) as double[]
natomsList = args[2].split(',').collect({ it as int }) as int[]
pressList = args[8].split(',').collect({ it as double }) as double[]

rss = new Rss()
rss.elems = elems
rss.weights = weights
rss.outDir = args[3]
rss.natomsList = natomsList
rss.nstructs = args[4] as int
rss.atomicVolume = args[5] as double
rss.run()

mini = new Mini()
mini.inDir = rss.outDir
mini.outDir = args[6]
mini.nnpotPath = args[7]
mini.pressList = pressList
mini.keyword = args[9]
mini.loop = args[10] as int
mini.etol = args[11] as double
mini.ftol = args[12] as double
mini.run()
"""


DEFAULT_RATIOS = [
    (1, 1), (1, 2), (2, 1), (1, 3), (3, 1),
    (1, 4), (4, 1), (1, 5), (5, 1),
    (1, 6), (6, 1), (1, 7), (7, 1),
    (1, 8), (8, 1), (2, 3), (3, 2),
    (2, 5), (5, 2), (2, 7), (7, 2),
    (3, 4), (4, 3), (3, 5), (5, 3),
    (4, 5), (5, 4),
]


@dataclass(frozen=True)
class RssCase:
    label: str
    weights: tuple[int, ...]
    natoms: tuple[int, ...]

    def raw_dir(self, raw_root):
        return raw_root / self.label

    def min_dir(self, min_root):
        return min_root / self.label

    def done_file(self, min_root):
        return self.min_dir(min_root) / ".rss_done"

    def log_file(self, log_root):
        return log_root / f"{self.label}.log"


@dataclass(frozen=True)
class RssLayout:
    base: Path
    raw_root: Path
    min_root: Path
    log_root: Path
    collect_dir: Path
    runner: Path


@dataclass(frozen=True)
class CaseResult:
    case: RssCase
    output_count: int
    log_path: Path


@dataclass(frozen=True)
class RssConfig:
    elems: tuple[str, ...]
    jnn: str
    nstructs: int
    atomic_volume: float
    mini_press_list: tuple[float, ...]
    mini_keyword: str
    mini_loop: int
    mini_etol: float
    mini_ftol: float
    jse_cmd: str
    keep_raw: bool


def main():
    args = parse_args()
    elems = tuple(parse_elems(args.elems))
    if len(elems) not in (1, 2):
        raise SystemExit("Only unary and binary RSS are supported.")
    if len(elems) == 1 and args.ratios:
        raise SystemExit("--ratios is only valid for binary RSS.")
    if not Path(args.jnn).is_file():
        raise SystemExit(f"JNN potential does not exist: {args.jnn}")

    config = RssConfig(
        elems=elems,
        jnn=args.jnn,
        nstructs=args.nstructs,
        atomic_volume=args.atomic_volume,
        mini_press_list=tuple(args.mini_press_list),
        mini_keyword=args.mini_keyword.strip(),
        mini_loop=args.mini_loop,
        mini_etol=args.mini_etol,
        mini_ftol=args.mini_ftol,
        jse_cmd=args.jse_cmd,
        keep_raw=args.keep_raw,
    )
    if not config.mini_keyword:
        raise SystemExit("--mini-keyword must not be empty")

    cases = build_cases(elems, args)
    layout = make_layout(Path(args.out_dir or f"{''.join(elems)}-rss"))
    if not args.overwrite and is_collection_done(layout):
        count = count_structure_files(layout.collect_dir)
        print(f"Skip completed RSS collection: {layout.collect_dir} ({count})")
        return
    prepare_output(layout, args.overwrite)

    skipped = [case for case in cases if is_case_done(case, layout.min_root)]
    pending = [case for case in cases if case not in skipped]
    for case in skipped:
        print(f"Skip completed RSS case {case.label}")

    layout.runner.write_text(GROOVY_RUNNER, encoding="utf-8")
    try:
        run_pending_cases(pending, layout, config, args.jobs)
    finally:
        layout.runner.unlink(missing_ok=True)

    count = collect_poscars(cases, layout.min_root, layout.collect_dir)
    write_collection_done(layout, count)
    if not args.keep_minimized_work:
        shutil.rmtree(layout.min_root, ignore_errors=True)
        if layout.raw_root.exists() and not any(layout.raw_root.iterdir()):
            layout.raw_root.rmdir()
    print(f"RSS finished. Collected POSCARs: {layout.collect_dir} ({count})")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Standalone unary/binary RSS sampling via JNN/JSE Rss+Mini."
    )
    parser.add_argument("--elems", required=True, help="Al or Al,Si")
    parser.add_argument("--jnn", required=True, help="JNN potential path")
    parser.add_argument("--out-dir")
    parser.add_argument("--nstructs", type=positive_int, default=50)
    parser.add_argument("--atomic-volume", type=positive_float, default=12.0)
    parser.add_argument("--natoms-list", type=int_list)
    parser.add_argument("--ratios", type=ratio_list)
    parser.add_argument(
        "--jobs",
        type=nonnegative_int,
        default=0,
        help="parallel RSS cases; 0=auto, 1=sequential",
    )
    parser.add_argument(
        "--mini-press-list",
        type=float_list,
        default=[0.0, 20e4, 40e4],
        help="Mini box/relax pressures in bar: 0,20e4,40e4 = 0,20,40 GPa",
    )
    parser.add_argument("--mini-keyword", default="tri")
    parser.add_argument("--mini-loop", type=positive_int, default=10)
    parser.add_argument("--mini-etol", type=positive_float, default=1e-4)
    parser.add_argument("--mini-ftol", type=positive_float, default=1e-8)
    parser.add_argument("--jse-cmd", default="jse")
    parser.add_argument("--keep-raw", action="store_true")
    parser.add_argument(
        "--keep-minimized-work",
        action="store_true",
        help="Keep case-organized minimized work files after flat collection.",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def build_cases(elems, args):
    if len(elems) == 1:
        natoms = tuple(args.natoms_list or [9, 10, 12, 15, 18, 20, 22, 25])
        return [RssCase(f"unary-{elems[0]}", (1,), natoms)]

    cases = []
    for weights in args.ratios or DEFAULT_RATIOS:
        weights = tuple(weights)
        natoms = tuple(args.natoms_list or default_natoms(weights))
        validate_natoms(natoms, weights)
        cases.append(RssCase(f"w-{weights[0]}-{weights[1]}", weights, natoms))
    return cases


def make_layout(base):
    return RssLayout(
        base=base,
        raw_root=base / "raw",
        min_root=base / "minimized",
        log_root=base / "logs",
        collect_dir=base / "rss-minimized-poscar",
        runner=base / f".rss_run_case_{os.getpid()}.groovy",
    )


def prepare_output(layout, overwrite):
    assert_safe_output_dir(layout.base)
    if layout.base.exists() and not layout.base.is_dir():
        raise SystemExit(f"Output path exists and is not a directory: {layout.base}")
    if layout.base.exists() and overwrite:
        shutil.rmtree(layout.base)
    for path in (layout.base, layout.raw_root, layout.min_root, layout.log_root):
        path.mkdir(parents=True, exist_ok=True)


def run_pending_cases(cases, layout, config, jobs):
    if not cases:
        print("No pending RSS cases.")
        return

    workers = choose_workers(jobs, len(cases))
    print(f"Running {len(cases)} RSS case(s) with {workers} worker(s).")
    if workers == 1:
        for case in cases:
            result = run_case(case, layout, config)
            print_done(result)
        return

    failures = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_map = {
            pool.submit(run_case, case, layout, config): case
            for case in cases
        }
        for future in as_completed(future_map):
            case = future_map[future]
            try:
                print_done(future.result())
            except Exception as exc:
                failures.append((case, exc))
                print(f"FAILED RSS case {case.label}: {exc}")
    if failures:
        labels = ", ".join(case.label for case, _ in failures)
        raise SystemExit(f"Failed RSS case(s): {labels}")


def run_case(case, layout, config):
    raw_dir = case.raw_dir(layout.raw_root)
    min_dir = case.min_dir(layout.min_root)
    log_path = case.log_file(layout.log_root)
    clean_incomplete_case(raw_dir, min_dir)

    cmd = case_command(layout.runner, case, raw_dir, min_dir, config)
    with log_path.open("w", encoding="utf-8") as log:
        log.write("# " + " ".join(shlex.quote(str(x)) for x in cmd) + "\n")
        subprocess.run(
            cmd,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            check=True,
        )

    count = count_structure_files(min_dir)
    if count == 0:
        raise RuntimeError(f"case {case.label} produced no POSCAR files")
    write_done_marker(case, min_dir, count)
    if not config.keep_raw:
        shutil.rmtree(raw_dir, ignore_errors=True)
    return CaseResult(case, count, log_path)


def case_command(runner, case, raw_dir, min_dir, config):
    return [
        config.jse_cmd,
        str(runner),
        ",".join(config.elems),
        join_numbers(case.weights),
        join_numbers(case.natoms),
        str(raw_dir),
        str(config.nstructs),
        str(config.atomic_volume),
        str(min_dir),
        config.jnn,
        join_numbers(config.mini_press_list),
        config.mini_keyword,
        str(config.mini_loop),
        str(config.mini_etol),
        str(config.mini_ftol),
    ]


def clean_incomplete_case(raw_dir, min_dir):
    if raw_dir.exists():
        shutil.rmtree(raw_dir)
    if min_dir.exists():
        shutil.rmtree(min_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    min_dir.mkdir(parents=True, exist_ok=True)


def is_case_done(case, min_root):
    return case.done_file(min_root).exists() and count_structure_files(
        case.min_dir(min_root)
    ) > 0


def write_done_marker(case, min_dir, output_count):
    case.done_file(min_dir.parent).write_text(
        "\n".join([
            f"label={case.label}",
            f"weights={join_numbers(case.weights)}",
            f"natoms={join_numbers(case.natoms)}",
            f"outputs={output_count}",
            "",
        ]),
        encoding="utf-8",
    )


def print_done(result):
    print(
        f"Finished RSS case {result.case.label}: "
        f"{result.output_count} POSCAR(s), log={result.log_path}"
    )


def collect_poscars(cases, min_root, output_dir):
    files = []
    for case in cases:
        case_dir = case.min_dir(min_root)
        files.extend(
            (case, p)
            for p in case_dir.rglob("*")
            if p.is_file() and is_structure_file(p)
        )
    files = sorted(files, key=lambda item: (item[0].label, str(item[1])))
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    manifest = output_dir / "manifest.tsv"
    with manifest.open("w", encoding="utf-8") as fout:
        fout.write("new_name\toriginal_path\n")
        for i, (case, src) in enumerate(files, 1):
            name = f"{i:06d}.poscar"
            shutil.copy2(src, output_dir / name)
            source_name = Path(case.label) / src.relative_to(case.min_dir(min_root))
            fout.write(f"{name}\t{source_name}\n")
    return len(files)


def collection_done_file(layout):
    return layout.collect_dir / ".rss_done"


def is_collection_done(layout):
    return (
        collection_done_file(layout).exists()
        and count_structure_files(layout.collect_dir) > 0
    )


def write_collection_done(layout, output_count):
    collection_done_file(layout).write_text(
        f"outputs={output_count}\n",
        encoding="utf-8",
    )


def count_structure_files(directory):
    if not directory.exists():
        return 0
    return sum(1 for p in directory.rglob("*") if p.is_file() and is_structure_file(p))


def assert_safe_output_dir(path):
    target = path.resolve()
    if target == Path.cwd().resolve() or target.parent == target:
        raise SystemExit(f"Refusing unsafe output directory: {path}")


def choose_workers(jobs, ncases):
    if jobs == 0:
        return max(1, min(ncases, os.cpu_count() or 1))
    return min(jobs, ncases)


def default_natoms(weights):
    total = sum(weights)
    if total == 2:
        return [4, 6, 8]
    if total == 3:
        return [3, 6, 9]
    if total == 4:
        return [4, 8]
    return [total]


def validate_natoms(natoms, weights):
    total = sum(weights)
    bad = [n for n in natoms if n % total != 0]
    if bad:
        raise SystemExit(f"natoms {bad} incompatible with weights {weights}")


def parse_elems(text):
    return [x.strip() for x in text.split(",") if x.strip()]


def int_list(text):
    vals = [int(x.strip()) for x in text.split(",") if x.strip()]
    if not vals or any(x <= 0 for x in vals):
        raise argparse.ArgumentTypeError("expected positive comma-separated ints")
    return vals


def float_list(text):
    vals = [float(x.strip()) for x in text.split(",") if x.strip()]
    if not vals:
        raise argparse.ArgumentTypeError("expected comma-separated floats")
    return vals


def ratio_list(text):
    ratios = []
    try:
        for item in text.split(","):
            a, b = item.split(":")
            ratios.append((int(a), int(b)))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected ratios like 1:1,1:2") from exc
    if not ratios or any(a <= 0 or b <= 0 for a, b in ratios):
        raise argparse.ArgumentTypeError("expected positive ratios like 1:1,1:2")
    return ratios


def positive_int(text):
    value = int(text)
    if value <= 0:
        raise argparse.ArgumentTypeError("expected positive integer")
    return value


def nonnegative_int(text):
    value = int(text)
    if value < 0:
        raise argparse.ArgumentTypeError("expected nonnegative integer")
    return value


def positive_float(text):
    value = float(text)
    if value <= 0.0:
        raise argparse.ArgumentTypeError("expected positive float")
    return value


def join_numbers(values):
    return ",".join(str(x) for x in values)


def is_structure_file(path):
    name = path.name.lower()
    return name in ("poscar", "contcar") or name.endswith((".poscar", ".vasp"))


if __name__ == "__main__":
    main()
