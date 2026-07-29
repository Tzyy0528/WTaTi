# Memory Index

## Current State
Task `memory/33_clean_fcc_D3_selection_acceptance_and_dft/` accepted all
retained W/Ta/Ti D3 selection artifacts: complete finite score/audit/CUR
provenance, frozen gates/cards, final 100-POSCAR source identity, and
unchanged isolated 300-row D2 bases. Protocol-A DFT batches are submitted:
W `13531`, Ta `13532`, and Ti `13533`. The one immediate check found W/Ta
running and Ti pending resources; no monitoring is active.

The retained non-FCC W, Ta, and Ti workflows are complete through D4/M4;
E4 remains deferred. The clean-FCC restart is complete through D2/M2/E2 in
`memory/28_fcc_clean_restart/`; the user has now authorized all-element D3
launch, tracked in `memory/30_clean_fcc_D3_npt_launch/`.

Clean-FCC D1 is complete for all elements. Each D1 state had 200 validated
finite unary 32-atom rows, its matching M1 committee has ten validated
5,000-epoch models, and E1 uses only the fixed validation EOS reference.

All clean-FCC D2 MD jobs are `COMPLETED 0:0`: W `13456`, Ta `13457`, and Ti
`13458`. Every one of the 15 required source trajectories passed complete
provenance, finite-output, 32-atom/PBC/positive-cell, and frame-count
validation.

All three score-only jobs subsequently completed `0:0`. Every matching
`uncertainty_all_frames.csv` has 25,005 finite rows and 22,505 production
rows with complete M1-only provenance.

The D2 `U_min` values were recalculated from the matching ten final M1
test-force MAEs: W `0.166580000`, Ta `0.144480000`, and Ti
`0.110986000` eV/A. Geometry-audit jobs W `13465`, Ta `13466`, and Ti
`13467` all completed `0:0` and their full protected CSVs passed coverage,
finite-value, provenance, and frozen-gate validation. D2 CUR cards are
frozen in `research-plan.md` section 8.2.2. CUR jobs W `13469`, Ta `13470`,
and Ti `13471` completed `0:0`; their protected outputs passed complete
provenance, gate, CUR, duplicate, selected-POSCAR, and source/tail
validation. Protocol-A DFT jobs W `13477`, Ta `13478`, and Ti `13479` are
completed and passed full label validation. W/Ta D2 additions are atomically
published to their independent 300-row current DBs; M2 jobs `13495`/`13496`
completed and their ten-model, 5,000-epoch 270/30-fold committees passed
validation. Ti retry `13494` completed after the sole transient VASP
failure; its 100-row D2 label DB also passed complete validation, then was
merged and atomically published with its D1 base as a 300-row Ti
`current.db`. Ti M2 job `13512` completed and passed the same ten-model
5,000-epoch 270/30-fold validation. All three fixed-reference E2 evaluations
completed and passed artifact/isolation validation. Their aggregate raw /
phase-aligned MAEs (meV/atom) are W `67.567137 / 23.830581`, Ta
`51.670502 / 9.654377`, and Ti `17.053634 / 3.492649`. No monitoring is
active.

The documented selection workflow now also has
`scripts/slurm/run_md_selection_pipeline.slurm`: after an element-local card
is frozen, it runs score-only uncertainty, geometry audit, and projected CUR
in one protected allocation while retaining all intermediate artifacts. This
is recorded in `memory/31_combined_selection_pipeline/`. User-approved
clean-FCC D3 cards are recorded in `memory/32_clean_fcc_D3_md_validation_selection_card/`;
the production combined selection jobs W `13519`, Ta `13520`, and Ti `13521`
are now all `COMPLETED 0:0`. Their retained selection artifacts have not yet
been independently validated; no monitoring is active.

## Active Gate / Blocker
The clean-FCC E0/E1/E2 review is complete in
`memory/29_clean_fcc_e2_scientific_review/deliverable.md`. No element is a
clear green light for an unmodified D3 NPT card: W and Ta are conditional on
targeted bcc diagnostics/design plus finite-stress preflight; Ti is held for
a read-only D2 coverage/selection and full-committee EOS-spread diagnosis.
The user has explicitly overridden that review hold for an all-element
clean-FCC D3 launch. Task 30 passed all 30 finite-stress/NPT and no-overwrite
checks, then submitted D3 jobs W `13513`, Ta `13514`, and Ti `13515`. The
jobs later completed `0:0`, and task 32 validated all 21 NPT sources:
matching M2-only provenance, seven 5,001-frame finite 32-atom trajectories,
and seven 50,001-row finite NPT summaries per element. Task 32 then froze
the target-100 combined selection cards, passed final no-overwrite guards,
and submitted W `13519`, Ta `13520`, and Ti `13521`; all selections are now
`COMPLETED 0:0`, but their outputs remain to be validated. No monitoring is
active.

## Standing Constraints
- Keep W, Ta, and Ti databases, models, pools, trajectories, and outputs
  completely isolated.
- EOS references are validation-only and must never enter `current.db`.
- D2 uses only the matching D1 DB, 32-atom seed, and all ten M1 JNNs.
- D2 selection must be recalibrated from its own pool; do not loosen later
  geometry gates or reuse D1 numerical calibration values.
- Do not overwrite generated outputs, use legacy `nncalc`, or run E4.

## Ready Assets
- Matching clean-FCC 32-atom seeds, D2 selected pools, validated label DBs,
  isolated 300-row D2 current DBs, validated M2 committees, and protected
  E2 outputs for W, Ta, and Ti.
- Fixed EOS references below `results/<X>_eos_benchmark/`.
- D2 scheduler roots:
  `<X>-potential/fcc-restart/02-nvt-round-2/slurm_logs/`.
- Complete task record: `memory/28_fcc_clean_restart/`.

## Immediate Next Step
Wait for a user-requested focused D3 DFT status/completion check, then
read-only validate each element-local label DB (task/manifest completion,
Protocol-A/POTCAR identity, finite energy/forces/stress, and exact selected
source geometry) before any D3 merge. Preserve EOS results as validation-only;
merge, M3, and E3 remain unauthorized.
