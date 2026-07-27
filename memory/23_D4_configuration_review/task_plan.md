# Task Plan: D4 Configuration Review and Next-Round Launch

## Goal
Review E3 by element, freeze safe independent D4 sampling configurations, and launch only the authorized next-round work after protected preflight.

## Phases
- [x] Phase 1: Read current E3 state, decision gates, and previous D3 configuration records.
- [x] Phase 2: Select and record element-local D4 sampling and selection parameters.
- [x] Phase 3: Preflight M3 stress capability, paths, inputs, SLURM commands, and no-overwrite behavior.
- [x] Phase 4: Submit independent D4 sampling jobs and record job IDs; do not start scoring, selection, DFT, M4, or E4 without a completed prior stage.

## Key Questions
1. Which element-local D4 sampling configurations are justified by the E3 comparison and established decision gates?
2. Do all M3 committee models provide finite stress for any proposed NPT sources?
3. Are all D4 outputs absent, isolated, protected from overwrite, and backed by a frozen parameter record?

## Decisions Made
- D4 follows the required `04-npt-round-2` stage: use each matching M3
  committee, one established element-local seed, and no EOS structure/label.
- To respond to E3 without untested temperature, seed, or barostat changes,
  retain the validated D3 temperature and NPT controls but use the new
  interleaved pressure grid `2, 8, 15, 25, 35, 45, 55` GPa for each
  independently submitted element. This samples unsampled intermediate
  pressure/volume states and extends the former 50 GPa maximum only modestly.
- Preserve all ten matching M3 JNNs, `--rep 2 2 2`, 50,000 steps, 1 fs,
  write/log intervals 10/1, `tau-r=0.10`, `ttime=75 fs`, `ptime=75 fs`,
  bulk modulus 100 GPa, and `frac-traceless=0.0`.
- The read-only all-model M3 stress preflight passed for every element, so
  NPT is technically eligible pending the immediate protected submission
  preflight.

## Errors Encountered
- The first read-only M3 stress-probe invocation passed Python through standard
  input to `jse --pythontext`; this JSE option requires the program as its
  argument and printed usage without evaluating a model. Resolution: rerun
  the identical probe with the script supplied as the `--pythontext` argument;
  no workflow asset was modified.

## Status
**Complete** - D4 NPT jobs W `13235`, Ta `13236`, and Ti `13237` were
submitted after protected preflight. Do not score or otherwise advance until a
later focused completion check validates all 21 source outputs.
