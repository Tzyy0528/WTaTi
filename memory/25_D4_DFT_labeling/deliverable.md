# Deliverable: D4 Protocol-A VASP Labeling

## Outcome

D4 Protocol-A VASP labeling is complete and validated for W, Ta, and Ti.
Each element has exactly 100 isolated finite labels from only its own
approved D4 selection; no training database was changed.

## Key Results / Decisions

- W `13248`, Ta `13249`, and Ti `13250` completed with exit `0:0`.
- Every label DB has 100 source-mapped unary 16-atom static labels and 100
  normal-completion-marked VASP `OUTCAR`s.
- The three `current.db` files remain their 400-row D3 databases; no D4
  `updated.db`, M4 committee, or E4 result exists.
- A POSCAR/OUTCAR round trip changes coordinates by no more than `4.815e-08
  A`, consistent with output precision and well within the `1e-7 A`
  validation tolerance.

## How to Use / Verify

- Inspect `<X>-potential/04-npt-round-2/<X>_D4_selected_labeled.db` and
  `<X>-potential/04-npt-round-2/dft/vasp_<X>_D4_selected/`.
- A separately authorized next stage may merge only the matching 400-row
  `current.db` and 100-row D4 label DB into a protected 500-row `updated.db`.

## Files Changed

- `memory/25_D4_DFT_labeling/`: task record.
