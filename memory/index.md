# Memory Index

## Current State
Three isolated unary workflows are at the completed baseline `D0 -> M0 -> E0` stage:

| Element | D0 / M0 state | E0 selected model | Phase-aligned EOS MAE / RMSE (meV/atom) |
|---|---|---|---:|
| W | 100 D0 rows; 10-fold committee complete | `train-4/4.jnn` | 3.592 / 6.741 |
| Ta | 100 D0 rows; 10-fold committee complete | `train-9/9.jnn` | 6.254 / 8.832 |
| Ti | 100 D0 rows; 10-fold committee complete | `train-3/3.jnn` | 3.288 / 6.021 |

The fixed EOS evaluations are validation-only and are located at:

- `results/W_eos_benchmark/evaluations/E0_M0/`
- `results/Ta_eos_benchmark/evaluations/E0_M0/`
- `results/Ti_eos_benchmark/evaluations/E0_M0/`

## Active Gate / Blocker
E0 is complete as the fixed M0 baseline. D1 high-temperature NVT sampling
completed and passed output validation independently for W (job 13005), Ta
(job 13006), and Ti (job 13007), all with exit code 0:0. Independent
all-frame scoring and absolute-U projected-CUR selection are complete: W, Ta,
and Ti each have 100 validated selected structures. Element-local Protocol-A
DFT labeling completed successfully for W (job 13025), Ta (job 13026), and Ti
(job 13027): each produced a validated 100-row label DB. Each label DB has
now been merged only with its own D0 database, and all three validated
200-row D1 successors have been published as the corresponding element-local
`current.db`. The D0 snapshots and successor `updated.db` files are preserved.
The prior 1000-epoch M1 committee artifacts were removed with explicit user
approval. Replacement 5000-epoch M1 training has been submitted independently:
W job 13101, Ta job 13102, and Ti job 13103. All were PENDING at the one
immediate post-submission status check. The training policy for M1 and later
committees is now 5000 epochs; M0 remains the historical 1000-epoch baseline.
`research-plan.md` is the authoritative W/Ta/Ti plan.

## Standing Constraints
- Keep W, Ta, and Ti data, databases, models, candidate pools, and EOS references independent.
- Do not add EOS structures or labels to any `current.db`.
- Use staged SLURM execution and the approved absolute-U then
  current.db-projected-CUR selection policy for any future D1 work.
- Preserve existing generated outputs unless explicit overwrite or deletion approval is given.

## Ready Assets
- Element-local `current.db` D0 data and M0 committee outputs under `W-potential/`, `Ta-potential/`, and `Ti-potential/`.
- Fixed 57-point bcc/fcc/hcp EOS references and E0 predictions for each element.
- Shared setup records: `01_` and `02_`.
- Stage records with W/Ta/Ti subsections: `03_eos_preparation/`,
  `04_D0_generation/`, `05_M0_training/`, and `06_E0_evaluation/`.
- D1 preparation: `07_D1_NVT_preparation/`.
- D1 Protocol-A DFT labeling: `08_D1_DFT_labeling/`.
- D1 merge and prior 1000-epoch M1 submission: `09_D1_merge_M1_training/`.
- M1 5000-epoch replacement: `10_M1_5000_epoch_retraining/`.

## Immediate Next Step
When requested after jobs 13101/13102/13103 complete, validate their
independent ten-member M1 committees from the published 200-row element-local
D1 `current.db` files. Do not start E1 EOS evaluation until all committees
pass output, fold-coverage, and finite-diagnostic checks.
