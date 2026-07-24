# Research Plan: W, Ta, and Ti Unary NNAP Potentials

## 1. Scope and Non-Negotiable Separation

The deliverable is three independent unary potentials:

```text
W only:  W-potential/
Ta only: Ta-potential/
Ti only: Ti-potential/
```

This plan does **not** train a W-Ta-Ti alloy potential. Each element has its
own seed inputs, DFT protocol, PAW setup, D0/Dk databases, models, MD/RSS
candidate pools, selection outputs, VASP jobs, and EOS reference. No row,
structure, model, label cache, or generated output may be shared between
elements.

### 1.1 Difference from the completed Al study

The Al workspace was a *two-branch selection experiment* on one element:
two selection policies were compared from a common initial Al state, then
each branch maintained its own Dk/Mk/Ek history. Its fcc seed, 32-atom
design, NVT/NPT/RSS conditions, uncertainty cutoffs, label budgets, DFT
settings, reference energy, and EOS phases/results are Al-specific evidence,
not defaults.

WTaTi instead has three independent, single-policy unary loops:

```text
W:  D0 -> M0 -> E0 -> D1 -> M1 -> E1 -> ...
Ta: D0 -> M0 -> E0 -> D1 -> M1 -> E1 -> ...
Ti: D0 -> M0 -> E0 -> D1 -> M1 -> E1 -> ...
```

There is no Route 1/Route 2 comparison, no shared DFT union, and no shared
`current.db` in this workspace. A value must be calibrated separately for
the current W, Ta, or Ti committee; copying an Al value is prohibited.

If the intended deliverable is instead **one mixed W-Ta-Ti alloy potential**,
stop: this workspace is deliberately the wrong design. A ternary workflow
needs mixed-composition D0 structures/labels, composition-aware train/test
folds and selection quotas, alloy validation, and a different iteration
specification.

The active-learning selection policy is:

```text
committee-scored production frames
-> calibrated absolute-U lower cutoff
-> source-wise frame decorrelation
-> physical/risk gate
-> current.db-projected source-constrained CUR
-> approved extreme-U tail cap
-> DFT labels
```

## 2. Directory and State Convention

Use the following isolated paths, replacing `<X>` with `W`, `Ta`, or `Ti`.

```text
<X>-potential/
  00-input/
  model_versions/M0_from_D0/train-committee/
  01-nvt-round-1/
  02-npt-round-1/
  current.db

results/<X>_eos_benchmark/
  eos_reference/
  db_snapshots/
  model_versions/
  evaluations/E0_M0/
```

`current.db` is the state of only one element. `D0` is its initial DFT-labeled
database; `Dk = D(k-1) + labels(selected at round k)`. Preserve the
base rows before newly appended rows and record row counts, checksums, VASP
job IDs, model hashes, and selection provenance at every state transition.

EOS data are validation-only:

```text
results/<X>_eos_benchmark/eos_reference/*.db
results/<X>_eos_benchmark/eos_reference/eos_reference.csv
```

They must never be copied or merged into `<X>-potential/current.db`.

## 3. Gate 0: User Inputs and Frozen DFT Protocols

No seed generation, VASP, training, MD, RSS, or EOS calculation starts before
this gate passes separately for W, Ta, and Ti.

### 3.1 Required supplied assets

For each element, provide:

1. one ASE-readable unary seed structure;
2. a fixed set of unary EOS phase structures;
3. one locally licensed PAW-PBE `POTCAR` at `POTCAR/PBE/<X>/POTCAR`;
4. the intended PAW setup/variant name, checksum, and ENMAX;
5. the active-label and EOS-reference DFT protocols; and
6. an atomic reference energy consistent with the active-label protocol.

The expected input locations are documented in `README.md` and
`structures/README.md`. A structure must contain exactly the named element,
have a nonzero periodic three-dimensional cell, and pass cell/geometry checks.

### 3.2 Protocol A and Protocol B

Freeze two named protocols *for each element*:

```text
Protocol A: active-learning seed and selected-structure labels
Protocol B: fixed EOS-reference labels
```

