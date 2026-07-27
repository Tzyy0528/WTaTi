# Task Plan: D2 Database Merge

## Goal
Create and validate independent 300-row D2 successors by merging each
200-row D1 `current.db` with only its matching 100-row D2 label DB.

## Phases
- [x] Phase 1: Confirm base/label/output isolation, row counts, checksums, and
  protected output/publish state.
- [x] Phase 2: Run the three protected merges and validate the outputs.
- [x] Phase 3: Publish validated successors and deliver.

## Key Questions
1. Does each 300-row successor preserve all 200 D1 rows before its 100 D2
   labels?
2. Are W, Ta, and Ti DB inputs and outputs strictly isolated?

## Decisions Made
- Use `src/vasp_batch_dft.py merge` only after D2 label-DB validation.
- Keep the base DB, D2 label DB, and 300-row `updated.db` distinct.
- Do not start M2 training or E2 in this task.

## Errors Encountered
- None.

## Status
**Complete** - all validated 300-row successors were atomically published as
their matching element-local `current.db`. M2 is a separate, unstarted stage.
