# Elements, Sections & Parts — condensed reference

The mesh and its bookkeeping: nodes, elements, the section (formulation +
thickness/integration) and the part (ties section + material). Card fields come
from `LS-DYNA_Users_Guide` — search for the exact keyword.

## The PART triangle

```
*PART            -> PID references SECID (*SECTION) + MID (*MAT)
*SECTION_<type>  -> element formulation, thickness, integration
*MAT_<model>     -> material constants (see materials.md)
```

A `*PART` is the assembly unit: it binds one section and one material to a group
of elements.

## Keyword prefixes

- Nodes: `*NODE` (node id + coordinates), `*NODE_*` variants.
- Elements: `*ELEMENT_SOLID`, `*ELEMENT_SHELL`, `*ELEMENT_BEAM`,
  `*ELEMENT_DISCRETE`, `*ELEMENT_MASS`, `*ELEMENT_SEATBELT`.
- Sections: `*SECTION_SOLID`, `*SECTION_SHELL`, `*SECTION_BEAM`,
  `*SECTION_DISCRETE` — set element formulation (ELFORM), thickness, etc.
- Integration: `*INTEGRATION_SHELL`, `*INTEGRATION_BEAM` — custom through-thickness
  integration rules.
- Grouping: `*SET_NODE`, `*SET_SOLID`, `*SET_SHELL`, `*SET_PART`,
  `*SET_SEGMENT` — id lists that loads/contacts/BCs reference.

## Sets are the scoping mechanism

Most loads, contacts, and boundary conditions scope to a `*SET_*` (analogous to
a named selection). Define the set once, reference its SID everywhere.

## Finding the right card

```
search_ansys_docs("*SECTION_SHELL", scope="all")
search_ansys_docs("*ELEMENT_SOLID", scope="all")
search_ansys_docs("*SET_SEGMENT", scope="all")
```

## Notes

- ELFORM (element formulation) on `*SECTION_*` is the key performance/accuracy
  knob — verify the recommended value for your analysis in the guide.
- Segment sets (`*SET_SEGMENT`) are used for pressure loads and contact surfaces.
