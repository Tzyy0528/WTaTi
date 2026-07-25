# Task Plan: D1 Reselection from M0 Log Error

## Goal
Produce a replacement, independently auditable D1 CUR selection for W, Ta,
and Ti using a log-derived `U_min` and the retained D1 scoring inputs.

## Phases
- [x] Phase 1: Remove the revoked D1-selection-and-later workflow state.
- [x] Phase 2: Restore each element-local `current.db` from D0 and verify it.
- [x] Phase 3: Obtain the user-approved aggregate of the ten M0 test
  `MAE-F` values.
- [x] Phase 4: Extract the per-model errors, record each element's `U_min`,
  and prepare protected selection commands.
- [x] Phase 5: Submit and validate the replacement selection after command
  approval.
- [x] Phase 6: Review and deliver.

## Key Questions
1. Should `U_min` use the mean, maximum, median, or another specified
   aggregate of the ten final M0 test `MAE-F` values per element?

## Decisions Made
- Retain only the D1 MD trajectories and all-frame scoring CSVs as D1 inputs.
- Use the final right-hand (test) `MAE-F` value from every M0 model log; no
  production-pool percentile is a valid cutoff.
- Use the arithmetic mean of the ten model-level final test `MAE-F` values
  for the element's single `U_min`. Convert meV/A to eV/A.
- Keep the D1 `target=100`, descriptor settings, and original scale grid.
  Do not impose source balancing, frame gaps, tail caps, or physical gates
  without explicit approval.

## Errors Encountered
- The login-node `python3` lacks ASE. Snapshot verification used standard
  SQLite row counts and SHA-256 hashes instead.
- The first CUR-submission shell helper expanded its local `x` variable before
  assignment under `set -u`; no job was submitted. Resolved by assigning
  local variables on separate lines before constructing the round path.
- The first local validation matched the selected-POSCAR summary file as well
  as the selected-POSCAR directory. Resolved by requiring the matched path to
  be a directory; the corrected validation passed for all three elements.

## Status
**Complete** - CUR jobs 13128 (W), 13129 (Ta), and 13130 (Ti) completed
with exit code 0. Each output has 22,505 finite candidates and 100 unique,
finite unary 16-atom selected POSCARs. Protocol-A DFT labeling is tracked in
the fresh `09_D1_DFT_labeling` task.
