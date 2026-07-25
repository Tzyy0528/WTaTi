# Deliverable: D1 Restart and Reselection Setup

## Outcome
The revoked D1 selection and every downstream D1/M1/E1/D2 artifact were
removed. Each element's `current.db` is restored to its exact D0 snapshot;
the valid D1 MD trajectories and all-frame scoring CSVs are retained.

## Key Results / Decisions
- D1 reselection must use an aggregate of the ten M0 final test `MAE-F`
  values, not a production-pool percentile.
- The approved aggregate is the arithmetic mean of the ten model-level final
  test `MAE-F` values, evaluated independently for W, Ta, and Ti.
- Derived thresholds: W `0.064288`, Ta `0.047964`, and Ti `0.048319` eV/A.
  All 22,505 retained production frames per element satisfy the respective
  threshold and will enter projected CUR.
- Protected one-task, 24-hour CUR jobs are submitted: W 13128, Ta 13129, and
  Ti 13130. Their output roots did not exist at submission and cannot be
  overwritten by the template.
- The three jobs completed successfully (exit code `0:0`). Every selection
  output contains 22,505 finite candidates and exactly 100 unique, finite
  unary 16-atom POSCARs, with zero physical-gate rejections.

## How to Use / Verify
- Compare each `<X>-potential/current.db` with
  `<X>-potential/00-input/<X>_D0_labeled.db`; both have 100 rows and
  byte-identical hashes.
- Once the aggregate is specified, read the M0 model logs and derive an
  element-local `U_min` before submitting projected-CUR selection.

## Files Changed
- `memory/07_D1_NVT_preparation/`: corrected the historical selection record.
- `memory/08_D1_reselection/`: new restart plan, notes, and deliverable.
