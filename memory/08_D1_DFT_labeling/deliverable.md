# Deliverable: D1 Protocol-A DFT Labeling

## Delivered Label Databases

| Element | Labeled DB | Result |
|---|---|---|
| W | `W-potential/01-nvt-round-1/W_D1_selected_labeled.db` | 100 validated rows |
| Ta | `Ta-potential/01-nvt-round-1/Ta_D1_selected_labeled.db` | 100 validated rows |
| Ti | `Ti-potential/01-nvt-round-1/Ti_D1_selected_labeled.db` | 100 validated rows |

VASP jobs 13025, 13026, and 13027 completed successfully. The three batches
have 300 successful static DFT labels in total, each retained under its own
element root with its manifest, run summary, exact command, and VASP tasks.

At the completion of this DFT stage, no `current.db` had been modified. The
subsequent validated D1 merge and M1-training activity is recorded separately
under `memory/09_D1_merge_M1_training/`; E1 EOS validation remains unstarted.
