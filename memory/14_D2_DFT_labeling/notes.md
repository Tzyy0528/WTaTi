# Notes: D2 Protocol-A VASP Labeling

## Sources

### Source 1: Validated D2 selection
- Path: `memory/13_D2_scoring_selection/`
- Key points:
  - W, Ta, and Ti each have 100 unique finite unary 16-atom selected POSCARs.
  - CUR outputs are isolated under the corresponding
    `02-nvt-round-2/absolute-u-projected-cur/` root.

### Source 2: Frozen D1 Protocol-A label stage
- Path: `memory/09_D1_DFT_labeling/`
- Key points:
  - Use static `MAGMOM=_`, `KSPACING=0.2`, automatic
    `ENCUT=1.3*max(ENMAX)`, `NCORE=2`, no explicit SOC or spin override,
    `vasp_std`, 8 cores per task, and 8 concurrent tasks.
  - W/Ta/Ti POTCAR SHA-256 identities are recorded before every submission.

### Source 3: Active label implementation
- Path: `research-plan.md` Section 5; `docs/source_function_index.md`
- Key points:
  - New labels use `src/vasp_batch_dft.py` only through
    `scripts/slurm/run_vasp_batch_dft.slurm`.
  - New label DBs remain separate from `current.db` until a later validated
    merge.

## Frozen Protocol-A and D2 Preflight

The current source and the preserved D1 runner commands confirm the unchanged
static Protocol-A configuration:

```text
MAGMOM = _ (omit MAGMOM)
KSPACING = 0.2
ENCUT = 1.3 * max(selected POTCAR ENMAX)
NCORE = 2
VASP command = vasp_std
static settings include IBRION=-1 and NSW=0
explicit SOC and spin overrides = absent
```

Immediately before submission, each selected input directory has exactly 100
nonempty POSCARs, its corresponding `current.db` has 200 rows, and its
protected output DB and work root are absent:

```text
W:  input=W-potential/02-nvt-round-2/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p17022_cur100/
    db=W-potential/02-nvt-round-2/W_D2_selected_labeled.db
    work=W-potential/02-nvt-round-2/dft/vasp_W_D2_selected/
Ta: input=Ta-potential/02-nvt-round-2/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p14444_cur100/
    db=Ta-potential/02-nvt-round-2/Ta_D2_selected_labeled.db
    work=Ta-potential/02-nvt-round-2/dft/vasp_Ta_D2_selected/
Ti: input=Ti-potential/02-nvt-round-2/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p113619_cur100/
    db=Ti-potential/02-nvt-round-2/Ti_D2_selected_labeled.db
    work=Ti-potential/02-nvt-round-2/dft/vasp_Ti_D2_selected/
```

The element-local POTCAR SHA-256 checksums match the frozen D1 Protocol-A
identities:

```text
W  c0897285f1b301314dcc12eb838ce8a777aa860795754598b0626cb818170117
Ta b94d0231aa338d2b49887428178c5ebac7fa385cbd6154890af94e8013d269f3
Ti f8e8f1d080d9e9b45e792f1068744b07aba8441d1e7ce11486a5d4c0f5a1479e
```

Each allocation uses one node and 64 tasks to run eight concurrent eight-rank
VASP tasks. The current template has partition-default walltime. No
`OVERWRITE` or `FORCE_PREPARE` option is set; the runner rejects an existing
output DB.

Exact protected submission commands:

