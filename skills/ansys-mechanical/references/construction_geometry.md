# Construction Geometry & Coordinate Transforms — condensed API

Create in-Mechanical solids (e.g. a drop-test ground plate) and place them with
coordinate systems. Tokens verified from the Drop Test ACT extension. For
selections/named-selections see `geometry_and_selections.md`.

## Construction geometry + solid box

```python
construction = Model.AddConstructionGeometry()
construction.Name = "Scr_Ground_Construction"

solid = construction.AddSolid()
solid.Name = "Scr_ground"
solid.CoordinateSystem = cs                 # place on a coordinate system
solid.X1 = Quantity( size/2, "mm"); solid.X2 = Quantity(-size/2, "mm")
solid.Y1 = Quantity(  0.0,   "mm"); solid.Y2 = Quantity(-thk,    "mm")
solid.Z1 = Quantity( size/2, "mm"); solid.Z2 = Quantity(-size/2, "mm")
solid.AddGeometry()                          # realize the solid
construction.UpdateSolids()                  # (also UpdateAllSolids())
```

Reposition/rebuild an existing solid:

```python
solid.CoordinateSystem = new_cs
solid.X1 = Quantity(...); ...                # update extents
solid.DeleteGeometry(); solid.AddGeometry()  # recreate to force position update
construction.UpdateSolids()
ExtAPI.DataModel.Tree.Refresh()
```

## Stiffness behavior (make it rigid)

```python
# find the tree body under Model.Geometry, then:
ground_body.StiffnessBehavior = StiffnessBehavior.Rigid
```

## Coordinate systems (create, place, rotate)

```python
cs = Model.CoordinateSystems.AddCoordinateSystem()
cs.Name = "Collision Point"
cs.CoordinateSystemType = CoordinateSystemType.Cartesian
cs.OriginDefineBy = CoordinateSystemAlignmentType.Fixed
cs.OriginX = Quantity("0 [mm]"); cs.OriginY = Quantity("-0.1 [mm]"); cs.OriginZ = Quantity("0 [mm]")

# rotate in 90-degree steps (called repeatedly for multiples)
cs.RotateX(90); cs.RotateY(90); cs.RotateZ(90)
```

- To drive a CS by transformations instead of fixed origin, set an alignment
  property (`DefineBy` / `OrientationDefineBy`) to
  `CoordinateSystemAlignmentType.Transformations` and use `AddTransformation` /
  `SetTransformationValue` (see `geometry_and_selections.md`).

## Key enums

- `StiffnessBehavior`: `Rigid`, `Flexible`
- `CoordinateSystemType`: `Cartesian`, `Cylindrical`
- `CoordinateSystemAlignmentType`: `Fixed`, `Transformations`

## Notes

- After creating construction geometry, the new body appears under
  `Model.Geometry`; find it by `Name` to set material / stiffness / mesh.
- Recreating geometry (`DeleteGeometry`+`AddGeometry`) is the robust way to force
  a position update when only moving the coordinate system doesn't refresh.
