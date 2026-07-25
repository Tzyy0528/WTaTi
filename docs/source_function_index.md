# W-Ta-Ti Source Function Index

Read `research-plan.md` before selecting an entry point. All production work is
element-isolated and staged; `src/ase_md.py` is not the production scheduler.

| Goal | Entry point | Use |
|---|---|---|
| Prepare/run/collect VASP labels | `src/vasp_batch_dft.py` | Use `label` via `scripts/slurm/run_vasp_batch_dft.slurm`; repository-local PAW files are read from `POTCAR/PBE/<element>/POTCAR`. |
| Merge new labels into an element DB | `src/vasp_batch_dft.py merge` | Base, labeled, and output DB paths must be distinct. |
| Train a committee | `src/dbselectandtrain.py::db_select_and_train()` | First audit W/Ta/Ti `ENERGY` values against Protocol A. The default is 5000 epochs; submit through `scripts/slurm/run_train_committee.slurm`. |
| Run one staged NVT/NPT sweep | `scripts/slurm/run_md_round.slurm` and `src/md_worker.py` | Use all committee models. NPT requires finite stress from every model. |
| Score all MD production frames | `scripts/slurm/run_uncertainty_scoring.slurm` and `src/stratified_uncertainty_selection.py` | Use `--score-only` and retain `uncertainty_all_frames.csv`; do not create or use percentile-bin candidates. |
| MD selection | `scripts/slurm/run_absolute_u_projected_cur.slurm` and `src/absolute_u_projected_cur_selection.py` | Calibrated absolute-U cutoff, auditable volume/force/distance gates, source-aware current.db-projected CUR, and an approved tail cap. Equal source quotas are opt-in only and require explicit approval. |
| Compute descriptors/CUR projection | `src/CUR.py`, `src/quota_cur_selection.py` | Called by the absolute-U selector; tune descriptor parameters only with an explicit record. |
| Generate fixed EOS structures | `src/eos_reference.py generate` | Always provide explicit `--structure`, `--output-dir`, and `--metadata` arguments. |
| Collect EOS DFT reference | `src/eos_reference.py collect` | Use only validation DBs and an explicit `--dft-db` list. |
| Evaluate a committee on EOS | `src/eos_check_jnn.py` plus `src/eos_predict_jnn.groovy` | Fixed reference only; parses final `MAE-E` fold diagnostics, uses JSE/Groovy NNAP inference, and writes protected predictions, phase metrics, and plots. |
| Optional RSS pool | `src/rss_sampling_embedded.py` | Use its `0,20e4,40e4` bar Mini pressures and the unary default atom counts; do not use quota-CUR as the final selector. |

## Source Constraints

- `src/vasp_batch_dft.py` is the supported new-label backend. The
  `dft_calculation.py`/`eos_reference.py run-dft` `nncalc` path is legacy and
  must not be submitted for new work.
- `src/temperature_table.py` contains W/Ta/Ti normal-pressure phase-change
  data and supplies the high-temperature liquid/near-liquid target for each
  element. The staged workflow still records the exact temperature passed to
  each submitted command.
- `src/absolute_u_projected_cur_selection.py` accepts a saved all-frame CSV;
  quote model globs when passing them to the preceding JSE scoring command.
