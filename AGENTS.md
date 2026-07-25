# Repository Guidelines

## Project Overview

This repository contains three independent ASE/NNAP active-learning
workflows for unary W, Ta, and Ti potentials. It is neither a W-Ta-Ti alloy
workflow nor a GPUMD production-simulation repository.

Each element has separate seed structures, DFT labels, databases, committees,
candidate pools, selection outputs, trajectories, and EOS references:

```text
W-potential/
Ta-potential/
Ti-potential/
```

Never mix assets between elements or copy generated assets from the parent Al
study. In particular, do not copy any `.db`, `.jnn`, trajectory, VASP work
directory, selection output, or EOS result. EOS structures and labels are
validation-only and must never enter an element's `current.db`.

The workflow for each element is `D0 -> M0 -> E0 -> D1 -> M1 -> E1 -> ...`.
It starts from the element-local structure inputs, labels controlled
perturbations with DFT, trains an NNAP committee, samples candidate structures,
selects uncertain and diverse configurations, and appends their DFT labels to
that element's database. New DFT labels must use
`src/vasp_batch_dft.py` and its SLURM template; do not use the legacy
`nncalc` path.

Authoritative workflow documentation:

- `research-plan.md`: reusable scientific goals, DFT protocol, parameter choices, selection strategy, and validation/decision gates.
- `docs/source_function_index.md`: quick source/function index for deciding which program or function can implement the current goal.
- `docs/unary_workflow.md`: staged unary W/Ta/Ti workflow, directory layout,
  and acceptance gates.
- `src/`: executable implementation. `src/ase_md.py` is a legacy
  one-command scheduler and is not the production entry point for this
  workspace.

## Project Navigation, Runtime, and Job Submission

### Files and generated outputs

- `src/`: active Python implementation. Use `docs/source_function_index.md` to
  map goals to scripts/functions before opening source files.
- `docs/`: workflow documentation. `docs/source_function_index.md` is the
  quick lookup; `docs/unary_workflow.md` provides the detailed staged
  workflow.
- `scripts/slurm/`: SLURM templates for expensive Python VASP DFT labeling, NNAP/JNN training, one-round MD, and single-worker MD jobs.
- Use `W-potential/`, `Ta-potential/`, and `Ti-potential/` as independent
  generated project roots. Each contains `00-input/`, model-version or round
  directories, and an element-local `current.db`.
- Fixed validation assets belong below `results/W_eos_benchmark/`,
  `results/Ta_eos_benchmark/`, and `results/Ti_eos_benchmark/`; they are not
  training inputs.
- For each future selection, retain auditable all-frame uncertainty,
  decorrelation, physical-gate, projected-CUR, and final POSCAR output files.

### Runtime environment and external tools

Assume commands run after loading the local JSE/NNAP environment:

```bash
module load jse
```

Important external commands/defaults:

- `nninit`: initial perturbation structure generator.
- `vasp_std`: VASP executable used by `src/vasp_batch_dft.py` after `module load jse`.
- `nncalc`: a legacy DFT-labeling command; not a supported submission path in
  this workspace.
- `jse`: default runner for `md_worker.py` and default module wrapper for DFT labeling.

Do not assume `uv`, GPUMD, or NEP production potentials are part of this repository unless the user explicitly adds them.

### Common lightweight commands

Use explicit staged commands for production work. Do not use
`src/ase_md.py` as a one-command scheduler: it does not implement this
workspace's required selection policy and its temperature table is
intentionally unconfigured.

Lightweight checks that may run directly on the login node:

```bash
python3 -m py_compile src/*.py
python3 src/<script>.py --help
jse src/eos_check_jnn.py --jnn-root <committee-dir> --model-id <model-id>
```

Before changing execution commands or runners, identify the targeted program/function through `docs/source_function_index.md`, then inspect only the relevant `src/*.py` file.

### Expensive-job rules

Do not launch expensive calculations directly on a login node. Submit them with SLURM (`sbatch`) or run inside an active compute allocation (`salloc` / `srun`) unless the user explicitly states that the current shell is already on an appropriate compute node.

Expensive tasks include:

- VASP DFT labeling via `src/vasp_batch_dft.py` / `scripts/slurm/run_vasp_batch_dft.slurm`;
- NNAP/JNN training;
- ASE MD sampling;
- RSS generation/minimization and full-committee scoring of large RSS pools;
- any command expected to consume significant CPU/GPU time.

