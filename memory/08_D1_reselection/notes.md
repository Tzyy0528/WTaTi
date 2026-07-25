# Notes: D1 Reselection from M0 Log Error

## Sources

### Source 1: D1 NVT preparation record
- Path: `memory/07_D1_NVT_preparation/`
- Key points:
  - D1 MD and all-frame scoring completed independently for W, Ta, and Ti.
  - The old P95-derived projected-CUR selections are revoked.

### Source 2: Workflow policy
- Path: `research-plan.md`, `docs/unary_workflow.md`
- Key points:
  - `U_min` must derive from the sampling committee's final test force error.
  - The aggregation of the ten model errors remains an explicit user choice.

## Commands and Observations

```bash
# Pre-cleanup DB state: D0 / current row counts
W 100 / 200
Ta 100 / 200
Ti 100 / 200
```

- Cleanup removed the old D1 CUR and labeling outputs, M1, E1_M1, D2, and
  obsolete memory records 08--15.
- Each `<X>-potential/current.db` was copied from
  `<X>-potential/00-input/<X>_D0_labeled.db`.
- Standard SQLite checks confirmed 100 rows in both source and target for
  every element; SHA-256 hashes matched exactly.
- Retained inputs:
  - `<X>-potential/01-nvt-round-1/md/`
  - `<X>-potential/01-nvt-round-1/uncertainty_all_frames.csv`
  - `<X>-potential/model_versions/M0_from_D0/train-committee/train-<i>/log`

## Approved U_min Rule

The user specified the arithmetic mean of the model-level final test
`MAE-F` values. Operationally, for each element:

```text
U_min = mean_i(final test MAE-F of M0 train-i, i = 0..9) / 1000
```

Each individual logged test `MAE-F` is already a mean absolute force error
over that model's test set. The second arithmetic mean produces the one
committee-wide threshold required for D1 selection. Units change from meV/A
to eV/A only in the final division by 1000. No selection command may use a
percentile-only cutoff.

## Derived Calibration Records

| Element | Ten-model mean test `MAE-F` (meV/A) | `U_min` (eV/A) | Production frames with `U >= U_min` |
|---|---:|---:|---:|
| W | 64.288 | 0.064288 | 22,505 / 22,505 |
| Ta | 47.964 | 0.047964 | 22,505 / 22,505 |
| Ti | 48.319 | 0.048319 | 22,505 / 22,505 |

The new element-local calibration artifacts are:

- `W-potential/01-nvt-round-1/uncertainty_calibration.json`
- `Ta-potential/01-nvt-round-1/uncertainty_calibration.json`
- `Ti-potential/01-nvt-round-1/uncertainty_calibration.json`

Each records all ten M0 log paths and final test values, the arithmetic-mean
formula, units, all-frame counts, source counts, and the approved D1 CUR
settings. The threshold retains every production frame for all three
elements; CUR will reduce each element's 22,505 candidates to the approved
100 structures.

## Prepared CUR Submission

The current template `scripts/slurm/run_absolute_u_projected_cur.slurm`
requires one node, one task, and 24 hours. It loads JSE, rejects an existing
output root, and writes the invoked command under the round's `slurm_logs/`.
For every element the protected command uses its D0-restored `current.db`,
the retained all-frame CSV, `target=100`, `r_c=6.0`, `n_max=5`, `l_max=6`,
and similarity threshold `0.99999`. It passes no source-balance, frame-gap,
tail-cap, or physical-gate options.

## CUR Submission

| Element | Job ID | `U_min` (eV/A) | Output root |
|---|---:|---:|---|
| W | 13128 | 0.064288 | `W-potential/01-nvt-round-1/absolute-u-projected-cur/` |
| Ta | 13129 | 0.047964 | `Ta-potential/01-nvt-round-1/absolute-u-projected-cur/` |
| Ti | 13130 | 0.048319 | `Ti-potential/01-nvt-round-1/absolute-u-projected-cur/` |

All three submissions use the prepared template configuration (one node, one
task, 24 hours) and explicit output/error logs at
`<round>/slurm_logs/cur-%j.{out,err}`. The output roots were absent before
submission, so the template's no-overwrite rule is active. The one immediate
`squeue` check found jobs 13128--13130 pending.
