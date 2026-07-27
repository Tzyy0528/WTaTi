# Deliverable: D4 NPT Validation, Scoring, and Projected-CUR Selection

## Outcome

D4 NPT validation, all-frame M3 scoring, and independent uncertainty-gated
projected-CUR selection completed for W, Ta, and Ti. Each element now has an
auditable, element-local 100-POSCAR D4 Protocol-A candidate set; no database
was changed by this task.

## Key Results / Decisions

- The retained production policy used matching M3 `U_min`, source
  decorrelation, physical/risk gates, current.db-projected CUR, and an
  element-local p99-U tail cap.
- CUR jobs W `13244`, Ta `13245`, and Ti `13246` completed `0:0`.
- Each selected set has 100 unique finite unary 16-atom 3D-periodic POSCARs,
  final ranks `000001..000100`, no gate rejections, and tail counts W/Ta/Ti
  of 4/1/1 (cap 10).
- All three 400-row D3 `current.db` files and EOS validation assets are
  unchanged.

## How to Use / Verify

- Inspect `<X>-potential/04-npt-round-2/absolute-u-projected-cur/`:
  `selection_parameters.txt`, `selection_summary.csv`,
  `physical_gate_rejections.csv`, `cur_selected_distribution.csv`, and
  `cur-selected-poscar_absolute_u*_cur100/`.

## Files Changed

- `memory/24_D4_validation_scoring_selection/`: D4 validation, scoring, and
  selection task record.
