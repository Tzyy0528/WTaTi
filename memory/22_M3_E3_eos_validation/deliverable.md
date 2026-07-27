# Deliverable: M3 E3 Fixed-Reference EOS Validation

## Outcome

Completed fixed-reference E3 EOS validation for the independent W, Ta, and Ti
M3 committees. All protected outputs are valid; no training database or EOS
reference was modified.

## Key Results / Decisions

- Selected EOS models: W `train-8/8.jnn`, Ta `train-2/2.jnn`, and Ti
  `train-3/3.jnn`.
- Aggregate E3 raw / phase-aligned MAE (meV/atom): W `72.978209 / 7.119618`,
  Ta `59.583841 / 6.994062`, Ti `40.041633 / 4.753056`.
- W regressed markedly in raw EOS error. Ta and Ti recover some E2 raw error
  but remain above their E0 raw baselines. Do not start D4 automatically.

## How to Use / Verify

- Read `results/<X>_eos_benchmark/evaluations/E3_M3/eos_metrics.csv` and
  `eos_predictions.csv`; plots are in the same directory.
- See `notes.md` for full E0--E3 comparison and artifact-validation details.

## Files Changed

- `results/W_eos_benchmark/evaluations/E3_M3/`: W predictions, metrics,
  selection audit, and plots.
- `results/Ta_eos_benchmark/evaluations/E3_M3/`: Ta predictions, metrics,
  selection audit, and plots.
- `results/Ti_eos_benchmark/evaluations/E3_M3/`: Ti predictions, metrics,
  selection audit, and plots.
- `memory/22_M3_E3_eos_validation/`: task record and final report.
