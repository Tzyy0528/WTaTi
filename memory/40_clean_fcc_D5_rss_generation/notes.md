# Notes: Clean-FCC D5 RSS Structure Generation

## Sources

### Source 1: Frozen D5 generator card
- Path/URL: `memory/39_clean_fcc_D5_rss_configuration/`.
- Key points:
  - Per-element atomic volume, M4 `train-5` relaxer, atom counts, Mini
    pressure/controls, retention, and no-overwrite policy are fixed.

### Source 2: RSS driver
- Path/URL: `src/rss_sampling_embedded.py`.
- Key points:
  - Requires explicit unary element, one JNN, output root, atomic volume,
    and optional RSS/Mini controls.
  - `--keep-raw --keep-minimized-work` preserves auditable work; the driver
    does not require or support an all-committee relaxation invocation.

### Source 3: SLURM convention
- Path/URL: `scripts/slurm/README.md`,
  `scripts/slurm/run_uncertainty_scoring.slurm`, and
  `scripts/slurm/run_rss_round.slurm`.
- Key points:
  - The new RSS wrapper uses one node, one task, and 24 hours, rejects login
    node execution and an existing `rss/` root, records the exact command,
    and never exposes `--overwrite`.
  - It invokes only `src/rss_sampling_embedded.py` through `srun`; no
    scoring, selection, DFT, database, training, or EOS command is present.

## Commands and Observations

```bash
# Wrapper syntax/help verification (no output generated).
bash -n scripts/slurm/run_rss_round.slurm
bash scripts/slurm/run_rss_round.slurm --help
python3 src/rss_sampling_embedded.py --help

# Read-only protected-input preflight (no output generated).
module load jse
python3 - <<'PY'
# Verify W/Ta/Ti D4 hashes/500-row unary state, M4 train-5 JNNs and MAE-F,
# absent <X>-potential/fcc-restart/05-rss-round-1 roots, and SLURM/JSE.
PY
```

## Synthesized Findings

### Wrapper and preflight acceptance

`scripts/slurm/run_rss_round.slurm` passed Bash syntax/help checks and uses
the frozen one-node, one-task, 24-hour resource setting. Documentation now
indexes the wrapper in `docs/source_function_index.md`,
`scripts/slurm/README.md`, and `docs/unary_workflow.md`.

The read-only preflight accepted exactly the matching D4/M4 inputs and
confirmed every D5 stage root is absent:

| Element | D4 500-row SHA-256 | M4 `train-5/5.jnn` SHA-256 | Test MAE-F (meV/A) | Atomic volume (A3/atom) |
|---|---|---|---:|---:|
| W | `1242b2f534f1bebc2730102b0e1c5d8b524c0adaee2a75259d687deecfa57480` | `99218ceaa7412486a04c4abb3f0908813d7379e13c1fa8ddc3e3e29e1478ae54` | 197.5 | 15.903934900 |
| Ta | `600bd1c0c7d205771fe7b9859731e9af05399498e4c9ae6757c9de3bb9616989` | `10bc1096d1b03a70fb190bdab4351f0782561483ecba7e3f6c9d6091001094f9` | 155.8 | 18.151564915 |
| Ti | `8db00646830c0cbb81037130881815b344f9be4f893a47e3d4a2dde075d2322b` | `c435c676a0072fe915c1029289b4845a071a66dcababe72843a1f23189fbc2dd` | 121.1 | 17.345854575 |

Every database has 500 finite unary 32-atom 3D-PBC rows and no EOS metadata.
`sbatch` and JSE resolve after `module load jse`; no inherited `OVERWRITE`
setting is present. The exact `rss/` roots and all later D5 output paths are
absent. The only permitted pre-submission mutation is creating each matching
`05-rss-round-1/slurm_logs/` directory for scheduler stdout/stderr.

### D5 RSS/Mini generation submission

After the accepted preflight, only the three matching scheduler-log directories
were created and the protected commands were submitted. Every submission uses
one node, one task, 24 hours, an absent `rss/` output root, no overwrite flag,
and only generation options:

| Element | Job ID | Output root | Relaxation JNN |
|---|---:|---|---|
| W | `13575` | `W-potential/fcc-restart/05-rss-round-1/rss/` | `M4/train-5/5.jnn` |
| Ta | `13576` | `Ta-potential/fcc-restart/05-rss-round-1/rss/` | `M4/train-5/5.jnn` |
| Ti | `13577` | `Ti-potential/fcc-restart/05-rss-round-1/rss/` | `M4/train-5/5.jnn` |

All three commands pass `--nstructs 50`,
`--natoms-list 9,10,12,15,18,20,22,25`,
`--mini-press-list 0,200000,400000`, `tri`, 10 Mini loops, `1e-4`/`1e-8`
tolerances, `--jobs 1`, `--keep-raw`, and `--keep-minimized-work`.

One immediate `squeue` query over `13575,13576,13577` returned no active
records. Per the no-polling rule, no further scheduler or artifact-status
check has been made. Terminal status and full pool validation remain pending
a later user request. No D5 scorer, selector, DFT, merge, training, or EOS
process has been submitted.

