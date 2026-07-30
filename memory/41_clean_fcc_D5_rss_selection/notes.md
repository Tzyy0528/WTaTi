# Notes: Clean-FCC D5 RSS Selection

## Sources

### Source 1: D5 RSS configuration
- Path/URL: `memory/39_clean_fcc_D5_rss_configuration/notes.md`
- Key points:
  - D5 needs 100 labels per element after selection, but this task stops at
    selected-structure provenance.
  - The fixed `U_min`, geometry-gate, projected-CUR, and tail-cap policy is
    element-local and uses all ten M4 models for scoring.

### Source 2: D5 generation record
- Path/URL: `memory/40_clean_fcc_D5_rss_generation/`
- Key points:
  - Corrected direct-JSE jobs are W `13579`, Ta `13580`, and Ti `13581`.
  - Raw and minimized work should be retained beneath each isolated
    `fcc-restart/05-rss-round-1/rss/` root.

### Source 3: Workflow policy and source index
- Path/URL: `research-plan.md` sections 3, 9, and 10;
  `docs/source_function_index.md`
- Key points:
  - RSS selection requires every minimized structure to receive all-committee
    uncertainty scoring, calibrated absolute-U, periodic geometry gates,
    D4-projected CUR, and capped extreme-U provenance.
  - The current source index does not identify a production RSS flat-POSCAR
    all-frame scoring/geometry-audit adapter; quota-CUR is disallowed as the
    final selector.

## Commands and Observations

```bash
# Pending: one focused terminal scheduler query for 13579,13580,13581,
# followed by read-only RSS/Mini pool validation if terminally successful.
```

The focused `sacct` query confirmed all three retries completed successfully:
W `13579` in `00:25:27`, Ta `13580` in `00:26:33`, and Ti `13581` in
`00:25:21`, each with exit `0:0`. The initial pool-validator implementation
then stopped on an unescaped comma-list string assertion against the shell
command record, before performing its geometry or manifest checks. Inspect
and safely parse that command record before rerunning the read-only
validation; no output was modified.

The safely parsed rerun accepted every W artifact: 400 raw structures, 1,200
minimized and flat-collected structures, complete 8-by-50 atom-count and
3-by-50 pressure-index coverage, finite unary positive-volume 3D-PBC
geometries, command/provenance markers, and byte-identical flat copies. It
then stopped at Ta because `Ta-00051-0.poscar` did not retain the atom count
of raw `Ta-00051.poscar`. Determine whether that apparent mapping failure is
a naming/order convention or an output defect before proceeding.

Read-only index-wide comparison established a Ta pool defect. All raw files
have the required 50 structures at each of 9, 10, 12, 15, 18, 20, 22, and 25
atoms, but minimized files have counts
`{9:158, 10:152, 12:157, 15:149, 18:150, 20:147, 22:144, 25:143}`.
Fifty-three of 1,200 `<raw-index>-<pressure-index>` files differ in atom
count from their claimed raw source; for example raw `Ta-00051.poscar` has
10 atoms whereas outputs `Ta-00051-{0,1,2}.poscar` have 20, 20, and 18 atoms.
This violates required atom-count/pressure provenance, so Ta cannot safely
enter all-frame selection. The analogous direct-index check found zero
mismatches and exactly 150 minimized structures per atom count for Ti.

## Synthesized Findings

### Selection gate

Pool completion is necessary but insufficient to submit selection. The
existing MD scorer/selector interfaces rely on trajectory/frame records,
whereas D5 RSS produces a flat minimized-POSCAR collection. A compliant
adapter must bridge that representation while retaining all-frame score,
source, geometry-audit, projected-CUR, tail, and selected-POSCAR artifacts.

