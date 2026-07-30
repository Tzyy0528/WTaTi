# Notes: Clean-FCC D4 Labels Through M4 and E4

## Sources

### Source 1: User authorization
- Path/URL: Conversation on 2026-07-29.
- Key points:
  - User states D4 DFT is complete and authorizes stepwise completion.

### Source 2: Prior D4 submission record
- Path/URL: `memory/37_clean_fcc_D4_to_DFT_submission/`.
- Key points:
  - D4 used isolated 400-row D3 bases and exactly 100 accepted selected
    POSCARs per element.
  - Protocol-A target DBs are `<X>_D4_labeled.db`.

## Commands and Observations

```bash
# Pending targeted recovery and validation.
```

## Synthesized Findings

### Pending
- The D3 acceptance pattern requires all 100 manifest/task/DB identities,
  finite results, frozen Protocol-A inputs, and exact selected-geometry
  correspondence before any database mutation.

### D4 label recovery and read-only acceptance

The user-reported D4 completions are confirmed by scheduler accounting:
W `13558` completed in `02:30:08`, Ta `13559` in `02:24:12`, and Ti
`13560` in `02:16:54`, all `COMPLETED 0:0`.

Every isolated D4 VASP batch passed full read-only acceptance. Each has a
100-entry manifest, 100 prepared task directories, run summary
`to_run=100`, `succeeded=100`, `failed=[]`, complete OUTCAR marker,
nonempty VASP result/log, eight-rank `srun` command, matching local PAW
checksum, and static Protocol-A INCAR (`MAGMOM` omitted, `KSPACING=0.2`,
auto ENCUT, `NCORE=2`, `IBRION=-1`, `NSW=0`). Each 100-row label DB has exact
manifest source order, finite energy/(32,3) forces/(6,) stress, unary
32-atom PBC positive-cell structures, no EOS metadata, and source geometry
agreement within `5e-9` in cell and wrapped scaled coordinates. The protected
400-row D3 bases and M3 committee digests remain unchanged.

| Element | D4 label DB SHA-256 | Cell-energy range (eV) | Max abs force (eV/A) | Max cell/scaled error |
|---|---|---:|---:|---:|
| W | `99a1312c68b8d17c8018c4d17883a5feb72aacd218430e8530a2b92ed092bf93` | -389.634925150 to -360.028301510 | 15.390391400 | `4.998e-9 / 4.999e-9` |
| Ta | `d8d8d7128a63b3181f4443c43b48d86cbd84406c5abaa1032182a117c44af3b3` | -357.035151900 to -330.396403480 | 8.814077630 | `4.997e-9 / 5.000e-9` |
| Ti | `00e8708dfc48082b341337418b955c3b9fb594bfe5542ddd5cc22176218f38a5` | -233.941712100 to -202.853671990 | 5.522828530 | `4.934e-9 / 5.000e-9` |

The first validator used over-strict decimal comparisons for INCAR ENCUT and
Ti metadata's binary float representation; rendering-/serialization-aware
numeric tolerances accepted the exact frozen values. No generated data was
changed during validation.

### D4 merge and publication

The three supported no-overwrite `src/vasp_batch_dft.py merge` commands
created independent `04-npt-round-2/updated.db` files. Full read-only
validation confirmed 500 finite unary 32-atom PBC rows in each result, with
an exact semantic 400-row D3 base prefix and validated 100-row D4-label
suffix, and no EOS metadata. Each result was checksum-verified after a
same-directory temporary copy, then atomically published as only the matching
`current.db`.

| Element | Published D4 500-row SHA-256 |
|---|---|
| W | `1242b2f534f1bebc2730102b0e1c5d8b524c0adaee2a75259d687deecfa57480` |
| Ta | `600bd1c0c7d205771fe7b9859731e9af05399498e4c9ae6757c9de3bb9616989` |
| Ti | `8db00646830c0cbb81037130881815b344f9be4f893a47e3d4a2dde075d2322b` |

