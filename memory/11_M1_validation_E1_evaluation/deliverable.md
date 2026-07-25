# Deliverable: M1 Fixed-Reference E1 Evaluation

## Outcome
E1 fixed-reference EOS evaluation completed and passed output validation for
W, Ta, and Ti. The output is validation-only; no training DB changed.

## Key Results / Decisions
- M1 committees are validated and ready for evaluation.
- E1 output is validation-only and element-isolated.
- W and Ti regressed in both aggregate raw and phase-aligned EOS errors.
  Ta improved phase-aligned EOS shape but regressed in raw cross-phase energy.

## How to Use / Verify
- Results are under `results/<X>_eos_benchmark/evaluations/E1_M1/`.
- Compare `eos_metrics.csv` with E0 before deciding whether to continue to D2.

## Files Changed
- `memory/11_M1_validation_E1_evaluation/`: E1 evaluation plan, notes, and
  deliverable.
