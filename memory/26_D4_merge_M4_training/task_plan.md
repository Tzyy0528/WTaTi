# Task Plan: D4 Merge and M4 Committee Training

## Goal
Independently merge each validated 100-row D4 label database with its matching 400-row D3 `current.db`, publish the validated 500-row D4 successor, and submit protected M4 committee training.

## Phases
- [x] Phase 1: Review D4 label provenance, merge/training controls, output protections, and resource settings.
- [x] Phase 2: Merge and validate W, Ta, and Ti D4 successors; publish only validated element-local `current.db` files.
- [x] Phase 3: Preflight and submit independent M4 committee-training jobs.
- [x] Phase 4: Record job IDs and deliver; do not monitor or start E4 automatically.

## Key Questions
1. Are all bases, label DBs, and protected D4 output paths independent, complete, and suitable for a 500-row merge?
2. Do the M4 commands train only from their matching published D4 database and preserve no-overwrite protections?

## Decisions Made
- User explicitly authorized D4 merges and M4 training.
- EOS references remain validation-only; E4 is outside this authorization.

## Errors Encountered
- Strict ASE-row comparison found that the current
  `src/vasp_batch_dft.py::merge_databases()` implementation does not copy
  VASP `calculator_parameters` from new label rows: it writes `row.toatoms()`
  plus key-value/data metadata, retaining the calculator name and all
  training-relevant energy/force/stress results but yielding an empty
  calculator-parameter mapping. This is the established behavior of the
  executable merge path (also present in the prior D3 `current.db`);
  provenance remains in the immutable D4 label DB. Resolution: validate
  exact structures, results, row order, and key-value/data metadata while
  recording this non-training metadata limitation; do not modify the merge
  implementation during an authorized production transition.

## Status
**Complete** - Validated 500-row D4 successors were atomically published as
W/Ta/Ti `current.db`. M4 jobs W `13275`, Ta `13276`, and Ti `13277` were
submitted with protected ten-model, five-worker, 5,000-epoch settings. A
focused completion check on 2026-07-27 found all three jobs `COMPLETED 0:0`.
The user explicitly deferred E4; no E4 action was started.
