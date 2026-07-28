# Notes: Clean FCC 2x2x2 Restart

## Sources

### Source 1: User instruction
- `2 2 2` means expansion in x, y, and z. The prior FCC workflow and its
  memory records were deleted and must not be reused.

### Source 2: Retained source structures
- `structures/W_benchmark/W-fcc.poscar`
- `structures/Ta_benchmark/Ta-fcc.poscar`
- `structures/Ti_benchmark/Ti-fcc.poscar`
- Each is the retained four-atom conventional FCC source for only its own
  element.

## Commands and Observations

### FCC cleanup

Cancellation requests were issued for FCC jobs `13372` through `13377`. A
final focused queue check found no remaining FCC job. The following prior
FCC-derived paths were then deleted:

```text
<X>-potential/fcc-restart/
<X>-potential/fcc-restart-2x2x2/
structures/<X>_fcc_restart/
structures/<X>_fcc_restart_2x2x2/
memory/28_fcc_restart_plan/ through memory/37_fcc_2x2x2_restart/
```

Post-deletion checks found no generated `fcc-restart` or `fcc_restart` path.
The protected D4 database hashes remain W
`d9d851b7e22ef2fdb84eeaa88d7822682e83a33f9de5eb91c188f92c2d0755bc`, Ta
`bce6490107a31f329bd89a30d7505c5e3665357a2f254afdc3e181cdf10698a0`, and
Ti `a68f2c8b4cd5e41788463566737fafa80e1e9b70a4c7a7006a953c57a922c6d2`.
All six fixed EOS metadata/reference hashes also match their recorded
identities.

## Synthesized Findings

- The clean restart has no D0 database, candidate pool, VASP work directory,
  committee, trajectory, selection, label, EOS prediction, or memory record
  inherited from the deleted FCC work.
- New seed validation must show 32 atoms and all three lattice-vector lengths
  exactly twice their respective retained four-atom source lengths.

### New seed construction and validation

Each fresh seed was written only after confirming that the new seed and
potential root paths were absent. It is an exact ASE `repeat((2, 2, 2))` of
only its matching retained source, with no additional transformation.

| Element | Source lengths (A) | Seed lengths (A) | Seed volume (A^3) | Minimum distance (A) | Seed SHA-256 |
|---|---|---|---:|---:|---|
| W | 3.991978500, 3.991978500, 3.991978500 | 7.983956999, 7.983956999, 7.983956999 | 508.925916812 | 2.822755067 | `43a64fcfafcd40792f69a8d51f3e73f8bee45bfcad84e8753e124c8a78a18d7c` |
| Ta | 4.171811608, 4.171811608, 4.171811608 | 8.343623215, 8.343623215, 8.343623215 | 580.850077277 | 2.949916278 | `76a07c56ec86b095195a4c0b7662385201f6ebb0175192d3dd2050092818b7b6` |
| Ti | 4.109149077, 4.109149077, 4.109149077 | 8.218298154, 8.218298154, 8.218298154 | 555.067346400 | 2.905607177 | `6072199ca77de8276f36c49e9beb4926b20c40ad271022e9df7aa912cdf136d1` |

Before atomic publication, each seed passed 32-atom unary composition,
3D-PBC, finite geometry, positive volume, positive minimum distance, exact
`2 * source_cell`, and exact wrapped-fractional-coordinate checks.

### D0 candidate-generation preflight

Under `module load jse`, `nninit` is available. Every new seed passes the
32-atom unary/PBC/finite/positive-volume check, and its matching
`<X>-potential/fcc-restart/` root and D0 pool are absent. The clean D0 card
uses no further supercell replication:

```bash
nninit <X> <X>-potential/fcc-restart/00-input/seed-generation/nninit-poscars \
  20 structures/<X>_fcc_restart/<X>-fcc-seed-32.poscar _ 1 1 1 \
  0.90,0.95,1.00,1.05,1.10 0.03
```

This creates 20 controlled perturbations at each of five scales, for 100
fresh 32-atom candidates per element.

### D0 candidate generation and validation

All three `nninit` commands completed successfully. Each pool contains exactly
100 consecutively named `<X>-00000.poscar` through `<X>-00099.poscar` files.
Every candidate is a unique, finite, unary, 3D-periodic 32-atom structure
with positive volume and minimum distance; no EOS or cross-element content is
present.

| Element | Volume/atom range (A^3) | Minimum-distance range (A) | Batch mean volumes/atom (A^3), scales 0.90 -> 1.10 | Ordered pool SHA-256 |
|---|---:|---:|---|---|
| W | 10.496816--22.888130 | 2.119496--2.906086 | 11.639258, 13.759711, 15.519430, 18.176808, 21.144842 | `b4524b7407e5fa9473ba9e450657b5b5c0b6494639042691724b6ce00e399c7d` |
| Ta | 11.757120--27.282647 | 2.219146--3.008631 | 13.333753, 15.588560, 18.134875, 21.061448, 24.387709 | `0a029dfa656f7360b200ebfa714100989aadc00ce360475329c5aeadbc57f484` |
| Ti | 11.150612--24.979403 | 2.219088--2.926410 | 12.591146, 14.731710, 17.528736, 19.586982, 22.862436 | `ba4c59ba7dd96bdac5ec801badcfe893707a2bd59666e6360839f8b8a7b17873` |

### D0 Protocol-A labeling preflight

The current `vasp_batch_dft.py label` CLI and the established static
Protocol-A card were checked. Each matching pool has 100 VASP5 POSCARs with
the expected unary `32`-atom header; the clean label DB, default VASP work
directory, clean FCC `current.db`, and scheduler-log directory are absent.
The current training reference energies are W `-12.9581`, Ta `-11.8578`, and
Ti `-7.8951` eV.

The first read-only preflight halted at Ti because its expected POTCAR
checksum was transcribed incorrectly in the validator. It created no output
and submitted no VASP job. The preflight will be rerun using the recorded
complete Ti checksum.

The rerun passed for all elements. The PAW SHA-256 / ENMAX / auto-ENCUT values
are W `c0897285...8170117 / 223.057 / 289.9741`, Ta
`b94d0231...3d269f3 / 223.667 / 290.7671`, and Ti
`f8e8f1d0...f5a1479e / 178.330 / 231.8290` eV. The retained D4 database
hashes remain unchanged.

The clean D0 labels use the frozen static Protocol-A settings:

```text
ISTART=0; ICHARG=2; PREC=Accurate; ALGO=Normal; EDIFF=1E-5; NELM=200
SIGMA=0.1; KSPACING=0.2; KGAMMA=.TRUE.; LASPH=.TRUE.; LREAL=Auto
ISYM=0; KPAR=1; NCORE=2; NSIM=6; IBRION=-1; NSW=0; ISIF=2
```

The no-overwrite submission card is one node, 64 tasks, 24 hours, eight VASP
ranks per calculation, and at most eight concurrent calculations. It makes
no partition, account, or GPU request:

```bash
sbatch --job-name=fcc_d0_<X> --nodes=1 --ntasks=64 --time=24:00:00 \
  --output=<X>-potential/fcc-restart/00-input/slurm_logs/fcc-d0-%j.out \
  --error=<X>-potential/fcc-restart/00-input/slurm_logs/fcc-d0-%j.err \
  scripts/slurm/run_vasp_batch_dft.slurm \
  <X>-potential/fcc-restart/00-input/seed-generation/nninit-poscars \
  <X>-potential/fcc-restart/00-input/<X>_FCC_D0_labeled.db _ 0.2
```

Neither `OVERWRITE` nor `FORCE_PREPARE` is set. The distinct default VASP
work directory is `00-input/dft/vasp_<X>_FCC_D0/`.

### Clean D0 Protocol-A submissions

After preflight, only the new required `00-input/slurm_logs/` directories
were created. The documented commands were submitted unchanged:

| Element | Job ID | Candidate input | Label DB output | Immediate status |
|---|---:|---|---|---|
| W | `13381` | `W-potential/fcc-restart/00-input/seed-generation/nninit-poscars/` | `W-potential/fcc-restart/00-input/W_FCC_D0_labeled.db` | `PENDING` |
| Ta | `13382` | `Ta-potential/fcc-restart/00-input/seed-generation/nninit-poscars/` | `Ta-potential/fcc-restart/00-input/Ta_FCC_D0_labeled.db` | `PENDING` |
| Ti | `13383` | `Ti-potential/fcc-restart/00-input/seed-generation/nninit-poscars/` | `Ti-potential/fcc-restart/00-input/Ti_FCC_D0_labeled.db` | `PENDING` |

One combined immediate `squeue` check was made after all three submissions.
No polling loop was started. No clean FCC D0 `current.db`, committee,
trajectory, selection, or EOS output exists yet.

### Clean D0 completion and label validation

On the user's completion report, one focused `sacct -X` check found all three
D0 batches terminally successful:

| Element | Job ID | State / exit | Elapsed |
|---|---:|---|---:|
| W | `13381` | `COMPLETED / 0:0` | 03:12:32 |
| Ta | `13382` | `COMPLETED / 0:0` | 02:47:21 |
| Ti | `13383` | `COMPLETED / 0:0` | 00:46:07 |

Read-only validation passed for every element:

- exactly 100 candidate POSCARs, manifest tasks, VASP task directories,
  successful run-summary tasks, complete OUTCARs, and labeled DB rows;
- exact source coverage and VASP5 unary 32-atom composition, matching only
  the element-local candidate pool;
- expected Protocol-A auto-ENCUT in every task metadata/INCAR;
- finite energy, `(32,3)` forces, and finite stress in every DB row;
- finite positive geometry and source/result agreement within
  `5.000e-09 A` in cell entries and fractional coordinates;
- no clean FCC `current.db` before publication; protected D4 DB hashes
  unchanged; no EOS content.

| Element | Label DB SHA-256 | Energy range (eV/32-atom cell) | Maximum force (eV/A) |
|---|---|---:|---:|
| W | `97079cfdf10c025c8887621b378940d18cb6fe9343432a1cc66917df5fb61a7e` | -399.837261230 to -266.735542030 | 11.243652100 |
| Ta | `250b1019aa284ad4623cce621f72f9e59b9a0e74dbd2c36bc09d9efc731c9995` | -370.518176610 to -270.976767980 | 7.224711850 |
| Ti | `37292ae7baaed45986cc03b51b7eb9dd1b918510f7dcd58a68837ee3ee407acd` | -245.138525990 to -201.378420900 | 3.151084180 |

