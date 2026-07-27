# Deliverable: D4 Merge and M4 Committee Training

## Outcome

W, Ta, and Ti D4 label sets were independently merged, validated, and
atomically published to their matching 500-row `current.db` files. Protected
M4 committee training completed successfully for all three elements; E4 was
explicitly deferred.

## Key Results / Decisions

- D4 database SHA-256 values: W
  `d9d851b7e22ef2fdb84eeaa88d7822682e83a33f9de5eb91c188f92c2d0755bc`,
  Ta `bce6490107a31f329bd89a30d7505c5e3665357a2f254afdc3e181cdf10698a0`,
  and Ti `a68f2c8b4cd5e41788463566737fafa80e1e9b70a4c7a7006a953c57a922c6d2`.
- Each 500-row successor retains base rows `1..400` followed by only its
  matching D4 labels in rows `401..500`, with finite unary 16-atom DFT
  energy/force/stress results and no EOS metadata.
- M4 jobs: W `13275`, Ta `13276`, and Ti `13277`; each is ten models, five
  workers, eight CPUs/worker, and 5,000 epochs.
- A focused 2026-07-27 `sacct` check found all three jobs `COMPLETED` with
  exit code `0:0` (W 00:08:30, Ta 00:08:17, Ti 00:08:56).
- The user explicitly deferred E4. Committee-artifact validation was not
  performed in this status-only check.

## How to Use / Verify

- If the M4 models are later used, validate ten nonempty model/log pairs and
  the complete disjoint 450/50 fold coverage for each matching 500-row
  database. Do not run E4 unless separately authorized.

## Files Changed

- `W-potential/current.db`, `Ta-potential/current.db`, `Ti-potential/current.db`:
  atomically published validated D4 successors.
- `<X>-potential/04-npt-round-2/updated.db`: protected D4 merge artifact.
- `memory/26_D4_merge_M4_training/`: task record.
