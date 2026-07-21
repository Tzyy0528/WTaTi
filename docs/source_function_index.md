# W-Ta-Ti Source Function Index

Read `research-plan.md` before selecting an entry point. All production work is
element-isolated and staged; `src/ase_md.py` is not the production scheduler.

| Goal | Entry point | Use |
|---|---|---|
| Prepare/run/collect VASP labels | `src/vasp_batch_dft.py` | Use `label` via `scripts/slurm/run_vasp_batch_dft.slurm`; repository-local PAW files are read from `POTCAR/PBE/<element>/POTCAR`. |
| Merge new labels into an element DB | `src/vasp_batch_dft.py merge` | Base, labeled, and output DB paths must be distinct. |
| Train a committee | `src/dbselectandtrain.py::db_select_and_train()` | First audit W/Ta/Ti `ENERGY` values against Protocol A. |
| Run one staged NVT/NPT sweep | `scripts/slurm/run_md_round.slurm` and `src/md_worker.py` | Use all committee models. NPT requires finite stress from every model. |
| Score all MD production frames | `src/stratified_uncertainty_selection.py` | Retain `uncertainty_all_frames.csv`; do not use its percentile candidates as final selection. |
| MD selection | `src/absolute_u_projected_cur_selection.py` | Calibrated absolute-U cutoff, source gaps, current-DB projection, source floor/ceil quotas, and tail cap. |
| Compute descriptors/CUR projection | `src/CUR.py`, `src/quota_cur_selection.py` | Called by the absolute-U selector; tune descriptor parameters only with an explicit record. |
| Generate fixed EOS structures | `src/eos_reference.py generate` | Always provide explicit `--structure`, `--output-dir`, and `--metadata` arguments. |
| Collect EOS DFT reference | `src/eos_reference.py collect` | Use only validation DBs and an explicit `--dft-db` list. |
| Evaluate a committee on EOS | `src/eos_check_jnn.py` | Fixed reference only; selected committee model must have an auditable fold diagnostic. |
| Optional RSS pool and selection | `src/rss_sampling_embedded.py`, `src/rss_quota_cur_selection.py` | Use only after separately approving the absolute-U/source/atom-count policy. |

## Source Constraints

- `src/vasp_batch_dft.py` is the supported new-label backend. The
  `dft_calculation.py`/`eos_reference.py run-dft` `nncalc` path is legacy and
  must not be submitted for new work.
- `src/temperature_table.py` intentionally has no W/Ta/Ti data. Do not use
  automatic temperature scheduling until it is populated from approved
  sources, and do not use it instead of the staged workflow.
- `src/absolute_u_projected_cur_selection.py` accepts a saved all-frame CSV;
  quote model globs when passing them to the preceding JSE scoring command.