### Clean D0 publication

Each validated label DB was copied to an agent-created same-directory
temporary `.tmp.db`, checksum and 100-row 32-atom contents revalidated, then
atomically renamed as only its matching clean FCC `current.db`. No target
existed before publication and no legacy D4 DB changed.

| Element | Published clean D0 `current.db` SHA-256 |
|---|---|
| W | `97079cfdf10c025c8887621b378940d18cb6fe9343432a1cc66917df5fb61a7e` |
| Ta | `250b1019aa284ad4623cce621f72f9e59b9a0e74dbd2c36bc09d9efc731c9995` |
| Ti | `37292ae7baaed45986cc03b51b7eb9dd1b918510f7dcd58a68837ee3ee407acd` |

### M0 committee preflight

Each published clean D0 database has exactly 100 finite unary 32-atom rows
and retains its matching label-DB checksum. The training reference energies
are still W `-12.9581`, Ta `-11.8578`, and Ti `-7.8951` eV. Every matching
`model_versions/M0_from_D0/train-committee/` root and outer FCC scheduler-log
directory is absent.

The no-overwrite M0 card uses ten models, five concurrent workers, 5,000
epochs, one node, five tasks, eight CPUs/task, and 48 hours:

```bash
sbatch --job-name=fcc_m0_<X> --nodes=1 --ntasks=5 --cpus-per-task=8 \
  --time=48:00:00 \
  --output=<X>-potential/fcc-restart/slurm_logs/fcc-m0-%j.out \
  --error=<X>-potential/fcc-restart/slurm_logs/fcc-m0-%j.err \
  scripts/slurm/run_train_committee.slurm \
  <X>-potential/fcc-restart/current.db \
  <X>-potential/fcc-restart/model_versions/M0_from_D0/train-committee \
  10 5 5000
```

No `OVERWRITE` setting is used. The scheduler-log directory is outside the
protected training directory, so the training template can create a new,
empty committee root.

### Clean M0 submissions

After preflight, only the new outer
`<X>-potential/fcc-restart/slurm_logs/` directories were created. The three
documented M0 commands were submitted unchanged:

| Element | Job ID | Training DB | Committee root | Immediate status |
|---|---:|---|---|---|
| W | `13395` | `W-potential/fcc-restart/current.db` | `W-potential/fcc-restart/model_versions/M0_from_D0/train-committee/` | `PENDING` |
| Ta | `13396` | `Ta-potential/fcc-restart/current.db` | `Ta-potential/fcc-restart/model_versions/M0_from_D0/train-committee/` | `PENDING` |
| Ti | `13397` | `Ti-potential/fcc-restart/current.db` | `Ti-potential/fcc-restart/model_versions/M0_from_D0/train-committee/` | `PENDING` |

One combined immediate `squeue` check was made after all submissions. No
polling loop was started. No M0 committee or E0 evaluation is yet validated.

On the user's later next-step request, one focused `sacct -X` check found W
`13395`, Ta `13396`, and Ti `13397` all `RUNNING 0:0` with about 1.5 minutes
elapsed. No polling loop was started.

### M0 completion and committee validation

On the user's completion report, one focused `sacct -X` check found all M0
jobs successful: W `13395` `COMPLETED 0:0` in 04:36, Ta `13396` `COMPLETED
0:0` in 04:16, and Ti `13397` `COMPLETED 0:0` in 04:06.

Read-only validation passed for all three committees:

- exactly ten nonempty `train-0` through `train-9` JNN, log, trainer,
  train-DB, and test-DB artifacts;
- `train.nepochs = 5000` in every trainer;
- ten disjoint 90/10 folds of only the matching clean 100-row FCC D0 DB,
  with every row once in test and nine times in train;
- only the matching unary 32-atom finite structures and results;
- finite final train/test `MAE-E` and `MAE-F` diagnostics; and unchanged
  clean FCC D0 and protected D4 DB hashes.

| Element | Test MAE-E range (meV/atom) | Test MAE-F range (meV/A) | Ordered model SHA-256 |
|---|---:|---:|---|
| W | 2.8970--8.8190 | 74.7100--98.7100 | `999a1896135a2448008176924cb6828af0bda39a4ae76adc139a06d256792246` |
| Ta | 1.9670--3.4710 | 50.8300--81.8900 | `8c4d0a734fd1394be62fd65962d38d05b349c9c95139b2742585076a4667082d` |
| Ti | 0.7126--1.9720 | 31.3500--44.7900 | `dd4518aa732d970862ce1cab10b35bedc51cb4b88199318bc9029c8ec546dc83` |

### E0 fixed-reference preflight

The current `eos_check_jnn.py` CLI and JSE runtime are available. W and Ta
passed read-only preflight using the unchanged 57-point fixed references:
19 each bcc/fcc/hcp rows, finite DFT energies, exact metadata/reference key
coverage, and absent clean E0 outputs. Ratio-filtered reporting candidates
are W 6/10 with `train-1/1.jnn` selected (train/test MAE-E 5.769/4.705
meV/atom), and Ta 9/10 with `train-5/5.jnn` selected (2.342/1.967
meV/atom).

The first preflight stopped before Ti selection because its expected metadata
checksum was transcribed incorrectly. It made no output; rerun with the
checksum read from the protected reference is required.

The corrected preflight passed for all three elements. Ti has 6/10 eligible
models and selects `train-5/5.jnn` with train/test MAE-E 1.035/0.848
meV/atom. The protected Ti metadata/reference hashes are
`3c11ea72890c9d0a1f336b7b609190b980fafdc8878c55d7af74d4cff0ad5ffb` and
`1a5f38ae444e9412c9bb0d5cfa5c15e0af89b1af3e1f675892276c6c3c93a541`.

The direct, no-overwrite E0 commands use only the fixed Protocol-B reference
and write only absent clean FCC-local outputs:

```bash
module load jse
python3 src/eos_check_jnn.py \
  --element <X> \
  --metadata results/<X>_eos_benchmark/eos_reference/eos_structures.csv \
  --reference-csv results/<X>_eos_benchmark/eos_reference/eos_reference.csv \
  --jnn-root <X>-potential/fcc-restart/model_versions/M0_from_D0/train-committee \
  --model-id E0_M0 \
  --output-dir <X>-potential/fcc-restart/evaluations \
  --max-train-test-ratio 1.25
```

### E0 execution

All three fixed-reference E0 evaluations completed successfully. JSE created
one local inference cache library beside each selected JNN, but did not
modify JNN model bytes, clean FCC `current.db`, legacy D4 assets, or EOS
references. The first read-only artifact validator then stopped only while
formatting an absolute selected-JNN path relative to an unresolved committee
path; it made no changes and will be rerun with normalized paths.

The corrected E0 artifact validator passed for W, Ta, and Ti:

- `jnn_selection.csv` has ten records and the stored selected JNN is the
  lowest eligible test-energy-MAE model under the 1.25 ratio filter;
- raw and DFT-merged prediction tables have 57 finite rows with exact
  19/19/19 bcc/fcc/hcp coverage;
- metric tables have finite bcc, fcc, hcp, and aggregate rows; both plots are
  nonempty;
- clean FCC D0 DBs retain 100 rows and their published hashes; all ten JNN
  hashes and all fixed EOS metadata/reference hashes remain unchanged.

| Element | Eligible / 10 | Selected M0 JNN | Train/test MAE-E (meV/atom) | Aggregate raw / aligned MAE (meV/atom) |
|---|---:|---|---:|---:|
| W | 6 | `train-1/1.jnn` | 5.769 / 4.705 | 131.064897 / 28.027437 |
| Ta | 9 | `train-5/5.jnn` | 2.342 / 1.967 | 16.182558 / 13.358162 |
| Ti | 6 | `train-5/5.jnn` | 1.035 / 0.848 | 36.024202 / 7.434641 |

### D1 NVT preflight

The active MD entry points were inspected: the staged runner requires
explicit `--rep`, creates one worker per source, and runs all supplied JNNs.
The NVT worker reads the seed, applies the stated `--rep`, then applies each
scale factor; it requires energy and forces but does not request stress.

`sbatch` and `srun` are available. Every clean seed is 32 atoms, periodic,
finite, and positive-volume; each clean D0 DB retains 100 rows; each matching
M0 committee has exactly the validated ten JNNs with its recorded digest; and
every new `01-nvt-round-1/` root is absent.

The approved D1 NVT card keeps the already-correct 32-atom cell with
`--rep 1 1 1`:

```text
ensemble = NVT
scale factors = 0.90, 0.95, 1.00, 1.05, 1.10
steps = 50000; timestep = 1.0 fs
write interval = 10; log interval = 1
HAL tau_r = 0.10; Langevin friction = 0.02 fs^-1
resources = one node, five exclusive one-core tasks, 24:00:00
```

| Element | Seed atoms | Seed volume (A^3) | Temperature (K) | M0 models |
|---|---:|---:|---:|---:|
| W | 32 | 508.925917 | 4928.15 | 10 |
| Ta | 32 | 580.850077 | 4485.65 | 10 |
| Ti | 32 | 555.067346 | 2750.65 | 10 |

The no-overwrite direct submission is:

```bash
sbatch --job-name=fcc_d1_<X> --nodes=1 --ntasks=5 --time=24:00:00 \
  --output=<X>-potential/fcc-restart/01-nvt-round-1/slurm_logs/fcc-d1-%j.out \
  --error=<X>-potential/fcc-restart/01-nvt-round-1/slurm_logs/fcc-d1-%j.err \
  scripts/slurm/run_md_round.slurm \
  --ensemble nvt \
  --round-dir <X>-potential/fcc-restart/01-nvt-round-1 \
  --poscar structures/<X>_fcc_restart/<X>-fcc-seed-32.poscar \
  --rep 1 1 1 --temperature <T_K> \
  --scale-factors 0.90 0.95 1.00 1.05 1.10 \
  --tau-r 0.10 --steps 50000 --timestep 1.0 \
  --write-interval 10 --log-interval 1 \
  --trajectory multi_nnap_md.xyz --summary energy_forces_summary.dat \
  --friction 0.02 --jnn-paths <all-ten-matching-M0-JNNs>
```

Only the outer `slurm_logs/` directory will be created before submission; no
round source directory, trajectory, DFT label, DB, model, or EOS asset is
overwritten.

### D1 NVT submissions

After the no-overwrite preflight, only the required clean round
`slurm_logs/` directories were created. The documented commands were
submitted with the exact corrected 32-atom POSCAR paths:

