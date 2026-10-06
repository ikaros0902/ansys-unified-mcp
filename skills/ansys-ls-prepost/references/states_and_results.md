# States & Results — condensed reference

Working with d3plot states and computing/fringing results. Verified from
`lsppscripting`.

## Switch state (time step)

```c
Int SCLSwitchStateTo(Int ist)   // 0 < ist <= largest state; returns 1 ok / 0 fail
```

Loop over states to build time histories: switch state, query values, store.

## Result components

- Displacement / velocity / acceleration → `SCLGetDataCenterVector` (NDCOOR xyz[3]).
- Stress / strain tensor → `SCLGetDataCenterTensor` with `parameter_name`
  `"global_stress"` or `"global_strain"` (TENSOR xyz[6]).
- Scalar component values → `SCLGetDataCenterFloat` with the right `typecode`
  and `ipt` (layer / integration point).

See `model_query.md` for the full signatures.

## Compute then fringe

A common workflow (from the doc examples):

1. Extract x/y/z displacement components for all nodes.
2. Compute a derived quantity (e.g. resultant displacement, averaged stress).
3. **Fringe** the computed result back in LS-PrePost as user-defined fringe data.
4. Optionally write the computed result to a file per state.

The computed array can be loaded back into LSPP as **User defined fringe data**,
so custom quantities display like any built-in result.

## binout reader

LS-PrePost scripting includes a binout reader for ASCII-family results
(e.g. glstat/matsum/nodout written by `*DATABASE_*`, see `ansys-lsdyna`). Search
`lsppscripting` for "binout" for the reader API.

## Notes

- Always check `SCLSwitchStateTo` returned 1 before reading state-dependent data.
- Tensor is 6 components (xyz[6]); resolve von Mises / principals in-script if
  needed.
