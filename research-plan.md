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
Decide and freeze the phase list before D0/M0 evaluation:

```text
W:  at least the user-approved bcc reference; optional transfer phases
Ta: at least the user-approved bcc reference; optional transfer phases
Ti: at least the user-approved hcp reference; optional transfer phases
```

The phase list must be physically motivated from the supplied structures. For
Ti, explicitly decide whether the EOS is fixed-shape static, or includes a
defined constrained relaxation of `c/a`/internal degrees of freedom. DFT and
NNAP must evaluate exactly the same structures.

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

Before committing seed parameters, declare seed supercell, number of
structures, scale factors, displacement magnitude, target atom count, and
minimum-distance limits. The Al 32-atom, five-scale, 100-structure example
is not an automatic W/Ta/Ti default.

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

For each approved round `k >= 1` and each element:

```text
D(k-1) -> Mk-1
-> matched NVT or NPT candidate trajectories
-> full-committee all-frame uncertainty scoring
-> calibrate U parameters and physical gates
-> absolute-U projected-CUR selection
-> Protocol-A VASP labels
-> Dk -> Mk -> Ek
```

Use explicit stage commands and paths. The automatic `src/ase_md.py` workflow
does not implement this selection policy and its temperature table is intentionally
empty; it is not a production entry point here.

### 6.1 Sampling design gate

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

### 6.2 Calibration and selection

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

### 6.3 DFT, merge, and retraining gates

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

## 7. RSS Extension (Only After MD Selection Is Validated)

RSS is optional and requires separate approval. Generate and minimize an
element-specific pool with the current committee, score the full pool, apply
a calibrated absolute-U window/tail policy and physical gates, then use
current-DB-projected CUR with explicit source and atom-count quotas. Do not
silently replace this with percentile layers. Validate RSS geometry,
minimization outcome, provenance, atom-count distribution, and DFT risk before
labeling.

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
