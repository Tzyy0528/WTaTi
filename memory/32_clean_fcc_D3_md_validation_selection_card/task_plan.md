# Task Plan: Clean-FCC D3 MD Validation and Selection Card

## Goal
Confirm terminal D3 NPT success and validate all 21 element-isolated source
outputs before freezing any combined score/audit/CUR selection cards.

## Phases
- [x] Phase 1: Record the user completion report and required validation gate.
- [x] Phase 2: Make one focused terminal-state check and validate all sources.
- [x] Phase 3: Derive/freeze all required D3 selection cards and pass
  no-overwrite preflight.
- [x] Phase 4: Submit the user-authorized W, Ta, and Ti combined selection
  jobs, make one immediate combined status check, and record their IDs.

## Key Questions
1. Did jobs W `13513`, Ta `13514`, and Ti `13515` finish successfully?
2. Does every `P-1GPa` through `P-50GPa` source have finite, complete,
   element-local 32-atom NPT trajectory and pressure-summary output?
3. What target and geometry/descriptor card remains to be explicitly
   approved before the combined selection runner can start?

## Decisions Made
- The user reports D3 NPT completion; this triggers the required one focused
  terminal-state check and read-only source validation.
- No scoring, CUR, DFT, merge, M3, or E3 submission is implied by this
  validation task.
- The combined selection pipeline can now consume the D3 trajectories after
  its remaining element-local target/gate/descriptor cards are explicitly
  frozen; it must not choose the DFT target autonomously.
- The user now explicitly approves `target=100` for each element and confirms
  use of the previously implemented one-allocation selection pipeline.
- The D3 cards use matching clean-D0 geometry gates and `r_c=6.0`,
  `n_max=5`, `l_max=6`, similarity `0.99999`; no frame gaps, source quotas,
  force, volume, or pressure hard gate is allowed.
- The user then said "开始吧", explicitly authorizing three independent
  one-node, one-task, 24-hour combined selection submissions.

## Errors Encountered
- The first read-only summary validator expected 13 numeric fields per data
  line, but the `#` exists only in the 13-field header; data lines correctly
  contain step plus 11 numeric values. It stopped on W step 0 without
  changing an asset. Resolution: validate the 13-token header and 12-token
  data rows, then rerun the full validation.
- A combined memory/documentation patch used stale `notes.md` context and
  failed before changing that file. Resolution: apply this focused update;
  no generated workflow asset was affected.
- The first compact no-overwrite guard compared the numeric pressure order
  with lexically sorted source directories and reported W as unexpected.
  Resolution: sort both expected and observed names; the corrected guard
  passed for all elements without changing an asset.

## Status
**Complete** - final no-overwrite guards passed and the combined selections
were submitted: W `13519`, Ta `13520`, Ti `13521`. The sole immediate
combined `squeue` check found all three running on `lpsnode02`; no monitoring
is active.
