# Deliverable: Clean-FCC M3 Validation and E3 Evaluation

## Outcome
M3 committee validation and the protected fixed-reference E3 EOS evaluations
are complete for W, Ta, and Ti. EOS results are validation-only; no
`current.db` or EOS reference was changed.

## Key Results / Decisions
- All three M3 committees contain ten finite, 5,000-epoch configured models
  with exact 360/40 D3 folds, test coverage once, training coverage nine
  times, and all ratio-1.25 eligible models.
- E3 selected W `train-3/3.jnn`, Ta `train-8/8.jnn`, and Ti
  `train-8/8.jnn`; all ten candidate folds were eligible.
- Aggregate raw / phase-aligned MAE (meV/atom): W `76.061896 / 20.302527`,
  Ta `72.373923 / 7.342374`, and Ti `31.944002 / 4.686592`.
- Versus E2, raw / phase-aligned MAE changes (meV/atom) are W
  `+8.494759 / -3.528054`, Ta `+20.703421 / -2.312003`, and Ti
  `+14.890368 / +1.193943`; this does not authorize E4.
- Each output contains finite, reference-matched bcc/fcc/hcp 19-point
  predictions, complete metrics, selection provenance, and nonempty plots.
- The initial JSE-Python-runner error was recovered under explicit user
  authorization by deleting only its partial W directory and rerunning with
  the Python entry point while retaining JSE for Groovy NNAP inference.

## How to Use / Verify
- Metrics: `<X>-potential/fcc-restart/evaluations/E3_M3/eos_metrics.csv`
- Predictions: `<X>-potential/fcc-restart/evaluations/E3_M3/eos_predictions.csv`
- Plots: `<X>-potential/fcc-restart/evaluations/E3_M3/*.png`
- Detailed audit and input/output hashes: `notes.md`.

## Files Changed
- `memory/36_clean_fcc_M3_validation_and_E3/`: task record.
- `<X>-potential/fcc-restart/evaluations/E3_M3/`: protected completed E3
  validation outputs for W, Ta, and Ti.
