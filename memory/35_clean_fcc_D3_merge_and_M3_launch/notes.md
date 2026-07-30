# Notes: Clean-FCC D3 Merge and M3 Launch

## Sources

### Source 1: D3 label acceptance
- Path: `memory/34_clean_fcc_D3_label_validation/`
- Key points:
  - Each D3 label DB has 100 validated finite unary 32-atom rows.
  - Its matching D2 `current.db` is unchanged with 300 rows.

### Source 2: Research-plan D3 transition
- Path: `research-plan.md`, section 11.
- Key points:
  - Merge via distinct base/new/updated paths; validate the 400-row
    base-prefix/new-suffix result before publishing.
  - M3 uses only published D3 data with ten models, five workers, and 5,000
    epochs.

## Commands and Observations

```bash
module load jse
python3 src/vasp_batch_dft.py merge \
  <X>-potential/fcc-restart/current.db \
  <X>-potential/fcc-restart/03-npt-round-1/<X>_D3_labeled.db \
  <X>-potential/fcc-restart/03-npt-round-1/updated.db
```

## Synthesized Findings

### Authorization
- The user explicitly authorized D3 dataset merging and M3 training for W,
  Ta, and Ti.

### Merge preflight, validation, and publication

No-overwrite preflight passed for all elements: each independent base/label/
updated path was distinct; base and D3 labels have 300 and 100 finite unary
32-atom rows, respectively; the base was byte-identical to its protected D2
`updated.db`; the D3 `updated.db` and M3 roots were absent; and no EOS
metadata was present. The frozen training references in
`src/dbselectandtrain.py` are W `-12.9581`, Ta `-11.8578`, and Ti
`-7.8951` eV.

The supported merges completed without `--overwrite`. Read-only validation
then confirmed 400 finite unary 32-atom rows per result, exact semantic
300-row D2 prefix plus 100-row D3-label suffix, and no EOS data. Each
verified `updated.db` was copied to a same-directory temporary path,
checksum-verified, and atomically published as only the matching
`current.db`.

| Element | Published 400-row D3 SHA-256 |
|---|---|
| W | `566bd0cfd13d0e231b692589de91e6f94b3cf51753753e6fce3ca8a70d9659af` |
| Ta | `09ab573a20cf35b29c121f1584492a8da5e87d5a97cba4f647802764ca6a1c20` |
| Ti | `0a0647a1ec9160124c0a5c24c0838442b7e4f390411d52cffa1f25dfa3d985be` |

### M3 training preflight and submissions

The no-overwrite M3 preflight passed: every published `current.db` has 400
finite unary rows and no EOS data; each M3 root was absent; scheduler-log
roots existed; and the frozen reference energies above match the active
source. The submitted resource card is one node, five tasks, eight CPUs per
task, 48 hours, with ten committee members, five concurrent workers, and
5,000 epochs:

```bash
env -u OVERWRITE sbatch --parsable \
  --job-name=fcc_m3_<X> --nodes=1 --ntasks=5 --cpus-per-task=8 \
  --time=48:00:00 \
  --output=<X>-potential/fcc-restart/slurm_logs/fcc-m3-%j.out \
  --error=<X>-potential/fcc-restart/slurm_logs/fcc-m3-%j.err \
  scripts/slurm/run_train_committee.slurm \
  <X>-potential/fcc-restart/current.db \
  <X>-potential/fcc-restart/model_versions/M3_from_D3/train-committee \
  10 5 5000
```

| Element | M3 job | One immediate status check |
|---|---:|---|
| W | `13540` | `RUNNING` on `lpsnode03` |
| Ta | `13541` | `RUNNING` on `dreamx-cpu` |
| Ti | `13542` | `PENDING (Resources)` |

No polling loop is active. E3 has not been submitted.
