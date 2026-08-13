# Control & Output — condensed reference

Solver control (`*CONTROL_*`), output requests (`*DATABASE_*`), and deck
plumbing (`*INCLUDE`, `*PARAMETER`, `*DEFINE_*`). Card fields come from
`LS-DYNA_Users_Guide` and `LS-DYNA_Implicit_Analysis_Guide`.

## Control (`*CONTROL_*`)

- `*CONTROL_TERMINATION` — end time (ENDTIM); required for a run.
- `*CONTROL_TIMESTEP` — time step control (explicit): TSSFAC, mass scaling.
- `*CONTROL_IMPLICIT_GENERAL` — switch to implicit; `*CONTROL_IMPLICIT_SOLUTION`,
  `*CONTROL_IMPLICIT_AUTO` for implicit stepping (see implicit guide).
- `*CONTROL_CONTACT`, `*CONTROL_SHELL`, `*CONTROL_SOLID`, `*CONTROL_HOURGLASS`,
  `*CONTROL_ENERGY` — global defaults for those areas.

## Output (`*DATABASE_*`)

- `*DATABASE_BINARY_D3PLOT` — state plot database (DT = write interval) → read in
  LS-PrePost (see the `ansys-ls-prepost` skill).
- `*DATABASE_BINARY_D3THDT` — time-history states.
- `*DATABASE_<ASCII>` (e.g. `GLSTAT`, `MATSUM`, `RCFORC`, `NODOUT`, `ELOUT`) —
  ASCII histories for energies, materials, contact forces, node/element output.
- `*DATABASE_HISTORY_*` — select the nodes/elements written to the ASCII files.

## Deck plumbing

- `*INCLUDE` — pull in another deck file (split large models).
- `*PARAMETER` / `*PARAMETER_EXPRESSION` — named parameters and expressions.
- `*DEFINE_*` — curves, tables, boxes, coordinate systems, transformations
  (`*DEFINE_CURVE`, `*DEFINE_TRANSFORMATION`, `*DEFINE_COORDINATE_SYSTEM`).

## Finding the right card

```
search_ansys_docs("*CONTROL_TERMINATION", scope="all")
search_ansys_docs("*DATABASE_BINARY_D3PLOT", scope="all")
search_ansys_docs("*CONTROL_IMPLICIT_GENERAL", scope="all")
```

## Notes

- A minimal explicit deck needs `*CONTROL_TERMINATION` +
  `*DATABASE_BINARY_D3PLOT` to run and produce viewable output.
- Implicit vs explicit is chosen via `*CONTROL_IMPLICIT_*` — see
  `LS-DYNA_Implicit_Analysis_Guide`.
