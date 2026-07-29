# Task Plan: Clean FCC 2x2x2 Restart

## Goal
Build new independent W, Ta, and Ti FCC active-learning workflows from
correctly expanded 2x2x2 FCC seeds, with no reuse of deleted FCC artifacts.

## Phases
- [x] Phase 1: Cancel FCC jobs and delete all prior FCC-derived paths and
  task records.
- [x] Phase 2: Create and validate new 32-atom FCC seeds from the retained
  four-atom benchmark FCC source cells.
- [x] Phase 3: Generate, validate, and Protocol-A label fresh D0 pools.
- [x] Phase 4: Publish validated D0 databases, train M0, and record E0.
- [ ] Phase 5: Continue D1 -> M1 -> E1 -> D2 only from this clean lineage.

## Key Questions
1. Does `2 2 2` replicate every source-cell lattice direction exactly twice,
   producing a 32-atom seed from each four-atom FCC source?
2. Are the fresh FCC roots disjoint from the retained D4/M4 and EOS assets?

## Decisions Made
- A `2 2 2` supercell means two copies in x, y, and z. It is the only
  accepted seed construction for this clean FCC restart.
- The new clean paths reuse the original names only after all prior contents
  were deleted: `structures/<X>_fcc_restart/` and
  `<X>-potential/fcc-restart/`.
- The already-expanded 32-atom seed will be passed to `nninit` with
  replication `1 1 1`; no additional seed replication is intended.
- D1 NVT will use the same validated 32-atom seed with `--rep 1 1 1` and all
  ten matching M0 JNNs; it will not use a 16-atom or `2x2x1` input.
- D1 scoring is one single-worker, element-isolated NVT job per element. It
  reads only the five stated-scale production trajectories and the exact
  matching ten-model M0 glob, writes only the absent all-frame CSV, and uses
  the template's mandatory `--score-only` invocation.
- The score-complete transition uses the arithmetic mean of the ten final
  M0 test `MAE-F` values (meV/A) divided by 1,000 as the element-local
  absolute uncertainty cutoff: W `0.088824`, Ta `0.063869`, and Ti
  `0.038361` eV/A. It does not use a pool percentile cutoff.
- Per the user's direction, the clean-D1 selection card is frozen from only
  the matching clean D0 labeled envelope and clean D1 all-frame data. W uses
  a 100-structure safe card; Ti uses a restricted 75-structure safe card; Ta
  has no physically qualified D1 candidate and is blocked from CUR/DFT until
  new sampling is authorized. This historical card is superseded with its
  deleted high-temperature D1 pool. No D4/M4 or prior FCC data calibrates
  replacement-card values.
- The user explicitly authorizes deleting all three old clean-D1 round roots
  (`<X>-potential/fcc-restart/01-nvt-round-1/`) rather than preserving them.
 The replacement D1 uses the original round paths, unchanged seed/M0/scale
  controls, and `T=1.10*T_m`; no parallel `T1p10Tm` output root is retained.
- The user explicitly directs simultaneous clean-FCC D2 sampling. The frozen
  M1 NVT cards retain `1.10*T_m` to isolate the new scale-grid change:
  W `0.95,1.00,1.05,1.10,1.15`; Ta
  `0.90,0.925,0.95,0.975,1.00`; and Ti
  `0.95,0.975,1.00,1.025,1.05`. Ta/Ti grids remain inside their D1
  geometry-safe windows; later D2 geometry gates are not relaxed.
- The old-D1-derived physical/risk cards are superseded with the deleted D1
  data. New `U_min` values remain M0-log-derived but all later candidate
  counts, physical gates, tail caps, and DFT targets must be recalibrated
  exclusively from the replacement D1 pool.
- Replacement D1 scoring remains one one-core, element-isolated NVT job per
  element. It uses only the replacement trajectories and matching M0
  committee glob, writes only an absent `uncertainty_all_frames.csv`, and
  relies on the template's mandatory score-only mode.

## Errors Encountered
- The first D0 labeling preflight stopped at Ti because the validator's
  manually transcribed expected POTCAR SHA-256 omitted characters. No output
  path was created and no calculation was submitted. Resolution: use the
  recorded full Ti checksum and rerun the read-only preflight.
- The first post-submission memory-index patch used stale wording and did not
  apply to that file; task-record updates succeeded. Resolution: read the
  current index and apply a focused status update without changing workflow
  assets.
- The first fixed-EOS E0 preflight stopped at Ti because a manually
  transcribed metadata SHA-256 was incorrect. No evaluation output was
  created. Resolution: use the checksum read directly from the protected
  reference and rerun the read-only preflight.
- The first E0 artifact validator stopped while formatting the selected
  absolute JNN path relative to an unresolved committee path. It made no
  changes. Resolution: normalize the committee path before reporting and
  rerun the read-only validator.
- The initial combined memory-record patch updated the task files but did not
  match the current `memory/index.md` wording. Resolution: apply the index
  update as a focused patch; no workflow asset was affected.
- A direct scorer `--help` check failed because the login-shell Python lacks
  NumPy. Resolution: load the required `jse` module before invoking the
  scorer; its CLI check then passed. No output was created.
- The first read-only all-frame CSV validator had a transcription syntax error
  in its expected-equilibration list expression and did not run. Resolution:
  correct the closing delimiter and rerun the validator; no workflow asset
  was modified.
- The first physical-gate scan correctly completed W but halted on an
  intentional assertion when the provisional Ta force gate, derived as a 10%
  margin beyond the D0 labeled-force maximum, removed four entire sources.
  Resolution: retain this as evidence that the D0-force-envelope rule is too
  restrictive for clean D1 Ta/Ti; rerun a non-asserting diagnostic scan and
  determine gates that preserve auditable source coverage. No selection
  output was created.
- The second gate scan confirmed the W card but halted at Ta because the
  exploratory alternative `max_force=100 eV/A` combined with the D0-derived
  minimum-distance gate still left zero qualified Ta candidates. Resolution:
  scan the coupled D1 force/minimum-distance distributions before setting a
  relaxed-but-explicit Ta/Ti safety envelope; no selection output was
  created.
