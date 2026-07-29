# Task Plan: Combined MD Structure-Selection Pipeline

## Goal
Provide one protected, element-isolated submission entry point that performs
all-frame uncertainty scoring, geometry audit, and absolute-U projected-CUR
selection while retaining every required intermediate artifact.

## Phases
- [x] Phase 1: Record scope and identify the existing three-stage flow.
- [x] Phase 2: Inspect the two current selection runners and Python CLIs.
- [x] Phase 3: Implement the minimal orchestration entry point and document it.
- [x] Phase 4: Run syntax/CLI and dry-run/no-overwrite verification.
- [x] Phase 5: Deliver the combined usage contract; do not submit production selection.

## Key Questions
1. Which parameters must stay explicit rather than being silently calibrated
   during a combined run?
2. How can the pipeline retain `uncertainty_all_frames.csv`,
   `geometry_audit.csv`, and protected CUR provenance without a second
   submission?
3. How does it fail closed before CUR if scoring/audit output is incomplete,
   invalid, or insufficient for the requested target?

## Decisions Made
- The combined operation is orchestration only: it must use the existing
  score-only and absolute-U projected-CUR implementations rather than create
  a parallel selector.
- W, Ta, and Ti remain one invocation/job each; the pipeline never takes
  mixed-element paths or model globs.
- It retains the full all-frame and audit artifacts, does not bypass
  element-local `U_min`, geometry gates, approved target, or tail cap, and
  preserves no-overwrite behavior.
- The pipeline derives `U_min` by the mandated arithmetic mean of the final
  test `MAE-F` values from exactly ten matching model logs, records every
  path/value, fixes p99 and `floor(0.05 * target)`, and verifies complete
  audit coverage before CUR.
- This implementation task does not authorize D3 scoring, selection, DFT,
  merge, M3, or E3 submission.

## Errors Encountered
- The first combined memory/index patch used stale surrounding context and
  did not update `memory/index.md`; task files were updated successfully.
  Resolution: read the current concise index and apply a focused update.

## Status
**Complete** - `scripts/slurm/run_md_selection_pipeline.slurm` provides the
one-allocation score/audit/CUR path. Shell syntax, help, invalid-element
rejection, and a D2 no-overwrite guard test passed; no production selection
was submitted or changed.
