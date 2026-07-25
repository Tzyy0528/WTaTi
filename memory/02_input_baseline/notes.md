# Notes: Input Baseline and Precalculation Plan

- Local PAW-PBE POTCAR files were confirmed present for W, Ta, and Ti at the
  required element-local paths.  They are not copied, committed, or recorded
  here.
- Seed files were created as role-separated copies of the approved starting
  phase inputs.  The EOS source files remain separate and validation-only.
- An initial static EOS convention was documented: uniform cell scaling with
  fixed shape and fixed fractional coordinates; hcp `c/a` remains fixed.
- The system Python interpreter does not provide `ase`; after `module load
  jse`, ASE successfully read every input.  Each structure is periodic,
  has positive volume, and contains only its folder's named element.
