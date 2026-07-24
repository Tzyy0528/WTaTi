# Notes

Submitted W M0 training on 2026-07-21:

```text
SLURM job: 12472
input: W-potential/current.db
output: W-potential/model_versions/M0_from_D0/train-committee/
committee_size=10
train_workers=5
epochs=1000
```

The job was running on `lpsnode01` immediately after submission. Historical
W reference energy already accepted by the user is used by
`src/dbselectandtrain.py`.

## Completion update, 2026-07-22

Job 12472 completed successfully. The committee contains 10 nonempty JNN
models. Its 10 disjoint test folds cover all 100 D0 rows (90/10 train/test in
each fold).

The element-local E0 validation selected
`train-4/4.jnn` from the final `MAE-E` diagnostics: 4.954 meV/atom train,
4.195 meV/atom test, and a 1.180930 train/test ratio. The model SHA-256 is
`ef27388f0bf7aa7c2779f31edfa231cf262ebb6bad0c6e9d763f89b7fe1afb3e`.
E0 results are recorded in `memory/2026-07-22-W-E0-evaluation/`; user
acceptance is pending and no MD work was started.
