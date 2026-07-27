# Task Plan: D2 Protocol-A VASP Labeling

## Goal
Produce three protected, element-local D2 Protocol-A label databases from the
validated 100-POSCAR projected-CUR selections.

## Phases
- [x] Phase 1: Confirm frozen Protocol-A inputs, POTCAR identities, selected
  POSCARs, output paths, resources, and no-overwrite state.
- [x] Phase 2: Submit independent W, Ta, and Ti VASP label batches.
- [x] Phase 3: Validate all completed label databases and deliver.

## Key Questions
1. Are all inputs and work/DB outputs strictly isolated by element?
2. Does every label database contain exactly 100 finite unary 16-atom labels?

## Decisions Made
- Use `src/vasp_batch_dft.py` through
  `scripts/slurm/run_vasp_batch_dft.slurm`; never use `nncalc`.
- Reuse the frozen D1 Protocol-A static settings without changes.
- Do not merge/publish `current.db`, train M2, or run E2 in this task.

## Errors Encountered
- None.

## Status
**Complete** - all three Protocol-A batches and their 100-row label databases
passed validation. The later D2 merge is a separate, unstarted stage.
