# Ti EOS Validation Preparation

## Fixed source roles

- Primary phases: hcp and bcc.
- Diagnostic transfer phase: fcc.
- Sources: `structures/Ti_benchmark/Ti-bcc.poscar`,
  `structures/Ti_benchmark/Ti-fcc.poscar`, and
  `structures/Ti_benchmark/Ti-hcp.poscar`.

## Required decisions before generation

1. Use the user-approved VASP batch backend static defaults as Ti Protocol B:
   `KSPACING=0.2`, automatic `ENCUT=1.3*ENMAX`, `MAGMOM=_`, and no explicit
   SOC or spin override.
2. Use the approved common 19-point lattice-scale grid from 0.97 to 1.03 for
   bcc, fcc, and hcp.
3. Review the exact SLURM-labeling and collection commands and
   their protected output paths.

## Output isolation

All generated Ti EOS structures, DFT DBs, and CSVs belong only under
`results/Ti_eos_benchmark/eos_reference/`; none may enter `Ti-potential/`.
