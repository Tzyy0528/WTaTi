# Notes: M2 E2 Fixed EOS Validation

## Sources

### Source 1: E2 workflow policy
- Path: `research-plan.md` Sections 6 and 11.3
- Key points:
  - E2 evaluates M2 against the unchanged fixed Protocol-B EOS references.
  - EOS references and results are validation-only and must not enter any
    training database.

### Source 2: Implementation map
- Path: `docs/source_function_index.md`
- Key points:
  - `src/eos_check_jnn.py` evaluates an NNAP committee using the fixed
    reference and writes protected predictions, phase metrics, and plots.

## Commands and Observations

- E2 is user-authorized, but it is gated on successful M2 completion and
  validation. The focused accounting check and committee validation are next.
- The first custom M2 fold validator had a local `row.symbols` list/set type
  error before completing any validation. It did not modify data or indicate
  a training error. A rerun also corrected the expected per-atom symbol-list
  shape; no generated asset was modified.

### M2 prerequisite validation (passed)
- The focused `sacct` check found W `13162`, Ta `13163`, and Ti `13164`
  `COMPLETED` with exit `0:0`.
- Every M2 committee has ten nonempty JNNs, ten logs, ten 5,000-epoch trainer
  files, and ten disjoint 270/30 train/test folds. Each matching 300-row
  `current.db` is reconstructed by every fold, and all ten test folds cover
  each row exactly once. All final `MAE-E` and `MAE-F` diagnostics are finite.

### E2 preflight (passed)
- Every fixed Protocol-B metadata/reference pair has 57 matching finite rows:
  19 each of bcc, fcc, and hcp. The output roots are absent:
  - `results/W_eos_benchmark/evaluations/E2_M2/`
  - `results/Ta_eos_benchmark/evaluations/E2_M2/`
  - `results/Ti_eos_benchmark/evaluations/E2_M2/`
- Fixed reference SHA-256 (`eos_structures.csv`, `eos_reference.csv`):
  - W: `d0fa9889b18797990d33114f91850c3710ee9b7b0c40856733cbdec392fa4a3d`,
    `d4360e843da262499a202613704cc73b483e3f74d8a016282da8d7179b512f64`
  - Ta: `16d5f83cd5a994109b17a66846a5091a718cfb6ce61d7f13f19a6e543222dc4f`,
    `869d901829f0682cb169923b1f0745e8e7503cff5385efb2a84bc53c1a06f4ab`
  - Ti: `3c11ea72890c9d0a1f336b7b609190b980fafdc8878c55d7af74d4cff0ad5ffb`,
    `1a5f38ae444e9412c9bb0d5cfa5c15e0af89b1af3e1f675892276c6c3c93a541`
- With the standard maximum train/test ratio of `1.25`, automatic selection
  has eligible folds and will report:
  - W: 7/10 eligible; `train-9/9.jnn`; train/test `MAE-E` 10.830/10.190
    meV/atom.
  - Ta: 8/10 eligible; `train-3/3.jnn`; train/test `MAE-E` 8.324/7.952
    meV/atom.
  - Ti: 7/10 eligible; `train-0/0.jnn`; train/test `MAE-E` 6.294/5.353
    meV/atom.

### Approved E2 commands

```bash
module load jse

python3 src/eos_check_jnn.py \
  --element W \
  --metadata results/W_eos_benchmark/eos_reference/eos_structures.csv \
  --reference-csv results/W_eos_benchmark/eos_reference/eos_reference.csv \
  --jnn-root W-potential/model_versions/M2_from_D2/train-committee \
  --model-id E2_M2 \
  --output-dir results/W_eos_benchmark/evaluations \
  --max-train-test-ratio 1.25
```

Repeat with matching Ta and Ti paths only. `eos_check_jnn.py` protects
`results/<X>_eos_benchmark/evaluations/E2_M2/` from overwrite. It writes the
selection audit, predictions, metrics, selected-model path, and two plots.

