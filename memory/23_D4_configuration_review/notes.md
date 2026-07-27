# Notes: D4 Configuration Review and Next-Round Launch

## Sources

### Source 1: Workflow state
- Path: `memory/index.md`, `memory/22_M3_E3_eos_validation/`
- Key points:
  - D3, M3, and E3 are complete for independent W, Ta, and Ti workflows.
  - E3 is validation-only and no D4 work has started.

### Source 2: Scientific decision gates and stage policy
- Path: `research-plan.md` Sections 8, 12, and 13
- Key points:
  - The required next stage is independent `04-npt-round-2`: `M3 -> D4`,
    using a new NPT pressure grid before a later recalibration and selection.
  - EOS regression requires preserving evidence and adjusting an
    element-local sampling configuration; it does not permit overwriting
    previous assets or adding EOS phases to training/sampling.
  - NPT uses all committee models and requires finite stress from every one.

### Source 3: D3 control and implementation precedent
- Path: `memory/18_D3_configuration_review/`, `scripts/slurm/run_md_round.slurm`,
  `src/md_worker.py`
- Key points:
  - The runner auto-submits when invoked with `bash`, allocating one node,
    seven one-core tasks, and its 24-hour template limit for seven pressures.
  - D3 used one seed per element, 2x2x2, the high-temperature target, seven
    pressures, and the recorded NPT controls. D4 changes only the pressure
    grid to make the post-E3 comparison interpretable.

## Commands and Observations

- The first JSE stress-probe invocation supplied Python via standard input,
  which `jse --pythontext` does not consume. It printed its help and did not
  evaluate a model or create an output.
- The corrected non-writing JSE probe used each matching 16-atom repeated
  seed and requested energy, forces, and six-component stress from every M3
  JNN. All 30 models returned finite values:

| Element | Finite stress | Seed volume (A3) | Initial model-pressure range (GPa) |
|---|---:|---:|---:|
| W | 10 / 10 | 254.916216 | -0.324983 to +0.249249 |
| Ta | 10 / 10 | 290.079564 | -0.805204 to -0.091038 |
| Ti | 10 / 10 | 277.109565 | -1.621353 to -1.176897 |

  JSE generated its normal inference JIT cache library beside JNNs that did
  not yet have one. No JNN, database, seed POSCAR, EOS reference, or D4
  output root was modified.

### Frozen D4 NPT parameter cards

The fixed-EOS results show mixed, non-uniform behavior (W raw regression,
Ta/Ti partial raw recovery). To avoid conflating D4 with an untested
temperature, seed, or barostat change, retain the validated D3 controls and
use a new interleaved pressure grid that samples intermediate states and only
modestly extends the former range.

| Field | W | Ta | Ti |
|---|---|---|---|
| Round/output root | `W-potential/04-npt-round-2/` | `Ta-potential/04-npt-round-2/` | `Ti-potential/04-npt-round-2/` |
| Input state | matching 400-row D3 `current.db` and ten M3 JNNs | same | same |
| Starting POSCAR | `structures/W_benchmark/W-seed.poscar` | `structures/Ta_benchmark/Ta-seed.poscar` | `structures/Ti_benchmark/Ti-seed.poscar` |
| Temperature | 4928.15 K | 4485.65 K | 2750.65 K |
| NPT pressures | 2, 8, 15, 25, 35, 45, 55 GPa | 2, 8, 15, 25, 35, 45, 55 GPa | 2, 8, 15, 25, 35, 45, 55 GPa |
| Supercell / duration | `2 2 2` / 50,000 steps | same | same |
| NPT controls | 1 fs; write/log 10/1; `tau-r=0.10`; `ttime=75 fs`; `ptime=75 fs`; 100 GPa bulk modulus; `frac-traceless=0.0` | same | same |
| SLURM resources | 1 node, 7 tasks, 24 h | same | same |

