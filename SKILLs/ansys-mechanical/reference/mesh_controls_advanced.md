# Mesh Controls (advanced) — condensed API

The full mesh-control surface used by real ACT meshing tools, beyond the basics
in `mesh.md`. Tokens verified from ACT extensions (AutoMesh / MeshTuner /
GoToMeshControls). Handle: `MesherObj = Model.Mesh`.

## Add controls

```python
sizing = MesherObj.AddSizing()
method = MesherObj.AddAutomaticMethod()
fmesh  = MesherObj.AddFaceMeshing()
washer = MesherObj.AddWasher()
```

Scope each with `.Location = sel` (a `CreateSelectionInfo(GeometryEntities)` with
`.Ids`), see `act_scripting_foundation.md`.

## Sizing

```python
sizing.Location    = sel
sizing.Type        = SizingType.ElementSize        # or SizingType.NumberOfDivisions
sizing.ElementSize = Quantity(2.0, "mm")            # when ElementSize
sizing.NumberOfDivisions = 4                        # when NumberOfDivisions
sizing.Behavior    = SizingBehavior.Hard            # Hard vs (soft default)
sizing.DefeatureSize = Quantity(0.2, "mm")
sizing.CaptureCurvature = False
sizing.GrowthRate  = 1.2
```

## Method (mesh method)

```python
method.Location = sel
method.Method   = MethodType.Sweep        # Sweep | QuadTri | Automatic | MultiZone | Prime | AllTriAllTet
# Sweep specifics
method.SourceTargetSelection = 4          # or 0 (program controlled)
method.SourceLocation        = face_sel
method.FreeFaceMeshType      = 2
method.SweepNumberDivisions  = n
# MultiZone / surface
method.SurfaceMeshMethod   = 1
method.PreserveBoundaries  = 0
method.MeshBasedDefeaturing = True
method.DefeaturingTolerance = method.MinimumEdgeLength
```

`MethodType.AllTriAllTet` is the reliable tetra fallback when Hex/Sweep/MultiZone
fails (check `body.ObjectState == ObjectState.Meshed` after generating).

## Face meshing & washer

```python
fmesh.Location = face_sel
fmesh.Method   = FaceMeshingMethod.Quadrilaterals

washer.Location = edge_sel
washer.NumberOfWasherLayers = 1
```

## Global mesh targets (InternalObject)

```python
MI = MesherObj.InternalObject
MI.GlobalTargetJacobianRatio = 0.65
MI.GlobalTargetMinLength     = 0.5
MI.GlobalTargetSkewness      = 45
MI.ForceUpdateMeshStates()          # refresh mesh state flags
```

## Generate / clear / batch connection

```python
MesherObj.Activate()
MesherObj.ElementSize = Quantity(2.0, "mm")   # global size
MesherObj.GenerateMesh()
MesherObj.ClearGeneratedData()                 # wipe mesh (destroys ALL mesh)
MesherObj.Update()
Model.Mesh.MeshBasedConnection                 # bool: mesh-based (batch) connection
```

## Freeze / unfreeze mesh (protect mesh during edits)

```python
geo_parts = [DataModel.GeoData.GeoPartById(pid) for pid in part_ids]
Model.FreezeMeshOnSelectedParts(geo_parts)
# ... edits that would otherwise remesh ...
Model.UnfreezeMeshOnSelectedParts(geo_parts)
```

## Grouping / tidy the tree

```python
MesherObj.GroupAllSimilarChildren()                     # group similar controls
iMC.Ungroup()                                            # ungroup a folder
folder = Model.InternalObject.AddTreeGroupingFolder(MesherObj.ObjectId)
folder.Name = "Scr_XXX"
control.RenameBasedOnDefinition()                        # auto-name a control
```

## Key enums

- `SizingType`: `ElementSize`, `NumberOfDivisions`
- `SizingBehavior`: `Hard` (soft is the default)
- `MethodType`: `Sweep`, `QuadTri`, `Automatic`, `MultiZone`, `Prime`, `AllTriAllTet`
- `FaceMeshingMethod`: `Quadrilaterals`
- Control types (for `IsMeshApplied`/filtering): `Ansys.ACT.Automation.Mechanical.MeshControls.Sizing`,
  `.FaceMeshing`, `.AutomaticMethod`, `.Washer`; folders are
  `Ansys.ACT.Automation.Mechanical.TreeGroupingFolder`.

## MCP tools that use this

`set_mesh_element_size`, `generate_mesh`, `get_mesh_statistics`.
