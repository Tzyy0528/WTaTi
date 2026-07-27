# Task Plan: D2 All-Frame Scoring and Structure Selection

## Goal
Score each validated D2 NVT pool with its full M1 committee, derive the
element-local `U_min` values, and produce protected projected-CUR selections
only after the D2 label budget is explicit.

## Phases
- [x] Phase 1: Confirm the validated D2 inputs, M1 committees, and absent
  scoring/selection outputs.
- [x] Phase 2: Submit and validate element-local all-frame uncertainty scoring.
- [x] Phase 3: Extract final M1 test `MAE-F` values and derive `U_min`.
- [x] Phase 4: Freeze the D2 CUR label budget and submit protected selection.
- [x] Phase 5: Validate selected structures and deliver.

## Key Questions
1. What D2 per-element DFT-label budget (`--target`) is approved for CUR?
2. Does every all-frame CSV retain isolated source and M1-committee provenance?

## Decisions Made
- Use the full ten-model M1 committee for each element's all-frame scoring.
- Use the user-approved final-test-MAE-F arithmetic mean for `U_min`.
- Retain the original NVT scale grid and use no source balancing, frame gaps,
  tail caps, or physical gates.
- The user clarified that the approved D1 default label budget carries forward:
  select 100 structures per element for D2.
- Do not submit DFT labels, merge databases, train M2, or run E2.

## Errors Encountered
- The CUR CLI requires explicit `--target`; resolved when the user confirmed
  the project-default continuation of 100 structures per element.

## Status
**Complete** - all three projected-CUR jobs completed successfully and their
100-structure element-local selections passed validation. DFT labeling is a
separate, unstarted stage.