- A focused Ti gate scan did not start because of a local bracket
  transcription syntax error in the read-only diagnostic. Resolution: correct
  the list-comprehension index expression and rerun; no workflow asset was
  modified.
- An initial documentation search used `rg --glob` after positional paths,
  which `rg` treated as invalid arguments. Resolution: the focused search was
  rerun without that misplaced option; it affected no workflow asset.
- The first post-submission memory patch updated the task files but did not
  match the current index context. Resolution: read the current index and
  apply its status transition as a focused patch; no workflow asset was
  affected.
- A post-submission filesystem assertion expected no `md/` directory before a
  replacement job began, but the scheduler started W quickly after the one
  allowed immediate queue check. Resolution: treat this as the expected race,
  make no further status/artifact checks or polling, and let the submitted
  jobs run.
- The initial Ta M1 artifact scan used `fd` without `--no-ignore`, so
  `.gitignore` patterns for `*.jnn`, `*.db`, and `log` hid generated files
  and caused a false empty-directory report. Resolution: rerun the scan with
  `fd -HI`; all ten folds contain the required JNN, trainer, DB, log, and
  history artifacts. The earlier empty-committee report is superseded.
- The first read-only D2 preflight stopped at W because its validator filled
  a distance-matrix diagonal with infinity and then incorrectly required the
  whole matrix to be finite. No path was created and no job was submitted.
  Resolution: check finite off-diagonal distances before masking the
  diagonal, then rerun the preflight.
- The corrected D2 preflight then stopped at W because a naive
  cross-element substring test matched `Ta` within the workspace directory
  name `WTaTi`. No path was created and no job was submitted. Resolution:
  test only element-specific path components such as `Ta-potential`, then
  rerun the read-only preflight.
- The first combined post-submission memory patch applied the task-plan and
  notes changes but missed stale contexts in the deliverable and index. No
  workflow asset changed. Resolution: read the current files and apply
  focused follow-up updates.

## Status
**Historical Phase 4** - D0 jobs W `13381`, Ta `13382`, and Ti `13383`
completed `0:0`; their three 100-row 32-atom label DBs passed complete
provenance, result, geometry, and protected-asset validation. Every matching
clean D0 `current.db` is atomically published, and M0 training passed
no-overwrite preflight. M0 jobs W `13395`, Ta `13396`, and Ti `13397` are
submitted. On the user's completion report, all completed `0:0` and passed
ten-model 5,000-epoch, disjoint-fold validation. Fixed-reference E0 passed
no-overwrite preflight, completed, and passed artifact/isolation validation.
**Currently in Phase 5** - inspect and preflight clean D1 NVT sampling from
only the matching 32-atom seed and full M0 committee. The D1 card passed
no-overwrite preflight; NVT jobs W `13399`, Ta `13400`, and Ti `13401` are
submitted. The single immediate check found all pending; do not poll. On a
later completion request, validate all 15 source trajectories before
all-frame uncertainty scoring. The D1 jobs have now completed successfully
and all 15 trajectories passed complete finite-output, provenance, and
frame-count validation. **Currently in Phase 5** - record and preflight
element-isolated all-frame, score-only uncertainty evaluation; the
no-overwrite preflight and exact submission cards are recorded. Submit the
three jobs, then make only one combined immediate status check. Jobs W
`13413`, Ta `13414`, and Ti `13415` are submitted; the one immediate
combined check found all pending. Do not poll. After terminal completion,
validate each 25,005-row all-frame CSV before deriving independent
committee-log `U_min` values. All three score jobs are now `COMPLETED 0:0`;
their element-local CSVs passed complete all-frame validation and the three
independent `U_min` values are recorded. **Currently in Phase 5** - develop
and obtain approval for element-local D1 physical/risk gates, a DFT target,
source-wise decorrelation gaps, and extreme-U tail caps before preflighting
absolute-U, current.db-projected CUR selection. Do not submit selection
without those approved values. The user has now directed determination of
those cards. W and Ti have frozen, auditable cards and may be separately
preflighted later; Ta is blocked because every D1 production frame violates
the clean-D0-derived minimum-distance safety gate. Do not submit Ta CUR/DFT;
preserve its scored evidence and await explicit authorization for new Ta
sampling. The user has now authorized replacing all old D1 evidence with
lower-temperature `1.10*T_m` reruns; verify no old job is active, delete only
the three old D1 roots, then preflight and submit the replacement runs.
The focused queue check found no old D1/score job active, and exactly those
three roots were deleted. The clean D0 `current.db` checksums remain
unchanged. **Currently in Phase 5** - preflight and submit the three
lower-temperature replacement D1 NVT jobs using the original, now-absent
round paths. Jobs W `13421`, Ta `13422`, and Ti `13423` are submitted; the
one immediate combined check found all pending. Do not poll. After terminal
completion, validate all replacement trajectories before scoring every frame.
All three replacement jobs are now `COMPLETED 0:0` and all 15 trajectories
passed complete output, command-provenance, finite-summary, and geometry
validation. **Currently in Phase 5** - preflight and submit new score-only
all-frame uncertainty jobs; the no-overwrite preflight and exact submission
cards are recorded. Submit the three jobs, then make only one combined
immediate status check. All selection quantities remain uncalibrated for the
replacement pool. Jobs W `13429`, Ta `13430`, and Ti `13431` are submitted;
the one immediate combined check found all pending. Do not poll. After
terminal completion, validate every replacement all-frame CSV and recalibrate
the replacement-pool physical/risk card.