| Element | Job ID | Seed / rep | Temperature (K) | Immediate status |
|---|---:|---|---:|---|
| W | `13399` | `W-fcc-seed-32.poscar` / `1 1 1` | 4928.15 | `PENDING` |
| Ta | `13400` | `Ta-fcc-seed-32.poscar` / `1 1 1` | 4485.65 | `PENDING` |
| Ti | `13401` | `Ti-fcc-seed-32.poscar` / `1 1 1` | 2750.65 | `PENDING` |

One combined immediate `squeue` check was made after all three submissions.
No polling loop was started. D1 trajectories must produce five valid
32-atom sources per element before score-only uncertainty evaluation.

### D1 NVT completion and complete trajectory validation

On the user's completion report, one focused `sacct -X` check found the D1
jobs terminally successful:

| Element | Job ID | State / exit | Elapsed |
|---|---:|---|---:|
| W | `13399` | `COMPLETED / 0:0` | 01:21:34 |
| Ta | `13400` | `COMPLETED / 0:0` | 01:20:40 |
| Ti | `13401` | `COMPLETED / 0:0` | 01:21:14 |

Read-only validation passed for all five `scale-{0p9,0p95,1,1p05,1p1}`
sources per element. Every source contains `command.sh`, `log`,
`multi_nnap_md.xyz`, and `energy_forces_summary.dat`; its command uses only
the matching `<X>-fcc-seed-32.poscar`, `--rep 1 1 1`, stated scale, and all
ten matching M0 JNNs. Each trajectory has exactly 5,001 finite unary
32-atom frames, and each summary has exactly 50,001 finite rows spanning
steps 0 through 50,000.

| Element | Total frames | Volume/atom range (A^3) | Maximum absolute force (eV/A) |
|---|---:|---:|---:|
| W | 25,005 | 11.593969--21.168137 | 22.556446 |
| Ta | 25,005 | 13.232491--24.159733 | 1339.514984 |
| Ti | 25,005 | 12.645128--23.087332 | 2574.486865 |

The high Ta/Ti forces are finite and were retained. Later selection must
handle them transparently through documented, approved physical/risk gates;
no source or frame may be silently discarded.

### D1 all-frame score-only preflight

`research-plan.md` section 10 and `docs/source_function_index.md` identify
`scripts/slurm/run_uncertainty_scoring.slurm` with
`src/stratified_uncertainty_selection.py` as the required all-frame entry
point. The current template allocates one node, one task, and 24 hours;
loads `jse`; sets all relevant thread counts to one; rejects an existing
all-frame CSV; verifies each explicitly requested NVT trajectory; and appends
`--score-only` itself. It writes a per-job command record below the existing
round `slurm_logs/` directory. The scorer's score-only branch writes only
`uncertainty_all_frames.csv`, preserves all frame records, and does not make
percentile-bin candidate files, POSCARs, selection CSVs, or bin summaries.

The first direct Python CLI check failed only because the default login-shell
Python does not provide NumPy. The required runtime check passed:

```bash
module load jse && python3 src/stratified_uncertainty_selection.py --help
```

Read-only preflight found, for every element:

- the target `01-nvt-round-1/uncertainty_all_frames.csv` is absent;
- no prior uncertainty, score, candidate, or selection output exists below
  the D1 round;
- exactly five requested `md/scale-{0p9,0p95,1,1p05,1p1}/multi_nnap_md.xyz`
  inputs and exactly ten matching M0 JNN files exist;
- the JNN glob is constrained to only
  `<X>-potential/fcc-restart/model_versions/M0_from_D0/train-committee/train-*/*.jnn`;
- existing D1 `slurm_logs/` directories will receive scheduler and command
  records only. Neither `OVERWRITE` nor the scorer `--overwrite` flag is
  used.

The no-overwrite score-only submission card is one element per job, with no
partition, account, or GPU request:

```bash
sbatch --job-name=fcc_score_<X> --nodes=1 --ntasks=1 --time=24:00:00 \
  --output=<X>-potential/fcc-restart/01-nvt-round-1/slurm_logs/fcc-score-%j.out \
  --error=<X>-potential/fcc-restart/01-nvt-round-1/slurm_logs/fcc-score-%j.err \
  scripts/slurm/run_uncertainty_scoring.slurm \
  --round-dir <X>-potential/fcc-restart/01-nvt-round-1 \
  --jnn-glob '<X>-potential/fcc-restart/model_versions/M0_from_D0/train-committee/train-*/*.jnn' \
  --mode nvt --scales 0.90 0.95 1.00 1.05 1.10 \
  --trajectory-name multi_nnap_md.xyz \
  --all-frames-csv <X>-potential/fcc-restart/01-nvt-round-1/uncertainty_all_frames.csv \
  --equilibration-fraction 0.10 --progress-interval 500
```

The template adds `--score-only`; it must not be passed to the template as a
separate argument because the template parser does not accept it.

### D1 all-frame score-only submissions

After the no-overwrite preflight and final absence check, the three recorded
cards were submitted unchanged:

| Element | Job ID | Output | Immediate status |
|---|---:|---|---|
| W | `13413` | `W-potential/fcc-restart/01-nvt-round-1/uncertainty_all_frames.csv` | `PENDING` |
| Ta | `13414` | `Ta-potential/fcc-restart/01-nvt-round-1/uncertainty_all_frames.csv` | `PENDING` |
| Ti | `13415` | `Ti-potential/fcc-restart/01-nvt-round-1/uncertainty_all_frames.csv` | `PENDING` |

One immediate combined `squeue` query reported W with `(None)` and Ta/Ti
with `(Priority)` pending reasons. No polling loop was started. Each job can
write only its own absent all-frame CSV plus scheduler/command records in its
already-existing element-local D1 round.

### D1 all-frame score completion, validation, and U_min calibration

On the user's completion report, one focused `sacct -X` check found all three
score jobs terminally successful:

| Element | Job ID | State / exit | Elapsed |
|---|---:|---|---:|
| W | `13413` | `COMPLETED / 0:0` | 00:25:21 |
| Ta | `13414` | `COMPLETED / 0:0` | 00:24:53 |
| Ti | `13415` | `COMPLETED / 0:0` | 00:25:00 |

Each matching scorer log records five trajectories, ten committee models, and
`done: scored_frames=25005`. Read-only all-frame CSV validation passed:

- exactly the expected 20-column header and 25,005 rows;
- exactly five matching NVT sources, each with frames 0--5,000 once;
- finite uncertainty, volume/atom, committee-mean maximum force, and
  model-0 maximum force in every row;
- matching element-local trajectory path, source type, and scale metadata;
- exactly 500 discarded-equilibration rows per source (2,500 per element);
- all score-only fields remain empty/false: no uncertainty bins, candidate
  IDs/files, candidate ranks, CUR scores, or selected frames;
- the only score artifact beneath each round is
  `uncertainty_all_frames.csv`; no percentile-bin candidate or selection
  output was created.

| Element | All-frame U min / mean / max (eV/A) | Volume/atom range (A^3) | Max committee-mean force (eV/A) |
|---|---:|---:|---:|
| W | `4.0949908e-10 / 6.6577046 / 32.77991` | 11.593969--21.168137 | 36.27588 |
| Ta | `2.8284767e-09 / 1139.6605 / 5558.0305` | 13.232491--24.159733 | 1451.8888 |
| Ti | `1.1544619e-09 / 198.39773 / 15638.129` | 12.645128--23.087332 | 2591.0328 |

The final `MAE-F: train | test` diagnostics were parsed from exactly these
M0 log paths:

```text
<X>-potential/fcc-restart/model_versions/M0_from_D0/train-committee/train-0/log
...
<X>-potential/fcc-restart/model_versions/M0_from_D0/train-committee/train-9/log
```

| Model (`train-i/log`) | W test MAE-F (meV/A) | Ta test MAE-F (meV/A) | Ti test MAE-F (meV/A) |
|---:|---:|---:|---:|
| 0 | 87.53 | 65.84 | 44.79 |
| 1 | 96.47 | 81.89 | 38.27 |
| 2 | 98.38 | 67.16 | 41.14 |
| 3 | 77.59 | 61.75 | 33.75 |
| 4 | 88.62 | 52.54 | 31.35 |
| 5 | 98.71 | 61.31 | 39.60 |
| 6 | 74.71 | 50.83 | 39.00 |
| 7 | 78.01 | 59.17 | 35.80 |
| 8 | 97.42 | 69.87 | 35.69 |
| 9 | 90.80 | 68.33 | 44.22 |

Using the mandatory arithmetic mean of these ten **test** errors, followed by
meV/A to eV/A conversion:

| Element | Mean test MAE-F (meV/A) | U_min (eV/A) |
|---|---:|---:|
| W | 88.824000 | `0.088824000` |
| Ta | 63.869000 | `0.063869000` |
| Ti | 38.361000 | `0.038361000` |

All 4,501 production frames in every source exceed the corresponding
`U_min`; the cutoff remains mandatory but does not reduce this unstable D1
pool. This is not a justification to substitute a percentile threshold.

The current absolute-U selector was inspected. It excludes the flagged
equilibration rows, applies the absolute-U and optional volume/force gates,
then source-wise candidate-frame spacing, reconstructs gated frames to
measure optional minimum distances, projects descriptors against only the
matching current DB, and applies optional final-frame spacing and an
extreme-U tail cap during CUR. It refuses an existing output root and writes
all physical-gate rejections and provenance. Its default descriptor card is
`r_c=6.0`, `n_max=5`, `l_max=6`, similarity threshold `0.99999`; these may
be retained unless a documented descriptor-coverage reason requires a change.
Source quotas remain disabled because equal quota-CUR requires explicit
approval.

Before CUR submission, the remaining required, element-specific approvals
are DFT target, candidate/final frame gaps, physical gates (volume, force,
minimum distance), and a tail threshold/cap. The extreme finite Ta/Ti
uncertainty/force values must be handled by those auditable gates and cap,
not silently removed.

### Frozen clean-D1 physical/risk cards

The user directed that the element-local cards be determined before CUR. The
method uses only the matching clean 100-row D0 `current.db` as the labeled
physical reference and the matching clean D1 score CSV/trajectories. No D4,
M4, old FCC, EOS, or cross-element asset was used.

