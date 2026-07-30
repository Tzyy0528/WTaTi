# Notes: Clean-FCC D4 Through DFT Submission

## Sources

### Source 1: User-authorized workflow
- Path: Conversation on 2026-07-29.
- Key points:
  - Reuse D3 NPT and selection policy for element-isolated D4.
  - Use M3 committees and newly recalibrated M3-log `U_min`.
  - Submit Protocol-A DFT after selection and stop monitoring at submission.

## Commands and Observations

```bash
# Targeted execution templates and D3 records inspected:
scripts/slurm/run_md_round.slurm
scripts/slurm/run_md_selection_pipeline.slurm
scripts/slurm/run_vasp_batch_dft.slurm
src/md_worker.py
memory/30_clean_fcc_D3_npt_launch/
memory/33_clean_fcc_D3_selection_acceptance_and_dft/
```

## Synthesized Findings

### Frozen D4 card recovered from D3

Each D4 command substitutes only its matching M3 committee and 400-row D3
`current.db`; it otherwise retains D3 NPT controls:

| Element | D4 root | Seed / rep | Temperature (K) | Pressures (GPa) |
|---|---|---|---:|---|
| W | `W-potential/fcc-restart/04-npt-round-2/` | `W-fcc-seed-32.poscar` / `1 1 1` | 4928.15 | `1,5,10,20,30,40,50` |
| Ta | `Ta-potential/fcc-restart/04-npt-round-2/` | `Ta-fcc-seed-32.poscar` / `1 1 1` | 4485.65 | `1,5,10,20,30,40,50` |
| Ti | `Ti-potential/fcc-restart/04-npt-round-2/` | `Ti-fcc-seed-32.poscar` / `1 1 1` | 2750.65 | `1,5,10,20,30,40,50` |

Common controls are NPT, 50,000 steps, 1.0 fs, write/log interval `10/1`,
HAL `tau_r=0.10`, `ttime=75.0` fs, `ptime=75.0` fs, bulk modulus `100.0`
GPa, and `frac_traceless=0.0`. Each job requests one node, seven one-core
tasks, and 24 hours. It passes exactly `train-0/0.jnn` through
`train-9/9.jnn` from only the matching M3 committee.

### D4 preflight acceptance

All three `fcc-restart/04-npt-round-2/` roots and every D4 later-stage path
(MD, selection, label DB, and VASP root) were absent. Existing non-FCC
`<X>-potential/04-npt-round-2/` roots are unrelated protected workflows and
are not inputs or outputs. The published D3 DB checksums and 400-row state
are unchanged, seeds are finite unary 32-atom 3D-PBC cells, and exactly ten
nonempty M3 JNNs plus logs exist per element. The stable M3 committee digest
is W `4b70e76b9c07d3941384e8186093b0a161fd9b99ae0a94c9803370ee2a52b757`,
Ta `271099ae358772212cbde93530d79ff7279e4d33e27ad316fe630abeb53b8b88`,
and Ti `f272715af70b61fa657a0a5fc13a404a7438e151aaebae22497d611ab6d91584`.

An all-model, no-write JSE/ASE preflight used `src.md_worker.build_calculator`
with one M3 JNN at a time, `compute_stress=True`, finite energy/force/stress
checks, and construction of the production ASE `NPT` integrator with the
frozen controls. All 30 models passed:

| Element | Models | Energy range (eV) | Diagonal-stress range (eV/A3) |
|---|---:|---:|---:|
| W | 10 / 10 | -400.66119304 to -400.43124751 | -0.04568763 to -0.03645136 |
| Ta | 10 / 10 | -371.31856070 to -371.12602131 | -0.03972718 to -0.03453513 |
| Ti | 10 / 10 | -246.70836257 to -246.59217017 | +0.00992183 to +0.01262923 |

JSE compiled normal local inference-cache libraries beside M3 JNNs during
the preflight; JNN content hashes remain unchanged. The deprecated
`asAseCalculator()` warning originates in the existing worker and does not
affect returned finite properties or NPT construction.

### D4 MD submissions

After a second no-overwrite guard, each otherwise-absent D4 root received only
its `slurm_logs/` directory and was submitted directly with `sbatch` rather
than the self-submit branch, so that element-local scheduler stdout/stderr
paths are retained. Each command uses the frozen D4 card above, seven tasks,
one node, and 24 hours, with all ten explicit matching M3 JNN paths:

| Element | D4 MD job | Immediate scheduler state |
|---|---:|---|
| W | `13546` | `RUNNING` on `lpsnode02` |
| Ta | `13547` | `RUNNING` on `lpsnode02` |
| Ti | `13548` | `RUNNING` on `lpsnode02` |

