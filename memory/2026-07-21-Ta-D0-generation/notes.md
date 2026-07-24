# Notes

Generated with `nninit` from `structures/Ta_benchmark/Ta-seed.poscar`:

```text
seed_rep=2 2 2
seed_nstructs=20 per scale
seed_scales=0.90,0.95,1.00,1.05,1.10
seed_disturb=0.03
```

Output: `Ta-potential/00-input/seed-generation/nninit-poscars/`

Validation passed:

```text
count=100
composition=Ta only
atoms/structure=16
PBC=3D, finite cell and positions, positive volume
minimum pair distance range=2.179011 to 2.996142 A
volume/atom range=11.966058 to 25.705051 A^3
```

The command and generation log are retained in the sibling
`seed-generation/` directory. No DFT, ASE DB, or model was created.

The user approved labeling all 100 validated candidates with default static
Protocol A: `MAGMOM=_`, `KSPACING=0.2`, automatic `ENCUT=1.3*ENMAX`, and no
explicit SOC or spin override. No additional numerical minimum-distance
filter was applied beyond the completed finite/positive-distance validation.

Submitted job 12460 on 2026-07-21:

```text
input:  Ta-potential/00-input/seed-generation/nninit-poscars/
output: Ta-potential/00-input/Ta_D0_labeled.db
work:   Ta-potential/00-input/dft/vasp_Ta_D0/
```

The job was running on `lpsnode01` immediately after submission.

Job 12460 completed with exit code 0 in 01:33:23. The labeled DB contains 100
Ta-only, 16-atom rows with finite energy, forces, and stress. It was copied
without modification to `Ta-potential/current.db` as D0.

| Asset | SHA-256 |
|---|---|
| `Ta_D0_labeled.db` | `fdd9005db9f754d6cd4f31c8c04429aa57e7d46d3fef8cb4eb48348031aa0072` |
| `Ta-potential/current.db` (D0) | `fdd9005db9f754d6cd4f31c8c04429aa57e7d46d3fef8cb4eb48348031aa0072` |
