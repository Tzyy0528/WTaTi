# Task Plan: D1 Protocol-A DFT Labeling

## Goal
Label the validated replacement D1 selections for W, Ta, and Ti with the
frozen element-local Protocol-A VASP workflow and publish only new,
element-isolated label databases.

## Phases
- [x] Phase 1: Confirm replacement D1 CUR selections completed and validate
  the 100 selected POSCARs per element.
- [x] Phase 2: Confirm DFT protocol, input/output/work paths, resources, and
  no-overwrite state.
- [x] Phase 3: Submit independent W, Ta, and Ti VASP label batches.
- [x] Phase 4: Validate completed label databases and deliver.

## Key Questions
1. Do the selected inputs, Protocol-A settings, and output paths remain
   isolated for all three elements?
2. Does each completed label DB contain exactly 100 finite unary rows?

## Decisions Made
- Use `src/vasp_batch_dft.py` via
  `scripts/slurm/run_vasp_batch_dft.slurm`; never use legacy `nncalc`.
- Reuse the frozen D0 Protocol-A static settings: `MAGMOM=_`,
  `KSPACING=0.2`, automatic `ENCUT=1.3*max(ENMAX)`, `NCORE=2`, no explicit
  SOC or spin override, 8 cores per VASP task, and 8 concurrent tasks.
- Do not merge/publish `current.db`, train M1, or run E1/D2 in this task.

## Errors Encountered
- No top-level D0 VASP batch metadata JSON was retained in the old work
  roots. Resolved by using the preserved D0 runner command logs, which record
  the frozen Protocol-A settings, and recording the current element-local
  POTCAR SHA-256 values before D1 submission.

## Status
**Complete** - independent Protocol-A batches W 13133, Ta 13134, and Ti
13135 completed with exit code `0:0`. Every batch has 100 successful VASP
tasks and a matching 100-row DB with finite unary energy, forces, and stress.
The subsequent user-approved merge is tracked in
`memory/10_D1_merge_M1_training/`.