Before submitting an expensive job, confirm the exact command, output paths, resource settings, and overwrite behavior. Use `scripts/slurm/` as the default starting point and edit cluster-specific directives such as partition, account, wall time, CPU count, and GPU request.

After submission, report the Job ID and at most one immediate status check.
Do not start polling loops, periodic checks, or active monitoring unless the
user explicitly requests monitoring. A later user request for status may
perform one focused check without changing this default.

Current SLURM templates:

- `scripts/slurm/run_vasp_batch_dft.slurm`: active Python VASP batch-labeling template; protects existing output DBs by default.
- `scripts/slurm/run_train_committee.slurm`: committee-training template; protects existing non-empty training directories by default.
- `scripts/slurm/run_md_round.slurm`: normal one-round NVT/NPT MD template; run with `bash ...` so it can self-submit with a matching task count.
- `scripts/slurm/run_md_worker.slurm`: debug/rerun one MD condition only; normal workflow should use `run_md_round.slurm`.

Read the template itself before submission for its current CLI, resource
defaults, and supported overrides. Research-specific parameter choices belong
in `research-plan.md`, not in this file. Existing output paths are protected:
do not overwrite or delete generated data without explicit user approval.

## Repository Workflow Constraints

- For status, planning, next-step, and research-strategy questions, prioritize `memory/`, `research-plan.md`, and `docs/source_function_index.md` before inspecting source code.
- Treat the current `src/` implementation as the executable source of truth.
  Use `docs/unary_workflow.md` only when detailed workflow background is
  needed.
- Preserve W, Ta, and Ti isolation in every command and output path. Never
  introduce a mixed-element database, committee, candidate pool, trajectory,
  selection, or EOS reference.
- Every element-local `current.db` is that element's cross-round state. Each
  active-learning round trains from it, labels selected structures, writes an
  element-local update, and refreshes only that element's `current.db`.
- Existing generated data are protected by default. Use or add overwrite behavior only when explicit and documented.
- Add user-supplied seed/EOS structures only below `structures/`. Add local
  PAW-PBE files only below `POTCAR/PBE/<element>/POTCAR`; do not commit or
  redistribute POTCAR files.
- EOS validation structures and all EOS-reference DB/CSV data are
  validation-only and must never enter a training DB.
- `temperature_table.py` contains placeholder temperature data; do not use it
  for production sampling.
- NPT sampling requires calculators that provide stress. Check `src/md_worker.py` before changing NPT/barostat behavior.
- Freeze and record element-specific active-label (Protocol A) and EOS
  reference (Protocol B) DFT protocols before producing labels. Verify the
  W/Ta/Ti `ENERGY` values in `src/dbselectandtrain.py` against the frozen
  Protocol A; do not assume historical values are valid.
- W and Ta require an explicit PAW valence/semicore and SOC decision; Ti
  requires an explicit PAW valence and spin-policy decision. Record POTCAR
  identity/checksum, ENCUT, k-point policy, smearing, convergence, and static
  versus relaxation choices for each protocol.
- Every active-learning selection uses:

  ```text
  current committee -> all-frame uncertainty scoring
  -> calibrated absolute-U lower cutoff
  -> source-wise candidate frame decorrelation
  -> approved physical/risk gates
  -> current.db-projected, source-constrained CUR
  -> approved extreme-U tail cap -> DFT
  ```

  Calibrate the absolute-U cutoff and tail cap independently for every
  element and model version. They are not transferable error thresholds.
- Use `research-plan.md` for DFT consistency choices, MD/RSS sampling and
  selection strategy, training parameters, database validation gates, EOS
  metrics, and scientific stop/continue decisions.
- Use `docs/source_function_index.md` to map an approved research step to the
  active script or function before inspecting or editing source code.


## Required Memory Workflow

For complex implementation, debugging, documentation, or scientific-workflow tasks, use persistent markdown notes under `memory/`. The directory may not exist yet; create it when first needed.

### Context priority rule

For status, next-step, planning, research-strategy, or workflow-navigation questions, use this source order:

1. Read `memory/index.md`.
2. Read the relevant `memory/<NN>_*/task_plan.md`, `notes.md`, and final report/deliverable when such a task folder exists.
3. Read `research-plan.md`.
4. Read `docs/source_function_index.md` to identify which program/function can implement the current goal.
5. Read `docs/unary_workflow.md` only if detailed staged-workflow background
   is still needed.
