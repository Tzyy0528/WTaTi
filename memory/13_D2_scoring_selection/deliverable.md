# Deliverable: D2 All-Frame Scoring and Structure Selection

## Outcome
Independent W, Ta, and Ti D2 score-only jobs completed from their respective
ten-model M1 committees. Their all-frame CSVs passed provenance, frame-count,
equilibration, finite-data, and score-only-state validation. The resulting
projected-CUR selections have been submitted.

## Key Results / Decisions
- D2 `U_min`: W `0.17022`, Ta `0.14444`, Ti `0.113619` eV/A.
- Scoring jobs: W `13146`, Ta `13147`, and Ti `13148`, all completed `0:0`.
- Candidates after `U_min` and equilibration: W `22,385`, Ta `22,342`, Ti
  `21,914`.
- Projected-CUR jobs (target 100 per element): W `13150`, Ta `13151`, and Ti
  `13152`, all completed `0:0`.
- Every element has 100 unique, finite unary 16-atom selected POSCARs and
  zero physical-gate rejections.
- No DFT, database merge, M2, or E2 work is in scope.

## How to Use / Verify
- The next unstarted stage is independent Protocol-A VASP labeling of the
  three selected POSCAR sets.

## Files Changed
- `memory/13_D2_scoring_selection/`: scoring/selection task record.
