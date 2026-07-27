# Notes: D3 Protocol-A VASP Labeling

## Sources

### Source 1: Completed D3 selection
- Path: `memory/19_D3_scoring_selection/`
- Key points:
  - Each element has exactly 100 validated, element-local D3 selected POSCARs.
  - EOS assets remain excluded and no database has been changed.

### Source 2: Frozen prior Protocol-A labels
- Path: `memory/09_D1_DFT_labeling/`; `memory/14_D2_DFT_labeling/`
- Key points:
  - D3 reuses the D1/D2 static active-label protocol without modification:
    `MAGMOM=_`, `KSPACING=0.2`, `ENCUT=1.3*max(ENMAX)`, `NCORE=2`,
    `vasp_std`, eight 8-rank VASP tasks per 64-task allocation, and no
    explicit SOC or spin override.
  - The output DB and VASP work root must both be absent; no overwrite or
    forced input rewrite is allowed.

### Source 3: Current implementation and research policy
- Path: `research-plan.md` Section 5; `docs/source_function_index.md`;
  `scripts/slurm/run_vasp_batch_dft.slurm`; `src/vasp_batch_dft.py`
- Key points:
  - The active backend is the template's `label` subcommand, which writes a
    per-POSCAR static task, runs VASP via exclusive 8-rank `srun` steps, and
    collects only completed energy/force/stress results into a new ASE DB.
  - The runner uses repository-local `POTCAR/PBE/<element>/POTCAR`, not the
    legacy `nncalc` path, and rejects an existing output DB by default.
  - The static generated INCAR retains `IBRION=-1`, `NSW=0`, `ISIF=2`,
    `PREC=Accurate`, `ALGO=Normal`, `EDIFF=1E-5`, `SIGMA=0.1`, `KGAMMA=True`,
    `LASPH=True`, `ISYM=0`, and no `MAGMOM`, SOC, or explicit spin override.

## Commands and Observations

- User explicitly authorized the next D3 VASP labeling stage.

## Frozen Protocol-A and Immediate Preflight (passed)

The active `src/dbselectandtrain.py::ENERGY` values were checked against the
corresponding M2 generated `Trainer.groovy` files and match:

```text
W  -12.9581 eV
Ta -11.8578 eV
Ti  -7.8951 eV
```

The existing Protocol-A PAW identities are unchanged. Standard PBE PAWs
(`W`, `Ta`, and `Ti`, rather than a semicore variant) have ZVAL 6, 5, and 4,
respectively; explicit SOC and spin overrides remain absent. `vasp_std` is
available after `module load jse`. Although the module exposes
`VASP_PP_PATH`, the active batch backend correctly takes PAWs only from the
repository-local paths audited below.

| Element | Selected input | Base DB | PAW SHA-256 | ENMAX -> auto ENCUT (eV) | Protected label DB / work root |
|---|---|---:|---|---|---|
| W | 100 unique `000001..000100.poscar` | 300 rows | `c0897285f1b301314dcc12eb838ce8a777aa860795754598b0626cb818170117` | 223.057 -> 289.9741 | absent / absent |
| Ta | 100 unique `000001..000100.poscar` | 300 rows | `b94d0231aa338d2b49887428178c5ebac7fa385cbd6154890af94e8013d269f3` | 223.667 -> 290.7671 | absent / absent |
| Ti | 100 unique `000001..000100.poscar` | 300 rows | `f8e8f1d080d9e9b45e792f1068744b07aba8441d1e7ce11486a5d4c0f5a1479e` | 178.330 -> 231.8290 | absent / absent |

Each selected input set was revalidated as finite, 16-atom, 3D-periodic,
unary expected-element POSCARs with positive volume and unique file contents.
The matching bases retain their D2 hashes:

```text
W  b2a6ed5a86848a6fc83e3c13ceb4bc08ab2e60f0e7d753e2cb8555068c2c6476
Ta b4e7e34325bfc9506147c58bf4b9ebeb69a7491c2cb7510961cd457695c1a866
Ti 36eb18737c291e1dd26b11ca995f3255c0ae8da881e821ce66b08a0047e177cb
```

### D3 VASP batch submission (2026-07-25)

The protected submissions reuse the frozen static settings exactly:
`MAGMOM=_`, `KSPACING=0.2`, automatic `ENCUT=1.3*max(ENMAX)`, `NCORE=2`,
`vasp_std`, 8 cores/task, 8 concurrent VASP tasks, 1 node, and 64 SLURM
tasks. The template has no explicit wall time, preserving the partition
default. `OVERWRITE`, `FORCE_PREPARE`, and all merge/training options remain
absent.