The requested active monitoring is now in effect. No D4 selection, DFT,
merge, M4, or E4 command has been submitted.

### D4 terminal MD acceptance

Active scheduler monitoring found all D4 MD allocations terminally successful:
W `13546` `COMPLETED 0:0` in `00:23:05`, Ta `13547` `COMPLETED 0:0` in
`00:22:49`, and Ti `13548` `COMPLETED 0:0` in `00:24:23`.

Read-only validation accepted all seven pressure sources per element. Every
source has exact matching-M3 command provenance, complete log, 5,001 finite
unary 32-atom 3D-PBC trajectory frames with finite energy/(32,3) force/(6,)
stress, and 50,001 finite consecutive NPT summary rows. The matching
400-row D3 DBs and M3 JNN hashes are unchanged, and all D4 selection/DFT
paths remain absent.

| Element | Frames / summary rows | Volume/atom (A3) | Instant pressure (GPa) | Maximum absolute force component (eV/A) |
|---|---:|---:|---:|---:|
| W | 35,007 / 350,007 | 13.594182-23.362874 | -15.062950-94.476020 | 15.242273 |
| Ta | 35,007 / 350,007 | 13.975722-26.097684 | -10.180180-100.949580 | 16.235243 |
| Ti | 35,007 / 350,007 | 9.732340-22.446045 | -7.292960-132.701570 | 8.758543 |

The approved D4 selection card is the D3 card with the matching M3 glob and
400-row D3 base: NPT pressures `1,5,10,20,30,40,50` GPa, target `100`,
equilibration fraction `0.10`, progress interval `500`, zero candidate/final
frame gaps, linear p99 tail cap `5`, `r_c=6.0`, `n_max=5`, `l_max=6`, and
similarity `0.99999`. The fixed clean-D0 gates are W `d_min=1.695596956`,
`q_void=0.946305262`; Ta `1.775316838`, `0.942271015`; and Ti
`1.775270170`, `0.946161232`. The pipeline will independently derive and
record each M3-based `U_min`.

### D4 combined-selection submissions

Immediately before submission, each element passed a compact no-overwrite and
isolation guard: its seven nonempty D4 pressure trajectories were present,
the frozen 400-row D3 database checksum and path-ordered ten-model M3
digest were unchanged, every model had its trainer log, and
`uncertainty_all_frames.csv`, `geometry_audit.csv`,
`absolute-u-projected-cur/`, `<X>_D4_labeled.db`, and `dft/` were absent.

Each direct `sbatch` command used
`scripts/slurm/run_md_selection_pipeline.slurm` with the approved NPT
pressure grid, target 100, exact element gate values, M3 glob, 1 node,
1 task, 24-hour limit, and element-local `slurm_logs/select-<X>-%j.{out,err}`
paths. The runner retains no-overwrite protection for all pipeline outputs
and derives `U_min` from all ten final M3 test-force MAEs.

| Element | Selection job | Immediate scheduler state |
|---|---:|---|
| W | `13549` | `RUNNING` on `lpsnode02` |
| Ta | `13550` | `RUNNING` on `lpsnode02` |
| Ti | `13551` | `RUNNING` on `lpsnode02` |

Active selection monitoring is authorized. No D4 DFT job, merge, M4, or E4
job has been submitted.

### D4 combined-selection terminal status

Focused active monitoring observed all three combined-selection allocations
reach successful terminal state. The scheduler accounting is:

| Element | Selection job | State / exit | Elapsed |
|---|---:|---|---:|
| W | `13549` | `COMPLETED 0:0` | `01:39:00` |
| Ta | `13550` | `COMPLETED 0:0` | `01:36:10` |
| Ti | `13551` | `COMPLETED 0:0` | `01:38:06` |

The next required action is read-only acceptance of all retained selection
artifacts. No DFT job has been submitted.

### D4 selection acceptance

A full read-only cross-artifact audit accepted all three isolated selections.
It verified exact M3-only stage-command provenance and the approved D3 policy,
the ten-log M3 `U_min` derivation, all finite 35,007-frame score records,
7-by-5,001 source/frame coverage, 31,507 production frames, and exact audit
coverage of every production frame with `U >= U_min`. All audit geometry
values are finite for unary 32-atom 3D-PBC configurations and apply the
frozen element-specific gates. The 100 final structures per element are
unique, finite unary 32-atom positive-cell PBC POSCARs whose cell and wrapped
fractional coordinates exactly match their recorded D4 trajectory frame.

