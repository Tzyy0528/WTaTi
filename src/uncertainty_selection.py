import os
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from ase.geometry import wrap_positions
from ase.io import iread, write


def log(message):
    print(message, flush=True)


def set_default_thread_limits():
    """Avoid oversubscribing CPU threads when several selection workers run."""
    thread_vars = (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    )
    for name in thread_vars:
        os.environ.setdefault(name, "1")


def build_calculators(jnn_paths):
    try:
        from jsex.nnap import NNAP
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Uncertainty selection requires the Python module 'jsex.nnap'. "
            "Run selection with the JSE/NNAP Python environment that provides jsex."
        ) from exc

    calculators = []
    for path in jnn_paths:
        potential = NNAP(str(path))
        calculators.append(
            potential.ase() if hasattr(potential, "ase") else potential.asAseCalculator()
        )
    return calculators


def committee_forces(atoms, calculators):
    """计算所有 committee calculator 给出的力。"""
    forces = []
    for calc in calculators:
        atoms.calc = calc
        forces.append(atoms.get_forces())
    return np.array(forces)


def uncertainty_and_max_force(atoms, calculators):
    """Compute max per-atom committee force covariance uncertainty."""
    forces = committee_forces(atoms, calculators)
    model_count = forces.shape[0]
    if model_count < 2:
        raise ValueError("Committee uncertainty requires at least two calculators")

    force_mean = forces.mean(axis=0)
    force_diff = forces - force_mean[None, :, :]
    covariance_trace = np.sum(force_diff * force_diff, axis=(0, 2)) / (model_count - 1)
    per_atom_uncertainty = np.sqrt(covariance_trace)
    uncertainty = per_atom_uncertainty.max()
    max_force = np.linalg.norm(forces[0], axis=1).max()
    return uncertainty, max_force


def choose_selection_workers(args, trajectory_count):
    requested = getattr(args, "selection_workers", 0)
    if requested is None:
        requested = 0
    if requested < 0:
        raise ValueError("selection-workers must be >= 0")
    if trajectory_count <= 0:
        return 1
    if requested != 1 and running_under_jvm():
        log(
            "Uncertainty selection: JVM/JSE interpreter detected; "
            "using serial workers=1 to avoid fork-based multiprocessing deadlock"
        )
        return 1
    if requested == 0:
        return max(1, min(trajectory_count, os.cpu_count() or trajectory_count))
    return max(1, min(requested, trajectory_count))


def running_under_jvm():
    """JSE runs Python inside a JVM; forking it can deadlock child workers."""
    candidates = [Path(sys.executable).name.lower()]
    try:
        candidates.append(Path(os.readlink("/proc/self/exe")).name.lower())
    except OSError:
        pass
    return any(name.startswith("java") for name in candidates)


def job_payloads(jobs, jnn_paths, args, tmp_root):
    payloads = []
    for job_index, job in enumerate(jobs):
        xyz_path = job.work_dir / job.trajectory
        if not xyz_path.exists():
            raise FileNotFoundError(f"Missing trajectory: {xyz_path}")
        payloads.append(
            {
                "job_index": job_index,
                "xyz_path": str(xyz_path),
                "jnn_paths": [str(path) for path in jnn_paths],
                "u_min": args.u_min,
                "u_max": args.u_max,
                "progress_interval": getattr(args, "selection_progress_interval", 500),
                "tmp_dir": str(tmp_root / f"job_{job_index:04d}"),
            }
        )
    return payloads


def select_trajectory(payload):
    """Worker: scan one trajectory and write selected frames to temporary files."""
    set_default_thread_limits()
    calculators = build_calculators(payload["jnn_paths"])
    xyz_path = Path(payload["xyz_path"])
    tmp_dir = Path(payload["tmp_dir"])
    tmp_dir.mkdir(parents=True, exist_ok=True)

    records = []
    frames_seen = 0
    progress_interval = payload.get("progress_interval", 500)
    for frame_id, atoms in enumerate(iread(str(xyz_path), index=":")):
        frames_seen += 1
        positions = wrap_positions(atoms.get_positions(),
                                   atoms.get_cell(),
                                   atoms.get_pbc())
        atoms.set_positions(positions)
        uncertainty, max_force = uncertainty_and_max_force(atoms, calculators)
        if payload["u_min"] <= uncertainty <= payload["u_max"]:
            tmp_path = tmp_dir / f"frame_{frame_id:08d}.poscar"
            write(tmp_path, atoms, format="vasp")
            records.append(
                {
                    "frame_id": frame_id,
                    "uncertainty": uncertainty,
                    "max_force": max_force,
                    "tmp_path": str(tmp_path),
                }
            )
        if progress_interval and frames_seen % progress_interval == 0:
            log(
                f"selection progress trajectory {payload['job_index'] + 1}: "
                f"frames={frames_seen} selected={len(records)} path={xyz_path}"
            )

    return {
        "job_index": payload["job_index"],
        "xyz_path": str(xyz_path),
        "frames_seen": frames_seen,
        "records": records,
    }


def run_selection_workers(payloads, workers):
    if workers == 1:
        results = []
        for payload in payloads:
            result = select_trajectory(payload)
            log(
                f"selection done trajectory {result['job_index'] + 1}/{len(payloads)}: "
                f"frames={result['frames_seen']} selected={len(result['records'])} "
                f"path={result['xyz_path']}"
            )
            results.append(result)
        return results

    results = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        future_map = {
            executor.submit(select_trajectory, payload): payload
            for payload in payloads
        }
        for future in as_completed(future_map):
            result = future.result()
            log(
                f"selection done trajectory {result['job_index'] + 1}/{len(payloads)}: "
                f"frames={result['frames_seen']} selected={len(result['records'])} "
                f"path={result['xyz_path']}"
            )
            results.append(result)
    return results


def select_structures(round_dir, jobs, jnn_paths, args):
    """筛选不确定度落在指定窗口内的轨迹帧。"""
    set_default_thread_limits()
    selected_dir = round_dir / "selected-poscar"
    selected_dir.mkdir(parents=True, exist_ok=True)
    for old_path in selected_dir.glob("*.poscar"):
        old_path.unlink()
    old_summary = selected_dir / "selection_summary.dat"
    if old_summary.exists():
        old_summary.unlink()
    summary_path = round_dir / "selection_summary.dat"
    if summary_path.exists():
        summary_path.unlink()

    tmp_root = selected_dir / ".tmp_selection"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True)

    payloads = job_payloads(jobs, jnn_paths, args, tmp_root)
    workers = choose_selection_workers(args, len(payloads))
    log(
        f"Uncertainty selection: trajectories={len(payloads)} "
        f"workers={workers} committee={len(jnn_paths)}"
    )

    selected = []
    counter = 1
    try:
        results = run_selection_workers(payloads, workers)
        results.sort(key=lambda item: item["job_index"])
        with open(summary_path, "w", encoding="utf-8") as summary:
            summary.write("# file frame uncertainty_eVA max_force_eVA\n")
            for result in results:
                records = sorted(result["records"], key=lambda item: item["frame_id"])
                for record in records:
                    out_path = selected_dir / f"{counter:06d}.poscar"
                    shutil.move(record["tmp_path"], out_path)
                    selected.append(out_path)
                    summary.write(
                        f"{out_path.name} {record['frame_id']:d} "
                        f"{record['uncertainty']:.8f} {record['max_force']:.8f}\n"
                    )
                    counter += 1
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    log(f"Selected {len(selected)} structures in {selected_dir}")
    return selected
