# 10 BGA-shadow leveling (step 9) - `1_Scripts/level_bga_shadow.py`

## Why

The supports of the warpage model (step 8) define the zero plane through three corners of
the board. The BGA shadow is a small area inside the board and is generally tilted against
that plane: its raw Z displacement is rigid tilt plus warpage. Shadow moiré and the JEDEC
flatness limits judge the package area against its own best-fit plane. Leveling removes the
least-squares plane of the shadow nodes; the remaining height range is the warpage.

## Inputs (per case, both from the same solve)

| File | From | Content |
|---|---|---|
| exported result (`.txt`, `.csv`, text `.xls`) | Mechanical: Directional Deformation Z scoped to the BGA-shadow named selection > Export > Text File | `Node Number`, `Directional Deformation (mm)` |
| `ds.dat` | solver files directory of that solve | `NBLOCK`: X, Y, Z of every node; `/com,--- Data in consistent NMM units` |

The script looks up X and Y of every exported node in the NBLOCK by node number (fixed-width
and free format, Fortran `D` exponents, several NBLOCKs). The exported file may be tab,
comma, semicolon or blank separated.

## Settings: section `leveling` of the project JSON

| Key | Default | Meaning |
|---|---|---|
| `z_unit` | `mm` | unit of the exported displacement: `mm`, `m`, `um`. A unit in the column header that differs is an input error |
| `xy_unit` | `mm` | unit of the coordinates in `ds.dat` (`NMM` solver units = mm) |
| `flip_z` | `false` | multiply the displacement by -1 (view from the other side). Swaps Smile and Cry |
| `value_column` | `null` | header text of the displacement column when the file has several value columns |
| `mode` | `detrend` | `detrend`: z - (a x + b y + c). `rotate`: rigid rotation of the point cloud so that the plane normal becomes +Z |
| `method` | `OLS` | plane fit: `OLS` (least squares), or `RANSAC`, `Huber`, `Tukey` for measured data with outliers |
| `output_dir` | `leveling` | relative to the JSON |
| `html`, `png` | `true` | write the interactive HTML and the PNG pictures |
| `accept_warnings` | `false` | see Warnings |
| `cases` | `[]` | `{"name", "result", "dat"}` per exported result; optional `value_column` per case |
| `differences` | `[]` | `{"name", "minuend", "subtrahend"}`: case A minus case B, node by node, **before** leveling |

`detrend` and `rotate` give the same warpage for the small tilts of a warpage model (the
difference is of the order tilt squared). `detrend` is the default because the earlier
studies used it.

A difference answers "how does the shadow deform between two temperatures". It is not the
difference of two warpage values: the plane is fitted to the difference field.

## Run

```
python 1_Scripts\level_bga_shadow.py <project.json> [--case NAME]
```

or set `CONFIG_FILE` at the top of the script and press Run.

Exit codes: 0 done; 2 done but a WARNING needs a human decision; 3 input error.

## Outputs

`<output_dir>\leveling_summary.csv` (one line per case) and per case
`<output_dir>\<case>\`:

| File | Content |
|---|---|
| `<case>_report.md` | warpage in um and mil, shape, plane, tilt, node count, sources, warnings |
| `<case>_leveled.csv` | node, X/Y in board coordinates, X/Y local (area corner at 0), input UZ (mm), leveled Z (um, mil) |
| `<case>.html` | interactive 3D surface and contour (plotly embedded, about 5 MB, opens offline) |
| `<case>_contour.png`, `<case>_3d.png` | pictures for reports |

Outputs of a case are rewritten when the case is run again (they are derived data; the
inputs are never touched).

## Result definitions

- **Warpage** = maximum - minimum of the leveled Z over the shadow nodes.
- **Shape**: the extreme that lies nearer to the centre of the area (bounding-box centre)
  decides. Maximum nearer to the centre = **Cry** (centre high), signed warpage negative.
  Minimum nearer = **Smile** (centre low), signed warpage positive. The sign follows the Z
  values after the optional flip.
- **Tilt** = angle between the fitted plane and the XY plane.

## Warnings (exit code 2)

A warning never changes the numbers. It means a human must look before the result is used.

| Warning | Usual cause |
|---|---|
| column states no unit | export edited by hand; confirm `z_unit` |
| n nodes are not in `ds.dat` | the two files are from different solves or meshes |
| node Z coordinates span more than 0.001 mm | the selection covers more than one surface |
| fewer than 9 nodes | wrong named selection or very coarse mesh |
| input displacement above 20 mm, warpage outside 0.01 to 2000 um | wrong unit |
| tilt above 2 degrees | wrong column or unit |

After the engineer has accepted the warnings: `"accept_warnings": true`, run again.

Input errors (exit 3): file missing, header unit differs from `z_unit`, several value
columns and no `value_column`, no common node between result and `ds.dat`, `ds.dat` units
differ from `xy_unit`, unknown mode or method.

## Example and regression value

`2_examples/leveling_sample`: a 30 -> 220 C result of an earlier project (not TH5), 323 BGA-shadow nodes (90 x 80 mm,
5 mm mesh). It only checks the script; it is not a reference result of any current board.
Result 57.54 um = 2.265 mil; Smile as exported, Cry with `flip_z = true` (the original study of
2026-03-25 used the flipped sign and reported 0.057539 mm, Cry). `tests/test_leveling.py`
checks this value.

## Possible next step

Doing the plane fit inside Mechanical (a result script on the named selection) would remove
the export of the result file and of `ds.dat`. Not done yet.
