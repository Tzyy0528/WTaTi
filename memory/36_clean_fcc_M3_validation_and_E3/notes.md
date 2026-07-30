# Notes: Clean-FCC M3 Validation and E3 Evaluation

## Sources

### Source 1: M3 launch record
- Path: `memory/35_clean_fcc_D3_merge_and_M3_launch/`
- Key points:
  - Each published D3 database has 400 rows.
  - W/Ta/Ti M3 jobs are `13540`, `13541`, and `13542`.

### Source 2: Fixed EOS workflow
- Paths: `research-plan.md` sections 6 and 11.3; and
  `docs/source_function_index.md`.
- Key points:
  - Evaluate only an eligible model on the unchanged fixed Protocol-B
    reference.
  - EOS outputs are validation-only and must never enter `current.db`.

## Commands and Observations

```bash
sacct -j 13540,13541,13542 \
  --format=JobIDRaw,JobName%30,State,ExitCode,Elapsed -n -P
```

## Synthesized Findings

### Terminal M3 scheduler status

| Element | Job | State / exit | Elapsed |
|---|---:|---|---:|
| W | `13540` | `COMPLETED / 0:0` | `00:15:13` |
| Ta | `13541` | `COMPLETED / 0:0` | `00:13:35` |
| Ti | `13542` | `COMPLETED / 0:0` | `00:14:12` |

Committee and E3-output acceptance are pending.

### Validator retry

The first read-only validation command did not inspect or modify committee
artifacts: importing `src/eos_check_jnn.py` with an unregistered temporary
`importlib` module failed during `dataclass` setup. The retry registers the
module in `sys.modules` before execution, so it can use the evaluator's
actual MAE-E parsing and eligibility policy.

### M3 and E3 preflight acceptance

The successful retry used `module load jse` and a read-only Python validator.
For every element it verified the published D3 DB checksum, 400 finite unary
32-atom rows, ten exactly named and nonempty folds, one nonempty fold-local
JNN/log/trainer/train DB/test DB per fold, `train.nepochs = 5000`, matching
element/reference energy in every trainer, and finite final MAE-E/MAE-F
diagnostics. Direct SQLite comparison of physical/calculator/data fields
showed every train/test row to be an exact subset of only the matching D3
`current.db`; each fold was 360/40 and disjoint, each D3 ID appeared in test
once and training nine times.

| Element | Selected model under ratio <= 1.25 | Final energy MAE, train/test (meV/atom) | Eligible folds | Test-force MAE range (meV/A) | Selected-epoch range |
|---|---|---:|---:|---:|---:|
| W | `train-3/3.jnn` | 7.959 / 6.997 | 10 / 10 | 189.1-221.9 | 1121-3112 |
| Ta | `train-8/8.jnn` | 6.637 / 5.897 | 10 / 10 | 157.2-197.7 | 531-5000 |
| Ti | `train-8/8.jnn` | 4.794 / 4.424 | 10 / 10 | 118.7-140.4 | 286-1344 |

The selected train/test MAE ratios are W 1.137, Ta 1.125, and Ti 1.084.
All fold-level ratios were <= 1.240. The selected epoch is the NNAP
early-stop checkpoint and remains within the configured 5,000-epoch limit.

The same read-only preflight confirmed all three protected
`evaluations/E3_M3/` directories were absent. The unchanged fixed references
have 57 unique finite points per element, with bcc/fcc/hcp each contributing
19 points; metadata/reference keys, atom counts, and POSCAR paths match.

| Element | D3 `current.db` SHA-256 | EOS metadata / reference CSV SHA-256 |
|---|---|---|
| W | `566bd0cfd13d0e231b692589de91e6f94b3cf51753753e6fce3ca8a70d9659af` | `d0fa9889b18797990d33114f91850c3710ee9b7b0c40856733cbdec392fa4a3d` / `d4360e843da262499a202613704cc73b483e3f74d8a016282da8d7179b512f64` |
| Ta | `09ab573a20cf35b29c121f1584492a8da5e87d5a97cba4f647802764ca6a1c20` | `16d5f83cd5a994109b17a66846a5091a718cfb6ce61d7f13f19a6e543222dc4f` / `869d901829f0682cb169923b1f0745e8e7503cff5385efb2a84bc53c1a06f4ab` |
| Ti | `0a0647a1ec9160124c0a5c24c0838442b7e4f390411d52cffa1f25dfa3d985be` | `3c11ea72890c9d0a1f336b7b609190b980fafdc8878c55d7af74d4cff0ad5ffb` / `1a5f38ae444e9412c9bb0d5cfa5c15e0af89b1af3e1f675892276c6c3c93a541` |

`src/eos_check_jnn.py` creates `<output-dir>/<model-id>` and refuses a
pre-existing directory. It selects the lowest eligible final test-energy MAE
and writes the selected model, complete JNN selection table, raw/merged EOS
predictions, metrics, and two plots. The approved E3 commands use the
matching M3 committee, fixed element-local metadata/reference pair, model ID
`E3_M3`, output parent `<X>-potential/fcc-restart/evaluations`, and the
default explicit ratio cutoff `1.25`.

### E3 runner failure

The documented direct invocation

```bash
module load jse
jse src/eos_check_jnn.py ...
```

