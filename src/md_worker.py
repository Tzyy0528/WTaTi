import argparse
import math
import os
import shlex
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from ase import units
from ase.calculators.calculator import Calculator, all_changes
from ase.geometry import cell_to_cellpar, cellpar_to_cell
from ase.io import read, write
from ase.md.langevin import Langevin
from ase.md.npt import NPT
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution, Stationary


@dataclass
class MDJob:
    """描述一个 NVT 或 NPT 采样任务。"""
    ensemble: str
    label: str
    work_dir: Path
    temperature: float
    trajectory: str = "multi_nnap_md.xyz"
    scale_factor: float = 1.0
    pressure: float = 0.0


def format_value(value):
    """将数值格式化为适合目录名的字符串。"""
    return f"{value:g}".replace("-", "m").replace(".", "p")


def build_md_jobs(round_dir, ensemble, temperature, args):
    """为当前轮次生成 NVT 缩放或 NPT 压力 MD 任务。"""
    md_root = round_dir / "md"
    jobs = []
    if ensemble == "nvt":
        for scale_factor in args.scale_factors:
            label = f"scale-{format_value(scale_factor)}"
            jobs.append(MDJob(
                ensemble="nvt",
                label=label,
                work_dir=md_root / label,
                temperature=temperature,
                scale_factor=scale_factor,
            ))
    else:
        for pressure in args.pressures:
            label = f"P-{format_value(pressure)}GPa"
            jobs.append(MDJob(
                ensemble="npt",
                label=label,
                work_dir=md_root / label,
                temperature=temperature,
                pressure=pressure,
            ))
    return jobs


def md_command(job, args, worker_script, poscar, jnn_paths):
    """构建单个 MD 子进程命令。"""
    cmd = [
        args.runner,
        str(worker_script),
        "--ensemble", job.ensemble,
        "--work-dir", str(job.work_dir),
        "--poscar", str(poscar),
        "--rep", *[str(value) for value in args.md_rep],
        "--temperature", str(job.temperature),
        "--tau-r", str(args.tau_r),
        "--steps", str(args.steps),
        "--timestep", str(args.timestep),
        "--write-interval", str(args.write_interval),
        "--log-interval", str(args.log_interval),
        "--trajectory", job.trajectory,
        "--summary", "energy_forces_summary.dat",
    ]
    if job.ensemble == "nvt":
        cmd += ["--scale-factor", str(job.scale_factor),
                "--friction", str(args.friction)]
    else:
        cmd += [
            "--pressure", str(job.pressure),
            "--ttime", str(args.ttime),
            "--ptime", str(args.ptime),
            "--bulk-modulus-gpa", str(args.bulk_modulus_gpa),
            "--frac-traceless", str(args.frac_traceless),
        ]
        if args.pfactor is not None:
            cmd += ["--pfactor", str(args.pfactor)]
    cmd += ["--jnn-paths"] + [str(path) for path in jnn_paths]
    return cmd


def run_one_md_job(job, args, worker_script, poscar, jnn_paths):
    """运行单个 MD 任务并记录命令和日志。"""
    job.work_dir.mkdir(parents=True, exist_ok=True)
    cmd = md_command(job, args, worker_script, poscar, jnn_paths)

    command_text = " ".join(shlex.quote(part) for part in cmd)
    (job.work_dir / "command.sh").write_text(command_text + "\n", encoding="utf-8")

    with open(job.work_dir / "log", "w", encoding="utf-8") as log:
        subprocess.run(cmd, cwd=job.work_dir, stdout=log,
                       stderr=subprocess.STDOUT, text=True, check=True)
    return job


