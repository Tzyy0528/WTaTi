# Memory Index

## Current State
The independent W, Ta, and Ti workflows completed `D3 -> M3 -> E3` and the
D4 database transition. Every element-local `current.db` is a validated
500-row D4 successor. M4 jobs completed successfully; E4 remains deferred.

All prior FCC-derived structures, databases, models, trajectories, labels,
evaluations, scheduler outputs, and task records were deleted on user
instruction. A clean FCC restart is active in `28_fcc_clean_restart/`.

The fixed validation-only references remain under:

- `results/W_eos_benchmark/`
- `results/Ta_eos_benchmark/`
- `results/Ti_eos_benchmark/`

## Active Gate / Blocker
Fresh W, Ta, and Ti seed POSCARs are validated exact `2 2 2` repeats of only
their retained four-atom benchmark FCC sources: 32 atoms and all three
lattice-vector lengths doubled. Each fresh `fcc-restart/` root now contains
only its matching validated 100-frame 32-atom D0 candidate pool. Clean D0
Protocol-A VASP jobs W `13381`, Ta `13382`, and Ti `13383` completed `0:0`.
All three matching 100-row, finite 32-atom label DBs passed complete
validation and are atomically published as only their matching clean FCC D0
`current.db`. Clean M0 committee jobs W `13395`, Ta `13396`, and Ti `13397`
completed `0:0`; every ten-model 5,000-epoch committee and its fixed
57-point E0 output passed validation. E0 aggregate raw/aligned MAEs
(meV/atom) are W `131.064897/28.027437`, Ta `16.182558/13.358162`, and Ti
`36.024202/7.434641`. The user authorized deleting all old D1 trajectories,
scores, and D1-local logs after their jobs were confirmed inactive. Fresh
lower-temperature (`1.10*T_m`) D1 jobs W `13421`, Ta `13422`, and Ti
`13423` completed `0:0` from the same validated 32-atom seeds and M0
committees. All replacement five-source trajectories passed complete
finite-output and command-provenance validation.

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
- Active clean restart record: `28_fcc_clean_restart/`.

## Immediate Next Step
Replacement all-frame score-only jobs W `13429`, Ta `13430`, and Ti `13431`
completed `0:0`; every replacement 25,005-row CSV passed all-frame,
provenance, and score-only-output validation. The mandatory M0 mean-test
force-MAE cutoffs are recomputed as W `0.088824`, Ta `0.063869`, and Ti
`0.038361` eV/A. The user has superseded the provisional 25/75 saved-frame
candidate/final decorrelation policy: future clean-D1 selection will not
apply temporal source gaps. The new selection policy is absolute-U, 80% of
matching-D0 minimum distance, 115% of matching-D0 normalized periodic
maximum-empty-sphere metric, current.db-projected CUR, and a p99 tail cap of
five structures. It uses target 100 for each element and preserves force,
volume, and source distributions as auditable diagnostics rather than
automatic hard rejections. After code/documentation updates and a complete
no-overwrite preflight, clean-D1 selection jobs W `13440`, Ta `13441`, and
Ti `13442` were submitted. A later focused check found Ta `13441` completed
while W/Ti were still running; a subsequent focused check found all three
selection jobs terminally successful. Complete W/Ta/Ti output validation
passed, with exactly 100 final 32-atom POSCARs for each element. Protocol-A
DFT jobs are now submitted for the matching selected sets: Ta `13444`
(`RUNNING` on its focused check), W `13445` (`PENDING`), and Ti `13446`
(`PENDING` on their one combined immediate check). Do not poll. On a later
completion request, validate the three element-local label DBs before any
merge, M1, or E1 step. The deleted D1 score CSVs and all old selection cards
remain superseded and must not be reused.
