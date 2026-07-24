# Notes

The W EOS inputs passed ASE/JSE checks.

| Phase | Source | Atoms | Volume (A^3) |
|---|---|---:|---:|
| bcc | `structures/W_benchmark/W-bcc.poscar` | 2 | 31.86452704 |
| fcc | `structures/W_benchmark/W-fcc.poscar` | 4 | 63.61573960 |
| hcp | `structures/W_benchmark/W-hcp.poscar` | 2 | 33.22780109 |

EOS convention: static uniform cell scaling with fixed cell shape and fixed
fractional coordinates; no ionic or cell relaxation.

All three W phases above are mandatory EOS-validation inputs and will be
scaled/labeled separately.

The user approved a common 19-point lattice-scale grid from 0.97 to 1.03.
On 2026-07-21, 57 W EOS POSCARs were generated: 19 each for bcc, fcc, and
hcp. The metadata is
`results/W_eos_benchmark/eos_reference/eos_structures.csv`.

The user approved the VASP batch backend defaults as Protocol B and approved
default SLURM partition/account/walltime behavior. The planned submission is
three independent phase jobs, each with the template default of one node and
64 tasks; no overwrite option will be used.

Submitted 2026-07-21:

| Phase | SLURM job ID | Output DB |
|---|---:|---|
| bcc | 12448 | `results/W_eos_benchmark/eos_reference/W_eos_dft_bcc.db` |
| fcc | 12449 | `results/W_eos_benchmark/eos_reference/W_eos_dft_fcc.db` |
| hcp | 12450 | `results/W_eos_benchmark/eos_reference/W_eos_dft_hcp.db` |

All three jobs were pending in the default `batch` partition with reason
`Priority` immediately after submission. No DFT database existed at that time.

All jobs completed with exit code 0:

| Phase | SLURM job ID | Elapsed |
|---|---:|---:|
| bcc | 12448 | 00:01:11 |
| fcc | 12449 | 00:01:03 |
| hcp | 12450 | 00:01:05 |

Each phase DB contains exactly 19 W-only rows with finite energy, forces, and
stress. `eos_reference.csv` contains 57 matched rows (19 per phase) with
finite DFT energy fields.

| Asset | SHA-256 |
|---|---|
| `eos_structures.csv` | `d0fa9889b18797990d33114f91850c3710ee9b7b0c40856733cbdec392fa4a3d` |
| `eos_reference.csv` | `d4360e843da262499a202613704cc73b483e3f74d8a016282da8d7179b512f64` |
| `W_eos_dft_bcc.db` | `728eea931f56c1cd5f26d0362caecdef74ce8c2064ee9bcfe59693cdd7225852` |
| `W_eos_dft_fcc.db` | `fce41e14612a350549c30ea469317807131cd5cbc995c5548bc53a101c5d2cf5` |
| `W_eos_dft_hcp.db` | `644bac3dd4fd53146d1555fb9eac1c2d1ad785017956bef10c743eea39b02e23` |
