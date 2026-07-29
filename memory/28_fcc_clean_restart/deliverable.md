# Deliverable: Clean FCC 2x2x2 Restart

## Outcome
The prior FCC workflow has been removed. A new, correct restart begins only
from the retained four-atom FCC source POSCARs. Fresh 32-atom `2 2 2` seeds
are published and validated for W, Ta, and Ti; fresh D0 Protocol-A VASP
labeling, M0 training, and fixed-reference E0 validation completed and passed
artifact/isolation validation.

## Key Results / Decisions
- No prior FCC-generated asset may be reused.
- D4/M4 databases/models and fixed EOS references remain protected.
- Every clean D0 pool contains 100 validated, unique 32-atom FCC-derived
  candidates from only its matching clean `2 2 2` seed.
- D0 label jobs W `13381`, Ta `13382`, and Ti `13383` are queued after
  no-overwrite preflight; all completed `0:0` and their three 100-row
  32-atom label DBs passed validation.
- The matching label DBs are atomically published as new clean FCC D0
  `current.db` files; M0 jobs W `13395`, Ta `13396`, and Ti `13397` are
  submitted after preflight.
- M0 committees have ten valid 5,000-epoch models and complete disjoint
  90/10 D0 coverage; E0 uses only the immutable 57-point EOS references.
- At user direction, all old D1 round roots were deleted after confirming no
  old D1/score job was active; their trajectories, score CSVs, and
  old-D1-derived selection cards are not retained or reused.
- Lower-temperature `1.10 Tm` replacement D1 jobs W `13421`, Ta `13422`,
  and Ti `13423` completed `0:0` after a no-overwrite preflight; all
  replacement trajectories passed complete finite-output validation. Their
  score-only uncertainty cards are preflighted and all later selection values
  must be recalibrated from scratch.
- Replacement all-frame score-only jobs W `13429`, Ta `13430`, and Ti
  `13431` completed `0:0` (00:25:26, 00:25:19, and 00:25:19). Each
  replacement 25,005-row CSV passed complete all-frame and score-only-output
  validation.
- Recomputed mandatory absolute cutoffs are W `0.088824`, Ta `0.063869`,
  and Ti `0.038361` eV/A from the matching ten final M0 test `MAE-F`
  diagnostics. Replacement U min/mean/max are W
  `4.09499076e-10/4.95135792/24.9671306`, Ta
  `2.82847667e-09/643.197106/9715.76767`, and Ti
  `1.15446185e-09/131.15245/5477.57987` eV/A.
- Replacement-only selection cards are frozen. They use the matching
  clean-D0 volume/force/minimum-distance envelopes, 25/75 saved-frame
  candidate/final gaps, and no source quotas. W can require all five
  sources; Ta and Ti have only safe subsets after transparent collapse gates.
  The DFT targets are W 100, Ta 40, and Ti 50; qualified-pool p99 tail
  threshold/cap pairs are W `14.815457628/5`, Ta `9.027888543/2`, and Ti
  `5.851985654/2` eV/A/count.
- No CUR selection or later DFT/merge/training/EOS job has been submitted.
  The old high-temperature D1 cards remain superseded.
- The user subsequently superseded the provisional 25/75-frame temporal
  decorrelation policy. The W 100, Ta 40, and Ti 50 targets were derived
  from the removed 75-frame feasibility rule and are no longer active.
  Future selection will use absolute-U screening, periodic
  minimum-distance and abnormal-void geometry gates, current.db-projected
  CUR, a capped extreme-U layer, and final structural duplicate checks.
  Void thresholds and DFT budgets require read-only recalibration before
  any selection submission.
- The new policy is now documented and implemented. Its active clean-D1
  values are a 100-structure target per element, 80% of clean-D0 minimum
  pair distance, 115% of clean-D0 normalized maximum-empty-sphere value,
  geometry-valid p99 U tail threshold, tail cap 5, and no temporal frame
  gaps. Protected CUR jobs W `13440`, Ta `13441`, and Ti `13442` are
  submitted; selection output validation is pending.
- Ta selection job `13441` subsequently completed and passed full selection
  validation: 6,193 candidates, 16,312 geometry rejections, 100 selected
  32-atom Ta structures, and p99 tail threshold `13.338168350` eV/A with
  five selected tail structures. Ta Protocol-A DFT job `13444` is submitted
  without overwrite; W/Ti selection validation remains pending.
