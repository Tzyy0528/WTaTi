# Task Plan: Clean FCC 2x2x2 Restart

## Goal
Build new independent W, Ta, and Ti FCC active-learning workflows from
correctly expanded 2x2x2 FCC seeds, with no reuse of deleted FCC artifacts.

## Phases
- [x] Phase 1: Cancel FCC jobs and delete all prior FCC-derived paths and
  task records.
- [x] Phase 2: Create and validate new 32-atom FCC seeds from the retained
  four-atom benchmark FCC source cells.
- [ ] Phase 3: Generate, validate, and Protocol-A label fresh D0 pools.
- [ ] Phase 4: Publish validated D0 databases, train M0, and record E0.
- [ ] Phase 5: Continue D1 -> M1 -> E1 -> D2 only from this clean lineage.

## Key Questions
1. Does `2 2 2` replicate every source-cell lattice direction exactly twice,
   producing a 32-atom seed from each four-atom FCC source?
2. Are the fresh FCC roots disjoint from the retained D4/M4 and EOS assets?

## Decisions Made
- A `2 2 2` supercell means two copies in x, y, and z. It is the only
  accepted seed construction for this clean FCC restart.
- The new clean paths reuse the original names only after all prior contents
  were deleted: `structures/<X>_fcc_restart/` and
  `<X>-potential/fcc-restart/`.
- The already-expanded 32-atom seed will be passed to `nninit` with
  replication `1 1 1`; no additional seed replication is intended.

## Errors Encountered
- The first D0 labeling preflight stopped at Ti because the validator's
  manually transcribed expected POTCAR SHA-256 omitted characters. No output
  path was created and no calculation was submitted. Resolution: use the
  recorded full Ti checksum and rerun the read-only preflight.

## Status
**Currently in Phase 3** - new W, Ta, and Ti seeds passed exact `2 2 2`
source-cell validation: each has 32 atoms and all three lattice vectors are
doubled. All three fresh D0 pools have 100 validated 32-atom candidates;
the Protocol-A VASP cards passed no-overwrite preflight. Submit the three
independent D0 label batches next.
