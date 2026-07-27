# Deliverable: D2 Protocol-A VASP Labeling

## Outcome
Element-isolated D2 Protocol-A VASP label batches completed from the three
validated 100-POSCAR CUR selections. Each new label DB passed 100-row finite
unary 16-atom energy, force, and stress validation.

## Key Results / Decisions
- DFT inputs will be the three validated 100-POSCAR D2 CUR selections only.
- Jobs W `13154`, Ta `13155`, and Ti `13156` completed `0:0`.
- New label DBs: `W_D2_selected_labeled.db`,
  `Ta_D2_selected_labeled.db`, and `Ti_D2_selected_labeled.db`, each with
  100 rows.
- No database merge, M2 training, or EOS work is included.

## How to Use / Verify
- Before publishing any `current.db`, merge each element's 200-row D1 base
  with only its own 100-row D2 label DB and validate the 300-row successor.

## Files Changed
- `memory/14_D2_DFT_labeling/`: D2 DFT-labeling task record.
