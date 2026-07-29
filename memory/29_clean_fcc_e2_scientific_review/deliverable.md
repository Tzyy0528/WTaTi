# Deliverable: Clean-FCC E0/E1/E2 Scientific Review

## Outcome
The clean-FCC D2 EOS evidence is mixed. W and Ta can proceed only to a
targeted, element-specific D3 design after the required NPT stress preflight;
Ti should not begin generic D3 until a read-only diagnosis explains why M2
regressed relative to M1. No workflow asset was changed.

## Evidence

Aggregate raw / phase-aligned fixed-EOS MAEs (meV/atom):

| Element | E0 | E1 | E2 | E2 vs E1 |
|---|---:|---:|---:|---:|
| W | 131.064897 / 28.027437 | 64.413224 / 21.424392 | 67.567137 / 23.830581 | +3.153913 / +2.406189 |
| Ta | 16.182558 / 13.358162 | 66.435829 / 8.339454 | 51.670502 / 9.654377 | -14.765327 / +1.314923 |
| Ti | 36.024202 / 7.434641 | 14.103997 / 1.962939 | 17.053634 / 3.492649 | +2.949637 / +1.529710 |

The values use the unchanged 57-point Protocol-B reference. E1-to-E2 is the
best controlled comparison because both M1 and M2 use 5,000 epochs; E0 is
still the required historical baseline but M0 used 1,000 epochs.

## Element-Specific Recommendation

| Element | Assessment | Recommendation |
|---|---|---|
| W | E2 remains much better than E0 but regresses from E1 in both aggregate metrics. Primary bcc raw MAE worsens strongly, and its minimum-volume shift reaches `-0.628831 A^3/atom`. | Conditional D3 only after a targeted bcc compression/minimum diagnostic and finite-stress preflight. Do not use an unmodified generic NPT card. |
| Ta | E2 recovers raw error from E1 but worsens its shape metric; primary bcc shape and minimum volume regress, and aggregate raw error remains worse than E0. | Conditional D3 design focused on bcc pressure/volume coverage and bcc-hcp relative energetics, with finite-stress preflight. |
| Ti | E2 remains better than E0 but is worse than E1 in both aggregate metrics. Both primary-phase shapes regress, and hcp gains a negative minimum-volume shift. | Hold generic D3. First perform read-only D2 selection/coverage and full-committee EOS-spread diagnosis; redesign a targeted next stage only if that evidence identifies a remediable gap. |

## Decision Limits

- The plan has no numerical EOS acceptance threshold or uncertainty interval,
  so this is a directional rather than statistically significant comparison.
- E0/E1/E2 select one eligible reporting JNN, not a committee-mean EOS.
- EOS references remain validation-only and must not enter any `current.db`.

## How to Use / Verify

Compare:

```text
<X>-potential/fcc-restart/evaluations/E0_M0/eos_metrics.csv
<X>-potential/fcc-restart/evaluations/E1_M1/eos_metrics.csv
<X>-potential/fcc-restart/evaluations/E2_M2/eos_metrics.csv
```

against `research-plan.md` sections 6.3, 11.3, and 13.

## Files Changed
- `memory/29_clean_fcc_e2_scientific_review/`: validation-only review record.
