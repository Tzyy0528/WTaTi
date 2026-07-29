# Task Plan: Clean-FCC D3 NPT Launch

## Goal
Launch independent W, Ta, and Ti clean-FCC D3 NPT sampling from their
validated D2/M2 states, using only finite-stress M2 committees and protected
new D3 output roots.

## Phases
- [x] Phase 1: Record user authorization and isolate scope.
- [x] Phase 2: Verify NPT worker behavior, freeze D3 cards, and preflight.
- [x] Phase 3: Submit W/Ta/Ti D3 NPT jobs with SLURM.
- [x] Phase 4: Record submission status and next validation gate.

## Key Questions
1. Does every M2 model provide finite stress for its matching 32-atom seed
   before an NPT run is allowed?
2. What element-local D3 temperature and pressure cards can be frozen without
   reusing another element's generated data?
3. Are all D3 outputs absent and protected from overwrite?

## Decisions Made
- The user explicitly overrides the preceding review hold and authorizes D3
  launch for all three elements.
- W, Ta, and Ti retain isolated D3 paths, databases, M2 committees, seeds,
  pressures, trajectories, and later selections.
- No D3 selection, DFT, merge, M3, or E3 action is authorized by this launch.
- The D3 cards explicitly use the section 8.3 high-temperature targets
  (W/Ta/Ti: 4928.15/4485.65/2750.65 K), rather than inheriting the D2 NVT
  temperatures, with the authorized `1,5,10,20,30,40,50` GPa pressure grid.
- `src/md_worker.py` requires every NNAP calculator to return stress for NPT;
  all 30 matching M2 models passed finite energy, `(32,3)` force, `(6,)`
  stress, and ASE `NPT` initialization on only their matching 32-atom seed.
- The no-overwrite preflight passed: each matching current DB is its expected
  300-row checksum, all three seeds and all 30 ordered M2 JNNs are valid,
  and D3/M3/E3 output roots remain absent.

## Errors Encountered
- A first lightweight preflight used the module-loaded `python3` directly;
  that interpreter lacks `jsex.nnap`, so it stopped before opening a model or
  creating a D3 output. Resolution: rerun the same no-write probe through
  `jse --pythontext`, the runtime used by the production worker.

## Status
**Complete** - W `13513`, Ta `13514`, and Ti `13515` were submitted as
independent protected one-node, seven-task, 24-hour D3 NPT allocations. The
one permitted immediate combined `squeue` check found W `PENDING (None)`,
Ta `PENDING (Priority)`, and Ti `PENDING (Priority)`. Do not poll. On a
later user completion/status request, make one focused terminal-state check
and validate all seven element-local NPT sources before any scoring.
