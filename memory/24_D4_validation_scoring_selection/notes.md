# Notes: D4 NPT Validation, Scoring, and Projected-CUR Selection

## Sources

### Source 1: D4 workflow state
- Path: `memory/index.md`, `memory/23_D4_configuration_review/`
- Key points:
  - D4 NPT jobs W `13235`, Ta `13236`, and Ti `13237` completed `0:0`.
  - Each element used seven independent NPT pressures and all ten matching M3 models.

### Source 2: Selection policy
- Path: `research-plan.md` Sections 10 and 12; `docs/source_function_index.md`
- Key points:
  - Score every frame, derive a per-element M3-log `U_min`, then use
    physical/risk gates and current.db-projected CUR.
  - CUR-only and global Top-U selection are not the production policy.

## Commands and Observations

### D4 NPT post-run validation (passed)

Each element has exactly the frozen seven-source grid
`P-2GPa`, `P-8GPa`, `P-15GPa`, `P-25GPa`, `P-35GPa`, `P-45GPa`, and
`P-55GPa`. Every one of the 21 sources has nonempty `command.sh`, `log`,
`multi_nnap_md.xyz`, and `energy_forces_summary.dat`; reproduces only its
matching seed, M3 committee, pressure, temperature, and NPT controls; and
contains no EOS or cross-element path.

All logs report both `Starting NPT biased MD` and `Finished MD`. Every
trajectory contains 5,001 finite unary 16-atom 3D-periodic frames, and every
summary contains 50,001 finite consecutive steps (`0..50000`) with finite
pressure diagnostics.

| Element | Total frames | Volume/atom range (A3) | Instantaneous pressure range (GPa) | Max force component (eV/A) |
|---|---:|---:|---:|---:|
| W | 35,007 | 12.879321--22.200915 | -20.732--118.013 | 13.779890 |
| Ta | 35,007 | 12.932737--25.474669 | -14.380--134.127 | 13.439166 |
| Ti | 35,007 | 9.422574--20.481919 | -7.652--149.631 | 11.353878 |

These validated trajectories are candidate pools only. They do not yet
constitute DFT candidates or authorize a `current.db` change.

### Protected D4 score-only preflight (passed)

Immediately before submission, every element had its matching 400-row
`current.db`, seven nonempty validated D4 trajectories, and exactly ten
nonempty M3 JNN/log pairs. Both the protected all-frame CSV and projected-CUR
root were absent for every element. The score-only template requests one node,
one task, and 24 hours; it has no overwrite mode and writes no candidates.

The required M3 final test-force calibration (right-hand final `MAE-F` log
values, meV/A) is:

| Element | Test MAE-F values (fold 0..9, meV/A) | Mean (meV/A) | `U_min` (eV/A) |
|---|---|---:|---:|
| W | 220.4, 212.8, 188.0, 188.9, 200.0, 197.1, 203.3, 216.9, 201.0, 231.7 | 206.010000 | 0.206010000 |
| Ta | 166.0, 164.0, 148.3, 167.1, 163.8, 159.9, 170.3, 164.7, 166.3, 174.4 | 164.480000 | 0.164480000 |
| Ti | 146.4, 138.3, 118.9, 128.6, 137.0, 120.0, 138.0, 134.4, 124.0, 153.1 | 133.870000 | 0.133870000 |

The submission command for each element is:

```bash
sbatch --output <X>-potential/04-npt-round-2/slurm_logs/score-%j.out \
  scripts/slurm/run_uncertainty_scoring.slurm \
  --round-dir <X>-potential/04-npt-round-2 \
  --jnn-glob '<X>-potential/model_versions/M3_from_D3/train-committee/train-*/*.jnn' \
  --mode npt --pressures 2 8 15 25 35 45 55 \
  --equilibration-fraction 0.10 \
  --all-frames-csv <X>-potential/04-npt-round-2/uncertainty_all_frames.csv
```

