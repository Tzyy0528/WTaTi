# Notes: Clean-FCC D5 DFT Readiness

## Sources

### Source 1: D5 RSS selection deliverable
- Path: `memory/41_clean_fcc_D5_rss_selection/deliverable.md`
- Key points:
  - Each element has 100 provenance-validated selected POSCARs.
  - No DFT, merge, training, or EOS stage was authorized by that task.

### Source 2: Prior accepted Protocol-A records
- Path: `memory/20_D3_DFT_labeling/notes.md` and
  `memory/37_clean_fcc_D4_to_DFT_submission/notes.md`
- Key points:
  - Protocol A is unchanged through D4: static VASP, `KSPACING=0.2`,
    automatic `ENCUT=1.3*ENMAX`, `NCORE=2`, `MAGMOM=_`, no explicit SOC or
    spin override, and `vasp_std`.
  - Standard local PAWs, not semicore variants, are frozen: W ZVAL 6, Ta
    ZVAL 5, Ti ZVAL 4.
  - D4 confirms the same PAW checksums and successful static-label protocol.

### Source 3: Current production VASP entry points
- Path: `research-plan.md` section 5; `docs/source_function_index.md`;
  `scripts/slurm/run_vasp_batch_dft.slurm`; `src/vasp_batch_dft.py`
- Key points:
  - Only the SLURM template calling `vasp_batch_dft.py label` is supported.
  - The current backend writes static `IBRION=-1`, `NSW=0`, `ISIF=2`,
    `PREC=Accurate`, `ALGO=Normal`, `EDIFF=1E-5`, and `SIGMA=0.1`;
    `MAGMOM=_` omits MAGMOM. It has no `LSORBIT` or `ISPIN` override.
  - The template rejects an existing output DB by default. Existing nonempty
    VASP task directories also fail preparation unless `--force` is supplied.

## Commands and Observations

```bash
# Read-only selection/base-DB/POTCAR audit (with module load jse)
# - Python Path.glob("*.poscar") and ASE: 100 final POSCARs per element;
#   selected names 000001..000100, all unary/PBC/finite/positive-cell.
# - selection_summary.csv: 100 selected rows, CUR ranks 1..100, and exact
#   selected-file name correspondence.
# - current.db: matching frozen SHA-256 and 500 unary 32-atom rows.
# - planned D5 label DB and VASP work roots: absent.
# - local POTCAR: frozen checksum and ENMAX verified.
# - command -v vasp_std and sbatch; vasp_batch_dft.py --help.
# Final authorization-time no-overwrite check:
# - all three selected POSCAR directories still contain exactly 100 files;
# - W_D5_labeled.db, Ta_D5_labeled.db, Ti_D5_labeled.db and their matching
#   dft/vasp_<X>_D5 work roots are absent;
# - OVERWRITE, FORCE_PREPARE, and PREPARE_ONLY remain unset.
```

## Synthesized Findings

### Frozen Protocol-A card

| Element | Local standard PAW SHA-256 | ZVAL / ENMAX (eV) | Auto ENCUT (eV) |
|---|---|---:|---:|
| W | `c0897285f1b301314dcc12eb838ce8a777aa860795754598b0626cb818170117` | 6 / 223.057 | 289.9741 |
| Ta | `b94d0231aa338d2b49887428178c5ebac7fa385cbd6154890af94e8013d269f3` | 5 / 223.667 | 290.7671 |
| Ti | `f8e8f1d080d9e9b45e792f1068744b07aba8441d1e7ce11486a5d4c0f5a1479e` | 4 / 178.330 | 231.8290 |

- W and Ta use the frozen standard (non-semicore) PAWs and exclude SOC.
- Ti uses its frozen standard ZVAL-4 PAW with no `ISPIN`/`MAGMOM` override;
  its Protocol-A spin policy is the default non-spin VASP calculation.
- All use `MAGMOM=_`, `KSPACING=0.2`, auto ENCUT above, `NCORE=2`, and the
  static policy. `vasp_std` resolves to `/home/opt/vasp-6.5.0/vasp_std`.

### Read-only D5 batch preflight

| Element | Selected input validation | D4 base DB | Selected-set SHA-256 | Protected D5 outputs |
|---|---|---|---|---|
| W | 100, unary W, 3D PBC, finite, 9--25 atoms | 500 rows, `1242b2f534f1...` | `cbbbb92b8dd5d2d023c297ed6946e6bcbdb1522303103008e73a9cd30b063e75` | `W_D5_labeled.db` / `dft/vasp_W_D5`: absent |
| Ta | 100, unary Ta, 3D PBC, finite, 9--25 atoms | 500 rows, `600bd1c0c7d2...` | `7dcc8fb4431df71f12253b9ceecc8e8b4996660f2b90f08ce57f2b429904500e` | `Ta_D5_labeled.db` / `dft/vasp_Ta_D5`: absent |
| Ti | 100, unary Ti, 3D PBC, finite, 9--25 atoms | 500 rows, `8db00646830c...` | `3896c15687b7f01673b8fe5ca7d2b8d57189f821e33663d20ca480be1cbaa512` | `Ti_D5_labeled.db` / `dft/vasp_Ti_D5`: absent |

