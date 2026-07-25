# Task Plan: D1 Protocol-A DFT Labeling

## Goal
Label the independently selected W, Ta, and Ti D1 CUR structures with the
frozen Protocol-A VASP workflow, without modifying any `current.db`.

## Phases
- [x] Confirm three independent 100-structure CUR input directories and
  absent label DB/work-directory outputs.
- [x] Freeze the D1 commands to the completed D0 Protocol-A settings.
- [x] Submit independent W, Ta, and Ti VASP batches.
- [x] Monitor and validate independent W, Ta, and Ti VASP batches.
- [x] Validate completed VASP tasks and labeled ASE DBs.
- [x] Hand off the validated labels for the separately recorded element-local
  D1 database merge.

## Fixed Protocol-A Batch Settings

```text
PAW:              POTCAR/PBE/<element>/POTCAR
VASP:             vasp_std from the jse/4.1.1b module (VASP 6.5.0)
MAGMOM:           omitted (_)
KSPACING:         0.2
ENCUT:            1.3 * max(POTCAR ENMAX)
static:           IBRION=-1, NSW=0, ISIF=2
EDIFF:            1E-5
NCORE:            2
resources:        1 node, 64 tasks, 8 concurrent 8-core VASP tasks, 24 h
```

No overwrite, force-prepare, source balancing, or cross-element input is
permitted.

## Submission

| Element | SLURM job | Input structures | Output DB |
|---|---:|---:|---|
| W | 13025 | 100 | `W_D1_selected_labeled.db` |
| Ta | 13026 | 100 | `Ta_D1_selected_labeled.db` |
| Ti | 13027 | 100 | `Ti_D1_selected_labeled.db` |

All three jobs completed on `lpsnode01` with exit code 0:0. Their label DBs
passed independent finite-data, unary, source-provenance, and row-count
validation. No `current.db` has been modified.
