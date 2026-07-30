# Research Plan: W, Ta, and Ti Unary NNAP Potentials

## 1. Scope

This workspace trains three independent unary potentials:

```text
W only:  W-potential/
Ta only: Ta-potential/
Ti only: Ti-potential/
```

It is not a W-Ta-Ti alloy workflow. W, Ta, and Ti never share a structure,
DFT label, ASE database, committee model, MD/RSS trajectory, selection pool,
VASP work directory, EOS reference, or `current.db`.

Every element follows the same version convention:

```text
D0 -> M0 -> E0 -> D1 -> M1 -> E1 -> D2 -> M2 -> E2 -> ...
```

where `Dk` is the training database, `Mk` is the committee trained from it,
and `Ek` is the fixed-EOS validation of that committee.

EOS structures and labels are validation-only. They must never enter an
element training database.

## 2. Execution Model

The normal workflow is a configured staged pipeline, not a sequence of manual
acceptance gates:

```text
configure one element/stage
-> submit the expensive stage through SLURM
-> automatically validate required outputs
-> continue to the next stage
```

The workflow stops only on a hard failure:

- a required input or output path is missing;
- an output path would be overwritten without explicit permission;
- a DFT label, structure, cell, force, stress, or model result is non-finite;
- an element-local path contains another element;
- a database/model/EOS version mapping is incomplete.

Normal EOS results are recorded for comparison. They are not a repeated manual
approval step. `E0` is the baseline against which `E1`, `E2`, and later
results are compared.

## 3. Non-Negotiable Selection Policy

Every active-learning selection uses this exact chain:

```text
current committee
-> score every production frame
-> calibrated absolute-U lower cutoff
-> periodic minimum-distance and abnormal-local-void gates
-> current.db-projected CUR
-> capped extreme-U tail
-> DFT labels
```

Do not replace this with global Top-K uncertainty selection, uncertainty-bin
quotas, final quota-CUR, or an unprojected CUR calculation.

`src/stratified_uncertainty_selection.py` may be used to score all frames and
write `uncertainty_all_frames.csv`, but its percentile-bin candidates are not
the final DFT set. Final selection uses
`src/absolute_u_projected_cur_selection.py`.

The current element/model/pool determines `U_min`, DFT budget, and CUR
parameters. They are recorded with the round; they are not copied from Al or
another element.

Candidate/final temporal frame gaps are disabled unless explicitly approved
for a later round. Structural redundancy is controlled by projection against
the element-local `current.db` and the final descriptor-similarity check, not
by frame number.

## 4. Directory, Version, and Provenance Convention

For element `<X>` in `W`, `Ta`, or `Ti`:

```text
<X>-potential/
  00-input/
  current.db                              # D(k-1) before a round
  model_versions/
    M0_from_D0/train-committee/
    Mk_from_Dk/train-committee/
  01-nvt-round-1/
  02-nvt-round-2/
  03-npt-round-1/
  04-npt-round-2/
  05-rss-round-1/
  06-rss-round-2/

results/<X>_eos_benchmark/
  eos_reference/
  db_snapshots/
  evaluations/E0_M0/
  evaluations/Ek_Mk/
```

For each state transition, retain:

```text
base/current DB checksum and row count
new-label DB checksum and row count
updated DB checksum and row count
committee model hashes
SLURM job IDs
exact command and parameter values
selection provenance
EOS reference checksum and Ek result paths
```

The only operation that changes `<X>-potential/current.db` is a successful
merge of `D(k-1)` and the element-local labeled set `Lk`.

## 5. DFT Protocols

### 5.1 Protocol A and Protocol B

Each element has two frozen DFT protocols:

```text
Protocol A: active-learning seed and selected-structure labels
Protocol B: fixed EOS-reference labels
```

The following are recorded for each protocol:

```text
element and PAW setup/variant
POTCAR checksum and ENMAX
VASP version
XC functional
ENCUT policy and convergence evidence
KPOINTS/KSPACING policy and convergence evidence
smearing method and width
ISPIN, initial MAGMOM, and final magnetic-state policy
SOC inclusion/exclusion decision
EDIFF and all INCAR overrides
static/ionic/cell-relaxation policy
energy, force, and stress units
```

W and Ta require an explicit semicore/valence and SOC decision. Ti requires
an explicit valence and spin-policy decision. A Protocol A/B mismatch is
allowed only when its energy/atom, force, and stress difference has been
quantified on an overlap set and recorded.

