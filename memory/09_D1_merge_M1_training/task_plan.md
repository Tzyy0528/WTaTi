# Task Plan: D1 Database Merge and M1 Committee Training

## Goal
Create and validate the independent D1 successors for W, Ta, and Ti from
their respective D0 and validated D1 Protocol-A label databases; publish each
successor as its element-local `current.db`; then train independent M1
ten-member committees through SLURM.

## Phases
- [x] Confirm base, label, successor, and M1 output paths are element-local;
  confirm no successor or M1 train directory existed.
- [x] Merge each D0 `current.db` with its own validated 100-row D1 label DB
  into a new `01-nvt-round-1/updated.db`, without overwrite.
- [x] Validate all three 200-row successors: exact base-first/labels-last
  ordering, unary finite 16-atom data, 3D PBC, no EOS provenance, and unique
  geometries/stored hashes.
- [x] Publish only the validated successors as the three element-local D1
  `current.db` files; preserve `updated.db` and `00-input/*_D0_labeled.db`.
- [x] Check the M1 SLURM template syntax, train-output paths, and exact
  40-core submission resources with `sbatch --test-only`.
- [x] Submit independent W, Ta, and Ti M1 committee trainings through SLURM;
  monitor them to successful completion.
- [ ] Validate completed M1 committees: SLURM exit state, ten nonempty JNN
  files, disjoint complete D1 folds, and finite training diagnostics.

## Frozen M1 Training Configuration

```text
committee size:  10
concurrent jobs: 5
cores/job:       8
allocation:      1 node, 5 tasks, 8 CPUs/task (40 cores)
epochs:          1000
wall time:       48:00:00
runner:          scripts/slurm/run_train_committee.slurm
```

The historical atomic reference energies retained with prior user approval
remain W `-12.9581`, Ta `-11.8578`, and Ti `-7.8951` eV in
`src/dbselectandtrain.py`. Their Protocol-A consistency caveat is unchanged.

No E1 EOS evaluation is included in this task.
