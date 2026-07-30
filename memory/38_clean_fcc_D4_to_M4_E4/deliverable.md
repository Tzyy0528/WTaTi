# Deliverable: Clean-FCC D4 Labels Through M4 and E4

## Outcome
The isolated clean-FCC W, Ta, and Ti D4 -> M4 -> E4 workflow is complete and
accepted. Each element now has its own verified 500-row D4 `current.db`, a
validated ten-fold M4 committee, and a fixed-reference E4 evaluation.

## Key Results / Decisions
- D4 Protocol-A labels: every element accepted all 100 selected 32-atom
  configurations. The verified D4 suffixes were merged with only their own
  400-row D3 bases and atomically published as 500-row states.
- Published D4 hashes: W
  `1242b2f534f1bebc2730102b0e1c5d8b524c0adaee2a75259d687deecfa57480`;
  Ta `600bd1c0c7d205771fe7b9859731e9af05399498e4c9ae6757c9de3bb9616989`;
  Ti `8db00646830c0cbb81037130881815b344f9be4f893a47e3d4a2dde075d2322b`.
- M4 training jobs W `13569`, Ta `13570`, and Ti `13571` all completed
  successfully. Each committee passed fold, provenance, finite-diagnostic,
  and JNN-content validation.
- E4 selected W `train-5/5.jnn` (10/10 eligible), Ta `train-2/2.jnn`
  (9/10), and Ti `train-9/9.jnn` (10/10). Aggregate raw /
  phase-aligned EOS MAE is respectively W `53.287499 / 16.061060`, Ta
  `73.655557 / 9.142611`, and Ti `31.118935 / 2.870559` meV/atom.
- E4 output, D4 database, M4 JNN, and fixed EOS-reference hashes passed
  post-run isolation checks. EOS validation data was not merged into a
  training database.
- No D5, RSS generation, further MD, or cleanup was started.

## How to Use / Verify
- E4 records: `<X>-potential/fcc-restart/evaluations/E4_M4/`.
- The complete validation method, per-phase metrics, digests, and E3
  comparison are recorded in `notes.md`.

## Files Changed
- `<X>-potential/fcc-restart/current.db`: verified D4 500-row state
  (`X = W, Ta, Ti`).
- `<X>-potential/fcc-restart/model_versions/M4_from_D4/train-committee/`:
  accepted ten-fold M4 committee.
- `<X>-potential/fcc-restart/evaluations/E4_M4/`: accepted fixed-reference
  EOS evaluation.
- `memory/38_clean_fcc_D4_to_M4_E4/`: completed task record.
