# Session & Command Files — condensed reference

How the three scripting layers fit together. Verified from `lsppscripting`.

## SCL — the scripting command language

SCL is a C-like language executed inside LS-PrePost. From a script you can:

- run LS-PrePost commands,
- retrieve LS-DYNA results and use data-center extraction functions,
- read results from d3plot files or model data from the keyword input file,
- output to the message file / a user file, or send data back to LS-PrePost for
  fringing or plotting.

## Command file (`.cfile`)

A cfile is a sequence of recorded LS-PrePost commands. It can drive the GUI
(open model, set views, fringe) and, importantly, call a script:

```
runscript script.scl arg1 arg2      # call an SCL script with parameters
runpython  script.py  arg1 arg2      # call a Python script with parameters
```

- Parameters listed after the script name are passed to the script (e.g. input
  file, output file, numeric params).
- A common pattern: `example.cfile` defines input/output paths + a few params,
  then calls the SCL/Python script that does the work.

## Passing arguments from the command line

Scripts can read the arguments passed via `runscript`/`runpython` (e.g. a file
name, a numeric parameter, or a string). This is how a reusable script is
parameterized per run.

## Which layer to use

- Pure GUI automation (open, view, fringe, save image) → cfile commands.
- Data extraction / computation on results or model → SCL or Python with the
  data-center API (see `model_query.md`, `states_and_results.md`).
- Prefer Python when you want general-purpose libraries alongside the `SCL*` API.

## Notes

- For the exact GUI command tokens (open, fringe, genselect, ...), search
  `Ansys_LS-PrePost_Users_Guide` / `lsppscripting`.
