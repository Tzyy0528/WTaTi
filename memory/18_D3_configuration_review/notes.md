# Notes: Post-E2 D3 Configuration Review

## Sources

### Source 1: Current evidence
- Path: `memory/index.md`; `memory/17_M2_E2_eos_validation/notes.md`
- Key points:
  - M2 committees and fixed-reference E2 artifacts are valid and all
    `current.db` files remain independent 300-row D2 states.
  - W recovered from E1 but remains worse than E0; Ta regressed from both;
    Ti improved phase-aligned shape but regressed in raw EOS error.

### Source 2: Stage and sampling policy
- Path: `research-plan.md` Sections 8, 12, and 13
- Key points:
  - The nominal next stage is `D3 -> M3 -> E3`: NPT sampling from M2.
  - NPT requires finite stress from every committee model. Use all committee
    models, not the EOS reporting model alone.
  - Before a stage, freeze the element-local parameter card: DB checksum, all
    JNN hashes, starting phase/POSCAR, temperature, pressure grid, explicit MD
    parameters, resources, and output paths.
  - An EOS regression requires preserving evidence and adjusting the next
    element-local configuration; it must not cause asset overwrites.

## Synthesized Findings

### Preflight environment note
`module load jse` alone provides ASE to shell `python3` but not the embedded
`jsex` module required by NNAP MD. Run the non-writing stress probe through
`jse --pythontext`, matching the production worker's JSE Python runtime.
The JSE `NNAP` import was then confirmed successfully.

### NPT implementation audit
- `src/md_worker.py` builds an NPT calculator with
  `compute_stress=True`, requests `energy`, `forces`, and `stress` from every
  NNAP model, and raises an error if any model omits stress.
- NPT requires a 3D periodic cell. It uses `--pressure`, `--ttime`,
  `--ptime`, `--bulk-modulus-gpa` (unless `--pfactor` overrides it), and
  `--frac-traceless`.
- `scripts/slurm/run_md_round.slurm` self-submits when invoked with `bash`;
  seven NPT pressures will request one node, seven one-core tasks, and the
  template's 24-hour limit. It writes per-source work below the round root.

### All-model NPT stress preflight (passed)

The non-writing JSE probe used only each element's established single seed,
repeated `2 2 2`. It requested energy, forces, and stress independently from
all ten matching M2 JNNs. All values and all six stress components were finite.
The protected D3 roots were absent before and after the probe.

| Element | Seed | Atoms | Volume (A3) | Finite stress | Initial model pressure range (GPa) |
|---|---|---:|---:|---:|---:|
| W | `structures/W_benchmark/W-seed.poscar` | 16 | 254.916216 | 10 / 10 | -0.645 to +0.743 |
| Ta | `structures/Ta_benchmark/Ta-seed.poscar` | 16 | 290.079564 | 10 / 10 | -0.562 to +0.175 |
| Ti | `structures/Ti_benchmark/Ti-seed.poscar` | 16 | 277.109565 | 10 / 10 | -1.485 to -1.144 |

The JSE probe created its normal inference JIT cache libraries beside M2 JNNs
that lacked them. It did not change any JNN, database, seed POSCAR, EOS
reference, or D3 output root. JSE emitted a deprecation warning for
`asAseCalculator()`; that is the same interface currently used by
`src/md_worker.py` and did not affect the finite-stress result.

### Frozen D3 NPT parameter cards

The cards retain one seed structure per element, all ten M2 models, the D2
high-temperature target, and the research-plan starting pressure grid. The
fixed EOS structures remain validation-only.

