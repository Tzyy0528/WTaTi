# Deliverable: D3 Scoring and Projected-CUR Selection

## Outcome
All D3 NPT frames were scored with their matching M2 committee, and the
approved projected-CUR policy selected exactly 100 validated structures for
each element. No DFT labeling or downstream stage was started.

## Key Results / Decisions
- W, Ta, and Ti inputs/outputs must remain isolated.
- EOS references and labels remain outside selection and training inputs.
- Score-only jobs W `13176`, Ta `13177`, and Ti `13178` completed `0:0`;
  each retained 35,007 auditable all-frame records.
- `U_min`: W `0.194310000`, Ta `0.166670000`, Ti `0.125950000` eV/A.
- CUR jobs W `13182`, Ta `13183`, and Ti `13184` completed `0:0`.
- Every output has 100 unique finite unary 16-atom POSCARs, ranks
  `000001`--`000100`, zero physical-gate rejections, source-wise 50/100-frame
  decorrelation, and tail counts W/Ta/Ti = 1/3/2, each below the cap of 10.

## How to Use / Verify
- Selected outputs:
  - `W-potential/03-npt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p19431_cur100/`
  - `Ta-potential/03-npt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p16667_cur100/`
  - `Ti-potential/03-npt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p12595_cur100/`
- Review `selection_parameters.txt`, `selection_summary.csv`,
  `physical_gate_rejections.csv`, and `cur_selected_distribution.csv` in each
  protected CUR root.

## Files Changed
- `memory/19_D3_scoring_selection/`: complete D3 scoring/selection task record.
