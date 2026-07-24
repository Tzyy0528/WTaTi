# Deliverable

Results: `results/Ta_eos_benchmark/evaluations/E0_M0/`

- `jnn_selection.csv`: auditable 10-fold selection; 5 folds eligible.
- `best_jnn.txt`: `train-9/9.jnn`.
- `eos_nnap_predictions_raw.csv` and `eos_predictions.csv`: 57 finite,
  validation-only EOS predictions.
- `eos_metrics.csv` and two EOS plots.

Aggregate raw MAE/RMSE/max are 49.3215/60.4726/94.3533 meV/atom. Aggregate
phase-aligned MAE/RMSE/max are 6.25364/8.83163/23.0423 meV/atom. Grid-minimum
volume shifts are 0.00000 (bcc), 0.00000 (fcc), and +0.187559
Angstrom^3/atom (hcp).

SHA-256: selected JNN
`37f45b750ba16274f18b606ccaf6c89dddd0ee36a4f22c094baccdc051c0874e`;
predictions
`640a58a6a110644689afc1622e6e5eab8d00c31689cfdd86bf201ce751717cea`;
metrics
`04091ed9e4cb0514c51167198563e49463edaa9d3f4342091ec405511f9dd576`.

E0 has been evaluated but is awaiting user acceptance. No MD or active
learning was started.
