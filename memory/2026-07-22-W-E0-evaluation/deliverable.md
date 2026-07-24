# Deliverable

Results: `results/W_eos_benchmark/evaluations/E0_M0/`

- `jnn_selection.csv`: auditable 10-fold selection; 9 folds eligible.
- `best_jnn.txt`: `train-4/4.jnn`.
- `eos_nnap_predictions_raw.csv` and `eos_predictions.csv`: 57 finite,
  validation-only EOS predictions.
- `eos_metrics.csv` and two EOS plots.

Aggregate raw MAE/RMSE/max are 25.6215/32.5237/61.2253 meV/atom. Aggregate
phase-aligned MAE/RMSE/max are 3.59239/6.74144/24.6147 meV/atom. The bcc,
fcc, and hcp DFT/NNAP grid-minimum volumes agree on this fixed grid.

SHA-256: selected JNN
`ef27388f0bf7aa7c2779f31edfa231cf262ebb6bad0c6e9d763f89b7fe1afb3e`;
predictions
`fb9ce8a1a29543b96e232af44b15eeeee8062ae03e95f90ac63ebcb027f48bd7`;
metrics
`b257bb31922a2eb9a1e0a04a3dc9013d4eea3c2851e0ef408b46e04ef381364b`.

E0 has been evaluated but is awaiting user acceptance. No MD or active
learning was started.
