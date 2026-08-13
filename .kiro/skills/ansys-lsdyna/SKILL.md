---
name: ansys-lsdyna
description: Condensed Ansys LS-DYNA keyword-deck reference, organized by keyword family (materials, elements/sections/parts, contact/constraints, loads/initial, control/output, specialized solvers). Use whenever the user builds or edits an LS-DYNA *KEYWORD input deck, chooses material/contact/element/boundary keywords, sets up implicit vs explicit runs, maps data with Envyo, launches solves with LS-Run, or migrates from Autodyn. For LS-PrePost pre/post-processing and its cfile/Python scripting, use the ansys-ls-prepost skill.
keywords: ls-dyna, lsdyna, keyword, deck, *KEYWORD, *MAT, *CONTACT, *ELEMENT, *SECTION, *PART, *BOUNDARY, *CONSTRAINED, *LOAD, *INITIAL, *CONTROL, *DATABASE, implicit, explicit, Envyo, LS-Run, Autodyn migration
---

# Ansys LS-DYNA Keyword Deck (condensed, by family)

LS-DYNA is keyword-driven: a model is a `*KEYWORD` deck, not a Python object
tree. There is **no ANSYS MCP dispatch tool** for the LS-DYNA solver, so this
skill is a documentation reference: it maps keyword families to the local guides
and tells you what to search. The family split follows how PyDYNA groups
keywords.

## Deck basics

```
*KEYWORD
*TITLE
 my model
... keyword cards, grouped by family ...
*END
```

- Cards are fixed/comma format; each `*KEYWORD` has a documented card layout.
- Get exact card fields from the local guides via search (below) — do not guess
  field positions.

## Which reference file to open

| Family | File | Keyword prefixes |
|---|---|---|
| Materials | `reference/materials.md` | `*MAT_*` |
| Elements, sections, parts | `reference/elements_sections_parts.md` | `*ELEMENT_*`, `*SECTION_*`, `*PART`, `*NODE`, `*SET_*`, `*INTEGRATION_*` |
| Contact & constraints | `reference/contact_and_constraints.md` | `*CONTACT_*`, `*RIGIDWALL_*`, `*CONSTRAINED_*`, `*BOUNDARY_*` |
| Loads & initial conditions | `reference/loads_and_initial.md` | `*LOAD_*`, `*INITIAL_*` |
| Control & output | `reference/control_and_output.md` | `*CONTROL_*`, `*DATABASE_*`, `*INCLUDE`, `*PARAMETER`, `*DEFINE_*` |
| Specialized solvers | `reference/specialized_solvers.md` | ALE, EM, ICFD, `*EOS_*`, SPH/particle, thermal, IGA |

## Workflow & related tools

- **Build the deck**: usually in LS-PrePost — see the `ansys-ls-prepost` skill.
- **Implicit vs explicit**: `LS-DYNA_Implicit_Analysis_Guide` for implicit setup.
- **Map data between meshes**: `Envyo_Users_Guide`.
- **Launch solves**: `LS-Run_Users_Guide`.
- **From Autodyn**: `Explicit_Dynamics_Autodyn_to_LS-DYNA_Migration_Guide`.

## Fallback: search the full docs

- `search_ansys_docs(query, scope="all")` — LS-DYNA docs are guides (product
  `lsdyna`); search all scopes.
- Use single, exact tokens including the leading `*` where relevant (e.g.
  `*MAT_PIECEWISE_LINEAR_PLASTICITY`, `*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE`).
- Note: `LS-DYNA_Keyword_and_Theory_Manuals.md` is effectively empty and not
  indexed — rely on `LS-DYNA_Users_Guide` and the analysis guides instead.

## MCP tools

None for the LS-DYNA solver. For Python deck building outside this repo, PyDYNA
(`ansys.dyna.core`) exists but is not wired into this MCP.