For W and Ta, the proposed hard geometry gates are 5% outside the clean-D0
volume/minimum-distance envelope; the force gate is 10% beyond the clean-D0
maximum atomic DFT-force norm. These are labeled-envelope safety limits, not
pool-percentile filters. The initial D0-derived Ti distance limit would leave
only 71 candidates, so Ti uses a still conservative, explicitly documented
10% inward distance margin (`2.000000 A`) while retaining its 10% D0-force
margin. This permits a limited 75-label update without admitting the
collapsed `scale-1p1` source.

| Element | D0 V/atom min--max (A^3) | D0 min distance (A) | D0 max atomic force norm (eV/A) |
|---|---:|---:|---:|
| W | 10.496815898--22.888129870 | 2.119496195 | 13.943852959 |
| Ta | 11.757120460--27.282646784 | 2.219146047 | 7.542197694 |
| Ti | 11.150611726--24.979402597 | 2.219087713 | 3.477224962 |

The frozen D1 selection cards are:

| Element | U_min (eV/A) | V/atom gate (A^3) | Max force (eV/A) | Min distance (A) | Candidate/final source gap (saved frames) | DFT target | Tail threshold / cap |
|---|---:|---:|---:|---:|---:|---:|---:|
| W | 0.088824000 | 9.971975103--24.032536364 | 15.338238254 | 2.013521386 | 50 / 100 | 100 | 17.210970970 / 10 |
| Ta | 0.063869000 | 11.169264437--28.646779123 | 8.296417463 | 2.108188744 | 50 / 100 | 0 (blocked) | N/A |
| Ti | 0.038361000 | 10.593081139--26.228372727 | 3.824947459 | 2.000000000 | 50 / 100 | 75 | 10.313380748 / 7 |

The 50/100-frame gaps equal 0.5/1.0 ps at the frozen 10 fs trajectory-write
interval. They decorrelate candidates source-wise without enabling source
balancing or equal quotas. `--balance-sources` remains disabled. W retains
all five sources. Ti retains safe candidates from `scale-0p9`, `scale-0p95`,
`scale-1`, and `scale-1p05`; `scale-1p1` is fully rejected by the recorded
force/distance gates, not silently omitted. `--require-all-sources` must
therefore remain disabled for Ti. Ta has no safe source and must not invoke
the selector, whose target must be positive.

Tail thresholds are the linear-interpolated p99 of the qualified,
candidate-gap-decorrelated, element-local uncertainty pool. They do not
replace `U_min`; they define only the extreme-U layer. The tail cap is at
most 10% of the fixed DFT target: 10 of 100 for W and 7 of 75 for Ti.

Read-only gate scans produced:

| Element | Candidate-gap survivors | Distance-qualified candidates | Qualified sources (counts) | Tail p99 count |
|---|---:|---:|---|---:|
| W | 451 | 451 | 0.90: 90; 0.95: 90; 1.00: 90; 1.05: 91; 1.10: 90 | 5 |
| Ta | N/A | 0 | none | N/A |
| Ti | 299 | 168 | 0.90: 7; 0.95: 45; 1.00: 52; 1.05: 64; 1.10: 0 | 2 |

W has 451 qualified candidates for its 100-structure target. Ti has 168
qualified candidates; the same-source 100-frame spacing admits at most 107
of them, leaving adequate margin for its conservative target of 75. Ta's
all-production minimum-distance range is only 0.161471--0.867785 A, wholly
below its 2.108188744 A clean-D0-derived safety gate; relaxing the gate to
admit such overlapped cells is not scientifically defensible. Its D1
evidence is retained, but its DFT target is zero and no Ta CUR/DFT job may be
submitted from this trajectory.

A final read-only cardinality check gives W 227 chronologically feasible
frames at its 100-frame final source gap (45/45/46/46/45 by increasing
scale), well above its target of 100. The three clean FCC `current.db` hashes
still match their D0 publication values, and every
`absolute-u-projected-cur/` output root remains absent.

### User-authorized D1 replacement at 1.10 Tm

The user directed that the old D1 artifacts not be retained. A focused
`squeue` check over old MD and score job IDs `13399`--`13401` and
`13413`--`13415` found no active job. The following roots were then deleted
under explicit authorization:

```text
W-potential/fcc-restart/01-nvt-round-1/
Ta-potential/fcc-restart/01-nvt-round-1/
Ti-potential/fcc-restart/01-nvt-round-1/
```

This removes only the old D1 trajectories, score CSVs, and their D1-local
logs; it does not remove a selection output (none existed), D0 labels/current
DBs, M0 models, D4/M4 assets, or EOS references. Post-deletion checks confirm
the original three D1 paths are absent and clean D0 `current.db` checksums
remain W `97079cfdf10c025c8887621b378940d18cb6fe9343432a1cc66917df5fb61a7e`,
Ta `250b1019aa284ad4623cce621f72f9e59b9a0e74dbd2c36bc09d9efc731c9995`,
and Ti
`37292ae7baaed45986cc03b51b7eb9dd1b918510f7dcd58a68837ee3ee407acd`.

The replacement D1 card preserves all validated controls except temperature:

```text
ensemble = NVT; seed = matching 32-atom FCC seed; rep = 1 1 1
scales = 0.90, 0.95, 1.00, 1.05, 1.10
steps = 50000; timestep = 1.0 fs; write/log interval = 10/1
HAL tau_r = 0.10; Langevin friction = 0.02 fs^-1
committee = all ten matching M0 JNNs; no stress request
```

| Element | Tm (K) | Replacement temperature (K) |
|---|---:|---:|
| W | 3683.15 | 4051.465 |
| Ta | 3269.15 | 3596.065 |
| Ti | 1941.15 | 2135.265 |

Each temperature was verified exactly as `1.10 * Tm`. The no-overwrite
submission uses one node, five tasks, 24 hours, no partition/account/GPU
request, and writes only the newly recreated original D1 root:

```bash
sbatch --job-name=fcc_d1_t1p10tm_<X> --nodes=1 --ntasks=5 --time=24:00:00 \
  --output=<X>-potential/fcc-restart/01-nvt-round-1/slurm_logs/fcc-d1-t1p10tm-%j.out \
  --error=<X>-potential/fcc-restart/01-nvt-round-1/slurm_logs/fcc-d1-t1p10tm-%j.err \
  scripts/slurm/run_md_round.slurm \
  --ensemble nvt \
  --round-dir <X>-potential/fcc-restart/01-nvt-round-1 \
  --poscar structures/<X>_fcc_restart/<X>-fcc-seed-32.poscar \
  --rep 1 1 1 --temperature <1.10*Tm> \
  --scale-factors 0.90 0.95 1.00 1.05 1.10 \
  --tau-r 0.10 --steps 50000 --timestep 1.0 \
  --write-interval 10 --log-interval 1 \
  --trajectory multi_nnap_md.xyz --summary energy_forces_summary.dat \
  --friction 0.02 --jnn-paths <train-0/0.jnn ... train-9/9.jnn>
```

Before submission, each target root must remain absent; only its new
`slurm_logs/` directory may be created. The runner is not given an overwrite
option, and all ten JNN paths remain constrained to the matching clean M0
committee.

### Replacement D1 submissions

After no-overwrite preflight, only the three new D1 `slurm_logs/` directories
were created. The recorded replacement cards were submitted unchanged:

| Element | Job ID | Temperature (K) | Immediate status |
|---|---:|---:|---|
| W | `13421` | 4051.465 | `PENDING` |
| Ta | `13422` | 3596.065 | `PENDING` |
| Ti | `13423` | 2135.265 | `PENDING` |

One immediate combined `squeue` check found W with `(None)` and Ta/Ti with
`(Priority)` pending reasons. No polling loop was started. The deleted D1
score CSVs, candidate evidence, and old physical/risk cards are not inputs
to this replacement round; all selection quantities must be recalculated
from its new trajectories.

### Replacement D1 completion and trajectory validation

On the user's completion report, one focused `sacct -X` check found:

| Element | Job ID | State / exit | Elapsed |
|---|---:|---|---:|
| W | `13421` | `COMPLETED / 0:0` | 01:11:36 |
| Ta | `13422` | `COMPLETED / 0:0` | 01:11:01 |
| Ti | `13423` | `COMPLETED / 0:0` | 01:11:18 |

Read-only validation passed for all five replacement sources
`scale-{0p9,0p95,1,1p05,1p1}` per element. Every source has nonempty
`command.sh`, `log`, `multi_nnap_md.xyz`, and
`energy_forces_summary.dat`. Every command uses only the matching 32-atom
seed, `--rep 1 1 1`, the matching `1.10*T_m` temperature, stated scale, and
the ten exact matching M0 JNN paths. Each source has exactly 5,001 finite
unary 32-atom 3D-periodic trajectory frames and exactly 50,001 finite
eight-column summary rows for steps/time 0--50,000 fs.

| Element | Total frames | V/atom range (A^3) | Minimum pair-distance range (A) | Maximum summary force (eV/A) |
|---|---:|---:|---:|---:|
| W | 25,005 | 11.593969--21.168137 | 1.934670--3.105031 | 23.784261 |
| Ta | 25,005 | 13.232491--24.159733 | 0.058676--3.244908 | 5683.053903 |
| Ti | 25,005 | 12.645128--23.087332 | 0.016747--3.196168 | 9140.593436 |

The lower-temperature trajectories are numerically complete, but their
finite Ta/Ti near-overlap frames remain evidence for later explicit
physical/risk gates. No frame/source is silently discarded at this stage.

### Replacement D1 score-only preflight

The current scoring template and scorer CLI were rechecked. The template
allocates one node, one task, and 24 hours; loads JSE; constrains all scoring
threads to one; refuses an existing all-frame CSV; validates all explicitly
requested NVT trajectories; and adds `--score-only` itself. It writes only
the all-frame CSV plus scheduler and exact-command records, never
percentile-bin candidates, selection CSVs, or POSCARs.

Read-only preflight passed for W, Ta, and Ti:

- each new `01-nvt-round-1/uncertainty_all_frames.csv` is absent and there is
  no score, candidate, or selection artifact below the replacement round;
- each replacement round has exactly five trajectories and each matching M0
  committee has exactly ten nonempty JNNs;
- the element-local glob is only
  `<X>-potential/fcc-restart/model_versions/M0_from_D0/train-committee/train-*/*.jnn`;
- no overwrite flag is used.

The no-overwrite replacement score card is:

