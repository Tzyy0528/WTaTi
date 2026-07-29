# Notes: Clean-FCC D3 MD Validation and Selection Card

## Sources

### Source 1: Completion report and D3 launch record
- Paths: user report; `memory/30_clean_fcc_D3_npt_launch/`.
- Key points:
  - D3 jobs are W `13513`, Ta `13514`, and Ti `13515`.
  - Each must produce the seven `P-1GPa` through `P-50GPa` NPT sources.

### Source 2: Workflow validation gate
- Path: `research-plan.md`, section 8.4.
- Key points:
  - Every source requires command, log, trajectory, and summary outputs.
  - NPT validation requires finite positions/cell/volume/energy/forces and
    finite stress/pressure diagnostics before all-frame scoring.

### Source 3: Combined selection entry point
- Path: `memory/31_combined_selection_pipeline/deliverable.md`.
- Key points:
  - After MD validation and a frozen card, one pipeline allocation can run
    score-only, audit, and CUR without bypassing retained artifacts.

## Commands and Observations

```bash
sacct -X -j 13513,13514,13515 \
  --format=JobID,JobName%18,State,ExitCode,Elapsed --noheader

# Under module load jse, read-only validation of all 21 NPT sources:
# - frozen current.db/JNN digests unchanged;
# - exact M2-only command provenance;
# - command/log/trajectory/summary existence and completion;
# - 5,001 finite unary 32-atom/PBC/positive-cell trajectory frames/source;
# - finite energy, (32,3) force, and (6,) stress;
# - 50,001 finite consecutive summary rows/source, including NPT pressure.
```

## Synthesized Findings

### Terminal jobs and complete D3 source validation

The one focused accounting check found all three jobs terminally successful:

| Element | Job ID | State / exit | Elapsed |
|---|---:|---|---:|
| W | `13513` | `COMPLETED / 0:0` | `00:59:20` |
| Ta | `13514` | `COMPLETED / 0:0` | `00:59:10` |
| Ti | `13515` | `COMPLETED / 0:0` | `01:00:02` |

All seven expected `P-1GPa`, `P-5GPa`, `P-10GPa`, `P-20GPa`, `P-30GPa`,
`P-40GPa`, and `P-50GPa` sources passed for every element. Every source has
the matching M2-only `command.sh`, a complete `Starting NPT biased MD` /
`Finished MD` log, 5,001 finite unary 32-atom 3D-periodic positive-cell
trajectory frames with finite energy, `(32,3)` forces, and `(6,)` stress, and
50,001 finite consecutive summary rows with finite pressure diagnostics.

| Element | Frames / summary rows | Volume/atom (A3) | Instant pressure (GPa) | Maximum force component (eV/A) |
|---|---:|---:|---:|---:|
| W | 35,007 / 350,007 | 13.665253--23.025559 | -13.858810--92.131740 | 16.984412 |
| Ta | 35,007 / 350,007 | 13.914933--25.196221 | -9.419690--100.749940 | 11.924722 |
| Ti | 35,007 / 350,007 | 9.745292--20.820924 | -5.119070--134.980490 | 11.064491 |

The three 300-row current-DB checksums and all three ordered ten-model M2
digests remain frozen. D3 all-frame, audit, CUR, DFT, merge, M3, and E3
outputs remain absent.

### Remaining selection-card gate

The combined runner will derive `U_min` from the matching ten M2 logs and
uses p99 with `floor(0.05 * target)` automatically. Before it may be
submitted, the user must explicitly approve the D3 DFT target for W, Ta, and
Ti and confirm the element-local distance/void and descriptor values. The
prior D2 numerical target is not silently inherited.

### Frozen clean-FCC D3 combined selection cards

The user approved the one-allocation combined runner and `target=100` for
each independent element, then explicitly authorized submission. The frozen
cards are recorded in `research-plan.md` section 8.2.4:

| Element | U_min (eV/A) | min distance (A) | max normalized void | descriptor card |
|---|---:|---:|---:|---|
| W | `0.187770000` | `1.695596956` | `0.946305262` | `r_c=6.0`, `n_max=5`, `l_max=6`, similarity `0.99999` |
| Ta | `0.167500000` | `1.775316838` | `0.942271015` | same |
| Ti | `0.117740000` | `1.775270170` | `0.946161232` | same |

All jobs use NPT pressures `1 5 10 20 30 40 50`, equilibration fraction
`0.10`, progress interval `500`, zero candidate/final frame gaps, and linear
p99 with `tail_max=floor(0.05*100)=5`. The runner derives each U_min from
exactly ten final M2 trainer-log test-force MAEs, retains all intermediate
artifacts, and rejects existing selection outputs.

Read-only preflight confirmed `OVERWRITE` unset; each independent current DB
has exactly 300 rows and its frozen checksum; exactly ten matching nonempty
M2 JNNs and logs; and absent D3 score, audit, CUR, DFT, merge, M3, and E3
outputs. D3 roots contain the validated seven pressure trajectories and
existing MD/scheduler artifacts only.

### Combined selection submissions

Immediately before each submission, an element-local no-overwrite guard again
confirmed `OVERWRITE` unset, frozen current-DB checksum, seven pressure
trajectories, ten nonempty M2 JNN/log pairs, and absent score/audit/CUR/DFT/M3/E3
outputs. The following one-node, one-task, 24-hour jobs were submitted:

| Element | Job ID | Scheduler stdout / stderr |
|---|---:|---|
| W | `13519` | `W-potential/fcc-restart/03-npt-round-1/slurm_logs/select-W-%j.out/.err` |
| Ta | `13520` | `Ta-potential/fcc-restart/03-npt-round-1/slurm_logs/select-Ta-%j.out/.err` |
| Ti | `13521` | `Ti-potential/fcc-restart/03-npt-round-1/slurm_logs/select-Ti-%j.out/.err` |

The one permitted immediate combined `squeue` check found all three jobs
running (`R`) on `lpsnode02`: W at `0:39`, Ta at `0:21`, and Ti at `0:03`.
No polling or monitoring is active. DFT labeling, merge, M3, and E3 remain
unauthorized.

### User-requested terminal selection status

On the user's subsequent report that structure selection had finished, one
focused `sacct` check found all three combined selection allocations
successfully terminal:

| Element | Job ID | State / exit | Elapsed |
|---|---:|---|---:|
| W | `13519` | `COMPLETED / 0:0` | `02:15:02` |
| Ta | `13520` | `COMPLETED / 0:0` | `02:13:03` |
| Ti | `13521` | `COMPLETED / 0:0` | `02:16:48` |

This confirms scheduler success only. The next mandatory gate is read-only
validation of the retained score-only, geometry-audit, and projected-CUR
outputs (including final POSCAR/provenance/source/tail checks) before any
Protocol-A DFT submission.
