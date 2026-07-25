# Deliverable: D1 Protocol-A DFT Labeling

## Outcome
Independent Protocol-A VASP batches completed for the three validated D1
selections: W 13133, Ta 13134, and Ti 13135. Each produced a separate,
validated 100-row D1 label DB.

## Key Results / Decisions
- D1 inputs are validated and element-isolated.
- The frozen D0 Protocol-A static VASP settings will be reused unchanged.
- Output DBs and VASP work roots are protected and currently absent.
- Each job uses one node and 64 tasks for eight concurrent eight-rank VASP
  tasks; no output overwrite or forced input rewrite is enabled.
- Every VASP task completed and each label DB has finite unary 16-atom energy,
  forces, and stress. `current.db` is unchanged pending an explicit merge.

## How to Use / Verify
- Submit only through `scripts/slurm/run_vasp_batch_dft.slurm`.
- After completion, require 100 successful VASP tasks and 100 finite unary
  rows in each new DB before any merge.

## Files Changed
- `memory/09_D1_DFT_labeling/`: DFT labeling plan, provenance, and deliverable.
