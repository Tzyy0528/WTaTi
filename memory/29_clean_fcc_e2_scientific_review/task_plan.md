# Task Plan: Clean-FCC E0/E1/E2 Scientific Review

## Goal
Assess element-isolated E0, E1, and E2 fixed-reference EOS results for W,
Ta, and Ti and recommend whether D3 sampling is scientifically justified.

## Phases
- [x] Phase 1: Initialize review record and preserve scope.
- [x] Phase 2: Gather and validate E0/E1/E2 metrics and phase trends.
- [x] Phase 3: Compare against decision criteria and determine per-element
  D3 recommendation.
- [x] Phase 4: Deliver an auditable review without starting new workflow work.

## Key Questions
1. Does M2 improve fixed-reference EOS raw and phase-aligned errors relative
   to E0 and E1 for each element?
2. Which phase-specific errors and equilibrium-volume shifts remain material?
3. Does the evidence justify element-specific D3 sampling, a targeted
   diagnostic, or a stop/hold decision?

## Decisions Made
- The review is validation-only: no EOS record may enter a training DB.
- W, Ta, and Ti metrics and recommendations remain independent.
- No D3 sampling, selection, DFT, merge, or training will begin as part of
  this review without a later explicit user authorization.
- E1-to-E2 is the primary incremental comparison because M1 and M2 both use
  the 5,000-epoch training policy; E0 remains the required baseline but M0
  used the historical 1,000-epoch policy.
- W and Ta merit only conditional, element-specific D3 design work; Ti is
  held from generic D3 pending a targeted read-only diagnosis.

## Errors Encountered
- None.

## Status
**Complete** - the review and recommendation are recorded in
`deliverable.md`; no workflow work was started.
