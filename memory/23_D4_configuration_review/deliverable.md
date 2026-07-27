# Deliverable: D4 Configuration Review and Next-Round Launch

## Outcome

Reviewed E3, froze protected element-local D4 NPT cards, and submitted the
independent D4 sampling allocations. All M3 stress preflights and no-overwrite
input/output checks passed.

## Key Results / Decisions

- D4 uses all ten matching M3 models, one established seed per element,
  `2 2 2`, the established temperature and NPT controls, and the new pressure
  grid `2, 8, 15, 25, 35, 45, 55` GPa.
- Submitted jobs: W `13235`, Ta `13236`, Ti `13237`; each requests one node,
  seven tasks, and 24 hours.
- No D4 scoring, selection, DFT, merge, M4, or E4 step has started.

## How to Use / Verify

- On a later completion/status request, query only jobs `13235`, `13236`, and
  `13237` once, then validate all seven NPT source outputs per element before
  authorizing score-only processing.

## Files Changed

- `memory/23_D4_configuration_review/`: D4 decision, preflight, and
  submission record.
- `<X>-potential/04-npt-round-2/`: protected D4 outputs produced only by the
  submitted element-local allocations.