def run_md_jobs(jobs, args, worker_script, poscar, jnn_paths):
    """按限定并行度运行所有 MD 任务。"""
    if not jobs:
        return

    max_workers = max(1, min(args.max_md_workers, len(jobs)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(run_one_md_job, job, args, worker_script, poscar,
                            jnn_paths)
            for job in jobs
        ]
        for future in as_completed(futures):
            job = future.result()
            print(f"Finished {job.ensemble.upper()} MD: {job.label}")


class XYZWriter:
    """将 MD 轨迹帧追加写入 extxyz 文件。"""
    def __init__(self, filename):
        """保存目标轨迹文件路径。"""
        self.filename = filename
        self.append = False

    def write(self, atoms):
        """将一帧 ASE Atoms 追加到轨迹文件。"""
        write(self.filename, atoms, format="extxyz", append=self.append)
        self.append = True


def build_calculator(jnn_paths, tau_r, compute_stress):
    """创建带 HAL 偏置的多 NNAP ASE calculator。"""
    try:
        from jsex.nnap import NNAP
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "NNAP MD requires the Python module 'jsex.nnap'. "
            "Run MD with the JSE/NNAP Python environment that provides jsex."
        ) from exc

    class MultiNNAPCalculator(Calculator):
        """对 NNAP committee 求平均并施加 HAL 偏置的 ASE calculator。"""
        implemented_properties = ["energy", "forces", "energies", "stress"]

        def __init__(self, calculators, tau_r=0.1, lambda_reg=1e-5,
                     compute_stress=False, **kwargs):
            """保存 committee calculator 与 HAL 偏置参数。"""
            super().__init__(**kwargs)
            self.calcs = calculators
            self.K = len(calculators)
            self.tau_r = tau_r
            self.lambda_reg = lambda_reg
            self.compute_stress = compute_stress

        def calculate(self, atoms=None, properties=("energy", "forces"),
                      system_changes=all_changes):
            """汇总 committee 结果并添加 HAL 偏置力。"""
            super().calculate(atoms, properties, system_changes)

            n_atoms = len(atoms)
            need_stress = self.compute_stress or "stress" in properties
            calc_properties = ["energy", "forces"]
            if need_stress:
                calc_properties.append("stress")

            energies = np.zeros(self.K)
            forces = np.zeros((self.K, n_atoms, 3))
            stresses = np.zeros((self.K, 6))
            atom_energies = np.zeros((self.K, n_atoms))
            has_atom_energies = True

            for i, calc in enumerate(self.calcs):
                calc.calculate(atoms, properties=calc_properties,
                               system_changes=all_changes)

                if "energy" not in calc.results or "forces" not in calc.results:
                    raise RuntimeError("NNAP calculator did not return energy/forces")

                energies[i] = calc.results["energy"]
                forces[i] = calc.results["forces"]

                if need_stress:
                    if "stress" not in calc.results:
                        raise RuntimeError(
                            "NPT requires stress, but an NNAP model did not "
                            "return stress"
                        )
                    stresses[i] = calc.results["stress"]

                if "energies" in calc.results:
                    atom_energies[i] = calc.results["energies"]
                else:
                    has_atom_energies = False

            energy_avg = energies.mean()
            force_avg = forces.mean(axis=0)

            var_energy = ((energies - energy_avg) ** 2).mean()
            sigma = np.sqrt(self.lambda_reg + var_energy)

            grad_sigma2 = np.zeros((n_atoms, 3))
            for k in range(self.K):
                grad_sigma2 += (energies[k] - energy_avg) * (force_avg - forces[k])
            grad_sigma2 *= 2.0 / self.K
            grad_sigma = grad_sigma2 / (2.0 * sigma)

            norm_force = np.sum(np.linalg.norm(force_avg, axis=1))
            norm_grad = np.sum(np.linalg.norm(grad_sigma, axis=1)) + 1e-12
            tau = self.tau_r * (norm_force / norm_grad)

            self.results["energy"] = energy_avg
            self.results["forces"] = force_avg + tau * grad_sigma
            if need_stress:
                self.results["stress"] = stresses.mean(axis=0)
            if has_atom_energies:
                self.results["energies"] = atom_energies.mean(axis=0)

    calc_list = [NNAP(jnn_path).asAseCalculator() for jnn_path in jnn_paths]
    return MultiNNAPCalculator(calc_list, tau_r=tau_r,
                               compute_stress=compute_stress)


def temperature_from_kinetic_energy(atoms):
    """将原子动能换算为瞬时温度。"""
    return atoms.get_kinetic_energy() / (1.5 * units.kB * len(atoms))


def check_periodic_cell(atoms, ensemble):
    """确认结构具有可用于周期性 MD 的三维晶胞。"""
    if atoms.cell.rank < 3 or atoms.get_volume() <= 0:
        raise ValueError(f"{ensemble.upper()} MD requires a non-zero 3D cell")
    if ensemble == "npt" and not atoms.get_pbc().all():
        raise ValueError("NPT MD requires periodic boundary conditions in 3D")


def read_repeated_structure(poscar, rep):
    """Read an MD starting structure and repeat it along the cell axes."""
    atoms = read(poscar)
    return atoms.repeat(tuple(rep))


def npt_pfactor(args):
    """返回 ASE NPT 所需的 barostat 因子。"""
    if args.pfactor is not None:
        return args.pfactor
    bulk_modulus = args.bulk_modulus_gpa * units.GPa
    return (args.ptime * units.fs) ** 2 * bulk_modulus


