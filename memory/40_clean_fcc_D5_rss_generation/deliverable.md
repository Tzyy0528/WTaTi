# Deliverable: Clean-FCC D5 RSS Structure Generation

## Outcome
Corrected protected W/Ta/Ti D5 RSS/Mini generation initially completed through
SLURM with exit `0:0`. W/Ti pools passed retained-artifact validation. Under
separate user authorization, only Ta's invalid RSS root was deleted and
regeneration job `13586` was submitted. Although it completed at the
scheduler level, it has 60 logged Mini failures. The user explicitly approved
an auditable partial-pool policy: exclude those 60 failures and retain the
1,140 fully valid nonfailed candidates for the separate 100-structure
selection.

## Key Results / Decisions
- Generation only; no D5 scoring, selection, DFT, merge, training, or EOS.
- Jobs W `13579`, Ta `13580`, and Ti `13581` use the direct-JSE wrapper with
  one node, one task, and a 24-hour limit.
- A later focused accounting check found W `13579`, Ta `13580`, and Ti
  `13581` completed in 25--27 minutes with exit `0:0`.
- W/Ti each retain 400 raw and 1,200 mapped minimized/flat structures. Ta
  initially contained 53 minimized structures with atom counts inconsistent
  with their raw-source names; its invalid root was removed without touching
  any scheduler log, and no downstream Ta stage was started.
- Ta retry `13586` uses the unchanged frozen card, matching FCC D4/M4 inputs,
  one node, one task, 24 hours, and no overwrite option. It completed in
  25:15 with exit `0:0`, but 60 Mini LAMMPS neighbor-list overflows caused
  52 raw/minimized atom-count provenance mismatches. All 60 logged failures
  are excluded from the subsequently approved partial pool.

## How to Use / Verify
- Use `memory/41_clean_fcc_D5_rss_selection/` for the separate selection
  task. The partial-pool selection must retain the Mini failure log/checksum
  and exclusion CSV, and may use only the 1,140 valid nonfailed structures.

## Files Changed
- `memory/40_clean_fcc_D5_rss_generation/`: active generation record.
