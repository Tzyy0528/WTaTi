# Notes: D1 Protocol-A DFT Labeling

## Inputs and Outputs

| Element | CUR input POSCARs | New labeled DB | New VASP work directory |
|---|---:|---|---|
| W | 100 | `W-potential/01-nvt-round-1/W_D1_selected_labeled.db` | `W-potential/01-nvt-round-1/dft/vasp_W_D1_selected/` |
| Ta | 100 | `Ta-potential/01-nvt-round-1/Ta_D1_selected_labeled.db` | `Ta-potential/01-nvt-round-1/dft/vasp_Ta_D1_selected/` |
| Ti | 100 | `Ti-potential/01-nvt-round-1/Ti_D1_selected_labeled.db` | `Ti-potential/01-nvt-round-1/dft/vasp_Ti_D1_selected/` |

The selected input directories are protected output from D1 CUR:

```text
W-potential/01-nvt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u6p73061_cur100/
Ta-potential/01-nvt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u3p49643_cur100/
Ti-potential/01-nvt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u5p9331_cur100/
```

## Frozen Protocol A

The D1 batches reproduce the completed D0 static Protocol-A command:

```text
MAGMOM=_
KSPACING=0.2
ENCUT_FACTOR=1.3
NCORE=2
CORES_PER_JOB=8
MAX_WORKERS=8
VASP_COMMAND=vasp_std
```

The generated INCAR uses `PREC=Accurate`, `ALGO=Normal`, `EDIFF=1E-5`,
`NELM=200`, `SIGMA=0.1`, `KGAMMA=.TRUE.`, `LASPH=.TRUE.`, `LREAL=Auto`,
`ISYM=0`, `KPAR=1`, `NSIM=6`, `IBRION=-1`, `NSW=0`, and `ISIF=2`.
There is no explicit MAGMOM or SOC override.

Local PAW metadata, inspected without copying PAW content:

| Element | ENMAX (eV) | D1 ENCUT (eV) | SHA-256 |
|---|---:|---:|---|
| W | 223.057 | 289.9741 | `c0897285f1b301314dcc12eb838ce8a777aa860795754598b0626cb818170117` |
| Ta | 223.667 | 290.7671 | `b94d0231aa338d2b49887428178c5ebac7fa385cbd6154890af94e8013d269f3` |
| Ti | 178.330 | 231.8290 | `f8e8f1d080d9e9b45e792f1068744b07aba8441d1e7ce11486a5d4c0f5a1479e` |

The user previously approved retaining the historical atomic reference
energies in `src/dbselectandtrain.py`: W `-12.9581`, Ta `-11.8578`, and Ti
`-7.8951` eV. DFT labeling does not use them; their Protocol-A consistency
remains a training-stage caveat.

## Submitted Batches

| Element | Job ID | Final state | Elapsed | Successful tasks |
|---|---:|---|---:|---:|
| W | 13025 | COMPLETED, 0:0 | 01:11:44 | 100 |
| Ta | 13026 | COMPLETED, 0:0 | 01:06:38 | 100 |
| Ti | 13027 | COMPLETED, 0:0 | 01:08:15 | 100 |

The jobs use no overwrite flags. Their exact commands are recorded under
`<X>-potential/01-nvt-round-1/slurm_logs/vasp_batch_command-<jobid>.sh`.

## Completed Label Validation

| Element | DB SHA-256 | Rows | Energy/atom range (eV) | Max-force range (eV/A) |
|---|---|---:|---:|---:|
| W | `60ff0c0e975a929e522640030b9a7608bac4863bfc7cf5f431099110f1032da4` | 100 | -12.064164 to -9.621682 | 5.926629 to 24.868057 |
| Ta | `ac3e04341c1199c70f05931473a9993c5c9ac004e60e375cf8aa34d9416e789e` | 100 | -11.099562 to -8.800891 | 3.240738 to 14.583382 |
| Ti | `673d6dfc3bde46feae8811345f5abaa567af019bb66b10af1c6d22a3c52f471d` | 100 | -7.250921 to -6.220508 | 2.215101 to 29.193577 |

Each work tree contains 100 OUTCAR files; its run summary reports 100
successful tasks and no failures. Every label DB contains finite energy,
forces, and stress, positive finite 16-atom cells, and only its expected
element. The DB `source` fields map one-to-one to the 100 D1 CUR POSCARs.
Static VASP cells and positions agree with their inputs within `6e-8 A`.

The W, Ta, and Ti `current.db` files remain their original 100-row D0
snapshots with their recorded hashes. The D1 label DBs are validated but are
not merged.

## Validation Required After Completion

- Complete. The next workflow stage is a separately reviewed, element-local
  database merge.
