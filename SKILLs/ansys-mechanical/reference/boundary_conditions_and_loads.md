# Boundary Conditions & Loads — condensed API

Curated subset of the most-used supports/loads scripting API. Loads and supports
are added to an **analysis** object (not the Model) and scoped with `.Location`.
For load types not listed, search `Ansys_Scripting_in_Mechanical_Guide` /
`Mechanical_Object_Reference`.

## Handle

```python
ANALYSIS = Model.Analyses[0]   # e.g. Static Structural
```

## Pattern

```python
BC = ANALYSIS.Add<Type>()      # create
BC.Location = NAMED_SELECTION  # scope to geometry / named selection
# ...set magnitude / components...
```

## Supports

```python
FIX = ANALYSIS.AddFixedSupport()
FIX.Location = NS_FIXED

FRIC = ANALYSIS.AddFrictionlessSupport()
FRIC.Location = NS_FACE

DISP = ANALYSIS.AddDisplacement()
DISP.Location = NS_FACE
# set per-DOF components; leave a DOF free by not defining it
DISP.XComponent.Output.SetDiscreteValue(0, Quantity("0 [m]"))

RDISP = ANALYSIS.AddRemoteDisplacement()   # translations + rotations
```

## Loads

```python
# Pressure
PRES = ANALYSIS.AddPressure()
PRES.Location = NS_FACE
PRES.AppliedBy = LoadAppliedBy.SurfaceEffect
PRES.Magnitude.Output.SetDiscreteValue(0, Quantity("-100 [Pa]"))

# Force (vector load)
FORCE = ANALYSIS.AddForce()
FORCE.Location = NS_FACE
FORCE.DefineBy = LoadDefineBy.Components
FORCE.XComponent.Output.SetDiscreteValue(0, Quantity("100 [N]"))

# Others: AddRemoteForce(), AddMoment(), AddStandardEarthGravity()
GRAV = ANALYSIS.AddStandardEarthGravity()
```

## Common properties

- `.Location` — the scoped geometry / named selection.
- `.Magnitude.Output.SetDiscreteValue(step_index, Quantity(...))` — scalar loads.
- `.XComponent / .YComponent / .ZComponent` — vector components (same
  `.Output.SetDiscreteValue` pattern).
- `.DefineBy` — `LoadDefineBy.Components` vs `.Vector`.
- `.AppliedBy` — e.g. `LoadAppliedBy.SurfaceEffect` / `.Direct`.

## Key enums

- `LoadDefineBy`: `Components`, `Vector`, `Normal`
- `LoadAppliedBy`: `SurfaceEffect`, `Direct`
- Multiphysics loads exist too (e.g. `AddVoltageGround()` for coupled-field).

## MCP tools that use this

`add_fixed_support`, `add_frictionless_support`, `add_displacement`,
`add_remote_displacement`, `add_force`, `add_remote_force`, `add_moment`,
`add_pressure`, `add_standard_gravity`, `list_boundary_conditions`.
