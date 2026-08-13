# Connections & Contacts — condensed API

Curated subset of the contact and joint scripting API. Connections are added to
`Model.Connections`. For connection types not listed, search
`Ansys_Scripting_in_Mechanical_Guide` / `Mechanical_Object_Reference`.

## Handle

```python
connections = Model.Connections
```

## Contact region

```python
contact = connections.AddContactRegion()
contact.SourceLocation = ns_source        # named selection / geometry
contact.TargetLocation = ns_target
contact.ContactType    = ContactType.Frictionless   # Bonded, NoSeparation, Frictional, ...
contact.PinballRegion  = ContactPinballType.ProgramControlled
contact.RestitutionFactor = 0.5           # (rigid-dynamics style contact)
contact.RBDContactDetection = DSRBDContactDetection.kCDGeometryBased
```

## Joint

```python
joint = connections.AddJoint()
joint.ConnectionType = JointScopingType.BodyToGround   # or BodyToBody
joint.Type           = JointType.Fixed                 # Revolute, Translational, ...
joint.MobileLocation = ns_fixed                        # (+ ReferenceLocation for BodyToBody)
```

Other connection adders on `connections`: springs, beams, bearings, spot welds —
search the object reference for the exact `Add<Type>()` name.

## Bonded contact (real ACT usage)

```python
grp = Model.Connections.AddConnectionGroup(); grp.Name = "_Bonded_by_script"
bonded = grp.AddContactRegion()
bonded.SourceLocation = face1_sel          # CreateSelectionInfo(GeometryEntities) with .Ids
bonded.TargetLocation = face2_sel
bonded.ShellThicknessEffect = False
# pinball + offset for bonded
bonded.PinballRegion  = ContactPinballType.Radius
bonded.PinballRadius  = Quantity("1.2 [mm]")
bonded.BondedMaximumOffset = Quantity(0.6, "mm")
if bonded.ContactType == ContactType.Bonded:
    ...
```

## Typed children lookup

```python
CG = Ansys.ACT.Automation.Mechanical.Connections.ConnectionGroup
CR = Ansys.ACT.Automation.Mechanical.Connections.ContactRegion
groups   = Model.Connections.GetChildren[CG](True)
contacts = Model.Connections.GetChildren[CR](True)
# or untyped: DataModel.GetObjectsByType(DataModelObjectCategory.ContactRegion)
```

## Remote points

```python
rp = Model.RemotePoints.AddRemotePoint()
rp.Name = "RP_1"
rp.ScopingMethod = GeometryDefineByType.Component     # scope to a named selection
rp.Location      = named_selection
rp.Behavior      = LoadBehavior.Rigid                  # Rigid / Deformable
rp.DOFSelection  = RemotePointDOFSelectionType.Manual
rp.XComponent = rp.YComponent = rp.ZComponent = ActiveOrInactive.Active
rp.RotationX  = rp.RotationY  = rp.RotationZ  = ActiveOrInactive.Active
```

## Joint scoped BodyToBody + promote

```python
joint = grp.AddJoint()
joint.Type           = Ansys.Mechanical.DataModel.Enums.JointType.Fixed   # Revolute / Cylindrical
joint.ConnectionType = JointScopingType.BodyToBody
ref_sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
ref_sel.Ids = reference_ns.Location.Ids
joint.ReferenceLocation = ref_sel
mob_sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
mob_sel.Ids = mobile_ns.Location.Ids
joint.MobileLocation = mob_sel
# promote an under-defined joint to a remote point
if joint.ObjectState == ObjectState.UnderDefined:
    joint.Activate(); joint.PromoteToRemotePoint()
```

## Key enums

- `ContactType`: `Bonded`, `NoSeparation`, `Frictionless`, `Frictional`, `Rough`
- `ContactPinballType`: `ProgramControlled`, `Radius`, `AutoDetectionValue`
- `JointScopingType`: `BodyToGround`, `BodyToBody`
- `JointType`: `Fixed`, `Revolute`, `Translational`, `Cylindrical`, `Spherical`,
  `Universal`, `Planar`, `General` (fully qualified:
  `Ansys.Mechanical.DataModel.Enums.JointType.*`)
- `DSRBDContactDetection`: rigid-body contact detection modes.
- `LoadBehavior`: `Rigid`, `Deformable`, `Coupled`
- `RemotePointDOFSelectionType`: `Program Controlled`, `Manual`
- `ActiveOrInactive`: `Active`, `Inactive`
- `GeometryDefineByType`: `Geometry`, `Component`, `Worksheet` (RP scoping uses `Component`)

## Notes

- Contact needs both `SourceLocation` and `TargetLocation`.
- Joints scoped `BodyToGround` set only `MobileLocation`; `BodyToBody` also set a
  reference location.