Record the following for each protocol:

```text
element and intended PAW setup/variant
VASP version and POTCAR checksum
XC functional
ENCUT policy and convergence result
KPOINTS or KSPACING policy and convergence result
smearing method and width
ISPIN, initial MAGMOM, final magnetic-state policy
SOC inclusion/exclusion decision
all INCAR overrides, EDIFF, and static/relaxation policy
energy, force, and stress units and required outputs
```

W and Ta require an explicit choice of PAW valence/semicore treatment and SOC
policy. Ti likewise requires an explicit PAW valence choice and spin policy.
Do not infer any of these from the element name or reuse an Al setting. If
Protocol A and B differ, label a small overlap set with both and prove that
the energy/atom, force, and stress shifts meet declared tolerances before
training begins.

The VASP backend's `ENCUT = 1.3 * max(ENMAX)` and `KSPACING = 0.2` are only
implementation starting defaults, not approved W/Ta/Ti production settings.

### 3.3 Atomic reference-energy gate

`src/dbselectandtrain.py::ENERGY` currently contains historical W, Ta, and Ti
entries. Before any NNAP training, audit or replace them using isolated-atom
calculations from frozen Protocol A. Record the exact values and calculation
settings in the task record. Values from a different PAW setup, ENCUT,
spin/SOC policy, or VASP version must not be silently reused.

## 4. Fixed EOS Validation

EOS is the mandatory metric used to accept or reject each model version.
Every element has the following mandatory three-phase EOS validation set;
each listed phase must be uniformly scaled, Protocol-B labeled, and retained
in the fixed reference:

```text
W:  bcc (primary), fcc (diagnostic), hcp (diagnostic)
Ta: bcc (primary), fcc (diagnostic), hcp (diagnostic)
Ti: hcp and bcc (primary), fcc (diagnostic)
```

For Ti, explicitly decide whether the EOS is fixed-shape static, or includes
a defined constrained relaxation of `c/a`/internal degrees of freedom. DFT
and NNAP must evaluate exactly the same structures.

For every frozen phase:

1. choose a scale interval that brackets the DFT minimum;
2. use a fixed grid (19 uniformly spaced scales is a starting design only);
3. generate once with `src/eos_reference.py generate` and explicit
   `--structure label=path`, `--output-dir`, and `--metadata` paths;
4. label with Protocol B using `src/vasp_batch_dft.py` through SLURM;
5. collect `eos_reference.csv`; and
6. retain the metadata/DFT checksum for all E0, E1, ... comparisons.

For every Mk, record aggregate and per-phase:

- raw energy RMSE/MAE and maximum absolute error;
- phase-aligned relative energy RMSE/MAE;
- DFT and NNAP grid minimum volume;
- optional fitted equilibrium volume/lattice parameter and bulk modulus;
- selected committee model and its train/test diagnostic.

Committee fold metrics select an eligible candidate model, but never replace
the EOS metric. An iteration succeeds only if it improves the predeclared EOS
criterion without unacceptable DFT failures or MD instability.

## 5. Baseline: D0 -> M0 -> E0

Run this sequence independently three times.

```text
<X>-seed.poscar
-> controlled cell/position perturbations
-> Protocol-A VASP labels
-> D0/current.db
-> M0 committee
-> fixed Protocol-B EOS evaluation E0
```

The D0 seed design is fixed for W, Ta, and Ti:

| Parameter | Approved value |
|---|---|
| seed supercell (`seed_rep`) | `2 2 2` |
| repeated-cell atom count | 16 |
| structures per scale (`seed_nstructs`) | 20 |
| lattice scales (`seed_scales`) | `0.90, 0.95, 1.00, 1.05, 1.10` |
| position-disturbance amplitude (`seed_disturb`) | `0.03` |
| total generated seed structures | 100 per element |

Every supplied seed POSCAR contains two atoms, so `nninit` begins from a
16-atom repeated cell for every element. This design applies only to D0 seed
generation; production MD `--rep` values remain separate stage-specific
decisions. The seed generator exposes no numerical minimum-distance option:
an element-specific minimum-distance limit must therefore be set and checked
on the generated POSCAR population before Protocol-A DFT submission.

