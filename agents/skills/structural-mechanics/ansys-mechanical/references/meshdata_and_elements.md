# Mesh Data & Elements — condensed API

Query the generated mesh: nodes, elements, connectivity, element types, and
per-body mass. Tokens verified from Interference-Check / Section-Mass ACT tools.

## Get the mesh data object

```python
mesh = model.MeshData                                   # whole-model mesh
mesh = DataModel.MeshDataByName(DataModel.MeshDataNames[0])
# fallback: model.Analyses[0].MeshData
region = mesh.MeshRegionById(geo_body.Id)               # mesh of one body
```

## Nodes & elements

```python
mesh.NodeIds; mesh.ElementIds                 # id lists
nd = mesh.NodeById(nid);  nd.X, nd.Y, nd.Z     # node coords (SI, meters)
el = mesh.ElementById(eid)
el.NodeIds                                     # element connectivity
el.GetBody()                                   # owning body (has .Id)
el.Type                                        # ElementTypeEnum member

region.Elements; region.ElementIds; region.NodeIds   # per-body
```

## Element types

```python
element.Type == ElementTypeEnum.kQuad4
```

- Shells: `kTri3`, `kQuad4` (linear); `kTri6`, `kQuad8` (quadratic)
- Solids: `kTet4`, `kHex8` (linear); `kTet10`, `kHex20` (quadratic)

Use these to detect linear vs quadratic, or tetra vs hex dominance (count per
body) — e.g. to choose an LS-DYNA section formulation
(see `lsdyna_via_mechanical.md`).

## Per-body queries

```python
body.Elements          # element count on a tree Body (0 => unmeshed)
body.Mass              # body mass as a Quantity (str -> "value unit")
body.GetBoundingBox()  # geo body bounding box
```

## Notes

- Node coordinates are in solver SI (meters); multiply by 1000 for mm.
- `body.Elements == 0` is the standard "not yet meshed" check before querying.
- For large models, build a spatial index (e.g. KD-tree) over element centroids
  in-script rather than O(n^2) scans.
