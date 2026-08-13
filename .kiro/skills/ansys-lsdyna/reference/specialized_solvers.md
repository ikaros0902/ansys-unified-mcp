# Specialized Solvers — condensed reference

LS-DYNA's multiphysics and specialized solvers. Each has its own keyword group;
card fields come from `LS-DYNA_Users_Guide` and the analysis guides.

## ALE / fluid-structure

- `*ALE_*` (e.g. `*ALE_MULTI-MATERIAL_GROUP`), `*CONSTRAINED_LAGRANGE_IN_SOLID`
  — Arbitrary Lagrangian-Eulerian for large deformation / FSI.

## SPH & particle methods

- `*SECTION_SPH`, `*ELEMENT_SPH` — smoothed-particle hydrodynamics.
- `*DEFINE_SPH_*`; discrete elements via `*ELEMENT_DISCRETE_SPHERE` / `*DES_*`.

## EOS (equation of state)

- `*EOS_*` (e.g. `*EOS_LINEAR_POLYNOMIAL`, `*EOS_JWL`, `*EOS_GRUNEISEN`) —
  pressure-volume behavior for high-rate/fluid materials; paired with a `*MAT_*`.

## Electromagnetics (EM)

- `*EM_*` (e.g. `*EM_CONTROL`, `*EM_MAT_*`, `*EM_SOLVER_*`) — resistive/inductive
  heating, forming, magnetics.

## Incompressible CFD (ICFD)

- `*ICFD_*` (e.g. `*ICFD_CONTROL_*`, `*ICFD_BOUNDARY_*`, `*ICFD_SECTION`) —
  incompressible flow solver, coupling to structure.

## Thermal

- `*CONTROL_THERMAL_*`, `*MAT_THERMAL_*`, `*BOUNDARY_TEMPERATURE_*`,
  `*BOUNDARY_FLUX_*`, `*BOUNDARY_CONVECTION_*` — thermal / coupled thermal-mech.

## Isogeometric (IGA)

- `*IGA_*` — isogeometric analysis (NURBS-based).

## Finding the right card

```
search_ansys_docs("*ALE_MULTI-MATERIAL_GROUP", scope="all")
search_ansys_docs("*EOS_JWL", scope="all")
search_ansys_docs("*EM_CONTROL", scope="all")
search_ansys_docs("*ICFD_CONTROL", scope="all")
```

## Notes

- These solvers add their own `*CONTROL_<SOLVER>` cards on top of the base deck.
- Coupled runs (EM/ICFD/thermal ↔ structure) need matching control + coupling
  cards — verify the coupling keyword in the relevant guide.
