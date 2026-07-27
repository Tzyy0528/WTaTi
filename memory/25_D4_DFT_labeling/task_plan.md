# Task Plan: D4 Protocol-A VASP Labeling

## Goal
Validate the completed independent D4 Protocol-A VASP labels for W, Ta, and Ti without modifying any training database.

## Phases
- [x] Phase 1: Confirm terminal SLURM states for the three submitted D4 label jobs.
- [x] Phase 2: Validate each element-local labeled database and VASP task coverage.
- [x] Phase 3: Record the result and deliver status; do not merge, train M4, or run E4.

## Key Questions
1. Did all three jobs complete successfully?
2. Does each output contain exactly the matching 100 finite, unary, 16-atom D4 labels?

## Decisions Made
- D4 label validation is read-only. `current.db`, EOS assets, merges, M4, and E4 remain out of scope.

## Errors Encountered
- Exact binary geometry-fingerprint comparison failed because the static
  VASP/OUTCAR round-trip changes coordinates by at most `4.815e-08 A` and
  cell entries by at most `4.994e-09 A`. Resolution: validate the explicit
  one-to-one source mapping, composition, and geometry agreement at a
  conservative `1e-7 A` tolerance.

## Status
**Complete** - Jobs W `13248`, Ta `13249`, and Ti `13250` produced three
validated, isolated 100-row D4 label databases. All `current.db` files remain
the unchanged 400-row D3 state; merge, M4, and E4 have not started.