### D4 score-only submission (2026-07-26)

Immediately before each submission, the matching protected
`uncertainty_all_frames.csv` remained absent. Submitted independent
all-ten-M3-model score-only jobs:

| Element | Job ID | Output CSV |
|---|---:|---|
| W | `13240` | `W-potential/04-npt-round-2/uncertainty_all_frames.csv` |
| Ta | `13241` | `Ta-potential/04-npt-round-2/uncertainty_all_frames.csv` |
| Ti | `13242` | `Ti-potential/04-npt-round-2/uncertainty_all_frames.csv` |

Each job requests one node, one task, and 24 hours. One immediate focused
queue check found all three `RUNNING` on `lpsnode01`. No monitoring loop was
started; projected-CUR selection remains unsubmitted pending score validation
and current-pool gate calibration.

### D4 score-only completion status

A later focused `sacct` check found all score-only jobs `COMPLETED` with exit
`0:0`: W `13240` in `00:07:06`, Ta `13241` in `00:06:59`, and Ti `13242` in
`00:04:46`. CSV artifact validation, gate calibration, and projected-CUR
selection remain unstarted.

### D4 all-frame CSV validation and gate calibration (passed)

Every protected score-only CSV has the complete schema and exactly 35,007
rows: seven expected sources with frames `0..5000`; the first 500 frames per
source are the only discarded-equilibration records; every required
uncertainty, volume, force, and pressure value is finite. The score command
uses only its matching ten-M3-JNN glob, seven D4 trajectories, NPT mode, and
`--score-only`; no EOS or cross-element provenance is present. No candidate or
final-selection field was written.

| Element | Production frames | `U >= U_min` | U p0 / p50 / p99 / p100 (eV/A) | Qualified-pool p99 tail U (eV/A) |
|---|---:|---:|---:|---:|
| W | 31,507 | 17,690 | 0.083209 / 0.214171 / 0.510972 / 1.502103 | 0.560109 |
| Ta | 31,507 | 15,289 | 0.061882 / 0.162744 / 0.442644 / 1.590160 | 0.518687 |
| Ti | 31,507 | 23,766 | 0.058921 / 0.180635 / 0.611047 / 1.699771 | 0.649240 |

The current D3 `current.db` is the labeled-envelope reference. A read-only
geometry scan of every D4 production frame passing its element-local `U_min`
used a 5% outward volume/minimum-distance margin and 10% outward
max-force-norm margin. All qualified frames pass every gate and every source
retains far more than 100 candidates collectively:

| Element | Min V/atom (A3) | Max V/atom (A3) | Max force (eV/A) | Min distance (A) | Qualified V range (A3) | Qualified max force / min distance |
|---|---:|---:|---:|---:|---|---|
| W | 10.033503 | 24.608059 | 25.227742 | 1.601840 | 13.289768--22.200915 | 18.242233 / 1.820716 |
| Ta | 11.367755 | 26.990304 | 15.297877 | 1.561930 | 14.104499--23.574498 | 13.225193 / 1.728106 |
| Ti | 10.723466 | 27.622515 | 32.112934 | 1.321087 | 11.018644--20.481919 | 13.083461 / 1.597362 |

The frozen D4 selection policy is therefore:

- matching M3-log `U_min`: W `0.206010000`, Ta `0.164480000`, Ti
  `0.133870000` eV/A;
- target 100; no source balancing or per-source quota;
- candidate/final same-source gaps: 50/100 saved frames;
- current-pool p99 tail thresholds above; independently retained tail cap 10;
- physical gates from the table above;
- `r_c=6.0`, `n_max=5`, `l_max=6`, similarity threshold `0.99999`.

The preflighted projected-CUR command is:

