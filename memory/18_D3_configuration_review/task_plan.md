# Task Plan: Post-E2 D3 Configuration Review

## Goal
Identify the gated, element-local next workflow step after E2 and define the
required review items before any D3 NPT sampling authorization.

## Phases
- [x] Phase 1: Review M2/E2 evidence and workflow stage order.
- [x] Phase 2: Define D3 readiness checks and element-specific review focus.
- [x] Phase 3: Deliver the recommended next action without submitting jobs.
- [x] Phase 4: Run lightweight all-model NPT stress preflights.
- [x] Phase 5: Freeze and validate separate D3 parameter cards without
  submitting MD.
- [x] Phase 6: Submit independent protected W, Ta, and Ti D3 NPT sweeps.
- [x] Phase 7: Validate completed D3 NPT trajectories before scoring.

## Key Questions
1. Does the workflow permit automatic D3 submission after the E2 results?
2. What parameter-card and physical checks are mandatory before D3?
3. Which E2 failure modes need element-specific attention?

## Decisions Made
- Do not start D3 automatically: E2 regressed in at least one required metric
  for every element and the research plan requires an adjusted next
  element-local configuration after review.
- The nominal next workflow stage, if authorized, is independent
  `D3 -> M3 -> E3` NPT sampling from M2, not RSS or a mixed-element run.
- User clarified the scientific design: use one preselected starting structure
  per element for MD, and evaluate transferability to all three EOS phases.
  Do not add fcc/hcp EOS structures or separate phase sources to MD/DFT
  training merely because their validation error is larger.

## Errors Encountered
- A direct `python3` stress-preflight attempt after `module load jse` could
  import ASE but not `jsex` (`ModuleNotFoundError`). This is an environment
  invocation issue, not a model failure; rerun the identical calculator probe
  through the JSE Python entry point used by `md_worker.py`.
- An initial JSE import smoke test queried `NNAP.__name__`, which the JEP
  proxy does not expose. The import itself succeeded; rerun without that
  unsupported introspection attribute.

## Status
**Complete** - D3 jobs W `13168`, Ta `13169`, and Ti `13170` completed with
zero exit status. All 21 NPT sources passed finite-output and frozen-control
validation. All-frame M2 uncertainty scoring is the next separate,
user-authorized stage.
