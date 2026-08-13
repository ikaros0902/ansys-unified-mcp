# Native SpaceClaim Scripting — Commands

Modeling and topology commands. Most take a `Selection` (+ an `*Options` object)
and return a result whose `.CreatedBodies` / `.CreatedFaces` / `.CreatedObjects`
/ `.Success` you read back. Tokens verified from real ACT extensions.

## Midsurface (sheet metal)

```python
options = MidsurfaceOptions()
options.AllowNonManifold = False
options.ExtendSurfaces   = True
options.CreationLocation = CreationLocation.ActiveComponent
options.Group            = True
options.OffsetType       = MidSurfaceOffsetType.Middle
cmd = Midsurface(options)
cmd.AddMatchingFacePairs(face1, face2, 1.0e-5, True)   # (f1, f2, tol, auto-find)
result = cmd.Execute()
result.Success; result.CreatedFaces
```

## Fill / Delete (defeature)

```python
result = Fill.Execute(sel);   result.CreatedFaces   # heal holes/rounds
Delete.Execute(sel)                                  # delete faces/edges
```

## Loft / Extrude / Revolve

```python
# Loft between edge loops
opts = LoftOptions(); opts.GeometryCommandOptions = GeometryCommandOptions()
opts.ExtrudeType = ExtrudeType.Add
result = Loft.Create(edges_sel, None, opts)

# Extrude edges up to a face
ExtrudeEdges.Execute(edge_sel, direction, upto_sel, Point.Create(MM(0),MM(0),MM(0)), ExtrudeType.None)

# Extrude / revolve faces
opts = ExtrudeFaceOptions(); opts.ExtrudeType = ExtrudeType.ForceIndependent
ExtrudeFaces.Execute(face_sel, MM(-0.1), opts)
opts = RevolveFaceOptions(); opts.ExtrudeType = ExtrudeType.ForceIndependent
result = RevolveFaces.Execute(face_sel, axis_line, DEG(360), opts)   # -> result.CreatedBodies
```

## Split / Copy / Move / Rename

```python
result = SplitBody.ByCutter(body_sel, datum_sel)     # -> result.CreatedBodies
result = Copy.Execute(sel)                            # -> result.CreatedObjects
opts = MoveOptions()
Move.Translate(sel, direction, MM(1.0), opts)         # direction is a Direction/Vector
Move.Rotate(sel, axis_line, DEG(90), opts)
Move.UpTo(sel, upto_sel, anchor_point, opts)
anchor = Move.GetAnchorPoint(sel)
RenameObject.Execute(sel, "Ball")
DatumPlaneCreator.Create(Point.Create(MM(0),MM(0),MM(0)), Direction.DirZ)
```

## Named selections (groups)

```python
groups = NamedSelection.GetGroups(DocumentHelper.GetRootPart())
for g in groups: g.Name; g.Members; g.IsDeleted; g.Delete()
NamedSelection.Delete("GrpName")
sel.CreateAGroup("GrpName")          # create (see native_selection.md)
```

## Share topology / imprint (for bonded / shared mesh)

```python
opts = ForceShareOptions(); opts.Tolerance = MM(0.01)
ForceShare.FixSpecific(face_sel, opts)      # share specific faces
ForceShare.FindAndFix(opts)                  # find & share automatically

opts = ShareTopologyNamedSelectionOptions(); opts.Tolerance = MM(0.5)
ShareTopologyNamedSelection.FindAndFix(opts)     # create bonded-face named selections

opts = FixImprintOptions(); opts.Tolerance = MM(0.01)
opts.SearchFaces = True; opts.SearchEdges = True; opts.SearchCurves = True
FixImprint.FindAndFix(opts)                       # imprint feature lines

root.ShareTopology = ShareTopology.Merge          # set part-level share topology
```

## Key option types / enums

- Option objects: `MidsurfaceOptions`, `LoftOptions`, `ExtrudeFaceOptions`,
  `RevolveFaceOptions`, `MoveOptions`, `ForceShareOptions`,
  `ShareTopologyNamedSelectionOptions`, `FixImprintOptions`, `GeometryCommandOptions`
- `GeometryCommandOptions`: `KeepMirror`, `KeepLayoutSurfaces`,
  `KeepCompositeFaceRelationships`, `Select`
- `CreationLocation`: `ActiveComponent`
- `ExtrudeType`: `Add`, `None`, `ForceIndependent`
- `MidSurfaceOffsetType`: `Middle`
- `ShareTopology`: `Merge`, `Share`, `None`

## Notes

- Commands mutate the model; guard long loops with the transaction / task helpers
  in `native_helpers_and_transaction.md` and re-check `item.IsDeleted`.
- `Execute` vs `Create`: geometry-producing commands (Loft/RevolveFaces/SplitBody)
  return a result with `CreatedBodies`/`CreatedFaces`/`CreatedObjects`.
