# Deliverable: D2 M2 Committee Training

## Outcome
The independently protected M2 committees completed successfully from the
matching validated 300-row D2 databases and passed all required validation.

## Key Results / Decisions
- W, Ta, and Ti training inputs remain strictly isolated.
- E2 is not included.
- Jobs: W `13162`, Ta `13163`, and Ti `13164` all completed with exit `0:0`.
- Resources per job: one node, five tasks, eight CPUs per task, 48 hours;
  each trains ten models with five concurrent workers for 5,000 epochs.
- Every committee has ten nonempty JNNs and complete logs; all 270/30 folds
  are disjoint and their test-fold union covers the matching 300-row input
  exactly once. Final `MAE-E` and `MAE-F` diagnostics are finite.

## How to Use / Verify
- Use each element's `train-committee/` root as the validated M2 committee
  input for the separately authorized E2 fixed-reference EOS evaluation.

## Files Changed
- `memory/16_D2_M2_training/`: M2 training task record.
