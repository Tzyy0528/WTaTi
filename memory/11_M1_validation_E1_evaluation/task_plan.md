# Task Plan: M1 Fixed-Reference E1 Evaluation

## Goal
Evaluate each validated M1 committee against its unchanged element-local
Protocol-B EOS reference, compare E1 with E0, and preserve validation-only
outputs outside all training databases.

## Phases
- [x] Phase 1: Confirm M1 roots, E0 references, and protected E1 output
  roots.
- [x] Phase 2: Select an eligible reporting model from each M1 committee and
  run E1 prediction/metric evaluation.
- [x] Phase 3: Validate E1 outputs and compare them with E0.
- [x] Phase 4: Review and deliver.

## Key Questions
1. Do the E1 inputs and outputs remain isolated by element and separate from
   all training databases?
2. How do E1 raw and phase-aligned EOS metrics compare with E0?

## Decisions Made
- Reuse the fixed Protocol-B EOS reference unchanged.
- E1 is validation-only and must not modify `current.db` or any training DB.
- Do not start D2 in this task.

## Errors Encountered
- None.

## Status
**Complete** - E1 output is validated for all three elements. W and Ti
regressed in both aggregate raw and phase-aligned EOS errors; Ta improved
phase-aligned shape but regressed in raw cross-phase energy. `current.db` was
not changed.
