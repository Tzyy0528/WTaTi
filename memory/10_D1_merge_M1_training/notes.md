# Notes: D1 Merge and M1 Training

## Sources

### Source 1: Validated D1 labels
- Path: `memory/09_D1_DFT_labeling/`
- Key points:
  - W, Ta, and Ti each have an independent validated 100-row D1 label DB.
  - The three D0 `current.db` files remain 100-row snapshots pending merge.

### Source 2: Merge and training workflow
- Path: `research-plan.md` section 11;
  `docs/source_function_index.md`
- Key points:
  - Base, labeled, and updated DB paths must be different.
  - Publish only a validated 200-row successor as `current.db`.
  - M1 uses ten models, five concurrent workers, and 5000 epochs.

## Planned Element-Local Merge Paths

| Element | Base DB | New D1 label DB | Successor DB |
|---|---|---|---|
| W | `W-potential/current.db` | `W-potential/01-nvt-round-1/W_D1_selected_labeled.db` | `W-potential/01-nvt-round-1/updated.db` |
| Ta | `Ta-potential/current.db` | `Ta-potential/01-nvt-round-1/Ta_D1_selected_labeled.db` | `Ta-potential/01-nvt-round-1/updated.db` |
| Ti | `Ti-potential/current.db` | `Ti-potential/01-nvt-round-1/Ti_D1_selected_labeled.db` | `Ti-potential/01-nvt-round-1/updated.db` |

## Planned M1 Roots

```text
W-potential/model_versions/M1_from_D1/train-committee/
Ta-potential/model_versions/M1_from_D1/train-committee/
Ti-potential/model_versions/M1_from_D1/train-committee/
```

The roots must be absent before protected training submission.

## Completed D1 Merge and Publication

`src/vasp_batch_dft.py merge` created each `updated.db` without overwrite:

| Element | D0 base rows | D1 label rows | `updated.db` rows | Published `current.db` rows |
|---|---:|---:|---:|---:|
| W | 100 | 100 | 200 | 200 |
| Ta | 100 | 100 | 200 | 200 |
| Ti | 100 | 100 | 200 | 200 |

JSE/ASE validation verified that rows 1--100 in every successor reproduce the
respective D0 source configurations and labels, rows 101--200 reproduce only
that element's D1 label DB, and all 200 rows are finite unary 16-atom
structures with finite energy, forces, and stress. Only after that validation
was `updated.db` copied to the corresponding `current.db`; the byte hashes
now match exactly.

## M1 Energy Audit and Submission

The M0-accepted reference energies in `src/dbselectandtrain.py` are unchanged
and match the element-local single-species D1 databases:

```text
W  ENERGY[W]  = -12.9581 eV
Ta ENERGY[Ta] = -11.8578 eV
Ti ENERGY[Ti] =  -7.8951 eV
```

| Element | Job ID | Input | Committee output |
|---|---:|---|---|
| W | 13138 | `W-potential/current.db` | `W-potential/model_versions/M1_from_D1/train-committee/` |
| Ta | 13139 | `Ta-potential/current.db` | `Ta-potential/model_versions/M1_from_D1/train-committee/` |
| Ti | 13140 | `Ti-potential/current.db` | `Ti-potential/model_versions/M1_from_D1/train-committee/` |

Each protected submission explicitly requests 10 models, 5 parallel workers,
and 5000 epochs. The template allocates one node, 5 tasks, 8 CPUs per task,
and 48 hours. M1 roots were absent, and no overwrite setting was used. The
one immediate `squeue` check found jobs 13138--13140 pending.

## Completed M1 Validation

| Element | Job ID | State / exit | Committee validation |
|---|---:|---|---|
| W | 13138 | `COMPLETED / 0:0` | 10 JNN files; finite diagnostics; 10 disjoint 180/20 folds covering 200 rows |
| Ta | 13139 | `COMPLETED / 0:0` | 10 JNN files; finite diagnostics; 10 disjoint 180/20 folds covering 200 rows |
| Ti | 13140 | `COMPLETED / 0:0` | 10 JNN files; finite diagnostics; 10 disjoint 180/20 folds covering 200 rows |

Every fold's train and test structures are disjoint, their union reproduces
the input 200-row `current.db`, and the union of the ten test folds covers
each D1 row exactly once. `Trainer.groovy` records `train.nepochs = 5000` for
all 30 M1 folds. The next stage is E1 evaluation against the unchanged,
validation-only Protocol-B EOS references.
