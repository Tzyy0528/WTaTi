# Notes

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
