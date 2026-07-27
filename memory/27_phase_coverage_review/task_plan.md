# Task Plan: Phase-Coverage Diagnosis

## Goal
Determine whether the single-phase initial seeds plausibly explain the W, Ta,
and Ti EOS transfer errors after the user-supplied KSPACING scan.

## Phases
- [x] Phase 1: Read the KSPACING scan and quantify the `0.2` difference from
  the finest tested spacing.
- [x] Phase 2: Quantify fixed-reference DFT energy differences among bcc,
  fcc, and hcp.
- [x] Phase 3: Compare the phase-energy evidence with the E3 raw and
  phase-aligned metrics.
- [x] Phase 4: Deliver a read-only diagnosis and future-round recommendation.
- [x] Phase 5: Resolve the follow-up question of why Ti HCP is not exact
  despite an HCP initial seed.

## Key Questions
1. Is `KSPACING = 0.2` a likely dominant source of the observed EOS error?
2. Can single-phase candidate pools reliably acquire competing crystal
   topologies?

## Decisions Made
- Retain the frozen `KSPACING = 0.2` protocol unless a broader
  structure/volume convergence test contradicts the supplied scan.
- Do not alter the running M4 jobs, existing databases, or validation-only
  EOS assets.
- Treat Ti HCP as a small absolute-energy-offset issue, not a poorly learned
  EOS shape: E3 has `5.692` meV/atom raw MAE but `0.843` meV/atom
  phase-aligned MAE and zero grid-minimum-volume shift.

## Errors Encountered
- Initial `memory/index.md` update hunk did not match the current wrapped
  M4-status paragraph after the three task files were created; reread the
  index and applied a targeted update. No workflow artifact was affected.

## Status
**Complete** - The evidence favors missing phase coverage and relative
phase-energy anchors over KSPACING as the main explanation for the observed
raw EOS errors. Ti also needs retained/added HCP equilibrium-neighborhood
coverage if sub-5-meV absolute HCP accuracy is required.
