# Memory Index

## Current State
The independent W, Ta, and Ti workflows completed replacement `D1 -> M1 ->
E1`. Every element-local `current.db` is a validated 200-row D1 successor:
100 preserved D0 rows followed by 100 labels from only its own D1 selection.

The fixed validation-only E0 references remain at:

- `results/W_eos_benchmark/evaluations/E0_M0/`
- `results/Ta_eos_benchmark/evaluations/E0_M0/`
- `results/Ti_eos_benchmark/evaluations/E0_M0/`

## Active Gate / Blocker
E0 is the fixed M0 baseline. D1 high-temperature NVT sampling completed and
passed validation independently for W (job 13005), Ta (job 13006), and Ti
(job 13007); all-frame scoring jobs 13011--13013 also completed. Their D1
MD trajectories and all-frame scoring CSVs are retained.

The historical D1 projected-CUR selection used a production-pool P95 cutoff.
The user revoked that policy and explicitly authorized removal of its CUR
outputs, labels, D1 successors, M1, E1, D2, and later memory. Replacement
D1 CUR completed successfully: each element has 100 validated selected
structures. Protocol-A DFT jobs W 13133, Ta 13134, and Ti 13135 completed
successfully. Each new D1 label DB contains 100 finite unary 16-atom labels.
They were merged only with their corresponding D0 base, and all D1
`current.db` files were published after validation. M1 jobs W 13138, Ta
13139, and Ti 13140 completed successfully and all three committees passed
model, fold-coverage, and finite-diagnostic validation. Fixed-reference E1
is complete: W and Ti regressed in raw and phase-aligned EOS errors; Ta
improved phase-aligned shape but regressed in raw cross-phase energy.

## Standing Constraints
- Keep W, Ta, and Ti data, databases, models, candidate pools, and EOS references independent.
- Do not add EOS structures or labels to any `current.db`.
- Use staged SLURM execution and absolute-U then current.db-projected-CUR
  selection for the replacement D1 work.
- Derive each `U_min` as the arithmetic mean of the final test `MAE-F`
  values in the ten models used for that element and round, converted to
  eV/A; never use a percentile-only MD-pool cutoff or copy a threshold
  between elements/model versions.
- Preserve existing generated outputs unless explicit overwrite or deletion approval is given.

## Ready Assets
- Element-local `current.db` D0 data and M0 committee outputs under `W-potential/`, `Ta-potential/`, and `Ti-potential/`.
- Fixed 57-point bcc/fcc/hcp EOS references and E0 predictions for each element.
- Shared setup records: `01_` and `02_`.
- Stage records with W/Ta/Ti subsections: `03_eos_preparation/`,
  `04_D0_generation/`, `05_M0_training/`, and `06_E0_evaluation/`.
- D1 preparation: `07_D1_NVT_preparation/`.
- D1 restart and reselection: `08_D1_reselection/`.
- D1 Protocol-A labeling: `09_D1_DFT_labeling/`.
- D1 merge and M1 training: `10_D1_merge_M1_training/`.
- M1 fixed-reference E1 validation: `11_M1_validation_E1_evaluation/`.

## Immediate Next Step
D2 NVT jobs W `13142`, Ta `13143`, and Ti `13144` completed successfully.
All 15 original-D1-grid sources passed provenance, finite-data, frame-count,
summary-count, and final-log validation. The next gated action is element-local
all-frame uncertainty scoring with the full M1 committees; selection and later
stages remain unstarted.