**Currently in Phase 5** - replacement scoring jobs W `13429`, Ta `13430`,
and Ti `13431` completed `0:0` in 00:25:26, 00:25:19, and 00:25:19. Every
replacement all-frame CSV passed the exact 20-column/25,005-row, source,
finite-field, equilibration, and score-only-output validation. Matching M0
test-MAE-F means recalculated the mandatory U cutoffs as W `0.088824`, Ta
`0.063869`, and Ti `0.038361` eV/A. Perform a read-only replacement-pool
scan of the matching clean-D0 geometry/force envelope, production-frame
risks, collapse extent, and source-gap cardinality. Freeze new gates, gaps,
targets, source-coverage decisions, and qualified-pool-p99 tail caps before
any absolute-U current.db-projected CUR preflight. All old selection cards
remain superseded.

**Current Phase 5 decision** - the replacement-only physical/risk cards are
now frozen. All use volume limits 5% beyond the matching clean-D0 range,
maximum committee force 10% above the matching clean-D0 maximum atomic DFT
force, and minimum distance 5% below the matching clean-D0 minimum:

| Element | U_min (eV/A) | Candidate / final gap (saved frames) | DFT target | p99 tail threshold / cap | Source policy |
|---|---:|---:|---:|---:|---|
| W | 0.088824000 | 25 / 75 | 100 | 14.815457628 / 5 | require all; no quotas |
| Ta | 0.063869000 | 25 / 75 | 40 | 9.027888543 / 2 | no require-all; no quotas |
| Ti | 0.038361000 | 25 / 75 | 50 | 5.851985654 / 2 | no require-all; no quotas |

These values are derived from the replacement pools and current D0 only, not
copied from the deleted D1 card. Ta is no longer globally blocked: only its
safe 0.90, 0.95, and 1.00 subsets may enter CUR. Ti may use only its safe
0.95, 1.00, and 1.05 subsets. No CUR/DFT job has been submitted; the next
step is an element-isolated no-overwrite selection preflight and submission
only with user authorization.

**Superseding Phase 5 decision** - the user has directed removal of both
candidate and final temporal decorrelation stages. The 25/75-frame gaps,
the final-feasibility counts, and the W/Ta/Ti 100/40/50 targets derived from
those counts are superseded and must not be used. Rebuild the selection
policy from all post-equilibration frames with the required absolute-U
cutoff, then hard geometric rejection only for periodic minimum-distance
overlap and a calibrated abnormal-void metric. Preserve finite values,
positive cell volume, unary/PBC validity, and provenance as invariants.
Maximum force, global volume, and source composition are diagnostics/risk
records rather than automatic hard gates. Current.db-projected CUR remains
the diversity selector; final structural similarity/duplicate checks remain,
but no temporal separation is imposed. The DFT budgets must be explicitly
approved or recalibrated after the new geometry-only candidate counts are
known. No selection, DFT, merge, M1, or E1 job is authorized.

**Threshold-calibration research** - the current selector already implements
periodic minimum-distance rejection through `--min-distance`, but it has no
local-void metric or CLI option. A read-only D0 scan established the
element-local distance thresholds as 95% of the D0 minimum distances:
W `2.013521386`, Ta `2.108188744`, and Ti `2.108133328` A. The proposed
void metric is the periodic Delaunay maximum-empty-sphere radius normalized
by `(V/N)^(1/3)`. Its D0 maxima are W `0.822874141`, Ta `0.819366100`, and
Ti `0.822748897`; a provisional 15% tolerance gives candidate limits W
`0.946305262`, Ta `0.942271015`, and Ti `0.946161232`. These are pending
user approval and a full-pool read-only audit; no selection card is frozen.

**Superseding distance decision** - the user set the periodic
minimum-distance threshold to 80%, not 95%, of the matching clean-D0
minimum distance. The active proposed values are W `1.695596956`, Ta
`1.775316838`, and Ti `1.775270170` A. This supersedes the earlier 95%
candidate values. The abnormal-void definition/threshold remains pending;
do not run selection until it is frozen and implemented.

**Implementation/preflight status** - on the user's authorization, the
selection documentation and selector now implement the geometry-first policy:
absolute `U_min`, no temporal gaps, 80%-D0 minimum distance, 115%-D0
normalized periodic empty-sphere limit, current.db-projected CUR, and a p99
tail cap. Python compilation, shell syntax, CLI validation, and W/Ta/Ti
periodic D0 geometry checks passed. The no-overwrite preflight passed for all
three D1 round roots: each matching D0 base has 100 unary 32-atom rows, every
score CSV has 25,005 rows/22,505 post-equilibration frames/five sources, and
every post-equilibration frame meets its matching U cutoff. The approved
selection card is target 100 per element, linear p99 candidate-U threshold,
tail cap 5, no source quota/require-all policy, and descriptor parameters
`r_c=6.0`, `n_max=5`, `l_max=6`, similarity `0.99999`. Selection output
roots remain absent. Submit the three one-node, one-task, 24-hour
no-overwrite SLURM selection jobs, then make one combined immediate status
check.

**Selection submission** - the exact geometry-first cards were submitted as
one-node, one-task, 24-hour protected CUR jobs: W `13440`, Ta `13441`, and
Ti `13442`. Each targets only its matching clean D1 root/current.db and uses
its recorded U/minimum-distance/normalized-void values, `--target 100`,
`--tail-quantile 0.99`, and `--tail-max 5`, without temporal-gap,
volume/force, quota, or require-all-source options. The one permitted
immediate combined `squeue` check found all three `PENDING` (`Priority` for
Ta/Ti; no assigned node reported for W). Do not poll. After terminal
completion, validate the protected outputs before any DFT step.

