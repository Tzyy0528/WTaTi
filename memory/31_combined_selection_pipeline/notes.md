# Notes: Combined MD Structure-Selection Pipeline

## Sources

### Source 1: User request
- The currently separate structure-selection steps should be available as one
  combined operation.

### Source 2: Authoritative workflow
- Path: `research-plan.md`, sections 10.1--10.4.
- Key points:
  - Score every production frame with the full matching committee.
  - Preserve `uncertainty_all_frames.csv`; apply absolute-U and the two
    periodic geometry gates; retain a complete geometry audit.
  - Use current.db-projected CUR and the capped p99 extreme-U layer.

### Source 3: Entry-point index
- Path: `docs/source_function_index.md`.
- Key points:
  - `scripts/slurm/run_uncertainty_scoring.slurm` is the supported score-only
    runner.
  - `scripts/slurm/run_absolute_u_projected_cur.slurm` is the supported
    geometry-audit/CUR runner.

### Source 4: Existing implementation contracts
- Paths: `scripts/slurm/run_uncertainty_scoring.slurm`;
  `scripts/slurm/run_absolute_u_projected_cur.slurm`;
  `src/stratified_uncertainty_selection.py`;
  `src/absolute_u_projected_cur_selection.py`.
- Key points:
  - The scorer refuses an existing all-frame CSV and its `--score-only` mode
    writes no percentile-bin candidates.
  - Audit-only CUR applies absolute-U plus only the periodic distance/void
    gates and atomically writes one record per inspected frame.
  - Final CUR atomically publishes a new output root and already writes
    candidate/rejection/CUR/tail/POSCAR provenance.
  - The existing final selector resolves linear tail quantiles itself, so
    calling it after a complete audit retains exactly the current policy.

## Commands and Observations

```bash
# Lightweight implementation checks; no production selection is launched.
bash -n scripts/slurm/run_md_selection_pipeline.slurm
bash scripts/slurm/run_md_selection_pipeline.slurm --help
git diff --check -- scripts/slurm/run_md_selection_pipeline.slurm \
  research-plan.md docs/source_function_index.md docs/unary_workflow.md

# A synthetic SLURM environment against the completed D2 round confirms that
# an existing all-frame CSV stops before model loading or output creation.
SLURM_JOB_ID=999 bash scripts/slurm/run_md_selection_pipeline.slurm \
  --element W --round-dir W-potential/fcc-restart/02-nvt-round-2 \
  --base W-potential/fcc-restart/current.db \
  --jnn-glob 'W-potential/fcc-restart/model_versions/M1_from_D1/train-committee/train-*/*.jnn' \
  --mode nvt --scales 0.95 1.00 1.05 1.10 1.15 \
  --target 100 --min-distance 1.695596956 \
  --max-normalized-void 0.946305262 \
  --r-c 6.0 --n-max 5 --l-max 6 --similarity-threshold 0.99999
# Expected: exit 1, refusing the existing uncertainty_all_frames.csv.
```

## Synthesized Findings

### Delivered execution contract

`scripts/slurm/run_md_selection_pipeline.slurm` accepts exactly one element,
round, base DB, ten-model matching JNN glob, explicit NVT/NPT source grid,
approved target, distance/void limits, and descriptor parameters. It rejects
cross-element potential paths and every pre-existing all-frame/audit/CUR
output before it writes any selection artifact.

Within one one-node, one-task allocation, it:

1. parses the final `MAE-F: train | test` line from all ten model logs,
   writes `selection-u-min-<jobid>.txt`, and calculates the required
   arithmetic-mean test-force `U_min` in eV/A;
2. executes the existing full-committee `--score-only` implementation and
   retains `uncertainty_all_frames.csv`;
3. executes the existing audit-only selector with zero frame gaps and only
   absolute-U/distance/void gates, retaining `geometry_audit.csv`;
4. verifies exact post-equilibration/post-`U_min` audit coverage, finite
   geometry fields, and at least `target` geometry-valid frames;
5. executes the existing projected-CUR selector with zero frame gaps,
   p99-tail policy, and deterministic `tail_max=floor(0.05*target)`.

The DFT target, geometry thresholds, and descriptor policy remain required
arguments. The runner does not derive a budget from an unlabeled pool,
relax gates, add source/force/volume filters, submit DFT, or continue to
merge/training/EOS.

### Verification

- `bash -n`, `--help`, and `git diff --check` passed.
- An invalid-element CLI test exits `2` before any file operation.
- The completed W D2 round test exits `1` with
  `Refusing to overwrite existing selection output:
  .../uncertainty_all_frames.csv`; it creates no output.
- No D3 score, audit, CUR, DFT, merge, model, or EOS job was submitted.
