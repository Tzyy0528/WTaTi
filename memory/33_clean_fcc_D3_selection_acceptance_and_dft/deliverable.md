# Deliverable: Clean-FCC D3 Selection Acceptance and DFT Submission

## Outcome
All completed D3 selection artifacts for W, Ta, and Ti passed read-only
acceptance. Three independent, no-overwrite Protocol-A VASP label batches
were submitted for the 100 validated selected structures of each element.

## Key Results / Decisions
- Retained all-frame score, geometry-audit, projected-CUR, p99-tail,
  source-distribution, selected-POSCAR, and D2-base-isolation checks passed
  for every element.
- Each selected set has 100 finite unary 32-atom, 3D-periodic structures
  matching its original NPT trajectory frames.
- The frozen Protocol-A static setup is preserved: `MAGMOM=_`,
  `KSPACING=0.2`, automatic `1.3*ENMAX` ENCUT, `NCORE=2`, and VASP static
  settings.
- Submitted DFT jobs: W `13531`, Ta `13532`, Ti `13533`; no overwrite
  variables were passed.

## How to Use / Verify
- DFT logs: `<X>-potential/fcc-restart/03-npt-round-1/slurm_logs/`.
- Label DB targets: `<X>-potential/fcc-restart/03-npt-round-1/<X>_D3_labeled.db`.
- On a later user-requested completion/status report, validate each label DB
  before the D3 merge, M3 training, or E3 EOS evaluation.

## Files Changed
- `memory/33_clean_fcc_D3_selection_acceptance_and_dft/`: task record.
