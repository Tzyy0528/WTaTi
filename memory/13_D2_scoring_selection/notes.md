# Notes: D2 All-Frame Scoring and Structure Selection

## Sources

### Source 1: D2 MD validation
- Path: `memory/12_D2_NVT_sampling/`
- Key points:
  - All 15 D2 source trajectories passed finite-data and count validation.
  - Every element has five completed NVT sources with 5,001 frames each.

### Source 2: Workflow policy and source index
- Path: `research-plan.md` Section 10; `docs/source_function_index.md`
- Key points:
  - Score every production frame with the full sampling committee.
  - Derive `U_min` from the arithmetic mean of the ten final test `MAE-F`
    values and convert meV/A to eV/A.
  - Use `scripts/slurm/run_uncertainty_scoring.slurm` for score-only work and
    `scripts/slurm/run_absolute_u_projected_cur.slurm` for projected CUR.

### Source 3: D1 replacement selection
- Path: `memory/08_D1_reselection/`
- Key points:
  - The approved policy does not impose source balancing, frame gaps, tail
    caps, or physical gates.
  - D1 used `r_c=6.0`, `n_max=5`, `l_max=6`, and similarity threshold
    `0.99999`; the D2 label budget is not specified in the D2 record.

## Scoring Preflight

- Each element has five nonempty validated D2 trajectories and exactly ten
  nonempty M1 JNNs and training logs under its own element-local committee.
- The protected outputs
  `<X>-potential/02-nvt-round-2/uncertainty_all_frames.csv` and
  `<X>-potential/02-nvt-round-2/absolute-u-projected-cur/` are absent for W,
  Ta, and Ti.
- The scoring template refuses an existing all-frame CSV. It uses one node,
  one task, and a 24-hour walltime; each command explicitly directs stdout and
  stderr to its element-local `slurm_logs/` directory.

Exact scoring commands:

```bash
sbatch --nodes=1 --ntasks=1 --time=24:00:00 --output W-potential/02-nvt-round-2/slurm_logs/score-%j.out --error W-potential/02-nvt-round-2/slurm_logs/score-%j.err scripts/slurm/run_uncertainty_scoring.slurm --round-dir W-potential/02-nvt-round-2 --jnn-glob 'W-potential/model_versions/M1_from_D1/train-committee/train-*/*.jnn' --mode nvt --scales 0.90 0.95 1.00 1.05 1.10 --trajectory-name multi_nnap_md.xyz --equilibration-fraction 0.10 --all-frames-csv W-potential/02-nvt-round-2/uncertainty_all_frames.csv --progress-interval 500

sbatch --nodes=1 --ntasks=1 --time=24:00:00 --output Ta-potential/02-nvt-round-2/slurm_logs/score-%j.out --error Ta-potential/02-nvt-round-2/slurm_logs/score-%j.err scripts/slurm/run_uncertainty_scoring.slurm --round-dir Ta-potential/02-nvt-round-2 --jnn-glob 'Ta-potential/model_versions/M1_from_D1/train-committee/train-*/*.jnn' --mode nvt --scales 0.90 0.95 1.00 1.05 1.10 --trajectory-name multi_nnap_md.xyz --equilibration-fraction 0.10 --all-frames-csv Ta-potential/02-nvt-round-2/uncertainty_all_frames.csv --progress-interval 500

sbatch --nodes=1 --ntasks=1 --time=24:00:00 --output Ti-potential/02-nvt-round-2/slurm_logs/score-%j.out --error Ti-potential/02-nvt-round-2/slurm_logs/score-%j.err scripts/slurm/run_uncertainty_scoring.slurm --round-dir Ti-potential/02-nvt-round-2 --jnn-glob 'Ti-potential/model_versions/M1_from_D1/train-committee/train-*/*.jnn' --mode nvt --scales 0.90 0.95 1.00 1.05 1.10 --trajectory-name multi_nnap_md.xyz --equilibration-fraction 0.10 --all-frames-csv Ti-potential/02-nvt-round-2/uncertainty_all_frames.csv --progress-interval 500
```

## M1-Derived Calibration

Final right-hand test `MAE-F` values, arithmetic means, and thresholds:

| Element | Final test `MAE-F` values (meV/A; train-0..9) | Mean (meV/A) | `U_min` (eV/A) |
|---|---|---:|---:|
| W | 186.5, 169.2, 156.3, 170.6, 198.6, 137.1, 171.1, 179.1, 138.1, 195.6 | 170.22 | 0.17022 |
| Ta | 135.9, 133.5, 150.4, 142.9, 183.3, 123.8, 160.2, 150.3, 119.0, 145.1 | 144.44 | 0.14444 |
| Ti | 114.3, 88.28, 104.6, 114.6, 140.0, 103.1, 111.5, 107.2, 98.61, 154.0 | 113.619 | 0.113619 |

The calculation is `mean(final test MAE-F) / 1000`; it is independent for
each element and does not use an MD-pool percentile.

## Scoring Submission and Immediate Status

- W D2 all-frame scoring: SLURM job `13146`
- Ta D2 all-frame scoring: SLURM job `13147`
- Ti D2 all-frame scoring: SLURM job `13148`

The one immediate `squeue` check after submission found all three jobs
`RUNNING` on `lpsnode03` (elapsed approximately four seconds). No automatic
monitoring was started.

## Scoring Completion and CSV Validation

One focused `sacct` check found all scoring allocations and workers
`COMPLETED` with exit code `0:0`:

- W job `13146`: 5:11 elapsed
- Ta job `13147`: 5:08 elapsed
- Ti job `13148`: 2:14 elapsed

