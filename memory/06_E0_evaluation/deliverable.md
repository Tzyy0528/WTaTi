# Deliverable: E0 Fixed EOS Evaluation: W, Ta, and Ti

This record groups the common workflow stage only. W, Ta, and Ti data, calculations, and outputs remain strictly independent.

## W

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

## Ta

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

## Ti

Results: `results/Ti_eos_benchmark/evaluations/E0_M0/`

- `jnn_selection.csv`: auditable 10-fold selection; 7 folds eligible.
- `best_jnn.txt`: `train-3/3.jnn`.
- `eos_nnap_predictions_raw.csv` and `eos_predictions.csv`: 57 finite,
  validation-only EOS predictions.
- `eos_metrics.csv` and two EOS plots.

Aggregate raw MAE/RMSE/max are 24.4730/32.5849/69.6353 meV/atom. Aggregate
phase-aligned MAE/RMSE/max are 3.28833/6.02077/21.4110 meV/atom. Grid-minimum
volume shifts are 0.00000 (bcc), +0.518647 (fcc), and 0.00000
Angstrom^3/atom (hcp).

SHA-256: selected JNN
`31e2f6df45559473bc4362cd87c18e6750f443727558446c74a34f92edc70258`;
predictions
`f38092e666dd4f6aa3aef0c5a80075c78a0de80b2b9cec35a566ae45cbe5fe6d`;
metrics
`dfbb6698b1de0d2df9312518aaf27ba9fae4c1cbd5ff25f424aa84a7afdcf01f`.

E0 has been evaluated but is awaiting user acceptance. No MD or active
learning was started.