The existing `absolute_u_projected_cur_selection.py` can preserve the required
policy unchanged if the adapter materializes validated RSS structures as
per-`(natoms, Mini-pressure)` extxyz archives and records those archive paths
and frame indices in the all-frame CSV. Its audit and final CUR stages can
then reread exactly the scored atoms, while an RSS source-map CSV retains the
flat POSCAR, minimized source, raw index, pressure index, checksums, and
archive-frame mapping. This is the chosen minimal integration path; it does
not use the quota-CUR helper.

Initial adapter testing did not modify any pool. The first W/Ti provenance
preflight exposed a relative-versus-resolved path comparison bug in the new
adapter, which is corrected before retry. Import-dependent help and synthetic
tests must run after `module load jse` because the default shell Python lacks
ASE/NumPy; the production wrapper already loads this environment.

### RSS selection adapter implementation

Added `src/rss_all_frame_scoring.py` and
`scripts/slurm/run_rss_selection_pipeline.slurm`. The scorer rejects an
existing output root, verifies complete configured raw/minimized/flat
coverage, byte-identical flat/minimized POSCARs, unary finite 3D-PBC
geometries, raw-index/pressure-index identity, and exact ten-JNN input. It
then atomically writes per-`(natoms, Mini-pressure)` extxyz archives,
`uncertainty_all_frames.csv`, `rss_frame_provenance.csv`, and JNN checksums.

The pipeline runs this all-frame scorer directly inside its one-node/one-task
SLURM allocation, derives the ten-log mean final-test-force `U_min`, then
uses the existing absolute-U geometry audit and D4-projected CUR unchanged.
It fixes zero frame gaps, linear p99 tail, and `floor(target/20)` tail cap;
it writes only a new protected `rss-selection/` root and no DFT/database/
training/EOS artifact.

After `module load jse`, `python3 -m py_compile src/*.py`, Bash syntax/help
checks, W/Ti adapter provenance checks on their actual 1,200-structure pools,
an expected Ta provenance rejection, and a monkeypatched synthetic archive/
CSV materialization test all passed. The source index, unary workflow guide,
and SLURM README now document this RSS-specific path.

The first W/Ti submission-preflight heredoc failed before any input check
because it ran from the repository root without adding `src/` before importing
`rss_all_frame_scoring`. This is a preflight harness import-path error only;
add `src/` explicitly and rerun read-only. No scheduler job or selection
output was created.

The final read-only preflight confirmed that both W/Ti `rss-selection/` roots
were absent, `OVERWRITE` was unset, the intended FCC D4 databases existed,
and the JSE runner was available after `module load jse`. The wrapper fixes
one node, one task, and 24 hours and no submission used an overwrite option.
The bare login shell does not expose `jse` until its module is loaded; this
was resolved without changing any input or output artifact.

Submitted exactly the two independent protected cards:

```bash
sbatch ... run_rss_selection_pipeline.slurm --element W \
  --round-dir W-potential/fcc-restart/05-rss-round-1 \
  --base W-potential/fcc-restart/current.db --target 100 \
  --min-distance 1.695596956 --max-normalized-void 0.946305262 \
  --r-c 6.0 --n-max 5 --l-max 6 --similarity-threshold 0.99999
# Submitted batch job 13584

sbatch ... run_rss_selection_pipeline.slurm --element Ti \
  --round-dir Ti-potential/fcc-restart/05-rss-round-1 \
  --base Ti-potential/fcc-restart/current.db --target 100 \
  --min-distance 1.775270170 --max-normalized-void 0.946161232 \
  --r-c 6.0 --n-max 5 --l-max 6 --similarity-threshold 0.99999
# Submitted batch job 13585
```

The one immediate combined `squeue` query reported both jobs pending (`PD`)
at `0:00`. No Ta job was submitted and no DFT, merge, M5, or E5 operation was
started. Do not poll further unless the user asks.

### User-requested status check and failure diagnosis

```bash
sacct -X -n -P -j 13584,13585 \
  --format=JobID,State,ExitCode,Elapsed,Start,End,Reason
# 13584|FAILED|1:0|00:00:53|...|None
# 13585|FAILED|1:0|00:00:50|...|None
```

