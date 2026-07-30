# Task Plan: Clean-FCC D5 RSS Configuration

## Goal
Define an evidence-based, element-isolated D5 RSS/Mini configuration for W,
Ta, and Ti after D4/M4/E4, without generating candidates or submitting jobs.

## Phases
- [x] Phase 1: Initialize task record and recover accepted D4/M4/E4 state.
- [x] Phase 2: Review the frozen workflow requirements and prior-stage
  coverage/selection evidence.
- [x] Phase 3: Define W/Ta/Ti D5 configuration adjustments and explicit
  decision gates.
- [x] Phase 4: Deliver a no-execution D5 configuration card.

## Key Questions
1. Which RSS parameters remain frozen workflow defaults, and which require an
   element-specific adjustment after E4?
2. How should Ta's small E4 regression be addressed without modifying
   accepted D4/M4/E4 artifacts or weakening selection gates?
3. What approval and preflight gates must be satisfied before any D5 RSS job
   can be submitted?

## Decisions Made
- This task is planning-only. It must not generate RSS structures, score a
  pool, label DFT data, mutate a database, train a model, or submit a job.
- W, Ta, and Ti will retain completely independent D5 roots, committees,
  calibration, and selection records.
- Keep the documented RSS/Mini support at the unary atom-count list
  `9,10,12,15,18,20,22,25`, Mini pressures `0,20,40` GPa, and Mini controls
  `tri`, 10 loops, `etol=1e-4`, and `ftol=1e-8`. Use 50 RSS structures per
  unary case, retain raw/minimized work, and never use `--overwrite`.
- Use the force-stable member of the energy-ratio-eligible M4 committee for
  single-potential RSS/Mini relaxation: W `train-5/5.jnn`, Ta
  `train-5/5.jnn`, and Ti `train-5/5.jnn`. Score the complete retained pool
  later with all ten matching M4 models; the one-model EOS reporting choice
  is not the scoring committee.
- Ta's E4 regression does not justify changing pressure range, increasing
  the DFT budget, relaxing physical gates, adding EOS structures, or adding
  source quotas. Its adjustment is the lower-held-out-force `train-5` Mini
  relaxer plus a mandatory post-pool coverage and full-committee diagnostic
  before any DFT authorization.
- The present source tree has no production RSS all-frame scorer/geometry
  audit adapter that feeds the required `absolute_u_projected_cur_selection`
  contract. `rss_quota_cur_selection.py` is explicitly prohibited as the
  final selector. This implementation gap blocks D5 submission, not the
  configuration decision.

## Errors Encountered
- An exploratory `rg -h` used a help alias rather than the intended
  no-filename option while reading M4 logs. It produced only ripgrep help;
  rerunning with `rg --no-filename` recovered the final MAE-F values. No
  artifact was modified.

## Status
**Complete (planning only)** - the D5 RSS/Mini cards and the required
pre-submission implementation/approval gates are recorded. No D5 artifact or
job was created.
