---
name: ansys-mechanical
description: Condensed Ansys Mechanical scripting (ACT) API, organized by function (ACT foundation, geometry/selections, mesh, materials, connections, loads, construction geometry, mesh data, results, LS-DYNA-via-Mechanical). Use whenever the user writes or debugs a Mechanical script or ACT extension through the ANSYS MCP (run_mechanical_script / execute_mechanical_script_live) or its convenience tools (add_force, add_fixed_support, generate_mesh, ...), builds a structural/modal/acoustic/explicit or LS-DYNA analysis inside Mechanical, works with ExtAPI/DataModel/GeoData/SelectionManager/mesh controls/remote points/construction geometry, or asks how a Mechanical Python API (AddFixedSupport, AddContactRegion, AddRemotePoint, GenerateMesh, CreateLoadObject, WriteInputFile, Solve) works. Load the matching reference/<function>.md before generating code so object and property names are exact.
keywords: mechanical, ACT, extension, onupdateStep, ExtAPI, DataModel, GeoData, SelectionManager, Model, Analysis, AddNamedSelection, GenerationCriteria, GenerateMesh, AddSizing, AddWasher, AddContactRegion, AddRemotePoint, AddJoint, AddConstructionGeometry, FreezeMeshOnSelectedParts, MeshData, ElementTypeEnum, CreateLoadObject, TimeStepCalc, WriteInputFile, AddFixedSupport, AddTotalDeformation, Solve, LSDYNA, object reference
---

# Ansys Mechanical Scripting API (condensed, by function)

This skill gives you the Mechanical ACT scripting API condensed by function, so
you can generate correct scripts without reading the multi-MB guides. The
`reference/` folder holds one file per functional area — open only the one(s)
you need.

## Core entry points (always available in a Mechanical script)

```python
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS
Model      = DataModel.Project.Model      # also exposed directly as `Model`
MESH       = Model.Mesh
CONNECTIONS = Model.Connections
ANALYSIS   = Model.Analyses[0]            # e.g. Static Structural / Modal
SETTINGS   = ANALYSIS.Children[0]         # Analysis Settings
SOLUTION   = ANALYSIS.Solution
```

- Values with units use `Quantity('0.5 [m]')`, `Quantity('50000 [Hz]')`.
- Objects are created with `parent.Add<Thing>()` and scoped with `.Location`.
- Selection is done via named selections or `ExtAPI.SelectionManager`.

## Which reference file to open

| Function | File | Covers |
|---|---|---|
| ACT foundation (start here for extensions) | `reference/act_scripting_foundation.md` | ExtAPI/DataModel/Model, GeoData + Geo*Wrapper, SelectionManager, Tree, ObjectState, Transaction, Quantity, `onupdateStep(step)`, logging |
| Geometry & selections | `reference/geometry_and_selections.md` | Bodies/parts, suppress, coordinate systems, symmetry, named selections + worksheet criteria (incl. diagnostics/mesh-interference) |
| Mesh (basics) | `reference/mesh.md` | Global mesh, sizing, `GenerateMesh()` |
| Mesh controls (advanced) | `reference/mesh_controls_advanced.md` | Method/FaceMeshing/Washer, MultiZone/Prime/Sweep, InternalObject targets, freeze, grouping |
| Materials | `reference/materials.md` | Assign materials to bodies, material assignment objects |
| Connections & contacts | `reference/connections_and_contacts.md` | Contact regions, bonded, joints, remote points, promote |
| Boundary conditions & loads | `reference/boundary_conditions_and_loads.md` | Supports, pressure, force, displacement, gravity, remote BCs |
| Construction geometry | `reference/construction_geometry.md` | In-Mechanical solids, coordinate-system rotate/transform, rigid stiffness |
| Analysis setup & solve | `reference/analysis_setup.md` | Analysis handle, analysis settings (steps/modal/solver), `Solve()` |
| Mesh data & elements | `reference/meshdata_and_elements.md` | MeshData, nodes/elements, connectivity, ElementTypeEnum, body mass |
| Results & post-processing | `reference/results_and_postprocessing.md` | Add result objects, read min/max/frequency values |
| LS-DYNA via Mechanical | `reference/lsdyna_via_mechanical.md` | `CreateLoadObject`/`CreateObject("...","LSDYNA")`, solver Properties, `WriteInputFile(.k)`, drop/gravity/velocity |

For writing an **ACT extension**, start with `act_scripting_foundation.md` (the
shared data-model/selection/transaction layer), then open the functional file(s)
for the task. Anything not in these files — use the doc search (below). These
reference files are a curated subset of the most-used dispatch API, not the whole
object model.

## Fallback: search the full docs

The full API is indexed. When a name isn't in the reference files:

- `search_ansys_docs(query, scope="api")` — searches `Ansys_Scripting_in_Mechanical_Guide`
  (api_scripting) and `Mechanical_Object_Reference` (api_reference) first.
- `get_ansys_doc_chunk(doc, chunk_id, context=1)` — pull the full chunk.
- Use single, exact API tokens (e.g. `AddContactRegion`) — the index is a
  keyword/substring search, so multi-word natural-language queries often miss.
- For ACT-specific classes/enums not in the indexed docs, the authoritative
  source is the ACT API Reference / ACT Customization Guide for Mechanical (not
  in the MCP index; available under `ACT_Test/3.documents/md`).

## Relation to the ANSYS MCP convenience tools

Many MCP tools wrap this API directly, so the reference files also explain what
those tools do under the hood: `add_fixed_support`→`AddFixedSupport`,
`add_force`→`AddForce`, `add_pressure`→`AddPressure`,
`generate_mesh`→`Mesh.GenerateMesh`, `add_total_deformation`→`AddTotalDeformation`,
`solve_analysis`→`Analysis.Solve`. Prefer the MCP tools for common actions; drop
to `run_mechanical_script` for anything they don't cover.