`ENCUT = 1.3 * max(ENMAX)` and `KSPACING = 0.2` are backend starting values,
not universal production values. The active Protocol A and fixed Protocol B
used for existing W/Ta/Ti data must not be changed retroactively. Any
convergence test or future protocol change creates a separately named,
documented protocol; it does not silently relabel an existing state.

### 5.2 DFT Input and Output Rules

User-supplied structures belong below `structures/`. Locally licensed PAW
files belong below `POTCAR/PBE/<X>/POTCAR` and are never committed or copied.

All new DFT labels use:

```text
src/vasp_batch_dft.py
scripts/slurm/run_vasp_batch_dft.slurm
```

The legacy `nncalc` path is not a production labeling route.

For a DFT batch, record:

```text
input POSCAR directory
output ASE DB
VASP work directory
Protocol A or B identifier
MAGMOM, KSPACING, ENCUT, and INCAR overrides
cores per VASP task and concurrent-task count
SLURM allocation and job ID
```

Before publishing a label DB, automatically require:

```text
one successful VASP task per input structure
finite energy, forces, and stress
unary expected composition
expected atom-count range
output DB row count equals completed task count
```

## 6. Fixed EOS Validation

### 6.1 Fixed Reference

The EOS reference is generated once, Protocol-B labeled once, and reused
unchanged for `E0`, `E1`, and every later validation.

| Element | Primary phases | Diagnostic phases |
|---|---|---|
| W | bcc | fcc, hcp |
| Ta | bcc | fcc, hcp |
| Ti | hcp, bcc | fcc |

The EOS definition is static unless an explicit constrained-relaxation
definition is frozen first:

```text
uniformly scale cell vectors
keep fractional coordinates fixed
keep cell shape fixed
keep Ti hcp c/a fixed
evaluate identical structures with DFT and NNAP
```

The established reference uses 19 fixed uniformly spaced scale points per
phase. Its exact structure metadata, DFT databases, and CSV checksum are the
reference identity. Do not alter the grid after E0.

### 6.2 EOS Generation and Collection

Generate with explicit paths:

```bash
python3 src/eos_reference.py generate \
  --structure <phase>=structures/<X>_benchmark/<X>-<phase>.poscar \
  --output-dir results/<X>_eos_benchmark/eos_reference \
  --metadata results/<X>_eos_benchmark/eos_reference/eos_structures.csv
```

Label each phase through the Protocol-B VASP batch workflow, then collect with
an explicit validation DB list:

```bash
python3 src/eos_reference.py collect \
  --metadata results/<X>_eos_benchmark/eos_reference/eos_structures.csv \
  --dft-db <phase>=<phase-reference.db> \
  --output-csv results/<X>_eos_benchmark/eos_reference/eos_reference.csv
```

The EOS DBs and CSV remain under `results/<X>_eos_benchmark/`; they are never
passed to merge or copied into `current.db`.

### 6.3 EOS Metrics

For each `Mk`, select an eligible committee member using its final
train/test diagnostic, then evaluate it on the unchanged fixed reference with
`src/eos_check_jnn.py` and `src/eos_predict_jnn.groovy`.

Record per phase and aggregate:

```text
raw energy MAE, RMSE, and maximum absolute error
phase-aligned relative energy MAE, RMSE, and maximum absolute error
DFT and NNAP grid-minimum scale and volume/atom
optional fitted equilibrium volume/lattice parameter/bulk modulus
selected JNN path, hash, and train/test diagnostic
```

The phase-aligned relative quantity is:

```text
[E_NNAP(V) - min(E_NNAP)] - [E_DFT(V) - min(E_DFT)]
```

Train/test error selects a reporting model; it does not replace the EOS
metric. The scientific comparison is `E1` versus `E0`, then `Ek` versus both
`E(k-1)` and `E0`.

## 7. Baseline: D0 -> M0 -> E0

The completed baseline design for each element is:

| Parameter | Value |
|---|---|
| seed supercell `seed_rep` | `2 2 2` |
| repeated-cell atom count | 16 |
| structures per scale | 20 |
| D0 linear scales | `0.90, 0.95, 1.00, 1.05, 1.10` |
| position disturbance | `0.03` |
| D0 structures per element | 100 |
| committee size | 10 |
| train/test folds | 10 disjoint 90/10 folds |

