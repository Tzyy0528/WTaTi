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

## Selection After MD

```text
all-frame committee scoring
-> calibrated absolute-U lower cutoff
-> current.db-projected CUR
-> Protocol-A DFT labels
```

Run `src/stratified_uncertainty_selection.py --score-only` for the first
step. It writes the all-frame CSV and equilibration-discard flags without
creating percentile-bin POSCAR candidates or candidate summary files.

The DFT budget and `U_min` are calibrated from the element-local production
pool. Source quotas, frame gaps, physical-risk thresholds, and tail caps are
not active selection constraints.

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

## Completed Scoring, Calibration, and CUR Selection

| Element | Score job | CUR job | `U_min` (eV/A) | Candidate pool | CUR selected |
|---|---:|---:|---:|---:|---:|
| W | 13011 | 13017 | 6.730613322 | 1,126 | 100 |
| Ta | 13012 | 13018 | 3.496426176 | 1,126 | 100 |
| Ti | 13013 | 13019 | 5.933101487 | 1,126 | 100 |

All six jobs completed with exit code 0. Each scoring job evaluated all 25,005
frames with its own ten-model M0 committee. It marked the first 500 frames of
each scale source as equilibration, leaving 22,505 production frames.

For each element, `U_min` is the 95th percentile of the post-equilibration
committee-uncertainty distribution. This is an element-local absolute cutoff,
not a percentile-bin selection: every frame at or above the recorded numeric
cutoff formed the CUR candidate pool. The cutoff, source counts, and descriptor
parameters are recorded in `<X>-potential/01-nvt-round-1/uncertainty_calibration.json`.

CUR used `target=100`, `r_c=6.0`, `n_max=5`, `l_max=6`, similarity threshold
`0.99999`, no source balancing, no frame gaps, and no tail cap. Final source
counts were:

| Element | `scale-0p9` | `scale-0p95` | `scale-1` | `scale-1p05` | `scale-1p1` |
|---|---:|---:|---:|---:|---:|
| W | 2 | 1 | 2 | 8 | 87 |
| Ta | 28 | 6 | 3 | 10 | 53 |
| Ti | 43 | 8 | 1 | 10 | 38 |

The protected CUR roots contain candidate and selected POSCARs plus
`selection_summary.csv`, `cur_selected_distribution.csv`, and
`selection_parameters.txt`. Validation confirmed 1,126 finite unary
16-atom candidates and 100 finite, unique selected structures for every
element; each `current.db` remains unchanged at 100 unary rows.
