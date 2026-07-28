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
- `<X>-potential/fcc-restart/current.db`: atomically published clean 100-row
  D0 databases.
- `<X>-potential/fcc-restart/model_versions/M0_from_D0/train-committee/`:
  validated ten-model M0 committees.
- `<X>-potential/fcc-restart/evaluations/E0_M0/`: clean fixed-reference E0
  predictions, metrics, selection records, and plots.
- `<X>-potential/fcc-restart/01-nvt-round-1/slurm_logs/`: roots for the
  completed lower-temperature D1 scheduler and command records.
- `<X>-potential/fcc-restart/01-nvt-round-1/md/`: validated replacement D1
  trajectories and per-step summaries.
- `<X>-potential/fcc-restart/01-nvt-round-1/uncertainty_all_frames.csv`:
  validated replacement all-frame uncertainty scores.
