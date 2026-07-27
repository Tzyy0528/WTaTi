# Notes: Clean FCC 2x2x2 Restart

## Sources

### Source 1: User instruction
- `2 2 2` means expansion in x, y, and z. The prior FCC workflow and its
  memory records were deleted and must not be reused.

### Source 2: Retained source structures
- `structures/W_benchmark/W-fcc.poscar`
- `structures/Ta_benchmark/Ta-fcc.poscar`
- `structures/Ti_benchmark/Ti-fcc.poscar`
- Each is the retained four-atom conventional FCC source for only its own
  element.

## Commands and Observations

### FCC cleanup

Cancellation requests were issued for FCC jobs `13372` through `13377`. A
final focused queue check found no remaining FCC job. The following prior
FCC-derived paths were then deleted:

```text
<X>-potential/fcc-restart/
<X>-potential/fcc-restart-2x2x2/
structures/<X>_fcc_restart/
structures/<X>_fcc_restart_2x2x2/
memory/28_fcc_restart_plan/ through memory/37_fcc_2x2x2_restart/
```

Post-deletion checks found no generated `fcc-restart` or `fcc_restart` path.
The protected D4 database hashes remain W
`d9d851b7e22ef2fdb84eeaa88d7822682e83a33f9de5eb91c188f92c2d0755bc`, Ta
`bce6490107a31f329bd89a30d7505c5e3665357a2f254afdc3e181cdf10698a0`, and
Ti `a68f2c8b4cd5e41788463566737fafa80e1e9b70a4c7a7006a953c57a922c6d2`.
All six fixed EOS metadata/reference hashes also match their recorded
identities.

## Synthesized Findings

- The clean restart has no D0 database, candidate pool, VASP work directory,
  committee, trajectory, selection, label, EOS prediction, or memory record
  inherited from the deleted FCC work.
- New seed validation must show 32 atoms and all three lattice-vector lengths
  exactly twice their respective retained four-atom source lengths.

### New seed construction and validation

Each fresh seed was written only after confirming that the new seed and
potential root paths were absent. It is an exact ASE `repeat((2, 2, 2))` of
only its matching retained source, with no additional transformation.

| Element | Source lengths (A) | Seed lengths (A) | Seed volume (A^3) | Minimum distance (A) | Seed SHA-256 |
|---|---|---|---:|---:|---|
| W | 3.991978500, 3.991978500, 3.991978500 | 7.983956999, 7.983956999, 7.983956999 | 508.925916812 | 2.822755067 | `43a64fcfafcd40792f69a8d51f3e73f8bee45bfcad84e8753e124c8a78a18d7c` |
| Ta | 4.171811608, 4.171811608, 4.171811608 | 8.343623215, 8.343623215, 8.343623215 | 580.850077277 | 2.949916278 | `76a07c56ec86b095195a4c0b7662385201f6ebb0175192d3dd2050092818b7b6` |
| Ti | 4.109149077, 4.109149077, 4.109149077 | 8.218298154, 8.218298154, 8.218298154 | 555.067346400 | 2.905607177 | `6072199ca77de8276f36c49e9beb4926b20c40ad271022e9df7aa912cdf136d1` |

Before atomic publication, each seed passed 32-atom unary composition,
3D-PBC, finite geometry, positive volume, positive minimum distance, exact
`2 * source_cell`, and exact wrapped-fractional-coordinate checks.

### D0 candidate-generation preflight

Under `module load jse`, `nninit` is available. Every new seed passes the
32-atom unary/PBC/finite/positive-volume check, and its matching
`<X>-potential/fcc-restart/` root and D0 pool are absent. The clean D0 card
uses no further supercell replication:

```bash
nninit <X> <X>-potential/fcc-restart/00-input/seed-generation/nninit-poscars \
  20 structures/<X>_fcc_restart/<X>-fcc-seed-32.poscar _ 1 1 1 \
  0.90,0.95,1.00,1.05,1.10 0.03
```

This creates 20 controlled perturbations at each of five scales, for 100
fresh 32-atom candidates per element.

### D0 candidate generation and validation

All three `nninit` commands completed successfully. Each pool contains exactly
100 consecutively named `<X>-00000.poscar` through `<X>-00099.poscar` files.
Every candidate is a unique, finite, unary, 3D-periodic 32-atom structure
with positive volume and minimum distance; no EOS or cross-element content is
present.