**Ta selection validation and DFT transition** - a later focused status check
found Ta selection job `13441` `COMPLETED 0:0` while W `13440` and Ti
`13442` remained running. Ta output validation passed: 6,193
geometry-valid candidates plus 16,312 distance/void rejections exactly cover
the 22,505 post-equilibration frames; 100 unique unary 32-atom Ta POSCARs
pass finite/PBC/positive-cell/minimum-distance/normalized-void checks; the
linear p99 tail threshold is `13.338168350` eV/A and exactly five selected
frames are tail frames; CUR ranks, selected files, and source provenance are
complete. The Ta Protocol-A preflight passed with absent label DB/work root,
the matching selected 100 POSCARs, matching Ta POTCAR SHA-256
`b94d0231aa338d2b49887428178c5ebac7fa385cbd6154890af94e8013d269f3`,
ENMAX `223.667`, and auto-ENCUT `290.7671` eV. Ta DFT job `13444` is
submitted with one node, 64 tasks, 24 hours, eight VASP ranks per task and
eight concurrent workers. Its one immediate check found it `PENDING`. Do not
poll. No W/Ti DFT, merge, M1, or E1 job is submitted.

**W/Ti preflight correction** - W/Ti D1 DFT preflight initially stopped because manually expanded POTCAR
  checksums from abbreviated task notes were incorrect. No output path was
  created and no W/Ti DFT job was submitted. Resolution: read the full
checksums directly from the local POTCAR files and rerun the read-only
preflight.

**Ta label-validator correction** - the first read-only Ta D1 label validator
stopped at an INCAR literal-string assertion because VASP writes
`EDIFF = 1E-5` while the expected text used `1e-05`. The values are
numerically identical; no workflow asset was changed. Resolution: compare
numeric INCAR tags numerically and rerun the full read-only validation. The
second validator then stopped because generated INCAR serializes auto-ENCUT
`290.7671` as `290.767`; this is output rounding, not a protocol change.
Resolution: validate printed ENCUT against the auto value with a
`5e-4` eV formatting tolerance and rerun.

**W/Ti selection validation and DFT transition** - a subsequent focused
status check found W `13440` and Ti `13442` `COMPLETED 0:0` (elapsed
`00:57:37` and `00:48:39`), alongside the already completed Ta selection.
W validation passed: 20,120 candidates, 2,385 geometry rejections, 100
finite unary 32-atom POSCARs, p99 U `14.039897016` eV/A, and five selected
tail frames. Ti validation passed: 12,726 candidates, 9,779 geometry
rejections, 100 finite unary 32-atom POSCARs, p99 U `14.002407670` eV/A,
and four selected tail frames. Every candidate/selected/rejection record
passed its matching absolute-U, distance/void, no-gap, CUR-rank, tail-cap,
and provenance checks.

The corrected W/Ti Protocol-A preflights passed with absent DB/work roots,
the matching selected 100 POSCARs, and direct local POTCAR validation:
W SHA-256 `c0897285f1b301314dcc12eb838ce8a777aa860795754598b0626cb818170117`,
ENMAX/auto-ENCUT `223.057/289.9741` eV; Ti SHA-256
`f8e8f1d080d9e9b45e792f1068744b07aba8441d1e7ce11486a5d4c0f5a1479e`,
ENMAX/auto-ENCUT `178.330/231.8290` eV. W DFT job `13445` and Ti DFT job
`13446` were submitted with the same no-overwrite one-node, 64-task,
24-hour, eight-rank/eight-worker card as Ta. Their one combined immediate
check found both `PENDING`. Ta DFT `13444` was `RUNNING` on the preceding
focused check. Do not poll. No merge, M1, or E1 job is submitted.

**Ta DFT completion gate** - a later focused `sacct` check found Ta Protocol-A
DFT job `13444` `COMPLETED 0:0` in `00:56:05`. The next required operation is
read-only validation of the element-local `Ta_D1_labeled.db`: completed VASP
task/source coverage, Protocol-A metadata, finite energy/forces/stress,
32-atom geometry agreement, and absence of EOS/cross-element content. Only
after that validation may a distinct updated D1 DB be merged and atomically
published as Ta `current.db`; then Ta M1 can be preflighted/submitted. W/Ti
DFT status is not checked here.

**Latest Phase 5 Ta transition** - Ta D1 label validation passed, then the
distinct D0 base and D1 labels were merged to the 200-row
`01-nvt-round-1/updated.db`. The first 100 rows remain D0 and the final 100
remain D1; all rows are finite unary 32-atom Ta structures with no EOS data.
After the original D0 checksum was confirmed unchanged, the validated merged
DB was atomically published as Ta `current.db`; its SHA-256 is
`69b733947c729bd4aa5685f8598ceb8a4356be80f5f00797dd3b156e051cf95a`.
The Ta M1 no-overwrite preflight passed with `ENERGY["Ta"] = -11.8578`, an
absent committee path, 10 models, 5 workers, and 5,000 epochs. Job `13448`
is submitted with one node, 5 tasks, 8 CPUs/task, and 48 hours; its one
immediate status was `PENDING (Priority)`. Do not poll. W/Ti labels, DBs,
and models remain untouched.

**Latest Phase 5 Ti label gate** - on the user's completion report, focused
`sacct` found Ti Protocol-A DFT job `13446` `COMPLETED 0:0` in `01:03:53`.
Read-only validation passed: exactly 100 selected sources, manifest tasks,
complete VASP directories, and label DB rows; static Protocol A, finite
energy/forces/stress, and source-geometry agreement all hold. Ti D0 remains
the protected 100-row `current.db`; do not merge, publish, or submit Ti M1
without explicit authorization. W remains unpolled and independent.

**Latest Phase 5 Ti transition** - after explicit user authorization, Ti D1
was merged from distinct D0 base and D1 label DBs to the 200-row
`01-nvt-round-1/updated.db`. The ordered D0 prefix and D1 suffix, finite
unary 32-atom Ti results, absence of EOS data, and unchanged D0 checksum
were all validated before publication. The merged DB was atomically
published as Ti `current.db` (SHA-256
`f2874ac425d45bacf41c1e78503e7ece08c59c477b7ad219926e32f4bada577b`).
The Ti M1 no-overwrite preflight passed with `ENERGY["Ti"] = -7.8951`, an
absent committee path, and the 10-model/5-worker/5,000-epoch policy. Job
`13450` is submitted with one node, 5 tasks, 8 CPUs/task, and 48 hours; its
one immediate status was `PENDING (Resources)`. Do not poll. W remains
untouched and unpolled.

