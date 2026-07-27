# Task Plan: D2 NVT Sampling from M1

## Goal
Start independent D2 NVT candidate sampling for W, Ta, and Ti using their
validated M1 committees, the approved original D1 scale grid, and protected
element-local output roots.

## Phases
- [x] Phase 1: Confirm E1 completion, M1 committee inputs, D2 temperatures,
  scale grid, and absent protected output roots.
- [x] Phase 2: Review the NVT SLURM runner and submit three element-local D2
  sweeps.
- [x] Phase 3: Validate all D2 source trajectories and summaries.
- [ ] Phase 4: Score all D2 production frames with the M1 committees.
- [ ] Phase 5: Review and deliver.

## Key Questions
1. Are the five D2 NVT sources and all ten M1 models isolated by element?
2. Do all 15 source runs produce complete finite trajectory and summary data?

## Decisions Made
- Use the original D1 scale grid: `0.90, 0.95, 1.00, 1.05, 1.10`.
- Use the established D1 NVT controls: `2 2 2`, 50,000 steps, 1 fs,
  trajectory interval 10, log interval 1, `tau-r=0.10`, and
  friction `0.02 fs^-1`.
- Use each element's complete ten-model M1 committee; do not use the EOS
  reporting model alone.
- Do not select structures, submit DFT, merge, train M2, or run E2 in this
  task.

## Errors Encountered
- None.

## Status
**Sampling task complete** - all 15 D2 MD sources passed validation. D2
all-frame scoring and selection are tracked in
`memory/13_D2_scoring_selection/`.
