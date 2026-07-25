# Deliverable: D1 Merge and M1 Training

## Outcome
All three D1 successors were merged and validated, then published as the
element-local 200-row `current.db`. M1 committee jobs are submitted: W 13138,
Ta 13139, and Ti 13140.

## Key Results / Decisions
- Each successor will contain 200 rows: its 100 D0 rows followed by its own
  100 validated D1 labels.
- M1 training will use ten models, five concurrent workers, and 5000 epochs.
- Each `updated.db` and published `current.db` has 200 rows with D0 first and
  the corresponding D1 labels appended.
- Training roots were protected and absent; no overwrite option was used.
- All three M1 jobs completed successfully. Each committee has ten nonempty
  models, finite diagnostics, and complete disjoint fold coverage of D1.

## How to Use / Verify
- Validate all ten JNN models, fold coverage, and finite diagnostics after
  training finishes; this validation now passes.

## Files Changed
- `memory/10_D1_merge_M1_training/`: new merge/training task records.