6. Read targeted `src/*.py` files only when:
   - the user asks for implementation, debugging, code changes, or exact command construction;
   - an exact CLI/API behavior must be verified before execution;
   - the previous documents are insufficient or appear stale.

For planning-only questions, do not inspect source code unless the previous documents are insufficient. If source inspection is needed, state the reason first.

Before making substantive implementation or workflow decisions:

1. Follow the context priority rule above.
2. If code execution, code editing, or exact behavior verification is required, read only the targeted current source file(s) under `src/` after identifying them through `docs/source_function_index.md`.
3. For any substantive new complex task, create `memory/<NN>_<slug>/` with:
   - `task_plan.md`: goals, phases, decisions, errors, and status;
   - `notes.md`: sources, commands, observations, and intermediate reasoning;
   - `deliverable.md` or another clearly named final report.

Keep `memory/index.md` concise and up to date when using memory. It should summarize the current workflow/task state, active blocker or gate, standing constraints, ready assets, and immediate next step. Do not turn it into a long task history.

Work principle: use persistent markdown files as working memory on disk for complex tasks, instead of relying only on chat context.

### The 3-file workflow

For every complex task, create and maintain these files:

| File | Purpose | When to Update |
|------|---------|----------------|
| `task_plan.md` | Track goal, phases, decisions, errors, and current status | After each phase / major action |
| `notes.md` | Store research, findings, commands, and intermediate knowledge | During research / discovery / debugging |
| `[deliverable].md` | The final written output artifact | At completion and as needed |

If the user does not specify a deliverable file name, use `deliverable.md`.

Create `task_plan.md` first, then initialize `notes.md` and `[deliverable].md` early so they exist before large intermediate outputs accumulate.

Default memory files are only the three markdown files above. Do not create extra helper files such as `*.log`, `*_jobid.txt`, ad-hoc status files, or raw-output sidecars unless the user explicitly asks for them or the output is too large for practical inclusion in `notes.md`. When an auxiliary file is genuinely needed, explain why, record its path and summary in `notes.md`, and keep `memory/index.md` concise.

### Core workflow

```text
Loop 1: Create/refresh task_plan.md with goal and phases
Loop 2: Research -> save to notes.md -> update task_plan.md
Loop 3: Read notes.md -> execute/build -> write/update deliverable.md -> update task_plan.md
Loop 4: Deliver final output
```

### task_plan.md template

```markdown
# Task Plan: [Brief Description]

## Goal
[One sentence describing the end state]

## Phases
- [ ] Phase 1: Plan and setup
- [ ] Phase 2: Research/gather information
- [ ] Phase 3: Execute/build
- [ ] Phase 4: Review and deliver

## Key Questions
1. [Question to answer]
2. [Question to answer]

## Decisions Made
- [Decision]: [Rationale]

## Errors Encountered
- [Error]: [Resolution]

## Status
**Currently in Phase X** - [What I'm doing now]
```

### notes.md template

```markdown
# Notes: [Topic]

## Sources

### Source 1: [Name]
- Path/URL: [link]
- Key points:
  - [Finding]

## Commands and Observations

```bash
# command snippets or checks used
```

## Synthesized Findings

### [Category]
- [Finding]
```

### deliverable.md template

```markdown
# Deliverable: [Title]

## Outcome
[What is delivered, in 1-3 sentences]

## Key Results / Decisions
- [Result/decision]

## How to Use / Verify
- [Command/check]

## Files Changed
- [path]: [what changed]
```

### Critical rules

1. Always create `task_plan.md` before substantive work on a complex task.
2. Read `task_plan.md` and relevant `notes.md` before major decisions.
3. Update `task_plan.md` after each phase or major action.
4. Store large outputs in `notes.md` or `deliverable.md`, not chat.
5. Log every error and resolution in `task_plan.md`.

## Editing Guidelines

- Keep changes minimal and consistent with the existing function-level workflow.
- For behavior changes, update both the relevant `src/*.py` implementation and
  `docs/unary_workflow.md` when applicable.
- Prefer small, verifiable edits. After Python changes, run `python3 -m py_compile src/*.py` when feasible.
- Avoid running expensive `nninit`, VASP/DFT labeling, training, or MD jobs unless the user explicitly asks for execution.
- Do not modify generated `<system>-potential/` outputs unless the task is specifically about generated data or cleanup.
- Do not restore or rely on legacy `nncalc` submission assets.
