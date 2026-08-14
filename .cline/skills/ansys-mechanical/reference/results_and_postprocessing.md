# Results & Post-processing — condensed API

Curated subset of the result-object API. Result objects are added to the
**Solution** object, then read after solving. For solve/settings see
`analysis_setup.md`. For result types not listed, search
`Ansys_Scripting_in_Mechanical_Guide` / `Mechanical_Object_Reference`.

## Handle

```python
SOLUTION = Model.Analyses[0].Solution
```

## Add result objects

```python
TOTAL_DEF = SOLUTION.AddTotalDeformation()
NORMAL    = SOLUTION.AddNormalStress()
EQV       = SOLUTION.AddEquivalentStress()
DIR_DEF   = SOLUTION.AddDirectionalDeformation()

# Modal: one result per mode
d1 = SOLUTION.AddTotalDeformation(); d1.Mode = 2
d2 = SOLUTION.AddTotalDeformation(); d2.Mode = 5
```

Common adders: `AddTotalDeformation`, `AddDirectionalDeformation`,
`AddEquivalentStress`, `AddNormalStress`, `AddPrincipalStress`, `AddStressTool`,
`AddForceReaction`.

## Read result values (after solving)

Solve first (`Analysis.Solve(True)`, see `analysis_setup.md`), then:

```python
TOTAL_DEF.Minimum.Value        # unit-aware scalar
TOTAL_DEF.Maximum.Value
NORMAL.Minimum.Value
NORMAL.Maximum.Value

d1.ReportedFrequency.Value     # modal deformation → natural frequency
```

- Scalar results expose `.Minimum.Value` / `.Maximum.Value`.
- Modal deformation results expose `.ReportedFrequency.Value` and `.Mode`.
- Scope a result to a named selection via `.Location` (same pattern as loads).

## Key enums

- `SolverType` (settings) — see `analysis_setup.md`.
- Result-specific enums (principal-stress type, orientation, etc.) — search the
  object reference for exact members.

## MCP tools that use this

`add_total_deformation`, `add_total_deformation_all_modes`,
`add_directional_deformation`, `add_equivalent_stress`, `add_principal_stress`,
`add_stress_tool`, `add_reaction_force`, `get_modal_frequencies`,
`generate_report`.