### Failed launch diagnosis and protected retry requirement

On the user's later status request, one focused `sacct` check found all three
submitted jobs terminally failed with exit `1:0` after six seconds:

| Element | Job ID | State | Exit | Elapsed |
|---|---:|---|---|---:|
| W | `13575` | `FAILED` | `1:0` | 00:00:06 |
| Ta | `13576` | `FAILED` | `1:0` | 00:00:06 |
| Ti | `13577` | `FAILED` | `1:0` | 00:00:06 |

Their matching JSE logs identify one common wrapper defect: JSE's RSS/Mini
resource assignment rejects a `jse` child run through `srun`, then raises a
null-resource exception. The failed roots contain only
`rss/logs/unary-<X>.log`; no raw, minimized, collection, score, selection,
DFT, database, training, or EOS artifact exists.

`scripts/slurm/run_rss_round.slurm` now invokes the RSS Python driver directly
inside the `sbatch` allocation, as JSE requires, and its documentation is
updated. A retry still cannot proceed automatically: the driver correctly
refuses the existing partial `rss/` roots. Obtain explicit authorization to
delete only these three roots, retain all `slurm_logs/` including the original
failure logs, re-preflight, and submit corrected generation-only jobs.

### Authorized partial-root cleanup

The user explicitly authorized deleting only the three failed `rss/` roots.
Immediately before deletion, each root was verified to contain exactly its
single `logs/unary-<X>.log` failure log, no symlinks, no files below
`raw/unary-<X>` or `minimized/unary-<X>`, and no collected/score/selection/DFT/
database/training/EOS output. The following roots were then removed:

```text
W-potential/fcc-restart/05-rss-round-1/rss/
Ta-potential/fcc-restart/05-rss-round-1/rss/
Ti-potential/fcc-restart/05-rss-round-1/rss/
```

Only the three sibling `slurm_logs/` directories remain under their round
roots; they were not modified. The corrected direct-JSE retry requires a new
read-only input/output preflight before submission.

### Corrected retry preflight: initial stop

The read-only retry preflight loaded the JSE environment, unset `OVERWRITE`,
and began verifying the frozen D4 database and M4 `train-5` JNN SHA-256
identities. It stopped at the W input-identity assertion before submitting a
job. Read-only diagnosis found that the check mistakenly used the separate
non-FCC root-level `<X>-potential/current.db` files: they are valid 500-row
16-atom states with hashes W `d9d851b7...`, Ta `bce6490107...`, and Ti
`a68f2c8b4...`, which match their non-FCC `04-npt-round-2/updated.db`
counterparts. The frozen clean-FCC D4 state instead belongs at
`<X>-potential/fcc-restart/current.db` and has the task-39 hashes. Rerun the
preflight against those matching FCC paths; the three `rss/` roots remain
absent and no new scheduler job was created.

### Corrected FCC retry preflight: pass

The corrected read-only check used only
`<X>-potential/fcc-restart/current.db` and its matching M4 committee. For W,
Ta, and Ti it accepted the frozen D4 SHA-256 and the matching `train-5/5.jnn`
SHA-256, all ten `train-0` through `train-9` JNN paths, 500 finite unary
32-atom 3D-PBC rows with no EOS metadata, and an absent
`05-rss-round-1/rss/` output root. It also confirmed `OVERWRITE` was unset,
the wrapper passed `bash -n`, and both `sbatch` and JSE resolve after
`module load jse`.

The retry is therefore authorized to submit only the frozen generation card:
one node, one task, 24 hours; `--nstructs 50`;
`--natoms-list 9,10,12,15,18,20,22,25`; Mini pressures
`0,200000,400000` bar; `tri`, 10 loops, `etol=1e-4`, `ftol=1e-8`;
`--jobs 1`; retained raw/minimized work; and no `--overwrite`.

### Corrected direct-JSE retry submission

The protected corrected-generation commands were submitted with wrapper
resources of one node, one task, and 24 hours. They use only their matching
FCC M4 `train-5/5.jnn`, write only to their matching
`fcc-restart/05-rss-round-1/rss/` root, and set SLURM stdout/stderr to the
sibling `slurm_logs/rss-%j.{out,err}` paths:

| Element | Job ID | Atomic volume (A3/atom) |
|---|---:|---:|
| W | `13579` | 15.903934900 |
| Ta | `13580` | 18.151564915 |
| Ti | `13581` | 17.345854575 |

Each command supplies the frozen 50-structure, eight atom-count, three-Mini-
pressure, `tri`/10-loop/`1e-4`/`1e-8`, sequential-worker, retained-work
card. It supplies no `--overwrite` option.

One immediate `squeue` query found all three jobs `RUNNING` on `lpsnode02` at
elapsed time `0:15`. Per the no-polling rule, no further scheduler or
artifact check will be made unless the user asks for status. An unintended
temporary `/tmp/d5_rss_retry_jobids.<pid>` submission record was verified to
contain only these three job IDs and removed immediately.

