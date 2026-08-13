# Model Build — condensed reference

Creating and editing mesh/model from a script. Behaviors verified from the
`lsppscripting` examples; get exact command tokens from the doc.

## What scripting can build (from doc examples)

- Create a plate and mesh it with shell elements.
- Drag shell elements in a direction (e.g. +Z) to form a solid block.
- Delete a part (e.g. remove the shell part, keep the solid part).
- Write a part out to a file.
- Create a load curve from an equation + parameters, write it to a file, and
  load it back for display in the XY-plot interface.

## Pattern

```
example.cfile
  ── define input/output files + params
  ── runpython build_model.py  in.k  out.k  nx  ny
                     │ create nodes/elements
                     │ mesh / drag / delete
                     ▼ write part to out.k
```

## Query while building

Use the data-center getters (see `model_query.md`) to read back counts, ids, and
connectivity after building — e.g. number of nodes/elements, largest ids, node
id array, element connectivity for a given element.

## Notes

- Mesh creation, dragging, and part write use LS-PrePost command tokens; get
  their exact names from `Ansys_LS-PrePost_Users_Guide` / `lsppscripting`
  (search the specific operation, e.g. "drag", "mesh", "write part").
- For the resulting LS-DYNA keyword deck (materials, sections, contacts), see the
  `ansys-lsdyna` skill.