| Element | Job ID | Input POSCAR root | New label DB | VASP work root |
|---|---:|---|---|---|
| W | 13185 | `W-potential/03-npt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p19431_cur100/` | `W-potential/03-npt-round-1/W_D3_selected_labeled.db` | `W-potential/03-npt-round-1/dft/vasp_W_D3_selected/` |
| Ta | 13186 | `Ta-potential/03-npt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p16667_cur100/` | `Ta-potential/03-npt-round-1/Ta_D3_selected_labeled.db` | `Ta-potential/03-npt-round-1/dft/vasp_Ta_D3_selected/` |
| Ti | 13187 | `Ti-potential/03-npt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p12595_cur100/` | `Ti-potential/03-npt-round-1/Ti_D3_selected_labeled.db` | `Ti-potential/03-npt-round-1/dft/vasp_Ti_D3_selected/` |

The one immediate focused queue check found all three jobs running on
`lpsnode01`; the template reports the partition's unlimited allocation limit.

### Terminal states and partial validation

The focused accounting check after the user reported completion found:

| Element | Initial job | State / exit | Elapsed | Label DB status |
|---|---:|---|---:|---|
| W | 13185 | FAILED / 1:0 | 01:13:14 | absent; retry required |
| Ta | 13186 | COMPLETED / 0:0 | 01:06:25 | validated, 100 rows |
| Ti | 13187 | COMPLETED / 0:0 | 01:16:00 | validated, 100 rows |

Ta and Ti label DB validation passed: each has exactly 100 unique
source-mapped rows, unary expected composition, 16 atoms, 3D PBC, finite
positions/cells/energy/forces/stress, positive volume, and no EOS provenance.

| Element | Energy range (eV/16-atom cell) | Volume range (A3/16-atom cell) |
|---|---:|---:|
| Ta | -182.285839040 to -164.516839210 | 238.845950527 to 404.351026021 |
| Ti | -119.360075020 to -105.084588360 | 193.624254534 to 315.297339365 |

W's runner completed 98 tasks and failed only
`00092_000092` and `00099_000099`, both with `srun` exit 139 / VASP MPI
segmentation faults on `lpsnode01`. The failures occurred at the same time
and do not present a VASP electronic-convergence error; no W label DB was
collected. The work root contains 98 normal completion-marked OUTCARs and two
incomplete task directories. The backend's no-force reuse logic verifies the
same source POSCAR/INCAR metadata, skips the 98 completed tasks, runs only the
two incomplete tasks, and collects the DB only if all 100 tasks complete.

### W retry submission

The corrected protected preflight found exactly 98 completion-marked W task
directories and two incomplete directories, the W label DB still absent, and
the original 100-POSCAR input unchanged. Job `13220` was then submitted with
one node, eight tasks, `CORES_PER_JOB=8`, and `MAX_WORKERS=1`. It retains the
identical Protocol-A INCAR/POTCAR settings and reuses matching prepared tasks;
neither `OVERWRITE` nor `FORCE_PREPARE` is enabled. Per the user's request,
no active monitoring was started.

### Final D3 label validation (passed)

On the user's explicit check request, focused accounting found W retry
`13220` `COMPLETED / 0:0` in `00:02:21`. All three labeled DBs now pass the
complete pre-merge audit:

- exactly 100 rows and 100 normal VASP completion-marked OUTCARs;
- one-to-one `000001.poscar`--`000100.poscar` source coverage and unique
  structure hashes;
- unary expected element, 16 atoms, 3D PBC, finite positions/cell/energy,
  `(16,3)` forces, and six-component stress; positive finite volume;
- matching unchanged 300-row D2 base DB and absent protected `updated.db`;
- no EOS or cross-element provenance.

| Element | Final label DB SHA-256 | Energy range (eV/16-atom cell) | Volume range (A3/16-atom cell) |
|---|---|---:|---:|
| W | `32da8595645a38fae7d8ab29db03e0cba1fd7060b37a3f0c83246741f85742b9` | -199.618807310 to -177.553197670 | 224.870669743 to 350.007027751 |
| Ta | `ea7d9a8500678ae492ed7c8e18e6bd3e32c86cbbcd5885f97daaa9255bf061de` | -182.285839040 to -164.516839210 | 238.845950527 to 404.351026021 |
| Ti | `3276f7d5c3ea0779af71624d05fcad17f442bcf10fc7e90408a9fba70b5b78f2` | -119.360075020 to -105.084588360 | 193.624254534 to 315.297339365 |

All three independent merge preconditions are now satisfied:

```text
base current.db: 300 rows, unchanged and element-local
new D3 label DB: 100 validated rows, element-local
output 03-npt-round-1/updated.db: absent
expected merged D3 database: 400 rows
```

Merge remains a separate user-authorized stage. M3 training and E3 evaluation
remain out of scope.

## Synthesized Findings

### Scope
- Use only `src/vasp_batch_dft.py` through
  `scripts/slurm/run_vasp_batch_dft.slurm`.
- Keep W, Ta, and Ti inputs, POTCARs, job outputs, and labeled DBs separate.
- Do not merge any labeled DB or train/evaluate a successor model in this
  task.
