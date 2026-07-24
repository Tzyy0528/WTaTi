# Deliverable

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
