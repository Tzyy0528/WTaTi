# Task Plan: Clean-FCC D4 Through DFT Submission

## Goal
Run isolated W, Ta, and Ti D4 NPT sampling and D3-policy selection, then
submit their selected Protocol-A DFT label batches while monitoring through
submission only.

## Phases
- [x] Phase 1: Recover D3 parameter cards, inspect current execution
  templates, and preflight D4 no-overwrite/isolation inputs.
- [x] Phase 2: Submit and monitor D4 NPT MD for all elements.
- [x] Phase 3: Validate D4 trajectories; submit and monitor D4 selection.
- [x] Phase 4: Validate selection; submit three D4 Protocol-A DFT batches
  and stop monitoring.
- [x] Phase 5: Record submitted commands, job IDs, outputs, and stop state.

## Key Questions
1. Do all D4 commands retain the D3 card while substituting only the matching
   M3 committee and 400-row D3 database?
2. Are `U_min` values independently re-derived from each M3 committee while
   all other approved D3 selection-policy parameters remain fixed?
3. Can all three Protocol-A label jobs be submitted to protected isolated
   output paths without any database merge, M4 training, E4, or DFT polling?

## Decisions Made
- The user explicitly authorized all-element D4 using the D3 NPT and
  selection policy, followed by Protocol-A DFT submission.
- Recompute `U_min` from M3 final test-force MAEs; do not copy M2/D3 values.
- Monitor MD and selection actively through DFT submission, then stop
  monitoring immediately without waiting for DFT completion.
- Do not merge labels, modify `current.db`, train M4, or start E4.

## Errors Encountered
- An initial shell glob/`awk` count reported zero M3 JNNs despite the ten
  visible fold directories. A direct fold-by-fold nonempty-file check
  immediately corrected this to ten JNNs and ten logs per element; no
  workflow artifact was created or changed.
- The first read-only selection validator compared audit values to
  ten-significant-digit all-frame CSV values with a `1e-9` absolute
  tolerance. W frame `P-1GPa:500` differed by `2.6e-9` in volume/atom due
  only to the scorer CSV formatting. Relax the cross-CSV tolerance to
  `1e-7` and rerun; no generated artifact was modified.
- A compact DFT-preflight display used an `fd` extension/depth expression
  that printed zero selected POSCARs despite the already accepted 100-file
  selection directories. Use direct Python `*.poscar` globbing for the
  actual no-overwrite preflight; no artifact was modified.

## Status
**Complete at the user-authorized stopping point** - D4 Protocol-A DFT jobs
W `13558`, Ta `13559`, and Ti `13560` were submitted. Monitoring stopped
immediately after the final submission; do not query or act on DFT results
without a new user request.