failed for W in `predict_eos()` with
`NameError: name '__file__' is not defined`. The JSE Python runner does not
provide `__file__`, but the evaluator path is currently constructed from it.
The script had already created the protected W directory
`W-potential/fcc-restart/evaluations/E3_M3/`; `set -e` stopped before Ta and
Ti. No D3 database or EOS reference was written. Because output paths are
protected, inspect this W partial directory read-only and obtain explicit
authorization before deleting/replacing it for the canonical `python3`
rerun, which supplies `__file__` and still invokes JSE only for NNAP
inference.

Read-only inspection found that the W partial directory contains only the
2,916-byte `jnn_selection.csv`, which correctly records all ten eligible W
folds and `train-3/3.jnn` as the lowest-test-MAE choice. No raw predictions,
merged predictions, metrics, plots, or `best_jnn.txt` exist. Ta/Ti canonical
E3 directories remain absent. A post-failure checksum check confirmed that
all three D3 DBs and all six EOS reference CSVs still exactly match the
preflight digests above.

The user explicitly authorized removal of that failed W partial directory and
a canonical Python-runner rerun for all three elements. This authorization is
limited to `W-potential/fcc-restart/evaluations/E3_M3/`; no database,
reference, committee, or other generated artifact may be removed or
overwritten.

### Canonical E3 completion and validation

After confirming that the authorized W directory contained only
`jnn_selection.csv`, it was deleted. A no-overwrite guard confirmed that all
three `evaluations/E3_M3/` roots were absent and that the three D3 DB
checksums still matched. The successful canonical invocation was:

```bash
module load jse
python3 src/eos_check_jnn.py \
  --element <W|Ta|Ti> \
  --metadata results/<X>_eos_benchmark/eos_reference/eos_structures.csv \
  --reference-csv results/<X>_eos_benchmark/eos_reference/eos_reference.csv \
  --jnn-root <X>-potential/fcc-restart/model_versions/M3_from_D3/train-committee \
  --model-id E3_M3 \
  --output-dir <X>-potential/fcc-restart/evaluations \
  --max-train-test-ratio 1.25
```

This Python entry point supplies `__file__`; it still launches JSE/Groovy
NNAP inference through `src/eos_predict_jnn.groovy`. All three commands
completed successfully and selected the preflight-predicted models. JSE
created a local compiled inference cache in each selected fold; the JNN
files themselves remained unchanged.

Read-only output validation accepted each E3 directory. Every element has
exactly seven nonempty expected artifacts (`best_jnn.txt`,
`jnn_selection.csv`, raw/merged 57-point predictions, metrics CSV, and two
plots); all selection, prediction, reference, raw-error, phase-aligned, and
grid-minimum numerical fields are finite. The three bcc/fcc/hcp phases have
19 matched points each (57 total); all paths resolve only to the matching
element's EOS reference and selected M3 JNN. The output selection tables have
all ten eligible folds and the stated lowest-test-MAE model. D3 DBs remain
400 rows with their published hashes; all EOS metadata/reference CSV hashes
remain exactly as preflighted. Full metric fields are retained in each
`eos_metrics.csv`.

Aggregate EOS error metrics (raw / phase-aligned, meV/atom):

| Element | MAE | RMSE | Max absolute error |
|---|---:|---:|---:|
| W | 76.061896 / 20.302527 | 97.090810 / 30.165315 | 181.298130 / 81.770243 |
| Ta | 72.373923 / 7.342374 | 89.378609 / 11.205456 | 153.457896 / 35.783123 |
| Ti | 31.944002 / 4.686592 | 46.864102 / 7.916812 | 82.416544 / 23.606558 |

Per-phase raw / phase-aligned MAE (meV/atom), followed by DFT/NNAP
grid-minimum scale and volume shift (A3/atom):

| Element | Phase | Raw / aligned MAE | DFT / NNAP scale | Volume shift |
|---|---|---:|---:|---:|
| W | bcc | 92.254 / 25.270 | 1.000000 / 1.006667 | +0.320774 |
| W | fcc | 3.013 / 2.452 | 1.006667 / 1.006667 | +0.000000 |
| W | hcp | 132.919 / 33.186 | 0.993333 / 0.990000 | -0.163382 |
| Ta | bcc | 120.955 / 13.348 | 1.000000 / 0.996667 | -0.180696 |
| Ta | fcc | 1.429 / 0.659 | 1.010000 / 1.010000 | +0.000000 |
| Ta | hcp | 94.738 / 8.020 | 0.996667 / 0.990000 | -0.371370 |
| Ti | bcc | 16.703 / 11.829 | 0.996667 / 1.003333 | +0.343801 |
| Ti | fcc | 0.561 / 0.276 | 0.993333 / 0.996667 | +0.171728 |
| Ti | hcp | 78.568 / 1.955 | 0.996667 / 0.996667 | +0.000000 |

The stable combined SHA-256 digests over the ten M3 JNN contents are:

| Element | Committee JNN digest |
|---|---|
| W | `4b70e76b9c07d3941384e8186093b0a161fd9b99ae0a94c9803370ee2a52b757` |
| Ta | `271099ae358772212cbde93530d79ff7279e4d33e27ad316fe630abeb53b8b88` |
| Ti | `f272715af70b61fa657a0a5fc13a404a7438e151aaebae22497d611ab6d91584` |

Relative to the archived E2 aggregate raw / phase-aligned MAE, E3 changes
(meV/atom) are W `+8.494759 / -3.528054`, Ta `+20.703421 / -2.312003`, and
Ti `+14.890368 / +1.193943`. This is a recorded validation comparison, not
authorization to start E4 or alter any training database.
