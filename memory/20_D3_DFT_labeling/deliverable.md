# Deliverable: D3 Protocol-A VASP Labeling

## Outcome
Independent Protocol-A D3 labeling completed and passed validation for W, Ta,
and Ti. The 100-row label DBs are ready for later separate merges; no
database was changed.

## Key Results / Decisions
- The completed D3 selections are the only labeling inputs.
- No merge, M3 training, or E3 evaluation is in scope.
- W initial job `13185` had two MPI/VASP segment faults after 98 successful
  tasks; no-force retry `13220` completed the two missing tasks safely.
- All final label DBs have 100 finite unary 16-atom energy/force/stress
  labels: W `W_D3_selected_labeled.db`, Ta `Ta_D3_selected_labeled.db`, and
  Ti `Ti_D3_selected_labeled.db`.

## How to Use / Verify
- Before a separately authorized merge, use each 300-row `current.db`, its
  matching 100-row label DB, and absent
  `<X>-potential/03-npt-round-1/updated.db`; validate the resulting 400-row
  database before publishing it.

## Files Changed
- `memory/20_D3_DFT_labeling/`: D3 DFT-labeling task record.