- Each selected set has exact names `000001.poscar` through `000100.poscar`,
  one-to-one provenance in `selection_summary.csv`, and CUR ranks 1--100.
- The working shell has no inherited `OVERWRITE`, `FORCE_PREPARE`, or
  `PREPARE_ONLY` setting. `sbatch` and the JSE-provided `vasp_std` resolve.
- The template's standard allocation is one node / 64 tasks, typically eight
  concurrent eight-rank VASP tasks (`CORES_PER_JOB=8`, `MAX_WORKERS=8`);
  it currently has no explicit wall-time directive. Resource/account/partition
  settings still need confirmation immediately before an authorized submission.
- No DFT job, task preparation, output DB creation, merge, training, or EOS
  action occurred in this audit.

### Authorized submission card

- User authorization: submit all three D5 Protocol-A batches.
- Resources: `--nodes=1 --ntasks=64 --time=24:00:00`;
  `CORES_PER_JOB=8`, `MAX_WORKERS=8`, `NCORE=2`, and
  `VASP_COMMAND=vasp_std`. The default cluster partition/account is retained,
  consistent with accepted D4 labeling.
- No-overwrite: explicitly remove `OVERWRITE`, `FORCE_PREPARE`, and
  `PREPARE_ONLY` from the `sbatch` environment; do not pass an overwrite or
  force option.
- Outputs: only `<X>-potential/fcc-restart/05-rss-round-1/<X>_D5_labeled.db`
  and `dft/vasp_<X>_D5/` beneath the matching element root.

### D5 Protocol-A submissions

After the final no-overwrite guard, the following supported commands were
submitted from the repository root:

```bash
env -u OVERWRITE -u FORCE_PREPARE -u PREPARE_ONLY WORK_DIR=W-potential/fcc-restart/05-rss-round-1/dft/vasp_W_D5 CORES_PER_JOB=8 MAX_WORKERS=8 NCORE=2 VASP_COMMAND=vasp_std ENCUT_FACTOR=1.3 PROGRESS_INTERVAL=60 sbatch --job-name=W_D5_DFT --nodes=1 --ntasks=64 --time=24:00:00 --output W-potential/fcc-restart/05-rss-round-1/slurm_logs/vasp-submit-%j.out --error W-potential/fcc-restart/05-rss-round-1/slurm_logs/vasp-submit-%j.err scripts/slurm/run_vasp_batch_dft.slurm W-potential/fcc-restart/05-rss-round-1/rss-selection/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p20788_cur100 W-potential/fcc-restart/05-rss-round-1/W_D5_labeled.db _ 0.2
env -u OVERWRITE -u FORCE_PREPARE -u PREPARE_ONLY WORK_DIR=Ta-potential/fcc-restart/05-rss-round-1/dft/vasp_Ta_D5 CORES_PER_JOB=8 MAX_WORKERS=8 NCORE=2 VASP_COMMAND=vasp_std ENCUT_FACTOR=1.3 PROGRESS_INTERVAL=60 sbatch --job-name=Ta_D5_DFT --nodes=1 --ntasks=64 --time=24:00:00 --output Ta-potential/fcc-restart/05-rss-round-1/slurm_logs/vasp-submit-%j.out --error Ta-potential/fcc-restart/05-rss-round-1/slurm_logs/vasp-submit-%j.err scripts/slurm/run_vasp_batch_dft.slurm Ta-potential/fcc-restart/05-rss-round-1/rss-selection/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p18167_cur100 Ta-potential/fcc-restart/05-rss-round-1/Ta_D5_labeled.db _ 0.2
env -u OVERWRITE -u FORCE_PREPARE -u PREPARE_ONLY WORK_DIR=Ti-potential/fcc-restart/05-rss-round-1/dft/vasp_Ti_D5 CORES_PER_JOB=8 MAX_WORKERS=8 NCORE=2 VASP_COMMAND=vasp_std ENCUT_FACTOR=1.3 PROGRESS_INTERVAL=60 sbatch --job-name=Ti_D5_DFT --nodes=1 --ntasks=64 --time=24:00:00 --output Ti-potential/fcc-restart/05-rss-round-1/slurm_logs/vasp-submit-%j.out --error Ti-potential/fcc-restart/05-rss-round-1/slurm_logs/vasp-submit-%j.err scripts/slurm/run_vasp_batch_dft.slurm Ti-potential/fcc-restart/05-rss-round-1/rss-selection/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p134_cur100 Ti-potential/fcc-restart/05-rss-round-1/Ti_D5_labeled.db _ 0.2
```

| Element | Job ID | Immediate `squeue` state |
|---|---:|---|
| W | `13601` | `PD`, reason `(None)` |
| Ta | `13602` | `PD`, reason `(Priority)` |
| Ti | `13603` | `PD`, reason `(Priority)` |

- The displayed `squeue` command was the single immediate status check.
- No subsequent polling, output inspection, DFT-result validation, merge,
  M5 training, or E5 action is authorized.