- W/Ti selection jobs `13440`/`13442` subsequently completed and passed full
  validation. W has 20,120 candidates/2,385 geometry rejections/p99
  `14.039897016` eV/A/five selected tail frames; Ti has 12,726/9,779/p99
  `14.002407670` eV/A/four selected tail frames. Both have exactly 100
  selected finite unary 32-atom structures. Protocol-A DFT jobs W `13445`
  and Ti `13446` are submitted without overwrite; label validation is
  pending.
- Ta D1 labels passed full Protocol-A, finite-result, and selected-geometry
  validation. The 100-row Ta D0 base and 100-row D1 label DB were merged in
  order, then atomically published as the 200-row Ta `current.db` with
  SHA-256 `69b733947c729bd4aa5685f8598ceb8a4356be80f5f00797dd3b156e051cf95a`;
  the distinct `01-nvt-round-1/updated.db` is retained.
- Ta M1 job `13448` completed successfully with ten valid 5,000-epoch
  180/20 folds. The initial missing-artifact report was corrected: `fd`
  respected `.gitignore` and hid generated JNN/DB/log files. E1 then
  completed on only the fixed Ta EOS reference. Aggregate raw/aligned MAEs
  are `66.435829/8.339454` meV/atom versus E0
  `16.182558/13.358162`, so raw cross-phase error regressed but
  phase-aligned shape error improved.
- Ti DFT job `13446` completed successfully and its 100 D1 labels passed
  complete Protocol-A, task/manifest, finite-result, and source-geometry
  validation. After explicit authorization, Ti D1 was merged and atomically
  published as a 200-row current DB with SHA-256
  `f2874ac425d45bacf41c1e78503e7ece08c59c477b7ad219926e32f4bada577b`.
  Ti M1 job `13450` completed with a valid ten-model committee and E1
  improves aggregate raw/aligned EOS MAE from `36.024202/7.434641` to
  `14.103997/1.962939` meV/atom.
- W DFT job `13445` completed successfully and its 100 D1 labels passed
  complete Protocol-A, task/manifest, finite-result, and source-geometry
  validation. After explicit authorization, W D1 was merged and atomically
  published as a 200-row current DB with SHA-256
  `c98274fb1b798c7fcaa339c8b77d4aeb295805bf200881c037cf4dceaa37e492`.
  W M1 job `13453` completed with a valid ten-model committee and E1
  improves aggregate raw/aligned EOS MAE from `131.064897/28.027437` to
  `64.413224/21.424392` meV/atom.
- Frozen clean-FCC D2 NVT cards are recorded in `research-plan.md` section
  8.2.1. Read-only no-overwrite preflight passed for all matching 200-row D1
  DBs, 32-atom seeds, ten-model M1 committees, and absent D2/M2/E2 outputs.
  D2 jobs W `13456`, Ta `13457`, and Ti `13458` were then submitted
  independently; the one immediate check found W/Ta running and Ti pending.
  Do not poll.
- All D2 jobs subsequently completed `0:0` and all 15 element-isolated
  trajectories passed full provenance, frame-count, finite-result, unary,
  PBC, positive-cell, and summary validation. The next stage is M1
  all-frame score-only evaluation; no D2 score, selection, label, M2, or E2
  output exists yet.
- No-overwrite score-only preflight then passed for all D2 trajectories and
  matching M1 committees. Independent full-frame scoring jobs W `13462`, Ta
  `13463`, and Ti `13464` are submitted; one immediate combined check found
  all pending. Do not poll.
- All three D2 score-only jobs subsequently completed `0:0`; their CSVs pass
  exact schema, source/frame/equilibration, finite-score, provenance, and
  score-only-output validation (25,005 all-frame and 22,505 production rows
  per element). D2 selection calibration remains the next unsatisfied gate.
- The D2 geometry audits completed successfully and passed full
  post-`U_min` coverage/provenance/periodic-gate validation. Frozen D2 CUR
  cards are W `12,813 / 1.582394200`, Ta `21,403 / 2.762254279`, and Ti
  `19,420 / 0.872469347` for geometry-valid candidates / p99 U (eV/A), all
  with 100-label target and tail cap 5. Actual CUR selection and DFT remain
  unsubmitted.
- User-authorized D2 CUR jobs W `13469`, Ta `13470`, and Ti `13471` are
  submitted after strict no-overwrite preflight; active monitoring continues
  only until validated CUR outputs lead to DFT submission.
