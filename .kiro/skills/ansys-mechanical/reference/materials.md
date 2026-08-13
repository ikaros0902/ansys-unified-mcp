# Materials — condensed API

Curated subset of material assignment scripting. Materials themselves come from
Engineering Data (defined in Workbench); in Mechanical you mostly **assign** an
existing material to bodies. For anything not here, search
`Ansys_Scripting_in_Mechanical_Guide` / `Mechanical_Object_Reference`.

## Simplest path: MCP tools

- `list_materials` — list materials available in Engineering Data.
- `assign_material(body_name, material_name)` — assign a material to a body.

Prefer these for common cases; drop to scripting below for bulk/conditional
assignment.

## Read a body's material

```python
bodies = Model.Geometry.GetChildren(DataModelObjectCategory.Body, True)
for body in bodies:
    name = body.Material        # assigned material name (string)
    body.Material = "Structural Steel"   # assign by name
```

## Material assignment objects (bulk / scripted)

Assignments live under the Materials folder as `MaterialAssignment` objects:

```python
matFolder = ExtAPI.DataModel.GetObjectsByType(
    Ansys.ACT.Automation.Mechanical.Materials)[0]

for ch in matFolder.Children:
    if ch.GetType() == Ansys.ACT.Automation.Mechanical.MaterialAssignment:
        ch.Material    # material name
        ch.Location    # scoped geometry selection
```

Scope an assignment to bodies via the SelectionManager:

```python
sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
sel.Ids = [b.GetGeoBody().Id for b in bodies]      # geo body ids
ExtAPI.SelectionManager.NewSelection(sel)
assignment.Location = sel
```

## Key types

- `Ansys.ACT.Automation.Mechanical.Materials` — the materials folder object.
- `Ansys.ACT.Automation.Mechanical.MaterialAssignment` — one assignment.
- `SelectionTypeEnum.GeometryEntities` — selection info type for geo scoping.

## MCP tools that use this

`list_materials`, `assign_material`.
