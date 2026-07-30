# Task Plan: Clean-FCC D4 Labels Through M4 and E4

## Goal
Validate and separately publish completed W, Ta, and Ti D4 labels, train and
validate their M4 committees, then run and validate fixed-reference E4.

## Phases
- [x] Phase 1: Recover D4 submission state and validate the three D4 label DBs.
- [x] Phase 2: Merge/publish isolated 500-row D4 databases.
- [x] Phase 3: Preflight, submit, and validate three M4 committees.
- [x] Phase 4: Preflight, run, and validate fixed-reference E4.
- [x] Phase 5: Deliver the independent D4/M4/E4 records.

## Key Questions
1. Does every D4 label DB contain exactly the validated selected configurations
   with one finite Protocol-A result per input structure?
2. Can each 400-row D3 base and its own D4 label DB be merged and atomically
   published as an isolated 500-row D4 `current.db`?
3. Do the resulting M4 committees and E4 evaluations meet their artifact,
   fold/provenance, and fixed-reference acceptance conditions?

## Decisions Made
- The user authorized stepwise completion from completed D4 DFT through label
  validation, D4 publication, M4, and E4.
- Keep all W, Ta, and Ti artifacts, databases, model roots, and EOS results
  element-local; EOS references remain validation-only.
- Do not overwrite generated outputs; each gate must pass before downstream
  submission or publication.
- E4 uses only the matching M4 committee and immutable Protocol-B EOS
  reference. It does not update an active-learning database or authorize D5.

## Errors Encountered
- The first read-only D4 label validator compared the full auto-ENCUT value
  to the six-significant-digit INCAR rendering at `1e-8` tolerance. W has
  `1.3*ENMAX=289.9741` eV and `INCAR ENCUT=289.974`; use a `1e-3` eV
  formatting tolerance only for this rendered INCAR value and rerun. No
  artifact was modified.
- The corrected validator fully accepted W and Ta but stopped on an
  unannotated assertion while starting Ti. A focused read-only Ti diagnostic
  found only binary floating-point serialization in every task metadata file:
  stored `encut=231.82900000000004` versus decimal `231.8290`. Compare
  metadata ENCUT numerically at a tight tolerance, then rerun; no generated
  artifact was modified.
- An exploratory `fd` command placed its depth option after the search path
  and printed zero task directories. Direct child-directory globbing correctly
  found 100 VASP task directories per element; no artifact was modified.
- The first atomic-publication helper omitted `module load jse`, so its ASE
  import failed before preflight or any filesystem mutation. Reload JSE and
  rerun the same guarded publication.
- The first JSE-loaded retry contained only an accidentally truncated Python
  setup block and made no changes; the following complete guarded invocation
  staged checksum-verified temporary files and atomically published all three
  D4 states.
- The first M4 preflight attempted to import `dbselectandtrain` without the
  repository `src/` on `PYTHONPATH`; it failed before checking or changing an
  artifact. Rerun with `PYTHONPATH=src`, matching the training template.
- The first E4 no-overwrite/reference preflight stopped on an unannotated
  assertion before writing any E4 output. Diagnose the first fixed-reference
  invariant read-only, then rerun the preflight with its actual stable path
  convention. The reference uses generated fixed POSCARs below
  `results/<X>_eos_benchmark/eos_reference/structures/`, not direct paths
  below `structures/<X>_*`; correct that path assertion and rerun.
- An initial post-run local validator assumed every EOS cell contained two
  atoms. The fixed reference correctly uses structure-dependent atom counts
  (bcc 2; fcc/hcp 4). Compare every prediction to its matching metadata and
  reference row instead; no artifact was modified. A typo in the local Ta
  reference checksum constant was similarly corrected before the final
  read-only validation.

## Status
**Complete** - D4 labels and publications, M4 committees, and protected E4
evaluations passed independent element-local validation. No D5/RSS work was
started.
