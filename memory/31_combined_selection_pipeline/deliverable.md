# Deliverable: Combined MD Structure-Selection Pipeline

## Outcome
Delivered a protected one-submission MD selection orchestrator:
`scripts/slurm/run_md_selection_pipeline.slurm`.

## Key Results / Decisions
- It runs full-committee score-only uncertainty, complete geometry audit, and
  current.db-projected CUR sequentially in one element-local allocation.
- It derives and records `U_min` from the final test `MAE-F` values in the
  exact ten matching model logs; p99 and `floor(0.05 * target)` are fixed.
- It requires an approved target, distance/void gates, and descriptor card;
  it refuses cross-element paths and all pre-existing output artifacts.
- No production selection was launched.

## How to Use / Verify
- Run `bash scripts/slurm/run_md_selection_pipeline.slurm --help`.
- Submit only after MD validation and card approval; see the generic command
  in `docs/unary_workflow.md` section "Combined execution after a frozen
  selection card."
- The runner retains `uncertainty_all_frames.csv`, `geometry_audit.csv`,
  model-derived `U_min` record, and the protected CUR/POSCAR provenance.

## Files Changed
- `scripts/slurm/run_md_selection_pipeline.slurm`: new one-allocation
  score/audit/CUR orchestrator.
- `research-plan.md`: combined-run execution contract.
- `docs/source_function_index.md`: indexed combined entry point.
- `docs/unary_workflow.md`: documented generic submission card.
- `memory/31_combined_selection_pipeline/`: task record.