The baseline sequence is:

```text
<X>-seed.poscar
-> nninit controlled perturbations
-> Protocol-A VASP labels
-> <X>-potential/current.db = D0
-> M0 committee
-> fixed Protocol-B EOS = E0
```

The D0 population is checked for unary composition, 3D PBC, finite positions,
positive cell volume, finite minimum distance, and finite DFT results before
it becomes `current.db`.

The completed D0 record above used the original two-atom seed cells with
`seed_rep = 2 2 2`. The current `W`/`Ta`/`Ti` seed POSCARs are their explicit
16-atom `2 x 2 x 2` supercells. Future sampling started from these seed files
must use `--rep 1 1 1` to retain a 16-atom cell; `--rep 2 2 2` would create a
128-atom cell and requires an explicit new parameter card.

`E0` is the required baseline record. A poor but complete E0 remains useful:
later rounds test whether the selection process improves it.

## 8. Common Round Parameter Card

Before submitting one element-local stage, define its parameter card once and
record it with the command. It is not an extra approval gate.

### 8.1 Required Sampling Parameters

```text
element and round name
input DB checksum and M(k-1) JNN hashes
starting POSCAR/phase
ensemble: NVT, NPT, or RSS
supercell repetition (`1 1 1` for the current 16-atom seed POSCARs)
temperature
NVT scale factors or NPT pressures
steps, timestep, equilibration fraction, write interval, log interval
HAL tau_r and thermostat/barostat settings
random seed only for deterministic debugging when supported by the worker
all JNN paths
SLURM resources and expected output paths
```

The normal MD runner is:

```text
scripts/slurm/run_md_round.slurm
src/md_worker.py
```

It requires explicit `--rep`, NVT scale factors or NPT pressures, a
temperature, and all committee JNN paths. The selected best JNN from EOS is
not used alone for active-learning MD.

### 8.2 MD Implementation Starting Values

The current worker defaults are execution starting values and must be recorded
when used:

| Parameter | NVT/NPT worker default |
|---|---:|
| timestep | 1.0 fs |
| steps | 50,000 |
| write interval | 10 steps |
| log interval | 1 step |
| HAL `tau_r` (NVT and NPT) | 0.10 |
| NVT Langevin friction | 0.02 fs^-1 |
| NPT thermostat time | 75 fs |
| NPT barostat time | 75 fs |
| NPT bulk modulus for `pfactor` | 100 GPa |
| NPT `frac_traceless` | 0.00 |

The detailed stage configuration overrides a default only by passing the
explicit value on the command line. The current 16-atom seed POSCARs require
`--rep 1 1 1` for a 16-atom production cell; use `--rep 2 2 2` only after
explicitly approving a 128-atom calculation. Temperature, scale grid,
pressure grid, trajectory length, and DFT budget remain element- and
stage-specific.

### 8.2.1 Frozen Clean-FCC D2 NVT Cards

For the active clean-FCC restart only, `02-nvt-round-2` samples the matching
32-atom seed with `--rep 1 1 1`, the full matching ten-model M1 committee,
and its matching 200-row D1 `current.db`. The D2 cards are:

| Element | Temperature (K) | NVT scale factors | Rationale |
|---|---:|---|---|
| W | 4051.465 | `0.95, 1.00, 1.05, 1.10, 1.15` | A new grid that extends the expanded region; 64 of 100 D1 labels came from scale 1.10. |
| Ta | 3596.065 | `0.90, 0.925, 0.95, 0.975, 1.00` | A new intermediate grid restricted to the D1 geometry-safe 0.90--1.00 window. |
| Ti | 2135.265 | `0.95, 0.975, 1.00, 1.025, 1.05` | A new intermediate grid restricted to the D1 geometry-safe 0.95--1.05 window. |

All cards use 50,000 steps, a 1.0 fs timestep, trajectory/log intervals of
10/1 steps, HAL `tau_r=0.10`, Langevin friction `0.02 fs^-1`, one node with
five one-core tasks, and a 24-hour allocation. Retain the D1 temperature to
isolate the required new scale-grid change and test the M1 improvement. The
severe D1 Ta/Ti collapse evidence does not relax later D2 geometry gates:
all-frame uncertainty, absolute-U, geometry-first projected-CUR, and DFT
quantities must be recalibrated independently from each D2 pool. EOS
references remain validation-only and are not inputs to D2.