All three protected `uncertainty_all_frames.csv` files passed schema,
provenance, and numerical validation. Each has exactly 25,005 finite rows:
five isolated element-local sources with 5,001 consecutive frames each. The
score-only files contain no selection or CUR fields. The 10% equilibration
rule discards exactly 500 frames per source, leaving 22,505 production frames
per element.

| Element | `U_min` (eV/A) | `U >= U_min` production candidates | Candidates by scale 0.90, 0.95, 1.00, 1.05, 1.10 | Full-pool U range (eV/A) |
|---|---:|---:|---|---|
| W | 0.17022 | 22,385 | 4,451, 4,445, 4,487, 4,501, 4,501 | 0.000000000--8.221191809 |
| Ta | 0.14444 | 22,342 | 4,446, 4,452, 4,467, 4,480, 4,497 | 0.000000002--3.637261028 |
| Ti | 0.113619 | 21,914 | 4,501, 4,501, 4,493, 4,227, 4,192 | 0.000000001--1.357467039 |

The user clarified that the D1 approved 100-structure budget is the intended
project default for D2. The CUR CLI still receives it explicitly as
`--target 100`; it does not have a technical default. The inherited selection
configuration is `r_c=6.0`, `n_max=5`, `l_max=6`, similarity `0.99999`, zero
candidate/final frame gaps, and no source balancing, tail cap, or physical
gates.

## CUR Submission Preflight

Immediately before submission, each element-local score CSV had exactly
25,005 data rows, each `current.db` had exactly 200 rows, and all three
protected CUR output roots were absent. The template requests one node, one
task, and 24 hours per element, and rejects a pre-existing output root.

Exact protected CUR commands:

```bash
sbatch --nodes=1 --ntasks=1 --time=24:00:00 --output W-potential/02-nvt-round-2/slurm_logs/cur-%j.out --error W-potential/02-nvt-round-2/slurm_logs/cur-%j.err scripts/slurm/run_absolute_u_projected_cur.slurm --round-dir W-potential/02-nvt-round-2 --all-frames W-potential/02-nvt-round-2/uncertainty_all_frames.csv --base W-potential/current.db --output-root W-potential/02-nvt-round-2/absolute-u-projected-cur --u-min 0.17022 --target 100 --candidate-frame-gap 0 --final-frame-gap 0 --r-c 6.0 --n-max 5 --l-max 6 --similarity-threshold 0.99999

sbatch --nodes=1 --ntasks=1 --time=24:00:00 --output Ta-potential/02-nvt-round-2/slurm_logs/cur-%j.out --error Ta-potential/02-nvt-round-2/slurm_logs/cur-%j.err scripts/slurm/run_absolute_u_projected_cur.slurm --round-dir Ta-potential/02-nvt-round-2 --all-frames Ta-potential/02-nvt-round-2/uncertainty_all_frames.csv --base Ta-potential/current.db --output-root Ta-potential/02-nvt-round-2/absolute-u-projected-cur --u-min 0.14444 --target 100 --candidate-frame-gap 0 --final-frame-gap 0 --r-c 6.0 --n-max 5 --l-max 6 --similarity-threshold 0.99999

sbatch --nodes=1 --ntasks=1 --time=24:00:00 --output Ti-potential/02-nvt-round-2/slurm_logs/cur-%j.out --error Ti-potential/02-nvt-round-2/slurm_logs/cur-%j.err scripts/slurm/run_absolute_u_projected_cur.slurm --round-dir Ti-potential/02-nvt-round-2 --all-frames Ti-potential/02-nvt-round-2/uncertainty_all_frames.csv --base Ti-potential/current.db --output-root Ti-potential/02-nvt-round-2/absolute-u-projected-cur --u-min 0.113619 --target 100 --candidate-frame-gap 0 --final-frame-gap 0 --r-c 6.0 --n-max 5 --l-max 6 --similarity-threshold 0.99999
```

## CUR Submission and Immediate Status

- W D2 projected CUR: SLURM job `13150`
- Ta D2 projected CUR: SLURM job `13151`
- Ti D2 projected CUR: SLURM job `13152`

The one immediate `squeue` check found all three jobs `RUNNING` on
`lpsnode03` (elapsed approximately 2:20). No automatic monitoring was
started.

## CUR Completion and Selection Validation

One focused `sacct` check found all three projected-CUR jobs `COMPLETED` with
exit code `0:0`:

- W job `13150`: 15:44 elapsed
- Ta job `13151`: 15:28 elapsed
- Ti job `13152`: 16:40 elapsed

All selections passed output, parameter, provenance, and structure validation.
For each element, the output has the expected no-overwrite CUR provenance,
zero physical-gate rejections, the configured `U_min`, 100 unique CUR ranks
and POSCARs (`000001`--`000100`), and finite unary 16-atom structures with
positive volumes. The selected POSCAR file contents are unique.

| Element | Candidates | Selected source counts at scales 0.90, 0.95, 1.00, 1.05, 1.10 | Selected U range (eV/A) | Minimum selected distance (A) |
|---|---:|---|---|---:|
| W | 22,385 | 2, 2, 1, 18, 77 | 0.216465--8.221192 | 1.686147 |
| Ta | 22,342 | 5, 3, 3, 28, 61 | 0.157117--1.222275 | 1.797091 |
| Ti | 21,914 | 12, 3, 6, 15, 64 | 0.117965--1.094815 | 1.701557 |

No DFT work was submitted. The next stage, if authorized, is independent
Protocol-A VASP labeling of only these three 100-POSCAR selections through
`src/vasp_batch_dft.py` and `scripts/slurm/run_vasp_batch_dft.slurm`.
