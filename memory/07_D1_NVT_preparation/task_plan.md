# Task Plan: D1 High-Temperature NVT Preparation

## Goal
Prepare independent W, Ta, and Ti `01-nvt-round-1` high-temperature NVT
sampling from their completed M0 committees.

## Phases
- [x] Confirm the element-local D0/M0/E0 assets and absent D1 output paths.
- [x] Record the common D1 NVT sampling configuration and element temperatures.
- [x] Review the exact SLURM command, resources, and protected output paths.
- [x] Submit independent W, Ta, and Ti NVT sweeps through SLURM.
- [x] Validate all element-local trajectories and MD summaries after completion.
- [x] Score every production frame with the respective M0 committee under SLURM.
- [x] Calibrate element-local `U_min` and apply current.db-projected CUR
  with the approved 100-structure budget per element.
- [ ] Label the selected structures with Protocol-A DFT.

## Fixed D1 NVT Configuration

```text
supercell:       2 2 2
scale factors:   0.90, 0.95, 1.00, 1.05, 1.100
steps:           50000
timestep:        1.0 fs
write interval:  10 steps
log interval:    1 step
HAL tau_r:       0.10
friction:        0.02 fs^-1
```

Element temperatures:

```text
W:  4928.15 K
Ta: 4485.65 K
Ti: 2750.65 K
```

## Submission

| Element | SLURM job ID | Submitted sources |
|---|---:|---:|
| W | 13005 | five NVT scale factors |
| Ta | 13006 | five NVT scale factors |
| Ti | 13007 | five NVT scale factors |

## Status
Jobs 13005 (W), 13006 (Ta), and 13007 (Ti) completed successfully with exit
code 0 on 2026-07-24. Each of the 15 scale sources passed trajectory and
summary validation. All-frame scoring jobs 13011--13013 and projected-CUR
jobs 13017--13019 also completed with exit code 0. Each element now has a
validated, independent 100-structure CUR selection. Protocol-A DFT labeling
is the next stage.