```bash
sbatch --job-name=fcc_score_t1p10tm_<X> --nodes=1 --ntasks=1 --time=24:00:00 \
  --output=<X>-potential/fcc-restart/01-nvt-round-1/slurm_logs/fcc-score-t1p10tm-%j.out \
  --error=<X>-potential/fcc-restart/01-nvt-round-1/slurm_logs/fcc-score-t1p10tm-%j.err \
  scripts/slurm/run_uncertainty_scoring.slurm \
  --round-dir <X>-potential/fcc-restart/01-nvt-round-1 \
  --jnn-glob '<X>-potential/fcc-restart/model_versions/M0_from_D0/train-committee/train-*/*.jnn' \
  --mode nvt --scales 0.90 0.95 1.00 1.05 1.10 \
  --trajectory-name multi_nnap_md.xyz \
  --all-frames-csv <X>-potential/fcc-restart/01-nvt-round-1/uncertainty_all_frames.csv \
  --equilibration-fraction 0.10 --progress-interval 500
```

The template adds `--score-only`; it is intentionally not passed as a
template argument.

### Replacement D1 score-only submissions

After the no-overwrite preflight and final absence check, the replacement
score cards were submitted unchanged:

| Element | Job ID | Output | Immediate status |
|---|---:|---|---|
| W | `13429` | `W-potential/fcc-restart/01-nvt-round-1/uncertainty_all_frames.csv` | `PENDING` |
| Ta | `13430` | `Ta-potential/fcc-restart/01-nvt-round-1/uncertainty_all_frames.csv` | `PENDING` |
| Ti | `13431` | `Ti-potential/fcc-restart/01-nvt-round-1/uncertainty_all_frames.csv` | `PENDING` |

One immediate combined `squeue` query found W with `(None)` and Ta/Ti with
`(Priority)` pending reasons. No polling loop was started.

### Replacement D1 score completion, CSV validation, and U_min recalculation

On the user's completion report, one focused `sacct -X` check found all
replacement scoring jobs terminally successful:

| Element | Job ID | State / exit | Elapsed |
|---|---:|---|---:|
| W | `13429` | `COMPLETED / 0:0` | 00:25:26 |
| Ta | `13430` | `COMPLETED / 0:0` | 00:25:19 |
| Ti | `13431` | `COMPLETED / 0:0` | 00:25:19 |

Read-only validation passed for each replacement
`01-nvt-round-1/uncertainty_all_frames.csv`:

- the expected 20-column header and exactly 25,005 rows;
- all five matching source paths and exactly 5,001 frames per source;
- finite required uncertainty, volume/atom, and committee-force fields;
- exactly 500 flagged equilibration-discard rows per source;
- correct source metadata; and
- empty/false score-only candidate, rank, CUR, and selection fields.

Each matching scorer log reports `done: scored_frames=25005`; no percentile
candidate or final-selection output was created.

| Element | U min / mean / max (eV/A) | Max committee-mean force (eV/A) |
|---|---:|---:|
| W | `4.09499076e-10 / 4.95135792 / 24.9671306` | `27.4636937` |
| Ta | `2.82847667e-09 / 643.197106 / 9715.76767` | `2453.89295` |
| Ti | `1.15446185e-09 / 131.15245 / 5477.57987` | `1696.04702` |

The mandatory absolute-U values were recomputed from the final test `MAE-F`
diagnostic in the matching ten M0 training logs. The M0 committee is
unchanged, but these values are explicitly recorded for the replacement
pool:

| Element | Test MAE-F values, train-0 through train-9 (meV/A) | Mean (meV/A) | U_min (eV/A) |
|---|---|---:|---:|
| W | `87.53, 96.47, 98.38, 77.59, 88.62, 98.71, 74.71, 78.01, 97.42, 90.80` | 88.824000 | `0.088824000` |
| Ta | `65.84, 81.89, 67.16, 61.75, 52.54, 61.31, 50.83, 59.17, 69.87, 68.33` | 63.869000 | `0.063869000` |
| Ti | `44.79, 38.27, 41.14, 33.75, 31.35, 39.60, 39.00, 35.80, 35.69, 44.22` | 38.361000 | `0.038361000` |

The absolute cutoff may admit most or all replacement production frames; it
must not be replaced by a percentile cutoff. The deleted high-temperature
D1 targets, gate counts, tail thresholds/caps, source decisions, and
selection cards remain superseded. Replacement-pool physical/risk scans must
derive all later values before CUR or DFT.

### Replacement-pool physical/risk scan and frozen CUR cards

This read-only scan uses only each matching clean 100-row D0 `current.db`,
the matching replacement score CSV, and the matching replacement trajectory.
It computes every trajectory-frame minimum pair distance with the periodic
cell. The current DB hashes remain the published clean-D0 hashes, and all
three `absolute-u-projected-cur/` roots remain absent.

The D0 envelopes were recalculated directly from the matching labeled
structures and DFT forces:

| Element | D0 V/atom min--max (A^3) | D0 minimum distance (A) | D0 maximum atomic force norm (eV/A) |
|---|---:|---:|---:|
| W | 10.496815898--22.888129870 | 2.119496195 | 13.943852959 |
| Ta | 11.757120460--27.282646784 | 2.219146047 | 7.542197694 |
| Ti | 11.150611726--24.979402597 | 2.219087713 | 3.477224962 |

The new, uniformly derived physical envelope uses the D0 volume interval
with a 5% outward margin, the D0 maximum force with a 10% outward margin,
and the D0 minimum distance with a 5% inward margin. These are rederived
values, not an inherited old card:

| Element | V/atom gate (A^3) | Max committee-mean force (eV/A) | Minimum distance (A) |
|---|---:|---:|---:|
| W | 9.971975103--24.032536364 | 15.338238254 | 2.013521386 |
| Ta | 11.169264437--28.646779123 | 8.296417464 | 2.108188744 |
| Ti | 10.593081139--26.228372727 | 3.824947459 | 2.108133328 |

All 22,505 post-equilibration frames for every element pass its mandatory
absolute-U cutoff, and all observed volumes fall inside these volume gates.
The force/distance gates, rather than a U percentile, remove unstable
near-overlap frames:

| Element | Raw frames passing all U/volume/force/distance gates | Frames below 95% of D0 min distance | Frames below 50% of D0 min distance |
|---|---:|---:|---:|
| W | 22,099 / 22,505 | 164 / 22,505 (0.73%) | 0 / 22,505 |
| Ta | 3,679 / 22,505 | 16,447 / 22,505 (73.08%) | 15,972 / 22,505 (70.97%) |
| Ti | 4,636 / 22,505 | 15,451 / 22,505 (68.65%) | 7,137 / 22,505 (31.71%) |

Thus Ta and Ti retain severe finite collapse evidence at `1.10*T_m`; no
minimum-distance relaxation is used to meet a target. Ta has safe segments
only in sources 0.90, 0.95, and 1.00. Ti has safe segments only in sources
0.95, 1.00, and 1.05. W retains safe candidates from all five sources.

For source decorrelation, uncertainty autocorrelation was evaluated on pairs
where both post-equilibration frames pass the physical envelope. The
source-median correlations at saved-frame lags 25/50/75 were W
`0.017/-0.009/0.005`, Ta `0.001/0.132/-0.023`, and Ti
`0.045/0.033/0.022`. A 25-frame candidate gap is 0.25 ps and is beyond the
slowest median crossing below 0.1; the Ta median remains above 0.1 at 50
frames, but is below it at 75. The new gaps are therefore 25 saved frames
(0.25 ps) for candidate extraction and 75 saved frames (0.75 ps) during
CUR. They were not copied from the deleted D1 card.

The candidate counts below follow the selector's exact order: discard
equilibration, absolute U, volume/force gates, source-wise 25-frame gap,
then reconstructed-frame distance gate. The 75-frame figures are
chronological source-wise feasibility bounds after all gates:

| Element | Qualified candidates by source, 0.90/0.95/1.00/1.05/1.10 | Total candidates | 75-frame feasible total |
|---|---|---:|---:|
| W | 179 / 178 / 180 / 181 / 180 | 898 | 301 |
| Ta | 31 / 171 / 41 / 0 / 0 | 243 | 84 |
| Ti | 0 / 79 / 152 / 62 / 0 | 293 | 115 |

The DFT target rule is `min(100, 10*floor(N_feasible/20))`: no element
exceeds its 100-row D0 baseline and its 75-frame feasible pool retains at
least two structures per selected label. It yields W 100, Ta 40, and Ti 50.
`--balance-sources` remains disabled for all three. W uses
`--require-all-sources`; Ta and Ti must leave it disabled because their
collapsed sources have no qualified candidate.

Tail thresholds are the linear-interpolated p99 of the qualified,
25-frame-decorrelated candidate uncertainty pool. To prevent a p99
risk-layer configuration from dominating projected CUR, the new cap is 5%
of the DFT target (rounded down):

| Element | U_min (eV/A) | p99 tail threshold (eV/A) | Qualified p99-tail candidates | Tail cap | DFT target |
|---|---:|---:|---:|---:|---:|
| W | 0.088824000 | 14.815457628 | 9 | 5 | 100 |
| Ta | 0.063869000 | 9.027888543 | 3 | 2 | 40 |
| Ti | 0.038361000 | 5.851985654 | 3 | 2 | 50 |

The p99 threshold is solely a risk-layer definition; it does not replace
the mandatory M0-log-derived U cutoff. The unchanged descriptor starting
card remains `r_c=6.0`, `n_max=5`, `l_max=6`, and similarity `0.99999`;
the replacement scan supplies no descriptor-rank reason to change it.

The three frozen cards are selection-ready but no selection has been
submitted. Before an explicitly authorized SLURM submission, preflight the
element-local command, resource request, protected absent output root, and
all input/output paths. No VASP labels, DB merge, M1 training, or E1
evaluation may start before a selected set completes and is validated.

### User-directed revision: geometry-first selection without temporal gaps

The user directed removal of both the 25-frame candidate decorrelation and
75-frame final-feasibility stages. The former cards, final-feasibility
counts, and DFT targets W 100, Ta 40, and Ti 50 are superseded because the
targets were calculated from the 75-frame counts.

The replacement selection design is:

```text
all-frame scoring -> remove equilibration -> absolute U_min
-> periodic minimum-distance gate -> abnormal-void gate
-> current.db-projected CUR -> capped extreme-U layer -> final structural
similarity/identity audit -> Protocol-A DFT
```

The two geometric gates are the only ordinary physical hard rejections:

- minimum pair distance under periodic boundary conditions, initially
  calibrated independently from the matching clean D0 geometry;
