# Notes: D2 Database Merge

## Sources

### Source 1: Validated D2 labels
- Path: `memory/14_D2_DFT_labeling/`
- Key points:
  - Every element has a matching validated 100-row D2 Protocol-A label DB.
  - The label DBs remain separate from 200-row D1 `current.db`.

### Source 2: Workflow policy and implementation map
- Path: `research-plan.md` Section 11; `docs/source_function_index.md`
- Key points:
  - A merge appends the element-local labels to the corresponding base DB.
  - Publish `updated.db` as `current.db` only after finite-data and row-order
    validation.

## Merge Preflight

All three base/label/output paths are distinct. Each 200-row D1 base and
100-row D2 label DB has no `eos` provenance in its `tag` or `source` metadata.
The protected `updated.db` paths were absent:

| Element | Base SHA-256 | Label SHA-256 |
|---|---|---|
| W | `04c1fff04786abf0eca8f2c29385dbe9d3227a415e605add852beecaddd03fab` | `8bfb67a846699f416dcdeadbf83feeca858836f6ef7ba97cfb81126b0773f1ee` |
| Ta | `4527c1609276bd68b0b1f524f805e1aa118ae981f5a2a530d35511facdaaf5c4` | `1ebc8e915c5a1d73aececb9e70df7b64b2436e9265ddb52e94d4e2e1a8799f05` |
| Ti | `71e0e046b9dafdaddc2c8abd4537ea3e99c1d503d8949e580daef0ffe2088531` | `92a326dda359d194735d387a04945f6be0d5d6e359bc934b5273d73da57d84bd` |

The merge is a lightweight direct JSE/ASE database operation. It uses no
`--overwrite` option, does not alter `current.db`, and writes only the
element-local output below:

```bash
module load jse
python3 src/vasp_batch_dft.py merge W-potential/current.db W-potential/02-nvt-round-2/W_D2_selected_labeled.db W-potential/02-nvt-round-2/updated.db
python3 src/vasp_batch_dft.py merge Ta-potential/current.db Ta-potential/02-nvt-round-2/Ta_D2_selected_labeled.db Ta-potential/02-nvt-round-2/updated.db
python3 src/vasp_batch_dft.py merge Ti-potential/current.db Ti-potential/02-nvt-round-2/Ti_D2_selected_labeled.db Ti-potential/02-nvt-round-2/updated.db
```

Only after validation proves 300 rows, preserved base-row order, appended D2
labels, finite unary data, and no EOS provenance will the validated
`updated.db` be copied to its matching `current.db`.

## Merge Validation and Publication

The three direct no-overwrite merges each reported `current=200`, `labeled=100`,
and `total=300`. Validation confirmed:

- `updated.db` IDs are consecutive 1--300;
- rows 1--200 reproduce their respective D1 base data and order exactly;
- rows 201--300 reproduce only the matching D2 label data and order exactly;
- every row is unary with the expected element, 16 atoms, 3D PBC, finite
  position/cell/energy/forces/stress, and positive volume;
- no `eos` provenance is present.

| Element | Updated SHA-256 | Published `current.db` rows |
|---|---|---:|
| W | `b2a6ed5a86848a6fc83e3c13ceb4bc08ab2e60f0e7d753e2cb8555068c2c6476` | 300 |
| Ta | `b4e7e34325bfc9506147c58bf4b9ebeb69a7491c2cb7510961cd457695c1a866` | 300 |
| Ti | `36eb18737c291e1dd26b11ca995f3255c0ae8da881e821ce66b08a0047e177cb` | 300 |

After verifying that each original 200-row `current.db` still matched the
preflight hash, publication copied its validated `updated.db` through a
same-directory temporary file and atomically replaced only its matching
`current.db`. Post-publication SHA-256 and 300-row checks matched the
validated successors.
