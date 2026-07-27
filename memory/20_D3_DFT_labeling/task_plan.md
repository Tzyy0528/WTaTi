# Task Plan: D3 Protocol-A VASP Labeling

## Goal
Submit and validate independent Protocol-A VASP labels for the 100 approved
D3 projected-CUR structures of W, Ta, and Ti without changing any database.

## Phases
- [x] Phase 1: Review frozen Protocol-A records, target runner, selected
  inputs, protected output DBs, and SLURM resources.
- [x] Phase 2: Submit the three element-local VASP batch-labeling jobs.
- [x] Phase 3: Validate terminal job states and labeled DB artifacts.
- [x] Phase 4: Deliver the DFT-labeling result; do not merge or train.

## Key Questions
1. Do the existing Protocol-A settings and local POTCAR identities still match
   the prior W/Ta/Ti labeling record?
2. Does every submission consume exactly its own 100 selected POSCARs and
   write only its own absent labeled DB?
3. Are every completed labeled DB's structures finite, unary, and auditable?

## Decisions Made
- The user authorized D3 DFT labeling after the completed CUR selection.
- Reuse the frozen Protocol-A strategy; only pre-submission audit/recording,
  not a scientific protocol change, is required.
- DFT labeling, database merge, M3 training, and E3 are separate stages.
- The current `src/dbselectandtrain.py::ENERGY` values W `-12.9581`, Ta
  `-11.8578`, and Ti `-7.8951` eV agree with the matching M2
  `Trainer.groovy` frozen reference energies.
- W retry will retain every Protocol-A input and use one concurrent 8-rank
  task only, so the runner safely reuses 98 completed tasks and reruns only
  the two incomplete tasks without overwriting any completed output.
- W retry `13220` was submitted with one node, eight tasks, and one 8-rank
  worker; it has no overwrite or force option.
- W retry `13220` completed `0:0`; all three label DBs now have exactly 100
  finite, unary, 16-atom labels and are ready for independent protected
  merges with their matching 300-row bases.

## Errors Encountered
- An initial read-only `rg` command placed `--glob` after the search path,
  producing an option-as-path error. Resolution: repeated the focused search
  with the option before the path and verified the frozen references directly
  from each M2 `Trainer.groovy`; no workflow artifact was affected.
- W initial VASP batch `13185` failed after 98/100 tasks because task
  directories `00092_000092` and `00099_000099` received VASP/MPI exit
  status 139 (`SIGSEGV`) on `lpsnode01`. The output DB was not created;
  all other task OUTCARs are complete. Resolution: submit a no-force,
  one-worker retry against the same protected work root and absent DB.
- The first retry preflight used an overly narrow task-directory pattern and
  stopped before any `sbatch` call. Resolution: corrected the read-only
  directory count to include `00100_000100`, rechecked 98 complete plus two
  incomplete tasks, and submitted only once as job `13220`.

## Status
**Complete** - W/Ta/Ti D3 labels all passed final validation. The next
separate authorized operation is three element-local no-overwrite merges into
400-row `updated.db`; no merge, publication, M3 training, or E3 evaluation
has started.
