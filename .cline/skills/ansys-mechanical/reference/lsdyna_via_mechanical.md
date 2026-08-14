# LS-DYNA via Mechanical (ACT) — condensed API

Driving the **LS-DYNA solver add-on inside Mechanical** through ACT: LS-DYNA
load objects, the CFL time-step calculator, analysis-settings/solver properties,
and writing the `.k` deck. This is different from the raw keyword deck — see the
`ansys-lsdyna` skill for `*KEYWORD` cards. Tokens verified from the Drop / Shock /
Section-Mass ACT extensions.

## Confirm the analysis is LS-DYNA

```python
analysis = Model.Analyses[0]
if 'LSDYNA' not in analysis.Properties[6].StringValue:
    return   # not an LS-DYNA system
analysis_settings = next(c for c in analysis.Children if 'Analysis Settings' in c.Name)
solver = analysis.Solver
```

## LS-DYNA load objects (`CreateLoadObject`)

```python
sec = analysis.CreateLoadObject("Section", "LSDYNA")
sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
sel.Ids = body_ids
sec.Properties['Geometry/DefineBy/Geo'].Value = sel
sec.Properties['Formulation'].Value = 'Fully Integrated Shell Element'   # or e.g.
#   '1 point Tetrahedron'
#   'Poor Aspect Ratio, Fully Integrated S/R Solid , Accurate Formulation'
DataModel.GetObjectById(sec.ObjectId).Name = 'scr_shell'
```

`CreateLoadObject(<type>, "LSDYNA")` creates an LS-DYNA-specific object (e.g.
`"Section"`); scope it via `Properties['Geometry/DefineBy/Geo']` and configure
via named `Properties[...]`.

## CFL time-step calculator (`CreateObject`)

```python
cfl = ExtAPI.DataModel.CreateObject("TimeStepCalc", 'LSDYNA')
cfl.Properties["Time Step Safety Factor"].Value = 0.9
cfl.Properties["Linear Viscosity Coefficient"].Value = 0.06
sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
sel.Ids = body_ids
cfl.Properties['Geometry/DefineBy/Geo'].Value = sel
cfl.Import(); Model.Activate(); cfl.Activate()
min_cfl = cfl.Properties['Minimum CFL value'].Value
```

Note: object property scoping can be asynchronous; a common trick to force an
update is to add then delete a dummy comment (`Model.AddComment().Delete()`).

## Analysis settings / solver properties

Two access styles appear:

```python
# a) by property path on the Solver object
solver.Properties['Solver Controls/Solver Type'].Value = 'Structural Analysis Only'
solver.Properties['Solver Controls/Explicit Solution Only'].Value = 'No'
solver.Properties['Solver Controls/Solver Precision'].Value = 'double'   # / 'single'
solver.Properties['Step Controls/Endtime'].Value = 0.015
solver.Properties['Implicit Controls/Initial Time Step'].Value = 1e-3
solver.Properties['Implicit Controls/Maximum Time Step Size'].Value = 1e-2
rc = solver.Properties['Output Controls/Calculate Results At']; rc.Value = 'Time'; rc.Validate()
solver.Properties['Output Controls/Time'].Value = 1e-4
solver.NotifyChange()

# b) by index into analysis_settings.Properties, using InternalValue (enum index)
props = [str(p) for p in analysis_settings.Properties]
analysis_settings.Properties[props.index('Step Controls/Endtime')].InternalValue = endtime
analysis_settings.Properties[props.index('Memory Management/Memory Allocation')].InternalValue = 1  # Manual
analysis_settings.Properties[props.index('Output Controls/Stress')].InternalValue = 1              # Yes
```

- `.Value` sets by display string; `.InternalValue` sets by the option's integer
  index; call `.Validate()` / `solver.NotifyChange()` / `Tree.Refresh()` after
  changes that gate other properties.

## Loads / initial conditions (LS-DYNA transient)

```python
# Drop height (under Initial Conditions)
ic = ExtAPI.DataModel.GetObjectsByName("Initial Conditions")[0]
dh = ic.InsertDropHeight()
dh.DropHeight = Quantity("1000 [mm]")
dh.DropDirection = DropDirection.NegativeY
dh.CoordinateSystem = cs
dh.Location = sel

# Gravity
g = analysis.AddEarthGravity(); g.Direction = GravityOrientationType.NegativeYAxis

# Initial velocity + prescribed velocity time-history
iv = analysis.AddInitialVelocity(); iv.DefineBy = LoadDefineBy.Components
iv.YComponent = Quantity("-1000 [mm sec^-1]")
v = analysis.AddVelocity(); v.DefineBy = LoadDefineBy.Components
v.XComponent.Inputs[0].DiscreteValues = [Quantity(str(t)+'[s]') for t in tlist]
v.XComponent.Output.DiscreteValues    = [Quantity(str(a)+'[mm/s]') for a in vlist]

analysis.InitialConditions            # existing ICs
analysis.Solution.Activate()          # bring solution into view before inserting
```

## Write the deck (.k)

```python
Model.NamedSelections.GenerateAllNamedSelections()   # refresh NS first
# optionally flip mesh-based connection off + ForceUpdateMeshStates before writing
analysis.WriteInputFile(r"D:\out\face.k")
```

## Key enums

- `DropDirection`: `NegativeY`, `PositiveY`, ...
- `GravityOrientationType`: `NegativeYAxis`, ...
- `LoadDefineBy`: `Components`, `Vector`
- Property values are LS-DYNA add-on strings (e.g. formulations, solver type) —
  confirm exact strings in the deck or the LS-DYNA guides.

## Relation to other skills

- Raw `*KEYWORD` deck semantics (what a Section/Contact/Control card means):
  `ansys-lsdyna`.
- Post-processing the resulting `d3plot`: `ansys-ls-prepost`.
