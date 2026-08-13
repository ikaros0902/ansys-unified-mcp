---
name: ansys-optislang
description: Condensed Ansys optiSLang scripting API, organized by function (session/project, nodes & actors, parameters & responses, algorithms, designs & results). Use whenever the user drives optiSLang through the ANSYS MCP (connect_optislang, run_optislang_script, start_optislang_project), builds a solver chain / parametric system, sets up sensitivity / DoE / optimization / robustness, or asks how the native optiSLang Python API (add_actor, ParametricSystemActor, SensitivityActor, Parameter Manager) works. Load the matching reference/<function>.md before generating code.
keywords: optislang, run_python_script, add_actor, actors, ParametricSystemActor, AlgorithmSystemActor, SensitivityActor, RobustnessActor, ARSMActor, NLPQLPActor, parameter manager, criteria, objective, constraint, DoE, sensitivity, optimization, MOP, robustness, design
---

# Ansys optiSLang Scripting API (condensed, by function)

The ANSYS MCP drives optiSLang through its **native `run_python_script` API**
(the server-side optiSLang Python). High-level PyOptiSLang client helpers are
deliberately avoided because they vary across releases. So the reference files
document the native optiSLang Python API — the code you pass to
`run_optislang_script`.

## Core entry points

```python
# MCP session (client side)
connect_optislang(project_path="", ini_timeout=60)   # launch/connect
run_optislang_script("<native optiSLang python>")     # runs osl.run_python_script
start_optislang_project()                             # osl.start() — solve, blocking
```

Inside `run_optislang_script`, you write **native optiSLang Python**, where the
project scenery is built from actors:

```python
node = actors.SensitivityActor("Sensitivity")   # create an actor
add_actor(node)                                  # add it to the scenery
```

## Which reference file to open

| Function | File | Covers |
|---|---|---|
| Session & project | `reference/session_and_project.md` | connect/run/start, client vs native API |
| Nodes & actors | `reference/nodes_and_actors.md` | `add_actor`, actor classes, parametric/postprocessing actors |
| Parameters & responses | `reference/parameters_and_responses.md` | Parameter Manager, criteria (objective/constraint/limit state) |
| Algorithms | `reference/algorithms.md` | Sensitivity, sampling/DoE, optimizers, robustness |
| Designs & results | `reference/designs_and_results.md` | Design Container, MOP, result designs |

Anything not in these files — search the docs (below). Reference files are a
curated subset of the most-used dispatch API.

## Fallback: search the full docs

- `search_ansys_docs(query, scope="api")` — hits
  `optiSLang_Customization_API_and_Remote_Control` (api_reference) first.
- Method guides: `Methods_for_Parametric_Design_Optimization`,
  `optiSLang_Methods_for_Multi-Disciplinary_Optimization_and_Robustness_Analysis`.
- `get_ansys_doc_chunk(doc, chunk_id, context=1)` — pull the full chunk.
- Use single, exact tokens (e.g. `add_actor`, `ParametricSystemActor`).

## MCP tools (dispatch surface)

`connect_optislang`, `optislang_version`, `run_optislang_script`,
`start_optislang_project`, `disconnect_optislang`.
