# Notes: Clean-FCC D3 NPT Launch

## Sources

### Source 1: User authorization
- The user directs that D3 start for W, Ta, and Ti despite the preceding
  E0/E1/E2 review recommendations.

### Source 2: Scientific review
- Path: `memory/29_clean_fcc_e2_scientific_review/deliverable.md`
- Key points:
  - D3 must remain element-local.
  - NPT stress preflight is mandatory.

### Source 3: Active MD implementation and runner
- Paths: `src/md_worker.py`; `scripts/slurm/run_md_round.slurm`
- Key points:
  - NPT constructs a calculator with `compute_stress=True`, requests
    energy/forces/stress from every supplied NNAP model, and raises if any
    model omits stress.
  - It requires a three-dimensional periodic cell and initializes ASE `NPT`
    with `--pressure`, `--ttime`, `--ptime`, `--bulk-modulus-gpa`, and
    `--frac-traceless`.
  - Direct `bash scripts/slurm/run_md_round.slurm ...` self-submits one node
    with seven tasks for the seven explicit pressures. It creates only the
    listed D3 root after allocation start; no overwrite option is used.

### Source 4: ASE stress interface
- Path: `/home/tuzhengyu/.sciagent/skills/ase-master/references/upstream-doc/ase/atoms.py`
- Key points:
  - `Atoms.get_stress()` obtains calculator stress and returns six Voigt
    components `(xx, yy, zz, yz, xz, xy)`.

## Commands and Observations

```bash
# Read targeted worker/template, then check parser/syntax.
bash -n scripts/slurm/run_md_round.slurm
module load jse && python3 -m py_compile src/md_worker.py

# Actual no-write calculator/NPT preflight, run via the JSE Python runtime.
module load jse
jse --pythontext '<build_calculator([one matching M2 JNN],
  compute_stress=True); get energy/forces/stress; initialize ASE NPT>'
```

## Synthesized Findings

### Frozen D3 NPT cards

The user override is recorded in `research-plan.md` section 8.2.3. The
normal-pressure high-temperature targets are explicit D3 choices rather than
copied D2 conditions:

| Element | D3 root | DB SHA-256 | 32-atom seed / `--rep` | Temperature (K) | Ordered M2 digest |
|---|---|---|---|---:|---|
| W | `W-potential/fcc-restart/03-npt-round-1/` | `a852be39b421e61ff198b9d0d8b1351db5ae2b6729bcfdae6448b3c965bd9309` | `W-fcc-seed-32.poscar` / `1 1 1` | 4928.15 | `1211bf2cde44f68c6d40c0482905ac93656446e3c247e2f1e41236ac84e464b5` |
| Ta | `Ta-potential/fcc-restart/03-npt-round-1/` | `ee90d87b4f8f10db42d2e82ce2c4e81a38d188293e6428cc90e186c4c128dc7b` | `Ta-fcc-seed-32.poscar` / `1 1 1` | 4485.65 | `8ebba204b49962f92d7dd045a6818ed7a1e6d905b1ceee5bfcb5990169dd82b4` |
| Ti | `Ti-potential/fcc-restart/03-npt-round-1/` | `cfd5f2f5141c46f7b3636b2eb70d65b71d814e0fa4658c51aaa8ac44d2eb9196` | `Ti-fcc-seed-32.poscar` / `1 1 1` | 2750.65 | `864dc2078e1df8e2bc1e27369ea918faebe66810bcaba309d3f6871e11c3cb84` |

Each ordered digest is SHA-256 over the ten byte hashes, in exact fold order
`train-0/0.jnn` through `train-9/9.jnn`, below only that row's M2 root.
Every card passes all ten paths explicitly. Common controls are pressures
`1, 5, 10, 20, 30, 40, 50` GPa; 50,000 steps; 1.0 fs; write/log `10/1`;
HAL `tau_r=0.10`; `ttime=75.0` fs; `ptime=75.0` fs; bulk modulus `100.0`
GPa; `frac_traceless=0.0`; one node, seven exclusive one-core tasks, and
24 hours. `OVERWRITE` is unset.

### All-model finite-stress preflight

The first direct `python3` probe stopped before loading a model because the
module-loaded Python lacks `jsex.nnap`; it made no D3 output. The corrected
JSE-runtime probe used the actual `src.md_worker.build_calculator()` with one
model at a time and `compute_stress=True`, called ASE energy/forces/stress,
and initialized the same ASE `NPT` API/control values as production.

| Element | Seed atoms / volume (A3) | Models passed | Energy range (eV) | Diagonal stress range (eV/A3) |
|---|---:|---:|---:|---:|
| W | 32 / 508.925916812 | 10 / 10 | -400.65026843 to -400.44039658 | -0.04338570 to -0.03702214 |
| Ta | 32 / 580.850077277 | 10 / 10 | -371.30380640 to -371.06835820 | -0.03839721 to -0.03409666 |
| Ti | 32 / 555.067346400 | 10 / 10 | -246.67179853 to -246.56188924 | 0.00953555 to 0.01186772 |

Every model returned finite energy, finite `(32,3)` forces (zero at the
perfect FCC seed), and finite `(6,)` stress; all 30 NPT constructors and
`set_fraction_traceless(0.0)` calls succeeded. JSE generated its normal
inference cache libraries beside some M2 JNNs, but did not alter a JNN,
database, seed, EOS asset, or D3 root.

### No-overwrite preflight

`bash -n` for the runner, worker compilation, and runner `--help` passed.
Every current DB has exactly 300 finite unary 32-atom rows and its recorded
SHA-256. Every matching seed is finite, 32-atom, unary, 3D-periodic, and
positive-volume. Exactly ten nonempty element-matching M2 paths exist per
card. The D3 root, M3 root, E3 root, and therefore all D3 trajectory,
scoring, selection, and DFT paths are absent for all three elements; no
input/output path contains another element's potential or seed component.

### Submission and immediate status

The runner's direct self-submit branch cannot set element-local scheduler
stdout/stderr paths. Its documented direct-`sbatch` mode was therefore used
with `--ntasks=7`, after creating only the otherwise-empty
`<D3-root>/slurm_logs/` directory for each element. Every submission passed
the exact frozen controls and its ten explicit matching JNN paths; no
`OVERWRITE`, partition, account, GPU, `--pfactor`, selection, DFT, merge, M3,
or E3 option was used.

| Element | Job ID | Scheduler stdout/stderr | Immediate state |
|---|---:|---|---|
| W | `13513` | `W-potential/fcc-restart/03-npt-round-1/slurm_logs/fcc-d3-W-%j.{out,err}` | `PENDING (None)` |
| Ta | `13514` | `Ta-potential/fcc-restart/03-npt-round-1/slurm_logs/fcc-d3-Ta-%j.{out,err}` | `PENDING (Priority)` |
| Ti | `13515` | `Ti-potential/fcc-restart/03-npt-round-1/slurm_logs/fcc-d3-Ti-%j.{out,err}` | `PENDING (Priority)` |

The one combined `squeue` check was made immediately after all three
submissions. No polling or post-submission artifact check is active. A later
terminal-success request must validate every expected `P-1GPa`, `P-5GPa`,
`P-10GPa`, `P-20GPa`, `P-30GPa`, `P-40GPa`, and `P-50GPa` source before
separately considering all-frame scoring.
