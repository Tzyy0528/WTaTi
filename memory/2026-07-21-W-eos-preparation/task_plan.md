# W EOS Validation Preparation

## Fixed source roles

- Primary phase: bcc.
- Diagnostic transfer phases: fcc and hcp.
- Sources: `structures/W_benchmark/W-bcc.poscar`,
  `structures/W_benchmark/W-fcc.poscar`, and
  `structures/W_benchmark/W-hcp.poscar`.

## Required decisions before generation

1. Use the user-approved VASP batch backend static defaults as W Protocol B:
   `KSPACING=0.2`, automatic `ENCUT=1.3*ENMAX`, `MAGMOM=_`, and no explicit
   SOC or spin override.
2. Use the approved common 19-point lattice-scale grid from 0.97 to 1.03 for
   bcc, fcc, and hcp.
3. Review the exact SLURM-labeling and collection commands and
   their protected output paths.

## Output isolation

All generated W EOS structures, DFT DBs, and CSVs belong only under
`results/W_eos_benchmark/eos_reference/`; none may enter `W-potential/`.
