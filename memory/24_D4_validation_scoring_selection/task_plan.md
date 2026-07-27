# Task Plan: D4 NPT Validation, Scoring, and Projected-CUR Selection

## Goal
Validate every completed D4 NPT source, then apply the established independent
uncertainty-gated, physical/risk-gated, current.db-projected CUR policy to
select auditable D4 Protocol-A candidates without starting DFT labeling.

## Phases
- [x] Phase 1: Validate all 21 completed D4 NPT sources against frozen controls and finite-output requirements.
- [x] Phase 2: Preflight and submit independent all-frame M3 score-only jobs.
- [x] Phase 3: Validate all-frame score CSVs and calibrate element-local M3-log `U_min` values.
- [x] Phase 4: Freeze D4 physical/risk gates, source decorrelation, and tail cap from current evidence.
- [x] Phase 5: Preflight, submit, and validate independent absolute-U projected-CUR selections.
- [x] Phase 6: Deliver selected POSCAR provenance; do not start Protocol-A DFT labeling, merge, M4, or E4.

## Key Questions
1. Do all seven D4 NPT sources per element reproduce their frozen controls and contain finite, complete trajectory and pressure outputs?
2. Does every all-frame CSV score only the matching element's 35,007 D4 frames with all ten M3 models?
3. Which independently calibrated `U_min`, gates, and tail policy safely retain uncertain but diverse D4 candidates?

## Decisions Made
- The user retained the established production chain: all-frame uncertainty
  scoring -> element/model-specific `U_min` -> decorrelation -> physical/risk
  gates -> current.db-projected CUR -> tail cap.
- CUR-only and global Top-U selection are not authorized.
- D4 retains target 100, no source balancing, candidate/final source frame
  gaps of 50/100, descriptor controls `r_c=6.0`, `n_max=5`, `l_max=6`,
  similarity threshold `0.99999`, and a current-pool p99-U tail threshold
  with a 10-structure cap. The per-element threshold and all physical gates
  are newly calibrated from D4 M3/current.db evidence.

## Errors Encountered
- Initial `memory/index.md` update hunk had stale context after a partial
  multi-file patch; reread and updated the index with a targeted patch. No
  workflow artifact or submission was affected.

## Status
**Complete** - CUR jobs W `13244`, Ta `13245`, and Ti `13246` completed
`0:0`; all three protected selections passed audit with exactly 100 valid
POSCARs. The user separately authorized the next D4 Protocol-A DFT task;
no database merge, M4, or E4 action has started.
