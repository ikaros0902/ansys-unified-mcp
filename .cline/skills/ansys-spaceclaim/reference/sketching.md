# Sketching — condensed API

2D sketch primitives for the PyAnsys Geometry path. Verified from the project's
geometry driver. A sketch is drawn on a plane, then extruded/revolved into a
body (see `modeling.md`).

## Imports & handle

```python
from ansys.geometry.core.sketch import Sketch
from ansys.geometry.core.math import Point2D, Point3D, Plane, Vector3D

sketch = Sketch()                                  # default plane (origin)
sketch.plane = Plane(Point3D([cx, cy, cz]))        # move the sketch plane
```

## Primitives

```python
sketch.circle(Point2D([0, 0]), radius)             # circle at center, radius (m)
sketch.box(Point2D([0, 0]), length, width)         # rectangle centered at point
sketch.arc(Point2D([0, r]), Point2D([0, 0]), Point2D([0, 2*r]))  # center, start, end
```

- Coordinates are `Point2D([x, y])` in the sketch plane; lengths in meters.
- `sketch.box(center, length, width)` draws a rectangle centered on `center`.
- `sketch.arc(center, start, end)` — used e.g. for a semicircle profile to revolve.

## Other primitives

Sketches also support segments/lines and parametric profiles. For the full
sketch API (segment, polygon, ellipse, ...), search `SpaceClaim_Documentation`
or the PyAnsys Geometry sketch reference by exact method name.

## Notes

- Build the full closed profile before extruding/revolving.
- To place a profile off-origin, set `sketch.plane` rather than offsetting every
  point.