Use `scripts/slurm/run_vasp_batch_dft.slurm` for labels and
`scripts/slurm/run_train_committee.slurm` for committee training. Validate:

- every successful DB row has finite energy, forces, and stress;
- all rows contain only `<X>` and the intended atom-count range;
- every VASP task maps to one input POSCAR and has the frozen protocol;
- D0 row count equals completed labels;
- model folds are complete/disjoint and every committee `.jnn` is nonempty;
- the EOS reference has not changed and is not in D0.

`E0` must exist before active learning. A poor E0 can be a valid baseline;
an absent or inconsistent E0 is a stop condition.

## 6. Active-Learning Iteration

For each approved round `k >= 1` and each element, the state transition is:

```text
D(k-1) -> Mk-1
-> matched NVT or NPT candidate trajectories
-> full-committee all-frame uncertainty scoring
-> calibrate U parameters and physical gates
-> absolute-U projected-CUR selection
-> enforce physical/risk gate on the proposed DFT set
-> Protocol-A VASP labels Lk
-> validate Lk -> Dk -> Mk -> Ek -> continue/stop decision
```

Use explicit stage commands and paths. The automatic `src/ase_md.py` workflow
does not implement this selection policy and its temperature table is intentionally
empty; it is not a production entry point here.

### 6.0 Required macro schedule for each unary element

Each of W, Ta, and Ti follows the same **stage order** as the Al study. The
three elements execute it independently; stages never share trajectories,
labels, databases, committees, or EOS results.

| Stage | Sampling input | Candidate method | Required accepted output before next stage |
|---|---|---|---|
| Baseline | seed structures | controlled perturbations | `D0 -> M0 -> E0` |
| `01-nvt-round-1` | `M0`, approved NVT scale grid | MD all-frame score -> absolute-U projected CUR | `L1 -> D1 -> M1 -> E1` |
| `02-nvt-round-2` | `M1`, newly generated approved NVT scale grid | MD all-frame score -> recalibrated absolute-U projected CUR | `L2 -> D2 -> M2 -> E2` |
| `03-npt-round-1` | `M2`, approved NPT pressure grid | finite-stress gate -> MD all-frame score -> recalibrated selection | `L3 -> D3 -> M3 -> E3` |
| `04-npt-round-2` | `M3`, newly generated approved NPT pressure grid | finite-stress gate -> MD all-frame score -> recalibrated selection | `L4 -> D4 -> M4 -> E4` |
| `05-rss-round-1` | `M4`, approved RSS/Mini design | full-pool score -> calibrated absolute-U/physical gates -> projected quota-CUR | `L5 -> D5 -> M5 -> E5` |
| `06-rss-round-2` | `M5`, approved RSS/Mini design | full-pool score -> recalibrated absolute-U/physical gates -> projected quota-CUR | `L6 -> D6 -> M6 -> E6` |

The table fixes the **order**, not numerical settings. For every element and
every stage, independently approve the seed/phase, temperature, NVT scale
grid, NPT pressure grid, supercell, trajectory length, RSS atom-count/Mini
design, DFT budget, U thresholds, physical gates, and resource request. No
Al numerical setting transfers.

`01` begins only after accepted E0; `02` after E1; `03` after E2; `04` after
E3; `05` after E4; and `06` after E5. A failed gate stops that element at its
current state; it does not skip ahead to NPT or RSS.

### 6.1 Round contract: inputs, outputs, and decision

Do not treat an iteration as just “run MD again.” For a fixed element `<X>`
and round `k`, use the following named artifacts:

