# Deliverable: Clean-FCC D3 Protocol-A Label Validation

## Outcome
The W, Ta, and Ti D3 Protocol-A DFT batches all completed successfully and
their 100-row element-local label databases passed full read-only acceptance.

## Key Results / Decisions
- Jobs W `13531`, Ta `13532`, and Ti `13533` are `COMPLETED 0:0`.
- Every element has exact 100/100 selected input, manifest task, completed
  VASP task, and label DB row coverage.
- Protocol-A static INCAR/POTCAR identity, finite energy/force/stress,
  32-atom unary geometry, and source/result agreement passed.
- The independent 300-row D2 `current.db` files are unchanged.
- The next protected transition is D2 + D3 labels -> 400-row D3
  `current.db`, only after explicit merge authorization.

## How to Use / Verify
- Validated labels:
  `<X>-potential/fcc-restart/03-npt-round-1/<X>_D3_labeled.db`.
- See `notes.md` for Protocol-A, task, finite-result, geometry, and checksum
  results.
- Do not train M3 or evaluate E3 until a merge creates and validates the
  matching D3 training database.

## Files Changed
- `memory/34_clean_fcc_D3_label_validation/`: task record.
