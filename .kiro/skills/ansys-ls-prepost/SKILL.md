---
name: ansys-ls-prepost
description: Condensed Ansys LS-PrePost scripting reference (SCL command language, command files, and the Python data-center API), organized by function (session/cfile, model query, states & results, model build, output/export). Use whenever the user automates LS-PrePost, writes cfile / SCL / LS-PrePost Python scripts, queries model or d3plot data (nodes, elements, stress, displacement), fringes computed results, or builds/edits an LS-DYNA model in LS-PrePost. For the LS-DYNA solver keyword deck itself, use the ansys-lsdyna skill.
keywords: ls-prepost, lspp, SCL, cfile, command file, runscript, runpython, LsPrePost, execute_command, cmd_result_get_value, DataCenter, get_data, data center, SCLGetDataCenterFloat, SCLGetDataCenterVector, SCLSwitchStateTo, d3plot, fringe, genselect, partsort, print png, movie gif, selection buffer, binout, post-processing
---

# Ansys LS-PrePost Scripting (condensed, by function)

LS-PrePost has three scripting layers. Know which one you need:

1. **SCL (Scripting Command Language)** — a C-like language run inside
   LS-PrePost. It can run LS-PrePost commands, retrieve LS-DYNA results, use the
   data-center extraction functions, and read d3plot / keyword data.
2. **Command file (`.cfile`)** — recorded LS-PrePost commands. A cfile can call
   an SCL/Python script via `runscript` / `runpython`, passing parameters.
3. **Python** — LS-PrePost Python modules: `LsPrePost` (`execute_command`,
   `cmd_result_get_value`) and `DataCenter` (`get_data`), plus the lower-level
   `SCL*` data-center functions. This is what real post-processing scripts use.

There is **no ANSYS MCP dispatch tool** for LS-PrePost, so this skill is a
documentation reference over `lsppscripting` and `Ansys_LS-PrePost_Users_Guide`.

## Core idea

```
example.cfile  ── runpython script.py arg1 arg2 ──►  Python/SCL script
                                                       │ query model/results
                                                       │ compute
                                                       ▼
              message file / user file  ◄──  or send back to LSPP for fringing
```

## Which reference file to open

| Function | File | Covers |
|---|---|---|
| Session & cfile | `reference/session_and_cfile.md` | SCL vs cfile vs Python, `runscript`/`runpython`, passing args |
| Model query | `reference/model_query.md` | Data-center getters, typecodes, parameter names, selection buffer |
| States & results | `reference/states_and_results.md` | `SCLSwitchStateTo`, stress/strain tensors, displacement vectors, fringe, binout |
| Model build | `reference/model_build.md` | Create nodes/elements, drag to solid, curves, delete/write parts |
| Output & export | `reference/output_export.md` | Write to message/user files, fringe back into LSPP, export parts |
| Python module interface | `reference/python_module_interface.md` | `LsPrePost.execute_command`, `DataCenter.get_data`, `cmd_result_get_value`, real SCL command tokens (genselect/fringe/print png/movie/state) |

## Fallback: search the full docs

- `search_ansys_docs(query, scope="api")` — hits `lsppscripting` (api_scripting)
  first; GUI workflows are in `Ansys_LS-PrePost_Users_Guide`.
- `get_ansys_doc_chunk(doc, chunk_id, context=1)` — pull the full chunk.
- Use single, exact tokens (e.g. `SCLGetDataCenterFloat`, `SCLSwitchStateTo`).

## MCP tools

None for LS-PrePost. Build the deck it produces per the `ansys-lsdyna` skill.