Both jobs completed Stage 1: each validated its 500-row element-local D4
database, derived its ten-log `U_min` (W `0.20788`, Ti `0.134` eV/A), scored
all 1,200 RSS/Mini structures, and wrote 1,200 all-frame and provenance rows
plus the 24 grouped source archives. Neither reached a geometry audit or CUR
output.

Both Stage-2 traces reported the same adapter error: the all-frame CSV named
an archive below the scorer's removed temporary directory
`.rss-selection.tmp-<pid>/source-frames/`, rather than its final atomically
renamed `rss-selection/source-frames/` location. Therefore the existing
partial output roots are not valid selection results.

Fixed `src/rss_all_frame_scoring.py` so it still writes archives to the
temporary root but records the final `output_root/source-frames/...` path.
After `module load jse`, targeted `py_compile`, a synthetic
materialization/CSV-path test, and `git diff --check` passed. The W/Ti
partial roots remain protected and were not changed or removed. A user must
explicitly authorize deletion of only:

```text
W-potential/fcc-restart/05-rss-round-1/rss-selection/
Ti-potential/fcc-restart/05-rss-round-1/rss-selection/
```

before their corrected no-overwrite selection cards can be resubmitted. Keep
both `slurm_logs/` directories. Ta remains independently blocked by its 53
raw/minimized provenance mismatches.

### Approved Ta logged-failure partial selection

Ta regeneration `13586` completed at the scheduler level but its retained
Mini log recorded 60 LAMMPS neighbor-list-overflow `exit=1` pairs. All 52
atom-count mismatches are among those pairs; eight further logged failures
happen to retain their nominal atom count. The user explicitly directed that
the failed structures be omitted while preserving the 100-structure selection
target.

Updated `src/rss_all_frame_scoring.py` with optional
`--mini-failure-log`. It parses only the final JSE `LMP FAIL LIST`, rejects
invalid/duplicate/unconfigured source keys, excludes all and only its
`exit=1` pairs, accepts missing output only for such pairs, and writes
`mini_failure_exclusions.csv`. Every nonfailed raw/pressure pair remains
mandatory and receives the former strict composition, geometry, atom-count,
manifest, and byte-identity validation. `score_parameters.txt` and the SLURM
input record retain the failure-log path and checksum.

Updated `scripts/slurm/run_rss_selection_pipeline.slurm`,
`research-plan.md`, `docs/source_function_index.md`,
`docs/unary_workflow.md`, and `scripts/slurm/README.md` to require explicit,
auditable failure-list exclusion rather than silent partial-pool acceptance.

After `module load jse`, targeted/full Python syntax checks, wrapper syntax
and help checks, `git diff --check`, an actual Ta read-only validation
(`60` excluded, `1,140` complete valid candidates), and a synthetic
missing-failed-output/materialization test passed.

Submitted only the protected Ta selection card:

```bash
sbatch ... run_rss_selection_pipeline.slurm --element Ta \
  --round-dir Ta-potential/fcc-restart/05-rss-round-1 \
  --base Ta-potential/fcc-restart/current.db --target 100 \
  --min-distance 1.775316838 --max-normalized-void 0.942271015 \
  --r-c 6.0 --n-max 5 --l-max 6 --similarity-threshold 0.99999 \
  --mini-failure-log Ta-potential/fcc-restart/05-rss-round-1/rss/logs/unary-Ta.log
# Submitted batch job 13589
```

The one immediate `squeue` check found `13589` pending (`PD`) at `0:00`.
No W/Ti or DFT/database/training/EOS asset was changed. Do not poll unless
the user asks.

### Ta selection terminal validation

On the user's later request, a focused accounting query reported Ta `13589`
`COMPLETED`, exit `0:0`, elapsed `00:01:37`. Read-only validation accepted:

- `score_parameters.txt`: Ta-only ten-model committee, 1,140 scored
  structures, 60 logged Mini exclusions, and the retained failure-log
  checksum;
