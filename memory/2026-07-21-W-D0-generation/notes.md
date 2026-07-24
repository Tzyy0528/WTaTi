# Notes

Generated with `nninit` from `structures/W_benchmark/W-seed.poscar`:

```text
seed_rep=2 2 2
seed_nstructs=20 per scale
seed_scales=0.90,0.95,1.00,1.05,1.10
seed_disturb=0.03
```

Output: `W-potential/00-input/seed-generation/nninit-poscars/`

Validation passed:

```text
count=100
composition=W only
atoms/structure=16
PBC=3D, finite cell and positions, positive volume
minimum pair distance range=2.068102 to 2.841296 A
volume/atom range=10.561582 to 23.436247 A^3
```

The command and generation log are retained in the sibling
`seed-generation/` directory. No DFT, ASE DB, or model was created.

The user approved labeling all 100 validated candidates with default static
Protocol A: `MAGMOM=_`, `KSPACING=0.2`, automatic `ENCUT=1.3*ENMAX`, and no
explicit SOC or spin override. No additional numerical minimum-distance
filter was applied beyond the completed finite/positive-distance validation.

Submitted job 12459 on 2026-07-21:

```text
input:  W-potential/00-input/seed-generation/nninit-poscars/
output: W-potential/00-input/W_D0_labeled.db
work:   W-potential/00-input/dft/vasp_W_D0/
```

The job was running on `lpsnode01` immediately after submission.

Job 12459 completed with exit code 0 in 01:31:18. The labeled DB contains 100
W-only, 16-atom rows with finite energy, forces, and stress. It was copied
without modification to `W-potential/current.db` as D0.

| Asset | SHA-256 |
|---|---|
| `W_D0_labeled.db` | `e2b429335744c6e53a4691c03c51948b5192787696b67c41e4e6fac937309be3` |
| `W-potential/current.db` (D0) | `e2b429335744c6e53a4691c03c51948b5192787696b67c41e4e6fac937309be3` |
