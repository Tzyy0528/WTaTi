# Notes

Submitted Ti M0 training on 2026-07-21:

```text
SLURM job: 12474
input: Ti-potential/current.db
output: Ti-potential/model_versions/M0_from_D0/train-committee/
committee_size=10
train_workers=5
epochs=1000
```

The job was running on `lpsnode01` immediately after submission. Historical
Ti reference energy already accepted by the user is used by
`src/dbselectandtrain.py`.

## Completion update, 2026-07-22

Job 12474 completed successfully. The committee contains 10 nonempty JNN
models. Its 10 disjoint test folds cover all 100 D0 rows (90/10 train/test in
each fold).

The element-local E0 validation selected
`train-3/3.jnn` from the final `MAE-E` diagnostics: 1.810 meV/atom train,
1.548 meV/atom test, and a 1.169251 train/test ratio. The model SHA-256 is
`31e2f6df45559473bc4362cd87c18e6750f443727558446c74a34f92edc70258`.
E0 results are recorded in `memory/2026-07-22-Ti-E0-evaluation/`; user
acceptance is pending and no MD work was started.
