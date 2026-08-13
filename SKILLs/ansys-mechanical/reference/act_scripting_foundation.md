# ACT Scripting Foundation — condensed API

The foundation every Mechanical ACT script uses: the injected globals, the data
model, geometry access, selection, the tree, object state, transactions, and
logging. Tokens verified from real ACT extensions. This underlies all the other
mechanical reference files.

## Injected globals (available without import in ACT)

```python
ExtAPI        # top-level automation entry
Model         # == ExtAPI.DataModel.Project.Model
DataModel     # == ExtAPI.DataModel
Transaction   # context manager: with Transaction(True): ...
Quantity      # unit-aware value: Quantity("0.5 [mm]"), Quantity(val, "mm")
```

Units:

```python
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM   # or StandardMKS
ExtAPI.DataModel.Project.UnitSystem = UserUnitSystemType.StandardNMM
```

## ACT wizard entry (how inputs arrive)

When packaged as an ACT wizard, the entry point is `onupdateStep(step)` and user
inputs come from step properties (this is just the glue; the real work is the API
below):

```python
def onupdateStep(step):
    val   = step.Properties['PropName'].Value          # flat property
    sub   = step.Properties['Group'].Properties['Sub'].Value   # nested propertygroup
```

Long/UI-affecting work should run on the UI thread:

```python
ExtAPI.Application.InvokeUIThread(Main, args)   # args is a list, e.g. [None]
```

## Data model lookups

```python
DataModel.GetObjectsByType(DataModelObjectCategory.Body)          # Body / NamedSelection / ContactRegion ...
DataModel.GetObjectsByName("Initial Conditions")                  # by name -> list
DataModel.GetObjectById(objId)
Model.GetChildren(DataModelObjectCategory.NamedSelection, True)   # recursive children of a category
Model.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)  # typed variant
```

Handles: `Model.Geometry`, `Model.Mesh`, `Model.Connections`, `Model.Materials`,
`Model.CoordinateSystems`, `Model.NamedSelections`, `Model.RemotePoints`,
`Model.Analyses[0]`.

## Geometry data (GeoData) vs tree objects

Two parallel worlds: the **geometry** (GeoData, `Geo*Wrapper`) and the **tree**
(`Ansys.ACT.Automation.Mechanical.*`). Bridge with `GetGeoBody()` / `GetBody()`.

```python
for asm in ExtAPI.DataModel.GeoData.Assemblies:
    for part in asm.Parts:
        for body in part.Bodies:          # GeoBodyWrapper
            body.Id; body.Name; body.Suppressed
            body.BodyType.ToString()      # "GeoBodySolid" | "GeoBodySheet"
            body.GetBoundingBox()         # .Min.X .Max.X ...
            body.Faces; body.Edges; body.Vertices

geo_part = DataModel.GeoData.GeoPartById(part_id)
geo_ent  = DataModel.GeoData.GeoEntityById(entity_id)   # face/edge/body by id
tree_body = Model.Geometry.GetBody(geo_body)            # geo -> tree Body object
geo_body  = tree_body.GetGeoBody()                      # tree Body -> geo
```

Wrapper types (from `Ansys.ACT.Common.Geometry`): `GeoBodyWrapper`,
`GeoFaceWrapper`, `GeoEdgeWrapper` — test with
`entity.GetType() == Ansys.ACT.Common.Geometry.GeoBodyWrapper`.

## Selection

```python
SM = ExtAPI.SelectionManager
cur = SM.CurrentSelection                 # what the user picked
cur.Entities; cur.Ids                     # geo entities / ids

sel = SM.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)   # or .MeshElements
sel.Ids = [id1, id2]                      # scope by ids
sel.Entities = [body1, body2]             # or by entities
SM.NewSelection(sel)                      # push a selection
SM.ClearSelection()                       # clear so new objects get default scoping
```

`sel` is then assigned to `.Location` on loads/BCs/mesh controls/material
assignments.

## Tree (active objects) & object state

```python
ExtAPI.DataModel.Tree.ActiveObjects          # currently selected tree nodes
ExtAPI.DataModel.Tree.FirstActiveObject      # first one (often the analysis)
ExtAPI.DataModel.Tree.Refresh()
ExtAPI.DataModel.InternalObject["tree"].AddActiveObjectID(obj.ObjectId)   # select in tree

obj.GetType()          # e.g. Ansys.ACT.Automation.Mechanical.Body / Geometry / MeshControls.Sizing
obj.ObjectState        # ObjectState.Suppressed | FullyDefined | Meshed | Hidden | UnderDefined
obj.ObjectId; obj.Name; obj.Parent; obj.Children
```

Common pattern — find the owning analysis from any active object:

```python
actobj = Tree.FirstActiveObject
while 'Analysis' not in str(actobj.GetType()):
    actobj = actobj.Parent
analysis = actobj
```

## Transactions

Wrap model edits so the tree updates once and undo works:

```python
with Transaction(True):
    ns = Model.AddNamedSelection()
    ns.Name = "Scr_X"
# after the block, refresh if needed:
ExtAPI.DataModel.Tree.Refresh()
```

## Logging & messages

```python
ExtAPI.Log.WriteMessage("info")
ExtAPI.Log.WriteError(traceback_text)

clr.AddReference("Ansys.Mechanical.DataModel")
import Ansys.Mechanical.DataModel.Enums.MessageSeverityType as MessageSeverityType
ExtAPI.Application.Messages.AddMessage(MessageSeverityType.Info, msg)   # Info/Warning/Error

clr.AddReference("System.Windows.Forms")
import System
System.Windows.Forms.MessageBox.Show(msg)     # user-facing dialog
```

## Key enums / categories

- `DataModelObjectCategory`: `Body`, `NamedSelection`, `ContactRegion`, ...
- `SelectionTypeEnum`: `GeometryEntities`, `MeshElements`
- `ObjectState`: `Suppressed`, `FullyDefined`, `Meshed`, `Hidden`, `UnderDefined`
- `MechanicalUnitSystem`: `StandardNMM`, `StandardMKS`, ...

## Notes

- `Model.Geometry.LengthUnit` / `ExtAPI.DataModel.CurrentUnitFromQuantityName("Length")`
  report the active units; convert with the `units` module (`units.ConvertUnit`).
- Prefer ids over entity references across transactions — entities can go stale.
- For exact class/enum members not shown, see `Mechanical_Object_Reference` (via
  `search_ansys_docs`) or the ACT API Reference in `ACT_Test/3.documents/md`.
