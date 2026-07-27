# Task Plan: D3 All-Frame Scoring and Projected-CUR Selection

## Goal
Score every validated D3 NPT frame with its matching M2 committee, calibrate
element-local `U_min`, and select 100 protected projected-CUR POSCARs per
element.

## Phases
- [x] Phase 1: Audit D3 inputs, M2 diagnostics, protected scoring/CUR roots,
  and exact runner interfaces.
- [x] Phase 2: Submit and validate independent W, Ta, and Ti all-frame
  `--score-only` jobs.
- [x] Phase 3: Calibrate `U_min` and submit projected-CUR selection jobs.
- [x] Phase 4: Validate exactly 100 selected structures per element and
  deliver.

## Key Questions
1. Do the scoring and selection inputs remain fully element-local and
   protected from overwrite?
2. What are the independently derived M2-log force-error `U_min` values?
3. Do the final selections meet the 100-structure target and all audit/physical
   gate requirements?

## Decisions Made
- The user explicitly authorized sequential scoring then CUR selection of 100
  structures per element.
- Use the full matching M2 committee, D3 NPT pressures, and `--score-only`;
  do not create percentile-bin candidate files.
- EOS data remain validation-only and cannot enter the candidate or selection
  inputs.
- The score and CUR templates will be used unchanged with their protected
  output behavior; CUR source balancing is disabled.
- Calibrated M2-log thresholds are W `0.194310000`, Ta `0.166670000`, and Ti
  `0.125950000` eV/A; each is the arithmetic mean of its ten final test
  `MAE-F` values divided by 1000.
- All three score-only jobs completed `0:0` and their protected all-frame CSVs
  passed row, source/frame, numerical, M2-provenance, and score-only-output
  validation.
- Pending user approval, the recommended policy anchors permissive hard
  physical gates to each element's own D2 Protocol-A labeled envelope rather
  than trimming the D3 pool at p1/p99; it uses 50/100-frame source gaps and a
  qualified-pool-U-p99 tail cap of 10.
- The user approved that recommended D3 CUR policy on 2026-07-25.
- CUR jobs W `13182`, Ta `13183`, and Ti `13184` completed `0:0`; each
  produced 100 unique, finite, unary 16-atom ranked POSCARs with zero
  physical-gate rejections and all provenance/audit artifacts.

## Errors Encountered
- A combined memory patch had stale `memory/index.md` context after the task
  files were updated. Resolution: re-read the index and applied the concise
  index update separately; no workflow artifact was affected.

## Status
**Complete** - D3 all-frame scoring and approved projected-CUR selection are
validated for all elements. No DFT labeling, merge, M3 training, or E3 work
was started.