def write_nvt_log(dyn, atoms, filename):
    """追加写入 NVT 热力学量和力诊断信息。"""
    step = dyn.get_number_of_steps()
    time_fs = dyn.get_time() / units.fs
    epot = atoms.get_potential_energy()
    ekin = atoms.get_kinetic_energy()
    forces = atoms.get_forces()
    force_norm = np.linalg.norm(forces, axis=1)

    if step % 10 == 0:
        print(f"Step {step:6d}: E_pot = {epot:12.6f} eV, "
              f"T = {temperature_from_kinetic_energy(atoms):8.1f} K")

    if step == 0 or not os.path.exists(filename):
        with open(filename, "w") as handle:
            handle.write("# Step Time_fs PotE_eV KinE_eV TotE_eV Temp_K "
                         "MaxF_eVA MeanF_eVA\n")

    with open(filename, "a") as handle:
        handle.write(
            f"{step:8d} {time_fs:12.3f} {epot:16.8f} {ekin:16.8f} "
            f"{epot + ekin:16.8f} {temperature_from_kinetic_energy(atoms):12.3f} "
            f"{force_norm.max():14.8f} {force_norm.mean():14.8f}\n"
        )


def write_npt_log(dyn, atoms, filename):
    """追加写入 NPT 热力学量、力和压力诊断信息。"""
    step = dyn.get_number_of_steps()
    time_fs = dyn.get_time() / units.fs
    epot = atoms.get_potential_energy()
    ekin = atoms.get_kinetic_energy()
    forces = atoms.get_forces()
    force_norm = np.linalg.norm(forces, axis=1)

    stress = atoms.get_stress(include_ideal_gas=True)
    ev_a3_to_gpa = 160.21766208
    px_gpa, py_gpa, pz_gpa = (-stress[:3]) * ev_a3_to_gpa
    press_gpa = (px_gpa + py_gpa + pz_gpa) / 3.0

    if step % 10 == 0:
        print(f"Step {step:6d}: E_pot = {epot:12.6f} eV, "
              f"T = {temperature_from_kinetic_energy(atoms):8.1f} K, "
              f"P = {press_gpa:10.3f} GPa")

    if step == 0 or not os.path.exists(filename):
        with open(filename, "w") as handle:
            handle.write("# Step Time_fs PotE_eV KinE_eV TotE_eV Temp_K "
                         "MaxF_eVA MeanF_eVA Px_GPa Py_GPa Pz_GPa Press_GPa\n")

    with open(filename, "a") as handle:
        handle.write(
            f"{step:8d} {time_fs:12.3f} {epot:16.8f} {ekin:16.8f} "
            f"{epot + ekin:16.8f} {temperature_from_kinetic_energy(atoms):12.3f} "
            f"{force_norm.max():14.8f} {force_norm.mean():14.8f} "
            f"{px_gpa:12.5f} {py_gpa:12.5f} {pz_gpa:12.5f} {press_gpa:12.5f}\n"
        )


def run_nvt(args):
    """运行一个 Langevin NVT MD 任务。"""
    atoms = read_repeated_structure(args.poscar, args.rep)
    check_periodic_cell(atoms, "nvt")
    atoms.set_cell(atoms.get_cell() * args.scale_factor, scale_atoms=True)
    atoms.calc = build_calculator(args.jnn_paths, args.tau_r,
                                  compute_stress=False)

    MaxwellBoltzmannDistribution(atoms, temperature_K=args.temperature,
                                 force_temp=True)
    Stationary(atoms)
    dyn = Langevin(atoms, args.timestep * units.fs,
                   temperature_K=args.temperature,
                   friction=args.friction / units.fs,
                   fixcm=False)

    xyz_writer = XYZWriter(args.trajectory)
    dyn.attach(lambda: xyz_writer.write(atoms), interval=args.write_interval)
    dyn.attach(lambda: write_nvt_log(dyn, atoms, args.summary),
               interval=args.log_interval)
    dyn.run(args.steps)


def run_npt(args):
    """运行一个 ASE NPT MD 任务。"""
    if args.pressure is None:
        raise ValueError("--pressure is required for NPT")

    atoms = read_repeated_structure(args.poscar, args.rep)
    check_periodic_cell(atoms, "npt")
    cellpar = cell_to_cellpar(atoms.cell)
    atoms.set_cell(cellpar_to_cell(cellpar), scale_atoms=True)
    atoms.wrap()
    atoms.calc = build_calculator(args.jnn_paths, args.tau_r,
                                  compute_stress=True)

    MaxwellBoltzmannDistribution(atoms, temperature_K=args.temperature,
                                 force_temp=True)
    Stationary(atoms)
    dyn = NPT(atoms, timestep=args.timestep * units.fs,
              temperature_K=args.temperature,
              externalstress=args.pressure * units.GPa,
              ttime=args.ttime * units.fs,
              pfactor=npt_pfactor(args),
              mask=(1, 1, 1))
    dyn.set_fraction_traceless(fracTraceless=args.frac_traceless)

    xyz_writer = XYZWriter(args.trajectory)
    dyn.attach(lambda: xyz_writer.write(atoms), interval=args.write_interval)
    dyn.attach(lambda: write_npt_log(dyn, atoms, args.summary),
               interval=args.log_interval)
    dyn.run(args.steps)


