# Loads & Initial Conditions — condensed reference

Applied loads (`*LOAD_*`) and initial state (`*INITIAL_*`), most driven by a
load curve (`*DEFINE_CURVE`). Card fields come from `LS-DYNA_Users_Guide`.

## Loads (`*LOAD_*`)

- `*LOAD_NODE_*` — force/moment on nodes or a node set.
- `*LOAD_SEGMENT_*` / `*LOAD_SHELL_*` — pressure on a segment/shell set.
- `*LOAD_BODY_*` — body loads (gravity/acceleration), e.g. `*LOAD_BODY_Z`.
- `*LOAD_THERMAL_*` — thermal loading for coupled runs.

Loads reference a curve for their time history:

```
*LOAD_SEGMENT_SET   -> LCID points to a *DEFINE_CURVE
*DEFINE_CURVE       -> (time, value) pairs; scaled by SF
```

## Initial conditions (`*INITIAL_*`)

- `*INITIAL_VELOCITY`, `*INITIAL_VELOCITY_GENERATION` — initial velocities on
  nodes/parts (e.g. drop/impact speed).
- `*INITIAL_STRESS_*`, `*INITIAL_STRAIN_*` — preload / mapped state.
- `*INITIAL_TEMPERATURE_*` — starting temperatures.

## Curves & functions

- `*DEFINE_CURVE` — tabular (x,y) history referenced by LCID.
- `*DEFINE_FUNCTION` — analytical function.
- `*DEFINE_TABLE` — family of curves (e.g. rate-dependent).

## Finding the right card

```
search_ansys_docs("*LOAD_SEGMENT_SET", scope="all")
search_ansys_docs("*INITIAL_VELOCITY_GENERATION", scope="all")
search_ansys_docs("*DEFINE_CURVE", scope="all")
```

## Notes

- Almost every transient load needs a `*DEFINE_CURVE` (LCID); define it first.
- For prescribed motion (not force), see `*BOUNDARY_PRESCRIBED_MOTION_*` in
  `contact_and_constraints.md`.