| Field | W | Ta | Ti |
|---|---|---|---|
| Round/output root | `W-potential/03-npt-round-1/` | `Ta-potential/03-npt-round-1/` | `Ti-potential/03-npt-round-1/` |
| Input DB and SHA-256 | `W-potential/current.db` / `b2a6ed5a86848a6fc83e3c13ceb4bc08ab2e60f0e7d753e2cb8555068c2c6476` | `Ta-potential/current.db` / `b4e7e34325bfc9506147c58bf4b9ebeb69a7491c2cb7510961cd457695c1a866` | `Ti-potential/current.db` / `36eb18737c291e1dd26b11ca995f3255c0ae8da881e821ce66b08a0047e177cb` |
| One starting POSCAR and SHA-256 | `structures/W_benchmark/W-seed.poscar` / `148d4b803afe79054e9f5731a43d1154c3f069d64eb1c7125060dc5fdcf4b824` | `structures/Ta_benchmark/Ta-seed.poscar` / `2464a70893789c98cca858e7aff3fc966500c032f57afdb75024190f16c86b8f` | `structures/Ti_benchmark/Ti-seed.poscar` / `4c24b3d7ded6e2f551964203b579e638bdd5cee944762c132c7b6e6d00b7406c` |
| Committee root | `W-potential/model_versions/M2_from_D2/train-committee/` | `Ta-potential/model_versions/M2_from_D2/train-committee/` | `Ti-potential/model_versions/M2_from_D2/train-committee/` |
| Temperature | 4928.15 K | 4485.65 K | 2750.65 K |
| NPT pressures | 1, 5, 10, 20, 30, 40, 50 GPa | 1, 5, 10, 20, 30, 40, 50 GPa | 1, 5, 10, 20, 30, 40, 50 GPa |
| Supercell / duration | `2 2 2` / 50,000 steps | `2 2 2` / 50,000 steps | `2 2 2` / 50,000 steps |
| Common MD controls | 1 fs; write 10; log 1; `tau-r=0.10`; `ttime=75 fs`; `ptime=75 fs`; bulk modulus 100 GPa; `frac-traceless=0.0` | same | same |
| Future SLURM allocation | 1 node, 7 tasks, 24 h | 1 node, 7 tasks, 24 h | 1 node, 7 tasks, 24 h |

All 30 path-ordered M2 JNN hashes (`train-i/i.jnn`) are frozen below:

| Fold | W | Ta | Ti |
|---:|---|---|---|
| 0 | `314a40847b0717c2bdb2a078553be1fdf94df2b1343995bd317babc371be85a8` | `3e7e1cc75f4b2925c67da221d045596b475aff6a6b76d1136e06e31f578e64e9` | `485e5b4a4fbdf6b27073d4d488be5d8db3266bd4153390b1df737028f1967502` |
| 1 | `5cb8d4d260cb74d4d3a9d7d515f2d9044b1cd0097175299b3c603bb801e4d7ea` | `9389fee58206642e2d28609337ed90459d6e33065935ee73176e8de9bdeaaa65` | `4c28221a87aeb3a5aa7a035cfc1182c7db6fc7ea2ed725fabe036e48dbe67f8e` |
| 2 | `70f049241032335666979e3e492c2d98ccaf0a20149b7c1aef3847e51fcf9598` | `5dc8a9efbcb9a2f3747522bdf32663ef5aa45e89ff01d67f3eaa7758bb17df61` | `568f59b343edfed48e9023484f895dc61eef87f05034e2bac58da40f01d4b4a1` |
| 3 | `ffc5a653b3f84c2d0d69cf50d09d2d8678e8d782ebc20e84eac48b72a8884480` | `87bdabbc002f0319ed0f7b6204fe49da646e8dbd6cddd6d82325d68d7c7a155d` | `871f3ba732eb92c55d54db4807ecc00e2420eb4873925605282145cbc068791b` |
| 4 | `c483bf07572a6d3e7d3dbc3d72b6fd86f9ecb38b0271a50a619573f887ee1a1e` | `f1432a7d18d03883149a1c427f30fca136f1a7c0b9e50ba03638e18da9822586` | `26ee56a365b3f0d367be379220ceac4e78aa42516f962d1de0f9112c37b6c776` |
| 5 | `490a8c28ace40ad3b2ccdda7c1eeeae456314d8720b3ed0207ce1188a939f2d3` | `2259909dc4a917ec0c88ea743ca20c0172080706e2f1c667957745a67d7a6dfc` | `f11330643dfacee5b59aab19b2d6a800abf249eabf66cec156edc03bb765a6f0` |
| 6 | `17911a9fd863f19b32ffd17b79fdba387607cecb1383249f5dfd22c72e1063b3` | `7382506c540c473fc211583ae14b25d7839d2e960425098767ee64e11495371f` | `381289074b7519025216ccc61aca3dc56a8e391a14d5e8daf9d96e4c549e8b6e` |
| 7 | `902347020d1fb53133dc91ac1c551c31a13f55b8210ab4136d63c4cbf1bf3e72` | `bb79c67f8227c766e8d9d582eed5bee168cb896060f576adde0bad9371534b33` | `6ab4801772f7315435a202ac478e2c4e6f23aa5f7edf900ab468e18c5608752` |
| 8 | `d725712913adb3ed83e114f103894193f1669655f0b42cd770aba921fbc2ceed` | `3463b73dee035e88f040b0dea3ceebd144e58684c488c20e47a5679d810d6f84` | `1a61aacb1f7f81eaa163fa086c7044c35358cbd56aff8faba87ad712b0f3be8e` |
| 9 | `feab4daa7c7471d8456d2943cc713cd1e0d62986bbe484e1e712a39570490c60` | `b8d8dec7ff805ed772d5a1f074545ea61a8cd5e534e40e25a6323c1816c9dcd9` | `e1c3d3885aefb7f7bda3271c2c621b58838197a516eb69332ecd063627f9969f` |

