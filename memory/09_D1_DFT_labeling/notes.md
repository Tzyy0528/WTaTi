# Notes: D1 Protocol-A DFT Labeling

## Sources

### Source 1: Validated replacement D1 selection
- Path: `memory/08_D1_reselection/`
- Key points:
  - CUR jobs W 13128, Ta 13129, and Ti 13130 completed with exit code `0:0`.
  - Every element has 22,505 finite candidates and 100 unique selected unary
    16-atom POSCARs.

### Source 2: DFT protocol and runner
- Path: `research-plan.md` sections 5 and 11;
  `scripts/slurm/run_vasp_batch_dft.slurm`;
  `src/vasp_batch_dft.py`
- Key points:
  - Protocol-A labels must use the VASP batch runner, not `nncalc`.
  - New label DB, base DB, and later updated DB must be distinct.
  - The runner refuses an existing output DB unless an explicit overwrite is
    requested.

## Validated D1 Input Sets

| Element | Selected input directory | Selected structures |
|---|---|---:|
| W | `W-potential/01-nvt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p064288_cur100/` | 100 |
| Ta | `Ta-potential/01-nvt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p047964_cur100/` | 100 |
| Ti | `Ti-potential/01-nvt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p048319_cur100/` | 100 |

Each set passed finite-cell/position validation, positive-volume checks,
expected unary element and 16-atom count, unique selected source/frame keys,
and unique POSCAR byte hashes.

## Frozen Protocol-A Submission Configuration

Reuse D0's active-label static settings independently for each element:

```text
MAGMOM = _
KSPACING = 0.2
ENCUT = automatic 1.3 * max(POTCAR ENMAX)
NCORE = 2
SOC / explicit spin override = absent
VASP command = vasp_std
cores per VASP task = 8
concurrent VASP tasks = 8
SLURM allocation = 1 node, 64 tasks, partition-default wall time
```

Current local POTCAR SHA-256 values:

```text
W  c0897285f1b301314dcc12eb838ce8a777aa860795754598b0626cb818170117
Ta b94d0231aa338d2b49887428178c5ebac7fa385cbd6154890af94e8013d269f3
Ti f8e8f1d080d9e9b45e792f1068744b07aba8441d1e7ce11486a5d4c0f5a1479e
```

## Planned Protected Outputs

```text
W:  db=W-potential/01-nvt-round-1/W_D1_selected_labeled.db
    work=W-potential/01-nvt-round-1/dft/vasp_W_D1_selected/
Ta: db=Ta-potential/01-nvt-round-1/Ta_D1_selected_labeled.db
    work=Ta-potential/01-nvt-round-1/dft/vasp_Ta_D1_selected/
Ti: db=Ti-potential/01-nvt-round-1/Ti_D1_selected_labeled.db
    work=Ti-potential/01-nvt-round-1/dft/vasp_Ti_D1_selected/
```

All six paths were absent before submission preparation. No overwrite or
force-prepare option is permitted.

## DFT Submission

| Element | Job ID | Output label DB | VASP work root |
|---|---:|---|---|
| W | 13133 | `W-potential/01-nvt-round-1/W_D1_selected_labeled.db` | `W-potential/01-nvt-round-1/dft/vasp_W_D1_selected/` |
| Ta | 13134 | `Ta-potential/01-nvt-round-1/Ta_D1_selected_labeled.db` | `Ta-potential/01-nvt-round-1/dft/vasp_Ta_D1_selected/` |
| Ti | 13135 | `Ti-potential/01-nvt-round-1/Ti_D1_selected_labeled.db` | `Ti-potential/01-nvt-round-1/dft/vasp_Ti_D1_selected/` |

Each job calls `scripts/slurm/run_vasp_batch_dft.slurm` with its own selected
input directory, output DB, `MAGMOM=_`, and `KSPACING=0.2`. Explicit runner
environment settings are `WORK_DIR` as listed above, `CORES_PER_JOB=8`,
`MAX_WORKERS=8`, `NCORE=2`, and `VASP_COMMAND=vasp_std`. The template
requests one node and 64 tasks (eight concurrent eight-rank VASP tasks), with
partition-default wall time. No overwrite or force-preparation setting was
used. The one immediate `squeue` check found jobs 13133--13135 pending.

## Completed Label Validation

| Element | Job ID | State / exit | VASP tasks | Label DB rows | Label validation |
|---|---:|---|---:|---:|---|
| W | 13133 | `COMPLETED / 0:0` | 100 | 100 | finite unary 16-atom energy, forces, stress |
| Ta | 13134 | `COMPLETED / 0:0` | 100 | 100 | finite unary 16-atom energy, forces, stress |
| Ti | 13135 | `COMPLETED / 0:0` | 100 | 100 | finite unary 16-atom energy, forces, stress |

For every label DB, JSE/ASE validation checked 3D PBC, finite positions and
cell, positive volume, expected single-element composition and 16-atom count,
finite scalar energy, finite `(16, 3)` forces, and finite six-component
stress. Each of the 100 VASP task `OUTCAR` files has the normal completion
marker. The D1 label DBs are valid but remain separate from `current.db`.
