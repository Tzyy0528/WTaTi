# Ta EOS Validation Preparation

## Fixed source roles

- Primary phase: bcc.
- Diagnostic transfer phases: fcc and hcp.
- Sources: `structures/Ta_benchmark/Ta-bcc.poscar`,
  `structures/Ta_benchmark/Ta-fcc.poscar`, and
  `structures/Ta_benchmark/Ta-hcp.poscar`.

## Required decisions before generation

1. Use the user-approved VASP batch backend static defaults as Ta Protocol B:
   `KSPACING=0.2`, automatic `ENCUT=1.3*ENMAX`, `MAGMOM=_`, and no explicit
   SOC or spin override.
2. Use the approved common 19-point lattice-scale grid from 0.97 to 1.03 for
   bcc, fcc, and hcp.
3. Review the exact SLURM-labeling and collection commands and
   their protected output paths.

## Output isolation

All generated Ta EOS structures, DFT DBs, and CSVs belong only under
`results/Ta_eos_benchmark/eos_reference/`; none may enter `Ta-potential/`.
