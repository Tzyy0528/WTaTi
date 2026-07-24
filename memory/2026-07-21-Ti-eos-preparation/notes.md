# Notes

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