```text
input state:       D(k-1) = <X>-potential/current.db
input committee:   M(k-1) = model_versions/M(k-1)_from_D(k-1)/train-committee/
sampling output:   <X>-potential/<round-name>/md/*/
scoring output:    <X>-potential/<round-name>/uncertainty_all_frames.csv
selection output:  <X>-potential/<round-name>/absolute-u-projected-cur/
new labels:        <X>-potential/<round-name>/<X>_round-k_labeled.db = Lk
merged state:      <X>-potential/<round-name>/updated.db = Dk
new committee:     model_versions/Mk_from_Dk/train-committee/
fixed validation:  results/<X>_eos_benchmark/evaluations/Ek_Mk/
```

One round has exactly these eleven actions:

1. **Entry gate.** Verify `D(k-1)`, `M(k-1)`, and the fixed EOS reference
   checksum; confirm that the preceding `E(k-1)` was accepted. Record the
   committee hashes and the approved sampling/calibration sheet. Otherwise
   stop; do not sample.
2. **Sample.** Run one approved NVT *or* NPT source grid with every
   `M(k-1)` committee model. NVT varies only the approved scale sources; NPT
   varies only the approved pressure sources and first passes the all-model
   finite-stress gate. The trajectories belong to this element and this
   round only.
3. **Trajectory gate.** Check every source trajectory/log for finite
   positions, cell, volume, forces, and (for NPT) stress/pressure. A failed
   or unsafe source is diagnosed or rerun before uncertainty scoring; it is
   not silently omitted.
4. **Score all production frames.** Re-evaluate every non-equilibration frame
   with the full `M(k-1)` committee and save
   `uncertainty_all_frames.csv`. This file, rather than a percentile sample,
   is the input to final selection.
5. **Calibrate this round.** From this one committee/pool, record
   `U_min`, `U_tail`, `N_tail_max`, candidate/final frame gaps, DFT budget,
   source floor/ceiling quotas, descriptor settings, and numerical physical
   limits. This is a reviewed decision; U is not a transferable DFT-error
   threshold.
6. **Select novelty and coverage.** Use the saved all-frame CSV plus
   `D(k-1)` in the absolute-U, source-constrained projected-CUR selector.
   It keeps only `U >= U_min`, applies source frame gaps and balanced source
   quotas, projects descriptors against `D(k-1)`, and caps the extreme-U
   tail. It writes the proposed POSCARs and selection provenance.
7. **Physical/DFT-risk gate.** Apply the approved minimum-distance,
   volume/atom, cell-shape, maximum-force, pressure, and estimated k-grid
   limits to every proposed DFT POSCAR. The current generic selector checks
   finite geometry but does **not** invent these element-specific numerical
   limits. A rejected final POSCAR means stop and reselect with an auditable
   approved filter; never silently label a smaller or different set.
8. **Label only the approved set.** Submit one `<X>`-local Protocol-A VASP
   batch and write `Lk`; do not use EOS structures, another element's PAW
   file, another element's work directory, or a shared label DB.
9. **Validate and merge.** Check Lk task completeness, finite
   energy/forces/stress, unary composition, protocol provenance, and row
   count. Merge `D(k-1) + Lk` once to `Dk`; verify the row-count identity and
   atomically publish that exact Dk as `<X>-potential/current.db`.
10. **Retrain.** Train a new committee only from Dk. Verify all folds are
    disjoint/complete and every expected `.jnn` plus training log exists.
11. **Validate and decide.** Evaluate Mk on the unchanged Protocol-B EOS
    reference, producing Ek. Compare its predeclared aggregate/per-phase EOS
    metrics with E0 and prior E values, then record one of: **continue with
    round k+1**, **repeat/repair this round**, or **stop**. A worse EOS,
    unsafe geometry, incomplete DFT, or unstable MD never auto-advances.

The only mutation of `current.db` is action 9. `Lk`, `Dk`, `Mk`, and `Ek`
remain immutable evidence for why the next iteration was or was not approved.

### 6.2 Sampling design gate

Before each sampling submission, record:

```text
element, model hash, input structure/phase, ensemble,
temperature, NVT scale grid or NPT pressure grid,
steps, equilibration discard, write interval, random seed,
committee paths, HAL parameters, and expected output paths
```

