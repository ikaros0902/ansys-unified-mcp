# Contact & Constraints — condensed reference

Interaction (`*CONTACT_*`, `*RIGIDWALL_*`) and kinematic ties / supports
(`*CONSTRAINED_*`, `*BOUNDARY_*`). Card fields come from `LS-DYNA_Users_Guide`.

## Contact (`*CONTACT_*`)

```
*CONTACT_<type>   -> defines an interaction between segment/part sets
```

Common types:

- `*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE` — general two-surface contact.
- `*CONTACT_AUTOMATIC_SINGLE_SURFACE` — self / all-inclusive contact.
- `*CONTACT_AUTOMATIC_NODES_TO_SURFACE` — node group against a surface.
- `*CONTACT_TIED_*` — tied (bonded) contact, incl. `_TIED_SURFACE_TO_SURFACE`.
- `*CONTACT_ERODING_*` — for eroding (failing) elements.

Scope via segment/part sets; key params: friction (FS/FD), soft constraint
(SOFT), offsets — verify on the card.

## Rigid walls (`*RIGIDWALL_*`)

- `*RIGIDWALL_PLANAR`, `*RIGIDWALL_GEOMETRIC_*` — analytical rigid barriers.

## Constraints (`*CONSTRAINED_*`)

- `*CONSTRAINED_NODAL_RIGID_BODY` — tie nodes into a rigid body.
- `*CONSTRAINED_SPOTWELD`, `*CONSTRAINED_RIGID_BODIES`,
  `*CONSTRAINED_JOINT_*` (revolute, spherical, ...),
  `*CONSTRAINED_TIED_NODES_FAILURE`, `*CONSTRAINED_EXTRA_NODES`.

## Boundary conditions (`*BOUNDARY_*`)

- `*BOUNDARY_SPC_*` — single-point constraints (fix DOFs) on nodes/sets.
- `*BOUNDARY_PRESCRIBED_MOTION_*` — impose displacement/velocity/acceleration.
- `*BOUNDARY_NON_REFLECTING` — non-reflecting boundaries.
- `*BOUNDARY_PRESCRIBED_MOTION_RIGID` — drive a rigid body.

## Finding the right card

```
search_ansys_docs("*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE", scope="all")
search_ansys_docs("*BOUNDARY_SPC_SET", scope="all")
search_ansys_docs("*CONSTRAINED_NODAL_RIGID_BODY", scope="all")
```

## Notes

- Prescribed motion vs SPC: SPC fixes DOFs to zero; prescribed motion imposes a
  time history (via `*DEFINE_CURVE`, see `loads_and_initial.md`).
- Implicit runs are sensitive to over-constraint — check the implicit guide.
