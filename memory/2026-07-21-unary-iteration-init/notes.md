# Notes

## 2026-07-21 Gate 0 preflight

- `python3 -m py_compile src/*.py` passed.
- The supported VASP batch, EOS, and absolute-U projected-CUR CLI entry
  points parsed `--help`.
- Under `module load jse`, ASE read all twelve supplied POSCAR files. Every
  file is periodic in 3D, has positive volume, and contains only its intended
  element.
- Local PAW metadata was inspected without copying the POTCAR files:

| Element | TITEL | ENMAX (eV) | SHA-256 |
|---|---|---:|---|
| W | `PAW_PBE W 08Apr2002` | 223.057 | `c0897285f1b301314dcc12eb838ce8a777aa860795754598b0626cb818170117` |
| Ta | `PAW_PBE Ta 17Jan2003` | 223.667 | `b94d0231aa338d2b49887428178c5ebac7fa385cbd6154890af94e8013d269f3` |
| Ti | `PAW_PBE Ti 08Apr2002` | 178.330 | `f8e8f1d080d9e9b45e792f1068744b07aba8441d1e7ce11486a5d4c0f5a1479e` |

## Gate 0 status

The input/PAW readability checks pass. Protocol A, Protocol B, isolated-atom
reference energies, EOS scale grids, D0 perturbation settings, NVT/NPT/RSS
numerical designs, and physical selection limits remain unapproved. No
expensive calculation was submitted.

## User-approved reference-energy decision

The user directed that no new isolated-atom calculations be run. Retain the
historical values currently present in `src/dbselectandtrain.py::ENERGY`:

| Element | Reference energy (eV) |
|---|---:|
| W | -12.9581 |
| Ta | -11.8578 |
| Ti | -7.8951 |

These values are accepted for the workflow without a new isolated-atom audit.
Their consistency with the final Protocol A remains unverified and must be
reported with the trained models.

## D0 seed-supercell decision

The user approved `seed_rep = 2 2 2` for W, Ta, and Ti D0 generation. The
supplied seed cells each contain two atoms, so the `nninit` input cell will
contain 16 atoms for every element.

The user approved the following seed generation settings, obtained from the
legacy `src/ase_md.py` parser:

| Parameter | Parser fallback |
|---|---|
| `seed_nstructs` | 20 structures per scale |
| `seed_scales` | `0.90,0.95,1.00,1.05,1.10` |
| `seed_disturb` | 0.03 |

Together with `seed_rep = 2 2 2`, these settings generate 100 structures per
element from a 16-atom repeated seed cell. The legacy automatic workflow and
its `nncalc` label path will not be used; D0 labels must use the VASP batch
workflow. A numerical minimum-distance gate remains to be set and checked
before DFT submission.
