# Task Plan: D1 Merge and M1 Training

## Goal
Merge each validated element-local D1 label DB with its D0 base, publish the
validated 200-row D1 `current.db`, and submit independent M1 committees.

## Phases
- [x] Phase 1: Confirm distinct base/label/updated paths and protected
  no-overwrite state.
- [x] Phase 2: Merge and validate the three 200-row D1 successors.
- [x] Phase 3: Publish the validated successors as element-local
  `current.db` and audit Protocol-A training energy settings.
- [x] Phase 4: Review the protected M1 training configuration and submit the
  three independent committees.
- [x] Phase 5: Validate completed committees and deliver.

## Key Questions
1. Does every successor preserve its 100 D0 rows and append exactly its own
   100 D1 rows?
2. Are the M1 inputs, outputs, and training settings isolated by element?

## Decisions Made
- Merge only through `src/vasp_batch_dft.py merge`, using distinct base,
  labeled, and `updated.db` paths.
- Train M1 from each validated 200-row `current.db` only after publication.
- Use ten models, five concurrent workers, and 5000 epochs for M1.
- Do not start E1 or D2 in this task.

## Errors Encountered
- None.

## Status
**Complete** - M1 jobs 13138 (W), 13139 (Ta), and 13140 (Ti) completed with
exit code `0:0`. Each committee has ten nonempty JNN files, disjoint 180/20
train/test folds covering all 200 D1 rows, and finite final diagnostics. The
next stage is the separate E1 fixed-reference EOS evaluation.