No D3 MD command has been invoked. On later explicit submission authorization,
guard every protected round root immediately before running the corresponding
command, then use this exact pattern (shown for W):

```bash
test ! -e W-potential/03-npt-round-1 || {
  echo "Refusing to overwrite W D3 output"; exit 1;
}
W_JNNS=()
for i in {0..9}; do
  W_JNNS+=("W-potential/model_versions/M2_from_D2/train-committee/train-${i}/${i}.jnn")
done
bash scripts/slurm/run_md_round.slurm \
  --ensemble npt \
  --round-dir W-potential/03-npt-round-1 \
  --poscar structures/W_benchmark/W-seed.poscar \
  --rep 2 2 2 \
  --temperature 4928.15 \
  --pressures 1 5 10 20 30 40 50 \
  --steps 50000 \
  --timestep 1.0 \
  --write-interval 10 \
  --log-interval 1 \
  --tau-r 0.10 \
  --ttime 75.0 \
  --ptime 75.0 \
  --bulk-modulus-gpa 100.0 \
  --frac-traceless 0.0 \
  --jnn-paths "${W_JNNS[@]}"
```

Use the matching Ta/Ti paths and the frozen temperatures with the same
protected pattern. The command self-submits one independent 7-task allocation
per element; it must not be run until the user explicitly authorizes D3 MD.

### D3 submission (2026-07-25)

- The user explicitly authorized D3 MD after the finite-stress preflight and
  frozen-card review.
- Every protected D3 root was checked absent immediately before its matching
  submission. No overwrite option was used.
- Submitted independent NPT allocations:
  - W: job `13168`
  - Ta: job `13169`
  - Ti: job `13170`
- Each command uses its matching one seed, all ten M2 JNNs, seven pressures
  (1, 5, 10, 20, 30, 40, 50 GPa), 50,000 steps, and the frozen NPT controls.
  The `bash` runner self-submitted one node with seven tasks and a 24-hour
  limit for each element.
- One immediate focused `squeue` check found all three jobs `RUNNING` on
  `lpsnode03`:

```text
13168 RUNNING unary_md_rou 0:08 1-00:00:00 1 lpsnode03
13169 RUNNING unary_md_rou 0:08 1-00:00:00 1 lpsnode03
13170 RUNNING unary_md_rou 0:07 1-00:00:00 1 lpsnode03
```

Do not poll. On a later user status/completion request, run one focused
`sacct` query, then validate all seven NPT sources per element before any
all-frame uncertainty scoring.

