# Nodes & Actors — condensed API

The optiSLang scenery is built from **actors** (nodes). Create an actor, set its
properties, then `add_actor(...)`. Native optiSLang Python (runs via
`run_optislang_script`). Verified actor names from
`optiSLang_Customization_API_and_Remote_Control` and `optiSLang_Users_Guide`.

## Pattern

```python
node = actors.<ActorClass>("Node name")   # create
node.<property> = <value>                  # configure
add_actor(node)                            # add to scenery
```

## Actor classes

- `actors.ParametricSystemActor` — the parametric system. Manages parameters,
  criteria, results, start designs, and designs (see `parameters_and_responses.md`).
- `actors.AlgorithmSystemActor` — algorithm system; supports binfile writing and
  algorithm-specific settings (see `algorithms.md`).
- `actors.PostprocessingActor` — a postprocessing node.
- Sampling / analysis actors: `SensitivityActor`, `RobustnessActor`,
  `SamplingActor` (see `algorithms.md`).
- Optimizer actors: `ARSMActor`, `NLPQLPActor`, `NOAActor` (with `EAActor`,
  `PSOActor`, `SDIActor`), `SimplexActor`, `MemeticActor`.

## Example: postprocessing node (verified)

```python
pp_node = actors.PostprocessingActor("Postprocessing")
pp_node.mdb_path = "D:\\develop\\oscillator_robustness.csv"
pp_node.text_import_settings_file = "D:\\develop\\oscillator_robustness.json"
pp_node.text_import_non_interactive = True
add_actor(pp_node)
```

## Notes

- Actor *properties* vary by class and release; for the exact settable names,
  search `optiSLang_Customization_API_and_Remote_Control` by the actor class name.
- A solver-chain integration node wraps your solver (e.g. a Workbench/Mechanical
  project) as an actor whose parameters/responses feed the parametric system.
