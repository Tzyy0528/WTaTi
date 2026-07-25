# Deliverable: D1 High-Temperature NVT Preparation

## Ready Configuration

- W, Ta, and Ti have independent D0/M0/E0 baselines and ten-model M0
  committees.
- D1 NVT uses a `2 2 2` supercell, five scale factors
  (`0.90, 0.95, 1.00, 1.05, 1.100`), and the recorded high-temperature target
  for each element.
- Final selection is direct absolute-U cutoff followed by current.db-projected
  CUR.

## Completed Work

| Element | NVT SLURM job | Result |
|---|---:|---|
| W | 13005 | COMPLETED, exit 0:0 |
| Ta | 13006 | COMPLETED, exit 0:0 |
| Ti | 13007 | COMPLETED, exit 0:0 |

Each allocation ran five single-core NVT scale sources. All 15 sources passed
validation: their four required outputs are nonempty, their logs report
`Finished MD`, trajectories have 5,001 finite unary 16-atom frames with
positive volumes, and summaries have 50,001 finite rows for steps 0--50,000.

## Completed Selection

All-frame M0-committee scoring completed under SLURM jobs 13011 (W), 13012
(Ta), and 13013 (Ti). The calibrated post-equilibration absolute-U cutoffs and
candidate pools were:

| Element | `U_min` (eV/A) | Candidates | Final CUR structures |
|---|---:|---:|---:|
| W | 6.730613322 | 1,126 | 100 |
| Ta | 3.496426176 | 1,126 | 100 |
| Ti | 5.933101487 | 1,126 | 100 |

Projected-CUR jobs 13017 (W), 13018 (Ta), and 13019 (Ti) completed with exit
code 0. Every final set is element-local and validated: 100 unique finite
unary 16-atom POSCARs with complete CUR provenance. The selected structures
are under `<X>-potential/01-nvt-round-1/absolute-u-projected-cur/`.

## Not Yet Performed

Protocol-A DFT labeling, database merge, training, and EOS evaluation remain
pending. The 300 selected POSCARs must remain element-local and must not be
merged into any `current.db` before their DFT labels are validated.
