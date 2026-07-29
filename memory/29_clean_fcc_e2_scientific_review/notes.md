# Notes: Clean-FCC E0/E1/E2 Scientific Review

## Sources

### Source 1: Clean-FCC task record
- Path: `memory/28_fcc_clean_restart/`
- Key points:
  - W, Ta, and Ti have independent 300-row D2 current DBs, validated M2
    committees, and fixed-reference E2 outputs.
  - EOS references are validation-only.

### Source 2: Research plan
- Path: `research-plan.md`, sections 6.1--6.3, 11.3, 12, and 13.
- Key points:
  - The identical 57-point fixed EOS reference (19 each bcc/fcc/hcp) is
    required for E0, E1, and E2 comparison.
  - W/Ta primary EOS phase is bcc; Ti primary phases are bcc and hcp.
  - Compare raw cross-phase error, phase-aligned shape error, and
    grid-minimum volume shifts. If EOS regresses, preserve evidence and
    adjust the next element-local stage.
  - D3 is an M2-driven NPT stage and requires finite calculator stress.

### Source 3: Protected EOS metrics
- Paths: `<X>-potential/fcc-restart/evaluations/E0_M0/`,
  `E1_M1/`, and `E2_M2/` for each element.
- Key points:
  - Each metric CSV has bcc/fcc/hcp and aggregate rows for the unchanged
    reference.
  - The selected reporting JNN is not a committee-average EOS result.

## Commands and Observations

```bash
# Read-only aggregation of protected E0/E1/E2 metric and selection CSVs.
python3 - <<'PY'
# Parsed aggregate and phase raw/aligned MAEs, grid-volume shifts, selected
# fold diagnostics, eligible-model counts, and E1/E0/E2 deltas.
PY
```

## Synthesized Findings

### Aggregate fixed-reference EOS MAEs

All values are meV/atom; lower is better. Deltas are E2 minus E1.

| Element | E0 raw / aligned | E1 raw / aligned | E2 raw / aligned | E2 - E1 raw / aligned |
|---|---:|---:|---:|---:|
| W | 131.064897 / 28.027437 | 64.413224 / 21.424392 | 67.567137 / 23.830581 | +3.153913 / +2.406189 |
| Ta | 16.182558 / 13.358162 | 66.435829 / 8.339454 | 51.670502 / 9.654377 | -14.765327 / +1.314923 |
| Ti | 36.024202 / 7.434641 | 14.103997 / 1.962939 | 17.053634 / 3.492649 | +2.949637 / +1.529710 |

Relative to E0, E2 raw/aligned changes are W
`-63.497760 / -4.196856`, Ta `+35.487944 / -3.703785`, and Ti
`-18.970568 / -3.941992` meV/atom.

### Primary-phase and minimum-volume evidence

- W bcc (primary): E2 versus E1 raw MAE worsens
  `40.853701 -> 90.265501`, while phase-aligned MAE improves
  `35.650159 -> 28.865127`; its minimum-volume shift becomes
  `-0.628831 A^3/atom` (from `-0.316526`). E2 improves W hcp raw MAE
  but worsens its shape error and minimum volume.
- Ta bcc (primary): E2 improves raw MAE
  `91.344289 -> 55.374184` but worsens phase-aligned MAE
  `13.170284 -> 19.538054` and shifts the minimum by
  `-0.360187 A^3/atom` (from `-0.180696`). Ta hcp improves in both raw
  and phase-aligned MAE from E1, but E2 aggregate raw error remains more
  than three times the E0 baseline.
- Ti bcc and hcp (both primary): E2 worsens bcc raw/aligned MAE
  `7.967100/2.141632 -> 21.615028/4.034564`; it improves hcp raw MAE
  `33.328286 -> 28.748446` but worsens hcp aligned MAE
  `3.158984 -> 6.087005` and introduces a `-0.171466 A^3/atom`
  minimum-volume shift. E1 is superior to E2 for both aggregate metrics.

### Interpretation and limits

- The fixed reference and metric definitions are unchanged, so directional
  E0/E1/E2 comparison is valid.
- M0 used the historical 1,000-epoch training policy while M1/M2 use 5,000
  epochs. Therefore E1-to-E2 best isolates the effect of the D2 addition;
  E0 remains the required baseline rather than a controlled training-policy
  comparison.
- No numerical acceptance threshold, EOS confidence interval, or
  full-committee EOS spread is defined. The result is a directional
  scientific assessment, not a statistical-significance claim.
- No element is a clear green light for an unmodified D3 card. W and Ta have
  mixed evidence suitable only for targeted D3 design; Ti should be held
  pending a read-only D2 coverage/selection diagnosis.
