#!/usr/bin/env python3
"""Batch VASP DFT labeling backend for ASE/NNAP active-learning data.

This script prepares one VASP static-calculation directory per POSCAR, can run
the batch with concurrent ``srun`` job steps, collects completed VASP results
into an ASE database, and merges that labeled-new-structures database with an
existing ``current.db``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from collections import OrderedDict
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
REPO_ROOT = SCRIPT.parents[1]
DEFAULT_POTCAR_ROOT = REPO_ROOT / "POTCAR" / "PBE"
DEFAULT_CORES_PER_JOB = 8
DEFAULT_KSPACING = 0.2
DEFAULT_ENCUT_FACTOR = 1.3
DEFAULT_NCORE = 2
PROGRESS_BAR_WIDTH = 30
META_NAME = "vasp_batch_meta.json"
MANIFEST_NAME = "vasp_batch_manifest.json"
COMPLETION_MARKERS = (
    "General timing and accounting",
    "Voluntary context switches",
)
STALE_VASP_OUTPUTS = (
    "OUTCAR",
    "vasprun.xml",
    "CONTCAR",
    "OSZICAR",
    "XDATCAR",
    "EIGENVAL",
    "IBZKPT",
    "REPORT",
    "WAVECAR",
    "CHGCAR",
    "log",
    "vasp_command.sh",
)


DEFAULT_INCAR = OrderedDict(
    [
        ("ISTART", 0),
        ("ICHARG", 2),
        ("PREC", "Accurate"),
        ("ALGO", "Normal"),
        ("EDIFF", "1E-5"),
        ("NELM", 200),
        ("SIGMA", 0.1),
        ("KSPACING", DEFAULT_KSPACING),
        ("KGAMMA", True),
        ("LASPH", True),
        ("LCHARG", False),
        ("LWAVE", False),
        ("GGA_COMPAT", False),
        ("LREAL", "Auto"),
        ("ISYM", 0),
        ("KPAR", 1),
        ("NCORE", DEFAULT_NCORE),
        ("NSIM", 6),
        ("IBRION", -1),
        ("NSW", 0),
        ("ISIF", 2),
    ]
)


def sort_key(path: Path) -> tuple[int, int | str, str]:
    matches = re.findall(r"\d+", path.stem)
    if matches:
        return (0, int(matches[-1]), path.stem)
    return (1, path.stem, path.stem)


def safe_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
    return cleaned or "structure"


def log(message: str) -> None:
    print(message, flush=True)


def format_duration(seconds: float) -> str:
    total = max(0, int(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_progress_bar(completed: int, total: int, width: int = PROGRESS_BAR_WIDTH) -> str:
    if total <= 0:
        ratio = 1.0
    else:
        ratio = max(0.0, min(1.0, completed / total))
    filled = int(round(ratio * width))
    bar = "#" * filled + "-" * (width - filled)
    return f"[{bar}] {ratio * 100:5.1f}%"


def estimate_eta(elapsed_seconds: float, completed: int, total: int) -> str:
    remaining = total - completed
    if remaining <= 0:
        return "00:00"
    if completed <= 0:
        return "--:--"
    return format_duration(elapsed_seconds * remaining / completed)


def bool_text(value: bool) -> str:
    return ".TRUE." if value else ".FALSE."


def format_incar_value(value: Any) -> str:
    if isinstance(value, bool):
        return bool_text(value)
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def parse_incar_set(spec: str) -> tuple[str, str]:
    if "=" not in spec:
        raise argparse.ArgumentTypeError(f"Expected KEY=VALUE, got: {spec}")
    key, value = spec.split("=", 1)
    key = key.strip().upper()
    value = value.strip()
    if not key or not value:
        raise argparse.ArgumentTypeError(f"Expected KEY=VALUE, got: {spec}")
    return key, value


def parse_potcar_map(spec: str) -> tuple[str, str]:
    if "=" not in spec:
        raise argparse.ArgumentTypeError(f"Expected ELEMENT=SETUP_DIR, got: {spec}")
    symbol, setup = spec.split("=", 1)
    symbol = symbol.strip()
    setup = setup.strip()
    if not symbol or not setup:
        raise argparse.ArgumentTypeError(f"Expected ELEMENT=SETUP_DIR, got: {spec}")
    return symbol, setup


def parse_enmax_from_potcar(path: Path) -> float:
    text = path.read_text(encoding="utf-8", errors="ignore")
    values = [float(value) for value in re.findall(r"\bENMAX\s*=\s*([0-9.]+)", text)]
    if not values:
        raise ValueError(f"Cannot find ENMAX in POTCAR: {path}")
    return max(values)


def incar_has_key(text: str, key: str) -> bool:
    pattern = re.compile(rf"^\s*{re.escape(key)}\b", re.IGNORECASE)
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].split("!", 1)[0]
        if pattern.match(line):
            return True
    return False


def build_incar_text(args: argparse.Namespace, encut: float | None = None) -> str:
    if getattr(args, "incar_template", None):
        text = Path(args.incar_template).read_text(encoding="utf-8")
        lines = [text.rstrip(), ""]
        extra_sets = getattr(args, "incar_set", []) or []
        extra_keys = {key.upper() for key, _ in extra_sets}
        if (
            encut is not None
            and "ENCUT" not in extra_keys
            and (getattr(args, "encut", None) is not None or not incar_has_key(text, "ENCUT"))
        ):
            lines.append("# Default added by vasp_batch_dft.py")
            lines.append(f"ENCUT = {format_incar_value(encut)}")
            lines.append("")
        if extra_sets:
            lines.append("# Overrides added by vasp_batch_dft.py")
            for key, value in extra_sets:
                lines.append(f"{key} = {value}")
            lines.append("")
        return "\n".join(lines)

    incar = OrderedDict(DEFAULT_INCAR)
    incar["KSPACING"] = getattr(args, "kspacing", DEFAULT_KSPACING)
    if encut is not None:
        incar["ENCUT"] = encut
    extra_sets = getattr(args, "incar_set", []) or []
    extra_keys = {key.upper() for key, _ in extra_sets}
    if getattr(args, "npar", None) is not None:
        incar.pop("NCORE", None)
        incar["NPAR"] = args.npar
    elif "NPAR" in extra_keys and "NCORE" not in extra_keys:
        incar.pop("NCORE", None)
    magmom = getattr(args, "magmom", "_")
    if magmom and magmom != "_":
        incar["MAGMOM"] = magmom
    for key, value in extra_sets:
        incar[key] = value

    lines = ["# Static single-point VASP input generated by vasp_batch_dft.py"]
    for key, value in incar.items():
        lines.append(f"{key} = {format_incar_value(value)}")
    return "\n".join(lines) + "\n"


def list_poscars(input_dir: Path) -> list[Path]:
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Input POSCAR directory not found: {input_dir}")
    poscars = sorted(input_dir.glob("*.poscar"), key=sort_key)
    if not poscars:
        raise RuntimeError(f"No *.poscar files found in {input_dir}")
    return poscars


def parse_poscar_species(poscar_path: Path) -> list[str]:
    lines = [line.strip() for line in poscar_path.read_text(encoding="utf-8").splitlines()]
    lines = [line for line in lines if line]
    if len(lines) < 7:
        raise ValueError(f"POSCAR is too short: {poscar_path}")

    symbols = lines[5].split()
    counts = lines[6].split()
    if symbols and counts and all(token.lstrip("+-").isdigit() for token in counts):
        return symbols
    raise ValueError(
        f"Cannot infer VASP5 element symbols from {poscar_path}; "
        "the POSCAR must contain an element-symbol line."
    )


class PotcarProvider:
    def __init__(self, root: Path, mappings: dict[str, str] | None = None):
        self.root = root
        self.mappings = mappings or {}
        self._cache: dict[tuple[str, ...], bytes] = {}
        self._enmax_cache: dict[str, float] = {}

    def potcar_path(self, symbol: str) -> Path:
        setup = self.mappings.get(symbol, symbol)
        path = self.root / setup / "POTCAR"
        if not path.is_file():
            raise FileNotFoundError(
                f"Missing POTCAR for {symbol}: expected {path}. "
                "Use --potcar-root or --potcar-map ELEMENT=SETUP_DIR if needed."
            )
        return path

    def write(self, species: list[str], dest: Path) -> None:
        key = tuple(species)
        if key not in self._cache:
            chunks = []
            for symbol in species:
                chunks.append(self.potcar_path(symbol).read_bytes())
            self._cache[key] = b"".join(chunks)
        dest.write_bytes(self._cache[key])

    def enmax(self, symbol: str) -> float:
        setup = self.mappings.get(symbol, symbol)
        if setup not in self._enmax_cache:
            self._enmax_cache[setup] = parse_enmax_from_potcar(self.potcar_path(symbol))
        return self._enmax_cache[setup]

    def recommended_encut(self, species: list[str], factor: float = DEFAULT_ENCUT_FACTOR) -> float:
        if not species:
            raise ValueError("Cannot determine ENCUT without species")
        return max(self.enmax(symbol) for symbol in species) * factor


def outcar_is_complete(task_dir: Path) -> bool:
    outcar = task_dir / "OUTCAR"
    if not outcar.exists() or outcar.stat().st_size == 0:
        return False
    with outcar.open("rb") as handle:
        size = outcar.stat().st_size
        handle.seek(max(0, size - 8192))
        tail = handle.read().decode(errors="ignore")
    return any(marker in tail for marker in COMPLETION_MARKERS)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def remove_stale_vasp_outputs(task_dir: Path) -> None:
    for name in STALE_VASP_OUTPUTS:
        path = task_dir / name
        if path.exists() and path.is_file():
            path.unlink()


def task_dirs(run_dir: Path) -> list[Path]:
    if (run_dir / "POSCAR").is_file():
        return [run_dir]
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")
    dirs = [p for p in run_dir.iterdir() if p.is_dir() and (p / "POSCAR").is_file()]
    return sorted(dirs, key=lambda p: p.name)


def prepare_task(
    task_dir: Path,
    poscar_path: Path,
    order: int,
    tag: str,
    args: argparse.Namespace,
    potcar_provider: PotcarProvider,
    force: bool,
) -> str:
    meta_path = task_dir / META_NAME
    source = str(poscar_path.resolve())
    species = parse_poscar_species(poscar_path)
    encut = (
        args.encut
        if getattr(args, "encut", None) is not None
        else potcar_provider.recommended_encut(
            species,
            getattr(args, "encut_factor", DEFAULT_ENCUT_FACTOR),
        )
    )
    incar_text = build_incar_text(args, encut=encut)

    if task_dir.exists() and any(task_dir.iterdir()) and not force:
        if meta_path.exists():
            meta = read_json(meta_path)
            if meta.get("source_poscar") == source:
                incar_path = task_dir / "INCAR"
                if incar_path.exists() and incar_path.read_text(encoding="utf-8") == incar_text:
                    return "reused"
                raise FileExistsError(
                    f"Existing task directory has stale/different INCAR: {task_dir}. "
                    "Use --force to rewrite prepared inputs and rerun completed outputs."
                )
            raise FileExistsError(
                f"Existing task directory has different source: {task_dir}. "
                "Use --force to overwrite prepared inputs."
            )
        raise FileExistsError(
            f"Existing non-empty task directory is not managed by this script: {task_dir}. "
            "Use --force only if it is safe to rewrite inputs."
        )

    task_dir.mkdir(parents=True, exist_ok=True)
    if force:
        remove_stale_vasp_outputs(task_dir)
    shutil.copy2(poscar_path, task_dir / "POSCAR")
    (task_dir / "INCAR").write_text(incar_text, encoding="utf-8")
    kpoints = task_dir / "KPOINTS"
    if kpoints.exists():
        kpoints.unlink()

    potcar_provider.write(species, task_dir / "POTCAR")
    meta = {
        "created_by": SCRIPT.name,
        "source_poscar": source,
        "source_name": poscar_path.name,
        "order": order,
        "tag": tag,
        "species": species,
        "encut": encut,
        "encut_source": (
            "explicit --encut"
            if getattr(args, "encut", None) is not None
            else f"{getattr(args, 'encut_factor', DEFAULT_ENCUT_FACTOR):g}*max(POTCAR ENMAX)"
        ),
    }
    write_json(meta_path, meta)
    return "prepared"


def prepare_batch(
    input_dir: Path,
    run_dir: Path,
    args: argparse.Namespace,
    potcar_provider: PotcarProvider,
    tag: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    input_dir = input_dir.resolve()
    run_dir = run_dir.resolve()
    if input_dir == run_dir:
        raise ValueError("input_dir and run_dir must be different")
    poscars = list_poscars(input_dir)
    tag = tag or input_dir.name
    run_dir.mkdir(parents=True, exist_ok=True)

    counts = {"prepared": 0, "reused": 0}
    tasks = []
    for index, poscar_path in enumerate(poscars, 1):
        task_name = f"{index:05d}_{safe_name(poscar_path.stem)}"
        task_dir = run_dir / task_name
        status = prepare_task(
            task_dir=task_dir,
            poscar_path=poscar_path,
            order=index,
            tag=tag,
            args=args,
            potcar_provider=potcar_provider,
            force=force,
        )
        counts[status] = counts.get(status, 0) + 1
        tasks.append(
            {
                "order": index,
                "task_dir": str(task_dir),
                "source_poscar": str(poscar_path.resolve()),
                "status": status,
            }
        )

    manifest = {
        "input_dir": str(input_dir),
        "run_dir": str(run_dir),
        "tag": tag,
        "task_count": len(poscars),
        "prepared": counts.get("prepared", 0),
        "reused": counts.get("reused", 0),
        "potcar_root": str(potcar_provider.root.resolve()),
        "encut": (
            str(args.encut)
            if getattr(args, "encut", None) is not None
            else f"{getattr(args, 'encut_factor', DEFAULT_ENCUT_FACTOR):g}*max(POTCAR ENMAX)"
        ),
        "tasks": tasks,
    }
    write_json(run_dir / MANIFEST_NAME, manifest)
    return manifest


def _parse_slurm_job_cpus(value: str) -> int | None:
    match = re.match(r"(\d+)", value.strip())
    return int(match.group(1)) if match else None


def detect_available_cpus() -> int:
    for key in ("SLURM_NTASKS", "SLURM_CPUS_ON_NODE", "SLURM_JOB_CPUS_PER_NODE"):
        raw = os.environ.get(key)
        if not raw:
            continue
        parsed = _parse_slurm_job_cpus(raw) if key == "SLURM_JOB_CPUS_PER_NODE" else int(raw)
        if parsed and parsed > 0:
            return parsed
    return os.cpu_count() or 1


def detect_max_workers(cli_value: int | None, cores_per_job: int, task_count: int) -> int:
    if cores_per_job <= 0:
        raise ValueError("cores-per-job must be > 0")
    if cli_value is not None:
        if cli_value <= 0:
            raise ValueError("max-workers must be > 0")
        return min(cli_value, task_count)
    return max(1, min(task_count, detect_available_cpus() // cores_per_job))


def run_task(task_dir: Path, cores_per_job: int, vasp_command: str, keep_chgcar: bool) -> None:
    command = ["srun", "--exclusive", "-n", str(cores_per_job), *shlex.split(vasp_command)]
    (task_dir / "vasp_command.sh").write_text(
        " ".join(shlex.quote(part) for part in command) + "\n",
        encoding="utf-8",
    )
    with (task_dir / "log").open("w", encoding="utf-8") as log_file:
        subprocess.run(
            command,
            cwd=task_dir,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            check=True,
        )
    if not keep_chgcar:
        chgcar = task_dir / "CHGCAR"
        if chgcar.exists():
            chgcar.unlink()


def run_batch(
    run_dir: Path,
    cores_per_job: int,
    max_workers: int | None,
    vasp_command: str,
    keep_chgcar: bool,
    force: bool,
    progress_interval: float = 60.0,
) -> dict[str, Any]:
    dirs = task_dirs(run_dir.resolve())
    if not dirs:
        raise RuntimeError(f"No prepared VASP task directories found in {run_dir}")
    workers = detect_max_workers(max_workers, cores_per_job, len(dirs))
    if progress_interval < 0:
        raise ValueError("progress-interval must be >= 0")

    to_run = []
    skipped = []
    for directory in dirs:
        if not force and outcar_is_complete(directory):
            skipped.append(directory)
        else:
            to_run.append(directory)

    log(f"tasks={len(dirs)} to_run={len(to_run)} skipped_completed={len(skipped)}")
    log(f"cores_per_job={cores_per_job} max_workers={workers} vasp_command={vasp_command}")
    log(f"progress_interval={progress_interval:g}s")

    succeeded = []
    failed = []
    start_time = time.monotonic()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        pending = {
            executor.submit(run_task, directory, cores_per_job, vasp_command, keep_chgcar): directory
            for directory in to_run
        }

        def report_progress(reason: str) -> None:
            pending_count = len(pending)
            running = min(workers, pending_count)
            waiting = max(0, pending_count - running)
            completed = len(skipped) + len(succeeded) + len(failed)
            elapsed_seconds = time.monotonic() - start_time
            elapsed = format_duration(elapsed_seconds)
            eta = estimate_eta(elapsed_seconds, completed, len(dirs))
            bar = format_progress_bar(completed, len(dirs))
            log(
                f"progress[{reason}] {bar} {completed}/{len(dirs)} "
                f"succeeded={len(succeeded)} failed={len(failed)} skipped={len(skipped)} "
                f"running~{running} waiting~{waiting} elapsed={elapsed} eta={eta}"
            )

        report_progress("start")
        timeout = progress_interval if progress_interval > 0 else None
        while pending:
            done, _ = wait(pending, timeout=timeout, return_when=FIRST_COMPLETED)
            if not done:
                report_progress("running")
                continue
            for future in done:
                directory = pending.pop(future)
                task_index = len(succeeded) + len(failed) + 1
                task_total = len(to_run)
                try:
                    future.result()
                    succeeded.append(directory)
                    log(f"done[{task_index}/{task_total}] {directory}")
                except Exception as exc:  # noqa: BLE001 - collect all task failures
                    failed.append((directory, str(exc)))
                    log(f"failed[{task_index}/{task_total}] {directory}: {exc}")
            report_progress("update")

    summary = {
        "task_count": len(dirs),
        "to_run": len(to_run),
        "skipped_completed": len(skipped),
        "succeeded": len(succeeded),
        "failed": [{"task_dir": str(path), "error": error} for path, error in failed],
    }
    write_json(run_dir.resolve() / "vasp_batch_run_summary.json", summary)
    log(
        f"run summary: succeeded={len(succeeded)} failed={len(failed)} "
        f"skipped={len(skipped)} elapsed={format_duration(time.monotonic() - start_time)}"
    )
    if failed:
        raise RuntimeError(f"{len(failed)} VASP task(s) failed; see task logs.")
    return summary


def import_ase_io():
    try:
        from ase.io import read
    except ModuleNotFoundError as exc:
        raise RuntimeError("ASE is required. Run after `module load jse` or install ASE.") from exc
    return read


def import_ase_db():
    try:
        from ase.db import connect
    except ModuleNotFoundError as exc:
        raise RuntimeError("ASE is required. Run after `module load jse` or install ASE.") from exc
    return connect


def read_vasp_result(task_dir: Path):
    read = import_ase_io()
    errors = []
    for filename, fmt in (("vasprun.xml", "vasp-xml"), ("OUTCAR", "vasp-out")):
        path = task_dir / filename
        if not path.exists() or path.stat().st_size == 0:
            continue
        try:
            return read(path, format=fmt, index=-1)
        except Exception as exc:  # noqa: BLE001 - fallback to the next parser
            errors.append(f"{filename}: {type(exc).__name__}: {exc}")
    joined = "; ".join(errors) if errors else "no vasprun.xml or OUTCAR found"
    raise RuntimeError(f"Cannot read VASP result in {task_dir}: {joined}")


def atoms_hash(atoms) -> str:
    payload = {
        "symbols": atoms.get_chemical_symbols(),
        "cell": atoms.cell.array.round(12).tolist(),
        "positions": atoms.positions.round(12).tolist(),
        "pbc": atoms.pbc.tolist(),
    }
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def require_results(atoms, task_dir: Path) -> None:
    if atoms.calc is None:
        raise RuntimeError(f"No calculator results found for {task_dir}")
    results = getattr(atoms.calc, "results", {})
    missing = [key for key in ("energy", "forces", "stress") if key not in results]
    if missing:
        raise RuntimeError(f"Missing VASP result(s) {missing} for {task_dir}")


def task_meta(task_dir: Path) -> dict[str, Any]:
    path = task_dir / META_NAME
    if path.exists():
        return read_json(path)
    return {
        "order": 0,
        "tag": task_dir.parent.name,
        "source_name": task_dir.name,
        "source_poscar": "",
    }


def collect_results(
    run_dir: Path,
    output_db: Path,
    overwrite: bool = False,
    skip_incomplete: bool = False,
    tag: str | None = None,
) -> int:
    connect = import_ase_db()
    run_dir = run_dir.resolve()
    output_db = output_db.resolve()
    if output_db.exists():
        if not overwrite:
            raise FileExistsError(f"Output DB exists; use --overwrite: {output_db}")
        output_db.unlink()
    output_db.parent.mkdir(parents=True, exist_ok=True)

    dirs = task_dirs(run_dir)
    ordered = sorted(dirs, key=lambda d: (task_meta(d).get("order", 0), d.name))
    written = 0
    skipped = []
    with connect(output_db) as db:
        for directory in ordered:
            if not outcar_is_complete(directory):
                message = f"Incomplete VASP task: {directory}"
                if skip_incomplete:
                    skipped.append(message)
                    continue
                raise RuntimeError(message)
            try:
                atoms = read_vasp_result(directory)
                require_results(atoms, directory)
            except Exception as exc:  # noqa: BLE001 - attach task context
                if skip_incomplete:
                    skipped.append(f"{directory}: {exc}")
                    continue
                raise
            meta = task_meta(directory)
            row_tag = tag or meta.get("tag") or run_dir.name
            key_value_pairs = {
                "unused": False,
                "tag": str(row_tag),
                "hash": atoms_hash(atoms),
                "source": str(meta.get("source_name") or directory.name),
            }
            db.write(atoms, key_value_pairs=key_value_pairs)
            written += 1

    if skipped:
        (output_db.parent / f"{output_db.stem}_skipped.txt").write_text(
            "\n".join(skipped) + "\n",
            encoding="utf-8",
        )
    log(f"wrote {written} rows to {output_db}")
    return written


def merge_databases(current_db: Path, labeled_db: Path, updated_db: Path, overwrite: bool = False) -> tuple[int, int]:
    connect = import_ase_db()
    current_db = current_db.resolve()
    labeled_db = labeled_db.resolve()
    updated_db = updated_db.resolve()
    if updated_db in (current_db, labeled_db):
        raise ValueError("updated_db must be different from current_db and labeled_db")
    for path in (current_db, labeled_db):
        if not path.exists():
            raise FileNotFoundError(path)
    if updated_db.exists():
        if not overwrite:
            raise FileExistsError(f"Updated DB exists; use --overwrite: {updated_db}")
        updated_db.unlink()
    updated_db.parent.mkdir(parents=True, exist_ok=True)

    current_count = 0
    labeled_count = 0
    with connect(updated_db) as out:
        with connect(current_db) as src:
            for row in src.select():
                out.write(
                    row.toatoms(),
                    key_value_pairs=dict(row.key_value_pairs),
                    data=dict(row.data),
                )
                current_count += 1
        with connect(labeled_db) as src:
            for row in src.select():
                out.write(
                    row.toatoms(),
                    key_value_pairs=dict(row.key_value_pairs),
                    data=dict(row.data),
                )
                labeled_count += 1

    log(
        f"merged current={current_count} labeled={labeled_count} "
        f"total={current_count + labeled_count} -> {updated_db}"
    )
    return current_count, labeled_count


def add_prepare_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--tag", help="ASE DB tag for collected rows; default is input_dir basename.")
    parser.add_argument("--potcar-root", type=Path, default=DEFAULT_POTCAR_ROOT)
    parser.add_argument("--potcar-map", action="append", type=parse_potcar_map, default=[],
                        metavar="ELEMENT=SETUP_DIR")
    parser.add_argument("--incar-template", type=Path,
                        help="Use this INCAR text instead of built-in defaults.")
    parser.add_argument("--kspacing", type=float, default=DEFAULT_KSPACING)
    parser.add_argument("--encut", type=float,
                        help="Explicit VASP ENCUT in eV; default is auto.")
    parser.add_argument("--encut-factor", type=float, default=DEFAULT_ENCUT_FACTOR,
                        help="Default ENCUT is this factor times max ENMAX from the selected POTCARs.")
    parser.add_argument("--npar", type=int)
    parser.add_argument("--magmom", default="_",
                        help="'_' means omit MAGMOM; otherwise write raw MAGMOM value.")
    parser.add_argument("--set", dest="incar_set", action="append", type=parse_incar_set,
                        default=[], metavar="KEY=VALUE",
                        help="Override/add an INCAR tag; may be repeated.")
    parser.add_argument("--force", action="store_true",
                        help="Rewrite existing prepared task inputs.")


def add_prepare_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("input_dir", type=Path, help="Directory containing *.poscar structures.")
    parser.add_argument("run_dir", type=Path, help="Directory for per-structure VASP tasks.")
    add_prepare_common_options(parser)


def add_run_common_options(parser: argparse.ArgumentParser, include_force: bool = True) -> None:
    parser.add_argument("--cores-per-job", type=int, default=DEFAULT_CORES_PER_JOB)
    parser.add_argument("--max-workers", type=int)
    parser.add_argument("--vasp-command", default="vasp_std")
    parser.add_argument("--progress-interval", type=float, default=60.0,
                        help="Seconds between live progress-bar snapshots while VASP tasks run; 0 disables periodic updates.")
    parser.add_argument("--keep-chgcar", action="store_true")
    if include_force:
        parser.add_argument("--force", action="store_true",
                            help="Run tasks even if OUTCAR already looks complete.")


def add_run_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("run_dir", type=Path, help="Prepared VASP task root.")
    add_run_common_options(parser)


def add_collect_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("run_dir", type=Path, help="Prepared/completed VASP task root.")
    parser.add_argument("output_db", type=Path, help="ASE DB containing labeled new structures.")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--skip-incomplete", action="store_true")
    parser.add_argument("--tag", help="Override DB tag for collected rows.")


def command_prepare(args: argparse.Namespace) -> None:
    potcar_provider = PotcarProvider(args.potcar_root.resolve(), dict(args.potcar_map))
    manifest = prepare_batch(
        input_dir=args.input_dir,
        run_dir=args.run_dir,
        args=args,
        potcar_provider=potcar_provider,
        tag=args.tag,
        force=args.force,
    )
    log(
        f"prepared={manifest['prepared']} reused={manifest['reused']} "
        f"tasks={manifest['task_count']} run_dir={manifest['run_dir']}"
    )


def command_run(args: argparse.Namespace) -> None:
    run_batch(
        run_dir=args.run_dir,
        cores_per_job=args.cores_per_job,
        max_workers=args.max_workers,
        vasp_command=args.vasp_command,
        keep_chgcar=args.keep_chgcar,
        force=args.force,
        progress_interval=args.progress_interval,
    )


def command_collect(args: argparse.Namespace) -> None:
    collect_results(
        run_dir=args.run_dir,
        output_db=args.output_db,
        overwrite=args.overwrite,
        skip_incomplete=args.skip_incomplete,
        tag=args.tag,
    )


def command_label(args: argparse.Namespace) -> None:
    potcar_provider = PotcarProvider(args.potcar_root.resolve(), dict(args.potcar_map))
    manifest = prepare_batch(
        input_dir=args.input_dir,
        run_dir=args.work_dir,
        args=args,
        potcar_provider=potcar_provider,
        tag=args.tag,
        force=args.force,
    )
    log(
        f"prepared={manifest['prepared']} reused={manifest['reused']} "
        f"tasks={manifest['task_count']} work_dir={manifest['run_dir']}"
    )
    if args.prepare_only:
        log("prepare-only requested; VASP was not launched and no DB was written.")
        return
    run_batch(
        run_dir=args.work_dir,
        cores_per_job=args.cores_per_job,
        max_workers=args.max_workers,
        vasp_command=args.vasp_command,
        keep_chgcar=args.keep_chgcar,
        force=args.force,
        progress_interval=args.progress_interval,
    )
    collect_results(
        run_dir=args.work_dir,
        output_db=args.output_db,
        overwrite=args.overwrite,
        skip_incomplete=False,
        tag=args.tag,
    )


def command_merge(args: argparse.Namespace) -> None:
    merge_databases(
        current_db=args.current_db,
        labeled_db=args.labeled_db,
        updated_db=args.updated_db,
        overwrite=args.overwrite,
    )


def validate_args(args: argparse.Namespace) -> None:
    if hasattr(args, "encut") and args.encut is not None and args.encut <= 0:
        raise ValueError("--encut must be positive")
    if hasattr(args, "encut_factor") and args.encut_factor <= 0:
        raise ValueError("--encut-factor must be positive")
    if hasattr(args, "kspacing") and args.kspacing is not None and args.kspacing <= 0:
        raise ValueError("--kspacing must be positive")
    if hasattr(args, "npar") and args.npar is not None and args.npar <= 0:
        raise ValueError("--npar must be positive")
    extra_keys = {
        key.upper()
        for key, _ in (getattr(args, "incar_set", []) or [])
    }
    if "NCORE" in extra_keys and (
        "NPAR" in extra_keys or getattr(args, "npar", None) is not None
    ):
        raise ValueError("Set either NCORE or NPAR, not both")
    if hasattr(args, "cores_per_job") and args.cores_per_job <= 0:
        raise ValueError("--cores-per-job must be positive")
    if hasattr(args, "max_workers") and args.max_workers is not None and args.max_workers <= 0:
        raise ValueError("--max-workers must be positive")
    if hasattr(args, "progress_interval") and args.progress_interval < 0:
        raise ValueError("--progress-interval must be >= 0")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare/run/collect VASP static calculations and merge labeled "
            "ASE DBs for the active-learning workflow."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="Prepare VASP task folders only.")
    add_prepare_options(prepare)
    prepare.set_defaults(func=command_prepare)

    run = subparsers.add_parser("run", help="Run prepared VASP task folders with srun.")
    add_run_options(run)
    run.set_defaults(func=command_run)

    collect = subparsers.add_parser("collect", help="Collect completed VASP results into ASE DB.")
    add_collect_options(collect)
    collect.set_defaults(func=command_collect)

    label = subparsers.add_parser("label", help="Prepare, run, and collect a POSCAR batch.")
    label.add_argument("input_dir", type=Path, help="Directory containing *.poscar structures.")
    label.add_argument("output_db", type=Path, help="ASE DB containing labeled new structures.")
    label.add_argument("--work-dir", type=Path, required=True,
                       help="Directory for per-structure VASP tasks.")
    label.add_argument("--prepare-only", action="store_true",
                       help="Only write POSCAR/INCAR/POTCAR task folders.")
    label.add_argument("--overwrite", action="store_true",
                       help="Overwrite output_db during collection.")
    add_prepare_common_options(label)
    add_run_common_options(label, include_force=False)
    label.set_defaults(func=command_label)

    merge = subparsers.add_parser("merge", help="Append labeled DB rows to current.db.")
    merge.add_argument("current_db", type=Path)
    merge.add_argument("labeled_db", type=Path)
    merge.add_argument("updated_db", type=Path)
    merge.add_argument("--overwrite", action="store_true")
    merge.set_defaults(func=command_merge)

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        validate_args(args)
        args.func(args)
    except Exception as exc:  # noqa: BLE001 - CLI should print concise failure
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
