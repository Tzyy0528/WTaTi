# Notes: D2 NVT Sampling from M1

## Sources

### Source 1: D1 NVT configuration
- Path: `memory/07_D1_NVT_preparation/`
- Key points:
  - The approved scale grid is `0.90, 0.95, 1.00, 1.05, 1.10`.
  - NVT uses `2 2 2`, 50,000 steps, 1 fs, trajectory interval 10, log
    interval 1, `tau-r=0.10`, and friction `0.02 fs^-1`.
  - Established temperatures are W 4928.15 K, Ta 4485.65 K, and Ti 2750.65 K.

### Source 2: M1/E1 state
- Path: `memory/10_D1_merge_M1_training/`,
  `memory/11_M1_validation_E1_evaluation/`
- Key points:
  - Every element has a validated ten-model M1 committee.
  - E1 is validation-only; D2 sampling must use the committee, not its
    single EOS reporting model.

### Source 3: NVT runner
- Path: `scripts/slurm/run_md_round.slurm`, `src/md_worker.py`
- Key points:
  - To be inspected before D2 submission for exact arguments, resources, and
    output-root protections.

## Intended D2 Isolation

```text
W:  M1 W committee -> W-potential/02-nvt-round-2/
Ta: M1 Ta committee -> Ta-potential/02-nvt-round-2/
Ti: M1 Ti committee -> Ti-potential/02-nvt-round-2/
```

No element may use another element's JNN model, temperature, trajectory,
database, candidate pool, or EOS asset.

## D2 Submission Preflight

Completed on 2026-07-25 before submission:

- All three protected D2 roots were absent:
  `W-potential/02-nvt-round-2/`,
  `Ta-potential/02-nvt-round-2/`, and
  `Ti-potential/02-nvt-round-2/`.
- Each element-local seed POSCAR exists.
- Each element-local `current.db` has exactly 200 rows.
- Each M1 committee has exactly ten nonempty JNN files under only its own
  `train-committee/train-*/` directories.
- The round runner auto-submits one `--nodes=1 --ntasks=5` allocation per
  element. Its current template requests a 24-hour walltime and launches five
  exclusive, one-task `srun` workers. The D2 roots are absent, so the runner's
  non-protective `mkdir -p` behavior cannot overwrite existing MD work.

Exact commands to submit:

