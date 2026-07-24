# Notes

The Python `jsex` package is not importable in the installed JSE Python
environment. Inference therefore used `src/eos_predict_jnn.groovy`, which
loads `jsex.nnap.NNAP` and `jse.vasp.POSCAR` in the supported Groovy runtime.

The final Ti `MAE-E` parser selected
`Ti-potential/model_versions/M0_from_D0/train-committee/train-3/3.jnn`:

```text
train energy MAE = 1.810 meV/atom
test energy MAE  = 1.548 meV/atom
train/test ratio = 1.16925064599 <= 1.25
```

The executed command was:

```bash
module load jse
python3 src/eos_check_jnn.py \
  --element Ti \
  --metadata results/Ti_eos_benchmark/eos_reference/eos_structures.csv \
  --reference-csv results/Ti_eos_benchmark/eos_reference/eos_reference.csv \
  --jnn-root Ti-potential/model_versions/M0_from_D0/train-committee \
  --model-id E0_M0_groovy_retry_20260722 \
  --output-dir results/Ti_eos_benchmark/evaluations \
  --max-train-test-ratio 1.25
```

Following explicit approval on 2026-07-22, the completed artifacts were moved
to `results/Ti_eos_benchmark/evaluations/E0_M0/`, replacing the obsolete
partial selection CSV from the failed attempt; the retry directory was removed.

All 57 predictions (19 each of bcc, fcc, hcp) were finite and matched the DFT
reference structure/scale keys. Phase-aligned errors zero each phase at its own
grid minimum. No DFT was launched and `Ti-potential/current.db` was not
modified.
