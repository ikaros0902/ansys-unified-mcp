# Design & Bodies — condensed API

The design tree, bodies, and components (PyAnsys Geometry path).

## Design

```python
design = modeler.create_design("MyDesign")   # active root Design
```

The `Design` is the root container. Sketches are extruded/revolved into bodies
that live under the design (or under components within it).

## Bodies

- `design.extrude_sketch(...)` / `design.revolve_sketch(...)` return a body.
- List bodies via the MCP `geometry_list_bodies()` tool.
- A body carries a name (set via the `name=` argument at creation).

## Components & named selections

Components (assembly nodes) and named selections are part of the design tree.
Their exact API (adding a component, grouping faces/bodies into a named
selection) is not wired into dedicated MCP tools — search the docs for the
exact method name, or use `execute_spaceclaim_script_live`:

```
search_ansys_docs("named selection", scope="all")
search_ansys_docs("component", scope="all")
```

Named selections created in geometry carry through to Mechanical scoping, so
name them meaningfully (they become the `Location` targets in the
`ansys-mechanical` loads/BC API).

## MCP tools that use this

`geometry_create_design`, `geometry_list_bodies`.