NPT additionally requires finite committee stress for all models and an
approved bulk-modulus/barostat configuration. Do not use an NPT trajectory
until finite cell, stress, volume, and pressure diagnostics have been checked.
The user must supply/approve W-, Ta-, and Ti-specific temperature and pressure
ranges; `temperature_table.py` provides none.

### 6.3 Calibration and selection

First score **every** production frame using the current full committee.
`src/stratified_uncertainty_selection.py` can produce the required
`uncertainty_all_frames.csv`; do not use its percentile candidates for final
selection.

For the current `<X>, Mk-1` pool, determine and record:

```text
U_min                 calibrated absolute lower cutoff
U_tail, N_tail_max    extreme-tail threshold and final-count cap
g_candidate           same-source candidate frame gap
g_final               same-source final frame gap
N_DFT                 total label budget
source min/max        floor/ceil allocation over NVT scales or NPT pressures
physical gates        numerical thresholds and actions
CUR descriptor/projector settings
```

Committee uncertainty is a model-coverage signal, not a DFT force-error
estimate. Set `U_min` and the tail cap from the present committee distribution,
geometry/force diagnostics, and a small approved DFT audit where needed;
recalibrate after every retraining. Never reuse an Al or another element's
absolute-U numbers.

Select with:

```text
src/absolute_u_projected_cur_selection.py
```

using the current `<X>-potential/current.db` as `--base` and the saved
all-frame CSV as `--all-frames`. It enforces a lower U cutoff, source-balanced
floor/ceil quotas, candidate/final frame gaps, current-DB descriptor
projection, and a tail cap. Its basic finite-cell/position/minimum-distance
checks are not a substitute for numerical physical thresholds. Quarantine or
reject structures that fail the predeclared minimum-distance, volume/atom,
cell-angle, interplanar-height, maximum-force, pressure, or estimated k-grid
criteria before DFT submission.

The final selection directory must retain source, frame, U, maximum force,
volume/atom, physical-gate result, CUR rank/score, base similarity, model
hash, and calibration parameters.

### 6.4 DFT, merge, and retraining gates

For a selected set, use a separately named VASP input root, work directory,
log directory, new-label DB, and merged output DB for that element and round.
Before merging:

```text
new labels are finite and complete
new rows contain only the expected element
new-label row count equals completed VASP tasks
base/new/updated DB paths differ
Dk rows = D(k-1) rows + new-label rows
EOS data are absent from Dk
```

After training Mk, rerun the unchanged EOS reference. If EOS worsens, DFT
failure is excessive, candidate geometry is unsafe, or MD is unstable, stop
and diagnose rather than automatically starting round `k+1`.

## 7. RSS Stages: 05 and 06

RSS is the required post-MD part of this plan, not a replacement for either
NVT or NPT. Start `05-rss-round-1` only after E4 passes, then start
`06-rss-round-2` only after E5 passes. Each RSS stage retains the same
transaction:

```text
Mk -> element-local RSS generation and Mini minimization
-> validate pool geometry/minimization/provenance
-> full-committee scoring
-> calibrated absolute-U window/tail plus physical/DFT-risk gates
-> current-DB-projected quota-CUR with source and atom-count quotas
-> L(k+1) -> D(k+1) -> M(k+1) -> E(k+1)
```

RSS atom-count range, raw-structure count, Mini pressures, source/atom-count
quotas, U window/tail cap, and DFT budget are approved separately for each
`<X>, Mk` pool. Do not silently replace the calibrated absolute-U policy with
percentile layers, and do not run stage 06 merely because stage 05 completed:
E5 must accept it first.

## 8. Stop/Continue Rules

Continue an element only when all of the following are true:

1. DFT protocol and atomic reference energy are frozen and auditable;
2. its Dk and Mk validation gates pass;
3. the EOS reference is unchanged and validation-only;
4. selection calibration and physical gates are recorded for the current pool;
5. the EOS success metric improves or an explicitly approved scientific
   reason justifies the added data.

Stop and request review for any mixed-element asset, protocol mismatch,
non-finite label, invalid cell/stress, unbracketed EOS minimum, missing
provenance, unsafe high-U population, or EOS regression.
