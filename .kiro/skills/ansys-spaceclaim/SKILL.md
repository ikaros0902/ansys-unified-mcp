---
name: ansys-spaceclaim
description: Condensed Ansys geometry API for the ANSYS MCP, covering two families — PyAnsys Geometry (ansys.geometry.core, via the geometry_* tools) and native SpaceClaim scripting (SpaceClaim.Api.V<ver>, via execute_spaceclaim_script_live and SpaceClaim ACT wizards). Use whenever the user creates or edits geometry, writes a SpaceClaim ACT extension (midsurface, defeature, share topology, BGA/array build), prepares/repairs CAD for simulation, or asks how Sketch/extrude/revolve, Selection, Midsurface, RevolveFaces, ForceShare, or ComponentHelper work. Load the matching reference/<function>.md before generating geometry code.
keywords: spaceclaim, discovery, geometry, ACT, PyAnsys Geometry, ansys.geometry.core, SpaceClaim.Api, Sketch, extrude_sketch, revolve_sketch, Selection, Midsurface, Fill, RevolveFaces, ExtrudeFaces, SplitBody, ForceShare, ShareTopologyNamedSelection, FixImprint, ComponentHelper, DocumentHelper, PowerSelection, SketchRectangle, Point2D, midsurface, defeature, share topology, CAD, STEP, IGES
---

# Ansys Geometry / SpaceClaim API (condensed, by function)

This project drives geometry through **two different API families**. Pick the
one that matches how you're running:

1. **PyAnsys Geometry** (`ansys.geometry.core`) — used by the MCP `geometry_*`
   tools. Geometry is built with `Sketch` + `extrude_sketch`/`revolve_sketch`.
   Files: `session.md`, `sketching.md`, `modeling.md`, `design_and_bodies.md`,
   `import_export.md`.
2. **Native SpaceClaim scripting** (`SpaceClaim.Api.V<ver>`) — used by
   `execute_spaceclaim_script_live` and by SpaceClaim ACT wizards (recorded-script
   API: `Selection`, `Midsurface`, `RevolveFaces`, `ForceShare`, `ComponentHelper`,
   ...). Files: the `native_*.md` set below. This is what ACT SpaceClaim
   extensions use.

They are NOT interchangeable — `ansys.geometry.core` classes do not exist in a
native SpaceClaim script and vice versa.

## Core entry points (PyAnsys Geometry path)

```python
from ansys.geometry.core.sketch import Sketch
from ansys.geometry.core.math import Point2D, Point3D, Plane, Vector3D

design  = modeler.create_design("MyDesign")   # active Design object
sketch  = Sketch()                             # 2D sketch on default plane
body    = design.extrude_sketch(name="B", sketch=sketch, distance=0.01)
```

- Lengths are in meters (SI). A block/cylinder is a sketch profile extruded a
  distance; a sphere is a semicircle revolved 360°.

## Which reference file to open

**PyAnsys Geometry path** (MCP `geometry_*` tools):

| Function | File | Covers |
|---|---|---|
| Session & connect | `reference/session.md` | Launch/connect modeler, create design, list bodies |
| Sketching | `reference/sketching.md` | `Sketch`, planes, `circle`/`box`/`arc`/`segment` |
| Modeling | `reference/modeling.md` | `extrude_sketch`, `revolve_sketch`, block/cylinder/sphere patterns |
| Design & bodies | `reference/design_and_bodies.md` | Design tree, bodies, components, named selections |
| Import / export | `reference/import_export.md` | Import CAD, export STEP/IGES |

**Native SpaceClaim scripting path** (`execute_spaceclaim_script_live` / ACT wizards):

| Function | File | Covers |
|---|---|---|
| Session & versions | `reference/native_session_and_versions.md` | `SpaceClaim.Api.V<ver>` load + auto-detect, `clr.ImportExtensions`, units, `onupdateStep` |
| Selection | `reference/native_selection.md` | `Selection` create/convert/filter/group, `PowerSelection` |
| Commands | `reference/native_commands.md` | `Midsurface`/`Fill`/`Loft`/`RevolveFaces`/`ExtrudeFaces`/`SplitBody`/`Move`/`ForceShare`/`ShareTopologyNamedSelection`/`FixImprint` |
| Sketch & geometry | `reference/native_sketch_and_geometry.md` | `SketchRectangle`/`SketchArc`/`Point2D`, `Vector`/`Direction`/`Plane`, shape/geometry queries |
| Helpers, view, transactions | `reference/native_helpers_and_transaction.md` | `DocumentHelper`/`MeasureHelper`/`ViewHelper`, undo/redo, `TransactionHelper`/`WriteBlock`/`Task` |

Anything not in these files — search the docs (below). Reference files are a
curated subset of the most-used dispatch API.

## Fallback: search the full docs

- `search_ansys_docs(query, scope="all")` — `SpaceClaim_Documentation` is indexed
  as a guide (product `spaceclaim`); search all scopes.
- `get_ansys_doc_chunk(doc, chunk_id, context=1)` — pull the full chunk.
- Use single, exact tokens; multi-word natural-language queries often miss.

## MCP tools (dispatch surface)

`geometry_launch`, `geometry_create_design`, `geometry_create_block`,
`geometry_create_cylinder`, `geometry_create_sphere`, `geometry_export`,
`geometry_import_file`, `geometry_list_bodies`, `geometry_status`,
`geometry_close`, and `execute_spaceclaim_script_live` (native SpaceClaim Python).
