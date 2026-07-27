# Notes: D2 M2 Committee Training

## Sources

### Source 1: Published D2 database state
- Path: `memory/15_D2_merge/`
- Key points:
  - W, Ta, and Ti `current.db` files are validated, independent 300-row D2
    successors.
  - Each contains 200 preserved D1 rows followed by 100 matching D2 labels.

### Source 2: Training policy and implementation map
- Path: `research-plan.md` Section 11.2; `docs/source_function_index.md`
- Key points:
  - Train only from `Dk`, with 10 models, 5 concurrent workers, 8 threads per
    worker, and 5,000 epochs.
  - Audit element `ENERGY` values against frozen Protocol A before training.

### Source 3: Training submission interface
- Path: `scripts/slurm/run_train_committee.slurm`;
  `src/dbselectandtrain.py::db_select_and_train()`
- Key points:
  - The SLURM runner uses one node, five tasks, eight CPUs per task, and a
    48-hour wall time.
  - It rejects an existing nonempty training directory unless `OVERWRITE=1`;
    this task must not use overwrite.
  - The Python entry point receives the input DB, output directory, committee
    size, concurrent-worker count, and epoch count.

## Commands and Observations

### M2 preflight (passed)
- Each of `W-potential/current.db`, `Ta-potential/current.db`, and
  `Ti-potential/current.db` has exactly 300 finite unary rows, with 16 atoms
  per row and no EOS provenance.
- The protected committee roots were absent:
  - `W-potential/model_versions/M2_from_D2/train-committee/`
  - `Ta-potential/model_versions/M2_from_D2/train-committee/`
  - `Ti-potential/model_versions/M2_from_D2/train-committee/`
- `src/dbselectandtrain.py::ENERGY` matches the frozen Protocol-A policy:
  - W: `-12.9581` eV
  - Ta: `-11.8578` eV
  - Ti: `-7.8951` eV
- Input DB SHA-256:
  - W: `b2a6ed5a86848a6fc83e3c13ceb4bc08ab2e60f0e7d753e2cb8555068c2c6476`
  - Ta: `b4e7e34325bfc9506147c58bf4b9ebeb69a7491c2cb7510961cd457695c1a866`
  - Ti: `36eb18737c291e1dd26b11ca995f3255c0ae8da881e821ce66b08a0047e177cb`

### Approved submission commands

```bash
sbatch --nodes=1 --ntasks=5 --cpus-per-task=8 --time=48:00:00 \
  scripts/slurm/run_train_committee.slurm \
  W-potential/current.db \
  W-potential/model_versions/M2_from_D2/train-committee \
  10 5 5000

sbatch --nodes=1 --ntasks=5 --cpus-per-task=8 --time=48:00:00 \
  scripts/slurm/run_train_committee.slurm \
  Ta-potential/current.db \
  Ta-potential/model_versions/M2_from_D2/train-committee \
  10 5 5000

sbatch --nodes=1 --ntasks=5 --cpus-per-task=8 --time=48:00:00 \
  scripts/slurm/run_train_committee.slurm \
  Ti-potential/current.db \
  Ti-potential/model_versions/M2_from_D2/train-committee \
  10 5 5000
```

### M2 submission (2026-07-25)
- Protected roots were checked absent immediately before submission. No
  `OVERWRITE` setting was used.
- Submitted jobs:
  - W: `13162`
  - Ta: `13163`
  - Ti: `13164`
- One immediate focused `squeue` check reported all three as `RUNNING` on
  `lpsnode03`, with the requested two-day wall-time limit:

```text
13162 RUNNING unary_train 0:03 2-00:00:00 1 lpsnode03
13163 RUNNING unary_train 0:03 2-00:00:00 1 lpsnode03
13164 RUNNING unary_train 0:03 2-00:00:00 1 lpsnode03
```

Do not poll. After the user requests status or reports completion, use one
focused `sacct` query, then validate models, folds, epoch settings, and final
diagnostics.

### M2 completion and validation
- Focused accounting result:
  - W `13162`: `COMPLETED`, exit `0:0`, elapsed `00:05:14`
  - Ta `13163`: `COMPLETED`, exit `0:0`, elapsed `00:05:10`
  - Ti `13164`: `COMPLETED`, exit `0:0`, elapsed `00:05:12`
- Every element passed the following validator checks:
  - exactly ten nonempty JNN files in `train-0/0.jnn` through
    `train-9/9.jnn`, ten nonempty logs, and ten complete training folders;
  - all `Trainer.groovy` files set `train.nepochs = 5000` and the matching
    unary symbol only;
  - each fold has 270 distinct train rows and 30 distinct test rows; train and
    test are disjoint, their union is the matching 300-row `current.db`, and
    the ten test folds cover every input row exactly once;
  - final train/test `MAE-E` and `MAE-F` values are finite in every log.
- Test diagnostic ranges (meV/atom for E, meV/A for F):
  - W: `MAE-E` 8.704--14.350; `MAE-F` 164.300--215.900
  - Ta: `MAE-E` 5.182--11.400; `MAE-F` 131.100--192.200
  - Ti: `MAE-E` 5.353--9.690; `MAE-F` 112.900--134.700
