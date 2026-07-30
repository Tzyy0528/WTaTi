# Memory Index

## Current State
Task `memory/38_clean_fcc_D4_to_M4_E4/` is complete. The isolated clean-FCC
W, Ta, and Ti workflows each accepted 100 D4 Protocol-A labels, atomically
published their own 500-row D4 `current.db`, trained/validated a ten-fold M4
committee, and accepted the fixed-reference E4 EOS evaluation.

E4 aggregate raw / phase-aligned MAE (meV/atom) is W
`53.287499 / 16.061060`, Ta `73.655557 / 9.142611`, and Ti
`31.118935 / 2.870559`. The selected E4 models are W `train-5/5.jnn`, Ta
`train-2/2.jnn`, and Ti `train-9/9.jnn`. D4 databases, M4 JNN contents, and
Protocol-B EOS reference CSVs remained checksum-unchanged during E4.

Task `memory/39_clean_fcc_D5_rss_configuration/` completed a no-execution D5
RSS/Mini card. It uses the standard unary atom-count and 0/20/40 GPa Mini
coverage, retained raw/minimized provenance, 100-label projected-CUR policy,
and force-stable `train-5/5.jnn` single-model relaxation (with all ten M4
models retained for later scoring). Ta keeps its physical/selection policy;
only its Mini relaxer changes from the energy-reporting model to the
lower-held-out-force model.

Task `memory/40_clean_fcc_D5_rss_generation/` initially submitted
generation-only RSS/Mini jobs W `13575`, Ta `13576`, and Ti `13577`; all
failed in six seconds because the wrapper placed JSE under `srun`. The user
authorized deletion of only the resulting partial `rss/` roots, leaving the
sibling `slurm_logs/` directories untouched. The direct-JSE wrapper and a
corrected FCC-D4/M4 preflight are now accepted. Retries W `13579`, Ta
`13580`, and Ti `13581` completed successfully. W/Ti pools passed validation;
Ta had 53 raw/minimized provenance mismatches. The user then authorized
deletion of only Ta's invalid `rss/` root, with its six scheduler-log files
verified unchanged. Corrected Ta regeneration job `13586` completed with
exit `0:0` but is again invalid: its Mini log records 60 LAMMPS neighbor-list
overflows, exactly encompassing all 52 raw/minimized atom-count mismatches.
The user explicitly approved retaining only the 1,140 fully valid nonfailed
Ta candidates. Protected Ta selection job `13589` completed successfully:
1,140 scored, 166 post-U, 124 geometry-valid, and exactly 100
current-D4-projected-CUR selected POSCARs; 2 fall in the capped tail layer.

Task `memory/41_clean_fcc_D5_rss_selection/` confirmed W `13579`, Ta
`13580`, and Ti `13581` completed with exit `0:0`. W/Ti each have a valid
400-raw/1,200-minimized-flat pool with complete atom-count/pressure
provenance. Ta has 53 minimized/raw atom-count mismatches and is blocked from
selection pending authorized remediation. The former RSS flat-POSCAR adapter
gap is now filled by `src/rss_all_frame_scoring.py` and
`scripts/slurm/run_rss_selection_pipeline.slurm`. Protected W/Ti selection
jobs `13584` and `13585` both failed in Stage 2 after scoring their full
1,200-frame pools. The new adapter recorded temporary archive paths in CSVs;
that bug is fixed and syntax/synthetic-path verified. The user authorized
deletion of only the two Stage-1 W/Ti `rss-selection/` roots; their
`slurm_logs/` checksums were unchanged and their RSS pools were retained.
Corrected W/Ti selection jobs `13591` and `13592` completed successfully and
each independently validated 100 selected POSCARs. W metrics are
1,200 scored / 373 post-U / 258 geometry-valid / 115 rejected / 0 tail; Ti
metrics are 1,200 / 158 / 158 / 0 / 2 tail.

Task `memory/42_clean_fcc_D5_dft_readiness/` completed a read-only
Protocol-A and VASP-batch preflight audit. All three 100-POSCAR D5 batches,
their frozen standard PAWs, 500-row D4 bases, and absent protected D5 outputs
passed. Under explicit user authorization, independent no-overwrite
Protocol-A VASP jobs W `13601`, Ta `13602`, and Ti `13603` were submitted;
one immediate check found them pending. It includes no merge, training, or
evaluation.

## Active Gate / Blocker
All W/Ta/Ti D5 selections and submission-time preflight are complete; VASP
jobs W `13601`, Ta `13602`, and Ti `13603` are submitted. Do not poll or
inspect them unless requested. After terminal completion, label validation is
required before any separately authorized merge, M5 training, or E5
evaluation. The RSS adapter preserves the required all-frame
absolute-U/current-DB-projected CUR policy; `rss_quota_cur_selection.py`
remains disallowed as a final selector.

## Standing Constraints
- Keep W, Ta, and Ti databases, committees, candidate pools, trajectories,
  DFT roots, and EOS outputs completely isolated.
- EOS structures and labels are validation-only and must never enter any
  `current.db`.
- Do not overwrite generated artifacts, use legacy `nncalc`, or begin D5/RSS,
  MD, labeling, or retraining without explicit user authorization.
- Preserve the accepted D4 500-row states and M4/E4 records. Future
  scientific decisions should use the fixed-reference results, not mutate
  them.

## Ready Assets
- W/Ta/Ti D4 `current.db` files: 500 validated finite unary 32-atom rows
  each.
- W/Ta/Ti M4 committees:
  `<X>-potential/fcc-restart/model_versions/M4_from_D4/train-committee/`.
- Accepted E4 records:
  `<X>-potential/fcc-restart/evaluations/E4_M4/`.
- Completed D5 configuration:
  `memory/39_clean_fcc_D5_rss_configuration/{task_plan.md,notes.md,deliverable.md}`.
- Submitted D5 generation task:
  `memory/40_clean_fcc_D5_rss_generation/`.
- Complete audit and deliverable:
  `memory/38_clean_fcc_D4_to_M4_E4/{task_plan.md,notes.md,deliverable.md}`.
- Earlier clean-FCC records remain available in `memory/28_*` through
  `memory/37_*`; E3 is recorded in
  `memory/36_clean_fcc_M3_validation_and_E3/`.

## Immediate Next Step
Obtain separate authorization before any Ta/W/Ti D5 DFT labeling; preserve
the selected-structure provenance and do not modify `current.db`.
