# Notes: EOS Preparation: W, Ta, and Ti

This record groups the common workflow stage only. W, Ta, and Ti data, calculations, and outputs remain strictly independent.

## W

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

## Ta

The Ta EOS inputs passed ASE/JSE checks.

| Phase | Source | Atoms | Volume (A^3) |
|---|---|---:|---:|
| bcc | `structures/Ta_benchmark/Ta-bcc.poscar` | 2 | 36.25994548 |
| fcc | `structures/Ta_benchmark/Ta-fcc.poscar` | 4 | 72.60625966 |
| hcp | `structures/Ta_benchmark/Ta-hcp.poscar` | 2 | 37.63704314 |

EOS convention: static uniform cell scaling with fixed cell shape and fixed
fractional coordinates; no ionic or cell relaxation.

All three Ta phases above are mandatory EOS-validation inputs and will be
scaled/labeled separately.

The user approved a common 19-point lattice-scale grid from 0.97 to 1.03.
On 2026-07-21, 57 Ta EOS POSCARs were generated: 19 each for bcc, fcc, and
hcp. The metadata is
`results/Ta_eos_benchmark/eos_reference/eos_structures.csv`.

The user approved the VASP batch backend defaults as Protocol B and approved
default SLURM partition/account/walltime behavior. The planned submission is
three independent phase jobs, each with the template default of one node and
64 tasks; no overwrite option will be used.

Submitted 2026-07-21:

| Phase | SLURM job ID | Output DB |
|---|---:|---|
| bcc | 12451 | `results/Ta_eos_benchmark/eos_reference/Ta_eos_dft_bcc.db` |
| fcc | 12452 | `results/Ta_eos_benchmark/eos_reference/Ta_eos_dft_fcc.db` |
| hcp | 12453 | `results/Ta_eos_benchmark/eos_reference/Ta_eos_dft_hcp.db` |

All three jobs were pending in the default `batch` partition with reason
`Priority` immediately after submission. No DFT database existed at that time.

All jobs completed with exit code 0:

| Phase | SLURM job ID | Elapsed |
|---|---:|---:|
| bcc | 12451 | 00:00:46 |
| fcc | 12452 | 00:00:58 |
| hcp | 12453 | 00:01:01 |

Each phase DB contains exactly 19 Ta-only rows with finite energy, forces, and
stress. `eos_reference.csv` contains 57 matched rows (19 per phase) with
finite DFT energy fields.

| Asset | SHA-256 |
|---|---|
| `eos_structures.csv` | `16d5f83cd5a994109b17a66846a5091a718cfb6ce61d7f13f19a6e543222dc4f` |
| `eos_reference.csv` | `869d901829f0682cb169923b1f0745e8e7503cff5385efb2a84bc53c1a06f4ab` |
| `Ta_eos_dft_bcc.db` | `ff8b82ce3c18190540113f5ebda7f81a697559de9720fa88cf442c1957a9dbfd` |
| `Ta_eos_dft_fcc.db` | `e7cb8171a8272fb63eb694b88ae6684a9ec9010e7184354c23bcd24429bbf65e` |
| `Ta_eos_dft_hcp.db` | `fe95f51c8cb79513af47f51e50562c4f4230e2950c570cf83d8c8b140e46adad` |

## Ti

The Ti EOS inputs passed ASE/JSE checks.

| Phase | Source | Atoms | Volume (A^3) |
|---|---|---:|---:|
| bcc | `structures/Ti_benchmark/Ti-bcc.poscar` | 2 | 34.37999012 |
| fcc | `structures/Ti_benchmark/Ti-fcc.poscar` | 4 | 69.38341830 |
| hcp | `structures/Ti_benchmark/Ti-hcp.poscar` | 2 | 34.63869562 |

EOS convention: static uniform cell scaling with fixed cell shape and fixed
fractional coordinates; the input hcp c/a remains fixed.

All three Ti phases above are mandatory EOS-validation inputs and will be
scaled/labeled separately.

The user approved a common 19-point lattice-scale grid from 0.97 to 1.03.
On 2026-07-21, 57 Ti EOS POSCARs were generated: 19 each for bcc, fcc, and
hcp. The metadata is
`results/Ti_eos_benchmark/eos_reference/eos_structures.csv`.

The user approved the VASP batch backend defaults as Protocol B and approved
default SLURM partition/account/walltime behavior. The planned submission is
three independent phase jobs, each with the template default of one node and
64 tasks; no overwrite option will be used.

Submitted 2026-07-21:

| Phase | SLURM job ID | Output DB |
|---|---:|---|
| bcc | 12454 | `results/Ti_eos_benchmark/eos_reference/Ti_eos_dft_bcc.db` |
| fcc | 12455 | `results/Ti_eos_benchmark/eos_reference/Ti_eos_dft_fcc.db` |
| hcp | 12456 | `results/Ti_eos_benchmark/eos_reference/Ti_eos_dft_hcp.db` |

All three jobs were pending in the default `batch` partition with reason
`Priority` immediately after submission. No DFT database existed at that time.

All jobs completed with exit code 0:

| Phase | SLURM job ID | Elapsed |
|---|---:|---:|
| bcc | 12454 | 00:00:24 |
| fcc | 12455 | 00:02:22 |
| hcp | 12456 | 00:02:20 |

Each phase DB contains exactly 19 Ti-only rows with finite energy, forces, and
stress. `eos_reference.csv` contains 57 matched rows (19 per phase) with
finite DFT energy fields.

| Asset | SHA-256 |
|---|---|
| `eos_structures.csv` | `3c11ea72890c9d0a1f336b7b609190b980fafdc8878c55d7af74d4cff0ad5ffb` |
| `eos_reference.csv` | `1a5f38ae444e9412c9bb0d5cfa5c15e0af89b1af3e1f675892276c6c3c93a541` |
| `Ti_eos_dft_bcc.db` | `5b4938e8e592aed17b8f93c5f126281ba90a11e897ddb02cc11b890bf79396b5` |
| `Ti_eos_dft_fcc.db` | `d6662734db883d2ae93660274e53237a5a34c37ed06f457c10eb008e7829f698` |
| `Ti_eos_dft_hcp.db` | `0baae66dee950316ba31cbdd862eff71a659e0ccc2263be629eb8a76ee7f205d` |