```bash
bash scripts/slurm/run_md_round.slurm --ensemble nvt --round-dir W-potential/02-nvt-round-2 --poscar structures/W_benchmark/W-seed.poscar --rep 2 2 2 --temperature 4928.15 --scale-factors 0.90 0.95 1.00 1.05 1.10 --steps 50000 --timestep 1.0 --write-interval 10 --log-interval 1 --tau-r 0.10 --friction 0.02 --jnn-paths W-potential/model_versions/M1_from_D1/train-committee/train-0/0.jnn W-potential/model_versions/M1_from_D1/train-committee/train-1/1.jnn W-potential/model_versions/M1_from_D1/train-committee/train-2/2.jnn W-potential/model_versions/M1_from_D1/train-committee/train-3/3.jnn W-potential/model_versions/M1_from_D1/train-committee/train-4/4.jnn W-potential/model_versions/M1_from_D1/train-committee/train-5/5.jnn W-potential/model_versions/M1_from_D1/train-committee/train-6/6.jnn W-potential/model_versions/M1_from_D1/train-committee/train-7/7.jnn W-potential/model_versions/M1_from_D1/train-committee/train-8/8.jnn W-potential/model_versions/M1_from_D1/train-committee/train-9/9.jnn

bash scripts/slurm/run_md_round.slurm --ensemble nvt --round-dir Ta-potential/02-nvt-round-2 --poscar structures/Ta_benchmark/Ta-seed.poscar --rep 2 2 2 --temperature 4485.65 --scale-factors 0.90 0.95 1.00 1.05 1.10 --steps 50000 --timestep 1.0 --write-interval 10 --log-interval 1 --tau-r 0.10 --friction 0.02 --jnn-paths Ta-potential/model_versions/M1_from_D1/train-committee/train-0/0.jnn Ta-potential/model_versions/M1_from_D1/train-committee/train-1/1.jnn Ta-potential/model_versions/M1_from_D1/train-committee/train-2/2.jnn Ta-potential/model_versions/M1_from_D1/train-committee/train-3/3.jnn Ta-potential/model_versions/M1_from_D1/train-committee/train-4/4.jnn Ta-potential/model_versions/M1_from_D1/train-committee/train-5/5.jnn Ta-potential/model_versions/M1_from_D1/train-committee/train-6/6.jnn Ta-potential/model_versions/M1_from_D1/train-committee/train-7/7.jnn Ta-potential/model_versions/M1_from_D1/train-committee/train-8/8.jnn Ta-potential/model_versions/M1_from_D1/train-committee/train-9/9.jnn

bash scripts/slurm/run_md_round.slurm --ensemble nvt --round-dir Ti-potential/02-nvt-round-2 --poscar structures/Ti_benchmark/Ti-seed.poscar --rep 2 2 2 --temperature 2750.65 --scale-factors 0.90 0.95 1.00 1.05 1.10 --steps 50000 --timestep 1.0 --write-interval 10 --log-interval 1 --tau-r 0.10 --friction 0.02 --jnn-paths Ti-potential/model_versions/M1_from_D1/train-committee/train-0/0.jnn Ti-potential/model_versions/M1_from_D1/train-committee/train-1/1.jnn Ti-potential/model_versions/M1_from_D1/train-committee/train-2/2.jnn Ti-potential/model_versions/M1_from_D1/train-committee/train-3/3.jnn Ti-potential/model_versions/M1_from_D1/train-committee/train-4/4.jnn Ti-potential/model_versions/M1_from_D1/train-committee/train-5/5.jnn Ti-potential/model_versions/M1_from_D1/train-committee/train-6/6.jnn Ti-potential/model_versions/M1_from_D1/train-committee/train-7/7.jnn Ti-potential/model_versions/M1_from_D1/train-committee/train-8/8.jnn Ti-potential/model_versions/M1_from_D1/train-committee/train-9/9.jnn
```

## Submission and Immediate Status

- W D2 NVT: SLURM job `13142`
  (`W-potential/02-nvt-round-2/`)
- Ta D2 NVT: SLURM job `13143`
  (`Ta-potential/02-nvt-round-2/`)
- Ti D2 NVT: SLURM job `13144`
  (`Ti-potential/02-nvt-round-2/`)

One immediate `squeue` check after all submissions found every job in
`RUNNING` state on `lpsnode03` (elapsed approximately three seconds). No
automatic monitoring was started.

## Completion and MD Validation

After the user reported completion, one focused `sacct` check found all three
round allocations and their five workers `COMPLETED` with exit code `0:0`:

- W job `13142`: 18:57 elapsed
- Ta job `13143`: 18:58 elapsed
- Ti job `13144`: 11:56 elapsed

The post-run validation passed for all 15 element-local scale sources. It
verified each source's nonempty `command.sh`, `log`,
`multi_nnap_md.xyz`, and `energy_forces_summary.dat`; the recorded NVT
controls, element-local seed and ten M1 JNN paths; and a final log line of
`Finished MD`.

Every trajectory has exactly 5,001 unary 16-atom, 3D-periodic frames with
finite positions, cells, positive volumes, energies, and forces. Every summary
has exactly 50,001 consecutive steps (0--50,000) with finite numerical
values. Minimum trajectory cell volumes (A^3) by scale `0.90, 0.95, 1.00,
1.05, 1.10` were:

```text
W:  185.833922, 218.558791, 254.916216, 295.097385, 339.293484
Ta: 211.468002, 248.706966, 290.079564, 335.803355, 386.095899
Ti: 202.012873, 237.586813, 277.109565, 320.788960, 368.832831
```

The validated D2 production pools are ready for all-frame uncertainty scoring.
No scoring, selection, DFT, merge, M2, or E2 work has been submitted.
