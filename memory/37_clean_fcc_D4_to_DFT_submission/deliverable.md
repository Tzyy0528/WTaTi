# Deliverable: Clean-FCC D4 Through DFT Submission

## Outcome
Completed the user-authorized clean-FCC D4 path through protected Protocol-A
DFT submission for isolated W, Ta, and Ti. Monitoring stopped at submission;
the jobs have not been queried afterward.

## Key Results / Decisions
- D4 NPT jobs W `13546`, Ta `13547`, and Ti `13548` completed `0:0`; all
  21 retained 32-atom NPT sources passed provenance and finite-output checks.
- Combined M3 selection jobs W `13549`, Ta `13550`, and Ti `13551` completed
  `0:0`. Every all-frame, U-cutoff, geometry-audit, projected-CUR, p99-tail,
  source, and final-POSCAR identity check passed.
- M3-recalibrated `U_min` values are W `0.20000000`, Ta `0.17464000`, and Ti
  `0.12831000` eV/A. Each DFT input has exactly 100 valid unary 32-atom
  3D-PBC positive-cell structures.
- Protocol-A DFT jobs W `13558`, Ta `13559`, and Ti `13560` were submitted
  with `MAGMOM=_`, `KSPACING=0.2`, auto `1.3*ENMAX` ENCUT, `NCORE=2`,
  eight concurrent eight-rank VASP tasks, and no overwrite/force/prepare
  flags.
- Do not merge labels, alter `current.db`, train M4, run E4, or query DFT
  status/results unless the user explicitly requests it.

## How to Use / Verify
- Retained D4 selection artifacts are below each
  `<X>-potential/fcc-restart/04-npt-round-2/` root.
- Intended DFT outputs are `<round>/<X>_D4_labeled.db` and
  `<round>/dft/vasp_<X>_D4/`; inspect only on a later user request.

## Files Changed
- `memory/37_clean_fcc_D4_to_DFT_submission/`: task plan, notes, and final
  stopping-point report.