```bash
sbatch --output <X>-potential/04-npt-round-2/slurm_logs/cur-%j.out \
  scripts/slurm/run_absolute_u_projected_cur.slurm \
  --round-dir <X>-potential/04-npt-round-2 \
  --all-frames <X>-potential/04-npt-round-2/uncertainty_all_frames.csv \
  --base <X>-potential/current.db \
  --output-root <X>-potential/04-npt-round-2/absolute-u-projected-cur \
  --u-min <element-U-min> --target 100 \
  --candidate-frame-gap 50 --final-frame-gap 100 \
  --r-c 6.0 --n-max 5 --l-max 6 --similarity-threshold 0.99999 \
  --tail-threshold <element-p99-tail-U> --tail-max 10 \
  --min-volume-per-atom <element-min-V> --max-volume-per-atom <element-max-V> \
  --max-force <element-max-force> --min-distance <element-min-distance>
```

### D4 protected projected-CUR submission (2026-07-26)

Immediately before submission, each matching all-frame CSV was nonempty with
exactly 35,007 rows; each current DB remained the expected unary 16-atom,
400-row D3 DB with its frozen SHA-256; and every element-local
`absolute-u-projected-cur` root (and selector temporary root) was absent.
The CSV trajectory paths were restricted to that element's D4 NPT round and
contained no EOS or other-element provenance.

Submitted the approved commands through
`scripts/slurm/run_absolute_u_projected_cur.slurm` with the frozen per-element
U/gate settings, target 100, 50/100 candidate/final source frame gaps,
descriptor settings `6.0/5/6/0.99999`, tail cap 10, and neither source
balancing nor all-source requirement:

| Element | Job ID | Protected selection root |
|---|---:|---|
| W | `13244` | `W-potential/04-npt-round-2/absolute-u-projected-cur` |
| Ta | `13245` | `Ta-potential/04-npt-round-2/absolute-u-projected-cur` |
| Ti | `13246` | `Ti-potential/04-npt-round-2/absolute-u-projected-cur` |

The template requests one node, one task, and 24 hours; it refuses an
existing output root and the selector uses an atomic temporary-output rename.
One immediate `squeue` check found all three jobs `PENDING` with no assigned
node. No monitoring loop was started.

### D4 projected-CUR completion and artifact validation (passed)

Focused accounting after the user's completion report found each selection job
`COMPLETED 0:0`: W `13244` in `00:05:38`, Ta `13245` in `00:05:36`, and Ti
`13246` in `00:05:49`.

For every element, the protected output contains
`selection_parameters.txt`, `physical_gate_rejections.csv`,
`selection_summary.csv`, `cur_selected_distribution.csv`, one candidate
POSCAR directory, and one selected-POSCAR directory. The audit confirms:

- exactly 100 selected, unique, finite unary 16-atom 3D-periodic POSCARs,
  with ranks/files `000001.poscar` through `000100.poscar`;
- all seven matching D4 NPT sources only, no EOS or cross-element trajectory
  provenance, and all final frames retain the 100-frame same-source gap;
- all 602/584/617 W/Ta/Ti candidates retain the 50-frame source gap,
  `U >= U_min`, and passed their physical gates; the physical-rejection CSVs
  are empty;
- selected tail counts are W 4, Ta 1, and Ti 1, each below the cap 10;
- the recorded parameters exactly match the frozen element-local policy, and
  all three 400-row D3 `current.db` SHA-256 values remain unchanged.

The final selected source distributions are:

| Element | P-2 | P-8 | P-15 | P-25 | P-35 | P-45 | P-55 |
|---|---:|---:|---:|---:|---:|---:|---:|
| W | 27 | 23 | 12 | 10 | 7 | 7 | 14 |
| Ta | 30 | 23 | 16 | 12 | 9 | 5 | 5 |
| Ti | 26 | 9 | 12 | 8 | 11 | 17 | 17 |

## Synthesized Findings

### Scope
- Keep W, Ta, and Ti candidate pools, models, score CSVs, and selections
  fully independent.
- EOS assets remain validation-only; no DFT labeling, database update, M4, or
  E4 action is within this task.
