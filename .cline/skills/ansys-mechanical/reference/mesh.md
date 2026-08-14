# Mesh — condensed API

Curated subset of the mesh scripting API. For controls not listed, search
`Ansys_Scripting_in_Mechanical_Guide` / `Mechanical_Object_Reference` (object
"Mesh" and its control objects).

## Handle

```python
MESH = Model.Mesh
```

## Global mesh settings + generate

```python
MESH.Activate()
MESH.ElementSize = Quantity('0.5 [m]')
MESH.GenerateMesh()
```

## Mesh controls (children of Mesh)

Add a control, scope it, set its parameters. Common controls:

```python
# Edge sizing by number of divisions
SIZING = MESH.AddSizing()
SIZING.Location = EDGE_NS
SIZING.NumberOfDivisions = 2

# Method (e.g. tetrahedrons / hex dominant / sweep)
METHOD = MESH.AddAutomaticMethod()
METHOD.Location = BODY_NS
METHOD.Method = MethodType.AllTriAllTet   # see MethodType enum
```

- Sizing key properties: `.ElementSize` (Quantity) OR `.NumberOfDivisions` (int),
  `.Behavior`, `.Location`.
- After changing controls, call `MESH.GenerateMesh()` again.

## Reading mesh statistics

Mesh node/element counts are exposed on the Mesh object (e.g. `.Nodes`,
`.Elements`); the MCP `get_mesh_statistics` tool returns these.

## Key enums

- `MethodType`: meshing method options (tet, hex-dominant, sweep, multizone, ...).
- Search the object reference for the exact `MethodType` / `Behavior` members
  when you need a specific one.

## MCP tools that use this

`set_mesh_element_size` → sets `Mesh.ElementSize`;
`generate_mesh` → `Mesh.GenerateMesh()`;
`get_mesh_statistics` → node/element counts.
