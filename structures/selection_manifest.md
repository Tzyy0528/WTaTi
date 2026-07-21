# Seed and EOS Structure Manifest

Approved on 2026-07-21.  The same starting geometry is retained as separate
assets when it has separate roles: `*-seed.poscar` is an active-label input,
whereas `*-<phase>.poscar` is EOS-validation-only.

| Element | Active-learning seed | EOS structures | EOS role |
|---|---|---|---|
| W | `W_benchmark/W-seed.poscar` (bcc) | bcc, fcc, hcp | bcc primary; fcc/hcp diagnostics |
| Ta | `Ta_benchmark/Ta-seed.poscar` (bcc) | bcc, fcc, hcp | bcc primary; fcc/hcp diagnostics |
| Ti | `Ti_benchmark/Ti-seed.poscar` (hcp) | bcc, fcc, hcp | hcp and bcc primary; fcc diagnostic |

The initial EOS definition is static: uniformly scale each supplied cell,
keep fractional coordinates and cell shape fixed, and do not perform ionic or
cell relaxations.  In particular, hcp calculations retain the input `c/a`.
EOS structures and their labels must never enter `current.db`.

The volume grid, Protocol A, Protocol B, PAW variant metadata, and
element-specific atomic reference energies remain to be frozen before any
calculation.
