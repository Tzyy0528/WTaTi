# Notes: D3 All-Frame Scoring and Projected-CUR Selection

## Sources

### Source 1: D3 validated NPT state
- Path: `memory/18_D3_configuration_review/`
- Key points:
  - Each element has seven validated, element-local D3 NPT trajectory sources.
  - Each source contains 5,001 finite 16-atom periodic frames and a complete
    NPT pressure summary.

### Source 2: Scoring and selection policy
- Path: `research-plan.md` Sections 10.1--10.3;
  `docs/source_function_index.md`
- Key points:
  - Score every production frame with all ten matching M2 models in
    `--score-only` mode.
  - Derive `U_min` independently from the arithmetic mean of final M2 test
    `MAE-F` values, in eV/A.
  - Select using absolute-U cutoff, source decorrelation, physical/risk gates,
    current.db-projected CUR, and an approved extreme-U tail cap.

### Source 3: Production runners and selector implementation
- Path: `scripts/slurm/run_uncertainty_scoring.slurm`;
  `scripts/slurm/run_absolute_u_projected_cur.slurm`;
  `src/stratified_uncertainty_selection.py`;
  `src/absolute_u_projected_cur_selection.py`
- Key points:
  - The scoring template requires SLURM, refuses an existing all-frame CSV,
    expands the supplied JNN glob, checks each declared NPT trajectory, then
    runs JSE scoring with `--score-only`.
  - The CUR template requires a distinct, absent output root and runs the
    absolute-U selector with default descriptor controls `r_c=6.0`,
    `n_max=5`, `l_max=6`, and similarity threshold `0.99999`.
  - The selector discards equilibration frames and sub-threshold uncertainty
    before volume/force gates and later evaluates the minimum-distance gate
    from the actual candidate geometry. Gate rejections are auditable in
    `physical_gate_rejections.csv`.
  - Tail threshold/cap and source balancing are opt-in. Source balancing will
    remain disabled because it has not been approved.

## Commands and Observations

- User authorized sequential score-only and projected-CUR execution with a
  target of 100 selected structures per element.
- The exact production runner interfaces were re-read before submission.

### Protected scoring preflight (passed)

All checks below were performed immediately before scoring submission:

| Element | D3 sources and frames | M2 JNNs / logs | Base DB rows | Score CSV / CUR root | `U_min` (eV/A) |
|---|---|---:|---:|---|---:|
| W | 7 x 5,001 | 10 / 10 | 300 | both absent | 0.194310000 |
| Ta | 7 x 5,001 | 10 / 10 | 300 | both absent | 0.166670000 |
| Ti | 7 x 5,001 | 10 / 10 | 300 | both absent | 0.125950000 |

- Every expected `P-{1,5,10,20,30,40,50}GPa` source had nonempty command,
  log, trajectory, and NPT-summary files. The trajectory frame count was
  confirmed from 5,001 `Lattice=` frames per source.
- Each `train-i` directory contains only the matching `i.jnn` and final
  training log required by the M2 committee glob. Each element-local
  `current.db` has 300 `systems` rows.
- D3 command provenance contains neither `results/` nor `eos`, so no EOS
  asset entered the MD input chain.

### M2 test-force calibration

The last `MAE-F: train | test` record was parsed from each matching M2
`train-i/log`. The right-hand test values (meV/A), arithmetic means, and
threshold conversion are:

| Element | Final test `MAE-F` values (meV/A, i=0..9) | Mean (meV/A) | `U_min` (eV/A) |
|---|---|---:|---:|
| W | 200.2, 185.5, 208.8, 183.7, 207.2, 204.6, 215.9, 193.6, 179.3, 164.3 | 194.310000 | 0.194310000 |
| Ta | 172.3, 142.9, 185.7, 145.2, 181.6, 192.2, 188.2, 160.8, 166.7, 131.1 | 166.670000 | 0.166670000 |
| Ti | 130.8, 134.5, 134.7, 113.2, 133.8, 124.4, 133.9, 117.8, 112.9, 123.5 | 125.950000 | 0.125950000 |

The prescribed rule is used directly: arithmetic mean / 1000; no MD-pool
percentile or prior-round threshold was used.

### Score-only submission (2026-07-25)

Each submission requested one node, one task, and 24 hours. It uses only the
matching full ten-model M2 glob, all seven NPT pressures, a 10% equilibration
discard, the protected element-local CSV path, and `--score-only` through the
template.

| Element | Job ID | Output CSV |
|---|---:|---|
| W | 13176 | `W-potential/03-npt-round-1/uncertainty_all_frames.csv` |
| Ta | 13177 | `Ta-potential/03-npt-round-1/uncertainty_all_frames.csv` |
| Ti | 13178 | `Ti-potential/03-npt-round-1/uncertainty_all_frames.csv` |

The one immediate focused queue check found all three jobs running on
`lpsnode03`. No pre-existing output was overwritten.

### Score-only completion and CSV validation (passed)

