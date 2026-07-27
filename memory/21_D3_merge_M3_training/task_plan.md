# Task Plan: D3 Merge and M3 Committee Training

## Goal
Merge each validated 100-row D3 label DB with its matching 300-row base,
publish only validated 400-row element-local `current.db` successors, and
train independent M3 committees from them.

## Phases
- [x] Phase 1: Preflight base/label/output isolation and merge the three D3
  databases.
- [x] Phase 2: Validate 400-row merged DBs and atomically publish matching
  `current.db` files.
- [x] Phase 3: Preflight and submit independent protected M3 committee jobs.
- [x] Phase 4: Validate completed M3 committee artifacts and deliver; do not
  start E3.

## Key Questions
1. Does each merge preserve all 300 base rows before its own 100 D3 labels?
2. Do only validated element-local 400-row successors replace `current.db`?
3. Do M3 committees use exactly their own published 400-row D3 database?

## Decisions Made
- The user authorized D3 merge followed by M3 committee training.
- Each merge is no-overwrite and element-local; DFT label DBs and EOS data
  remain separate from `current.db`.
- M3 uses the established ten-model, five-worker, 5,000-epoch training
  configuration after a fresh `ENERGY` reference audit.
- All validated 400-row `updated.db` files were atomically published to only
  their matching element-local `current.db`; the M3 preflight reconfirmed
  finite unary/no-EOS rows and matching training-reference energies.

## Errors Encountered
- The first publication loop had a transcription error in the Ti expected
  updated-DB SHA-256, so it stopped before modifying Ti after publishing W and
  Ta. Resolution: verified Ti still had its original 300-row hash, corrected
  the SHA-256, then atomically published only Ti; all three final hashes and
  row counts were subsequently verified.
- A combined memory update had stale `memory/index.md` context after the task
  records were written. Resolution: re-read the index and applied its concise
  state update separately; no workflow artifact was affected.

## Status
**Complete** - M3 jobs W `13221`, Ta `13222`, and Ti `13223` completed `0:0`.
Each committee passed ten-model, 5,000-epoch, complete disjoint 360/40-fold
coverage validation against only its matching published 400-row D3 database.
