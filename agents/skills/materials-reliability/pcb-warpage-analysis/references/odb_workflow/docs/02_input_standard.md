# 02 Input standard - what must be prepared before a run

Prepare one project folder, for example:

```
TH5_SYE\
  TH5_SYE.json                       <- copy of 4_config/project_config.template.json
  inputs\
    JVPCB1108062A.tgz                <- vendor working-gerber ODB++
    SYE_TH5_Workging Gerber_Stackup.xlsx   <- vendor stackup
  (design table, material library and 2D drawing may live elsewhere; paths in the JSON)
```

## 1. Vendor ODB++

- Format: `.tgz` / `.tar.gz` / `.tar` with **one job folder** inside.
- May contain panels, coupons, many steps, drill/mask/silk/document layers: the tool removes
  them. It must contain the single-board step and all copper layers as `BOARD` context
  `SIGNAL` / `POWER_GROUND` / `MIXED` layers, in stackup order (top first).
- The file is only read. Its SHA-256 is checked before and after the run.

## 2. Vendor stackup table

Any layout is accepted. The tool finds the stackup rows itself (see `08_vendor_table_formats.md`):

- one row per copper layer and one row per dielectric (PP / core), top to bottom;
- solder mask rows are allowed (ignored);
- two dielectric rows between one copper pair are allowed (merged after confirmation);
- the copper count must equal the ODB++ copper count.

**You must tell the tool which thickness column to use** - vendors put several thickness
columns side by side (design, stacking, final, vendor final). Put the header text into
`inputs.vendor_stackup.thickness_column`, e.g.

| Vendor | Header in the sheet | Value to write |
|---|---|---|
| SYE | `SYE Final\nThickness\nmil` (column R) | `"SYE Final Thickness"` |
| Founder | `Final Thickness(mil)` (column K) | `"Final Thickness"` |

All words you write must appear in the header (case and line breaks ignored). A column letter
(`"R"`) also works. If the text matches no column or several columns, the tool lists the
numeric columns with their headers, first values and sums, and asks.

Unit: read from the header (`mil`, `um`, `mm`) or set `thickness_unit`.

## 3. Design material table

The design team's stackup (e.g. `STACKUP, 42 LAYER, Hybrid, EM892K2_EM370Z_REV 06.xlsx`,
sheet `Stackup_L42_EM892K2+EM370Z`). Required per layer:

| Column content | Required | Used for |
|---|---|---|
| copper / p.p / core in one column | yes | layer kind and dielectric type |
| TOP / L2 .. L41 / BOT in one column | yes | copper names (`ecad_name`) |
| FR4 material on every dielectric row (e.g. `EM892K2`, `EM370(Z)`) | yes | layer names, Mechanical |
| copper weight (`1/2 oz+plating`, `1 oz`) | recommended | `copper_oz` in layer_map.csv |
| function (SIG/GND/PWR), foil (STD, HVLP4) | optional | `remark` in layer_map.csv |
| glass style (`PP(1078_RC67%)x1`) | optional | `remark` |

Copper rows **do not** need a material: the copper itself is one material in Mechanical; what
the copper layer needs is the **FR4 that fills it**, taken from the adjacent prepreg (rule in
`05_ambiguity_rules.md`).

**To have no FR4 question at all**, ask the design team to write the filling FR4 on the
copper row, in the same column as the dielectric materials, at least for the layers the
prepreg rule cannot decide (N+M lamination layer between two different prepregs, copper
between two cores). The name must be one of the material library (`EM370(Z)` is fine). The
tool then uses it without asking and lists it in the report. Any other text on a copper row
(`Copper`, a foil type) is ignored.

Materials are normalized to letters and digits, upper case: `EM370(Z)` -> `EM370Z`. This is
the only form written into layer and body names (the Mechanical v6 script and the material
library are compared the same way: `EM-370(Z)` of the library = `EM370Z`).

## 4. Material library (required for step 6)

`PCB_Material_Library.xml`: the Engineering Data library that `Update_PCB_Material_Library.bat`
writes from the workbook `00_PCB Material Properties Library.xlsx` (same folder, `Material
vendor` on the Suppliers share; rules in `3_materials/README_Material_Library.md`). It is the
only material file of the workflow:

- step 2 checks every FR4 of the design table against it (the run stops when one is missing
  and says why the converter left it out);
- step 2 embeds the materials of the board and `Copper for Warpage` in the Mechanical script;
- step 4 imports the same file into Engineering Data.

Materials are named `<Model>_RC<resin content>_Ortho` / `_Iso`. When the library has several
resin contents of one model, the tool asks which one the board uses (`material_variant.<KEY>`).
Write the full path into `inputs.material_library.path` (`%USERPROFILE%` may be used). The
tool warns when the workbook next to the XML is newer than the XML.

## 5. 2D drawing (optional)

The `.stp` used by LayerBuilder. The tool compares its rectangle with the ODB++ outline after
the origin shift and reports whether they are the same; it also computes coverage inside it.

## 6. The project JSON

Copy `4_config/project_config.template.json`. Every key has a `_key` help text next to it.
Minimum to fill: `project.name`, `project.vendor`, the three input paths and
`vendor_stackup.thickness_column`. Relative paths are relative to the JSON file; `{tool}`
means the tool folder.

The same JSON also carries the settings of step 3 (section `layerbuilder`, all `null` =
automatic, `07_downstream_workflow.md`) and of step 9 (section `leveling`, `10_leveling.md`).
Keep one JSON per board and vendor in the project folder, not in the tool folder.

## Checklist before running

- [ ] ODB++ is the latest working gerber of this board revision
- [ ] vendor stackup is the one that belongs to that ODB++ (same date / revision)
- [ ] thickness column name agreed with the requester
- [ ] design table has the material on every dielectric row
- [ ] every FR4 of the board is in `PCB_Material_Library.xml` (see `PCB_Material_Library_report.md`)
- [ ] copper count is the same in all three (the tool checks, but know it beforehand)
- [ ] N+M lamination layers / unusual layers: the FR4 to pair is written on the copper row of the design table, or you know it (answer in `answers`)