The M3 JNN list is path-ordered as `train-i/i.jnn` (`i=0..9`) under only its
matching `<X>-potential/model_versions/M3_from_D3/train-committee/` root.
No EOS reporting model is used alone, and no EOS path is supplied to MD.

### Protected D4 input/output preflight (passed)

Each matching `current.db` retains its published D3 SHA-256, 400 finite unary
16-atom 3D-periodic rows, and no EOS provenance:

| Element | `current.db` SHA-256 | Seed SHA-256 |
|---|---|---|
| W | `de91dcc3b96f7a893e70bed94f4e79a199ed7c7e2c042b3066f331cf33efe208` | `148d4b803afe79054e9f5731a43d1154c3f069d64eb1c7125060dc5fdcf4b824` |
| Ta | `e2963500627abaccb3d335f044f32d40de3b6dff227728aa140179656fac51d6` | `2464a70893789c98cca858e7aff3fc966500c032f57afdb75024190f16c86b8f` |
| Ti | `4fa6e59d7d04b7e78720aa30372bb35c9498020c73884b76e61eac9b48cac7d1` | `4c24b3d7ded6e2f551964203b579e638bdd5cee944762c132c7b6e6d00b7406c` |

All path-ordered M3 model hashes are frozen:

| Fold | W | Ta | Ti |
|---:|---|---|---|
| 0 | `391d1088c029f91f4c4bdca4c7899a85ab0569cb4fa4762cfbe6ac849f6f410a` | `b83c87fd828be5c09f1b560abe70fb4013f859b8dd81b0a97f3a9d5edf5b238b` | `77b2bffc2a958276e6265796db6bd9348ccd5bab53f4c8ea0010b11068cde98c` |
| 1 | `6cf2ab325ca0c294f838a42640fcdd9ca3bc163f9590bdadf68755fb275c4620` | `4f167fffe88644b5941581709933c257feca006282d65559d533af58bbef1433` | `c5e61b51620aef436e4909b07fe240fada3b296f21fc29dc5086e002e5915f90` |
| 2 | `d75818944f5ea5f8ea143f33df62be30b456b34fc36e6ab87bb51514a7d96404` | `57efa06f3fa906c95be594a80d80f4d96ef5045f9cb6336e003ed1577ca15a18` | `5af42165b0314a50bba46093b176b40a5041300c6890cf8621923ac7d8251672` |
| 3 | `6af477925265e02cdcc823444c89c7009581a7e4232b2facf3d17149e5661128` | `8751769288b9b54ae892bd04f64a530d9b21e73d3a9eec16d92ae09455d8889c` | `2866ac92e06e563788de490b5e61c22791b033924aa7f235dae2d9e1909f6a00` |
| 4 | `d65cd4c0a21017a538d196178896b4ebb28448c4deba66f1ff4b7e41709a6dc4` | `168f8a4f77d3773511f2787b9ad773e7b04cc8feacea52e0d857871db56d77da` | `124c9f9c8f663cfc1956288e30f933854f45696361a9b642a1a1d97201cc68e2` |
| 5 | `dcffcd6aea2f032d6793a81207531659dffff5585ce8a34a64d52c62b8be335c` | `9bfb154c574fdb62d46c20a1102a776d73440821f1055c45f079aa2916af6ff7` | `fcb9f4450510bb8b7189e2bbedd71eb745abf210e24156dddef6b9a8757066d5` |
| 6 | `cdf8d94014c25d038eae27652b4efbec96221e00a9598ee2f51098edb09796bd` | `892330dfa3043c25bf4f2fdff4ac0329e06c6f2a3212e439edccf5524bd4c166` | `4edb7f9376feaa22b835333bf90890c54f92a5a3249e7330280cd25efde039d6` |
| 7 | `e6d9cedfb8a23c7fdce8806df4d3e5272ee4e98fa5b1ec7564bdce9fdec4b0d2` | `a026c63a183fb53e3294f87f62680d16c41975fb76b94fc1bcc58e709e8e9902` | `e9f0982cdc1d73b7e23633044d4fbcc1caee50b8a9159ea89f3e0d5dc3d1c951` |
| 8 | `103b207a614290fecae31a7360f57c2dbae2a63a92c73330142136c32030935f` | `0a2a7a1594e944b9a21ae6e8692dfc4d468e399423dac70cbbe4660c7095ab98` | `a82763d69141d6a5fc9a72e4039b6792292619e15bf35b0beb13b857881b3e37` |
| 9 | `f690e807f0e382f5b258430bc0fe0026e3868d8eaf0358d7ef1cc4f3ff9b1457` | `8de4eb26e1498e63ac5a22f0b090c3350886514c1eb1f39c67e96b43753bcac1` | `fd62e225c9a0bc0c0787b6632c3a54149b960448399408a90005f6bb67b4ab3c` |

