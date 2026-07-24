# W-Ta-Ti Unary Active-Learning Workspace

This clean workspace is for three separate NNAP potentials:

```text
W only   -> W-potential/
Ta only  -> Ta-potential/
Ti only  -> Ti-potential/
```

It deliberately contains no structures, PAW files, DFT labels, databases,
models, trajectories, or results. It must not be used to train a combined
W-Ta-Ti alloy potential.

## Included

- `research-plan.md`: mandatory scientific workflow.
- `src/`: portable ASE/NNAP utilities, including the VASP batch backend and
  absolute-U projected-CUR selector.
- `scripts/slurm/`: VASP-labeling, committee-training, and MD templates.
- `docs/`: source map and staged operating guide.
- `structures/`: empty locations for input and EOS-reference structures.
- `POTCAR/PBE/`: empty locations for locally licensed PAW-PBE files.
- `results/` and `memory/`: initially empty output and task-record roots.

## Add These Inputs First

```text
structures/W_benchmark/W-seed.poscar
structures/W_benchmark/W-<phase>.poscar
structures/Ta_benchmark/Ta-seed.poscar
structures/Ta_benchmark/Ta-<phase>.poscar
structures/Ti_benchmark/Ti-seed.poscar
structures/Ti_benchmark/Ti-<phase>.poscar

POTCAR/PBE/W/POTCAR
POTCAR/PBE/Ta/POTCAR
POTCAR/PBE/Ti/POTCAR
```

`*-seed.poscar` is the source for initial perturbations. The `*-<phase>.poscar`
files are fixed, validation-only EOS inputs. They may describe the same
unrelaxed reference phase but must remain distinct input assets: generated EOS
scales and EOS labels never enter a training database.

For each of W, Ta, and Ti, bcc, fcc, and hcp are mandatory EOS-validation
phases. W/Ta use bcc as the primary phase; Ti uses hcp and bcc as primary
phases. The scale intervals must still be approved separately for every
element/phase.

## Before Any Calculation

1. Read `research-plan.md` and supply the missing per-element DFT protocol.
2. Check each supplied POSCAR is periodic, contains exactly one element, and
   has the intended phase/cell definition.
3. Check the PAW setup names, checksums, ENMAX values, and POSCAR species
   order. The VASP backend reads from `POTCAR/PBE/<element>/POTCAR`.
4. Converge and freeze active-label Protocol A and EOS-reference Protocol B
   separately for each element. Decide PAW variant, semicore treatment,
   smearing, spin, and whether SOC is included.
5. Audit or replace the W/Ta/Ti atomic reference energies in
   `src/dbselectandtrain.py` so they match Protocol A.
6. Set element-specific seed, MD, NPT, physical-gate, and selection calibration
   parameters. `src/temperature_table.py` is intentionally unconfigured.

## Active-Learning Workflow

```text
input structures + frozen Protocol A/B
-> D0 -> M0 -> fixed EOS E0
-> MD candidate pool + all-frame scoring
-> calibrated absolute-U cutoff + source decorrelation
-> physical gates + projected source-constrained CUR + tail cap
-> element-local DFT labels -> Dk -> Mk -> fixed EOS Ek
```

Run the W, Ta, and Ti sequences independently. Do not invoke the automatic
`src/ase_md.py` scheduler for production work; follow
`docs/unary_workflow.md`.

## Lightweight Checks

```bash
module load jse
python3 -m py_compile src/*.py
python3 src/vasp_batch_dft.py --help
python3 src/eos_reference.py --help
python3 src/absolute_u_projected_cur_selection.py --help
```

Do not run VASP, NNAP training, MD, RSS, or full-committee scoring on a login
node.
