# Deliverable: Phase-Coverage Diagnosis

## Outcome
The user-supplied KSPACING scans support retaining the frozen
`KSPACING = 0.2` setting. The stronger explanation for the current EOS
transfer issue is insufficient bcc/fcc/hcp phase coverage in candidate and
training data.

## Key Results / Decisions
- `0.20` differs from `0.10` by only 1.956, 1.151, and 0.872 meV/atom for W,
  Ta, and Ti, respectively.
- Fixed-reference phase energy gaps reach 499--514 meV/atom for W and
  253--287 meV/atom for Ta; Ti has 56--99 meV/atom non-ground-state gaps.
- E3 phase-aligned MAEs (4.75--7.12 meV/atom) are far below raw MAEs
  (40.04--72.98 meV/atom), indicating phase-relative energy offsets rather
  than a broadly poor intraphase EOS shape.
- Ti HCP is not a poor E3 EOS curve: it has `5.692` meV/atom raw MAE but
  `0.843` meV/atom phase-aligned MAE and the exact grid-minimum volume. It is
  a small energy offset and is modestly worse than its E0 HCP result.
- Do not modify existing databases, EOS labels, or the running M4 jobs.

## How to Use / Verify
- Inspect `W.csv`, `Ta.csv`, and `Ti.csv` for the KSPACING scan.
- Inspect `results/<X>_eos_benchmark/eos_reference/eos_reference.csv` for
  the fixed DFT EOS phase minima.
- See `notes.md` for exact calculations and a phase-aware future-round
  acquisition recommendation.

## Files Changed
- `memory/27_phase_coverage_review/`: diagnosis record only.
