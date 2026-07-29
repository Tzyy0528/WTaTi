# Task Plan: Clean-FCC D3 Selection Acceptance and DFT Submission

## Goal
Read-only validate the completed W, Ta, and Ti D3 selection artifacts, then,
only if all required gates pass, submit three isolated Protocol-A VASP DFT
batches for the selected structures.

## Phases
- [x] Phase 1: Establish terminal job status and locate the approved workflow.
- [x] Phase 2: Validate retained score, audit, CUR, and selected-POSCAR artifacts.
- [x] Phase 3: Verify frozen Protocol-A inputs and no-overwrite/resource preflight.
- [x] Phase 4: Submit DFT jobs and record one immediate status check.
- [x] Phase 5: Review and deliver.

## Key Questions
1. Does each completed selection retain complete, finite, element-isolated
   score/audit/CUR output satisfying its frozen D3 card?
2. Do the final selected POSCAR sets contain exactly 100 valid unary
   structures with required source, duplicate, and extreme-tail provenance?
3. Are the DFT command, output DB, work directory, Protocol-A settings,
   POTCAR identity, resources, and overwrite guards correct for each element?

## Decisions Made
- Selection scheduler success alone is insufficient; DFT follows only after
  independent output acceptance.
- Use `src/vasp_batch_dft.py` via
  `scripts/slurm/run_vasp_batch_dft.slurm`, never the legacy `nncalc` path.
- Keep all three element workflows and their output databases isolated.

## Errors Encountered
- The first read-only validator compared the literal shell command text and
  did not normalize the escaped comma separators written by `printf %q`.
  Resolution: parse recorded commands with `shlex.split`; no asset changed.
- The first ASE geometry comparison treated `Atoms.symbols` as a scalar
  equality expression. Resolution: compare chemical-symbol lists instead;
  no asset changed.
- The second read-only validator expected the wrong label
  (`source_uncertainty_layer`) for the selector's documented combined
  source/tail distribution rows. Resolution: validate the actual
  `source_layer` schema; no asset changed.
- The third read-only validator compared a floating-point command argument
  textually and rejected Ti's equivalent recorded `1.775270170` value.
  Resolution: normalize numeric CLI arguments before comparison; no asset
  changed.

## Status
**Complete** - selection acceptance passed and W/Ta/Ti D3 Protocol-A DFT
batches were submitted. No monitoring is active; the next gate is
read-only label validation after a user-requested completion/status report.