### 8.2.2 Frozen Clean-FCC D2 Selection Cards

The D2 geometry-audit jobs W `13465`, Ta `13466`, and Ti `13467` completed
with exit `0:0`. Each protected `geometry_audit.csv` exactly covers its
post-equilibration, post-`U_min` production frames and records finite,
periodic minimum-distance and normalized-empty-sphere values. The audit cards
and frozen projected-CUR selection cards are:

| Element | `U_min` (eV/A) | Post-`U_min` / geometry-valid | `U_tail` p99 (eV/A) | `N_DFT` / tail cap |
|---|---:|---:|---:|---:|
| W | 0.166580000 | 22,505 / 12,813 | 1.582394200 | 100 / 5 |
| Ta | 0.144480000 | 22,497 / 21,403 | 2.762254279 | 100 / 5 |
| Ti | 0.110986000 | 22,474 / 19,420 | 0.872469347 | 100 / 5 |

`U_min` is the required arithmetic mean of the matching ten M1 final
test-force MAEs. `U_tail` is the linear-interpolated p99 of only the
geometry-valid audit records. The 100-label D2 budget is independently
bounded to half of the matching 200-row D1 state and by the matching
geometry-valid candidate count; all three pools exceed that bound by more
than two orders of magnitude. It is not inherited from a D1 selection card.
The tail cap is therefore `floor(0.05 * 100) = 5`.

Every D2 CUR run must pass `--candidate-frame-gap 0 --final-frame-gap 0`,
`--tail-quantile 0.99`, its matching `--tail-max 5`,
`--min-distance` and `--max-normalized-void` values from section 10.2, and
the descriptor card `r_c=6.0`, `n_max=5`, `l_max=6`, similarity `0.99999`.
Do not pass force, volume, source-balance, or require-all-source gates. W's
scale `1.15` has no geometry-valid record under the frozen void limit; this
is an auditable outcome, not a reason to relax the gate or add a source
constraint.

### 8.2.3 Frozen Clean-FCC D3 NPT Cards

The user explicitly authorizes all-element clean-FCC D3 despite the
E0/E1/E2 review hold. `03-npt-round-1` therefore samples only the matching
32-atom clean-FCC seed with `--rep 1 1 1`, its matching 300-row D2
`current.db` as the protected state guard, and all ten matching M2 models.
The normal-pressure high-temperature targets from section 8.3 are an explicit
D3 choice; they do not inherit the D2 NVT cards. The one common, explicitly
authorized starting pressure grid is `1, 5, 10, 20, 30, 40, 50` GPa:

| Element | D3 root | Seed | Temperature (K) | M2 committee |
|---|---|---|---:|---|
| W | `W-potential/fcc-restart/03-npt-round-1/` | `structures/W_fcc_restart/W-fcc-seed-32.poscar` | 4928.15 | `W-potential/fcc-restart/model_versions/M2_from_D2/train-committee/` |
| Ta | `Ta-potential/fcc-restart/03-npt-round-1/` | `structures/Ta_fcc_restart/Ta-fcc-seed-32.poscar` | 4485.65 | `Ta-potential/fcc-restart/model_versions/M2_from_D2/train-committee/` |
| Ti | `Ti-potential/fcc-restart/03-npt-round-1/` | `structures/Ti_fcc_restart/Ti-fcc-seed-32.poscar` | 2750.65 | `Ti-potential/fcc-restart/model_versions/M2_from_D2/train-committee/` |

For each row, the complete ordered committee is exactly
`train-0/0.jnn`, `train-1/1.jnn`, ..., `train-9/9.jnn` below the listed
element-local committee root. Every card passes each of those paths
explicitly to the runner; no selected EOS model or cross-element model may
substitute for the committee.

All three cards use 50,000 steps at 1.0 fs, trajectory/log intervals `10/1`,
HAL `tau_r=0.10`, `ttime=75.0` fs, `ptime=75.0` fs, bulk modulus
`100.0` GPa (to derive `pfactor`), and `frac_traceless=0.0`. The runner is
submitted with one node, seven exclusive one-core tasks, and 24 hours, one
task for each pressure. A finite energy/force/(6,) stress and NPT-constructor
preflight is mandatory for every one of the 30 models before submission.
The pressure span provides the requested compression/volume exploration for
the W/Ta bcc-focused review; Ti proceeds only because of the user's explicit
override. D3 authorization does not authorize scoring, selection, DFT,
database merge, M3, or E3. EOS references remain validation-only.