- an abnormal local-void metric, to be calibrated from D0 rather than
  treating normal lattice interstices as failures. A normalized periodic
  maximum-empty-sphere metric is the preferred starting definition.

Finite data, positive cell volume, unary composition, PBC, and provenance
remain mandatory validity conditions. Committee force, total volume, source
composition, and uncertainty distributions remain recorded diagnostics. They
may inform a capped extreme-U risk layer but are not automatic rejections.
CUR continues to project against only the matching current.db; structural
similarity/duplicate checks remain mandatory, but no source-wise temporal
gap or final temporal-feasibility rule is imposed.

No void threshold, candidate count, DFT target, tail threshold/cap, or CUR
submission card has yet been recalibrated or approved under this revision.

### Read-only threshold calibration

The current `src/absolute_u_projected_cur_selection.py` reconstructs each
candidate POSCAR and supports a periodic minimum-distance rejection through
`--min-distance`. It does not implement an abnormal-void metric or a
corresponding CLI argument, so a code change and test will be required before
the revised selection policy can run.

For a local-void definition, the proposed statistic is the largest periodic
Delaunay-tetrahedron empty-sphere radius divided by the mean atom spacing:

```text
q_void = R_void,max / (V / N)^(1/3)
```

All 100 matching clean D0 structures were scanned read-only. The
minimum-distance threshold is 95% of the D0 minimum. The provisional void
limit is 115% of the maximum D0 `q_void`; it accepts every D0 structure and
allows 15% normalized local-disorder margin.

| Element | D0 min distance (A) | Proposed min-distance gate (A) | D0 max q_void | Proposed q_void limit |
|---|---:|---:|---:|---:|
| W | 2.119496195 | 2.013521386 | 0.822874141 | 0.946305262 |
| Ta | 2.219146047 | 2.108188744 | 0.819366100 | 0.942271015 |
| Ti | 2.219087713 | 2.108133328 | 0.822748897 | 0.946161232 |

The D0 `q_void` p99 values are W `0.821369442`, Ta `0.818975712`, and Ti
`0.822329067`, so the maximum-based limits are not set by a D0 outlier.

A read-only ten-frame-per-source D1 sample confirmed that the statistic
separates clear collapse/cavity conditions from compact frames. Sampled
maximum `q_void` values were W `1.037`, Ta `6.595`, and Ti `1.545`; Ta/Ti
large values coincide with very short pair distances in the sampled
structures. Some W expanded-source frames have acceptable pair distances
but `q_void` up to `1.037`; the proposed `q_void` gate would intentionally
classify those as local-cavity configurations. A full-pool audit is still
needed before freezing counts, tail limits, or DFT budgets.

### User-directed minimum-distance revision

The user selected an 80% clean-D0 minimum-distance gate, superseding the
earlier 95% proposal:

| Element | D0 min distance (A) | Active proposed min-distance gate (A) |
|---|---:|---:|
| W | 2.119496195 | 1.695596956 |
| Ta | 2.219146047 | 1.775316838 |
| Ti | 2.219087713 | 1.775270170 |

The user requested clarification of the abnormal local-void definition
before accepting a threshold. The Delaunay maximum-empty-sphere statistic
and its provisional D0-calibrated limits remain proposals only.

### Geometry-first selector implementation and selection preflight

On the user's authorization, the proposed Delaunay maximum-empty-sphere
definition is frozen for this replacement D1 selection. The active source and
documentation changes are:

- `src/absolute_u_projected_cur_selection.py`: adds the periodic
  `q_void = R_void,max/(V/N)^(1/3)` calculation, records void radius and
  normalized void for candidates/rejections, adds `--max-normalized-void`,
  and adds `--tail-quantile` for a geometry-valid linear p99 tail threshold;
- `scripts/slurm/run_absolute_u_projected_cur.slurm`: passes the new
  selector options;
- `research-plan.md`, `docs/unary_workflow.md`, and
  `docs/source_function_index.md`: record the new no-temporal-gap,
  distance/void, p99-tail workflow.

Read-only verification passed:

```text
python3 -m py_compile src/*.py
bash -n scripts/slurm/run_absolute_u_projected_cur.slurm
module load jse && python3 src/absolute_u_projected_cur_selection.py --help
```

The periodic metrics reproduce known clean-D0 frame values for W, Ta, and Ti.
The exact selection preflight confirms for every element: absent protected
output root and temporary root; matching 100-row unary 32-atom clean D0 DB;
25,005 all-frame/22,505 post-equilibration score rows from five matching
sources; every post-equilibration frame meets its recorded absolute `U_min`;
and the following recalculated geometry card:

| Element | U_min (eV/A) | DFT target | Tail quantile/cap | Min distance (A) | Max q_void |
|---|---:|---:|---:|---:|---:|
| W | 0.088824000 | 100 | p99 / 5 | 1.695596956 | 0.946305262 |
| Ta | 0.063869000 | 100 | p99 / 5 | 1.775316838 | 0.942271015 |
| Ti | 0.038361000 | 100 | p99 / 5 | 1.775270170 | 0.946161232 |

All cards use no candidate/final frame gap, no source quota, no
require-all-sources condition, and descriptor parameters `r_c=6.0`,
`n_max=5`, `l_max=6`, similarity `0.99999`. The p99 threshold is resolved
inside each protected selection job only after applying the two geometry
gates. The jobs use one node, one task, 24 hours, and no overwrite option.

### Geometry-first CUR submissions

The following exact no-overwrite commands were submitted after preflight:

```bash
sbatch --job-name=fcc_d1_geomcur_<X> --nodes=1 --ntasks=1 --time=24:00:00 \
  --output=<X>-potential/fcc-restart/01-nvt-round-1/slurm_logs/fcc-d1-geomcur-%j.out \
  --error=<X>-potential/fcc-restart/01-nvt-round-1/slurm_logs/fcc-d1-geomcur-%j.err \
  scripts/slurm/run_absolute_u_projected_cur.slurm \
  --round-dir <X>-potential/fcc-restart/01-nvt-round-1 \
  --all-frames <X>-potential/fcc-restart/01-nvt-round-1/uncertainty_all_frames.csv \
  --base <X>-potential/fcc-restart/current.db \
  --output-root <X>-potential/fcc-restart/01-nvt-round-1/absolute-u-projected-cur \
  --u-min <X-specific-U-min> --target 100 \
  --tail-quantile 0.99 --tail-max 5 \
  --min-distance <X-specific-80-percent-D0-limit> \
  --max-normalized-void <X-specific-115-percent-D0-limit> \
  --r-c 6.0 --n-max 5 --l-max 6 --similarity-threshold 0.99999
```

| Element | Job ID | Immediate status |
|---|---:|---|
| W | `13440` | `PENDING` |
| Ta | `13441` | `PENDING` |
| Ti | `13442` | `PENDING` |

One combined immediate `squeue` check was made after all submissions. No
polling loop was started. No DFT, merge, M1, or E1 command is submitted.

### Ta geometry-first selection validation and Protocol-A DFT submission

A later focused `sacct` check found Ta selection job `13441` terminally
successful (`COMPLETED 0:0`, elapsed `00:39:04`). W `13440` and Ti `13442`
were still running and were not polled further.

Ta read-only output validation passed:

- 6,193 candidate rows plus 16,312 distance/void rejections exactly equal
  the 22,505 post-equilibration score rows;
- all candidate rows meet `U_min=0.063869`, `d_min >= 1.775316838` A, and
  `q_void <= 0.942271015`;
- exactly 100 unique CUR ranks/POSCARs are selected, all finite unary
  32-atom 3D-periodic Ta structures with positive cells;
- the geometry-valid linear p99 uncertainty threshold is
  `13.338168350` eV/A and five selected structures are in its capped tail;
- selected source counts are scale 0.90: 8, 0.95: 26, and 1.00: 66.

Ta Protocol-A DFT preflight passed for:

```text
input:    Ta-potential/fcc-restart/01-nvt-round-1/absolute-u-projected-cur/
          cur-selected-poscar_absolute_u0p063869_cur100/
output:   Ta-potential/fcc-restart/01-nvt-round-1/Ta_D1_labeled.db
work dir: Ta-potential/fcc-restart/01-nvt-round-1/dft/vasp_Ta_D1/
```

The output DB and work directory were absent. The 100 selected POSCARs are
all finite unary 32-atom Ta cells. The matching local Ta POTCAR SHA-256 is
`b94d0231aa338d2b49887428178c5ebac7fa385cbd6154890af94e8013d269f3`;
ENMAX is `223.667` eV and the Protocol-A auto-ENCUT is `290.7671` eV.

The no-overwrite batch was submitted:

```bash
sbatch --job-name=fcc_d1_dft_Ta --nodes=1 --ntasks=64 --time=24:00:00 \
  --output=Ta-potential/fcc-restart/01-nvt-round-1/slurm_logs/fcc-d1-dft-%j.out \
  --error=Ta-potential/fcc-restart/01-nvt-round-1/slurm_logs/fcc-d1-dft-%j.err \
  scripts/slurm/run_vasp_batch_dft.slurm \
  Ta-potential/fcc-restart/01-nvt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u0p063869_cur100 \
  Ta-potential/fcc-restart/01-nvt-round-1/Ta_D1_labeled.db _ 0.2
```

Ta job `13444` is `PENDING` on the one immediate `squeue` check. No overwrite
environment variable is set; the template uses eight ranks per VASP task and
eight concurrent tasks from the 64-task allocation. No W/Ti DFT job is
submitted.

### W/Ti geometry-first selection validation and Protocol-A DFT submissions

A later combined status check found W selection `13440` and Ti selection
`13442` terminally successful (`COMPLETED 0:0`, elapsed `00:57:37` and
`00:48:39`). The same check found Ta DFT `13444` running; it was not checked
again after this point.

The initial W/Ti DFT preflight stopped only because full POTCAR SHA-256
values had been manually expanded incorrectly from abbreviated notes. It
created no output and submitted no job. The corrected direct hashes were
used for a successful rerun.

| Element | Candidates | Geometry rejections | Selected | p99 U (eV/A) | Selected tail | Selected source counts |
|---|---:|---:|---:|---:|---:|---|
| W | 20,120 | 2,385 | 100 | 14.039897016 | 5 | 0.90: 6; 0.95: 2; 1.00: 10; 1.05: 18; 1.10: 64 |
| Ti | 12,726 | 9,779 | 100 | 14.002407670 | 4 | 0.90: 36; 0.95: 29; 1.00: 30; 1.05: 5 |

