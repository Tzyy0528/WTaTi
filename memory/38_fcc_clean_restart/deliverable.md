# Deliverable: Clean FCC 2x2x2 Restart

## Outcome
The prior FCC workflow has been removed. A new, correct restart begins only
from the retained four-atom FCC source POSCARs. Fresh 32-atom `2 2 2` seeds
are published and validated for W, Ta, and Ti; fresh D0 Protocol-A VASP
labeling is submitted.

## Key Results / Decisions
- No prior FCC-generated asset may be reused.
- D4/M4 databases/models and fixed EOS references remain protected.
- Every clean D0 pool contains 100 validated, unique 32-atom FCC-derived
  candidates from only its matching clean `2 2 2` seed.
- D0 label jobs W `13381`, Ta `13382`, and Ti `13383` are queued after
  no-overwrite preflight; their D0 DBs must validate before publication.

## How to Use / Verify
- Before D0 generation, verify every new FCC seed is a 32-atom exact `2 2 2`
  repeat of only its matching four-atom source.

## Files Changed
- `memory/38_fcc_clean_restart/`: clean restart task record.
- `structures/<X>_fcc_restart/<X>-fcc-seed-32.poscar`: new validated
  element-local 32-atom FCC seeds.
- `<X>-potential/fcc-restart/00-input/seed-generation/nninit-poscars/`:
  fresh validated 100-frame 32-atom D0 pools.
- `<X>-potential/fcc-restart/00-input/slurm_logs/`: clean D0 scheduler-log
  directories.
