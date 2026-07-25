# Notes: D1 High-Temperature NVT

## Available Inputs

| Element | `current.db` | M0 committee | D1 output path |
|---|---|---|---|
| W | 100 rows | 10 JNN files | `W-potential/01-nvt-round-1/` validated |
| Ta | 100 rows | 10 JNN files | `Ta-potential/01-nvt-round-1/` validated |
| Ti | 100 rows | 10 JNN files | `Ti-potential/01-nvt-round-1/` validated |

Each sweep uses every JNN in its own element-local M0 committee:

```text
<X>-potential/model_versions/M0_from_D0/train-committee/train-*/*.jnn
```

## Sampling Configuration

The high-temperature targets come from
`src/temperature_table.py::make_temperatures([X], 1)`:

| Element | Temperature |
|---|---:|
| W | 4928.15 K |
| Ta | 4485.65 K |
| Ti | 2750.65 K |

All three elements use `--rep 2 2 2` and NVT scale factors
`0.90 0.95 1.00 1.05 1.100`. The standard worker settings are 50,000 steps,
1.0 fs timestep, trajectory write interval 10, log interval 1,
`--tau-r 0.10`, and `--friction 0.02`.

Random seeds are intentionally not fixed for exploratory MD.

## Current D1 Selection Policy

```text
all-frame committee scoring
-> log-derived absolute-U lower cutoff
-> current.db-projected CUR
-> Protocol-A DFT labels
```

Run `src/stratified_uncertainty_selection.py --score-only` for the first
step. It writes the all-frame CSV and equilibration-discard flags without
creating percentile-bin POSCAR candidates or candidate summary files.

For a given element, read the final right-hand (test) `MAE-F` value from each
of the ten M0 logs for the committee actually used in D1 MD. Convert the
explicitly approved aggregate from meV/A to eV/A and use that value as
`U_min`. A percentile of the MD pool is not a valid calibration rule.
Source quotas, frame gaps, physical-risk thresholds, and tail caps are not
active selection constraints unless separately approved.

## Execution Rule

Use the appropriate SLURM runner only after the exact command, allocation
resources, and new output paths are reviewed. Do not mix element paths,
committees, trajectories, or databases.

## Completed NVT Allocations and Validation

| Element | Job ID | State | Exit code | Scale sources |
|---|---:|---|---|---:|
| W | 13005 | COMPLETED | 0:0 | 5 |
| Ta | 13006 | COMPLETED | 0:0 | 5 |
| Ti | 13007 | COMPLETED | 0:0 | 5 |

The 15 source directories each contain nonempty `command.sh`, `log`,
`multi_nnap_md.xyz`, and `energy_forces_summary.dat` files. Every trajectory
contains 5,001 16-atom frames; every summary has 50,001 finite rows for steps
0 through 50,000. ASE parsing confirmed element-only symbols, finite
positions/cells/volumes/energies/forces, and positive cell volumes. Every log
ends with `Finished MD`.

The runs use protected, element-local output roots. Their exact per-source
commands are written under `<X>-potential/01-nvt-round-1/md/scale-*/command.sh`.
Do not resubmit into these directories.

## Completed Scoring and Revoked Historical Selection

Each scoring job evaluated all 25,005 frames with its own ten-model M0
committee. It marked the first 500 frames of each scale source as
equilibration, leaving 22,505 production frames.

The historical CUR jobs 13017--13019 used post-equilibration pool P95
cutoffs. That selection is invalid under the current rule and must not be
used. Its calibration JSON, CUR files, DFT labels, successors, M1/E1 outputs,
and D2 outputs are deleted during the D1 restart. The retained inputs are the
element-local MD trajectories and `uncertainty_all_frames.csv` files.

## D1 Restart Cleanup

The user-authorized cleanup completed on 2026-07-25. Before copying the D0
snapshots, the three `current.db` files contained 200 rows; each D0 snapshot
contained 100 rows. The restored `current.db` files each contain 100 rows and
have byte-identical SHA-256 hashes to their respective D0 snapshot.

Removed per element: the historical CUR root and calibration JSON, D1 DFT and
labeled DB files, D1 `updated.db`, M1, E1_M1, and the complete D2 root.
Removed memory records 08 through 15. D0, M0, E0, D1 MD trajectories, and D1
all-frame scoring CSVs remain intact.