For both elements, candidate plus rejection rows equal 22,505; every
candidate meets its matching U, 80%-D0 distance, and 115%-D0 normalized-void
limit; 100 unique selected CUR ranks/POSCARs are finite unary 32-atom
3D-periodic cells; tail selections do not exceed five; and no temporal,
volume, force, quota, or require-all-source gate was enabled.

Corrected Protocol-A DFT preflight:

| Element | POTCAR SHA-256 | ENMAX (eV) | Auto-ENCUT (eV) | Output DB | Work root |
|---|---|---:|---:|---|---|
| W | `c0897285f1b301314dcc12eb838ce8a777aa860795754598b0626cb818170117` | 223.057 | 289.9741 | `W_D1_labeled.db` | `dft/vasp_W_D1/` |
| Ti | `f8e8f1d080d9e9b45e792f1068744b07aba8441d1e7ce11486a5d4c0f5a1479e` | 178.330 | 231.8290 | `Ti_D1_labeled.db` | `dft/vasp_Ti_D1/` |

Both output DBs/work roots were absent and each input contains only the 100
matching selected POSCARs. The following no-overwrite pattern was submitted
for W and Ti, with `<tag>` equal to `0p088824` and `0p038361`, respectively:

```bash
sbatch --job-name=fcc_d1_dft_<X> --nodes=1 --ntasks=64 --time=24:00:00 \
  --output=<X>-potential/fcc-restart/01-nvt-round-1/slurm_logs/fcc-d1-dft-%j.out \
  --error=<X>-potential/fcc-restart/01-nvt-round-1/slurm_logs/fcc-d1-dft-%j.err \
  scripts/slurm/run_vasp_batch_dft.slurm \
  <X>-potential/fcc-restart/01-nvt-round-1/absolute-u-projected-cur/cur-selected-poscar_absolute_u<tag>_cur100 \
  <X>-potential/fcc-restart/01-nvt-round-1/<X>_D1_labeled.db _ 0.2
```

| Element | DFT job | Immediate status |
|---|---:|---|
| W | `13445` | `PENDING` |
| Ti | `13446` | `PENDING` |

One combined immediate `squeue` check was made after W/Ti submission. No
overwrite environment variable is set. No database merge, M1, or E1 job is
submitted.

### Ta DFT completion

On the user's completion report, one focused `sacct -X` check found Ta
Protocol-A DFT job `13444` terminally successful: `COMPLETED 0:0` in
`00:56:05`. The Ta label DB has not yet been inspected, merged, or published.
The required next gate is read-only label validation before any Ta D1 database
transition or M1 submission.

### Ta D1 label validation, merge, publication, and M1 submission

Read-only validation of `Ta_D1_labeled.db` passed before any database change:
there are exactly 100 selected inputs, manifest tasks, completed VASP task
directories, and DB rows. Every label uses static Protocol A, including the
Ta POTCAR SHA-256
`b94d0231aa338d2b49887428178c5ebac7fa385cbd6154890af94e8013d269f3`.
The ENMAX is `223.667` eV and generated `ENCUT=290.767` is the documented
serialization of auto-ENCUT `290.7671` eV. All energies, `(32, 3)` forces,
and stresses are finite; every 32-atom Ta cell agrees with its selected
POSCAR source within `5e-9 A`. The D1 cell-energy range is
`-362.863042630` to `-306.168139950` eV.

The no-overwrite merge preflight confirmed distinct base, label, and output
paths; absent `updated.db`; a 100-row finite unary-Ta D0 base; and the
published D0 SHA-256
`250b1019aa284ad4623cce621f72f9e59b9a0e74dbd2c36bc09d9efc731c9995`.
The supported merge completed:

```bash
module load jse && python3 src/vasp_batch_dft.py merge \
  Ta-potential/fcc-restart/current.db \
  Ta-potential/fcc-restart/01-nvt-round-1/Ta_D1_labeled.db \
  Ta-potential/fcc-restart/01-nvt-round-1/updated.db
```

Read-only validation of the result confirmed 200 finite unary 32-atom Ta
rows with no EOS metadata, exact D0-prefix/D1-suffix preservation, and
unchanged base D0 checksum. `updated.db` SHA-256 is
`69b733947c729bd4aa5685f8598ceb8a4356be80f5f00797dd3b156e051cf95a`.
It was copied to an exclusive same-directory temporary file, checksum-checked,
and published with `os.replace`; post-publication validation found the
200-row `Ta-potential/fcc-restart/current.db` byte-identical to `updated.db`.
The preserved `updated.db` remains the auditable D1 merge artifact.

The M1 no-overwrite preflight confirmed the published 200-row Ta DB, absent
`model_versions/M1_from_D1/train-committee/`, absent `fcc-m1-*` scheduler
outputs, valid template syntax, and `ENERGY["Ta"] = -11.8578`. It used the
approved one-node, 5-task, 8-CPUs/task, 48-hour resource card and did not set
`OVERWRITE`. The submitted command was:

```bash
sbatch --job-name=fcc_m1_Ta --nodes=1 --ntasks=5 --cpus-per-task=8 \
  --time=48:00:00 \
  --output=Ta-potential/fcc-restart/slurm_logs/fcc-m1-%j.out \
  --error=Ta-potential/fcc-restart/slurm_logs/fcc-m1-%j.err \
  scripts/slurm/run_train_committee.slurm \
  Ta-potential/fcc-restart/current.db \
  Ta-potential/fcc-restart/model_versions/M1_from_D1/train-committee \
  10 5 5000
```

Ta M1 job `13448` was accepted. Its one immediate `squeue` check reported
`PENDING (Priority)`; no monitoring loop was started. W/Ti assets were not
read, changed, or polled during this Ta transition.

### Ti D1 DFT completion and label validation

On the user's completion report, one focused `sacct -X` check found Ti
Protocol-A DFT job `13446` terminally successful: `COMPLETED 0:0` in
`01:03:53`. Read-only validation then passed before any Ti database change:

- the selected input directory, manifest, task root, and
  `Ti_D1_labeled.db` each contain exactly 100 records;
- every task has a complete OUTCAR and static Protocol-A INCAR;
- all task POTCARs match the local Ti POTCAR SHA-256
  `f8e8f1d080d9e9b45e792f1068744b07aba8441d1e7ce11486a5d4c0f5a1479e`;
  ENMAX is `178.330` eV and generated `ENCUT=231.829` represents the
  expected auto-ENCUT `231.8290` eV;
- all 100 labels are finite unary, 3D-periodic, positive-cell 32-atom Ti
  structures with finite energy, `(32, 3)` forces, and stress;
- every output cell and wrapped fractional coordinate agrees with its
  selected POSCAR source within `5e-9 A`, and no EOS/cross-element metadata
  is present.

The D1 cell-energy range is `-240.622186860` to `-204.253656960` eV.
Ti `current.db` has not been merged or replaced, and no Ti M1 job was
submitted: explicit user approval is required for that protected D1
transition. W job `13445` was not queried.

### Ti D1 merge, publication, and M1 submission

After the user explicitly authorized the Ti D1 transition, no-overwrite
preflight confirmed distinct base/label/output paths, absent `updated.db`,
and the 100-row published Ti D0 SHA-256
`37292ae7baaed45986cc03b51b7eb9dd1b918510f7dcd58a68837ee3ee407acd`.
The supported merge completed:

```bash
module load jse && python3 src/vasp_batch_dft.py merge \
  Ti-potential/fcc-restart/current.db \
  Ti-potential/fcc-restart/01-nvt-round-1/Ti_D1_labeled.db \
  Ti-potential/fcc-restart/01-nvt-round-1/updated.db
```

Validation found exactly 200 finite unary 32-atom Ti rows with no EOS
metadata. The first 100 records are bytewise-equivalent structure/result
records from D0, the last 100 are equivalently preserved D1 labels, and the
D0 base checksum remained unchanged. `updated.db` SHA-256 is
`f2874ac425d45bacf41c1e78503e7ece08c59c477b7ad219926e32f4bada577b`.
It was copied to an exclusive same-directory temporary DB, checksum-checked,
and atomically published using `os.replace`. Post-publication validation
confirmed the 200-row Ti `current.db` is byte-identical to retained
`updated.db`.

The Ti M1 no-overwrite preflight confirmed the published 200-row database,
an absent `model_versions/M1_from_D1/train-committee/`, no existing
`fcc-m1-*` scheduler outputs, template syntax, and `ENERGY["Ti"] = -7.8951`.
No `OVERWRITE` setting was used. The approved submission was:

```bash
sbatch --job-name=fcc_m1_Ti --nodes=1 --ntasks=5 --cpus-per-task=8 \
  --time=48:00:00 \
  --output=Ti-potential/fcc-restart/slurm_logs/fcc-m1-%j.out \
  --error=Ti-potential/fcc-restart/slurm_logs/fcc-m1-%j.err \
  scripts/slurm/run_train_committee.slurm \
  Ti-potential/fcc-restart/current.db \
  Ti-potential/fcc-restart/model_versions/M1_from_D1/train-committee \
  10 5 5000
```

Ti M1 job `13450` was accepted. Its one immediate `squeue` check reported
`PENDING (Resources)`; no monitoring loop was started. W assets were not
queried or changed.

### Ta M1 completion validation and E1 fixed-reference EOS

The user reported Ta M1 complete and requested the fixed-reference E1 EOS
evaluation. One focused status check found job `13448` as `COMPLETED 0:0` in
`00:07:02`. The first artifact scan was incorrect because `fd` respected
repository ignore patterns (`**/*.jnn`, `**/*.db`, and `**/log`) and showed
only directories. A corrected `fd -HI` scan found all expected artifacts:
ten JNNs, trainer scripts, train/test DBs, fold logs, history files, and both
configured scheduler files. The initial empty-committee report is
superseded.

The full read-only M1 validation passed:

- all ten folds have one nonempty `0.jnn` through `9.jnn` and
  `train.nepochs = 5000`;
- every fold has 180 train and 20 test rows from only the 200-row Ta D1 DB;
  test coverage is exactly once and train coverage exactly nine times per
  source row;
- all final train/test energy and force diagnostics are finite; the mean
  model test `MAE-F` is `144.4800` meV/A;
- six of ten models meet the 1.25 train/test energy-MAE ratio criterion.
  `train-5/5.jnn` is selected with train/test energy MAE
  `5.055/5.150` meV/atom and ratio `1.01879327399`;