- All D2 CUR jobs completed `0:0`; their candidates, rejections, selected
  POSCARs, current-DB-projected CUR provenance, tail caps, and source
  distributions passed full validation. A VASP round-trip-stable periodic
  void calculation was added and verified before DFT.
- Protocol-A D2 DFT jobs W `13477`, Ta `13478`, and Ti `13479` are submitted
  with independent selected inputs, output DBs, and work roots. Monitoring
  stops after their one immediate pending-status check by user instruction.
- W/Ta DFT completed and validated; their D2 100-label additions were merged
  and atomically published to 300-row current DBs. M2 jobs `13495` /
  `13496` completed and their ten 5,000-epoch 270/30-fold committees passed
  validation; fixed-reference E2 remains unrun.
- Ti retry job `13494` completed after its one transient VASP failure. Its
  aggregate 100-row D2 label DB now passes complete Protocol-A, task,
  finite-result, and source-geometry validation, while Ti `current.db`
  was subsequently authorized for merge. The D0/D1/D2 100/100/100 merge
  passed validation and was atomically published as the 300-row Ti
  `current.db` (SHA-256
  `cfd5f2f5141c46f7b3636b2eb70d65b71d814e0fa4658c51aaa8ac44d2eb9196`).
  Ti M2 job `13512` completed and passed committee validation.
- All independent clean-FCC D2 workflows now complete through M2/E2. The
  fixed-reference E2 aggregate raw/aligned EOS MAEs are W
  `67.567137/23.830581`, Ta `51.670502/9.654377`, and Ti
  `17.053634/3.492649` meV/atom. Outputs are isolated under each
  `<X>-potential/fcc-restart/evaluations/E2_M2/`; no D3 work has started.

## How to Use / Verify
- Before D0 generation, verify every new FCC seed is a 32-atom exact `2 2 2`
  repeat of only its matching four-atom source.

## Files Changed
- `memory/28_fcc_clean_restart/`: clean restart task record.
- `structures/<X>_fcc_restart/<X>-fcc-seed-32.poscar`: new validated
  element-local 32-atom FCC seeds.
- `<X>-potential/fcc-restart/00-input/seed-generation/nninit-poscars/`:
  fresh validated 100-frame 32-atom D0 pools.
- `<X>-potential/fcc-restart/00-input/slurm_logs/`: clean D0 scheduler-log
  directories.
- `<X>-potential/fcc-restart/00-input/<X>_FCC_D0_labeled.db`: validated
  element-local 100-row D0 Protocol-A label DBs.
- `<X>-potential/fcc-restart/current.db`: atomically published clean 200-row
  D1 databases for W, Ta, and Ti.
- `<X>-potential/fcc-restart/model_versions/M0_from_D0/train-committee/`:
  validated ten-model M0 committees.
- `<X>-potential/fcc-restart/evaluations/E0_M0/`: clean fixed-reference E0
  predictions, metrics, selection records, and plots.
- `<X>-potential/fcc-restart/evaluations/E1_M1/`: validated fixed-reference
  W, Ta, and Ti M1 EOS predictions, selection records, metrics, and plots.
- `<X>-potential/fcc-restart/01-nvt-round-1/slurm_logs/`: roots for the
  completed lower-temperature D1 scheduler and command records.
- `<X>-potential/fcc-restart/01-nvt-round-1/md/`: validated replacement D1
  trajectories and per-step summaries.
- `<X>-potential/fcc-restart/01-nvt-round-1/uncertainty_all_frames.csv`:
  validated replacement all-frame uncertainty scores.
- `<X>-potential/fcc-restart/01-nvt-round-1/updated.db`: retained validated
  D0-plus-D1 merge artifacts for W, Ta, and Ti.
- `<X>-potential/fcc-restart/02-nvt-round-2/slurm_logs/`: D2 scheduler-log
  roots created after no-overwrite preflight.
- `src/absolute_u_projected_cur_selection.py`: protected audit-only periodic
  geometry mode for pre-selection, post-`U_min` calibration.
- `scripts/slurm/run_absolute_u_projected_cur.slurm`: audit-only submission
  support with no-overwrite geometry-audit output protection.
- `docs/unary_workflow.md`: required geometry-audit stage before D2 CUR-card
  calibration.
- `research-plan.md`: frozen clean-FCC D2 selection cards and independent
  DFT-budget rationale.
