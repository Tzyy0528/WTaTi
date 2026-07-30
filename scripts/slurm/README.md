# SLURM Templates

These scripts are templates for expensive W, Ta, and Ti unary-potential jobs.
Submit from this workspace root and edit resource directives (`partition`,
`account`, wall time, CPU/GPU requests) for the local cluster before
production use. Run only one element-local workflow path per command.

All scripts load the JSE environment internally:

```bash
module load jse
```

## 1. Python VASP batch DFT labeling

For new DFT labeling work, use `run_vasp_batch_dft.slurm`. It requests one
node with 64 SLURM tasks by default:

```bash
#SBATCH --nodes=1
#SBATCH --ntasks=64
```

It does not set an explicit `#SBATCH --time` by default. The cluster partition
may still impose a default or maximum wall time. The backend launches one
`srun --exclusive -n <CORES_PER_JOB> vasp_std` step per structure and runs
multiple structures concurrently in the allocation.

Generic form:

```bash
sbatch scripts/slurm/run_vasp_batch_dft.slurm \
  <input_structure_dir> \
  <output.db> \
  [magmom=_] [kspacing=0.2] [encut=auto]
```

Default resource logic:

```text
64 total SLURM tasks
8 MPI ranks per VASP task by default (`CORES_PER_JOB=8`)
8 concurrent VASP tasks by default (`MAX_WORKERS=64/8`)
`NCORE=2` in generated INCAR files
explicit `ENCUT = 1.3 * max(POTCAR ENMAX)` unless the fifth positional argument overrides it
```

Generic Protocol-A/B labeling example:

```bash
sbatch scripts/slurm/run_vasp_batch_dft.slurm \
  <X>-potential/<round>/absolute-u-projected-cur/<selected-poscar-dir> \
  <X>-potential/<round>/<X>_selected_labeled.db \
  <approved-magmom> <approved-kspacing> <approved-encut>
```

Existing output DBs are protected. To replace one explicitly:

```bash
OVERWRITE=1 FORCE_PREPARE=1 sbatch scripts/slurm/run_vasp_batch_dft.slurm <input_structure_dir> <output.db> [magmom] [kspacing] [encut=auto]
```

Useful environment overrides:

```bash
WORK_DIR=...       # default: <output_db_dir>/dft/vasp_<output_stem without _labeled>
CORES_PER_JOB=8    # MPI ranks per VASP task
MAX_WORKERS=...    # concurrent VASP tasks
VASP_COMMAND=...   # default: vasp_std
NCORE=2            # VASP parallelization setting written to INCAR
PROGRESS_INTERVAL=60
ENCUT_FACTOR=1.3   # default factor multiplied by max POTCAR ENMAX
PREPARE_ONLY=1     # prepare/reuse input folders only
FORCE_PREPARE=1    # rewrite prepared inputs
KEEP_CHGCAR=1      # keep CHGCAR files after each task
```

No legacy `nncalc` submission template is included in this standalone
workspace. Do not use or restore that path for new active DFT labeling unless
explicitly requested.

## 2. NNAP committee training

Generic form:

```bash
sbatch scripts/slurm/run_train_committee.slurm \
  <input.db> \
  <train-committee-dir> \
  [committee_size=10] [train_workers=5] [epochs=5000]
```

`committee_size` must be at least 2 because the current training splitter builds cross-validation folds.

Default resource logic:

```bash
#SBATCH --nodes=1
#SBATCH --ntasks=5
#SBATCH --cpus-per-task=8
```

This means:

```text
10 total committee potentials
5 potentials trained concurrently
5000 training epochs by default
8 cores/threads per potential
40 cores requested in total
```

The 8-thread setting is already in the generated `Trainer.groovy` through `TrainJse.Conf.THREAD_NUMBER = 8`.

Example:

```bash
sbatch scripts/slurm/run_train_committee.slurm \
  <X>-potential/current.db \
  <X>-potential/model_versions/M0_from_D0/train-committee \
  <approved-committee-size> <approved-workers> <approved-epochs>
```

The script calls:

```python
from dbselectandtrain import db_select_and_train
```

and runs `db_select_and_train(input_db, train_dir, number=committee_size, max_parallel=train_workers, epochs=epochs)`.

Existing non-empty training directories are protected. To replace one explicitly:

```bash
OVERWRITE=1 sbatch scripts/slurm/run_train_committee.slurm <input.db> <train-committee-dir> [committee_size] [train_workers] [epochs]
```

## 3. ASE MD round

For the normal active-learning workflow, use `run_md_round.slurm`. It submits one NVT/NPT round as multiple parallel one-core MD workers in a single allocation: one `srun -n1` worker per scale factor or pressure.

Recommended usage is to run the script directly from the repository root. It
requires an explicit, approved NVT scale list or NPT pressure list, explicit
supercell repetition, and (for NPT) an approved `--bulk-modulus-gpa` or
`--pfactor`. It counts the supplied list and self-submits with matching
`sbatch -n <count>`.

NVT example:

```bash
bash scripts/slurm/run_md_round.slurm \
  --ensemble nvt \
  --round-dir <X>-potential/01-nvt-round-1 \
  --poscar structures/<X>_benchmark/<X>-seed.poscar \
  --rep <NX> <NY> <NZ> \
  --temperature <approved-temperature-K> \
  --scale-factors <s1> <s2> ... \
  --tau-r <approved-tau-r> \
  --steps <approved-steps> \
  --write-interval <approved-write-interval> \
  --log-interval <approved-log-interval> \
  --jnn-paths \
    <X>-potential/model_versions/M0_from_D0/train-committee/train-0/0.jnn \
    <X>-potential/model_versions/M0_from_D0/train-committee/train-1/1.jnn \
    <X>-potential/model_versions/M0_from_D0/train-committee/train-2/2.jnn
```

