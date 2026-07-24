# Notes

Submitted Ta M0 training on 2026-07-21:

```text
SLURM job: 12473
input: Ta-potential/current.db
output: Ta-potential/model_versions/M0_from_D0/train-committee/
committee_size=10
train_workers=5
epochs=1000
```

The job was running on `lpsnode01` immediately after submission. Historical
Ta reference energy already accepted by the user is used by
`src/dbselectandtrain.py`.

## Completion update, 2026-07-22

Job 12473 completed successfully. The committee contains 10 nonempty JNN
models. Its 10 disjoint test folds cover all 100 D0 rows (90/10 train/test in
each fold).

The element-local E0 validation selected
`train-9/9.jnn` from the final `MAE-E` diagnostics: 2.314 meV/atom train,
1.854 meV/atom test, and a 1.248112 train/test ratio. The model SHA-256 is
`37f45b750ba16274f18b606ccaf6c89dddd0ee36a4f22c094baccdc051c0874e`.
E0 results are recorded in `memory/2026-07-22-Ta-E0-evaluation/`; user
acceptance is pending and no MD work was started.
