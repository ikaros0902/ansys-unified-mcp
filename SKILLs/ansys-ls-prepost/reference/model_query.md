# Model Query — condensed reference

The data-center API retrieves model/result values into your script. Verified
signatures from `lsppscripting`. These are the `SCL*` functions (available in
SCL and Python).

## Scalars

```c
Int   SCLGetDataCenterInt(char *parameter_name)
Float SCLGetDataCenterFloat(char *parameter_name, Int typecode, Int index, Int ipt)
```

- `parameter_name` — a data-center name (see parameter name list in the doc).
- `typecode` — element/node type constant: `"SOLID"`, `"SHELL"`, `"BEAM"`,
  `"TSHELL"`, `"NODE"`, `"SPHNODE"` (pass `0` when not needed).
- `index` — element index; `ipt` — integration point / layer
  (`"MID"`, `"INNER"`, `"OUTER"`, or `1,2,...`).

## Vectors & tensors

```c
void SCLGetDataCenterVector(char *parameter_name, Int externalid, NDCOOR *result)
     // NDCOOR { Float xyz[3]; } — nodal coord, displacement, velocity, acceleration
void SCLGetDataCenterTensor(char *parameter_name, Int typecode, Int externalid,
                            Int ipt, TENSOR *result)
     // TENSOR { Float xyz[6]; } — parameter_name "global_stress" / "global_strain"
```

## Arrays

```c
Int SCLGetDataCenterIntArray(char *parameter_name, Int **results, Int type, Int id)
    // e.g. parameter_name "elemofpart_ids"; type=0 internal ids, type>0 external ids
    // id = element/part/nodeset/elementset id; returns array size
Int SCLGetDataCenterFloatArray(char *parameter_name, Int typecode, Int ipt, Float **results)
```

## Model size / topology

Typical queries (see the parameter name list in `lsppscripting`): number of
nodes/elements, largest node/element id, the node id array, element connectivity.

## Selection buffer

Scripts can read items the user picked into the **selection buffer** (e.g. the
node ids currently selected) — useful for acting on an interactive selection.

## Notes

- The available `parameter_name` values are enumerated in the doc's parameter
  name list — search `lsppscripting` for the exact name before using it.
- `typecode`/`ipt` only matter for element component values (shell/beam/tshell
  layers, fully integrated solids).
