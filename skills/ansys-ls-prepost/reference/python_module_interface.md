# LS-PrePost Python Module Interface — condensed API

The Python modules exposed **inside LS-PrePost** (`LsPrePost`, `DataCenter`),
used to drive SCL commands, read model/result data, and grab command results.
This is the interface real post-processing scripts use (verified from a d3plot
EPS-report tool). It complements the C-style `SCL*` data-center functions in
`model_query.md` / `states_and_results.md`.

## Imports

```python
import LsPrePost as lspp
from LsPrePost import cmd_result_get_value as crgv, execute_command as exec
import DataCenter as dc
```

## Run SCL commands

```python
lspp.execute_command("fringe 7")     # run any SCL command string
exec("fringe 7; pfringe")             # alias; ';' chains commands
```

## Read model / result data (DataCenter)

```python
part_ids = dc.get_data("validpart_ids")     # list of valid part ids
n_elem   = dc.get_data("num_elements")
n_states = dc.get_data("num_states")         # number of d3plot states
name     = dc.get_data("part_name", id=i)    # part name by index
```

## Grab the last command's result value

After a command that computes a fringe (e.g. `fringe 7; pfringe`), LS-PrePost
temporarily stores results for the active part; read them with
`cmd_result_get_value`:

```python
exec("fringe 7; pfringe")
exec("selectpart on {}".format(part_id))     # make one part active
element_id = crgv(0)     # element id of the extreme value
max_value  = crgv(1)     # max fringe value for the active part
```

## Common SCL command tokens (used via execute_command)

Grouped by purpose (exact tokens from real scripts):

- **Select parts**: `genselect target part`, `genselect allvis`, `genselect reverse`,
  `selectpart select 1|0`, `selectpart all on|off`, `selectpart on {id}`,
  `selectpart nrbody off`, `selectpart reverse`, `+m {id}` (add), `m {id}` (show only), `clearpick`
- **Part table**: `partsort sort|done|allpart`, `partsort fieldset none`,
  `partsort fieldset {col} 1`, `partsort write "part_data.csv"`
- **View / display**: `shad`, `ac` (auto-center), `isometric x|y|z`, `mesh off`,
  `color ...`, `transp global {v}`, `ident select 1|0`, `ident partname off`
- **Fringe / range**: `fringe 7`, `pfringe`, `maxvalue 7`,
  `range userdef {min} {max}`, `range fringelimit ...`, `range pal hue max {n}`,
  `range identmax 1`, `xyplot 1 legend off`, `xyplot 1 ymax {v}`
- **State**: `state {n}` (e.g. move to last: `state {num_states}`)
- **Export**: `print png {file}.png LANDSCAPE nocompress gamma 1.000 opaque enlisted "OGL1x1"`,
  `movie gif {WxH} {name} 1 10`

## Typical flow (d3plot post-processing)

```python
part_ids = dc.get_data("validpart_ids")
lspp.execute_command("state {}".format(dc.get_data("num_states")))   # last state
for pid in part_ids:
    exec("m {}".format(pid)); exec("fringe 7; pfringe")
    exec("selectpart on {}".format(pid))
    eid, eps = crgv(0), crgv(1)                       # element id, max EPS
    exec('print png EPS_{}.png LANDSCAPE nocompress gamma 1.000 opaque enlisted "OGL1x1"'.format(pid))
```

Report assembly (Excel/images) uses ordinary Python libs (`pandas`, `openpyxl`,
`numpy`) — not LS-PrePost API.

## Relationship to the SCL C-API

- `LsPrePost.execute_command` runs the same SCL commands you'd type in a cfile
  (see `session_and_cfile.md`).
- `DataCenter.get_data(...)` / `cmd_result_get_value(...)` are the Python-friendly
  data accessors; the `SCL*` functions in `model_query.md` are the lower-level
  C-style equivalents. Prefer whichever your host binding exposes.
