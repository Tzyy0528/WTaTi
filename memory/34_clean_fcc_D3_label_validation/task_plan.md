# Task Plan: Clean-FCC D3 Protocol-A Label Validation

## Goal
Read-only validate the completed W, Ta, and Ti D3 VASP label batches before
any D3 database merge, committee training, or EOS evaluation.

## Phases
- [x] Phase 1: Confirm terminal DFT scheduler status and identify the label-validation gate.
- [x] Phase 2: Validate manifests, VASP task completion, and frozen Protocol-A identity.
- [x] Phase 3: Validate label DB finiteness, composition, stress, and exact selected-source geometry.
- [x] Phase 4: Review and deliver the merge readiness decision.

## Key Questions
1. Do all 100 VASP tasks per element have complete output and one matching
   manifest/label-DB record?
2. Does every task retain the frozen element-local Protocol-A INCAR/POTCAR
   identity?
3. Are every energy, force, stress, cell, and source-geometry mapping finite
   and exact enough for a protected D3 merge?

## Decisions Made
- Scheduler completion alone does not authorize database mutation.
- Validate W, Ta, and Ti independently; EOS assets remain validation-only.
- Do not submit a merge, M3, or E3 job in this task.

## Errors Encountered
- None.

## Status
**Complete** - all three D3 label batches passed read-only validation. The
next protected action is an explicitly authorized D3 merge and atomic
publication of each element's 400-row `current.db`; M3/E3 remain unrun.
