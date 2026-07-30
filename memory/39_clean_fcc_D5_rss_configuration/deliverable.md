# Deliverable: Clean-FCC D5 RSS Configuration

## Outcome
The planning-only D5 RSS/Mini configuration is defined for W, Ta, and Ti.
No D5 structure, output directory, database, or scheduler job was created.

## Key Results / Decisions
- Use the isolated `05-rss-round-1/` root and only the matching 500-row D4
  database and ten-member M4 committee for each element.
- RSS/Mini card: clean-FCC seed atomic volume W/Ta/Ti
  `15.903934900 / 18.151564915 / 17.345854575` A3/atom; atom counts
  `9,10,12,15,18,20,22,25`; 50 raw structures per unary RSS case; Mini
  pressures `0,20,40` GPa; `tri`, 10 loops, `etol=1e-4`, `ftol=1e-8`.
- Retain raw/minimized artifacts with `--keep-raw --keep-minimized-work`;
  use `--jobs 1` and never use `--overwrite`.
- Use `train-5/5.jnn` as the single force-stable RSS/Mini relaxer for all
  three elements. The subsequent full-pool uncertainty score must still use
  all ten matching M4 models.
- Ta's E4 regression is addressed conservatively: change its Mini relaxer
  from E4's energy-selected `train-2` (180.1 meV/A held-out force MAE) to
  `train-5` (155.8 meV/A), but retain the standard pressure/atom-count
  coverage, `N_DFT=100`, D0 physical gates, and projected-CUR policy.
- D5 selection remains `U_min` recalculated from M4 logs, geometry-valid
  p99 tail with cap 5, only matching-D4 projected CUR, and the documented
  descriptor card. EOS data remains validation-only.
- A production RSS flat-POSCAR all-frame scoring/geometry-audit adapter is
  missing from the indexed implementation. Its absence blocks submission;
  `rss_quota_cur_selection.py` must not be substituted as final selection.

## How to Use / Verify
- Full card, per-element gates, expected `U_min`, and implementation gate:
  `memory/39_clean_fcc_D5_rss_configuration/notes.md`.
- Before any user-authorized D5 submission, validate the matching D4 DB and
  M4 digests, absent output paths, an approved RSS scoring adapter, and
  SLURM resources.

## Files Changed
- `memory/39_clean_fcc_D5_rss_configuration/`: completed planning record.