Focused accounting reported successful terminal states:

| Element | Job ID | State | Exit code | Elapsed |
|---|---:|---|---|---:|
| W | 13176 | COMPLETED | 0:0 | 00:06:06 |
| Ta | 13177 | COMPLETED | 0:0 | 00:06:01 |
| Ti | 13178 | COMPLETED | 0:0 | 00:03:50 |

Each CSV has the complete score-only schema and exactly 35,007 data rows:
seven expected NPT sources, 5,001 consecutive frames (`0..5000`) per source,
500 discarded (`0..499`) and 4,501 retained frames per source. All required
numerical values (`U`, volume/atom, mean-force metrics, and instantaneous
pressure) are finite. The score command cards record only their matching M2
glob, NPT mode, `1,5,10,20,30,40,50` GPa sources, and `--score-only`; they
contain no EOS path. All bin/candidate/final-selection fields are empty or
false, and no candidate, selected, percentile, or CUR output exists.

| Element | Production frames | `U >= U_min` | U p0/p50/p99/p100 (eV/A) |
|---|---:|---:|---|
| W | 31,507 | 29,928 | 0.092636 / 0.288319 / 0.642724 / 5.916576 |
| Ta | 31,507 | 25,734 | 0.074840 / 0.208423 / 0.536077 / 0.945238 |
| Ti | 31,507 | 28,098 | 0.063917 / 0.195672 / 0.499437 / 1.120813 |

The retained `U >= U_min` counts by source (`P-1`, `P-5`, `P-10`, `P-20`,
`P-30`, `P-40`, `P-50` GPa) are:

- W: 4,356, 4,409, 4,408, 4,293, 4,105, 4,285, 4,072.
- Ta: 3,298, 3,533, 3,539, 3,698, 3,736, 3,928, 4,002.
- Ti: 2,862, 3,364, 3,964, 4,428, 4,481, 4,498, 4,501.

### Qualified-pool physical/risk screening

A read-only single-threaded geometry scan computed the MIC minimum distance
for every retained `U >= U_min` frame; it wrote no files. Quantiles below are
for the same qualified candidates and provide the evidence needed to approve,
not assume, the numerical gates.

| Element | Volume/atom p1--p99 (A3) | Mean-force p99 (eV/A) | Min-distance p1 (A) | U p99 tail threshold (eV/A) |
|---|---:|---:|---:|---:|
| W | 14.155072--20.334498 | 12.434409 | 2.038657 | 0.649610 |
| Ta | 15.161535--22.295123 | 9.537076 | 2.003063 | 0.554112 |
| Ti | 12.425338--19.002211 | 6.133524 | 1.755472 | 0.510180 |

Full qualified ranges preserve the observed extreme-risk context:

| Element | Volume/atom min--max (A3) | Mean-force max (eV/A) | Min-distance min--max (A) | U max (eV/A) |
|---|---:|---:|---:|---:|
| W | 13.573798--22.276309 | 18.308366 | 1.804474--2.506083 | 5.916576 |
| Ta | 14.285370--25.745101 | 12.501239 | 1.811492--2.573529 | 0.945238 |
| Ti | 11.758770--20.229849 | 11.919833 | 1.603959--2.442216 | 1.120813 |

No recorded research-plan or prior task supplies approved numerical
volume/force/distance thresholds, source frame gaps, or tail caps. Historical
D1/D2 records explicitly used no such gates/caps and cannot override the
current mandatory policy. CUR is therefore not submitted until the user
approves a documented D3 policy.

### D2 labeled-envelope comparison and recommended policy (pending approval)

A read-only single-threaded scan of every matching Protocol-A-labeled
`current.db` structure found that the D3 qualified-pool geometry is already
within, or essentially within, the prior DFT-labeled operating envelope:

| Element | D2 volume/atom min--max (A3) | D2 min-distance min (A) | D2 max DFT-force norm (eV/A) |
|---|---:|---:|---:|
| W | 10.561582--23.436247 | 1.686147 | 22.934311 |
| Ta | 11.966058--25.705051 | 1.644137 | 13.907161 |
| Ti | 11.287859--26.307157 | 1.390618 | 29.193577 |

Ta's D3 maximum qualified volume is only 0.040050 A3/atom above the D2
maximum; all other D3 qualified extrema fall inside the labeled envelope.
Therefore D3-pool p1/p99 volume/force/distance filters would unnecessarily
discard physically labeled-like high-pressure or high-temperature states.

The recommended least-invasive policy is consequently:

1. Preserve the inherited `U_min`, target 100, descriptor controls, and no
   source balancing.
2. Use candidate/final source-wise gaps of 50/100 saved frames. At the frozen
   10 fs write interval these are 0.5/1.0 ps; they remove near-neighbor
   temporal duplication without adding source quotas.
3. Apply hard physical gates at a 5% outward geometry margin and 10% outward
   force margin from the D2 Protocol-A labeled extrema. These are safety
   guards, not percentile trimming; every current D3 qualified frame passes.
