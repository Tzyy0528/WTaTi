# Unary Iteration Initialization

## Scope

Start the three independent W, Ta, and Ti unary-potential workflows without
launching calculations before Gate 0 is approved.

## Planned stages

1. Verify Python entry points, JSE/ASE readability of every seed and EOS
   source structure, and local PAW metadata.
2. Freeze and record Protocol A and Protocol B separately for W, Ta, and Ti.
3. Retain the user-approved historical W, Ta, and Ti reference energies in
   `src/dbselectandtrain.py::ENERGY`; do not run new isolated-atom jobs.
4. Use the approved common D0 design: `2 2 2` seed supercell, 20 structures
   at each of scales `0.90,0.95,1.00,1.05,1.10`, and disturbance amplitude
   `0.03`; approve the D0 minimum-distance gate and stage-01 NVT
   sampling/calibration sheets.
5. Review exact SLURM commands, resources, output paths, and overwrite
   behavior before any VASP, training, MD, or RSS submission.

## Stop condition

Do not create DFT labels, databases, committees, trajectories, EOS results,
or selection outputs until Gate 0 is complete for the element being started.