**Latest Phase 5 Ta M1/E1 completion** - the user reported Ta M1 completion
and requested EOS. Focused `sacct` found job `13448` `COMPLETED 0:0` in
`00:07:02`; the corrected `fd -HI` artifact scan and full validation confirm
ten nonempty 5,000-epoch JNN folds with 180/20 train/test partitions, each
D1 record once in test and nine times in train. Fixed-reference E1 completed
without overwrite, using eligible `train-5/5.jnn` (train/test energy MAE
`5.055/5.150` meV/atom). All 57 EOS predictions and phase/all metrics passed
validation. Aggregate E1 raw/aligned MAEs are `66.435829/8.339454` meV/atom,
compared to E0 `16.182558/13.358162`; retain this mixed result for the
scientific decision gate and do not begin D2 automatically.

**Latest Phase 5 W label gate** - on the user's completion report, focused
`sacct` found W Protocol-A DFT job `13445` `COMPLETED 0:0` in `02:01:24`.
Read-only validation passed for exactly 100 selected sources, manifest tasks,
complete VASP directories, and D1 label DB rows; Protocol A, finite results,
and source geometry all agree. W D0 remains the protected 100-row
`current.db`; do not merge, publish, or submit W M1 without explicit
authorization.

**Latest Phase 5 W transition** - after explicit user authorization, the
distinct W D0 base and D1 label DBs were merged to
`01-nvt-round-1/updated.db`. The ordered D0 prefix/D1 suffix, finite unary
32-atom W results, no-EOS content, and unchanged D0 base checksum passed
validation before atomic publication. W `current.db` is now 200 rows with
SHA-256 `c98274fb1b798c7fcaa339c8b77d4aeb295805bf200881c037cf4dceaa37e492`.
The W M1 no-overwrite preflight passed with `ENERGY["W"] = -12.9581` and the
10-model/5-worker/5,000-epoch policy. Job `13453` is submitted with one
node, 5 tasks, 8 CPUs/task, and 48 hours; its one immediate status was
`RUNNING` on `lpsnode03`. Do not poll.

**Latest Phase 5 W/Ti M1/E1 completion** - on the user's completion report,
focused accounting found Ti `13450` and W `13453` `COMPLETED 0:0` in
`00:07:24` and `00:06:45`. Both committees passed ten nonempty 5,000-epoch
model, 180/20-fold, current-D1-coverage, finite-diagnostic, and
train/test-ratio validation. Their no-overwrite, fixed-reference E1 runs
completed and passed 57-point 19/19/19 bcc/fcc/hcp output validation. W
aggregate raw/aligned MAE improves from E0 `131.064897/28.027437` to E1
`64.413224/21.424392` meV/atom; Ti improves from
`36.024202/7.434641` to `14.103997/1.962939`. Preserve all results and do
not begin D2 without a separate scientific decision.

**Current Phase 5 D2 directive** - the user has explicitly directed all
three elements to proceed independently and concurrently to D2, superseding
the prior Ta-only diagnostic hold. Before submission, freeze and record one
new D2 NVT parameter card per element, verify every output path is absent,
and preflight each command against only its matching 200-row D1 database,
M1 committee, and 32-atom seed. No EOS reference may be used as a training
or sampling input.

**Current Phase 5 D2 card** - the cards are frozen in `research-plan.md`
section 8.2.1 and are ready for read-only no-overwrite preflight. Every card
uses the matching 32-atom seed with `--rep 1 1 1`, all ten M1 JNNs, 50,000
steps at 1.0 fs, trajectory/log intervals 10/1, `tau_r=0.10`, friction
`0.02`, one node/five tasks/24 hours, and no partition, account, GPU, or
overwrite setting. W uses 4051.465 K and scales
`0.95,1.00,1.05,1.10,1.15`; Ta uses 3596.065 K and
`0.90,0.925,0.95,0.975,1.00`; Ti uses 2135.265 K and
`0.95,0.975,1.00,1.025,1.05`. D2 selection parameters must be recalibrated
from the D2 pools; no EOS asset is an input.

**Current Phase 5 D2 submission** - after the two corrected read-only
preflight attempts, the third preflight passed for every element: each
matching `current.db` has exactly 200 finite unary 32-atom rows and its
recorded checksum; each seed is its recorded finite/PBC 32-atom POSCAR; all
ten matching M1 JNN paths are nonempty; every D2 root, M2 root, and E2 root
was absent. Template syntax and MD-worker compilation passed. Only each
absent D2 `slurm_logs/` directory was then created. The explicit no-overwrite
NVT cards were submitted as W `13456`, Ta `13457`, and Ti `13458`, each with
one node, five tasks, and 24 hours. The single permitted combined immediate
`squeue` check reported W and Ta `RUNNING` on `lpsnode02` and Ti `PENDING`
with no assigned node. Do not poll. On a later user status/completion
request, validate all 15 D2 trajectories before any score-only submission.

**Current Phase 5 D2 completion validation** - on the user's completion
report, one focused `sacct` check found W `13456`, Ta `13457`, and Ti
`13458` all `COMPLETED 0:0` in `00:50:05`, `00:50:10`, and `00:48:59`.
Read-only validation passed for every element: exactly five expected sources,
each with correct M1-only command provenance, 5,001 finite unary
32-atom/PBC/positive-cell trajectory frames, and 50,001 finite one-step
summary rows. `current.db` checksums are unchanged and all score, selection,
DFT-label, M2, and E2 outputs remain absent. The next staged operation is
three independent no-overwrite M1 `--score-only` submissions that write only
each D2 `uncertainty_all_frames.csv`; after completion, validate every
25,005-row CSV and recalculate D2-only uncertainty/geometry/CUR quantities.