### 8.2.4 Frozen Clean-FCC D3 Combined Selection Cards

After all 21 D3 NPT sources passed validation, the user explicitly approved
an element-local D3 target of 100 structures for W, Ta, and Ti. Each card
uses `scripts/slurm/run_md_selection_pipeline.slurm` once, with its matching
300-row D2 `current.db`, full ten-model M2 committee, and pressure grid
`1, 5, 10, 20, 30, 40, 50` GPa. It retains all-frame scoring, a complete
geometry audit, current.db-projected CUR, and final POSCAR provenance; it
does not authorize the subsequent DFT, merge, M3, or E3 stages.

| Element | `U_min` preflight (eV/A) | Target / tail cap | `d_min` (A) | Maximum normalized void | M2 committee |
|---|---:|---:|---:|---:|---|
| W | 0.187770000 | 100 / 5 | 1.695596956 | 0.946305262 | `W-potential/fcc-restart/model_versions/M2_from_D2/train-committee/` |
| Ta | 0.167500000 | 100 / 5 | 1.775316838 | 0.942271015 | `Ta-potential/fcc-restart/model_versions/M2_from_D2/train-committee/` |
| Ti | 0.117740000 | 100 / 5 | 1.775270170 | 0.946161232 | `Ti-potential/fcc-restart/model_versions/M2_from_D2/train-committee/` |

Each `U_min` is independently re-derived by the pipeline from the final
test `MAE-F` values of exactly `train-0/0.jnn` through `train-9/9.jnn`,
recorded with all ten model/log paths, and is not copied from D2. The
distance and void limits are the matching fixed clean-D0 `0.80*d_min` and
`1.15*q_void` gates. The descriptor card is `r_c=6.0`, `n_max=5`,
`l_max=6`, and similarity `0.99999`. Candidate/final frame gaps are zero;
do not pass source quotas, force, volume, or pressure hard gates. The runner
fixes the tail rule to linear p99 and `floor(0.05 * 100) = 5`.

Each independent submission uses one node, one task, 24 hours, and writes
only below its own `03-npt-round-1/` root:

```text
uncertainty_all_frames.csv
geometry_audit.csv
absolute-u-projected-cur/
slurm_logs/selection-u-min-<jobid>.txt
slurm_logs/combined-*-command-<jobid>.sh
```

All outputs must be absent before submission; no overwrite option is
permitted. The preflight validates the matching DB checksum/300 rows, exact
ten M2 JNN digest/logs, seven validated trajectories, absent D3 selection and
later-stage paths, and isolation from the other two elements.

### 8.3 Temperature Reference Data

`src/temperature_table.py` records these normal-pressure phase-change
reference values:

| Element | Melting point | Boiling point |
|---|---:|---:|
| W | 3683.15 K | 6173.15 K |
| Ta | 3269.15 K | 5702.15 K |
| Ti | 1941.15 K | 3560.15 K |

They were transcribed on 2026-07-24 from the peer-reviewed melting- and
boiling-point records in PubChem PUG View (CIDs 23964, 23956, and 23963,
respectively). `make_temperatures()` deliberately generates a high-temperature
liquid/near-liquid exploration target between those two limits. For one
high-temperature MD round, the default targets are:

| Element | `make_temperatures([X], 1)` target |
|---|---:|
| W | 4928.15 K |
| Ta | 4485.65 K |
| Ti | 2750.65 K |

These are the standard temperatures for the first high-temperature NVT round
unless the element-local parameter card explicitly overrides them.

The NVT source grid is:

```text
0.90, 0.95, 1.00, 1.05, 1.100
```

The standard high-temperature NVT source grid is exactly this list. For NPT,
a starting pressure list may be:

```text
1, 5, 10, 20, 30, 40, 50 GPa
```

but it is not used until finite stress from every committee model is
available. The staged SLURM runner uses `--bulk-modulus-gpa 100.0` by default;
this is a barostat response parameter for exploratory sampling, not the
imposed NPT pressure.

HAL-biased trajectories are active-learning exploration trajectories. The
committee-average energy and stress are diagnostic values; these trajectories
are not used to report equilibrium thermodynamic properties.

### 8.4 Automatic MD Output Check

Every source must produce:

