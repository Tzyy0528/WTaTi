# Task Plan: M1 5000-Epoch Retraining

## Goal
Replace the existing 1000-epoch W, Ta, and Ti M1 committee training outputs with fresh 5000-epoch M1 committees and document 5000 epochs as the standard for subsequent training.

## Phases
- [x] Phase 1: Plan and setup
- [x] Phase 2: Audit existing M1 outputs, training interface, and documentation
- [x] Phase 3: Remove only approved M1 training outputs; update configuration and documentation
- [x] Phase 4: Submit three independent 5000-epoch M1 trainings; verify submission and deliver

## Key Questions
1. Which exact M1 output directories and jobs correspond to the prior 1000-epoch training?
2. Which template, implementation, and workflow documents define the epoch count for current and future committee training?
3. What explicit SLURM commands and resources are required to retrain W, Ta, and Ti without overwriting unrelated data?

## Decisions Made
- Scope: W, Ta, and Ti remain separate; only M1 committee training products may be removed.
- Epoch policy: change the training target from 1000 to 5000 epochs for M1 and future committees, as requested.
- Historical preservation: retain the completed M0 and the prior M1 task record as historical 1000-epoch provenance; delete only the three generated M1 train directories.
- Default propagation: set 5000 as the default in the active training function and SLURM template, and in the legacy scheduler for consistency even though it is not a production entry point.

## Errors Encountered
- `ModuleNotFoundError: No module named 'ase'` during an initial direct
  implementation-import check: resolved by loading the required `jse` module
  before the lightweight Python verification.
- An initial broad stale-policy scan matched historical M0 task records:
  resolved by distinguishing immutable historical provenance from active code,
  templates, and workflow policy.
- A multi-file memory update initially missed a notes-file context line:
  resolved by reading the current note and applying the submission record in a
  focused follow-up patch.

## Status
**Complete** - The 1000-epoch M1 artifacts were removed, the 5000-epoch
policy was synchronized, and independent W/Ta/Ti replacement trainings were
submitted as jobs 13101/13102/13103. Their immediate state is PENDING; no
active monitoring is in progress.
