# Task Plan: Clean-FCC D5 RSS Selection

## Goal
Validate the completed isolated W, Ta, and Ti D5 RSS/Mini pools and perform
only a policy-compliant all-frame selection when a production RSS
scoring/geometry-audit adapter is available.

## Phases
- [x] Phase 1: Confirm terminal generation status and validate each RSS/Mini
  pool read-only.
- [x] Phase 2: Identify or implement and verify the missing RSS all-frame
  scoring/geometry-audit adapter.
- [x] Phase 3: Freeze selection cards and submit protected all-frame scoring
  and projected-CUR selection.
- [x] Phase 4: Validate selection provenance and deliver; do not label DFT.

## Key Questions
1. Did each direct-JSE retry produce complete, finite, unary, provenance-rich
   RSS/Mini artifacts for every configured source condition?
2. Is there an existing production adapter that maps flat RSS POSCARs to the
   required all-frame uncertainty, physical-gate, and current-DB-projected
   CUR workflow without using quota-CUR?
3. If not, what minimal implementation and verification are required before
   an expensive scoring/selection submission is safe?

## Decisions Made
- The user requests the next D5 step: structure selection. This does not
  authorize DFT labeling, database merging, M5 training, or E5 evaluation.
- W, Ta, and Ti remain fully isolated. EOS validation assets remain excluded
  from all candidate and training paths.
- Final RSS selection must retain the fixed D5 policy: all-ten-M4 scoring,
  recomputed absolute `U_min`, periodic distance/void gates,
  current-D4-projected CUR, geometry-valid linear-p99 tail with cap 5, and
  auditable final POSCAR provenance. `rss_quota_cur_selection.py` is not a
  final-selector substitute.
- The minimal adapter will validate each flat/minimized/raw RSS provenance
  chain, score all validated flat POSCARs with the ten-model committee, and
  atomically write per-atom-count/per-Mini-pressure extxyz archives plus
  all-frame and source-map CSVs. This supplies the existing audited
  absolute-U/projected-CUR selector without changing its semantics.
- The user explicitly approves a documented Ta partial-pool policy: exclude
  only the 60 `(raw index, Mini pressure)` failures named in the retained
  `LMP FAIL LIST`, retain an exclusion CSV, require complete valid coverage
  of every nonfailed source, and select the unchanged target of 100 only from
  the resulting 1,140 valid structures. Do not silently accept unlogged
  omissions, malformed nonfailed structures, or any failed Mini output.
- The user authorized cleanup of only the failed W/Ti `rss-selection/` roots
  to rerun their selection. Each root was confirmed to contain only Stage-1
  scoring artifacts, then deleted after containment/no-symlink checks; each
  sibling `slurm_logs/` tree retained an unchanged aggregate checksum. The
  W/Ti RSS generation pools were not changed.

## Errors Encountered
- The initial read-only pool validator stopped before structure checks because
  it matched the shell-escaped command-record text with unescaped
  comma-list tokens. Inspect the recorded command format and make the
  validator parse it safely; no pool artifact was changed and no selection
  job was submitted.
- The corrected validator accepted all W artifacts, then found that
  `Ta-00051-0.poscar` does not have the atom count of
  `raw/unary-Ta/Ta-00051.poscar`. Diagnose whether Mini's filename-to-raw
  mapping is non-identity or the Ta minimization output is corrupted before
  validating the remaining pools or submitting selection.
- Read-only comparison established a Ta-specific pool defect, not a benign
  naming convention: 53 of 1,200 minimized files have a different atom count
  from their filename-matched raw source and the minimized count distribution
  is no longer the required 150 structures per configured atom count. Ta
  cannot enter selection without a provenance-preserving correction or a
  user-authorized regeneration; W and Ti remain isolated.
- Initial adapter tests exposed a path-normalization bug: an absolute
  manifest source path was compared with a relative minimized directory,
  falsely rejecting valid W/Ti provenance. Normalize the directory before
  comparison. The standalone test shell also lacked the JSE Python
  environment; rerun all import-dependent checks after `module load jse`.
- One combined memory update applied the task-plan hunk but not the
  nonmatching notes hunk. Append the test record separately using the
  observed notes context; no pool or selection artifact was affected.
- The first W/Ti submission preflight stopped before checking inputs because
  its root-level Python heredoc did not add `src/` before importing the new
  adapter. Add that explicit import path and rerun the read-only preflight;
  no selection job or output was created.
- A minimal command-presence preflight did not find `jse` in the bare login
  shell. This was expected module initialization, not a missing dependency:
  after `source /etc/profile.d/modules.sh; module load jse`, the JSE runner
  was available and the no-overwrite W/Ti preflight passed.
- W `13584` and Ti `13585` both failed at Stage 2 after successful all-frame
  scoring. The atomic scorer stored temporary-root archive paths in its CSVs;
  after the root was renamed, the geometry audit could not find those paths.
  The adapter now records the final archive path and a synthetic
  materialization test passed. The two partial `rss-selection/` roots are
  protected generated outputs and cannot be deleted or overwritten without
  explicit user authorization.
- The first combined W/Ti post-run validator compared Ti's numeric
  `min_distance` string with a trailing-zero literal, producing a false
  assertion after W had passed. Revalidate Ti with numeric tolerance; all
  provenance, geometry, CUR, and 100-POSCAR checks then passed.

## Status
**Selection complete** - Ta `13589`, W `13591`, and Ti `13592` completed
with exit `0:0` and each independently validated exactly 100 selected
structures under its own D4/M4/RSS policy. No DFT/merge/training/EOS action
is authorized.