```text
<round>/md/<source>/command.sh
<round>/md/<source>/log
<round>/md/<source>/multi_nnap_md.xyz
<round>/md/<source>/energy_forces_summary.dat
```

Before all-frame scoring, require readable trajectories with finite positions,
cell, volume, energy, and forces. NPT additionally requires finite stress and
pressure diagnostics. Failed sources are fixed or rerun; they are not silently
excluded from a completed source grid.

## 9. RSS Candidate Generation

RSS is used in stages 05 and 06, after the required NVT/NPT stages. Its
element-local parameter card records:

```text
element
atomic volume
natoms list
Mini pressure list in bar (`0, 200000, 400000` = `0, 20, 40 GPa`)
number of raw structures per source
RSS sampling JNN path and all M(k-1) committee paths for later scoring
minimization settings
source and atom-count constraints
expected pool and output paths
```

Use:

```text
src/rss_sampling_embedded.py
```

RSS structures first pass finite-geometry and minimization/provenance checks.
Their full pool is then scored with the current committee. RSS selection uses
the same absolute-U then current-DB-projected CUR policy as MD; it does not
use uncertainty-bin or quota selection. Do not use
`src/rss_quota_cur_selection.py` as the final RSS selector.

For unary RSS, the current default `natoms` list is:

```text
9, 10, 12, 15, 18, 20, 22, 25
```

RSS and exploratory MD deliberately do not require a fixed random seed. Their
purpose is broad candidate generation; provenance records commands, model
hashes, inputs, and generated outputs rather than attempting bitwise-repeat
random trajectories.

### 9.1 Explicit Logged-Mini-Failure Partial-Pool Exception

The default RSS acceptance gate requires complete raw/minimized provenance.
It may be relaxed only by an explicit per-element/per-round approval when a
retained JSE Mini log has a final `LMP FAIL LIST`. The approved scorer input
must name that log and exclude exactly its `exit=1` `(raw structure, Mini
pressure)` pairs. It must write an exclusion artifact containing the log
checksum, source keys, paths, and observed failed outputs. Every nonfailed
source remains mandatory and must pass the normal unary, finite-geometry,
atom-count, Mini-pressure, and flat/minimized-byte-identity checks.

Never score or select a logged Mini failure, infer additional exclusions, or
silently accept unlogged missing/mismatched structures. The all-ten-model
uncertainty, absolute-U, geometry, current-DB-projected CUR, and capped-tail
policy are unchanged; the fixed DFT target is permitted only when the valid
remainder has sufficient geometry-valid candidates. The D5 Ta `M4` pool
generated by job `13586` is the currently approved application: 60 logged
Mini failures are excluded, leaving 1,140 valid candidate structures for the
unchanged target of 100.

## 10. All-Frame Scoring and Final Selection

### 10.1 Score Every Production Frame

For NVT/NPT:

```text
input:  <X>-potential/<round>/md/*/multi_nnap_md.xyz
models: all M(k-1) JNN files
output: <X>-potential/<round>/uncertainty_all_frames.csv
```

Use `src/stratified_uncertainty_selection.py` with explicit:

```text
--round-dir
--mode nvt or npt
--scales or --pressures
--jnn-glob
--trajectory-name
--equilibration-fraction
--all-frames-csv
```

The all-frame CSV is the final-selection input. It records at least:

```text
source label and source value
trajectory path and frame
uncertainty
volume/atom
maximum committee-mean force
instant pressure when available
equilibration-discard flag
```

### 10.2 Geometry Gates

After removal of equilibration frames and the element-local absolute-U lower
cutoff, reconstruct every candidate frame and apply only these ordinary
physical hard rejections:

```text
minimum pair distance under periodic boundary conditions
normalized maximum local empty sphere under periodic boundary conditions
```

For element `<X>`, set the minimum-distance limit from only the matching
clean D0 database:

```text
d_min >= 0.80 * min_D0(d_min)
```

Define the local-void statistic using the maximum Delaunay-tetrahedron empty
sphere over the periodic cell:

```text
q_void = R_void,max / (V / N)^(1/3)
q_void <= 1.15 * max_D0(q_void)
```

