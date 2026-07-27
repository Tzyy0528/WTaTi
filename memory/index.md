# Memory Index

## Current State
The independent W, Ta, and Ti workflows completed `D3 -> M3 -> E3` and the
D4 database transition. Every element-local `current.db` is a validated
500-row D4 successor. M4 jobs completed successfully; E4 remains deferred.

All prior FCC-derived structures, databases, models, trajectories, labels,
evaluations, scheduler outputs, and task records were deleted on user
instruction. A clean FCC restart is active in `38_fcc_clean_restart/`.

The fixed validation-only references remain under:

- `results/W_eos_benchmark/`
- `results/Ta_eos_benchmark/`
- `results/Ti_eos_benchmark/`

## Active Gate / Blocker
Fresh W, Ta, and Ti seed POSCARs are validated exact `2 2 2` repeats of only
their retained four-atom benchmark FCC sources: 32 atoms and all three
lattice-vector lengths doubled. Each fresh `fcc-restart/` root now contains
only its matching validated 100-frame 32-atom D0 candidate pool.

## Standing Constraints
- Keep W, Ta, and Ti data, databases, models, candidate pools, and EOS
  references independent.
- Do not add EOS structures or labels to any `current.db`.
- Do not reuse any deleted FCC asset or prior FCC job output.
- Preserve D4/M4 outputs unless the user explicitly directs otherwise.
- Use staged SLURM execution for DFT, training, and MD.
- Every future selection requires all-frame scoring, a current-committee
  mean-test-force-MAE absolute threshold, and current.db-projected CUR.
- Do not run E4.

## Ready Assets
- Retained element-local D4 `current.db` files and M4 committee outputs.
- Retained four-atom FCC source POSCARs in `structures/<X>_benchmark/`.
- Fixed EOS references, which remain validation-only.
- Historical non-FCC task records `01_` through `27_`.
- Active clean restart record: `38_fcc_clean_restart/`.

## Immediate Next Step
Preflight and submit independent Protocol-A D0 VASP labeling for the three
fresh candidate pools. Output DBs and VASP work directories must be new and
element-local.
