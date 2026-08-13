# Native SpaceClaim Scripting — Selection

Selection is the core of native SpaceClaim scripting: build a `Selection`, filter
/ convert it, then feed it to a command. Tokens verified from real ACT
extensions. See `native_session_and_versions.md` for imports.

## Build selections

```python
sel = Selection.GetActive()                 # what the user picked
sel = Selection.SelectAll()                 # everything
sel = Selection.Create(obj)                 # from one object (or *objs)
sel = Selection.CreateByObjects(objs)       # from a list
sel = Selection.CreateByNames("Solid")      # by object name
sel = Selection.CreateByGroups("GrpName")   # from a named-selection group
sel = Selection.Empty()                     # empty (accumulate with +)
BodySelection.Create(body); FaceSelection.Create(face); EdgeSelection.Create(edge)
```

Inspect / combine:

```python
sel.Items          # the underlying objects
sel.Count
combined = selA + selB          # union
remaining = selA - selB         # difference
bodies = [b for b in Selection.GetActive().GetItems[IDesignBody]()]   # typed items
```

## Convert between entity levels

```python
sel.ConvertToEdges()      # faces/bodies -> their edges
sel.ConvertToFaces()
sel.ConvertToBodies()
sel.ConvertToAdjacent()   # adjacent faces/edges
sel.ConvertByShape(sc.Scripting.Selection.GeometryType.Circle)   # keep only circles
```

## Filter

```python
sel.FilterByRadius(r_min, r_max)              # edges/faces by radius (use MM())
sel.FilterByBoundingSphere(point, radius)     # spatial proximity
sel.FilterFaces(); sel.FilterEdges()          # keep only faces / edges
sel.FilterByVisible()                          # keep only visible
```

## Activate / group

```python
sel.SetActive()             # make it the primary (green) selection
sel.SetActiveSecondary()    # secondary selection
grp = sel.CreateAGroup("Scr_MyGroup")   # create a named-selection group from it
```

## Power selection (rule-based)

```python
PowerSelection.Faces.ByRoundChain(Selection.Create(face))   # tangent round chain
PowerSelection.Faces.ByRoundRadius(radius, PowerSelectOptions(True),
                                   SearchCriteria.SizeComparison.SmallerOrEqual)
```

## Key types / enums

- Selection classes: `Selection`, `BodySelection`, `FaceSelection`, `EdgeSelection`
- `GeometryType` (under `Scripting.Selection`): `Circle`, ...
- Items are geometry objects: `IDesignBody`, design faces/edges (their `.Shape`,
  `.Faces`, `.Edges`, `.Parent`, `.Name`, `.IsDeleted` — see
  `native_sketch_and_geometry.md`).

## Notes

- Selections can go stale after a command deletes geometry — re-create from ids
  / names, or check `item.IsDeleted` before reuse.
- Build `Selection.Empty()` and accumulate with `+` when collecting across a loop.
