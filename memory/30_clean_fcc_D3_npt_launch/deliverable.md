# Deliverable: Clean-FCC D3 NPT Launch

## Outcome
All three protected D3 NPT cards and finite-stress/no-overwrite preflights
passed. Independent W, Ta, and Ti D3 NPT allocations were submitted.

## Key Results / Decisions
- W/Ta/Ti use their matching 32-atom seed with `--rep 1 1 1`, the full
  ten-model M2 committee, and `1,5,10,20,30,40,50` GPa.
- Temperatures are explicitly 4928.15, 4485.65, and 2750.65 K,
  respectively; the user authorization overrides the prior review hold.
- All 30 models returned finite energy, forces, and `(6,)` stress through the
  production calculator/NPT interface. The D3 roots were absent at
  no-overwrite preflight; M3/E3 roots remain absent.
- Jobs W `13513`, Ta `13514`, and Ti `13515` each request one node, seven
  one-core tasks, and 24 hours. The single immediate queue check found W
  `PENDING (None)` and Ta/Ti `PENDING (Priority)`.

## How to Use / Verify
- On a later status/completion request, make one focused terminal-state check.
  After terminal success, validate seven matching NPT sources per element
  before separately authorizing all-frame scoring.

## Files Changed
- `memory/30_clean_fcc_D3_npt_launch/`: D3 launch record.
