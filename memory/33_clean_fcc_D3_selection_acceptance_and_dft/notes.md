# Notes: Clean-FCC D3 Selection Acceptance and DFT Submission

## Sources

### Source 1: D3 selection record
- Path: `memory/32_clean_fcc_D3_md_validation_selection_card/`
- Key points:
  - W `13519`, Ta `13520`, and Ti `13521` are terminal `COMPLETED 0:0`.
  - Each approved card targets 100 structures with matching M2 committee,
    frozen geometry gates, projected CUR, and a capped five-structure p99
    extreme-uncertainty layer.

### Source 2: Workflow and active entry points
- Paths: `research-plan.md` sections 3, 5, 8.2.4; and
  `docs/source_function_index.md`.
- Key points:
  - Preserve every all-frame, audit, and projected-CUR artifact.
  - New labels must use `src/vasp_batch_dft.py` through
    `scripts/slurm/run_vasp_batch_dft.slurm`.

## Commands and Observations

```bash
# Terminal accounting check requested by the user:
sacct -j 13519,13520,13521 \
  --format=JobIDRaw,JobName%30,State,ExitCode,Elapsed -n -P
```

## Synthesized Findings

### Current status
- The three selection allocations completed successfully at scheduler level.
- D3 selection acceptance and Protocol-A DFT preflight passed for all
  elements; DFT submission is in progress.

### Validator corrections
- Recorded selection commands use shell-escaped commas (`1\,5\,...`) because
  the runner writes them with `printf %q`; read-only command checks must use
  `shlex.split`.
- The JSE ASE environment (`ASE 3.26.0`) is available after `module load jse`.
  Geometry validation compares chemical-symbol lists, not the array-like
  `Atoms.symbols` object.
- `cur_selected_distribution.csv` uses the selector's `source_layer` group
  name for joint source/tail rows; it does not use
  `source_uncertainty_layer`.
- Numeric selection command arguments are validated by numeric value, because
  the saved Ti command preserves a non-semantic trailing zero in
  `1.775270170`.

### D3 selection acceptance

Read-only acceptance passed. Each element retained 35,007 finite score rows
with exactly 31,507 production rows across its seven isolated NPT sources,
and its audit exactly covered production frames at or above the matching
M2-derived `U_min`. Frozen card/command provenance, ten-M2-log provenance,
geometry-gate conservation, projected-CUR rank and similarity checks,
linear-p99 tail cap, retained distribution, and byte-identical 300-row D2
base database checks all passed.

| Element | Post-U audit | Geometry valid / rejected | p99 U (eV/A) | Selected tail |
|---|---:|---:|---:|---:|
| W | 31,498 | 24,877 / 6,621 | 1.529091011 | 5 |
| Ta | 31,299 | 24,706 / 6,593 | 1.276440283 | 5 |
| Ti | 30,869 | 26,294 / 4,575 | 0.742445160 | 5 |

All final sets contain exactly 100 unique CUR-ranked POSCARs. Every final
structure is a finite unary, 32-atom, 3D-periodic positive-cell structure
and agrees exactly with both its candidate POSCAR and originating NPT
trajectory frame: maximum cell error is `0 A`; maximum wrapped scaled
coordinate error is `3.331e-16` (W/Ta) or `3.886e-16` (Ti).

### Protocol-A D3 DFT preflight

The D2 static Protocol-A command/INCAR is retained unchanged: `MAGMOM=_`,
`KSPACING=0.2`, auto `ENCUT=1.3*ENMAX`, `NCORE=2`, static
`IBRION=-1`, `NSW=0`, and the existing accuracy/convergence settings.
After `module load jse`, `vasp_std` resolves to
`/home/opt/vasp-6.5.0/vasp_std`.

Each selected D3 input directory has exactly 100 POSCARs. The intended label
DB and VASP work root are absent; `OVERWRITE`, `FORCE_PREPARE`, and
`PREPARE_ONLY` are unset. The local Protocol-A PAW identities remain:

| Element | POTCAR SHA-256 | ENMAX / auto-ENCUT (eV) |
|---|---|---:|
| W | `c0897285f1b301314dcc12eb838ce8a777aa860795754598b0626cb818170117` | 223.057 / 289.9741 |
| Ta | `b94d0231aa338d2b49887428178c5ebac7fa385cbd6154890af94e8013d269f3` | 223.667 / 290.7671 |
| Ti | `f8e8f1d080d9e9b45e792f1068744b07aba8441d1e7ce11486a5d4c0f5a1479e` | 178.330 / 231.8290 |

The authorized submissions use one node, 64 tasks, 24 hours, eight MPI ranks
per VASP task, and eight concurrent tasks. They write independent
`<X>_D3_labeled.db` and `dft/vasp_<X>_D3/` paths below their own round roots.

### D3 Protocol-A DFT submissions

The following no-overwrite command form was submitted independently for each
element, with the matching `tag`:

```bash
env -u OVERWRITE -u FORCE_PREPARE -u PREPARE_ONLY \
  CORES_PER_JOB=8 MAX_WORKERS=8 VASP_COMMAND=vasp_std \
  sbatch --parsable --job-name=fcc_d3_dft_<X> \
  --nodes=1 --ntasks=64 --time=24:00:00 \
  --output=<X>-potential/fcc-restart/03-npt-round-1/slurm_logs/fcc-d3-dft-%j.out \
  --error=<X>-potential/fcc-restart/03-npt-round-1/slurm_logs/fcc-d3-dft-%j.err \
  scripts/slurm/run_vasp_batch_dft.slurm \
  <selected-poscar-dir> \
  <X>-potential/fcc-restart/03-npt-round-1/<X>_D3_labeled.db _ 0.2
```

| Element | DFT job | One immediate status check |
|---|---:|---|
| W | `13531` | `RUNNING` on `lpsnode03` |
| Ta | `13532` | `RUNNING` on `dreamx-cpu` |
| Ti | `13533` | `PENDING (Resources)` |

No polling loop is active. Do not merge, train M3, or run E3 until each
completed label database passes read-only Protocol-A/task/finite/source
geometry validation.