Immediately before submission, each protected `04-npt-round-2` root will be
rechecked absent. The command uses no overwrite setting; `bash
scripts/slurm/run_md_round.slurm` will self-submit one independent 1-node,
7-task, 24-hour allocation per element.

### D4 submission (2026-07-26)

Immediately before each submission, its matching `04-npt-round-2` root was
still absent and its established seed plus all ten nonempty M3 JNNs were
present. The exact frozen command from the parameter table was passed to
`bash scripts/slurm/run_md_round.slurm`; no overwrite option was used.

| Element | Job ID | Output root |
|---|---:|---|
| W | `13235` | `W-potential/04-npt-round-2/` |
| Ta | `13236` | `Ta-potential/04-npt-round-2/` |
| Ti | `13237` | `Ti-potential/04-npt-round-2/` |

The template self-submitted one node with seven tasks and a 24-hour limit for
each element. One immediate focused queue check found all three jobs `RUNNING`
on `lpsnode01`. No monitoring loop was started.

### Later focused status check

A later single `squeue`/`sacct` check found all three allocations still
`RUNNING` with exit status `0:0`: W `13235` for `01:11:09`, Ta `13236` for
`01:11:08`, and Ti `13237` for `01:11:08`, all on `lpsnode01`. No output
validation or downstream submission has been started.

### Completion status

A subsequent focused `sacct` check found all D4 NPT allocations completed
successfully: W `13235` and Ta `13236` each `01:27:53`, Ti `13237`
`01:27:20`, all `COMPLETED` with exit `0:0`. Post-run source validation and
all downstream stages remain unstarted.

No D4 all-frame scoring, selection, DFT labeling, merge, M4 training, or E4
evaluation has been submitted.

### Selection-strategy interpretation

The user questioned why uncertainty-led selection has not consistently
improved the EOS metric. The current policy does not use global Top-U:
committee uncertainty supplies only the calibrated `U >= U_min` eligibility
gate; physical/risk gates and current.db-projected CUR provide the final
diversity selection.

The E0--E3 evidence shows why EOS need not improve monotonically under this
policy. Committee disagreement estimates extrapolation risk for sampled NPT
frames, whereas E3 measures static cross-phase energy offsets and shapes on
fixed bcc/fcc/hcp structures. The one-seed, high-temperature NPT generator
does not directly target those validation configurations. W improved
phase-aligned shape versus E2 but strongly regressed in raw cross-phase MAE;
Ta/Ti partly recovered E2 raw MAE but remain above E0. Thus the observed
failure is not evidence that CUR-only selection would fix the target mismatch.

No selection-policy change is authorized. Before replacing the uncertainty
gate, retain D4's post-run validation and later quantify M3 uncertainty
calibration on newly DFT-labeled D4 structures (error versus U), diagnose
validation-only EOS descriptor coverage relative to `current.db`, and audit
Protocol-A/Protocol-B energy-offset consistency. Any CUR-only policy would be
a separately frozen, auditable ablation rather than an unrecorded production
substitution.

## Synthesized Findings

### Scope
- Preserve strict W/Ta/Ti isolation.
- Do not modify `current.db` or EOS-reference assets in this configuration task.