```bash
WORK_DIR=W-potential/02-nvt-round-2/dft/vasp_W_D2_selected CORES_PER_JOB=8 MAX_WORKERS=8 NCORE=2 VASP_COMMAND=vasp_std ENCUT_FACTOR=1.3 PROGRESS_INTERVAL=60 sbatch --nodes=1 --ntasks=64 --output W-potential/02-nvt-round-2/slurm_logs/vasp-submit-%j.out --error W-potential/02-nvt-round-2/slurm_logs/vasp-submit-%j.err scripts/slurm/run_vasp_batch_dft.slurm W-potential/02-nvt-round-2/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p17022_cur100 W-potential/02-nvt-round-2/W_D2_selected_labeled.db _ 0.2

WORK_DIR=Ta-potential/02-nvt-round-2/dft/vasp_Ta_D2_selected CORES_PER_JOB=8 MAX_WORKERS=8 NCORE=2 VASP_COMMAND=vasp_std ENCUT_FACTOR=1.3 PROGRESS_INTERVAL=60 sbatch --nodes=1 --ntasks=64 --output Ta-potential/02-nvt-round-2/slurm_logs/vasp-submit-%j.out --error Ta-potential/02-nvt-round-2/slurm_logs/vasp-submit-%j.err scripts/slurm/run_vasp_batch_dft.slurm Ta-potential/02-nvt-round-2/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p14444_cur100 Ta-potential/02-nvt-round-2/Ta_D2_selected_labeled.db _ 0.2

WORK_DIR=Ti-potential/02-nvt-round-2/dft/vasp_Ti_D2_selected CORES_PER_JOB=8 MAX_WORKERS=8 NCORE=2 VASP_COMMAND=vasp_std ENCUT_FACTOR=1.3 PROGRESS_INTERVAL=60 sbatch --nodes=1 --ntasks=64 --output Ti-potential/02-nvt-round-2/slurm_logs/vasp-submit-%j.out --error Ti-potential/02-nvt-round-2/slurm_logs/vasp-submit-%j.err scripts/slurm/run_vasp_batch_dft.slurm Ti-potential/02-nvt-round-2/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p113619_cur100 Ti-potential/02-nvt-round-2/Ti_D2_selected_labeled.db _ 0.2
```

## Submission and Immediate Status

- W D2 Protocol-A label batch: SLURM job `13154`
- Ta D2 Protocol-A label batch: SLURM job `13155`
- Ti D2 Protocol-A label batch: SLURM job `13156`

The one immediate `squeue` check found all three jobs `RUNNING`; W and Ta
were on `lpsnode03`, and Ti was on `lpsnode01`. The partition reports a
365-day allocation limit because the template intentionally has no explicit
walltime. No automatic monitoring was started.

## Completion and Label-DB Validation

One focused `sacct` check found all allocations and all 100 eight-rank
`vasp_std` tasks per element `COMPLETED` with exit code `0:0`:

- W job `13154`: 1:01:42 elapsed
- Ta job `13155`: 55:09 elapsed
- Ti job `13156`: 36:43 elapsed

Each runner log reports 100 successful VASP tasks, 0 failures, 0 skipped
tasks, and a 100-row collected DB. Each work root contains 100 `OUTCAR` files
with the normal VASP completion marker. ASE/JSE validation then confirmed
every row has unary expected composition, 16 atoms, 3D PBC, finite positions,
cell, energy, `(16,3)` forces, and six-component stress, with positive volume.

| Element | Label DB rows | Energy range (eV/16-atom cell) | Minimum volume (A^3) | SHA-256 |
|---|---:|---|---:|---|
| W | 100 | -199.992242600 to -154.238963390 | 185.833921891 | `8bfb67a846699f416dcdeadbf83feeca858836f6ef7ba97cfb81126b0773f1ee` |
| Ta | 100 | -183.426547340 to -152.170106240 | 211.468001513 | `1ebc8e915c5a1d73aececb9e70df7b64b2436e9265ddb52e94d4e2e1a8799f05` |
| Ti | 100 | -119.620089650 to -103.786575520 | 202.012872621 | `92a326dda359d194735d387a04945f6be0d5d6e359bc934b5273d73da57d84bd` |

All new label DBs remain separate from `current.db`. The next unstarted
operation is a protected element-local merge from 200-row D1 `current.db`
plus its 100-row D2 label DB into a 300-row `updated.db`, followed by
validation before publication.
