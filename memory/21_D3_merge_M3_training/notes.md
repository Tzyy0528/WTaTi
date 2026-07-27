# Notes: D3 Merge and M3 Committee Training

## Sources

### Source 1: Validated D3 labels
- Path: `memory/20_D3_DFT_labeling/`
- Key points:
  - Every element has an independent validated 100-row D3 Protocol-A label DB.
  - The existing corresponding `current.db` remains the unchanged 300-row D2
    base, and protected `updated.db` paths are absent.

## Commands and Observations

- User explicitly authorized D3 merge and subsequent M3 training.

## D3 Merge and Publication

### Protected merge preflight (passed)

Immediately before no-overwrite merge, each element had a distinct 300-row
base, matching 100-row D3 label DB, absent `updated.db`, and absent M3 root.
All 1,200 checked base/label rows were finite, unary expected-element,
16-atom, 3D-periodic, and free of EOS provenance.

| Element | Base SHA-256 | Label SHA-256 |
|---|---|---|
| W | `b2a6ed5a86848a6fc83e3c13ceb4bc08ab2e60f0e7d753e2cb8555068c2c6476` | `32da8595645a38fae7d8ab29db03e0cba1fd7060b37a3f0c83246741f85742b9` |
| Ta | `b4e7e34325bfc9506147c58bf4b9ebeb69a7491c2cb7510961cd457695c1a866` | `ea7d9a8500678ae492ed7c8e18e6bd3e32c86cbbcd5885f97daaa9255bf061de` |
| Ti | `36eb18737c291e1dd26b11ca995f3255c0ae8da881e821ce66b08a0047e177cb` | `3276f7d5c3ea0779af71624d05fcad17f442bcf10fc7e90408a9fba70b5b78f2` |

`src/vasp_batch_dft.py merge` then wrote only:

```bash
module load jse
python3 src/vasp_batch_dft.py merge <X>-potential/current.db \
  <X>-potential/03-npt-round-1/<X>_D3_selected_labeled.db \
  <X>-potential/03-npt-round-1/updated.db
```

### Merge validation and atomic publication (passed)

Every `updated.db` has consecutive IDs `1..400`; rows `1..300` exactly
reproduce the matching base structure, calculator results, key-value
metadata, and order; rows `301..400` exactly reproduce only the matching D3
label DB in order. All 1,200 output rows again passed finite unary/no-EOS
validation.

| Element | Validated/published SHA-256 | Published rows |
|---|---|---:|
| W | `de91dcc3b96f7a893e70bed94f4e79a199ed7c7e2c042b3066f331cf33efe208` | 400 |
| Ta | `e2963500627abaccb3d335f044f32d40de3b6dff227728aa140179656fac51d6` | 400 |
| Ti | `4fa6e59d7d04b7e78720aa30372bb35c9498020c73884b76e61eac9b48cac7d1` | 400 |

After rechecking every old 300-row SHA, each matching `updated.db` was copied
to a same-directory temporary file and atomically replaced only that
element's `current.db`. A transcription error in the first Ti SHA comparison
stopped the loop before changing Ti; Ti's original hash was confirmed, then
the corrected standalone atomic publication completed. No W/Ta/Ti data were
mixed or overwritten outside their authorized `current.db`.

### M3 preflight (passed)

The published `current.db` hashes match the table above, each has 400 finite
unary 16-atom no-EOS rows, and each protected committee root is absent:

```text
W-potential/model_versions/M3_from_D3/train-committee/
Ta-potential/model_versions/M3_from_D3/train-committee/
Ti-potential/model_versions/M3_from_D3/train-committee/
```

The current `src/dbselectandtrain.py::ENERGY` reference values remain W
`-12.9581`, Ta `-11.8578`, and Ti `-7.8951` eV, matching the frozen
Protocol-A/M2 values. Approved M3 configuration is ten models, five
concurrent workers, eight threads per worker, and 5,000 epochs.

### M3 submission (2026-07-25)

Immediately before every submission, its matching published 400-row
`current.db` was present and its `M3_from_D3/train-committee` root was absent.
No `OVERWRITE` setting was used.

| Element | Job ID | Input DB | Committee root |
|---|---:|---|---|
| W | 13221 | `W-potential/current.db` | `W-potential/model_versions/M3_from_D3/train-committee/` |
| Ta | 13222 | `Ta-potential/current.db` | `Ta-potential/model_versions/M3_from_D3/train-committee/` |
| Ti | 13223 | `Ti-potential/current.db` | `Ti-potential/model_versions/M3_from_D3/train-committee/` |

Each job requests one node, five tasks, eight CPUs/task, and 48 hours, and
passes `10 5 5000` explicitly to the current training template. Per the
user's previous request, no immediate queue check or active monitoring was
started. E3 remains unstarted.

### M3 completion and validation (passed)

The later E3-authorized validation found W `13221`, Ta `13222`, and Ti
`13223` `COMPLETED` with exit `0:0`. Every committee contains ten nonempty
5,000-epoch JNN/log pairs. Each matching 400-row `current.db` is reconstructed
by ten disjoint 360/40 train/test folds, and every DB row occurs in exactly one
test fold. All final MAE-E/MAE-F diagnostics are finite. E3 was subsequently
authorized and recorded separately under `memory/22_M3_E3_eos_validation/`.

## Synthesized Findings

### Scope
- Merge only with `src/vasp_batch_dft.py merge`, then validate before
  publishing `current.db`.
- Train only through `scripts/slurm/run_train_committee.slurm` after each
  matching D3 successor is published.
- Do not start E3 evaluation in this task.
