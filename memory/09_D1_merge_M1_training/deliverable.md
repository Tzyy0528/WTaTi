# Deliverable: D1 Merge and M1 Committee Training

## Published D1 Databases

The validated successors have been published independently:

| Element | D1 `current.db` rows | SHA-256 |
|---|---:|---|
| W | 200 | `bc09246d602a927a6905fb33c386a7030705ff70bab1fb7a39e63e0bb7eec10b` |
| Ta | 200 | `8f72a927d657e7cfd6ffb743955acf1e3fa54e3261c783ffd611dd714edefec2` |
| Ti | 200 | `d59371001b625955b963f7d496ca7c5ea40de493e8ab8f7eb6d721ac7030ca68` |

Each comprises its unchanged 100-row D0 base followed by its own unchanged
100-row validated D1 labels. The element-local `updated.db` and D0 snapshot
are preserved.

## M1 Training Status

The M1 training configuration and scheduler allocation have passed
pre-submission validation. Independent M1 training has been submitted:

| Element | SLURM job | Initial state |
|---|---:|---|
| W | 13094 | RUNNING |
| Ta | 13095 | RUNNING |
| Ti | 13096 | RUNNING |

Final M1 artifact and fold validation remains pending. E1 EOS evaluation is
intentionally not started.
