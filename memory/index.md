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
The three clean-D1 selections passed independently and Protocol-A labels are
submitted only for their matching element-local sets. Ta D1 labels passed
full validation, were merged in D0-then-D1 order, and were atomically
published as the 200-row
`Ta-potential/fcc-restart/current.db` (SHA-256
`69b733947c729bd4aa5685f8598ceb8a4356be80f5f00797dd3b156e051cf95a`).
Ta M1 job `13448` completed successfully and passed the ten-model,
5,000-epoch, 180/20-fold validation. The earlier empty-directory report was
an `fd` ignore-rule inspection error; generated JNN/DB/log files are ignored
by `.gitignore` and were present. Ta E1 completed against only the fixed
57-point EOS reference. Aggregate raw/aligned MAEs are
`66.435829/8.339454` meV/atom versus E0
`16.182558/13.358162`: raw cross-phase error regressed while phase-aligned
shape error improved. No D2 step is started.

Ti D1 labels likewise passed validation, were merged in D0-then-D1 order,
and were atomically published as the 200-row
`Ti-potential/fcc-restart/current.db` (SHA-256
`f2874ac425d45bacf41c1e78503e7ece08c59c477b7ad219926e32f4bada577b`).
Ti M1 `13450` and W M1 `13453` both completed successfully and passed
independent ten-model, 5,000-epoch, 180/20-fold validation. Their fixed
57-point E1 evaluations also passed. Aggregate raw/aligned MAEs (meV/atom)
are W E0 -> E1 `131.064897/28.027437 -> 64.413224/21.424392`, and Ti E0 ->
E1 `36.024202/7.434641 -> 14.103997/1.962939`; both metrics improve for W
and Ti. No D2 step is started without a separate scientific decision. The
deleted D1 score CSVs and all superseded selection cards must not be reused.
