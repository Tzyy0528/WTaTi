# Notes: Phase-Coverage Diagnosis

## Sources

### Source 1: User KSPACING scans
- Paths: `W.csv`, `Ta.csv`, `Ti.csv`
- Key points:
  - The scans contain one energy and pressure result for each spacing from
    `0.50` to `0.10`.
  - Relative to `0.10`, the `0.20` energy differences are W `-1.956`,
    Ta `-1.151`, and Ti `-0.872` meV/atom, assuming the energy column is in
    eV/atom as its magnitude and the workflow records indicate.
  - The corresponding pressure-column differences are W `+0.169`, Ta
    `+0.301`, and Ti `+0.008` in the CSV's unstated pressure unit.

### Source 2: Fixed Protocol-B EOS references
- Paths: `results/<X>_eos_benchmark/eos_reference/eos_reference.csv`
- Key points:
  - The DFT minima define the following relative phase energies:

    | Element | Stable phase | bcc | fcc | hcp |
    |---|---|---:|---:|---:|
    | W | bcc | 0.00 | 499.46 | 514.32 |
    | Ta | bcc | 0.00 | 252.98 | 286.96 |
    | Ti | hcp | 99.24 | 55.70 | 0.00 |

    Values are meV/atom.

### Source 3: M3 E3 EOS-validation record
- Path: `memory/22_M3_E3_eos_validation/notes.md`
- Key points:
  - E3 raw / phase-aligned EOS MAE (meV/atom) is W `72.98 / 7.12`, Ta
    `59.58 / 6.99`, and Ti `40.04 / 4.75`.
  - The much smaller aligned errors indicate that the EOS shapes within
    phases are substantially better learned than their relative offsets.

### Source 4: Ti per-phase EOS metrics
- Paths: `results/Ti_eos_benchmark/evaluations/E0_M0/eos_metrics.csv`,
  `results/Ti_eos_benchmark/evaluations/E3_M3/eos_metrics.csv`
- Key points:
  - Ti E3 HCP raw / phase-aligned MAE is `5.692 / 0.843` meV/atom, and its
    EOS grid-minimum volume shift is `0.000 A3/atom`.
  - The HCP raw error is a nearly uniform positive NNAP energy offset of
    `4.6--6.5` meV/atom across the 19 EOS points, not a badly reproduced
    curvature or equilibrium volume.
  - HCP was better in E0 (`3.216 / 0.512` meV/atom) than E3, despite the
    original HCP seed.

## Commands and Observations

```bash
python3 -  # Parse the CSV scans and compare KSPACING 0.20 with 0.10.
python3 -  # Group fixed EOS-reference rows by phase and find DFT minima.
```

- W and Ta show small non-monotonic energy/pressure changes as the automatic
  k-point mesh changes, but no large systematic shift near `0.2`.
- The completed D0 configuration began W/Ta from bcc and Ti from hcp.
  Short MD/NPT trajectories seeded from one crystalline topology mostly
  explore distortions of that topology; they need not cross reconstructive
  bcc/fcc/hcp barriers. Projected CUR diversifies a supplied candidate pool,
  but cannot select a topology absent from it.
- An HCP initial seed does not guarantee that later uncertainty-gated
  selection retains an accurate static HCP equilibrium neighborhood. The
  D0 HCP perturbations are retained, but the 400 later selected structures
  can shift the finite-capacity fit toward stressed/high-temperature sampled
  environments. Random-split test MAE measures that training distribution,
  not the exact two-atom static EOS cells.

## Synthesized Findings

### Diagnosis
- The supplied scan supports retaining `KSPACING = 0.2`; it is unlikely to
  explain raw EOS errors of 40--73 meV/atom by itself.
- The multi-phase relative-energy task is difficult, particularly for W and
  Ta, whose fixed-reference fcc/hcp minima lie roughly 0.25--0.51 eV/atom
  above bcc.
- The initial single-phase pools therefore provide a plausible, primary
  explanation for poor raw cross-phase EOS transfer. This is consistent with
  the E3 raw-versus-aligned error pattern.
- Ti HCP is quantitatively the best E3 phase. Its remaining absolute offset
  may reflect training-distribution weighting or the 16-atom training versus
  two-atom EOS representation/DFT numerical mismatch. A matched static
  2-atom/16-atom Protocol-A convergence check is required to distinguish
  those explanations; the existing single-cell KSPACING scan cannot do so.

### Future-Round Recommendation
- After M4 is complete and validated, define phase-aware, independently
  generated Protocol-A candidate sources for each element's bcc/fcc/hcp
  structures, with near-equilibrium and compressed/expanded perturbations.
- Do not place EOS structures or Protocol-B labels into `current.db`; use
  separate Phase-A seed/candidate structures and Protocol-A DFT labels.
- Retain/add independent, perturbed 16-atom HCP configurations near its
  equilibrium neighborhood for Ti; do not add the validation EOS structures
  or labels themselves.
- First score such independent phase candidates with the current committee.
  Then apply the existing all-frame uncertainty, physical gate, and
  current.db-projected CUR policy to the combined, source-labelled pool.
