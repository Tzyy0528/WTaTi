# Task Plan: M3 E3 Fixed-Reference EOS Validation

## Goal
Validate each completed element-local M3 committee against its unchanged, validation-only 57-point Protocol-B EOS reference without changing any training database.

## Phases
- [x] Phase 1: Verify M3 committee completion, artifact integrity, and fold coverage.
- [x] Phase 2: Preflight protected E3 output paths, fixed references, and EOS evaluation commands.
- [x] Phase 3: Run independent W, Ta, and Ti E3 evaluations with the documented lightweight JSE evaluator.
- [x] Phase 4: Validate EOS artifacts and deliver the E3 comparison; do not alter `current.db`.

## Key Questions
1. Does each M3 committee contain ten valid 5,000-epoch models with complete disjoint 360/40 coverage of only its matching D3 database?
2. Are the fixed 57-point Protocol-B references intact and distinct from all training data?
3. Can each E3 evaluation be submitted without overwriting an existing output?

## Decisions Made
- E3 will use only the established fixed EOS reference for its matching element.
- EOS reference structures and labels remain validation-only and will not enter any `current.db`.
- M3 completed successfully for W `13221`, Ta `13222`, and Ti `13223`.
  Each committee passed ten-model, 5,000-epoch, disjoint 360/40-fold
  validation against only its matching 400-row D3 database.
- As in E0--E2, run `src/eos_check_jnn.py` directly after `module load jse`.
  This repository-designated 57-structure single-model inference is a
  lightweight validation command, not a DFT, training, or MD workload.
- E3 results are retained for comparison only. They do not support an
  automatic D4 start: W regressed strongly in raw EOS MAE, while Ta and Ti
  recovered only partly from E2 and remain above their E0 raw EOS baselines.

## Errors Encountered
- The initial read-only M3 validator used the system `python3`, which lacks
  NumPy. Resolution: rerun under the repository-required `module load jse`
  environment; no workflow asset was modified.

## Status
**Complete** - all E3 outputs passed protected artifact validation; `current.db`
and Protocol-B EOS references remain unchanged.
