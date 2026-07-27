# Task Plan: M2 E2 Fixed EOS Validation

## Goal
Validate each completed, independently trained M2 committee against its
matching fixed Protocol-B EOS reference without altering any `current.db`.

## Phases
- [x] Phase 1: Verify and validate prerequisite M2 committee training.
- [x] Phase 2: Audit fixed EOS inputs and protected E2 output paths.
- [x] Phase 3: Submit independent W, Ta, and Ti E2 EOS evaluations.
- [x] Phase 4: Validate E2 artifacts and compare with E1 and E0.

## Key Questions
1. Did every M2 committee finish with ten valid 5,000-epoch models and
   complete 300-row fold coverage?
2. Are the fixed Protocol-B reference inputs and E2 result paths isolated and
   protected for each element?
3. Do E2 EOS metrics improve or stabilize relative to E1 and E0?

## Decisions Made
- E2 uses only the fixed validation references; no EOS structure or label may
  enter an element-local `current.db`.
- W, Ta, and Ti evaluations are independent.
- Run the documented local JSE evaluator separately for each element. This is
  a repository-designated lightweight validation command, not a DFT, training,
  or MD submission.
- Do not start D3 or any later stage in this task. E2 regressed for at least
  one required metric for every element relative to E0 or E1, so any next
  element-local configuration requires explicit review and authorization.

## Errors Encountered
- Two initial custom M2-validator assertions used the wrong ASE `row.symbols`
  shape. They were corrected before the successful validation run; they did
  not modify data or indicate a training/EOS failure.

## Status
**Complete** - all E2 outputs passed validation. W improved versus E1 but
remains worse than E0; Ta regressed versus both; Ti phase-aligned shape
improved but raw EOS error regressed. No later stage was started.
