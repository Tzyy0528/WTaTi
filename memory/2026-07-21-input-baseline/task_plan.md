# Input Baseline and Precalculation Plan

## Approved scope

- Develop independent unary NNAP potentials for W, Ta, and Ti.
- Use bcc seeds for W and Ta and an hcp seed for Ti.
- Use bcc, fcc, and hcp as fixed EOS-validation structures for every element.
- Keep EOS labels and generated EOS structures outside all training databases.

## Next gated work

1. Verify the six seed/EOS input assets per element are readable, periodic,
   unary, and correctly associated with their intended phase.
2. Freeze per-element Protocol A (active labels) and Protocol B (EOS labels),
   including PAW identity, ENCUT, k-point density, smearing, spin/SOC,
   convergence, and stress settings.
3. Run isolated-atom Protocol-A calculations and record the reference energy
   used by `src/dbselectandtrain.py`.
4. Approve the explicit EOS volume grid, then generate and label its
   validation-only structures through SLURM.

No VASP, NNAP, MD, RSS, or full-committee calculation is authorized by this
record.
