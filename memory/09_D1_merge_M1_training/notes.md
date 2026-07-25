# Notes: D1 Merge and M1 Training

## Element-Local Merge Inputs and Outputs

| Element | D0 base input | Validated D1 labels | Validated D1 successor / published current |
|---|---|---|---|
| W | `W-potential/current.db` | `W-potential/01-nvt-round-1/W_D1_selected_labeled.db` | `W-potential/01-nvt-round-1/updated.db` |
| Ta | `Ta-potential/current.db` | `Ta-potential/01-nvt-round-1/Ta_D1_selected_labeled.db` | `Ta-potential/01-nvt-round-1/updated.db` |
| Ti | `Ti-potential/current.db` | `Ti-potential/01-nvt-round-1/Ti_D1_selected_labeled.db` | `Ti-potential/01-nvt-round-1/updated.db` |

Each merge used the reviewed, non-overwriting command form:

```bash
module load jse
python3 src/vasp_batch_dft.py merge <current.db> <D1_labels.db> <updated.db>
```

The merge order was D0 base rows followed by D1 label rows. No element path
was shared with another element.

## Checksums

| Element | D0 snapshot SHA-256 | D1 labels SHA-256 | D1 updated/current SHA-256 |
|---|---|---|---|
| W | `e2b429335744c6e53a4691c03c51948b5192787696b67c41e4e6fac937309be3` | `60ff0c0e975a929e522640030b9a7608bac4863bfc7cf5f431099110f1032da4` | `bc09246d602a927a6905fb33c386a7030705ff70bab1fb7a39e63e0bb7eec10b` |
| Ta | `fdd9005db9f754d6cd4f31c8c04429aa57e7d46d3fef8cb4eb48348031aa0072` | `ac3e04341c1199c70f05931473a9993c5c9ac004e60e375cf8aa34d9416e789e` | `8f72a927d657e7cfd6ffb743955acf1e3fa54e3261c783ffd611dd714edefec2` |
| Ti | `1fe2a5771706e8e6a673bd3a9e5908d465500f9679f5a5aea777f3f4099c739c` | `673d6dfc3bde46feae8811345f5abaa567af019bb66b10af1c6d22a3c52f471d` | `d59371001b625955b963f7d496ca7c5ea40de493e8ab8f7eb6d721ac7030ca68` |

The preserved D0 snapshot is `<X>-potential/00-input/<X>_D0_labeled.db`.
After validation, each byte-identical `updated.db` was copied to its own
`<X>-potential/current.db`; all three published databases have 200 rows.

## Successor Validation

For every element, the successor has exactly 200 rows:

```text
rows 1--100: exact D0 base-row content and order
rows 101--200: exact validated D1-label content and order
```

ASE validation confirmed every row is 16-atom unary W, Ta, or Ti as
appropriate; 3D periodic; has finite positions, cell, energy, forces, and
stress; and has positive finite volume. Provenance fields contain no `eos`
reference. Every successor contains 200 unique geometry fingerprints and 200
unique stored structure hashes. The base and label DB SHA-256 values remained
unchanged through the merge.

## M1 Pre-Submission Review

`bash -n scripts/slurm/run_train_committee.slurm` passed. The three intended
train directories were absent:

```text
<X>-potential/model_versions/M1_from_D1/train-committee/
```

The template will create the train directory and internal `slurm_logs` only
after it has verified that the train directory is not nonempty. Therefore,
the primary Slurm output uses the template default
`slurm-M1-<X>-<jobid>.out` in the repository root; the runner also writes
`train-committee/slurm_logs/train-<jobid>.out` and the exact command after
the protected-directory check.

The exact W, Ta, and Ti submissions passed `sbatch --test-only` as jobs
13091, 13092, and 13093, respectively. Each requests one node, five tasks,
eight CPUs per task, 48 hours, a ten-member committee, five training workers,
and 1,000 epochs.

## M1 Submission

The actual independent M1 committee submissions are:

| Element | SLURM job | Input DB | Train output |
|---|---:|---|---|
| W | 13094 | `W-potential/current.db` (200 rows) | `W-potential/model_versions/M1_from_D1/train-committee/` |
| Ta | 13095 | `Ta-potential/current.db` (200 rows) | `Ta-potential/model_versions/M1_from_D1/train-committee/` |
| Ti | 13096 | `Ti-potential/current.db` (200 rows) | `Ti-potential/model_versions/M1_from_D1/train-committee/` |

All jobs started successfully with initial `RUNNING` state and `0:0` exit
status in Slurm accounting. Each runner recorded the approved input path,
ten-member committee, five workers, 1,000 epochs, and 8 cores per worker
before starting NNAP training. Completion validation remains required.