**Current Phase 5 D2 score-only submission** - the no-overwrite preflight
passed for every element: its D1 checksum and 200-row DB are unchanged,
exactly five validated trajectories and ten matching nonempty M1 JNNs exist,
and score/selection/DFT/M2/E2 outputs are absent. Template syntax, scorer
compilation, JSE, and SLURM commands passed. The independent one-node,
one-task, 24-hour score-only jobs were submitted as W `13462`, Ta `13463`,
and Ti `13464`, with only their matching M1 glob, D2 scale list, 10% initial
equilibration discard, and absent `uncertainty_all_frames.csv` output path.
The single permitted immediate combined `squeue` check found all three
`PENDING` (Ta/Ti `Priority`; W no assigned node). Do not poll. On a later
user completion/status request, validate all three CSVs and recalculate the
ten-model M1 test-`MAE-F` absolute-U cutoff per element.

**D2 score-validator correction** - the first read-only CSV validator stopped
at W because it compared the score-command scale-list text literally and did
not allow harmless numeric formatting (`1.00` versus `1`). No asset changed.
Resolution: parse and compare scale values numerically, then rerun the full
CSV validator.
- The first M1 trainer-history JSON inspection assumed the JSON file was
  directly below `train-0`; it is actually under `train-0/jnnhistory/`.
  Resolution: inspect that path and extract final force diagnostics from the
  carriage-return-delimited terminal logs without reading their progress
  streams into memory.
- The first combined persistent-record patch used stale surrounding text and
  did not apply to either task file; no workflow asset changed. Resolution:
  append the D2 calibration record against the current file tails.

**Current Phase 5 D2 score validation** - on the user's completion report,
one focused `sacct` check found score-only jobs W `13462`, Ta `13463`, and Ti
`13464` all `COMPLETED 0:0` in `00:22:50`, `00:23:12`, and `00:22:55`.
After the formatting-only validator correction, every CSV passed: exact
20-column schema, 25,005 finite all-frame rows, five complete 5,001-frame
sources, 500 discarded plus 4,501 production frames per source, and 22,505
production frames per element. Command provenance uses only its matching M1
glob/scale list and score-only output; current D1 DB checksums are unchanged,
and no selection/DFT/M2/E2 output exists. Next, make a D2-only calibration
record from the ten M1 test `MAE-F` values and the production CSVs:
absolute-U cutoff, geometry-gate audit, p99 tail, candidate count, DFT
budget, and projected-CUR card. Do not reuse D1 numerical values or submit
selection before that card is frozen.

**Current Phase 5 D2 calibration** - read-only extraction of the final M1
`MAE-F` values confirms the matching ten-model arithmetic means and
`U_min` values: W `166.580000 meV/A -> 0.166580000 eV/A`, Ta
`144.480000 meV/A -> 0.144480000 eV/A`, and Ti `110.986000 meV/A ->
0.110986000 eV/A`. The post-`U_min` production counts are W `22,505`, Ta
`22,497`, and Ti `22,474`; the required distance/void audit must now run
over exactly those frames. The existing selector computes the prescribed
periodic geometry values only while creating a full CUR transaction, so a
protected audit-only mode is needed to avoid premature candidate/POSCAR/CUR
output with an uncalibrated DFT target. No D2 selection card, selection
output, or DFT submission is authorized yet.

**D2 geometry-audit submission** - the audit-only selector/template
implementation passed Python compilation, SLURM shell syntax, JSE CLI help,
whitespace, and a one-frame in-memory periodic-geometry API check. The
read-only no-overwrite preflight passed for all three elements: matching D1
databases retain their exact 200-row checksums, each score CSV has
`25,005/22,505` all/production frames and the recorded post-`U_min` count,
and its `geometry_audit.csv`, temporary audit sidecar, and CUR output root
are absent. The exact submitted cards are one node, one task, 24 hours, no
partition/account/GPU/overwrite, zero candidate/final gaps, and only the
matching `U_min`, minimum-distance, and normalized-void gates. Jobs W
`13465`, Ta `13466`, and Ti `13467` write only their own protected
`02-nvt-round-2/geometry_audit.csv` plus scheduler/command records. The one
permitted combined immediate check found all `PENDING` (W `(None)`, Ta/Ti
`(Priority)`). Do not poll. On a later completion/status request, validate
all audit CSVs before freezing the D2 projected-CUR selection cards.

**D2 geometry-audit validation and selection-card freeze** - on the user's
completion report, one focused accounting check found W `13465`, Ta `13466`,
and Ti `13467` `COMPLETED 0:0` in `00:32:47`, `00:32:20`, and `00:32:29`.
Each audit CSV exactly covers its post-`U_min` source/frame set with no
duplicates, preserves uncertainty/path/32-atom provenance, has finite
positive geometry diagnostics, and has gate status/reasons identical to the
frozen distance/void comparisons. The geometry-valid counts are W `12,813`,
Ta `21,403`, and Ti `19,420`; p99 tail thresholds are W `1.582394200`, Ta
`2.762254279`, and Ti `0.872469347` eV/A. The D2 cards are now frozen at
`N_DFT=100`, `tail-max=5`, zero temporal gaps, no force/volume/source gate,
and descriptor card `6.0/5/6/0.99999`; their independent budget rationale is
recorded in `research-plan.md` section 8.2.2. The actual CUR selections have
not been submitted. The next operation is an element-isolated no-overwrite
CUR preflight and submission only with explicit authorization.

**Current Phase 5 execution authorization** - the user explicitly authorizes
submission and active monitoring of all three frozen D2 projected-CUR
selections. After each selection completes, validate its protected output and
then preflight/submit the matching Protocol-A DFT batch. Continue monitoring
only through DFT submission; stop monitoring immediately after the DFT jobs
are submitted and make only their one permitted immediate combined status
check.