The D0 minimum/maximum values and resulting limits are recalculated and
recorded independently for every element. Normal lattice interstices are not
void failures. A targeted vacancy, pore, crack, or other intended cavity
requires a separately approved reference set; it must not be silently
admitted by relaxing this gate. Finite values, positive cell volume, unary
composition, 3D PBC, and trajectory provenance remain mandatory validity
conditions. Force, total volume, pressure, and source composition are
auditable diagnostics rather than ordinary hard rejections.

### 10.3 Calibrate the Current Pool

Use the current sampling committee's final logged test-force errors together
with the saved production-frame CSV to determine and record:

```text
U_min                 committee-log-derived force-error threshold
N_DFT                 final label budget
CUR parameters        r_c, n_max, l_max, similarity policy
U_tail                p99 of geometry-valid candidate uncertainty
```

For every JNN used in the MD committee, read the final `MAE-F` test value
(the right-hand value in the logged `MAE-F: train | test` pair). Use the
arithmetic mean of these ten model-level test errors, convert it from meV/A
to eV/A, and use it directly as `U_min`, because `U` is also in eV/A. Change
this aggregation only with explicit approval. Record all model-log paths, the
ten final test `MAE-F` values, the aggregation rule, and the resulting numeric
`U_min`.

Do not determine `U_min` from an unlabeled MD-pool percentile and do not
substitute an additional DFT calibration-set procedure for this rule. The
arithmetic-mean force-error aggregate is recalculated independently for the
committee used in every element and every round; it is never copied from
another element or model version.

For the extreme-U risk layer, use the linear-interpolated p99 of the
geometry-valid candidate uncertainty distribution and cap final tail
structures at `floor(0.05 * N_DFT)`. This tail layer does not replace
`U_min`, does not impose a global Top-K selection, and must remain subject
to current.db-projected CUR and final duplicate checks.

Historical exception: the original D1 selection used the production-pool U
P95 rule. It was explicitly revoked and its selection, labels, successors,
and downstream M1/E1/D2 assets were removed. The replacement D1 selection
uses the committee-log force-error threshold rule above; it must not use the
historical P95 calibration.

### 10.4 Absolute-U Projected CUR

Run:

```text
src/absolute_u_projected_cur_selection.py
```

with:

```text
--round-dir <X>-potential/<round>
--all-frames <round>/uncertainty_all_frames.csv
--base <X>-potential/current.db
--output-root <round>/absolute-u-projected-cur
--u-min <U_min>
--target <N_DFT>
--tail-quantile 0.99
--tail-max <floor(0.05*N_DFT)>
--min-distance <0.80*min_D0(d_min)>
--max-normalized-void <1.15*max_D0(q_void)>
--r-c <r_c>
--n-max <n_max>
--l-max <l_max>
--similarity-threshold <threshold>
```

The selector:

```text
removes all U < U_min frames
removes only failed periodic distance/void geometries
projects descriptors against current.db
writes p99 tail provenance and caps the selected tail layer
writes final POSCARs and provenance
```

The descriptor starting values are:

```text
r_c = 6.0
n_max = 5
l_max = 6
similarity threshold = 0.99999
```

Change them only with a recorded descriptor-rank/coverage reason.

### 10.5 One-Submission MD Selection Pipeline

The separate score-only, geometry-audit, and CUR entry points remain available
for calibration, diagnosis, and recovery. Once an element-local selection card
has already fixed its DFT target, distance/void gates, and descriptor policy,
the three execution steps may instead run sequentially in one protected
allocation through:

```text
scripts/slurm/run_md_selection_pipeline.slurm
```

The pipeline requires an explicit element, round, base DB, exact ten-model
committee glob, source grid, target, geometry limits, and descriptor
parameters. It derives the required `U_min` only from the final test
`MAE-F` values of those ten model logs, writes the paths/ten values/mean to
`slurm_logs/selection-u-min-<jobid>.txt`, fixes tail policy at linear p99 and
`floor(0.05 * target)`, and enforces zero candidate/final frame gaps. It
first writes `uncertainty_all_frames.csv`, then `geometry_audit.csv`, checks
that the audit exactly covers the post-equilibration/post-`U_min` frames and
has at least the requested number of geometry-valid frames, and only then
starts the existing projected-CUR selector.

This is an execution convenience, not an automatic scientific policy. It must
not infer or loosen the DFT target, geometry limits, source policy, descriptor
policy, or use another element's inputs. It refuses existing all-frame, audit,
or CUR outputs and retains the same all-frame, audit, gate-rejection,
projected-CUR, tail, and final-POSCAR artifacts as the separate flow. It does
not authorize DFT, merge, training, or EOS evaluation.