An initial publication helper lacked the JSE/ASE module and failed before
mutation; an accidental empty retry also made no change. The final guarded
publication staged all three temporary copies before replacing any
`current.db`, then checked their hashes and row counts.

### M4 preflight and submission

The three published 500-row D4 databases passed a fresh finite
unary-32-atom/PBC/no-EOS preflight. The active training references in
`src/dbselectandtrain.py` are exactly W `-12.9581`, Ta `-11.8578`, and Ti
`-7.8951` eV; M4 committee and E4 roots were absent. `jse` resolves after
loading the local module, and no inherited `OVERWRITE` setting was present.

Each protected direct submission uses one node, five tasks, eight CPUs per
task, 48 hours, ten total committee members, five concurrent workers, and
5,000 epochs through `scripts/slurm/run_train_committee.slurm` with only its
matching published D4 `current.db`:

| Element | M4 job | Immediate scheduler state |
|---|---:|---|
| W | `13569` | `RUNNING` on `lpsnode03` |
| Ta | `13570` | `RUNNING` on `lpsnode02` |
| Ti | `13571` | `RUNNING` on `lpsnode02` |

Focused monitoring found successful terminal scheduler accounting: W `13569`
completed `0:0` in `00:18:36`, Ta `13570` in `00:13:31`, and Ti `13571` in
`00:14:11`. No E4 output has been created; committee acceptance is next.

### M4 committee acceptance

All three M4 committees passed full read-only acceptance against only their
matching published D4 database. Every root has ten named nonempty JNN/log/
trainer/train-DB/test-DB folds, the exact one-element reference energy and
5,000-epoch trainer card, finite final MAE-E/MAE-F diagnostics, and exact
450/50 disjoint D4 folds. Each of the 500 D4 rows occurs once in test and
nine times in train across the committee; fold rows exactly match the
corresponding `current.db` row including geometry, calculator results, and
metadata. E4 roots remain absent.

| Element | M4 JNN digest | Selected-epoch range | Test MAE-E (meV/atom) | Test MAE-F (meV/A) | Ratio <=1.25 | Lowest eligible E4 candidate |
|---|---|---:|---:|---:|---:|---|
| W | `93e2e42ae7014f79522678ff164e786519d12cde21e59d3cfe1ecef7d9a8dbfd` | 1199-3545 | 7.483-9.638 | 197.5-215.0 | 10/10 | `train-5/5.jnn` |
| Ta | `ef116327379709feeb4364e02cbfc1aeb0a43b80d90900117295937117094ebd` | 788-4967 | 6.138-8.956 | 155.8-195.7 | 9/10 | `train-2/2.jnn` |
| Ti | `e551af6ca2bfbfe34926e7951330efd1e5f86a9dd1aa88c6f02681e69d02fd1e` | 698-3337 | 4.601-5.881 | 121.1-140.5 | 10/10 | `train-9/9.jnn` |

The one ineligible Ta fold is retained in committee provenance but will be
excluded by the explicit E4 maximum train/test energy-MAE ratio of 1.25.

### E4 fixed-reference evaluation and acceptance

The no-overwrite preflight confirmed absent `E4_M4` roots, unchanged D4
database/M4-committee digests, and immutable fixed Protocol-B references. Each
reference has 57 unique points (19 bcc, 19 fcc, 19 hcp), with matching
metadata/reference keys and structure-dependent atom counts (bcc 2; fcc and
hcp 4). The successful protected commands were:

```bash
module load jse
python3 src/eos_check_jnn.py \
  --element <W|Ta|Ti> \
  --metadata results/<X>_eos_benchmark/eos_reference/eos_structures.csv \
  --reference-csv results/<X>_eos_benchmark/eos_reference/eos_reference.csv \
  --jnn-root <X>-potential/fcc-restart/model_versions/M4_from_D4/train-committee \
  --model-id E4_M4 \
  --output-dir <X>-potential/fcc-restart/evaluations \
  --max-train-test-ratio 1.25
```

