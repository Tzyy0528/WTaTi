# Task Plan: Clean-FCC M3 Validation and E3 Evaluation

## Goal
Validate all completed W, Ta, and Ti M3 committee folds, then run protected
fixed-reference E3 EOS evaluations for the matching eligible committees.

## Phases
- [x] Phase 1: Confirm terminal M3 scheduler status and locate E3 entry points.
- [x] Phase 2: Validate M3 committee artifacts, folds, diagnostics, and D3 provenance.
- [x] Phase 3: Verify E3 no-overwrite/isolation preflight and run fixed EOS evaluation.
- [x] Phase 4: Validate E3 outputs and deliver.

## Key Questions
1. Does every M3 committee contain ten nonempty 5,000-epoch models with
   complete disjoint 360/40 D3 folds and finite diagnostics?
2. Is every E3 input restricted to the matching M3 committee and unchanged
   element-local Protocol-B EOS reference?
3. Do E3 outputs remain isolated, complete, and finite without entering any
   training database?

## Decisions Made
- The user explicitly authorized E3 after M3 completion.
- Only a fully validated M3 committee may be evaluated.
- E3 uses the fixed EOS reference and does not modify `current.db`.
- All W/Ta/Ti M3 committees passed the fold/provenance/diagnostic audit.
  The evaluator's ratio-1.25 policy leaves all ten folds eligible; it will
  select W `train-3/3.jnn`, Ta `train-8/8.jnn`, and Ti `train-8/8.jnn`.
- The user explicitly authorized deletion of only the failed partial W
  `evaluations/E3_M3/` directory and a canonical rerun through
  `python3 src/eos_check_jnn.py` with JSE loaded for inference.

## Errors Encountered
- Read-only validator initially failed while importing `src/eos_check_jnn.py`
  with `importlib`: the temporary module was not registered in `sys.modules`,
  which prevented `dataclass` annotation resolution. Retry after registering
  the module; no project artifacts were changed.
- The documented `jse src/eos_check_jnn.py ...` invocation failed for W
  after creating its protected `evaluations/E3_M3/` directory: JSE's Python
  runner does not define `__file__`, while `predict_eos()` dereferences it to
  find the Groovy evaluator. The shell stopped before Ta/Ti. Inspect the W
  partial output read-only and obtain explicit cleanup authorization before a
  canonical rerun; do not overwrite or delete it implicitly.

## Status
**Complete** - M3 provenance/diagnostic validation and protected E3 execution
and output/isolation validation passed for all three elements.
