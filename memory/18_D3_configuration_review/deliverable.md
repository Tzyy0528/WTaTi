# Deliverable: Post-E2 Recommended Next Step

## Outcome
All three lightweight all-model NPT stress preflights passed, protected D3
parameter cards were frozen, and the independent D3 NPT allocations completed
successfully. All 21 NPT sources passed trajectory and summary validation.

## Key Results / Decisions
- First prepare and approve distinct W/Ta/Ti D3 parameter cards plus
  all-model finite-stress preflights.
- Retain all M2 models for sampling and the established all-frame,
  recalibrated-U, physical-gate, projected-CUR selection policy.
- Keep one prescribed starting structure per element. Use the bcc/fcc/hcp EOS
  curves strictly to test transferability, not to introduce phase-specific MD
  sources or EOS labels into training.
- Address W, Ta, and Ti diagnostics by adjusting the same-source
  pressure/temperature/volume sampling card only.
- Each card uses its matching 300-row D2 database, all ten M2 JNNs, its
  established seed/temperature, `2 2 2`, and 1--50 GPa NPT starting grid.
- W, Ta, and Ti each passed finite energy, force, and six-component stress
  checks for all ten models on their matching 16-atom repeated seed.
- D3 jobs: W `13168`, Ta `13169`, and Ti `13170`; all were running in the
  one immediate focused queue check and later completed with exit `0:0`.
- Every element has seven validated `P-1GPa` through `P-50GPa` sources:
  35,007 finite 16-atom periodic frames and seven 50,001-step finite NPT
  pressure summaries.

## How to Use / Verify
- The complete hashes and guarded exact submission pattern are in
  `memory/18_D3_configuration_review/notes.md`.
- After explicit D3-MD authorization, submit through
  `scripts/slurm/run_md_round.slurm`, then validate all seven NPT sources per
  element before all-frame scoring.
- The next stage requires separate authorization: full M2 all-frame
  uncertainty scoring in `--score-only` mode, then independent `U_min`
  calibration before selection.

## Files Changed
- `memory/18_D3_configuration_review/`: post-E2 planning record.