| Element | Volume/atom range (A^3) | Minimum-distance range (A) | Batch mean volumes/atom (A^3), scales 0.90 -> 1.10 | Ordered pool SHA-256 |
|---|---:|---:|---|---|
| W | 10.496816--22.888130 | 2.119496--2.906086 | 11.639258, 13.759711, 15.519430, 18.176808, 21.144842 | `b4524b7407e5fa9473ba9e450657b5b5c0b6494639042691724b6ce00e399c7d` |
| Ta | 11.757120--27.282647 | 2.219146--3.008631 | 13.333753, 15.588560, 18.134875, 21.061448, 24.387709 | `0a029dfa656f7360b200ebfa714100989aadc00ce360475329c5aeadbc57f484` |
| Ti | 11.150612--24.979403 | 2.219088--2.926410 | 12.591146, 14.731710, 17.528736, 19.586982, 22.862436 | `ba4c59ba7dd96bdac5ec801badcfe893707a2bd59666e6360839f8b8a7b17873` |

### D0 Protocol-A labeling preflight

The current `vasp_batch_dft.py label` CLI and the established static
Protocol-A card were checked. Each matching pool has 100 VASP5 POSCARs with
the expected unary `32`-atom header; the clean label DB, default VASP work
directory, clean FCC `current.db`, and scheduler-log directory are absent.
The current training reference energies are W `-12.9581`, Ta `-11.8578`, and
Ti `-7.8951` eV.

The first read-only preflight halted at Ti because its expected POTCAR
checksum was transcribed incorrectly in the validator. It created no output
and submitted no VASP job. The preflight will be rerun using the recorded
complete Ti checksum.

The rerun passed for all elements. The PAW SHA-256 / ENMAX / auto-ENCUT values
are W `c0897285...8170117 / 223.057 / 289.9741`, Ta
`b94d0231...3d269f3 / 223.667 / 290.7671`, and Ti
`f8e8f1d0...f5a1479e / 178.330 / 231.8290` eV. The retained D4 database
hashes remain unchanged.

The clean D0 labels use the frozen static Protocol-A settings:

```text
ISTART=0; ICHARG=2; PREC=Accurate; ALGO=Normal; EDIFF=1E-5; NELM=200
SIGMA=0.1; KSPACING=0.2; KGAMMA=.TRUE.; LASPH=.TRUE.; LREAL=Auto
ISYM=0; KPAR=1; NCORE=2; NSIM=6; IBRION=-1; NSW=0; ISIF=2
```

The no-overwrite submission card is one node, 64 tasks, 24 hours, eight VASP
ranks per calculation, and at most eight concurrent calculations. It makes
no partition, account, or GPU request:

```bash
sbatch --job-name=fcc_d0_<X> --nodes=1 --ntasks=64 --time=24:00:00 \
  --output=<X>-potential/fcc-restart/00-input/slurm_logs/fcc-d0-%j.out \
  --error=<X>-potential/fcc-restart/00-input/slurm_logs/fcc-d0-%j.err \
  scripts/slurm/run_vasp_batch_dft.slurm \
  <X>-potential/fcc-restart/00-input/seed-generation/nninit-poscars \
  <X>-potential/fcc-restart/00-input/<X>_FCC_D0_labeled.db _ 0.2
```

Neither `OVERWRITE` nor `FORCE_PREPARE` is set. The distinct default VASP
work directory is `00-input/dft/vasp_<X>_FCC_D0/`.

### Clean D0 Protocol-A submissions

After preflight, only the new required `00-input/slurm_logs/` directories
were created. The documented commands were submitted unchanged:

| Element | Job ID | Candidate input | Label DB output | Immediate status |
|---|---:|---|---|---|
| W | `13381` | `W-potential/fcc-restart/00-input/seed-generation/nninit-poscars/` | `W-potential/fcc-restart/00-input/W_FCC_D0_labeled.db` | `PENDING` |
| Ta | `13382` | `Ta-potential/fcc-restart/00-input/seed-generation/nninit-poscars/` | `Ta-potential/fcc-restart/00-input/Ta_FCC_D0_labeled.db` | `PENDING` |
| Ti | `13383` | `Ti-potential/fcc-restart/00-input/seed-generation/nninit-poscars/` | `Ti-potential/fcc-restart/00-input/Ti_FCC_D0_labeled.db` | `PENDING` |

One combined immediate `squeue` check was made after all three submissions.
No polling loop was started. No clean FCC D0 `current.db`, committee,
trajectory, selection, or EOS output exists yet.
