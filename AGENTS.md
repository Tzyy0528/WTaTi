# W-Ta-Ti Unary-Potential Workspace Guidelines

## Scope

This is a clean ASE/NNAP active-learning workspace for three *independent*
unary potentials: W, Ta, and Ti. It is not a W-Ta-Ti alloy-potential
workspace.

- Never mix W, Ta, and Ti structures, DFT labels, ASE databases, committees,
  trajectories, selection pools, or EOS references.
- Use one independent project root per element: `W-potential/`,
  `Ta-potential/`, and `Ti-potential/`.
- Do not copy generated assets from the parent Al project into this workspace.
  In particular, do not copy any `.db`, `.jnn`, trajectory, VASP work
  directory, selection output, or EOS result.
- EOS structures and DFT labels are validation-only. They must never enter
  `current.db`.

## Default Selection Policy

Every active-learning selection must use:

```text
current committee -> all-frame uncertainty scoring
-> calibrated absolute-U lower cutoff
-> source-wise candidate frame decorrelation
-> approved physical/risk gates
-> current.db-projected, source-constrained CUR
-> approved extreme-U tail cap -> DFT
```

The absolute-U cutoff and tail cap are recalibrated for every element and
model version; they are not transferable error thresholds.

## Inputs and DFT

- Add user-supplied EOS/seed structures only under `structures/`.
- Add user-supplied PAW-PBE pseudopotentials only under
  `POTCAR/PBE/<element>/POTCAR`; do not commit or redistribute POTCAR files.
- Freeze and record an element-specific active-label DFT protocol and
  EOS-reference DFT protocol before creating any training labels.
- Verify the W, Ta, and Ti atomic reference energies in
  `src/dbselectandtrain.py::ENERGY` against the frozen active-label protocol
  before training. Do not assume the bundled historical values are valid.
- New DFT labels use `src/vasp_batch_dft.py` and
  `scripts/slurm/run_vasp_batch_dft.slurm`. Do not use the legacy `nncalc`
  path.

## Execution Rules

- Use explicit staged commands rather than `src/ase_md.py` for production:
  the one-command scheduler does not implement this selection policy and its
  temperature table is intentionally unconfigured.
- Do not launch VASP, NNAP training, MD, RSS, or full-committee scoring on a
  login node. Use SLURM or an active compute allocation after the exact
  command, resources, output paths, and overwrite behavior are reviewed.
- Existing output paths are protected. Do not overwrite or delete generated
  data without explicit approval.
- Record each substantial workflow task under `memory/` with
  `task_plan.md`, `notes.md`, and `deliverable.md`.
