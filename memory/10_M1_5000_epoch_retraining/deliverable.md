# Deliverable: M1 5000-Epoch Retraining

## Outcome
The completed 1000-epoch M1 committee artifacts for W, Ta, and Ti were
removed, and replacement 5000-epoch M1 trainings were submitted independently.
The jobs are pending; no M1 completion or E1 evaluation has been claimed.

## Key Results / Decisions
- M0 remains an immutable historical 1000-epoch baseline.
- Replacement M1 and all subsequent `Mk` committee trainings use 5000 epochs.
- Jobs submitted: W `13101`, Ta `13102`, Ti `13103`.
- Each job trains 10 members from its own 200-row D1 `current.db`, with 5
  concurrent workers and 8 threads per worker.
- D1 database checksums are unchanged from the validated published state.

## How to Use / Verify
- The submission template and the active function default to 5000 epochs:

  ```bash
  module load jse
  python3 -m py_compile src/*.py
  bash -n scripts/slurm/run_train_committee.slurm
  ```

- After the jobs complete, validate ten nonempty JNN files, complete disjoint
  D1 folds, finite training diagnostics, and Slurm exit state before E1.

## Files Changed
- `src/dbselectandtrain.py`: training-function default changed to 5000 epochs.
- `src/ase_md.py`: legacy scheduler default aligned to 5000 epochs.
- `scripts/slurm/run_train_committee.slurm`: default/usage text changed to
  5000 epochs.
- `scripts/slurm/README.md`: committee-training default documentation changed.
- `research-plan.md`: M1-and-later 5000-epoch policy and explicit command.
- `docs/source_function_index.md`: training entry records the default/template.
- `docs/unary_workflow.md`: staged training policy records 5000 epochs.
