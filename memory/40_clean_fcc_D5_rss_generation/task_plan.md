# Task Plan: Clean-FCC D5 RSS Structure Generation

## Goal
Generate only the isolated W, Ta, and Ti D5 RSS/Mini candidate pools through
SLURM using the frozen task-39 card, then validate the generated pool
artifacts without starting scoring, selection, DFT, merging, training, or EOS.

## Phases
- [x] Phase 1: Recover the frozen D5 generator card and identify the RSS
  driver/template gap.
- [x] Phase 2: Create and validate a protected RSS SLURM submission wrapper.
- [x] Phase 3: Perform corrected no-overwrite/isolation preflight and submit
  W/Ta/Ti RSS generation retry.
- [ ] Phase 4: Validate terminal generated-pool artifacts and deliver.

## Key Questions
1. Can the repository submit one unary RSS/Mini generation process per
   element without running on a login node or deleting an existing output?
2. Do all generated artifacts retain enough atom-count/pressure and
   raw/minimized provenance for the later all-pool scoring adapter?
3. Can the generation task remain strictly isolated from all downstream D5
   scoring, selection, DFT, database, training, and EOS work?

## Decisions Made
- The user authorized D5 structure generation only, after task 39 froze the
  RSS/Mini parameters. Downstream D5 work remains out of scope.
- Each element uses only its matching M4 `train-5/5.jnn` for RSS/Mini and
  writes only below `<X>-potential/fcc-restart/05-rss-round-1/rss/`.
- No output may be overwritten; the driver must receive neither
  `--overwrite` nor an existing completed/incomplete output root.
- The user authorized deletion of only the three failed partial `rss/` roots.
  Their one failure log and empty raw/minimized case directories were
  rechecked immediately before deletion; the sibling `slurm_logs/`
  directories were not touched.
- The corrected preflight must use
  `<X>-potential/fcc-restart/current.db`, not the separate root-level
  non-FCC database. It passed the frozen SHA-256 identities, 500 finite
  unary 32-atom 3D-PBC rows, no EOS metadata, complete ten-model M4
  committee, absent RSS roots, no inherited `OVERWRITE`, and available
  `sbatch`/JSE commands.
- Corrected direct-JSE generation-only retries submitted: W `13579`, Ta
  `13580`, and Ti `13581`. The one permitted immediate `squeue` check found
  all three `RUNNING` on `lpsnode02`; do not poll further unless the user asks
  for status.
- The user separately authorized deletion of only Ta's invalid completed
  `rss/` root for regeneration, while retaining `slurm_logs/`. The root
  contained 2,804 files, had no symlinks, and was removed only after its
  parent containment and retained-log checksum checks passed. The six
  scheduler-log files remained byte-identical.
- The repeated Ta preflight accepted the frozen FCC D4 database and
  M4 `train-5` JNN hashes, absent output root, unset `OVERWRITE`, and the
  fixed one-node/one-task/24-hour direct-JSE wrapper. Ta generation retry
  `13586` was submitted with the unchanged frozen RSS/Mini card.
- `scripts/slurm/run_rss_round.slurm` is the generation-only wrapper. It
  requires SLURM, one node/one task/24 hours, explicit RSS/Mini card values,
  an absent `rss/` root, and retained raw/minimized work.
- Submitted generation-only jobs: W `13575`, Ta `13576`, and Ti `13577`.
  They use only the matching M4 `train-5` JNN and the frozen task-39 card.

## Errors Encountered
- Initial generation jobs W `13575`, Ta `13576`, and Ti `13577` all failed
  after six seconds with `1:0`. Their identical JSE logs state that RSS/Mini
  cannot be run under `srun` after resource assignment, then raise a null
  resource error. Each partial `rss/` root contains only its one failure log;
  no raw, minimized, collected, score, selection, DFT, database, training, or
  EOS artifact was produced. The wrapper now runs JSE directly within the
  `sbatch` allocation, but protected retry requires explicit authorization to
  delete only those three partial `rss/` roots.
- A combined memory update applied the task-plan hunk but not the
  nonmatching notes hunk. The cleanup record is appended separately using the
  observed notes-file context; no workflow artifact was affected.
- An unintended `/tmp/d5_rss_retry_jobids.<pid>` helper record was created
  during submission. Its three expected lines were verified, then it was
  removed immediately; no repository or workflow asset was affected.
- The corrected read-only preflight stopped at the W input-identity assertion
  before any submission because the check incorrectly used the non-FCC
  `<X>-potential/current.db` files. Those are separate 500-row, 16-atom
  states with different hashes. The frozen D4/M4 assets are below
  `<X>-potential/fcc-restart/`; use that matching `current.db` for the
  corrected preflight.
- Ta regeneration `13586` completed with exit `0:0`, but its retained inner
  Mini log reports 60 LAMMPS `Neighbor list overflow` failures. All 52
  minimized/raw atom-count provenance mismatches are exactly among those 60
  failed `(raw index, pressure)` jobs. The wrapper/JSE Mini completes despite
  that fail list and emits 1,200 files, so scheduler success and file count
  are insufficient validity gates. The user then explicitly approved the
  documented partial-pool exception: retain the root, exclude all 60 exact
  logged failures, and require complete provenance for the remaining 1,140
  candidates before selection.

## Status
**Complete under an explicit partial-pool exception** - W/Ti pools passed
full retained-artifact validation. Ta retry `13586` has 60 logged Mini
neighbor-list failures, so those entries are excluded rather than treated as
valid generation output; the remaining 1,140 candidates passed full
nonfailed-source provenance validation. Separate Ta selection `13589`
completed and validated 100 selected structures; no DFT, merge, training, or
EOS action is part of this task.
