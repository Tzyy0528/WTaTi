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

Record PAW checksum/ENMAX, frozen Protocol A/B, atomic reference energy, and
MD settings in a task record. Do not submit anything at this step.

The current `W`/`Ta`/`Ti` seed POSCARs already contain 16 atoms as explicit
`2 x 2 x 2` supercells. Use `--rep 1 1 1` when sampling from them to retain a
16-atom MD cell. A further `--rep 2 2 2` produces 128 atoms and requires an
explicitly approved parameter card.

## 2. EOS Reference

Generate explicit, fixed EOS grids for all three required phases (`bcc`, `fcc`,
and `hcp`) of the current element. Repeat the command with an explicit
`--structure` argument for each phase, and label/collect every phase DB:

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
`uncertainty_all_frames.csv`. Pass `--score-only` so percentile-bin candidate
files are not created. Submit this through
`scripts/slurm/run_uncertainty_scoring.slurm`. Determine the current model's
`U_min` from the final test `MAE-F` values in logs of all models used for
sampling. Use their arithmetic mean, converted from meV/A to eV/A; do not set
it from an MD-pool percentile. Recalculate it independently for every element
and round. Record all ten values, the aggregation rule, model paths, and
numeric result. Then determine the total
target and CUR descriptor
parameters before submitting the
following CUR command through `scripts/slurm/run_absolute_u_projected_cur.slurm`:

```bash
sbatch --output <X>-potential/01-nvt-round-1/slurm_logs/cur-%j.out \
  scripts/slurm/run_absolute_u_projected_cur.slurm \
  --round-dir <X>-potential/01-nvt-round-1 \
  --all-frames <X>-potential/01-nvt-round-1/uncertainty_all_frames.csv \
  --base <X>-potential/current.db \
  --output-root <X>-potential/01-nvt-round-1/absolute-u-projected-cur \
  --u-min <calibrated-U-min> \
  --target <approved-DFT-budget> \
  --tail-quantile 0.99 \
  --tail-max <floor(0.05*approved-DFT-budget)> \
  --min-distance <0.80*D0-min-distance-A> \
  --max-normalized-void <1.15*D0-max-q-void> \
  --r-c 6.0 \
  --n-max 5 \
  --l-max 6 \
  --similarity-threshold 0.99999
```

No candidate or final temporal frame gap is passed. The only ordinary
physical hard rejections are periodic minimum-distance overlap and the
normalized periodic maximum-empty-sphere void metric. Committee force,
volume, pressure, and source composition are retained as diagnostics, not
ordinary hard filters. The output is protected. The selector writes
physical-gate rejections, candidate/selected POSCARs, source/tail
distributions, and parameter provenance. Validate its U range, distance/void
records, descriptor/CUR records, finite geometry, source allocation, and tail
cap before DFT.

`--balance-sources` imposes an equal quota across all surviving sources. It is
not a default source constraint and must be used only with an explicitly
approved source-quota policy. Without it, source composition is an auditable
CUR outcome rather than a hard selection constraint.

## 5. DFT, Dk, Mk, and Ek

Submit final selected POSCARs with a unique `<X>`-local work directory and
new-label DB. Validate the label DB, merge it only into that element's current
DB, train Mk, and perform the fixed EOS Ek evaluation. Compare Ek with E0 and
all prior Ek values before approving another round.

Committee training uses ten models, five concurrent workers, eight threads per
worker, and 5000 epochs by default. Pass the epoch count explicitly in every
production submission; do not reuse the historical 1000-epoch M0/M1 outputs.
