# Native SpaceClaim Scripting — Helpers, View & Transactions

Document/measure/geometry helpers, view control, status/messaging, and the
transaction/task pattern for long scripts. Tokens verified from real ACT
extensions. See `native_session_and_versions.md` for imports.

## Document & component helpers

```python
root = DocumentHelper.GetRootPart()          # root Part of the active document
ComponentHelper.GetActive()                  # active component
ComponentHelper.SetRootActive(None)          # activate root
ComponentHelper.SetActive(comp, None)        # activate a component
```

## Measurement

```python
gap = MeasureHelper.DistanceBetweenObjects(FaceSelection.Create(f1), FaceSelection.Create(f2))
gap.Distance
MeasureHelper.MinDistanceBetweenObjects(sel).Distance     # sel of 2 objects
MeasureHelper.MinDistanceBetweenAxes(sel).Distance
g = Gap.Create(pt1, pt2); g.Distance; g.GapVector
GeometryHelper.CurveCurveIntersect(edge1, edge2).NumberOfIntersections
```

## Face extensions (via clr.ImportExtensions)

```python
DesignFaceExtensions.GetTangentChain(face)        # tangent-connected faces
DesignFaceExtensions.GetFaceNormal(face, 0.5, 0.5)  # normal at (u,v) -> Vector
# after ImportExtensions these also work as methods: face.GetTangentChain(), face.GetFaceNormal(u,v)
```

## View / visibility

```python
ViewHelper.SetObjectVisibility(sel, VisibilityType.Hide, False, False)   # (sel, vis, inSelectedView, faceLevel)
ViewHelper.SetObjectVisibility(sel, VisibilityType.Show, False, False)
ViewHelper.HideOthers(sel)
ViewHelper.SetSketchPlane(Plane.PlaneZX)
ViewHelper.SetViewMode(InteractionMode.Solid)
```

## Status & messages

```python
ApplicationHelper.GetActive()
ApplicationHelper.ReportInformation("done")
MessageBox.Show("text", "Title")
Application.ReportStatus("msg", StatusMessageType.Information, None)
```

## Transactions, undo/redo, tasks

For long scripts, control the command transaction and run heavy commands as a
task so undo works and the UI stays responsive:

```python
TransactionHelper.BeginCommand("script")
# ... commands ...
TransactionHelper.EndCommand()

Application.Undo(1); Application.Redo(1)      # step back/forward N commands

from SpaceClaim.Api.V<ver> import Task as NewTask, WriteBlock
def _do(): Fill.Execute(sel)
TransactionHelper.EndCommand()
WriteBlock.ExecuteTask("Defeature", NewTask(_do))
TransactionHelper.BeginCommand("script")
```

A common "undo if the result is bad" pattern: `EndCommand()` → run task →
inspect result → `Application.Undo(1)` (wrapped by `EndCommand`/`BeginCommand`)
if adjacent faces were lost or areas changed too much.

## Key enums

- `VisibilityType`: `Hide`, `Show`
- `InteractionMode`: `Solid`
- `StatusMessageType`: `Information`, `Warning`, `Error`

## Notes

- `DocumentHelper.GetRootPart()` is the real root accessor (older docs show a
  bare `GetRootPart()` — prefer the helper).
- Group creation, undo checks, and task execution are how the defeature/midsurface
  tools stay robust against protected/complex CAD.
