# Deliverable: Clean-FCC D3 Merge and M3 Launch

## Outcome
Validated D3 labels were independently merged with their D2 bases, and the
verified 400-row D3 databases were atomically published. Matching M3
committee-training jobs were submitted for W, Ta, and Ti.

## Key Results / Decisions
- Published D3 `current.db` SHA-256: W
  `566bd0cfd13d0e231b692589de91e6f94b3cf51753753e6fce3ca8a70d9659af`,
  Ta `09ab573a20cf35b29c121f1584492a8da5e87d5a97cba4f647802764ca6a1c20`,
  Ti `0a0647a1ec9160124c0a5c24c0838442b7e4f390411d52cffa1f25dfa3d985be`.
- Each D3 database has the exact 300-row D2 prefix plus validated 100-row D3
  suffix; EOS data remain excluded.
- M3 submissions: W `13540`, Ta `13541`, Ti `13542`, each configured as ten
  models, five workers, and 5,000 epochs.

## How to Use / Verify
- Published database: `<X>-potential/fcc-restart/current.db`.
- Retained merged artifact:
  `<X>-potential/fcc-restart/03-npt-round-1/updated.db`.
- On a user-requested completion/status report, validate all ten M3 folds
  before any fixed-reference E3 evaluation.

## Files Changed
- `memory/35_clean_fcc_D3_merge_and_M3_launch/`: task record.