4. Define the risk tail as the qualified-pool U p99 and cap it at 10 of the
   100 selected structures. This specifically limits pathological extrapolative
   outliers (W reaches 5.916576 eV/A) while retaining high-U coverage.

| Element | Min V/atom (A3) | Max V/atom (A3) | Max force (eV/A) | Min distance (A) | Tail U (eV/A) | Tail max |
|---|---:|---:|---:|---:|---:|---:|
| W | 10.033503 | 24.608059 | 25.227742 | 1.601840 | 0.649610 | 10 |
| Ta | 11.367755 | 26.990304 | 15.297877 | 1.561930 | 0.554112 | 10 |
| Ti | 10.723466 | 27.622515 | 32.112935 | 1.321087 | 0.510180 | 10 |

This is a recommendation only. It must be explicitly approved before CUR
submission.

### Approved D3 CUR policy (2026-07-25)

The user approved the labeled-envelope recommendation above without changes:

- target: 100 per element; no source balancing or source quota;
- source-wise candidate/final gaps: 50/100 saved frames;
- physical gates and per-element tail thresholds/cap: the values in the
  preceding table;
- matching M2-log `U_min` and descriptors: W/Ta/Ti values already recorded,
  `r_c=6.0`, `n_max=5`, `l_max=6`, similarity threshold `0.99999`.

CUR is authorized only for these element-local D3 roots. DFT labeling,
database merge, M3 training, and E3 remain out of scope.

### CUR preflight and submission (2026-07-25)

Immediately before each submission, its all-frame CSV was present with 35,007
data rows, its matching `current.db` contained 300 rows, its protected CUR
root was absent, and neither CUR input contained `results/` or `eos`
provenance. No output was overwritten.

| Element | Job ID | Output root |
|---|---:|---|
| W | 13182 | `W-potential/03-npt-round-1/absolute-u-projected-cur/` |
| Ta | 13183 | `Ta-potential/03-npt-round-1/absolute-u-projected-cur/` |
| Ti | 13184 | `Ti-potential/03-npt-round-1/absolute-u-projected-cur/` |

Every job requests one node, one task, and 24 hours, and passes the approved
target, gaps, gates, tail policy, and `6.0/5/6/0.99999` descriptor controls.
`--balance-sources` and `--require-all-sources` were deliberately omitted.
The one immediate focused queue check found all three jobs running on
`lpsnode03`.

### CUR completion and final selection validation (passed)

Focused accounting reported:

| Element | Job ID | State | Exit code | Elapsed |
|---|---:|---|---|---:|
| W | 13182 | COMPLETED | 0:0 | 00:00:46 |
| Ta | 13183 | COMPLETED | 0:0 | 00:00:50 |
| Ti | 13184 | COMPLETED | 0:0 | 00:00:53 |

For every element, final validation confirmed:

- the expected protected output root, selection parameters, candidate/summary
  metadata, selected distribution, physical-gate audit, and CUR summary;
- matching element-local `current.db` and all-frame CSV paths only, with no
  EOS or cross-element provenance;
- the approved `U_min`, `50/100` gaps, target, tail policy, physical gates,
  descriptors, no source balancing, and no source quota;
- seven surviving candidate sources, candidate gaps >=50, final per-source
  gaps >=100, and no similarity rejection;
- zero physical-gate rejections and every candidate inside the approved
  volume, force, and geometry limits;
- exactly 100 `000001.poscar`--`000100.poscar` structures per element, with
  unique file contents, matching CUR ranks, finite positions/cells, positive
  volumes, 3D PBC, 16 atoms, and only the correct unary element.

| Element | Candidates | Selected | Tail selected / cap | Selected U range (eV/A) | Selected V/atom range (A3) | Selected min-distance range (A) |
|---|---:|---:|---:|---:|---:|---:|
| W | 632 | 100 | 1 / 10 | 0.197665--1.002400 | 14.054417--21.875439 | 1.961930--2.471913 |
| Ta | 626 | 100 | 3 / 10 | 0.168289--0.671866 | 14.927872--25.271939 | 1.944990--2.472005 |
| Ti | 629 | 100 | 2 / 10 | 0.127614--0.590714 | 12.101516--19.706084 | 1.762952--2.275292 |

Final source distributions (not quotas) are:

- W: P-1=29, P-5=20, P-10=17, P-20=7, P-30=8, P-40=6, P-50=13.
- Ta: P-1=30, P-5=26, P-10=13, P-20=7, P-30=14, P-40=5, P-50=5.
- Ti: P-1=29, P-5=18, P-10=13, P-20=11, P-30=6, P-40=9, P-50=14.

The selected POSCAR roots are:

- `W-potential/03-npt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p19431_cur100/`
- `Ta-potential/03-npt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p16667_cur100/`
- `Ti-potential/03-npt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p12595_cur100/`

No DFT labeling command was submitted.