## 11. DFT Label, Merge, Retrain, and EOS

For the selected set `Lk`:

```text
selected POSCARs
-> Protocol-A VASP batch
-> <X>_round-k_labeled.db = Lk
-> validate labels
-> merge D(k-1) + Lk = Dk
-> publish current.db = Dk
-> train Mk
-> fixed EOS evaluation = Ek
```

### 11.1 Label and Merge

Use separate, non-overlapping paths:

```text
base DB:       <X>-potential/current.db
new-label DB:  <X>-potential/<round>/<X>_round-k_labeled.db
updated DB:    <X>-potential/<round>/updated.db
```

Use `src/vasp_batch_dft.py` / `run_vasp_batch_dft.slurm` for labels and
`src/vasp_batch_dft.py merge` for the database transition.

Require:

```text
base/new/updated DB paths are different
all new labels are finite and unary
new-label row count equals completed VASP task count
Dk rows = D(k-1) rows + Lk rows
base rows remain before new rows
EOS data are absent from Dk
```

Only after these conditions pass is `updated.db` copied/published as the new
element-local `current.db`.

### 11.2 Retraining

Train only from `Dk`:

```bash
sbatch scripts/slurm/run_train_committee.slurm \
  <X>-potential/current.db \
  <X>-potential/model_versions/Mk_from_Dk/train-committee \
  10 5 5000
```

The completed M0 committees used the historical 1,000-epoch setting. The
replacement M1 committees and all later `Mk` committees use ten models, five
concurrent training workers, eight threads per worker, and 5,000 epochs.
Pass all four values explicitly in production submissions. This 5,000-epoch
policy is a documented training-design change and is not retroactive to M0.

Verify ten nonempty JNN files, disjoint folds, complete logs, and the expected
database row coverage.

### 11.3 EOS After Retraining

Evaluate `Mk` on the unchanged fixed Protocol-B reference:

```text
results/<X>_eos_benchmark/evaluations/Ek_Mk/
```

Compare `Ek` with `E(k-1)` and `E0`. Record whether EOS shape, phase-aligned
errors, raw cross-phase errors, and grid-minimum volumes improved, regressed,
or remained statistically unchanged.

## 12. Required Stage Order

The three elements follow this order independently:

| Stage | Input model | Candidate method | State produced |
|---|---|---|---|
| baseline | seed | perturbation + DFT + train + EOS | `D0 -> M0 -> E0` |
| 01-nvt-round-1 | `M0` | NVT scale grid + all-frame selection | `D1 -> M1 -> E1` |
| 02-nvt-round-2 | `M1` | new NVT scale grid + recalibration | `D2 -> M2 -> E2` |
| 03-npt-round-1 | `M2` | NPT pressure grid + finite-stress requirement | `D3 -> M3 -> E3` |
| 04-npt-round-2 | `M3` | new NPT pressure grid + recalibration | `D4 -> M4 -> E4` |
| 05-rss-round-1 | `M4` | RSS/Mini pool + full-pool selection | `D5 -> M5 -> E5` |
| 06-rss-round-2 | `M5` | new RSS/Mini pool + recalibration | `D6 -> M6 -> E6` |

Each completed row executes:

```text
sample -> automatic trajectory/pool validation -> all-frame scoring
-> current-pool calibration -> absolute-U cutoff -> current.db-projected CUR
-> Protocol-A DFT -> merge -> committee training -> fixed EOS
```

Do not skip from an NVT stage to NPT/RSS because another element reached that
stage. A failure affects only the element-local stage and its outputs.

## 13. Reporting and Scientific Interpretation

After every completed round, record:

```text
Dk/Mk/Ek identifiers and paths
new structure count and atom-count distribution
source-condition distribution
uncertainty distribution and calibrated U parameters
physical-filter rejections
DFT completion rate
committee training diagnostics
EOS raw/phase-aligned errors and minimum-volume comparison
```

The workflow is successful when added data improve or stabilize the fixed EOS
metric while remaining physically valid and computationally reproducible.

If EOS regresses, DFT is incomplete, MD becomes unstable, or the final set is
dominated by unsafe extreme-U structures, preserve the completed evidence and
adjust the next element-local stage configuration. Do not overwrite the
preceding database, model, trajectory, selection, or EOS result.