### E2 execution and output validation (passed)
- The three documented local JSE evaluations completed without overwrite:
  - W selected `train-9/9.jnn`, SHA-256
    `feab4daa7c7471d8456d2943cc713cd1e0d62986bbe484e1e712a39570490c60`
  - Ta selected `train-3/3.jnn`, SHA-256
    `87bdabbc002f0319ed0f7b6204fe49da646e8dbd6cddd6d82325d68d7c7a155d`
  - Ti selected `train-0/0.jnn`, SHA-256
    `485e5b4a4fbdf6b27073d4d488be5d8db3266bd4153390b1df737028f1967502`
- JSE created its normal new inference JIT cache shared library beside each
  selected JNN. No existing JNN, training DB, EOS reference, or `current.db`
  was overwritten.
- Each `E2_M2/` root contains a ten-row `jnn_selection.csv`, selected JNN
  path, 57 finite raw and DFT-merged prediction rows with exact
  structure/scale coverage, four finite metric rows (bcc/fcc/hcp/all), and
  two nonempty plots. The three `current.db` SHA-256 values remain identical
  to the M2 preflight values.

### Aggregate EOS comparison

All entries are meV/atom for the fixed 57-point reference; lower is better.

| Element | Metric | E0 | E1 | E2 | E2 - E1 | E2 - E0 |
|---|---|---:|---:|---:|---:|---:|
| W | raw MAE | 25.621463 | 45.399273 | 34.028971 | -11.370303 | +8.407508 |
| W | raw RMSE | 32.523733 | 60.239879 | 45.953686 | -14.286193 | +13.429953 |
| W | phase-aligned MAE | 3.592390 | 17.475940 | 10.956002 | -6.519938 | +7.363612 |
| W | phase-aligned RMSE | 6.741441 | 23.885493 | 16.262826 | -7.622667 | +9.521385 |
| Ta | raw MAE | 49.321472 | 53.766972 | 76.550292 | +22.783320 | +27.228820 |
| Ta | raw RMSE | 60.472591 | 63.991902 | 93.435777 | +29.443875 | +32.963186 |
| Ta | phase-aligned MAE | 6.253640 | 3.216911 | 7.245910 | +4.028999 | +0.992270 |
| Ta | phase-aligned RMSE | 8.831629 | 4.415112 | 10.831494 | +6.416382 | +1.999553 |
| Ti | raw MAE | 24.473007 | 32.850840 | 43.570257 | +10.719416 | +19.097250 |
| Ti | raw RMSE | 32.584851 | 42.908598 | 52.721166 | +9.812315 | +20.136315 |
| Ti | phase-aligned MAE | 3.288328 | 9.180635 | 3.272348 | -5.908287 | -0.015980 |
| Ti | phase-aligned RMSE | 6.020773 | 13.482158 | 4.850533 | -8.631625 | -1.170240 |

E2 grid-minimum volume shifts from DFT (A3/atom), listed as E0/E1/E2:

| Element | bcc | fcc | hcp |
|---|---|---|---|
| W | +0.000 / +0.000 / +0.000 | +0.000 / -0.320 / +0.162 | +0.000 / -0.326 / +0.000 |
| Ta | +0.000 / +0.000 / +0.000 | +0.000 / +0.000 / -0.185 | +0.188 / +0.000 / -0.186 |
| Ti | +0.000 / +0.171 / -0.339 | +0.519 / +0.519 / +0.000 | +0.000 / +0.000 / +0.000 |

### Interpretation
- W improved from E1 on aggregate raw and phase-aligned errors but remains
  worse than the E0 baseline on both.
- Ta regressed on aggregate raw and phase-aligned error relative to both E1
  and E0.
- Ti regressed on aggregate raw error relative to both E1 and E0, while its
  phase-aligned shape error improved from E1 and is marginally lower than E0.
- Per `research-plan.md` Section 13, preserve these results and adjust any
  next element-local configuration after explicit review; do not overwrite
  prior workflow assets or start D3 automatically.
