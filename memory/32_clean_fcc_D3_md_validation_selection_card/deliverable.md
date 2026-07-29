# Deliverable: Clean-FCC D3 MD Validation and Selection Card

## Outcome
All clean-FCC D3 NPT jobs completed successfully and all 21 expected
element-local NPT sources passed read-only validation. The authorized combined
selection jobs were then submitted as W `13519`, Ta `13520`, and Ti `13521`.

## Key Results / Decisions
- W `13513`, Ta `13514`, and Ti `13515` completed `0:0`.
- Each element has 35,007 validated finite 32-atom trajectory frames and
  350,007 finite NPT summary rows across its seven pressure sources.
- D3 score/audit/CUR outputs remain absent and protected.
- The user approved `target=100` per element, the matching clean-D0 geometry
  gates, and `r_c=6.0`, `n_max=5`, `l_max=6`, similarity `0.99999`.
- Frozen U_min values derived from the exact ten M2 logs are W `0.187770000`,
  Ta `0.167500000`, and Ti `0.117740000` eV/A; p99 tail cap is five frames.
- Final element-local no-overwrite guards passed immediately before each
  submission. The one immediate status check found all three jobs running.

## How to Use / Verify
- See `notes.md` for terminal states and source-validation ranges.
- The submitted jobs write protected D3 score, audit, and projected-CUR
  outputs below their own round root. Do not inspect status again unless the
  user requests it; DFT, merge, M3, and E3 remain unauthorized.

## Files Changed
- `memory/32_clean_fcc_D3_md_validation_selection_card/`: task record.
