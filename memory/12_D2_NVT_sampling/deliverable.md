# Deliverable: D2 NVT Sampling from M1

## Outcome
Independent W, Ta, and Ti D2 high-temperature NVT sweeps completed from their
respective ten-model M1 committees. All 15 scale sources passed post-run
trajectory, summary, and provenance validation.

## Key Results / Decisions
- W: job `13142`, completed `0:0`, `W-potential/02-nvt-round-2/`
- Ta: job `13143`, completed `0:0`, `Ta-potential/02-nvt-round-2/`
- Ti: job `13144`, completed `0:0`, `Ti-potential/02-nvt-round-2/`
- Every sweep uses only the original five-scale D1 grid and approved NVT
  controls. No scoring, selection, DFT, merge, M2, or E2 work was launched.

## How to Use / Verify
- The next gated stage is all-frame uncertainty scoring with each respective
  M1 committee, writing an element-local `uncertainty_all_frames.csv`.

## Files Changed
- `memory/12_D2_NVT_sampling/`: D2 planning, preflight, and submission record.
