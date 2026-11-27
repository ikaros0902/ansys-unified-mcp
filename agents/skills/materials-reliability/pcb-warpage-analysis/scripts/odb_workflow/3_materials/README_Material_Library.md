# PCB material library: from the workbook to Engineering Data

One source, one library:

```
00_PCB Material Properties Library.xlsx   (sheet "Table", maintained by hand)
        |  Update_PCB_Material_Library.bat   (double-click)
        v
PCB_Material_Library.xml            Engineering Data library, ANSYS 2025 R1 and later
PCB_Material_Library_report.md      what is in, what is not and why, every assumption
archive\                            earlier versions of both files
```

`PCB_Material_Library.xml` is the only material file of the PCB thermal-warpage workflow:
it is imported into Engineering Data, the ODB tool checks the design table against it, and
the Mechanical v6 script carries a copy of the materials of its board.

## When to run the converter

After every change of the sheet `Table`. Double-click `Update_PCB_Material_Library.bat`
(or `python Update_PCB_Material_Library.py`). Then read the report. The workbook may stay
open in Excel; the converter then reads its current state, unsaved edits included.

Nothing happens to the workbook. The XML is replaced only when its content changes, and the
previous XML and report go to `archive\` with a date in the name.

`python Update_PCB_Material_Library.py --check` reports without writing.

## What every material contains

For every laminate two materials are written; the resin content is part of the name:

| Name | Elasticity | Thermal expansion |
|---|---|---|
| `<Model>_RC<nn>_Ortho`, e.g. `EM-370(Z)_RC51_Ortho` | orthotropic, temperature dependent | orthotropic, instantaneous |
| `<Model>_RC<nn>_Iso` | isotropic, E = mean(Ex, Ey) | orthotropic, instantaneous |

plus density, thermal conductivity and specific heat. `RCNA` = no resin content stated.
`Copper for Warpage` is always written with fixed values (E 110 GPa, nu 0.34, 8960 kg/m3,
400 W/m-K, 380 J/kg-K, 17 ppm/C).

The Description of each material in Engineering Data lists its assumptions and defaults.

## How to add a material to the workbook

One row per value in sheet `Table`. Columns used by the converter: `Vendor`, `Model Name`,
`Resin Content`, `Glass Fiber`, `Items`, `Unit`, `Axis`, `Temperature`, `Value`.
`WB Value` and the other columns are not read.

| `Items` | `Unit` | `Axis` | `Temperature` | Needed |
|---|---|---|---|---|
| `Storage Modulus` | `MPa` (`GPa`, `Pa`) | `X`, `Y`, `Z`; empty or `X/Y` = both in-plane | every point of the curve | **yes**, X and/or Y |
| `CTE` | `ppm/C` (`1/C`) | `X`, `Y`, `Z`; empty or `X/Y` = both in-plane | every point of the curve | **yes**, in-plane and Z |
| `Poiison's Ratio` (as spelled in the workbook) | any | empty | 25 | **yes** |
| `Density` | `kg/m^3` (`g/cm^3`) | empty | 25 | **yes** |
| `Young's Modulus` | `MPa` | empty, `X/Y`, `X`, `Y` | 25 | optional |
| `Thermal Conductivity` | `W/m-K` | empty | 25 | optional (default 0.59) |
| `Specific Heat` | `J/kg-K` | empty | 25 | optional (default 1100) |
| `Tg` | `C` | empty | - | optional (shown in the description) |

`Resin Content`: a fraction (`0.51`) or a percentage (`51`). Two resin contents of one model
are two materials. Leave it empty when it is not known (`RCNA`).

## Rules the converter applies

1. **E(T) = Storage Modulus.** A `Young's Modulus` row adds its own temperature point
   (usually 25 C). When the Storage Modulus already has a point at that temperature, the
   Storage Modulus is kept and the report says so.
2. **Low-temperature end.** Every curve must reach 30 C. A curve that starts at or below
   50 C is extended to 30 C with a constant value (noted in the report and in the material
   description). A curve that starts above 50 C makes the material incomplete.
3. **High-temperature end.** Above the last data point the last value is held.
4. **X and Y** are kept separate. With one in-plane data set, X = Y.
5. **Ez**: from a Z Storage Modulus curve when the workbook has one; otherwise
   Ez = 0.6 x mean(Ex, Ey). A single Z value is not a curve and is not used.
6. **Shear moduli**: Gxy = mean(Ex, Ey) / (2(1+nu)); Gyz = Gxz = Ez / (2(1+nu)).
   One Poisson's ratio for XY, YZ and XZ.
7. **CTE** is written as instantaneous.
8. **A material is left out** (and listed in the report with the reason and the row number)
   when a required value is missing, a unit is not known, a value is not a number, an axis
   is not readable, or one temperature has two different values. Nothing is guessed.

## After the library changed

- New projects: import `PCB_Material_Library.xml` in Engineering Data (Workbench >
  Engineering Data > File > Import Engineering Data, or add it under Engineering Data
  Sources) and add the materials of the board to the project.
- Running projects keep the materials they already have. To use new data, run step 2 of the
  workflow again (the v6 script gets the new materials) and import the XML again.

## Where the library is

The library that every project uses is `PCB_Material_Library.xml` in the `Material vendor`
folder of the Suppliers share, next to the workbook. The project JSON points at that file and
the same file is imported into Engineering Data.

`ODB Modifying Tool\3_materials\PCB_Material_Library.xml` is a reference copy: it shows what
the file looks like and is not kept up to date. Do not use it for a project (the ODB tool
warns when a project JSON points at it).

## Master copy

`Update_PCB_Material_Library.py`, the `.bat` and this file are kept in
`ODB Modifying Tool\3_materials\` and copied next to the workbook. Change the master and copy
it; do not edit the copy.