NPT example skeleton:

```bash
bash scripts/slurm/run_md_round.slurm \
  --ensemble npt \
  --round-dir <X>-potential/02-npt-round-1 \
  --poscar structures/<X>_benchmark/<X>-seed.poscar \
  --rep <NX> <NY> <NZ> \
  --temperature <approved-temperature-K> \
  --pressures <p1> <p2> ... \
  --bulk-modulus-gpa <approved-value> \
  --tau-r <approved-tau-r> \
  --steps <approved-steps> \
  --write-interval <approved-write-interval> \
  --log-interval <approved-log-interval> \
  --jnn-paths path/to/0.jnn path/to/1.jnn path/to/2.jnn
```

The examples self-submit using the count of their explicitly supplied NVT/NPT
conditions. If you prefer calling `sbatch` directly, provide `-n` manually:

```bash
sbatch -n 6 scripts/slurm/run_md_round.slurm --ensemble nvt ... --jnn-paths ...
```

Use committee models for MD sampling. The `best .jnn` selection is for EOS checking, not for active-learning MD exploration.

Outputs are written under:

```text
<round-dir>/md/scale-*/
<round-dir>/md/P-*GPa/
```

Each child MD directory gets `command.sh`, `log`, `multi_nnap_md.xyz`, and `energy_forces_summary.dat`.

## 4. Single ASE MD worker

`run_md_worker.slurm` is kept for debugging or rerunning one MD condition manually. It submits exactly one `src/md_worker.py` job and forwards the normal MD worker options.

Example:

```bash
sbatch scripts/slurm/run_md_worker.slurm \
  --ensemble nvt \
  --work-dir <X>-potential/md/M0_nvt_scale_1 \
  --poscar structures/<X>_benchmark/<X>-seed.poscar \
  --temperature <approved-temperature-K> \
  --scale-factor 1.0 \
  --tau-r 0.1 \
  --steps 50000 \
  --jnn-paths path/to/0.jnn path/to/1.jnn path/to/2.jnn
```

## 5. RSS/Mini candidate-pool generation

`run_rss_round.slurm` runs exactly one element-local
`src/rss_sampling_embedded.py` generation process directly inside a one-node,
one-task, 24-hour allocation. JSE must not be wrapped in `srun` for this
driver. It generates and retains RSS/Mini structures only; it does not score
a pool, select DFT candidates, label, train, or evaluate.

The RSS output root must be absent. The template rejects an existing root and
never forwards `--overwrite`; raw and minimized work are retained for later
provenance validation. Submit with explicit approved parameters, for example:

```bash
sbatch \
  --output <X>-potential/<round>/slurm_logs/rss-%j.out \
  --error <X>-potential/<round>/slurm_logs/rss-%j.err \
  scripts/slurm/run_rss_round.slurm \
  --element <X> \
  --jnn <X>-potential/model_versions/Mk_from_Dk/train-committee/train-N/N.jnn \
  --out-dir <X>-potential/<round>/rss \
  --atomic-volume <approved-A3-per-atom> \
  --nstructs <approved-raw-count> \
  --natoms-list 9,10,12,15,18,20,22,25 \
  --mini-press-list 0,200000,400000 \
  --mini-keyword tri --mini-loop 10 \
  --mini-etol 1e-4 --mini-ftol 1e-8
```

The RSS driver has one unary case, so the template fixes `--jobs 1`; it is
not a multi-case parallel launcher. Adjust partition, account, and wall time
for the local cluster before production use.

## 6. RSS all-frame scoring and projected-CUR selection

`run_rss_selection_pipeline.slurm` is the protected companion to a completed
RSS/Mini pool. It requires an absent `<round>/rss-selection/` root, validates
the retained flat/minimized/raw manifest chain, and refuses a provenance
mismatch before scoring. It then runs, in one one-node/one-task/24-hour
allocation:

```text
all ten M4 models -> RSS all-frame uncertainty/source-map artifacts
-> absolute-U periodic geometry audit -> current.db-projected CUR
```

It uses the frozen unary D5 card (50 raw structures for each of
`9,10,12,15,18,20,22,25` atoms; Mini pressures `0,200000,400000` bar), derives
the ten-log mean test-force `U_min`, uses no frame gaps, and fixes the p99
tail cap to `floor(target/20)`. It writes no DFT, database, training, or EOS
output, and it does not call `rss_quota_cur_selection.py`.

Normally every raw/pressure source must pass retained provenance validation.
With explicit scientific approval, `--mini-failure-log
<round>/rss/logs/unary-<X>.log` accepts a partial pool only by excluding the
exact `exit=1` pairs in the final JSE `LMP FAIL LIST`. It writes
`mini_failure_exclusions.csv` with the log path/checksums and observed failed
artifacts, while every nonfailed source remains mandatory. It never scores or
selects a logged Mini failure.

Example:

```bash
sbatch \
  --output <X>-potential/05-rss-round-1/slurm_logs/rss-select-%j.out \
  --error <X>-potential/05-rss-round-1/slurm_logs/rss-select-%j.err \
  scripts/slurm/run_rss_selection_pipeline.slurm \
  --element <X> \
  --round-dir <X>-potential/05-rss-round-1 \
  --base <X>-potential/fcc-restart/current.db \
  --jnn-glob '<X>-potential/fcc-restart/model_versions/M4_from_D4/train-committee/train-*/*.jnn' \
  --target 100 \
  --min-distance <approved-A> \
  --max-normalized-void <approved-normalized-void> \
  --r-c 6.0 --n-max 5 --l-max 6 --similarity-threshold 0.99999 \
  [--mini-failure-log <round>/rss/logs/unary-<X>.log]
```
