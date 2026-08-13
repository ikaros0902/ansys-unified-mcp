# Analysis Setup & Solve — condensed API

Curated subset for reaching an analysis, configuring its Analysis Settings, and
solving. For settings not listed, search `Ansys_Scripting_in_Mechanical_Guide` /
`Mechanical_Object_Reference` (object "Analysis Settings" per analysis type).

## Handles

```python
ANALYSIS = Model.Analyses[0]            # first environment (Static Structural, Modal, ...)
SETTINGS = ANALYSIS.AnalysisSettings    # also ANALYSIS.Children[0]
SOLUTION = ANALYSIS.Solution
```

Analyses are usually created at the Workbench/project level (one Model cell per
analysis system). Inside Mechanical, reach them via `Model.Analyses[i]`. To find
the exact `Add<Type>Analysis` adder for programmatic creation, search the docs.

## Time / load steps

```python
SETTINGS.NumberOfSteps = 2
SETTINGS.SetStepEndTime(1, Quantity("0.4 [s]"))   # (step_index, end_time)
```

## Solver / type-specific settings

```python
# Static / transient
SETTINGS.SolverType = SolverType.Direct           # Direct, Iterative, ProgramControlled

# Modal
SETTINGS.MaximumModesToFind = 10
SETTINGS.LimitSearchToRange = True
SETTINGS.SearchRangeMinimum = Quantity('50000 [Hz]')
SETTINGS.SearchRangeMaximum = Quantity('150000 [Hz]')
```

## Solve

```python
ANALYSIS.Solve(True)     # True = synchronous (wait for completion)
```

## Key enums

- `SolverType`: `Direct`, `Iterative`, `ProgramControlled`
- Analysis-type-specific settings expose their own enums — search the object
  reference for the exact members.

## MCP tools that use this

`solve_analysis`, `get_solve_status`. Analysis-type systems are created through
the Workbench bridge tools (e.g. `create_static_structural_system_live`,
`create_modal_analysis_system_live`, ...).
