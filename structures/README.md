# Structure Inputs

This directory is intentionally empty of atomic structures.

Provide ASE-readable POSCAR/VASP files under one element-specific benchmark
directory only:

```text
W_benchmark/W-seed.poscar
W_benchmark/W-<phase>.poscar
Ta_benchmark/Ta-seed.poscar
Ta_benchmark/Ta-<phase>.poscar
Ti_benchmark/Ti-seed.poscar
Ti_benchmark/Ti-<phase>.poscar
```

`*-seed.poscar` is for seed perturbations. `*-<phase>.poscar` is a fixed
source structure for EOS validation. Do not place generated EOS scales,
selected structures, trajectories, or DFT outputs here.

Before use, record the structure provenance, phase, cell convention, PBC,
atom count, and whether its EOS is fixed-shape or has a specified constrained
relaxation. All structures in a folder must contain only its named element.