### D3 completion and seven-source validation (passed)

- Focused accounting result:
  - W `13168`: `COMPLETED`, exit `0:0`, elapsed `00:20:34`
  - Ta `13169`: `COMPLETED`, exit `0:0`, elapsed `00:20:27`
  - Ti `13170`: `COMPLETED`, exit `0:0`, elapsed `00:19:47`
- Each element has exactly seven NPT source directories:
  `P-1GPa`, `P-5GPa`, `P-10GPa`, `P-20GPa`, `P-30GPa`, `P-40GPa`, and
  `P-50GPa`. Every source has nonempty `command.sh`, `log`,
  `multi_nnap_md.xyz`, and `energy_forces_summary.dat`.
- All 21 commands reproduce the frozen NPT controls, matching element-local
  seed, temperature, pressure, and all ten M2 JNN paths. Each log records
  `Starting NPT biased MD` and `Finished MD`.
- Every source trajectory has exactly 5,001 finite unary 16-atom,
  3D-periodic frames. Every NPT summary has 50,001 finite consecutive steps
  (0--50,000), including finite `Px_GPa`, `Py_GPa`, `Pz_GPa`, and
  `Press_GPa`.

| Element | Total frames | Volume/atom range (A3) | Instant pressure range (GPa) | Maximum force component (eV/A) |
|---|---:|---:|---:|---:|
| W | 35,007 | 13.330852 to 22.276309 | -23.500 to 94.357 | 14.763947 |
| Ta | 35,007 | 13.400005 to 25.745101 | -14.317 to 114.445 | 11.488273 |
| Ti | 35,007 | 9.840026 to 20.259878 | -6.374 to 121.489 | 10.462343 |

The output validation establishes finite, auditable candidate pools only. It
does not waive the later source-wise physical/risk gates during selection.
The next separate stage is full all-frame M2 uncertainty scoring with
`scripts/slurm/run_uncertainty_scoring.slurm` in `--score-only` mode, followed
by a fresh M2-log-derived `U_min` calibration for each element.

### Recommended immediate action
Do not submit D3 yet. First prepare and approve separate W, Ta, and Ti D3 NPT
parameter cards, including a finite-stress preflight of all ten M2 models and
an element-specific pressure/temperature/volume sampling adjustment under only
the existing one-structure MD design. Inspect `src/md_worker.py` only when
constructing exact NPT commands or changing barostat behavior.

### Required D3 policy after authorization
1. Use only the matching `current.db` and M2 committee; retain all ten JNN
   paths for MD.
2. Use independent output roots and a `2 2 2` supercell. Record the full
   parameter card; the 1, 5, 10, 20, 30, 40, 50 GPa list is only a starting
   pressure grid, not an automatic prescription.
3. Run automatic NPT trajectory/stress validation before scoring every frame.
4. Apply the existing selection chain: all-frame uncertainty, newly calibrated
   absolute-U cutoff, source decorrelation, physical/risk gates, projected
   CUR against only the matching `current.db`, and approved extreme-U cap.
5. Never use fixed EOS structures or labels as D3 candidates or training data.
6. Retain one preselected MD starting structure per element. Vary thermodynamic
   state variables and the resulting sampled configurations, not the initial
   crystal prototype, to test whether the learned unary potential transfers to
   the three fixed EOS curves.

### Element-specific E2 diagnostic focus
The fcc/hcp/bcc EOS errors are transferability diagnostics, not instructions
to add their structures to training:

- W: fcc/hcp raw errors are 30.566/69.558 meV/atom. Adjust the same-source MD
  pressure/volume span only if it safely broadens sampled local environments.
- Ta: fcc/hcp raw errors are 132.365/91.553 meV/atom. Review the same-source
  pressure/temperature card and Protocol-A consistency; do not change to
  fcc/hcp starting structures.
- Ti: bcc/fcc raw errors are 74.770/51.797 meV/atom and bcc's grid minimum is
  -0.339 A3/atom from DFT. Use that only to guide pressure/volume coverage
  within the one-structure MD design.