- `uncertainty_all_frames.csv` and `rss_frame_provenance.csv`: 1,140 unique,
  finite unary Ta frames across 24 source archives, exactly the 1,200
  raw/pressure keys less the 60 logged failures;
- `geometry_audit.csv`: complete coverage of the 166 post-`U_min=0.18167`
  frames, 124 geometry-passing and 42 rejected records, all finite;
- `absolute-u-projected-cur/`: matching Ta D4 base checksum, target 100,
  descriptor/gate card unchanged, 100 unique CUR ranks/final POSCARs, and
  2 tail selections below the cap of 5.

Every selected POSCAR has matching Ta composition/atom count and selected
candidate provenance. No excluded raw/pressure key appears in a scored,
audited, or selected record. No DFT, database merge, M5 training, or E5
evaluation was started.

### Authorized W/Ti selection recovery

The user authorized selection of the remaining W/Ti pools. Before cleanup,
each `rss-selection/` root was checked as a real contained non-symlink
directory with only its expected Stage-1 files (all-frame CSV, source map,
score parameters, and 24 source archives) and no geometry audit/CUR output.
Only these roots were removed:

```text
W-potential/fcc-restart/05-rss-round-1/rss-selection/
Ti-potential/fcc-restart/05-rss-round-1/rss-selection/
```

The W and Ti `rss/` generation roots were not changed. Their respective
`slurm_logs/` trees had pre/post aggregate checksums
`0bd9d0f6b2eec26fafb5c90c39e5db63b2b51f518d856c54ef66b26e07ac86bd` and
`0e250624ebf61706f85c21911fdfbdc15dbeae42164ec321c0f5761252799f47`,
unchanged across cleanup.

The repeated no-overwrite preflight accepted each matching 500-row FCC D4
database, ten M4 JNNs/logs, 400 raw and 1,200 complete valid
raw/minimized/flat structures, absent selection roots, unset `OVERWRITE`, and
the one-node/one-task/24-hour wrapper. It also passed full Python syntax,
adapter help, and Bash syntax/help checks.

Submitted the unchanged 100-target selection cards:

```text
W job 13591: min_distance=1.695596956, max_normalized_void=0.946305262
Ti job 13592: min_distance=1.775270170, max_normalized_void=0.946161232
```

Both use their own FCC D4 DB, all ten matching M4 JNNs, original valid RSS
pool, `r_c=6.0`, `n_max=5`, `l_max=6`, similarity `0.99999`, no failure-log
exception, and no overwrite option. The one immediate combined `squeue` check
reported both pending (`PD`) at `0:00`. Do not poll unless the user asks.

### W/Ti selection terminal validation

On the user's subsequent status request, focused accounting reported W
`13591` `COMPLETED`, exit `0:0`, elapsed `00:01:31`, and Ti `13592`
`COMPLETED`, exit `0:0`, elapsed `00:01:13`. Their short runtimes are normal:
the fixed one-node allocation scores 1,200 retained small RSS structures and
runs the bounded audit/CUR workflow.

Read-only validation accepted each element's own D4 checksum, ten-model score
record, 24 source archives, complete 1,200 raw/pressure provenance,
finite all-frame/audit records, exact post-`U_min` audit coverage, geometry
gates, projected-CUR ranks, tail cap, and final Ta-free POSCAR provenance:

| Element | Scored | Post-U audit | Geometry valid / rejected | Final | Tail final |
|---|---:|---:|---:|---:|---:|
| W | 1,200 | 373 | 258 / 115 | 100 | 0 |
| Ti | 1,200 | 158 | 158 / 0 | 100 | 2 |

Both selected-POSCAR directories contain exactly 100 matching unary,
periodic structures. A first combined validator stopped only because it
compared Ti `min_distance=1.77527017` as text against a trailing-zero
literal; the numeric-tolerance rerun passed every Ti condition. No workflow
artifact was changed by validation and no DFT/database/training/EOS command
was submitted.