def parse_args():
    """解析单个 MD worker 的命令行参数。"""
    parser = argparse.ArgumentParser(description="Run one HAL-biased ASE MD job")
    parser.add_argument("--ensemble", choices=["nvt", "npt"], required=True)
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--poscar", required=True)
    parser.add_argument("--rep", nargs=3, type=int, default=[2, 2, 2],
                        metavar=("NX", "NY", "NZ"),
                        help="Repeat the starting POSCAR before MD")
    parser.add_argument("--jnn-paths", nargs="+", required=True)
    parser.add_argument("--temperature", type=float, required=True)
    parser.add_argument("--scale-factor", type=float, default=1.0)
    parser.add_argument("--pressure", type=float, help="NPT pressure in GPa")
    parser.add_argument("--tau-r", type=float, default=0.1)
    parser.add_argument("--steps", type=int, default=50000)
    parser.add_argument("--timestep", type=float, default=1.0,
                        help="Timestep in fs")
    parser.add_argument("--write-interval", type=int, default=10)
    parser.add_argument("--log-interval", type=int, default=1)
    parser.add_argument("--friction", type=float, default=0.02,
                        help="Langevin friction in fs^-1")
    parser.add_argument("--ttime", type=float, default=75.0,
                        help="NPT thermostat time in fs")
    parser.add_argument("--ptime", type=float, default=75.0,
                        help="NPT barostat time in fs")
    parser.add_argument("--bulk-modulus-gpa", type=float, default=100.0,
                        help="Bulk modulus used to derive NPT pfactor")
    parser.add_argument("--pfactor", type=float,
                        help="Override ASE NPT pfactor")
    parser.add_argument("--frac-traceless", type=float, default=0.05)
    parser.add_argument("--trajectory", default="multi_nnap_md.xyz")
    parser.add_argument("--summary", default="energy_forces_summary.dat")
    args = parser.parse_args()
    validate_args(args, parser)
    return args


def validate_args(args, parser):
    """检查单个 MD worker 的参数合法性。"""
    positive_ints = ["steps", "write_interval", "log_interval"]
    for name in positive_ints:
        if getattr(args, name) <= 0:
            parser.error(f"--{name.replace('_', '-')} must be positive")
    if any(value <= 0 for value in args.rep):
        parser.error("--rep values must be positive")

    positive_floats = [
        "temperature",
        "scale_factor",
        "timestep",
        "ttime",
        "ptime",
        "bulk_modulus_gpa",
    ]
    for name in positive_floats:
        value = getattr(args, name)
        if not math.isfinite(value) or value <= 0:
            parser.error(f"--{name.replace('_', '-')} must be positive")

    for name in ["tau_r", "friction"]:
        value = getattr(args, name)
        if not math.isfinite(value) or value < 0:
            parser.error(f"--{name.replace('_', '-')} must be non-negative")

    if args.pressure is not None and not math.isfinite(args.pressure):
        parser.error("--pressure must be finite")
    if args.pfactor is not None:
        if not math.isfinite(args.pfactor) or args.pfactor <= 0:
            parser.error("--pfactor must be positive")
    if not 0.0 <= args.frac_traceless <= 1.0:
        parser.error("--frac-traceless must be in [0, 1]")


def main():
    """单个 MD worker 的命令行入口。"""
    args = parse_args()
    args.work_dir = str(Path(args.work_dir).resolve())
    args.poscar = str(Path(args.poscar).resolve())
    args.jnn_paths = [str(Path(path).resolve()) for path in args.jnn_paths]

    os.makedirs(args.work_dir, exist_ok=True)
    os.chdir(args.work_dir)

    print(f"Starting {args.ensemble.upper()} biased MD")
    print(f"Temperature: {args.temperature:.3f} K")
    print(f"Starting structure repeat: {args.rep}")
    if args.ensemble == "nvt":
        print(f"Scale factor: {args.scale_factor}")
        run_nvt(args)
    else:
        print(f"Pressure: {args.pressure} GPa")
        run_npt(args)
    print("Finished MD")


if __name__ == "__main__":
    main()
