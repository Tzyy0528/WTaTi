# Deliverable: M2 E2 Fixed EOS Validation

## Outcome
E2 fixed-Protocol-B EOS validation completed and passed artifact validation
for W, Ta, and Ti. All results are validation-only and no `current.db` changed.

## Key Results / Decisions
- E2 will use fixed Protocol-B validation references only.
- W, Ta, and Ti output paths will remain independent and protected.
- Selected M2 reporting models: W `train-9/9.jnn`, Ta `train-3/3.jnn`, and
  Ti `train-0/0.jnn`.
- Each E2 output contains ten-model selection audit, 57 finite matched
  predictions, bcc/fcc/hcp/all metrics, and two nonempty plots.
- W recovered relative to E1 but remains worse than E0; Ta regressed relative
  to E1 and E0; Ti improved phase-aligned shape but regressed raw EOS error.

## How to Use / Verify
- Review `results/<X>_eos_benchmark/evaluations/E2_M2/eos_metrics.csv`
  against the matching E1 and E0 files. Detailed comparison and grid-minimum
  shifts are in `memory/17_M2_E2_eos_validation/notes.md`.
- Do not begin D3 automatically; review the per-element regressions and
  authorize an adjusted next-stage configuration first.

## Files Changed
- `memory/17_M2_E2_eos_validation/`: E2 validation task record.
- `results/W_eos_benchmark/evaluations/E2_M2/`: validated W EOS results.
- `results/Ta_eos_benchmark/evaluations/E2_M2/`: validated Ta EOS results.
- `results/Ti_eos_benchmark/evaluations/E2_M2/`: validated Ti EOS results.