| Element | M3-derived `U_min` (eV/A) | Post-U audit | Gate-valid CUR candidates | Gate rejected | Linear p99 U | Final source counts (`P-1,5,10,20,30,40,50GPa`) |
|---|---:|---:|---:|---:|---:|---|
| W | 0.20000000 | 29,248 | 24,038 | 5,210 | 1.04221200 | 35, 14, 23, 7, 9, 4, 8 |
| Ta | 0.17464000 | 28,499 | 23,432 | 5,067 | 0.94421906 | 30, 12, 15, 6, 15, 8, 14 |
| Ti | 0.12831000 | 27,915 | 24,277 | 3,638 | 0.57806026 | 34, 15, 8, 5, 17, 8, 13 |

For every element, the retained CUR parameters are target 100, zero candidate
and final frame gaps, p99 linear tail threshold, tail maximum 5, `r_c=6.0`,
`n_max=5`, `l_max=6`, and similarity threshold `0.99999`. CUR ranks are
exactly 1--100 with finite diagnostics and no selected similarity at or above
the threshold; exactly five selected structures occupy the p99 tail. The
candidate/source and tail distribution files, physical-gate rejection rows,
candidate/summary identity, all selected POSCAR filenames, the 400-row D3
database checksums, and ten-model M3 digests all passed isolation checks.

The first validator used an over-strict `1e-9` comparison of full-precision
audit values to ten-significant-digit all-frame CSV values and stopped on a
`2.6e-9` W volume/atom rounding difference. Re-running with a formatting
appropriate `1e-7` cross-CSV tolerance passed without changing any artifact.

### D4 Protocol-A DFT preflight

The exact selected POSCAR directories contain 100 valid final structures each,
and all three output databases and `dft/` work roots remain absent. The D3
400-row database / M3 committee checksums remain unchanged. The fixed
Protocol-A PAW identities and auto ENCUT values were rechecked:

| Element | POTCAR SHA-256 | ENMAX (eV) | `1.3*ENMAX` auto ENCUT (eV) |
|---|---|---:|---:|
| W | `c0897285f1b301314dcc12eb838ce8a777aa860795754598b0626cb818170117` | 223.057 | 289.9741 |
| Ta | `b94d0231aa338d2b49887428178c5ebac7fa385cbd6154890af94e8013d269f3` | 223.667 | 290.7671 |
| Ti | `f8e8f1d080d9e9b45e792f1068744b07aba8441d1e7ce11486a5d4c0f5a1479e` | 178.330 | 231.8290 |

With `module load jse`, `vasp_std` resolves to
`/home/opt/vasp-6.5.0/vasp_std`; no inherited overwrite, preparation, worker,
NCORE, or ENCUT-factor override is set. The approved submission uses one
node, 64 tasks, 24 hours, `CORES_PER_JOB=8`, `MAX_WORKERS=8`,
`VASP_COMMAND=vasp_std`, static `MAGMOM=_`, `KSPACING=0.2`, template-default
`NCORE=2`, and auto `ENCUT=1.3*ENMAX`, with no overwrite/force/prepare flag.

### D4 Protocol-A DFT submissions and monitoring stop

After the complete selection/DFT-input acceptance, three independent
no-overwrite jobs were submitted with
`env -u OVERWRITE -u FORCE_PREPARE -u PREPARE_ONLY`,
`CORES_PER_JOB=8`, `MAX_WORKERS=8`, and `VASP_COMMAND=vasp_std`. Each uses
`scripts/slurm/run_vasp_batch_dft.slurm`, one node, 64 tasks, 24 hours,
`MAGMOM=_`, `KSPACING=0.2`, and the template auto-ENCUT/default static
Protocol-A settings. The intended protected work roots are respectively
`dft/vasp_W_D4/`, `dft/vasp_Ta_D4/`, and `dft/vasp_Ti_D4/`.

| Element | DFT job | Selected input | Intended label DB |
|---|---:|---|---|
| W | `13558` | `cur-selected-poscar_absolute_u0p2_cur100/` | `W_D4_labeled.db` |
| Ta | `13559` | `cur-selected-poscar_absolute_u0p17464_cur100/` | `Ta_D4_labeled.db` |
| Ti | `13560` | `cur-selected-poscar_absolute_u0p12831_cur100/` | `Ti_D4_labeled.db` |

Monitoring stopped immediately after the Ti submission, as authorized. No
post-submission `squeue`/`sacct`, output inspection, label validation, merge,
M4 training, or E4 action was performed.