**D2 CUR submission** - the strict no-overwrite preflight passed for every
element: matching D1 `current.db` has its recorded checksum and 200 rows,
the matching M1 root has ten nonempty JNNs, its score/audit coverage and
geometry-valid count match the frozen card, and selection/label/updated/M2/E2
paths are absent. The exact one-node, one-task, 24-hour CUR cards use only
matching paths, `U_min`, zero gaps, target `100`, linear p99 with tail cap
`5`, frozen distance/void values, and descriptors `6.0/5/6/0.99999`; no
force/volume/source policy or overwrite is passed. W `13469`, Ta `13470`,
and Ti `13471` are submitted. The one permitted immediate combined check
found W `PENDING (None)` and Ta/Ti `PENDING (Priority)`. User-authorized
active monitoring now continues only until each output validates and the
three Protocol-A DFT jobs are submitted.

**D2 CUR monitored completion** - active monitoring found all CUR jobs
terminally successful: W `13469` `COMPLETED 0:0` in `01:42:17`, Ta `13470`
`COMPLETED 0:0` in `02:36:27`, and Ti `13471` `COMPLETED 0:0` in
`02:28:02`. Validate every protected CUR output completely before any DFT
preflight or submission; active monitoring remains authorized through the
subsequent DFT submissions only.

**CUR validator correction** - the first read-only CUR-output validator
stopped at W because it incorrectly expected an `all` row in
`cur_selected_distribution.csv`; the selector instead writes `source`,
`uncertainty_layer`, and `source_layer` aggregates. No workflow asset
changed. Resolution: compare the source and uncertainty-layer aggregates to
the selection summary, then rerun the full validator for all three elements.

**Void round-trip correction** - the second read-only validator found Ta
selected POSCAR `000097.poscar` with a spurious normalized void `4.6658`
after a VASP read, despite the source/candidate geometry being `0.8566`.
The positions and physical cell agree to `1e-15 A`; only an
`~1e-16 A` orthogonal-cell round-off component changes a degenerate Delaunay
simplex. No DFT was submitted. Resolution: remove only sub-`1e-12`-cell-scale
components before the periodic Delaunay calculation, document it, recompile,
recompute the D0 reference values unchanged, and revalidate every selected
VASP POSCAR before DFT preflight.

**D2 CUR validation and DFT submission** - after the round-trip correction,
all three protected CUR outputs passed complete validation. The
candidate/rejection/selected/tail counts are W `12,813/9,692/100/3`, Ta
`21,403/1,094/100/5`, and Ti `19,420/3,054/100/5`; every record exactly
covers the matching audit result, the linear p99/tail cap and descriptor
provenance match the frozen card, and all 300 selected VASP POSCARs are
finite, unary, 32-atom, PBC, geometry-gate-valid, and nonduplicate under the
round-trip-stable void metric. Recomputed clean-D0 minimum-distance/void
references remain unchanged. Protocol-A preflight then passed: selected sets
have 100 POSCARs, D1 DB hashes/200 rows are intact, label/work/updated/M2/E2
paths are absent, local POTCAR identity/ENMAX/auto-ENCUT agrees with the
frozen protocol, and the static INCAR defaults are intact. DFT jobs W
`13477`, Ta `13478`, and Ti `13479` are submitted with one node, 64 tasks,
24 hours, 8 VASP ranks/task, and 8 concurrent workers. Their one immediate
combined check found W `PENDING (None)` and Ta/Ti `PENDING (Priority)`.
Per user instruction, stop monitoring after this check; do not check these
jobs again without a later explicit request.

**Record-update correction** - two combined memory patches used stale
surrounding text while the task record was being extended; the matching
hunks were not applied and no workflow asset changed. Resolution: re-read the
current file tails and apply focused status updates. The final task, notes,
deliverable, and index records now state the DFT submission stop point.

**W/Ta D2 publish correction** - the first atomic-publication validator copied
the validated W merge to an agent-created temporary path ending only in
`.tmp`; ASE could not infer its database type and stopped before publication.
W/Ta `current.db` checksums and row counts remain the protected D1 values;
only the known agent-created W temporary copy exists. Resolution: remove that
temporary copy and retry the same validation/publication using an ASE-readable
temporary name ending in `.tmp.db`.

**D2 DFT completion and independent transitions** - on the user's completion
request, focused accounting found W `13477` and Ta `13478` `COMPLETED 0:0`
in `01:53:44` and `00:59:18`; their 100-row label DBs passed complete
Protocol-A task/source coverage, finite results, 32-atom geometry, and
unchanged-D1 validation. Ti `13479` failed `1:0` after 99 successful VASP
tasks because only `00086_000086` returned `139`; no Ti label DB, merge, or
M2 output exists. Its complete-output preflight passed: 99 task directories
are reusable and complete, the one failed task is incomplete, and the label
DB is absent. The no-overwrite resume job `13494` is submitted with the same
one-node/64-task/8-rank/8-worker static Protocol-A card; its one immediate
check found `PENDING (None)`. Do not poll.

W/Ta each merged their distinct 200-row D1 base and 100-row D2 label DB to a
validated ordered 300-row `updated.db`; every row is finite, unary, 32-atom,
and EOS-free. The validated results were atomically published as `current.db`
with W SHA-256 `a852be39b421e61ff198b9d0d8b1351db5ae2b6729bcfdae6448b3c965bd9309`
and Ta SHA-256
`ee90d87b4f8f10db42d2e82ce2c4e81a38d188293e6428cc90e186c4c128dc7b`.
No Ti current DB changed. W/Ta M2 preflight passed against the frozen
`ENERGY` values and absent M2 roots. M2 jobs W `13495` and Ta `13496` are
submitted with ten models, five workers, 5,000 epochs, one node/five tasks,
eight CPUs/task, and 48 hours; their one immediate combined check found both
`PENDING` (W `(None)`, Ta `(Priority)`). Do not poll.

