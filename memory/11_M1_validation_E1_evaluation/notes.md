# Notes: M1 Fixed-Reference E1 Evaluation

## Sources

### Source 1: M1 validation
- Path: `memory/10_D1_merge_M1_training/`
- Key points:
  - W, Ta, and Ti each have a validated 10-model M1 committee trained from
    its own 200-row D1 database.

### Source 2: EOS workflow
- Path: `research-plan.md` sections 6 and 11.3;
  `docs/source_function_index.md`
- Key points:
  - Reuse the fixed Protocol-B EOS references unchanged.
  - Select an eligible model from final train/test diagnostics for reporting,
    then compare E1 and E0 metrics.
  - EOS references and outputs are validation-only.

## Planned Element-Local Assets

```text
M1 committee:
  <X>-potential/model_versions/M1_from_D1/train-committee/
E0 reference/evaluation:
  results/<X>_eos_benchmark/evaluations/E0_M0/
E1 output:
  results/<X>_eos_benchmark/evaluations/E1_M1/
```

The E1 output roots must be absent and no EOS DB/CSV asset may be copied into
or merged with `<X>-potential/current.db`.

## E1 Execution and Output Validation

The documented local JSE evaluation was run separately for each element:

```text
python3 src/eos_check_jnn.py
  --element <X>
  --metadata results/<X>_eos_benchmark/eos_reference/eos_structures.csv
  --reference-csv results/<X>_eos_benchmark/eos_reference/eos_reference.csv
  --jnn-root <X>-potential/model_versions/M1_from_D1/train-committee
  --model-id E1_M1
  --output-dir results/<X>_eos_benchmark/evaluations
  --max-train-test-ratio 1.25
```

| Element | Eligible M1 folds | Reporting JNN | Train/test `MAE-E` (meV/atom) |
|---|---:|---|---|
| W | 6 / 10 | `train-2/2.jnn` | 9.779 / 9.322 |
| Ta | 4 / 10 | `train-1/1.jnn` | 7.809 / 6.569 |
| Ti | 9 / 10 | `train-2/2.jnn` | 5.652 / 4.678 |

Every E1 root contains a 10-row auditable `jnn_selection.csv`, selected-model
path, 57 finite DFT/NNAP prediction rows with one-to-one structure/scale
coverage, aggregate and phase metrics, and two nonempty EOS plots.

## E1 versus E0 Aggregate Metrics

All values are meV/atom; a negative delta is an improvement.

| Element | Metric | E0 | E1 | E1 - E0 |
|---|---|---:|---:|---:|
| W | raw MAE | 25.621463 | 45.399273 | +19.777810 |
| W | raw RMSE | 32.523733 | 60.239879 | +27.716146 |
| W | phase-aligned MAE | 3.592390 | 17.475940 | +13.883551 |
| W | phase-aligned RMSE | 6.741441 | 23.885493 | +17.144052 |
| Ta | raw MAE | 49.321472 | 53.766972 | +4.445500 |
| Ta | raw RMSE | 60.472591 | 63.991902 | +3.519311 |
| Ta | phase-aligned MAE | 6.253640 | 3.216911 | -3.036729 |
| Ta | phase-aligned RMSE | 8.831629 | 4.415112 | -4.416517 |
| Ti | raw MAE | 24.473007 | 32.850840 | +8.377834 |
| Ti | raw RMSE | 32.584851 | 42.908598 | +10.323747 |
| Ti | phase-aligned MAE | 3.288328 | 9.180635 | +5.892307 |
| Ti | phase-aligned RMSE | 6.020773 | 13.482158 | +7.461386 |
