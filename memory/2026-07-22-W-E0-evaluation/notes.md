# Notes

The Python `jsex` package is not importable in the installed JSE Python
environment. Inference therefore used `src/eos_predict_jnn.groovy`, which
loads `jsex.nnap.NNAP` and `jse.vasp.POSCAR` in the supported Groovy runtime.

The final W `MAE-E` parser selected
`W-potential/model_versions/M0_from_D0/train-committee/train-4/4.jnn`:

```text
train energy MAE = 4.954 meV/atom
test energy MAE  = 4.195 meV/atom
train/test ratio = 1.18092967819 <= 1.25
```

The executed command was:

```bash
module load jse
python3 src/eos_check_jnn.py \
  --element W \
  --metadata results/W_eos_benchmark/eos_reference/eos_structures.csv \
  --reference-csv results/W_eos_benchmark/eos_reference/eos_reference.csv \
  --jnn-root W-potential/model_versions/M0_from_D0/train-committee \
  --model-id E0_M0_groovy_retry_20260722 \
  --output-dir results/W_eos_benchmark/evaluations \
  --max-train-test-ratio 1.25
```

Following explicit approval on 2026-07-22, the completed artifacts were moved
to `results/W_eos_benchmark/evaluations/E0_M0/` and the retry directory was
removed.

All 57 predictions (19 each of bcc, fcc, hcp) were finite and matched the DFT
reference structure/scale keys. Phase-aligned errors zero each phase at its own
grid minimum. No DFT was launched and `W-potential/current.db` was not
modified.
