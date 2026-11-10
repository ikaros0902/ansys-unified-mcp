# Geometry & Selections — condensed API

Curated subset of the most-used geometry, coordinate-system, symmetry, and
named-selection scripting API. For anything not here, search
`Mechanical_Object_Reference` / `Ansys_Scripting_in_Mechanical_Guide`.

## Tree handles

```python
Model      = DataModel.Project.Model
GEOMETRY   = Model.Geometry            # bodies / parts container
COORD_SYS  = Model.CoordinateSystems
```

## Bodies & parts

- Iterate: `Model.Geometry.GetChildren(DataModelObjectCategory.Body, True)`
- Common body properties: `.Suppressed` (bool), `.Material` (name string),
  `.Name`, `.Assignment` (material assignment).
- Suppress/unsuppress a body: set `body.Suppressed = True/False`.

## Coordinate systems

```python
CS = Model.CoordinateSystems.AddCoordinateSystem()
CS.OriginZ = Quantity("0.1 [m]")
CS.AddTransformation(TransformationType.Offset, CoordinateSystemAxisType.PositiveZAxis)
CS.SetTransformationValue(1, 0.4)
CS.AddTransformation(TransformationType.Rotation, CoordinateSystemAxisType.PositiveXAxis)
CS.SetTransformationValue(2, 90)
```

## Symmetry

```python
SYM = Model.AddSymmetry()
REGION = SYM.AddSymmetryRegion()
REGION.Type = SymmetryRegionType.Symmetric
REGION.CoordinateSystem = CS
REGION.SymmetryNormal = SymmetryNormalType.ZAxis
```

## Named selections

Two scoping modes: direct geometry selection, or a Worksheet criterion.

```python
NS = DataModel.Project.Model.AddNamedSelection()
NS.Name = "NS_FIXED_FACE"
NS.ScopingMethod = GeometryDefineByType.Worksheet
```

### Worksheet generation criteria

```python
crit = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
crit.Active   = True
crit.Action   = SelectionActionType.Add
crit.EntityType = SelectionType.GeoFace          # GeoFace / GeoEdge / GeoBody / GeoVertex
crit.Criterion  = SelectionCriterionType.LocationZ  # LocationX/Y/Z, Size, Type, ...
crit.Operator   = SelectionOperatorType.Equal       # Equal, GreaterThan, LessThan, ...
crit.Value      = Quantity('0.00 [m]')
NS.GenerationCriteria.Add(crit)
NS.Activate()
NS.Generate()
```

### Worksheet criteria — indexed style (add-then-configure)

Real ACT code often adds an empty row then sets fields by index (needed for
diagnostics-type criteria like mesh interference):

```python
ns = Model.AddNamedSelection()
ns.ScopingMethod = GeometryDefineByType.Worksheet
ns.GenerationCriteria.Add(None)
ns.GenerationCriteria[0].EntityType = SelectionType.GeoBody
ns.GenerationCriteria[0].Criterion  = SelectionCriterionType.Size
ns.GenerationCriteria[0].Operator   = SelectionOperatorType.GreaterThan
ns.GenerationCriteria[0].Value      = Quantity("0 [mm mm mm]")
# a diagnostics criterion (e.g. body interference on the mesh)
ns.GenerationCriteria.Add(None)
ns.GenerationCriteria[1].Action     = SelectionActionType.Diagnostics
ns.GenerationCriteria[1].EntityType = SelectionType.MeshElement
ns.GenerationCriteria[1].Criterion  = SelectionCriterionType.BodyInterferenceMesh
ns.Generate()
count = ns.Properties[10].InternalValue   # e.g. number of flagged elements
ids   = ns.Location.Ids                     # resulting entity/element ids
```

### Direct selection via SelectionManager

See `act_scripting_foundation.md` for the full SelectionManager API. Quick form:

```python
current = ExtAPI.SelectionManager.CurrentSelection
ExtAPI.SelectionManager.ClearSelection()   # clear so new objects get default scoping
```

## Key enums

- `GeometryDefineByType`: `Worksheet`, `Geometry`
- `SelectionType`: `GeoBody`, `GeoFace`, `GeoEdge`, `GeoVertex`, `MeshElement`, `MeshNode`
- `SelectionActionType`: `Add`, `Remove`, `Filter`, `Diagnostics`
- `SelectionCriterionType`: `LocationX/Y/Z`, `Size`, `Type`, `Named Selection`,
  `BodyInterferenceMesh`
- `SelectionOperatorType`: `Equal`, `NotEqual`, `GreaterThan`, `LessThan`, ...
- `TransformationType`: `Offset`, `Rotation`
- `CoordinateSystemAxisType`: `PositiveX/Y/ZAxis`, `NegativeX/Y/ZAxis`
- `SymmetryRegionType`: `Symmetric`, `Antisymmetric`; `SymmetryNormalType`: `XAxis/YAxis/ZAxis`

## MCP tools that use this

`list_named_selections`, `delete_named_selection`, `suppress_bodies`,
`list_point_masses`, `convert_prefix_to_point_mass`, `convert_part_to_point_mass`.
