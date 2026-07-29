# W-Ta-Ti Unary Active-Learning Workspace

This is an active workspace for three independent unary NNAP potentials:

```text
W only   -> W-potential/
Ta only  -> Ta-potential/
Ti only  -> Ti-potential/
```

It is not a W-Ta-Ti alloy workflow. Databases, seed structures, committees,
candidate pools, trajectories, selections, DFT work directories, and
validation results must remain element-local at every stage.

## Repository Map

- `research-plan.md`: authoritative scientific protocol, selection policy,
  validation gates, and stop/continue decisions.
- `docs/source_function_index.md`: map from a workflow goal to the supported
  executable entry point.
- `docs/unary_workflow.md`: detailed staged operating guide and command
  patterns.
- `src/`: active ASE/NNAP implementation, including VASP batch labeling and
  projected-CUR selection.
- `scripts/slurm/`: protected submission templates for VASP, training, MD,
  and combined approved MD selection.
- `<X>-potential/`: element-local generated workflow roots and `current.db`
  cross-round state for `X = W, Ta, Ti`.
- `structures/`: supplied seed and fixed EOS-reference structures.
- `POTCAR/PBE/<X>/POTCAR`: local licensed PAW-PBE inputs; do not commit or
  redistribute POTCAR files.
- `results/<X>_eos_benchmark/`: fixed validation-only EOS assets.
- `memory/`: retained task plans, observations, and deliverables.

Generated data already exist in this workspace. They are protected by
default: do not overwrite, delete, copy between elements, or replace them
without explicit approval.

## Non-Negotiable Data Policy

- Keep W, Ta, and Ti fully isolated. Never create a mixed-element database,
  committee, candidate pool, selection, trajectory, or EOS result.
- Each element's `current.db` is its cross-round training state. New labels
  are validated and merged only into the matching element-local database.
- EOS structures, labels, databases, and metrics are validation-only and
  must never enter `current.db`.
- New labels use `src/vasp_batch_dft.py` through
  `scripts/slurm/run_vasp_batch_dft.slurm`; do not use the legacy `nncalc`
  path.
- Freeze per-element active-label Protocol A and EOS-reference Protocol B
  before producing labels. Record PAW identity/checksum, ENCUT, k-point and
  smearing policies, convergence, relaxation/static choice, and the W/Ta
  SOC/semicore or Ti spin/valence decisions.

## Production Workflow

```text
frozen Protocol A/B + element-local inputs
-> D0 -> M0 -> fixed-reference E0
-> element-local MD/RSS candidates
-> all-frame committee uncertainty scoring
-> calibrated absolute-U cutoff
-> source-wise decorrelation + approved physical/risk gates
-> current.db-projected, source-constrained CUR + capped p99 U tail
-> Protocol-A DFT labels -> Dk -> Mk -> fixed-reference Ek
```

The required selection chain is:

```text
current committee
-> all-frame scoring
-> element/model-specific absolute-U cutoff
-> candidate-frame decorrelation
-> approved geometry/risk gates
-> current.db-projected CUR
-> approved extreme-U tail cap
-> DFT
```

An absolute-U threshold and tail cap are calibrated independently for each
element and model version; neither is transferable. Source quotas, force,
volume, and pressure hard gates require explicit approval rather than being
assumed defaults.

## Choose the Supported Entry Point

Read `research-plan.md` first, then use
`docs/source_function_index.md` to select the program:

| Task | Supported route |
|---|---|
| Protocol-A DFT labels | `scripts/slurm/run_vasp_batch_dft.slurm` -> `src/vasp_batch_dft.py` |
| Database merge | `src/vasp_batch_dft.py merge` with distinct base, label, and output DBs |
| Committee training | `scripts/slurm/run_train_committee.slurm` |
| Staged NVT/NPT sampling | `scripts/slurm/run_md_round.slurm` |
| Score/audit/CUR diagnosis or recovery | Separate score-only, audit, and projected-CUR entry points in the source index |
| Approved combined MD selection | `scripts/slurm/run_md_selection_pipeline.slurm` |
| Fixed EOS generation/collection/evaluation | `src/eos_reference.py` and `src/eos_check_jnn.py` |

The combined MD-selection runner is an execution convenience only. After an
element-local target, distance/void gates, and descriptor card are frozen, it
runs and retains score-only uncertainty, complete geometry audit, and
projected CUR in one protected allocation. It derives the ten-log `U_min`
record but does not choose scientific policy or authorize DFT, merge,
retraining, or EOS evaluation.

Do not use `src/ase_md.py` as a production scheduler. Do not use the
placeholder `src/temperature_table.py` values for production sampling.

## Before a New Submission

1. Read the current task state in `memory/index.md`, then the relevant task
   record under `memory/`.
2. Confirm the element-local inputs, base DB, committee, round path, and
   output paths. Ensure every protected output path is absent unless an
   overwrite has been explicitly approved.
3. For NPT, verify finite stress from every committee model before launch.
4. Confirm the exact command, SLURM resources, output/error paths, and
   scientific card. Submit expensive work with `sbatch` or from an active
   compute allocation, never directly on a login node.
5. After submission, record the Job ID and make at most one immediate status
   check unless monitoring is explicitly requested.

The clean-FCC D3 combined-selection task record is
`memory/32_clean_fcc_D3_md_validation_selection_card/`. Consult it and
`memory/index.md` for the retained current checkpoint; do not infer later
DFT, merge, M3, or E3 authorization from a selection submission.

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
