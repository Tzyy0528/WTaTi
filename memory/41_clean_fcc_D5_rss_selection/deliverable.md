# Deliverable: Clean-FCC D5 RSS Selection

## Outcome
W and Ti RSS/Mini pools passed validation, and a protected RSS all-frame
scoring/geometry-audit/projected-CUR adapter is implemented and tested.
The initial W/Ti jobs `13584` and `13585` failed at Stage 2 because of an
archive-path bug; it is fixed and verified. Under subsequent explicit cleanup
authorization, only their Stage-1 selection roots were removed and corrected
W `13591` and Ti `13592` selection jobs completed and validated 100 selected
structures each. The user approved an auditable Ta
partial-pool exception: 60 logged Mini failures are excluded, leaving 1,140
valid candidates. Ta selection job `13589` completed successfully and
produced 100 fully validated selected structures.

## Key Results / Decisions
- Selection will remain isolated by element and will use all ten matching M4
  models for uncertainty.
- No DFT, database, training, or EOS stage is included.
- W/Ti each contain 400 raw and 1,200 fully mapped minimized/flat structures
  with exact 8-by-50 atom-count and 3-by-50 pressure coverage.
- Ta has 53 atom-count/provenance-mismatched minimized structures and cannot
  enter the pipeline until corrected.
- W and Ti run only their own FCC D4 base database, M4 committee, RSS pool,
  and new `rss-selection/` root, targeting 100 structures with a tail cap of
  5. Neither command uses overwrite behavior.
- Both failed jobs completed 1,200-frame all-committee scoring but could not
  start the geometry audit because their CSVs retained temporary archive
  paths. The source now records final archive paths, with a synthetic test
  confirming the correction.
- Ta `13586` has 60 logged Mini `exit=1` pairs, including all 52 atom-count
  mismatches. The adapter records these in `mini_failure_exclusions.csv`,
  scores only the 1,140 strict-valid nonfailed sources, and retains the
  failure-log checksum; target 100 and all selection gates are unchanged.
- Ta `13589` scored 1,140 frames; its 166 post-`U_min` frames produced 124
  geometry-valid candidates and 42 rejections. Current-D4-projected CUR
  selected exactly 100 final POSCARs, with 2 p99-tail selections (cap 5).
- W `13591` and Ti `13592` retain the original strict-complete 1,200-frame
  pools and target 100 structures. Both completed with exit `0:0` and passed
  all-frame, geometry, current-D4-projected CUR, capped-tail, and final
  POSCAR provenance validation.

## How to Use / Verify
- All three D5 selections are complete. Any DFT action for Ta, W, or Ti
  requires separate authorization.

## Files Changed
- `src/rss_all_frame_scoring.py`: RSS flat-pool validation, archive
  materialization, and all-committee scoring adapter.
- `scripts/slurm/run_rss_selection_pipeline.slurm`: protected RSS score,
  geometry-audit, and projected-CUR pipeline.
- `docs/source_function_index.md`, `docs/unary_workflow.md`,
  `scripts/slurm/README.md`: RSS selection entry point and behavior.
- `memory/41_clean_fcc_D5_rss_selection/`: active selection record.
