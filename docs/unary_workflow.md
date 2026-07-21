# Staged Unary Workflow

This guide applies once for W, once for Ta, and once for Ti. Replace `<X>` and
all placeholders with approved element-specific values. Never substitute an
asset from another element.

## 1. Preflight

```bash
module load jse
python3 -m py_compile src/*.py
python3 src/vasp_batch_dft.py --help
python3 src/eos_reference.py --help
```

Verify:

```text
structures/<X>_benchmark/<X>-seed.poscar
structures/<X>_benchmark/<X>-<phase>.poscar
POTCAR/PBE/<X>/POTCAR
```

Record PAW checksum/ENMAX, frozen Protocol A/B, atomic reference energy,
seed/MD settings, and physical-gate thresholds in a task record. Do not submit
anything at this step.

## 2. EOS Reference

Generate an explicit, fixed EOS grid:

```bash
python3 src/eos_reference.py generate \
  --structure <phase>=structures/<X>_benchmark/<X>-<phase>.poscar \
  --output-dir results/<X>_eos_benchmark/eos_reference \
  --metadata results/<X>_eos_benchmark/eos_reference/eos_structures.csv \
  --scales <approved scale values>
```

Label each phase directory with Protocol B through SLURM:

```bash
sbatch scripts/slurm/run_vasp_batch_dft.slurm \
  results/<X>_eos_benchmark/eos_reference/nncalc_input_by_structure/<phase> \
  results/<X>_eos_benchmark/eos_reference/<X>_eos_dft_<phase>.db \
  <magmom> <eos-kspacing> <eos-encut>
```

Then collect only those validation DBs:

```bash
python3 src/eos_reference.py collect \
  --metadata results/<X>_eos_benchmark/eos_reference/eos_structures.csv \
  --dft-db <phase>=results/<X>_eos_benchmark/eos_reference/<X>_eos_dft_<phase>.db \
  --output-csv results/<X>_eos_benchmark/eos_reference/eos_reference.csv
```

## 3. Baseline and Sampling

Create D0 with Protocol A, train M0, and evaluate E0 using separately
approved SLURM commands. Use:

```text
<X>-potential/current.db
<X>-potential/model_versions/M0_from_D0/train-committee/
results/<X>_eos_benchmark/evaluations/E0_M0/
```

Submit an explicitly approved NVT or NPT sweep using
`scripts/slurm/run_md_round.slurm`. For NPT, first demonstrate that every
committee model returns finite stress. Check every output trajectory/log before
selection.

## 4. Selection

First run full-committee all-frame scoring with
`src/stratified_uncertainty_selection.py` and retain its
`uncertainty_all_frames.csv`. Determine the current model's `U_min`,
`U_tail`, `N_tail_max`, gaps, total target, source quota feasibility, and
physical gates before executing the following skeleton:

```bash
python3 src/absolute_u_projected_cur_selection.py \
  --round-dir <X>-potential/01-nvt-round-1 \
  --all-frames <X>-potential/01-nvt-round-1/uncertainty_all_frames.csv \
  --base <X>-potential/current.db \
  --output-root <X>-potential/01-nvt-round-1/absolute-u-projected-cur \
  --u-min <calibrated-U-min> \
  --candidate-frame-gap <approved-gap> \
  --target <approved-DFT-budget> \
  --tail-threshold <calibrated-U-tail> \
  --tail-max <approved-tail-cap> \
  --final-frame-gap <approved-gap>
```

The output is protected. Validate source allocation, U range, final frame
gaps, descriptor/CUR records, geometry limits, and provenance before DFT.

## 5. DFT, Dk, Mk, and Ek

Submit final selected POSCARs with a unique `<X>`-local work directory and
new-label DB. Validate the label DB, merge it only into that element's current
DB, train Mk, and perform the fixed EOS Ek evaluation. Compare Ek with E0 and
all prior Ek values before approving another round.
