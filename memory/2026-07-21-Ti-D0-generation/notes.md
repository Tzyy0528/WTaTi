# Notes

Generated with `nninit` from `structures/Ti_benchmark/Ti-seed.poscar`:

```text
seed_rep=2 2 2
seed_nstructs=20 per scale
seed_scales=0.90,0.95,1.00,1.05,1.10
seed_disturb=0.03
```

Output: `Ti-potential/00-input/seed-generation/nninit-poscars/`

Validation passed:

```text
count=100
composition=Ti only
atoms/structure=16
PBC=3D, finite cell and positions, positive volume
minimum pair distance range=2.194457 to 2.911919 A
volume/atom range=11.287859 to 26.307157 A^3
```

The command and generation log are retained in the sibling
`seed-generation/` directory. No DFT, ASE DB, or model was created.

The user approved labeling all 100 validated candidates with default static
Protocol A: `MAGMOM=_`, `KSPACING=0.2`, automatic `ENCUT=1.3*ENMAX`, and no
explicit SOC or spin override. No additional numerical minimum-distance
filter was applied beyond the completed finite/positive-distance validation.

Submitted job 12461 on 2026-07-21:

```text
input:  Ti-potential/00-input/seed-generation/nninit-poscars/
output: Ti-potential/00-input/Ti_D0_labeled.db
work:   Ti-potential/00-input/dft/vasp_Ti_D0/
```

The job was running on `lpsnode01` immediately after submission.

Job 12461 completed with exit code 0 in 01:33:23. The labeled DB contains 100
Ti-only, 16-atom rows with finite energy, forces, and stress. It was copied
without modification to `Ti-potential/current.db` as D0.

| Asset | SHA-256 |
|---|---|
| `Ti_D0_labeled.db` | `1fe2a5771706e8e6a673bd3a9e5908d465500f9679f5a5aea777f3f4099c739c` |
| `Ti-potential/current.db` (D0) | `1fe2a5771706e8e6a673bd3a9e5908d465500f9679f5a5aea777f3f4099c739c` |
