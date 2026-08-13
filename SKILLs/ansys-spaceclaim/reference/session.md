# Session & Connect — condensed API

How to reach a live modeler/design, and the two scripting paths. Verified from
the project's geometry driver (`ansys.geometry.core`).

## MCP tools (simplest path)

- `geometry_launch(port?, host, transport_mode, connect_timeout)` — launch or
  connect to a Geometry/SpaceClaim service. If `port` is omitted it scans
  50051-50055 for a running instance.
- `geometry_create_design(name)` — create the active design.
- `geometry_list_bodies()` — list bodies in the active design.
- `geometry_status()` / `geometry_close()` — connection status / shutdown.

## PyAnsys Geometry objects (for execute-style scripting)

```python
# modeler is the connected client; create_design returns the active Design
design = modeler.create_design("MyDesign")
```

- The active `Design` is the root you add sketches/bodies to.
- Bodies are created by extruding/revolving sketches (see `modeling.md`).

## Native SpaceClaim Python path

`execute_spaceclaim_script_live(script, system_name="", timeout_seconds=120)`
sends a **SpaceClaim Python** script to the live SpaceClaim window through the
Workbench bridge. This is the SpaceClaim recorded-script API (different from
PyAnsys Geometry). For its exact calls, search `SpaceClaim_Documentation`:

```
search_ansys_docs("<operation>", scope="all")   # e.g. "component", "named selection"
```

## MCP tools that use this

`geometry_launch`, `geometry_create_design`, `geometry_status`,
`geometry_close`, `geometry_list_bodies`, `execute_spaceclaim_script_live`.
