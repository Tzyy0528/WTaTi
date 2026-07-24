# Ta E0 Fixed EOS Evaluation

## Scope

Evaluate only the Ta M0 committee against the fixed Ta bcc/fcc/hcp Protocol-B
EOS reference. The EOS reference, predictions, and metrics are validation-only
and must not enter `Ta-potential/current.db`.

## Inputs and method

1. Parse final committee `MAE-E: train | test` log records.
2. Exclude a fold when the absolute train/test ratio exceeds 1.25.
3. Select the eligible model with the lowest test energy MAE.
4. Use JSE/Groovy to evaluate that one unary Ta JNN on all 57 fixed EOS
   POSCARs.
5. Record raw and phase-aligned energy errors plus grid minimum volumes.

## Completion state

Completed on 2026-07-22. E0 results require user acceptance before any Ta
sampling or MD setup begins.
