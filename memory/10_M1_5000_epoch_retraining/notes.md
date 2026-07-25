# Notes: M1 5000-Epoch Retraining

## Sources

### Source 1: User request
- Key points:
  - Change all subsequent committee training from 1000 to 5000 epochs.
  - Delete the existing 1000-epoch M1 outputs and retrain M1 at 5000 epochs.
  - Synchronize the policy in `research-plan.md` and related workflow files.

### Source 2: `memory/index.md`
- Key points:
  - W, Ta, and Ti each have a validated 200-row D1 `current.db`.
  - M1 committee training is the active stage.
  - Existing generated outputs are protected unless deletion is explicitly approved; this request provides M1 deletion approval.

### Source 3: `memory/09_D1_merge_M1_training/`
- Key points:
  - M1 jobs 13094 (W), 13095 (Ta), and 13096 (Ti) completed successfully.
  - Each M1 was trained from its own validated 200-row D1 `current.db`, with
    10 committee members, 5 workers, 8 cores per worker, and 1000 epochs.

### Source 4: Training implementation and documentation
- Paths: `src/dbselectandtrain.py`, `scripts/slurm/run_train_committee.slurm`,
  `research-plan.md`, `docs/unary_workflow.md`, `docs/source_function_index.md`,
  and `scripts/slurm/README.md`.
- Key points:
  - The active training function and SLURM template accepted an explicit epoch
    value but previously defaulted to 1000.
  - The production training template protects non-empty train directories.

## Commands and Observations

```bash
# Audit result before deletion:
# W/Ta/Ti each have train-committee/ containing 72 files:
# 10 JNN files, 10 fold logs, and 10 Trainer.groovy files with
# "train.nepochs = 1000".
# Sizes: W 7,591,253 B; Ta 7,608,725 B; Ti 7,461,876 B.
#
# squeue confirmed none are live. sacct records:
# 13094 M1-W COMPLETED 0:0; 13095 M1-Ta COMPLETED 0:0;
# 13096 M1-Ti COMPLETED 0:0.
#
# Verification passed after the policy change:
# module load jse && python3 -m py_compile src/*.py
# bash -n scripts/slurm/run_train_committee.slurm
# db_select_and_train(...).epochs default == 5000
# git diff --check
#
# The exact replacement submissions passed sbatch --test-only:
# W  test job 13098, Ta test job 13099, Ti test job 13100.
# Each command specifies 10 members, 5 workers, and 5000 epochs. The template
# requests one node, 5 tasks, 8 CPUs/task, and 48 hours.
```

## Synthesized Findings

### Scope
- Only the following approved obsolete outputs will be removed:
  - `W-potential/model_versions/M1_from_D1/train-committee/`
  - `Ta-potential/model_versions/M1_from_D1/train-committee/`
  - `Ti-potential/model_versions/M1_from_D1/train-committee/`
- The D1 `current.db` inputs and all M0 outputs are retained.

### Completed Deletion
- With no live M1 job in `squeue`, the three approved M1 `train-committee/`
  directories were removed. No root `slurm-M1-*` output files existed.
- The retained D1 `current.db` SHA-256 values are unchanged:
  - W: `bc09246d602a927a6905fb33c386a7030705ff70bab1fb7a39e63e0bb7e`
  - Ta: `8f72a927d657e7cfd6ffb743955acf1e3fa54e3261c783ffd611dd714edefec2`
  - Ti: `d59371001b625955b963f7d496ca7c5ea40de493e8ab8f7eb6d721ac7030ca68`

### Replacement M1 Submission

| Element | Job ID | Input | Output | Immediate state |
|---|---:|---|---|---|
| W | 13101 | `W-potential/current.db` | `W-potential/model_versions/M1_from_D1/train-committee/` | PENDING |
| Ta | 13102 | `Ta-potential/current.db` | `Ta-potential/model_versions/M1_from_D1/train-committee/` | PENDING |
| Ti | 13103 | `Ti-potential/current.db` | `Ti-potential/model_versions/M1_from_D1/train-committee/` | PENDING |

Every submitted command is:

```bash
sbatch --job-name=M1-5000-<X> scripts/slurm/run_train_committee.slurm \
  <X>-potential/current.db \
  <X>-potential/model_versions/M1_from_D1/train-committee \
  10 5 5000
```

The template requests 1 node, 5 tasks, 8 CPUs/task, and 48 hours. This is the
only immediate status check; completion validation is deferred until requested.

### 5000-Epoch Policy
- M0 remains historical at 1000 epochs.
- The replacement M1 and every future `Mk` committee use 5000 epochs.
- The active Python default, training SLURM-template default, training-template
  documentation, source index, and staged workflow documentation are updated
  to the same policy. The legacy `ase_md.py` default is also aligned, while it
  remains prohibited as a production scheduler.

### Verification Note
- Initial direct Python import lacked ASE in the shell. `module load jse`
  resolved it; compilation, template shell syntax, default-epoch inspection,
  and `git diff --check` then passed.
