# Notes: D4 Merge and M4 Committee Training

## Sources

### Source 1: D4 label validation
- Path: `memory/25_D4_DFT_labeling/`
- Key points:
  - W, Ta, and Ti each have a validated, isolated 100-row D4 label DB.
  - Each matching `current.db` remains a 400-row D3 database.

## Commands and Observations

### Merge and publication preflight (passed)

The current executable paths were inspected after the source-function index:
`src/vasp_batch_dft.py merge` rejects an existing output DB unless
`--overwrite` is passed, and `scripts/slurm/run_train_committee.slurm` rejects
a nonempty training root unless `OVERWRITE=1` is passed. Neither override is
used.

Each matching input was present and independently validated before merge:

| Element | D3 base rows / SHA-256 | D4 label rows / SHA-256 |
|---|---|---|
| W | 400 / `de91dcc3b96f7a893e70bed94f4e79a199ed7c7e2c042b3066f331cf33efe208` | 100 / `c32006c90312bc82e3e210613347d789bf173bcf267d774ecacff27069f552c1` |
| Ta | 400 / `e2963500627abaccb3d335f044f32d40de3b6dff227728aa140179656fac51d6` | 100 / `d601c6c22a5eaa7349afb60cad1b4d7832a6cd4f596a1e5f9a3d4141fc7ec663` |
| Ti | 400 / `4fa6e59d7d04b7e78720aa30372bb35c9498020c73884b76e61eac9b48cac7d1` | 100 / `b3152128e7d8fcd950e78fa143982a46b65fecc31191b4b519a4c1c57f23c78e` |

All 1,500 input rows are finite, expected-element unary 16-atom,
three-dimensionally periodic structures with positive volume, finite
energy/forces/stress, no EOS metadata, and no base/D4 structural-hash
overlap. The three D4 `updated.db` paths and M4 committee roots were absent.
The current training references remain W `-12.9581`, Ta `-11.8578`, and Ti
`-7.8951` eV, matching the frozen M3 `Trainer.groovy` files.

### D4 merge validation and publication (passed)

Executed only the supported no-overwrite merge commands:

```bash
module load jse
python3 src/vasp_batch_dft.py merge <X>-potential/current.db \
  <X>-potential/04-npt-round-2/<X>_D4_selected_labeled.db \
  <X>-potential/04-npt-round-2/updated.db
```

Every `updated.db` contains consecutive IDs `1..500`; rows `1..400` are the
matching D3 base in order and rows `401..500` are only the matching D4 labels
in order. Structure, energy, free energy, force, stress, calculator name, and
key-value/data metadata are exact copies. All output rows passed finite,
unary, 16-atom, 3D-PBC, positive-volume, and no-EOS checks.

| Element | Published D4 SHA-256 | Rows |
|---|---|---:|
| W | `d9d851b7e22ef2fdb84eeaa88d7822682e83a33f9de5eb91c188f92c2d0755bc` | 500 |
| Ta | `bce6490107a31f329bd89a30d7505c5e3665357a2f254afdc3e181cdf10698a0` | 500 |
| Ti | `a68f2c8b4cd5e41788463566737fafa80e1e9b70a4c7a7006a953c57a922c6d2` | 500 |

After confirming all three original D3 and all three validated D4 checksums
before any replacement, each `updated.db` was copied to a same-directory
temporary file and atomically replaced only its matching `current.db`.

### M4 submission configuration

The authorized M4 command for each element will use only its published D4
`current.db`, its absent
`<X>-potential/model_versions/M4_from_D4/train-committee/` root, committee
size `10`, five workers, and `5,000` epochs. The SLURM template requests one
node, five tasks, eight CPUs per task, and 48 hours; no partition/account
override or overwrite setting is supplied. Scheduler stdout/stderr will use
the existing element-local D4 `slurm_logs/` directory.

### M4 submissions (2026-07-26)

Immediately before each `sbatch` command, the matching published D4
`current.db` had exactly 500 rows and its published SHA-256, its M4 committee
root was absent, and the D4 log directory existed. Submitted:

```bash
sbatch --output <X>-potential/04-npt-round-2/slurm_logs/m4-submit-%j.out \
  --error <X>-potential/04-npt-round-2/slurm_logs/m4-submit-%j.err \
  scripts/slurm/run_train_committee.slurm \
  <X>-potential/current.db \
  <X>-potential/model_versions/M4_from_D4/train-committee \
  10 5 5000
```

| Element | Job ID | Input DB | Committee root |
|---|---:|---|---|
| W | `13275` | `W-potential/current.db` | `W-potential/model_versions/M4_from_D4/train-committee/` |
| Ta | `13276` | `Ta-potential/current.db` | `Ta-potential/model_versions/M4_from_D4/train-committee/` |
| Ti | `13277` | `Ti-potential/current.db` | `Ti-potential/model_versions/M4_from_D4/train-committee/` |

No `OVERWRITE` setting or resource override was used. The template requests
one node, five tasks, eight CPUs per task, and 48 hours. One immediate
focused `squeue` check found W running on `dreamx-cpu` and Ta/Ti pending for
priority. No polling loop was started.

### M4 completion check (2026-07-27)

```bash
sacct -j 13275,13276,13277 --format=JobID,JobName%28,State,ExitCode,Elapsed -n -P
```

| Element | Job ID | State | Exit code | Elapsed |
|---|---:|---|---|---:|
| W | `13275` | `COMPLETED` | `0:0` | 00:08:30 |
| Ta | `13276` | `COMPLETED` | `0:0` | 00:08:17 |
| Ti | `13277` | `COMPLETED` | `0:0` | 00:08:56 |

The user explicitly decided not to run E4. Committee-artifact validation was
not run as part of this status check.

## Synthesized Findings

- D4 has been independently merged and published for W, Ta, and Ti. Each
  `current.db` is now a 500-row D4 successor.
- M4 scheduler jobs completed successfully but committee artifacts have not
  been independently validated. E4 is explicitly deferred.
