# Notes: Clean-FCC D5 RSS Configuration

## Sources

### Source 1: Accepted D4/M4/E4 record
- Path/URL: `memory/38_clean_fcc_D4_to_M4_E4/`.
- Key points:
  - All three elements have isolated 500-row D4 databases and validated M4
    committees.
  - E4 is complete and is validation-only.

### Source 2: Frozen workflow policy
- Path/URL: `research-plan.md`, sections 9, 10, 11, 12, and 13.
- Key points:
  - D5 is `05-rss-round-1`, from M4 through RSS/Mini, all-pool scoring,
    recalibration, physical gates, projected CUR, Protocol-A labels, M5, and
    fixed E5.
  - Unary RSS uses atom counts `9,10,12,15,18,20,22,25` and Mini pressures
    `0,20e4,40e4` bar.
  - Recalculate `U_min` from all ten M4 final test MAE-F values; use
    geometry-valid linear p99 for `U_tail`, cap its contribution at
    `floor(0.05*N_DFT)`, and retain current-DB-projected CUR.
  - EOS references are validation-only and cannot be candidate/training
    inputs.

### Source 3: RSS and selection implementation
- Path/URL: `docs/source_function_index.md`,
  `src/rss_sampling_embedded.py`,
  `src/stratified_uncertainty_selection.py`, and
  `src/absolute_u_projected_cur_selection.py`.
- Key points:
  - The RSS driver accepts one relaxation JNN, a unary atom-count list, raw
    structure count, atomic volume, Mini pressures, and Mini controls. Its
    defaults are `nstructs=50`, `tri`, 10 loops, `etol=1e-4`, and `ftol=1e-8`.
  - The driver otherwise removes raw/minimized case work, so D5 must pass
    `--keep-raw --keep-minimized-work` for auditable provenance.
  - Existing all-frame scorer and projected-CUR selector require
    trajectory/frame metadata. No production RSS POSCAR-pool adapter is
    indexed; `rss_quota_cur_selection.py` is explicitly disallowed as the
    final selector.

## Commands and Observations

```bash
# Read-only seed-volume and M4-diagnostic recovery; no RSS/DFT/training run.
module load jse
python3 - <<'PY'
from ase.io import read
# Read 32-atom clean-FCC seed volumes and matching D4 DB volume ranges.
PY
```

## Synthesized Findings

### D5 generator card

All three elements retain the documented first-RSS coverage rather than
changing multiple factors after E4:

| Field | W | Ta | Ti |
|---|---:|---:|---:|
| D5 root (must be absent at preflight) | `W-potential/fcc-restart/05-rss-round-1/` | `Ta-potential/fcc-restart/05-rss-round-1/` | `Ti-potential/fcc-restart/05-rss-round-1/` |
| RSS output root | `<D5-root>/rss/` | `<D5-root>/rss/` | `<D5-root>/rss/` |
| Atomic volume (clean-FCC seed, A3/atom) | 15.903934900 | 18.151564915 | 17.345854575 |
| Current D4 DB rows / guard | 500 / matching only | 500 / matching only | 500 / matching only |
| RSS/Mini relaxation JNN | `M4/train-5/5.jnn` | `M4/train-5/5.jnn` | `M4/train-5/5.jnn` |
| Final test MAE-F of relaxer (meV/A) | 197.5 | 155.8 | 121.1 |
| Atom counts | `9,10,12,15,18,20,22,25` | same | same |
| Raw structures per unary RSS case | 50 | 50 | 50 |
| Mini pressures | `0,200000,400000` bar | same | same |
| Mini controls | `tri`; 10 loops; `1e-4` / `1e-8` eV tolerances | same | same |

The RSS driver exposes one unary case, so `--jobs 1` is explicit; it does not
create useful case-level concurrency for one element. A future SLURM resource
request must be finalized only with the missing production scorer/adapter and
an approved time estimate; it must run in an allocation, never on the login
node.

`--keep-raw --keep-minimized-work` is required, and `--overwrite` is
forbidden. The output validation must retain per-structure Mini pressure and
atom-count provenance, finite unary 3D-PBC geometry, positive volume, and
the complete raw/minimized/log/flat-collection artifacts. The source does not
document a reliable multiplicative output count for an atom-count list, so
accept the actual manifest only after complete source-condition coverage,
rather than assuming a nominal pool size.

### Force-stable relaxation-model adjustment

RSS/Mini optimization requires force quality, whereas E4 selects its
reporting JNN by held-out energy MAE. Among folds that satisfy the E4
energy-ratio policy, the lowest held-out force-MAE JNN is `train-5/5.jnn`
for every element. Its test force MAE is W 197.5, Ta 155.8, and Ti 121.1
meV/A. For Ta this replaces E4's `train-2/2.jnn` (180.1 meV/A) as the
single Mini relaxer; for Ti it replaces E4's `train-9/9.jnn` (140.1 meV/A).
The full ten-model M4 committee remains mandatory for all-pool uncertainty
scoring and is not replaced by this single relaxer.

The expected D5 `U_min` values, to be recomputed and recorded from all ten
M4 logs during selection, are W 0.20788000, Ta 0.18167000, and Ti
0.13400000 eV/A.

### Selection card and Ta-specific controls

Freeze the D4-proven policy for each matching D4 `current.db`: target
`N_DFT=100`, zero candidate/final frame gaps, linear geometry-valid p99
`U_tail`, tail cap 5, `r_c=6.0`, `n_max=5`, `l_max=6`, and similarity
threshold `0.99999`. Preserve the matching clean-D0 physical gates:

| Element | Minimum distance (A) | Maximum normalized void |
|---|---:|---:|
| W | 1.695596956 | 0.946305262 |
| Ta | 1.775316838 | 0.942271015 |
| Ti | 1.775270170 | 0.946161232 |

Do not add force, total-volume, Mini-pressure, source-quota, or EOS-derived
hard gates. Those fields remain auditable diagnostics. Do not enlarge Ta's
RSS pressure range or DFT budget: its E4 change versus E3 is only
`+1.281634 / +1.800237` meV/atom raw/phase-aligned MAE, with no evidence
that a more extreme generator would address the offset. The force-stable
relaxer and complete default 0/20/40 GPa, multi-size pool change the
candidate generator without weakening selection.

Before any Ta DFT authorization, require a read-only D5 report that confirms
complete atom-count/pressure provenance after minimization, finite
all-ten-model scores, the current-pool M4-log `U_min`, physical-gate
rejections, projected-CUR coverage relative to only Ta's D4 DB, and the
tail/duplicate audit. This is a diagnostic/acceptance gate, not permission to
insert EOS structures or to alter a selection threshold.

### Blocking implementation gate

The generator configuration is complete, but D5 cannot be submitted
end-to-end yet. `rss_sampling_embedded.py` yields retained flat POSCARs;
the indexed scorer assumes `round/md/<source>/multi_nnap_md.xyz`, while the
projected-CUR selector requires `trajectory`, `trajectory_path`, and `frame`
records that it can reread. A small production RSS pool-to-all-frame scoring
and geometry-audit adapter (or an approved existing equivalent) is required
before execution. It must score every minimized POSCAR with all ten matching
M4 models, retain stable atom-count/pressure source provenance, feed the
existing absolute-U/projected-CUR semantics, reject pre-existing outputs, and
never use `rss_quota_cur_selection.py` as final selection.
