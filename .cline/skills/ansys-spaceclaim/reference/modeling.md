# Modeling — condensed API

Turn sketches into 3D bodies (PyAnsys Geometry path). Verified from the
project's geometry driver.

## Extrude a sketch → prism / cylinder

```python
design = modeler.create_design("D")
sketch = Sketch()
sketch.circle(Point2D([0, 0]), radius)
body = design.extrude_sketch(name="Cylinder", sketch=sketch, distance=height)
```

`extrude_sketch(name, sketch, distance)` — extrude the closed profile by
`distance` (meters) along the plane normal.

## Standard primitive patterns (as the MCP tools build them)

```python
# Block: box profile extruded
sketch.box(Point2D([0, 0]), length, width)
design.extrude_sketch(name="Block", sketch=sketch, distance=height)

# Cylinder: circle profile extruded
sketch.circle(Point2D([0, 0]), radius)
design.extrude_sketch(name="Cylinder", sketch=sketch, distance=height)

# Sphere: semicircle revolved 360° about an axis
sketch.arc(Point2D([0, radius]), Point2D([0, 0]), Point2D([0, 2*radius]))
design.revolve_sketch(name="Sphere", sketch=sketch, axis="Y", angle=360)
```

## Revolve a sketch → solid of revolution

```python
body = design.revolve_sketch(name="Rev", sketch=sketch, axis="Y", angle=360)
```

`revolve_sketch(name, sketch, axis, angle)` — revolve the profile `angle`
degrees about `axis` (e.g. `"Y"`). Use `angle < 360` for a partial body.

## Boolean / transform operations

Boolean (unite/subtract/intersect) and transforms (translate/scale/mirror) are
part of the modeling API but are not wired into dedicated MCP tools. For their
exact method names, search `SpaceClaim_Documentation` or use
`execute_spaceclaim_script_live` with native SpaceClaim calls.

## MCP tools that use this

`geometry_create_block` (box → extrude), `geometry_create_cylinder`
(circle → extrude), `geometry_create_sphere` (arc → revolve).
