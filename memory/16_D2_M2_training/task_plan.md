# Task Plan: D2 M2 Committee Training

## Goal
Train independent ten-model M2 NNAP committees from only the validated
300-row D2 `current.db` files.

## Phases
- [x] Phase 1: Audit D2 database state and frozen Protocol-A `ENERGY` values;
  confirm protected committee outputs and training resources.
- [x] Phase 2: Submit independent W, Ta, and Ti M2 committee training jobs.
- [x] Phase 3: Validate committee models, fold coverage, and diagnostics.

## Key Questions
1. Do the active `ENERGY` constants agree with the frozen Protocol-A policy
   before M2 training?
2. Does every committee contain ten nonempty models with disjoint folds
   covering all 300 rows?

## Decisions Made
- Train from only the corresponding element-local 300-row `current.db`.
- Use ten models, five concurrent training workers, eight threads per worker,
  and 5,000 epochs.
- Do not run E2 or subsequent D3 sampling in this task.
- The three protected M2 committee roots were absent at preflight; submission
  must not set `OVERWRITE=1`.

## Errors Encountered
- The first post-completion validation script attempted to put ASE
  `row.symbols` lists in a set and raised `TypeError: unhashable type: 'list'`;
  this is a validator-only error, not a training failure. Resolve by comparing
  each row symbol list directly.
- The corrected validator initially treated `row.symbols` as one
  element-level symbol rather than one symbol per atom, causing an input-symbol
  assertion before fold checks. Resolve by testing the set of per-atom symbols;
  no data were changed.

## Status
**Complete** - jobs W `13162`, Ta `13163`, and Ti `13164` completed with
zero exit status, and all three M2 committees passed model, fold, epoch,
diagnostic, and element-isolation validation.
