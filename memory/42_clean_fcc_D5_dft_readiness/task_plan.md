# Task Plan: Clean-FCC D5 DFT Readiness

## Goal
Determine whether W, Ta, and Ti D5 RSS selections satisfy all required Protocol-A VASP labeling preconditions without submitting or modifying generated data.

## Phases
- [x] Phase 1: Plan and setup
- [x] Phase 2: Review accepted selection and D4 Protocol-A records
- [x] Phase 3: Verify current VASP batch preflight inputs and protected paths
- [x] Phase 4: Review and deliver readiness decision
- [x] Phase 5: Submit three protected Protocol-A D5 VASP batches
- [x] Phase 6: Record job IDs and one immediate scheduler check

## Key Questions
1. Are the Protocol-A decisions and PAW identities/checksums frozen for each element?
2. Do the selected inputs, base databases, and proposed protected output paths meet the VASP batch requirements?

## Decisions Made
- No DFT job will be submitted from a readiness question alone.
- D5 may use the unchanged frozen static Protocol A: standard local PAWs
  (W ZVAL 6, Ta ZVAL 5, Ti ZVAL 4), no semicore substitution, SOC excluded,
  and no spin/MAGMOM override (Ti therefore uses VASP's default non-spin
  setting).
- If separately authorized, label only the three isolated 100-POSCAR D5
  batches through `scripts/slurm/run_vasp_batch_dft.slurm` and
  `src/vasp_batch_dft.py`; do not merge labels into `current.db`.
- The user authorized D5 DFT submission on 2026-07-29. Reuse the accepted D4
  resource card: one node, 64 tasks, 24 hours, eight 8-rank concurrent VASP
  tasks, and the cluster-default partition/account.
- Submitted independent no-overwrite batches: W `13601`, Ta `13602`, and Ti
  `13603`. One immediate `squeue` check found all three pending on priority;
  no active monitoring is authorized.

## Errors Encountered
- A first `fd` count reported zero selected POSCARs because repository ignore
  rules hide `*.poscar`; direct Python `Path.glob("*.poscar")` and ASE
  validation confirmed all 100 files per element. No artifact was changed.

## Status
**Complete at the authorized submission point** - D5 Protocol-A VASP jobs
were submitted. Do not poll, validate results, merge, train M5, or run E5
without a new user request.
