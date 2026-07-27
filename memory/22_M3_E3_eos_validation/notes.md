# Notes: M3 E3 Fixed-Reference EOS Validation

## Sources

### Source 1: Repository workflow state
- Path: `memory/index.md`
- Key points:
  - D3 successors contain 400 rows per element.
  - M3 jobs W `13221`, Ta `13222`, and Ti `13223` were submitted from their matching D3 databases.
  - E3 has not yet started.

### Source 2: EOS workflow mapping
- Path: `research-plan.md`, `docs/source_function_index.md`
- Key points:
  - Use `src/eos_check_jnn.py` plus `src/eos_predict_jnn.groovy`.
  - Evaluate only the unchanged validation-only EOS reference.

## Commands and Observations

- `sacct` reports M3 jobs W `13221`, Ta `13222`, and Ti `13223` completed
  with exit `0:0`. The initial system-Python validation attempt stopped before
  reading data because NumPy is unavailable outside the JSE environment.
- After `module load jse`, a read-only validator confirmed for every element:
  its `current.db` matches the validated 400-row D3 SHA-256 successor, the
  committee contains ten nonempty JNN/log pairs configured for 5,000 epochs,
  each fold is an exact disjoint 360/40 reconstruction of only that database,
  and the ten test folds cover every database row exactly once. All final
  `MAE-E`/`MAE-F` diagnostics are finite.

| Element | Eligible models (ratio <= 1.25) | Automatic E3 model | Train/test MAE-E (meV/atom) |
|---|---:|---|---:|
| W | 10/10 | `train-8/8.jnn` | 12.030 / 9.934 |
| Ta | 8/10 | `train-2/2.jnn` | 8.802 / 7.471 |
| Ti | 9/10 | `train-3/3.jnn` | 6.603 / 6.447 |

- Each fixed Protocol-B EOS metadata/reference pair remains a matching,
  finite 57-row set (19 each bcc/fcc/hcp), with E0--E2 reference checksums
  unchanged. All protected `E3_M3` roots were absent.

### Approved E3 commands

```bash
module load jse
python3 src/eos_check_jnn.py \
  --element <W|Ta|Ti> \
  --metadata results/<X>_eos_benchmark/eos_reference/eos_structures.csv \
  --reference-csv results/<X>_eos_benchmark/eos_reference/eos_reference.csv \
  --jnn-root <X>-potential/model_versions/M3_from_D3/train-committee \
  --model-id E3_M3 \
  --output-dir results/<X>_eos_benchmark/evaluations \
  --max-train-test-ratio 1.25
```

### E3 execution and artifact validation (passed)

- The three evaluations completed successfully with no overwrite:
  - W selected `train-8/8.jnn` (test `MAE-E` 9.934 meV/atom).
  - Ta selected `train-2/2.jnn` (test `MAE-E` 7.471 meV/atom).
  - Ti selected `train-3/3.jnn` (test `MAE-E` 6.447 meV/atom).
- JSE generated one expected inference JIT cache shared library beside each
  selected M3 JNN. It did not modify any training DB, EOS reference, JNN, or
  `current.db`.
- Every `E3_M3/` root contains ten JNN-selection rows, a selected-JNN record,
  57 finite raw and DFT-merged rows with exact bcc/fcc/hcp scale coverage,
  four finite metric rows, and two nonempty plots. All three `current.db` and
  fixed-reference SHA-256 values remain identical to preflight.

### Aggregate fixed-reference comparison

All entries are MAE in meV/atom; lower is better.

| Element | E0 raw | E1 raw | E2 raw | E3 raw | E3 - E2 | E0 aligned | E1 aligned | E2 aligned | E3 aligned | E3 - E2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| W | 25.621463 | 45.399273 | 34.028971 | 72.978209 | +38.949238 | 3.592390 | 17.475940 | 10.956002 | 7.119618 | -3.836384 |
| Ta | 49.321472 | 53.766972 | 76.550292 | 59.583841 | -16.966452 | 6.253640 | 3.216911 | 7.245910 | 6.994062 | -0.251848 |
| Ti | 24.473007 | 32.850840 | 43.570257 | 40.041633 | -3.528623 | 3.288328 | 9.180635 | 3.272348 | 4.753056 | +1.480708 |

E3 grid-minimum volume shifts from DFT (A3/atom), bcc/fcc/hcp:

- W: `+0.000000 / +0.000000 / +0.000000`
- Ta: `+0.000000 / -0.184554 / -0.186308`
- Ti: `+0.171328 / +0.344609 / +0.000000`

### Interpretation

- W phase-aligned EOS shape improved from E2 but remains worse than E0, and
  raw EOS MAE regressed sharply from E2 and E0.
- Ta improved from E2 in both aggregate metrics but remains worse than E0 in
  raw and phase-aligned MAE.
- Ti improved raw EOS MAE from E2 but remains worse than E0; phase-aligned
  MAE regressed from E2 and is worse than E0.
- Preserve E3 and require a separate element-specific configuration review
  before any D4 sampling, selection, labeling, or retraining.

## Synthesized Findings

### Scope
- Run one independent fixed-reference EOS evaluation each for W, Ta, and Ti.
- Do not modify `current.db`, training data, or fixed EOS reference assets.