**D2 terminal status and validation** - on the user's status request,
focused accounting found Ti DFT retry `13494`, W M2 `13495`, and Ta M2
`13496` all `COMPLETED 0:0`, in `00:02:53`, `00:11:51`, and `00:11:59`,
respectively. Ti's resume summary reports exactly 99 reused completed tasks,
one newly successful task, and zero failures. Its completed 100-row
`Ti_D2_labeled.db` passed task/manifest/Protocol-A, finite
energy/forces/stress, unary 32-atom/PBC/positive-cell, static
source-geometry, and label-provenance validation. Ti `current.db` remains
the protected 200-row D1 database with SHA-256
`f2874ac425d45bacf41c1e78503e7ece08c59c477b7ad219926e32f4bada577b`;
no Ti merge, publication, or M2 submission occurred.

W and Ta M2 committees each passed artifact, 5,000-epoch, finite-current-DB,
and disjoint-fold validation: ten nonempty JNN folds, 270/30 train/test
partitions of the matching 300-row D2 state, each row once in test and nine
times in train. W final test MAE-E/MAE-F ranges are
`5.851--10.690 meV/atom` and `169.6--201.9 meV/A`; Ta ranges are
`4.991--8.136 meV/atom` and `135.5--192.2 meV/A`. No E2 output exists.
The next mutable operations require explicit authorization: Ti's distinct
D1-plus-D2 merge, atomic `current.db` publication, and M2 submission; and
separate no-overwrite fixed-reference E2 evaluation of the validated W/Ta
M2 committees.

**Validation correction** - the first read-only W/Ta M2 validator
incorrectly required `MAE-E` and `MAE-F` to occur on one log line. JSE writes
them on consecutive lines, so it stopped without changing any asset.
Resolution: parse the final energy and force diagnostic lines independently;
the corrected full validation passed.

**Ti D2 transition authorization** - the user explicitly authorizes Ti's
distinct D1-plus-D2 merge, atomic `current.db` publication, and M2
submission. First run an element-isolated no-overwrite preflight against the
validated 200-row D1 base, 100-row D2 labels, absent updated/M2/E2 paths,
and frozen `ENERGY["Ti"] = -7.8951`; then merge and validate the ordered
300-row DB before publication. Submit only the validated Ti M2 committee
through the standard one-node, five-task, 5,000-epoch SLURM card and make
one immediate status check.

**Ti D2 merge/publication and M2 submission** - the corrected no-overwrite
preflight passed with the protected 200-row D1 SHA-256
`f2874ac425d45bacf41c1e78503e7ece08c59c477b7ad219926e32f4bada577b`,
the validated 100-row D2 label SHA-256
`346b004cae39d88ca53f772ac714a1fd815e6c3ad4a95842dec5aa2fec64d779`,
absent updated/M2/E2 paths, and `ENERGY["Ti"] = -7.8951`. The active
`vasp_batch_dft.py merge` created the distinct 300-row
`02-nvt-round-2/updated.db`. Its ordered D0/D1/D2 `100/100/100` segments,
finite unary 32-atom results, no-EOS provenance, and exact source-row
identity with the protected base and D2 label DB passed validation.

The validated merge was copied to an agent-created same-filesystem temporary
`*.tmp.db`, checksum/contents revalidated, and atomically published as Ti
`current.db` with SHA-256
`cfd5f2f5141c46f7b3636b2eb70d65b71d814e0fa4658c51aaa8ac44d2eb9196`.
The post-publication M2 preflight passed with the absent committee/E2 paths
and a 300-row finite unary Ti DB. Job `13512` is submitted with the standard
no-overwrite card: one node, five tasks, eight CPUs/task, 48 hours, ten
models, five workers, and 5,000 epochs. Its one permitted immediate check
reported `PENDING (None)` with no assigned node. Do not poll. On a later
completion/status request, validate this M2 committee before any Ti E2
evaluation.

**Ti preflight correction** - the first read-only merge preflight
incorrectly required the entire D1 base to share the D0
`nninit-poscars` tag. It stopped without creating an output; the actual
validated order is 100 D0 rows followed by 100 D1 selected rows. Resolution:
check the two D1 segments separately; the corrected preflight passed.

**E2 authorization** - the user explicitly authorizes independent
fixed-reference E2 evaluation for W, Ta, and Ti. Accounting confirms Ti M2
job `13512` is terminal `COMPLETED 0:0`; validate its committee and perform
one read-only no-overwrite preflight for all three M2 committees, matching
300-row current DBs, and fixed EOS references before direct element-isolated
`eos_check_jnn.py` evaluations.

**M2/E2 completion** - Ti M2 job `13512` completed `0:0` in `00:13:40`.
The same no-overwrite E2 preflight fully validated all three M2 committees:
ten nonempty 5,000-epoch JNN folds, 270/30 train/test partitions of only the
matching 300-row D2 current DB, each row once in test and nine times in
train. Fixed EOS metadata/reference pairs each have 57 matching finite
records with 19 bcc, 19 fcc, and 19 hcp points; all three `E2_M2` output
paths were absent.

The independent W/Ta/Ti direct fixed-reference evaluations completed and
their protected outputs passed full artifact, selection, 57-point
phase/key/provenance, finite prediction/metric, current-DB checksum, and
nonempty-plot validation. The selected model / eligible-count / aggregate
raw and phase-aligned MAE are:

| Element | M2 model | Eligible / 10 | Raw / aligned MAE (meV/atom) |
|---|---|---:|---:|
| W | `train-9/9.jnn` | 9 | `67.567137 / 23.830581` |
| Ta | `train-3/3.jnn` | 8 | `51.670502 / 9.654377` |
| Ti | `train-8/8.jnn` | 9 | `17.053634 / 3.492649` |

Only normal per-selected-model JSE inference cache libraries were created.
The W/Ta/Ti D2 workflows are now complete through M2/E2. Preserve the
mixed EOS outcomes and require a separate scientific decision before any D3
sampling, selection, DFT, or training.

**E2 preflight reporting correction** - the first all-element preflight
completed every validation assertion but then stopped while formatting a
relative selected-JNN path because that path had not been resolved. It
created no E2 output. Resolution: resolve the selected JNN before formatting;
the corrected selection preflight passed for W/Ta/Ti.