- the ordered M1 JNN SHA-256 digest is
  `be228ef3919b114c86dfd4f85285b4d5b373baea1478ebbf6d6b6e6fbbbfd6d7`.

No-overwrite E1 preflight verified absent
`Ta-potential/fcc-restart/evaluations/E1_M1/`, the unchanged 200-row Ta
current DB, and fixed reference checksums: metadata
`16d5f83cd5a994109b17a66846a5091a718cfb6ce61d7f13f19a6e543222dc4f`;
reference
`869d901829f0682cb169923b1f0745e8e7503cff5385efb2a84bc53c1a06f4ab`.
The direct lightweight evaluation completed:

```bash
module load jse
python3 src/eos_check_jnn.py \
  --element Ta \
  --metadata results/Ta_eos_benchmark/eos_reference/eos_structures.csv \
  --reference-csv results/Ta_eos_benchmark/eos_reference/eos_reference.csv \
  --jnn-root Ta-potential/fcc-restart/model_versions/M1_from_D1/train-committee \
  --model-id E1_M1 \
  --output-dir Ta-potential/fcc-restart/evaluations \
  --max-train-test-ratio 1.25
```

JSE created only its normal inference cache
`train-5/lib5_449de9df543f18bd.so`; the ten JNN byte digests, current DB,
and EOS references remain unchanged. E1 validation passed: `jnn_selection`
has 10 rows/6 eligible, raw and DFT-merged predictions have 57 finite
19/19/19 bcc/fcc/hcp records, all bcc/fcc/hcp/aggregate metric rows are
finite, and plots are nonempty (171,543 and 144,211 bytes).

| Metric | E0 M0 (meV/atom) | E1 M1 (meV/atom) | E1 - E0 |
|---|---:|---:|---:|
| Aggregate raw MAE | 16.182558 | 66.435829 | +50.253271 |
| Aggregate phase-aligned MAE | 13.358162 | 8.339454 | -5.018708 |

E1 phase raw/aligned MAEs and grid-minimum volume shifts are: bcc
`91.344289/13.170284` meV/atom and `-0.180696 A^3/atom`; fcc
`3.638304/0.385546` and `0.000000`; hcp `104.324893/11.462533` and
`-0.371370`. The shape metric improves but raw cross-phase energetics
regress, so preserve E1 and await an explicit scientific decision before D2.
W and Ti were not queried.

### W D1 DFT completion and label validation

On the user's completion report, one focused `sacct -X` check found W
Protocol-A DFT job `13445` terminally successful: `COMPLETED 0:0` in
`02:01:24`. Read-only validation passed before any W database change:

- the selected input directory, manifest, task root, and
  `W_D1_labeled.db` each contain exactly 100 records;
- every task has a complete OUTCAR and static Protocol-A INCAR;
- all task POTCARs match the local W POTCAR SHA-256
  `c0897285f1b301314dcc12eb838ce8a777aa860795754598b0626cb818170117`;
  ENMAX is `223.057` eV and generated `ENCUT=289.974` represents the
  expected auto-ENCUT `289.9741` eV;
- all 100 labels are finite unary, 3D-periodic, positive-cell 32-atom W
  structures with finite energy, `(32, 3)` forces, and stress;
- every output cell and wrapped fractional coordinate agrees with its
  selected POSCAR source within `5e-9 A`, and no EOS/cross-element metadata
  is present.

The D1 cell-energy range is `-391.945410290` to `-308.568741220` eV. W
`current.db` has not been merged or replaced, and no W M1 job was submitted:
explicit user approval is required for this protected D1 transition.

### W D1 merge, publication, and M1 submission

After the user explicitly authorized the W D1 transition, no-overwrite
preflight confirmed distinct base/label/output paths, absent `updated.db`,
and the published 100-row W D0 SHA-256
`97079cfdf10c025c8887621b378940d18cb6fe9343432a1cc66917df5fb61a7e`.
The supported merge completed:

```bash
module load jse && python3 src/vasp_batch_dft.py merge \
  W-potential/fcc-restart/current.db \
  W-potential/fcc-restart/01-nvt-round-1/W_D1_labeled.db \
  W-potential/fcc-restart/01-nvt-round-1/updated.db
```

Validation found exactly 200 finite unary 32-atom W rows with no EOS
metadata. The first 100 records exactly preserve D0 and the final 100 exactly
preserve D1 labels; the D0 base checksum remained unchanged.
`updated.db` SHA-256 is
`c98274fb1b798c7fcaa339c8b77d4aeb295805bf200881c037cf4dceaa37e492`.
It was copied to an exclusive same-directory temporary DB, checksum-checked,
and atomically published using `os.replace`. Post-publication validation
confirmed the 200-row W `current.db` is byte-identical to retained
`updated.db`.

The W M1 no-overwrite preflight confirmed the published 200-row database, an
absent `model_versions/M1_from_D1/train-committee/`, no `fcc-m1-*` scheduler
outputs, template syntax, and `ENERGY["W"] = -12.9581`. No `OVERWRITE`
setting was used. The approved submission was:

```bash
sbatch --job-name=fcc_m1_W --nodes=1 --ntasks=5 --cpus-per-task=8 \
  --time=48:00:00 \
  --output=W-potential/fcc-restart/slurm_logs/fcc-m1-%j.out \
  --error=W-potential/fcc-restart/slurm_logs/fcc-m1-%j.err \
  scripts/slurm/run_train_committee.slurm \
  W-potential/fcc-restart/current.db \
  W-potential/fcc-restart/model_versions/M1_from_D1/train-committee \
  10 5 5000
```

W M1 job `13453` was accepted. Its one immediate `squeue` check reported
`RUNNING` on `lpsnode03`; no monitoring loop was started.

### W/Ti M1 completion validation and E1 fixed-reference EOS

The user reported both remaining M1 jobs complete and requested the two
unfinished E1 evaluations. One focused combined `sacct -X` check found Ti
`13450` `COMPLETED 0:0` in `00:07:24` and W `13453` `COMPLETED 0:0` in
`00:06:45`.

Both read-only committee/E1 preflights passed:

| Element | Eligible / 10 | Selected M1 JNN | Train/test MAE-E (meV/atom) | Mean test MAE-F (meV/A) | Ordered JNN SHA-256 |
|---|---:|---|---:|---:|---|
| W | 4 | `train-3/3.jnn` | 6.418 / 6.151 | 166.5800 | `654d6d044f50aef75702d9eb77bba6ff56b7f888a7aca485bc4fb01ccfb8690e` |
| Ti | 7 | `train-5/5.jnn` | 3.698 / 3.417 | 110.9860 | `12e4f4c4e5ef45675a1f8ea8b3a794263ed2712d30ed5b168a76df821a93e2e3` |

For each element, all ten JNNs/trainers/logs/train DBs/test DBs are
nonempty; every trainer specifies 5,000 epochs; folds contain 180 train and
20 test rows drawn only from the matching 200-row D1 DB; every row appears
once in test and nine times in train. The matching fixed metadata/reference
pair has 57 common finite DFT rows with 19 each bcc/fcc/hcp, and the absent
element-local `evaluations/E1_M1/` path was confirmed before execution.

The two element-isolated direct evaluations completed in parallel:

```bash
module load jse
python3 src/eos_check_jnn.py \
  --element <W|Ti> \
  --metadata results/<W|Ti>_eos_benchmark/eos_reference/eos_structures.csv \
  --reference-csv results/<W|Ti>_eos_benchmark/eos_reference/eos_reference.csv \
  --jnn-root <W|Ti>-potential/fcc-restart/model_versions/M1_from_D1/train-committee \
  --model-id E1_M1 \
  --output-dir <W|Ti>-potential/fcc-restart/evaluations \
  --max-train-test-ratio 1.25
```

JSE created only normal inference cache libraries:
`W/train-3/lib3_449de9df543f18bd.so` and
`Ti/train-5/lib5_449de9df543f18bd.so`. W/Ti current DBs, fixed EOS
references, and M1 JNN bytes remained unchanged. Both E1 output validators
passed with 10 selection rows, 57 finite raw and DFT-merged predictions,
four finite phase/aggregate metric rows, and nonempty plots.

| Element | Aggregate raw MAE E0 -> E1 (meV/atom) | Aggregate aligned MAE E0 -> E1 (meV/atom) |
|---|---|---|
| W | 131.064897 -> 64.413224 | 28.027437 -> 21.424392 |
| Ti | 36.024202 -> 14.103997 | 7.434641 -> 1.962939 |

W phase raw/aligned MAEs and E1 grid-minimum volume shifts are bcc
`40.853701/35.650159` meV/atom and `-0.316526 A^3/atom`; fcc
`3.117093/2.179271` and `0.000000`; hcp `149.268877/26.443746` and
`-0.163382`. Ti values are bcc `7.967100/2.141632` and `0.000000`; fcc
`1.016604/0.588200` and `0.000000`; hcp `33.328286/3.158984` and
`0.000000`. Both W/Ti improve in raw and phase-aligned aggregate MAE;
preserve the results and await explicit D2-stage direction.

### Frozen clean-FCC D2 NVT cards

The user explicitly directed simultaneous, element-isolated D2 sampling,
superseding the former Ta-only diagnostic hold. `research-plan.md` section
8.2.1 freezes these cards:

| Element | Round root | Temperature (K) | Scale factors |
|---|---|---:|---|
| W | `W-potential/fcc-restart/02-nvt-round-2/` | 4051.465 | `0.95, 1.00, 1.05, 1.10, 1.15` |
| Ta | `Ta-potential/fcc-restart/02-nvt-round-2/` | 3596.065 | `0.90, 0.925, 0.95, 0.975, 1.00` |
| Ti | `Ti-potential/fcc-restart/02-nvt-round-2/` | 2135.265 | `0.95, 0.975, 1.00, 1.025, 1.05` |

Each card retains the D1 `1.10*T_m` temperature and execution controls
(32-atom seed, `--rep 1 1 1`, ten matching M1 JNNs, 50,000 steps, 1.0 fs,
trajectory/log intervals 10/1, HAL `tau_r=0.10`, friction `0.02`, one node,
five one-core tasks, 24 hours). This isolates the required new NVT scale-grid
change while testing the improved M1 committees. W extends the D1 expanded
region because 64 of 100 D1 labels came from scale 1.10; Ta/Ti introduce
intermediate scales only within their respective geometry-safe D1 windows.
The prior Ta/Ti collapse evidence does not relax any later D2 selection
geometry gate. D2 needs fresh all-frame calibration, and EOS is
validation-only rather than an input.
