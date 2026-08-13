# Parameters & Responses — condensed API

Parameters, criteria (responses/objectives/constraints), and start designs are
managed by the **ParametricSystemActor**. Native optiSLang Python.

## Where they live

```python
system = actors.ParametricSystemActor("ParametricSystem")
add_actor(system)
```

Per the API reference, the ParametricSystemActor manages: **parameters,
criteria, results, start designs, and designs**.

## Parameter Manager

The Parameter Manager holds the parameters used for the simulation (design
variables with bounds/type). It is the entry point for defining what varies.
For the exact method names to add/edit parameters, search
`optiSLang_Customization_API_and_Remote_Control` for "Parameter Manager".

## Criteria (objectives / constraints / limit states)

Criteria define the responses to evaluate and how they are judged:

- **Objective** — a quantity to minimize/maximize.
- **Constraint** — a bound the design must satisfy.
- **Limit state function** — used for reliability analyses.

(These three criterion roles are defined in the optiSLang actors reference.)

## Notes

- Parameters + criteria together define the parametric problem the algorithms
  (see `algorithms.md`) explore.
- Result values per design are collected into the Design Container (see
  `designs_and_results.md`).
- For exact setters (parameter bounds, criterion expressions), search the
  Customization API doc — these vary by release, so verify before generating.
