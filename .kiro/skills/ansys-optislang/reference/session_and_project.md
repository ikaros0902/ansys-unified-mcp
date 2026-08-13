# Session & Project — condensed API

How to connect, run native scripts, and solve. Verified from the project's
optiSLang controller (`ansys.optislang.core` → native `run_python_script`).

## MCP tools (client side)

```python
connect_optislang(project_path="", ini_timeout=60)   # new project if path empty
optislang_version()                                   # verified version string
run_optislang_script("<native optislang python>")     # osl.run_python_script(...)
start_optislang_project()                              # osl.start() — solve, blocking
disconnect_optislang(shutdown=True)                    # dispose the process
```

- `connect_optislang` reuses an existing session if one is already connected.
- `project_path` must point to an existing `.opf` file, else a new project opens.

## Two API layers (don't confuse them)

- **Client (PyOptiSLang, `Optislang`)** — how the MCP connects/launches. You do
  not write this directly; the MCP owns the session.
- **Native optiSLang Python** — the string you pass to `run_optislang_script`.
  This runs *inside* the optiSLang server and is where `add_actor(...)`, actor
  classes, and the parameter manager live. The reference files document this
  layer.

## Typical flow

```python
# 1) connect (MCP)          -> connect_optislang()
# 2) build scenery (native) -> run_optislang_script("<... add_actor ...>")
# 3) solve (MCP)            -> start_optislang_project()
# 4) read results (native)  -> run_optislang_script("<... designs ...>")
```

## MCP tools that use this

`connect_optislang`, `optislang_version`, `run_optislang_script`,
`start_optislang_project`, `disconnect_optislang`.