### Authorized Ta provenance remediation and regeneration

The user confirmed that W/Ti RSS generation pools are normal and explicitly
authorized only Ta's invalid RSS-pool cleanup and rerun. Before deletion,
`Ta-potential/fcc-restart/05-rss-round-1/rss/` was checked as a real
non-symlink directory contained by its round root; it contained 2,804 files
and no symlinks. The sibling `slurm_logs/` directory contained six files with
aggregate sorted-content checksum
`b87c5c773b8289f145fc7490ed78851e70764083cc688cc85b6206a54832ca85`.

Only the Ta `rss/` root was deleted. The same log-tree checksum was verified
afterward, so no scheduler-log file was modified or removed. No W, Ti, D4
database, M4 committee, selection output, DFT, merge, training, or EOS asset
was touched.

The repeated read-only Ta preflight loaded JSE and accepted the frozen
FCC-D4 checksum
`600bd1c0c7d205771fe7b9859731e9af05399498e4c9ae6757c9de3bb9616989`,
the matching M4 `train-5/5.jnn` checksum
`10bc1096d1b03a70fb190bdab4351f0782561483ecba7e3f6c9d6091001094f9`,
500 finite unary 32-atom 3D-PBC D4 rows, an absent Ta RSS root, unset
`OVERWRITE`, and the one-node/one-task/24-hour direct-JSE wrapper.

Submitted the unchanged frozen Ta RSS/Mini card:

```bash
sbatch \
  --output Ta-potential/fcc-restart/05-rss-round-1/slurm_logs/rss-%j.out \
  --error Ta-potential/fcc-restart/05-rss-round-1/slurm_logs/rss-%j.err \
  scripts/slurm/run_rss_round.slurm \
  --element Ta \
  --jnn Ta-potential/fcc-restart/model_versions/M4_from_D4/train-committee/train-5/5.jnn \
  --out-dir Ta-potential/fcc-restart/05-rss-round-1/rss \
  --atomic-volume 18.151564915 \
  --nstructs 50 --natoms-list 9,10,12,15,18,20,22,25 \
  --mini-press-list 0,200000,400000 --mini-keyword tri --mini-loop 10 \
  --mini-etol 1e-4 --mini-ftol 1e-8
# Submitted batch job 13586
```

The one immediate `squeue` check found `13586` pending (`PD`) at `0:00`.
Do not poll unless the user asks. Ta remains selection-blocked until this job
is terminally successful and its full raw/minimized/flat provenance is
validated.

### Ta retry terminal status and causal validation

On the user's subsequent cause/status question, one focused accounting query
reported Ta `13586` `COMPLETED`, exit `0:0`, elapsed `00:25:15`. Read-only
provenance validation then stopped at
`Ta-00191-1.poscar`: the raw source has 15 atoms while the minimized output
has 22. A complete count audit found 400 valid raw structures and 1,200
minimized files, but 52 filename-matched raw/minimized atom-count mismatches:
13 at 0 bar, 17 at 200,000 bar, and 22 at 400,000 bar. The minimized
atom-count distribution is `{9:157, 10:156, 12:158, 15:155, 18:142,
20:144, 22:150, 25:138}`, not the required 150 per size.

The retained `rss/logs/unary-Ta.log` gives the direct runtime failure:
LAMMPS/JSE Mini reports `ERROR on proc 0: Neighbor list overflow, boost
neigh_modify one` (`npair_bin.cpp:248`) while continuing its 1,200-item
progress loop. Its final `LMP FAIL LIST` contains 60 failed
`(raw structure, pressure)` jobs. Correlation against the audited files is
exact: all 52 atom-count/provenance mismatches belong to this failure list;
eight additional Mini failures happen to retain a matching atom count.

This is not evidence that the Ta M4 potential is quantitatively inaccurate:
an energy/force model cannot itself change an atom count. The demonstrated
mechanism is Mini/LAMMPS numerical failure on pathological RSS structures,
followed by invalid output association/fallback handling despite scheduler
success. The model or Mini pressure path could contribute to a collapse that
triggers the overflow, but that has not been isolated. Do not claim a
potential-quality failure without a controlled diagnostic. The current Ta
RSS root was not altered after this diagnosis.

### Approved Ta partial-pool handoff

The user explicitly accepted a reduced Ta candidate pool while retaining the
unchanged D5 target of 100 selected structures. The implementation treats this
as a strict exception, not a generic ignore-errors mode: it parses the final
`LMP FAIL LIST` from `rss/logs/unary-Ta.log`, excludes exactly its 60
`exit=1` raw-index/pressure pairs, and still requires all 1,140 nonfailed
sources to pass unary finite-geometry, atom-count, Mini-pressure, manifest,
and flat/minimized byte-identity checks. The read-only preflight accepted
that accounting exactly; no logged failure will be scored or selected.

Selection-specific implementation and submission are recorded in
`memory/41_clean_fcc_D5_rss_selection/`. No generation artifact was deleted
or modified for this policy change.
