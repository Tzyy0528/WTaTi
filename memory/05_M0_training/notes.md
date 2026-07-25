# Notes: M0 Committee Training: W, Ta, and Ti

This record groups the common workflow stage only. W, Ta, and Ti data, calculations, and outputs remain strictly independent.

## W

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

### Completion update, 2026-07-22

Job 12472 completed successfully. The committee contains 10 nonempty JNN
models. Its 10 disjoint test folds cover all 100 D0 rows (90/10 train/test in
each fold).

The element-local E0 validation selected
`train-4/4.jnn` from the final `MAE-E` diagnostics: 4.954 meV/atom train,
4.195 meV/atom test, and a 1.180930 train/test ratio. The model SHA-256 is
`ef27388f0bf7aa7c2779f31edfa231cf262ebb6bad0c6e9d763f89b7fe1afb3e`.
E0 results are recorded in `memory/2026-07-22-W-E0-evaluation/`; user
acceptance is pending and no MD work was started.

## Ta

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

### Completion update, 2026-07-22

Job 12473 completed successfully. The committee contains 10 nonempty JNN
models. Its 10 disjoint test folds cover all 100 D0 rows (90/10 train/test in
each fold).

The element-local E0 validation selected
`train-9/9.jnn` from the final `MAE-E` diagnostics: 2.314 meV/atom train,
1.854 meV/atom test, and a 1.248112 train/test ratio. The model SHA-256 is
`37f45b750ba16274f18b606ccaf6c89dddd0ee36a4f22c094baccdc051c0874e`.
E0 results are recorded in `memory/2026-07-22-Ta-E0-evaluation/`; user
acceptance is pending and no MD work was started.

## Ti

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

### Completion update, 2026-07-22

Job 12474 completed successfully. The committee contains 10 nonempty JNN
models. Its 10 disjoint test folds cover all 100 D0 rows (90/10 train/test in
each fold).

The element-local E0 validation selected
`train-3/3.jnn` from the final `MAE-E` diagnostics: 1.810 meV/atom train,
1.548 meV/atom test, and a 1.169251 train/test ratio. The model SHA-256 is
`31e2f6df45559473bc4362cd87c18e6750f443727558446c74a34f92edc70258`.
E0 results are recorded in `memory/2026-07-22-Ti-E0-evaluation/`; user
acceptance is pending and no MD work was started.
