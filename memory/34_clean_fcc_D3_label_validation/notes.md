# Notes: Clean-FCC D3 Protocol-A Label Validation

## Sources

### Source 1: D3 DFT submission record
- Path: `memory/33_clean_fcc_D3_selection_acceptance_and_dft/`
- Key points:
  - Each element has 100 accepted selected input POSCARs.
  - DFT uses the frozen static Protocol-A settings and its own output DB/work
    root below `03-npt-round-1/`.

### Source 2: Workflow label gate
- Paths: `research-plan.md` section 5.2 and
  `docs/source_function_index.md`.
- Key points:
  - Labels require successful VASP tasks; finite energy, forces, and stress;
    unary expected composition; expected structure count; and matching DB row
    count before a merge can be considered.

## Commands and Observations

```bash
sacct -j 13531,13532,13533 \
  --format=JobIDRaw,JobName%30,State,ExitCode,Elapsed -n -P
```

## Synthesized Findings

### Terminal scheduler status

| Element | Job | State / exit | Elapsed |
|---|---:|---|---:|
| W | `13531` | `COMPLETED / 0:0` | `01:51:25` |
| Ta | `13532` | `COMPLETED / 0:0` | `00:59:26` |
| Ti | `13533` | `COMPLETED / 0:0` | `00:50:18` |

Artifact validation is pending; no database has been merged or published.

### D3 label acceptance

Read-only validation passed for every element:

- its manifest has exactly 100 unique selected input POSCARs and 100 ordered
  prepared task directories; each run summary records 100 successful tasks,
  no failed tasks, and no skipped tasks;
- all 100 task folders have complete OUTCAR markers, nonempty logs, the
  expected eight-rank `srun` command, matching frozen static Protocol-A
  INCAR text, expected local POTCAR SHA-256, and correct source/ENCUT
  metadata;
- each 100-row output DB has exact manifest source order, finite energy,
  `(32,3)` forces, and `(6,)` stress, unary 32-atom 3D-periodic
  positive-cell geometries, and no EOS/cross-element content;
- each DFT DB geometry agrees with its selected source POSCAR within
  `5e-9 A` in cell and wrapped scaled coordinates, and each protected
  element-local 300-row D2 `current.db` remains byte-identical to its
  retained D2 `updated.db`.

| Element | Label DB SHA-256 | Cell energy range (eV) | Maximum abs. force (eV/A) | Max cell / scaled error |
|---|---|---:|---:|---:|
| W | `1fd3f62d90d875415c5b71603d9800f11a619eb8bc0cab813e5dc643fedef4db` | -388.151450800 to -360.382538680 | 15.383723550 | `4.969e-9 A / 4.998e-9` |
| Ta | `49acef02ca56e7dd7335c25895d2bb18209c4177f3f375d5e81c1fedb79137b6` | -354.830259900 to -324.815568770 | 9.149588940 | `4.952e-9 A / 5.000e-9` |
| Ti | `5d0c9ed3f2d5a9cf7eb18edbd0761e8c74911db3e9d76883f9b3c0bfb58de63a` | -235.089638690 to -206.102604280 | 5.861147780 | `4.854e-9 A / 5.000e-9` |

No D3 `updated.db` or M3/E3 output was created. The three labels are ready
for an explicitly authorized, element-isolated merge.
