# Native SpaceClaim Scripting — Sketch & Geometry

Sketching primitives and the geometry/shape objects you query. Tokens verified
from real ACT extensions (BGA ball builder etc.). See
`native_session_and_versions.md` for imports and the `MM()`/`DEG()` helpers.

## Sketch workflow

```python
ViewHelper.SetSketchPlane(Plane.PlaneZX)                # enter sketch on a plane
p1 = Point2D.Create(MM(0),  MM(0))
p2 = Point2D.Create(MM(0),  MM(0.25))
p3 = Point2D.Create(MM(0.5),MM(0.25))
SketchRectangle.Create(p1, p2, p3)
SketchArc.Create3PointArc(a1, a2, a3)                   # start, end, mid-ish (3 points)
SketchLine.Create(p1, p2)
result = ViewHelper.SetViewMode(InteractionMode.Solid)  # solidify sketch -> result.CreatedBodies
```

## Points, directions, vectors, lines, planes

```python
Point.Create(MM(x), MM(y), MM(z))       # 3D point
Point2D.Create(MM(u), MM(v))            # sketch point
Direction.DirX; Direction.DirY; Direction.DirZ
axis = Line.Create(Point.Create(MM(0),MM(0),MM(0)), Direction.DirZ)   # for revolve/rotate
Plane.PlaneZX                            # standard planes (PlaneXY/PlaneYZ/PlaneZX)
Matrix.Identity                          # e.g. for GetBoundingBox

v = Vector.Create(dx, dy, dz)
Vector.Dot(v1, v2); Vector.Cross(v1, v2)
v.UnitVector; v.Magnitude
# Direction arithmetic is overloaded (used for array pitch vectors):
direction = Direction.DirX*pitch1*(i) + Direction.DirY*pitch2*(j)
```

## Shape & geometry queries

```python
box = obj.Shape.GetBoundingBox(Matrix.Identity)
box.MinCorner.X, box.MinCorner.Y, box.MinCorner.Z
box.MaxCorner.X, box.MaxCorner.Y, box.MaxCorner.Z

face.Shape.Area
edge.Shape.Length
edge.Shape.StartPoint; edge.Shape.EndPoint
edge.EvalMid().Point                      # midpoint of an edge
geom = face.Shape.Geometry                # underlying geometry
geom.Radius; geom.MinorRadius; geom.Axis  # for Cylinder/Torus/Circle
body.Shape.Volume                          # 0 => sheet body
```

## Geometry types (for classifying faces/edges)

Under `SpaceClaim.Api.V<ver>.Geometry` (or `sc.Geometry`):

- Surfaces: `Plane`, `Cylinder`, `Cone`, `Torus`, `NurbsSurface`, `ProceduralSurface`
- Curves: `Line`, `Circle`, `NurbsCurve`, `ProceduralCurve`

```python
if face.Shape.Geometry.GetType() == sc.Geometry.Cylinder:
    r = face.Shape.Geometry.Radius
```

## Design objects

```python
body.Faces; body.Edges; body.Name; body.IsDeleted
body.GetMaster().Parent            # owning part/component
edge.Parent                        # owning body
edge.Faces                         # faces touching an edge (Count==1 => free edge)
```

## Key enums

- `InteractionMode`: `Solid` (solidify sketch)
- Standard planes: `Plane.PlaneXY`, `Plane.PlaneYZ`, `Plane.PlaneZX`
- `Direction`: `DirX`, `DirY`, `DirZ`

## Notes

- Sketch, then `SetViewMode(InteractionMode.Solid)` to turn the profile into a
  body; the result's `CreatedBodies[0]` is the new solid.
- `body.Shape.Volume == 0` distinguishes sheet (surface) bodies from solids.
- Wrap literals in `MM()`/`DEG()` — the API works in SI internally.
