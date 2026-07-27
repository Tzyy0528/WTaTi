# Notes: D4 Protocol-A VASP Labeling

## Sources

### Source 1: D4 selection record
- Path: `memory/24_D4_validation_scoring_selection/`
- Key points:
  - Each element has an isolated, audited set of 100 selected D4 POSCARs.
  - `current.db` remained at the 400-row D3 state after selection.

### Source 2: Workflow requirements
- Path: `research-plan.md`, `docs/source_function_index.md`
- Key points:
  - New labels use `src/vasp_batch_dft.py` through the SLURM VASP template.
  - A completed label DB must have one successful task per input, finite energy/forces/stress, expected unary composition, and matching row count.

## Commands and Observations

### Initial terminal-state check (2026-07-26)

```bash
sacct -j 13248,13249 --format=JobID,JobName,State,ExitCode,Elapsed,Start,End -n -P
```

- W job `13248` and Ta job `13249` are `COMPLETED` with exit `0:0`.
- Earlier state records show Ti job `13250` was also `COMPLETED 0:0` and its 100-row label DB passed validation.

### Final D4 label artifact validation (passed)

Each D4 VASP command used only its matching selected-POSCAR directory,
element-local output DB, and element-local work root. All commands retained
the frozen static Protocol-A controls: `MAGMOM=_`, `KSPACING=0.2`,
automatic `ENCUT=1.3*max(ENMAX)`, `NCORE=2`, eight 8-rank concurrent VASP
tasks, and `vasp_std`.

Every element has 100 normal-completion-marked `OUTCAR`s and a matching
100-row label DB. Each row maps one-to-one to a selected `000001.poscar` --
`000100.poscar` input; has the expected unary 16-atom, fully periodic
composition; positive finite cell volume; finite energy, `(16,3)` forces, and
six-component stress; and no EOS or cross-element source. The static
OUTCAR-to-POSCAR geometry round trip agrees within `4.815e-08 A` for
positions and `4.994e-09 A` for cell entries.

| Element | Label DB SHA-256 | Energy range (eV/16-atom cell) | Volume range (A3/16-atom cell) |
|---|---|---:|---:|
| W | `c32006c90312bc82e3e210613347d789bf173bcf267d774ecacff27069f552c1` | -199.877967730 to -179.412112870 | 213.988355760 to 343.570966112 |
| Ta | `d601c6c22a5eaa7349afb60cad1b4d7832a6cd4f596a1e5f9a3d4141fc7ec663` | -182.187701280 to -167.307811320 | 232.135547609 to 361.695573360 |
| Ti | `b3152128e7d8fcd950e78fa143982a46b65fecc31191b4b519a4c1c57f23c78e` | -119.379650880 to -97.167485310 | 176.918478374 to 317.366094286 |

The matching D3 `current.db` files remain at 400 rows, and no D4
`updated.db` exists. This task did not merge labels, publish a successor
database, train M4, or run E4.

## Synthesized Findings

- D4 label artifact validation for W and Ta is required before any merge or successor training decision.
- All three independent D4 label sets now satisfy the protected merge
  preconditions, pending separate user authorization.