Use the Python entry point after loading JSE. The JSE Python runner lacks
`__file__` and is not compatible with this evaluator.

Full read-only acceptance passed for all three `evaluations/E4_M4/` roots.
Each contains exactly the seven nonempty expected artifacts (`best_jnn.txt`,
selection CSV, raw/merged prediction CSVs, metric CSV, and two valid PNGs).
The tables contain ten folds, the selected lowest eligible test-energy-MAE
model, 57 finite raw and 57 finite merged predictions, exact fixed-reference
key/atom-count coverage, element-local POSCAR/JNN paths, recomputable raw and
phase-aligned errors, finite phase/aggregate metrics, and valid grid minima.

| Element | Selected M4 JNN | Eligible folds | Aggregate raw MAE / RMSE / max | Aggregate phase-aligned MAE / RMSE / max |
|---|---|---:|---:|---:|
| W | `train-5/5.jnn` | 10/10 | 53.287499 / 66.725101 / 127.546758 | 16.061060 / 22.359835 / 60.837811 |
| Ta | `train-2/2.jnn` | 9/10 | 73.655557 / 91.010545 / 148.739521 | 9.142611 / 12.892971 / 37.839024 |
| Ti | `train-9/9.jnn` | 10/10 | 31.118935 / 40.339243 / 73.069439 | 2.870559 / 3.789335 / 8.838018 |

All EOS errors in the table are meV/atom. Relative to the archived E3
aggregate raw / phase-aligned MAE, the E4 changes are W
`-22.774397 / -4.241467`, Ta `+1.281634 / +1.800237`, and Ti
`-0.825067 / -1.816033` meV/atom. This is a recorded fixed-reference
comparison only, not a quality gate that starts D5.

The post-run protected-state audit reconfirmed the published 500-row D4
database hashes, the ten-file M4 JNN digests, and Protocol-B CSV hashes:

| Element | D4 `current.db` | M4 JNN digest | Metadata / reference CSV |
|---|---|---|---|
| W | `1242b2f534f1bebc2730102b0e1c5d8b524c0adaee2a75259d687deecfa57480` | `93e2e42ae7014f79522678ff164e786519d12cde21e59d3cfe1ecef7d9a8dbfd` | `d0fa9889b18797990d33114f91850c3710ee9b7b0c40856733cbdec392fa4a3d` / `d4360e843da262499a202613704cc73b483e3f74d8a016282da8d7179b512f64` |
| Ta | `600bd1c0c7d205771fe7b9859731e9af05399498e4c9ae6757c9de3bb9616989` | `ef116327379709feeb4364e02cbfc1aeb0a43b80d90900117295937117094ebd` | `16d5f83cd5a994109b17a66846a5091a718cfb6ce61d7f13f19a6e543222dc4f` / `869d901829f0682cb169923b1f0745e8e7503cff5385efb2a84bc53c1a06f4ab` |
| Ti | `8db00646830c0cbb81037130881815b344f9be4f893a47e3d4a2dde075d2322b` | `e551af6ca2bfbfe34926e7951330efd1e5f86a9dd1aa88c6f02681e69d02fd1e` | `3c11ea72890c9d0a1f336b7b609190b980fafdc8878c55d7af74d4cff0ad5ffb` / `1a5f38ae444e9412c9bb0d5cfa5c15e0af89b1af3e1f675892276c6c3c93a541` |

JSE created/reused only normal selected-fold inference cache libraries:
W `train-5/lib5_449de9df543f18bd.so`, Ta
`train-2/lib2_449de9df543f18bd.so`, and Ti
`train-9/lib9_449de9df543f18bd.so`. The unchanged combined JNN digests show
that no model content changed. No EOS row or metadata entered any
`current.db`; no D5/RSS calculation was submitted.
