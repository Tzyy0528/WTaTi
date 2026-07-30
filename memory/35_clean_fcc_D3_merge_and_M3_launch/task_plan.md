# Task Plan: Clean-FCC D3 Merge and M3 Launch

## Goal
Merge each validated D3 label database with its protected D2 base, validate
and atomically publish the three 400-row D3 `current.db` files, then submit
matching independent M3 committee-training jobs.

## Phases
- [x] Phase 1: Confirm explicit authorization and merge/training requirements.
- [x] Phase 2: No-overwrite merge preflight and independent D3 merges.
- [x] Phase 3: Validate merged databases and atomically publish `current.db`.
- [x] Phase 4: Verify training inputs/settings and submit M3 jobs.
- [x] Phase 5: Record immediate status and deliver.

## Key Questions
1. Are every base, D3 label, updated, and published DB path distinct where
   required, isolated, and protected from unintended overwrite?
2. Do merged D3 databases preserve their 300-row D2 prefix, append only the
   validated 100 D3 rows, and contain no EOS/cross-element data?
3. Do M3 submissions use only their matching published 400-row D3 DB,
   Protocol-A reference energy, ten models, five workers, and 5,000 epochs?

## Decisions Made
- The user explicitly authorized all-element D3 merges and M3 training.
- Use `src/vasp_batch_dft.py merge` for each merge; validate before atomic
  publication.
- Submit training only through `scripts/slurm/run_train_committee.slurm`;
  do not submit E3 in this task.

## Errors Encountered
- None.

## Status
**Complete** - three D3 databases were independently merged, validated, and
atomically published; M3 jobs W `13540`, Ta `13541`, and Ti `13542` were
submitted. No monitoring is active.
