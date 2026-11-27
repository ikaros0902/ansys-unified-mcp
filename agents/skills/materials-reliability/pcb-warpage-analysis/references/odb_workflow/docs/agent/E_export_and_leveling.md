# Stage E - step 9: export, leveling, comparison

The engineer exports two files per case from Mechanical. You run the leveling script and
explain the result. Reference: `docs/10_leveling.md`.

## Why leveling (say this to the engineer if they ask)

The supports define "flat" through three corners of the board. The BGA shadow lies somewhere
inside the board and is usually tilted against that plane, so its raw Z displacement is tilt
plus warpage. A warpage measurement (shadow moiré) and the JEDEC limits look at the package
area against its own best-fit plane. The script fits a least-squares plane through the
shadow nodes and removes it; what remains is the warpage of the BGA shadow.

## Step 9a - export (the engineer)

For each temperature of interest ("case"):

1. Solution > **Directional Deformation**, Orientation Z, scoped to the BGA-shadow named
   selection, Display Time = the result time of that temperature.
2. Right-click the result > Export > Text File. The file has two columns:
   `Node Number` and `Directional Deformation (mm)`.
3. Copy `ds.dat` from the solver files directory of the same solve (Solution > right-click >
   Open Solver Files Directory). It holds the node coordinates.
4. Put both into `PROJECT_DIR\results\<case>\`. One `ds.dat` can serve several cases of the
   same solve.

Ask them for: the case names with their temperatures, the file names, and the unit shown in
the header of the exported file.

## Step 9b - settings (decision 11)

Ask, do not assume:

1. **Unit** of the exported displacement (`z_unit`: mm, m or um). It must agree with the
   header of the file.
2. **Sign**: is the displacement to be used as exported, or flipped (`flip_z`)? Flipping
   shows the board from the other side, as some measurements do. Smile and Cry swap with it,
   so the engineer must choose it knowingly, to match the data they compare with.
3. Is a **difference of two cases** wanted (for example 220 C minus 150 C)? The default is
   none: every case is leveled on its own. A difference subtracts the two displacement
   fields node by node first and then levels the result; it answers "how much does the
   warpage change between the two temperatures", not "what is the warpage at 220 C".
   Explain this before adding one.

Then fill the `leveling` section of the project JSON:

```json
"leveling": {
  "z_unit": "mm", "xy_unit": "mm", "flip_z": false,
  "mode": "detrend", "method": "OLS",
  "cases": [
    {"name": "220C", "result": "results/220C/BGA_Z_Disp.txt", "dat": "results/220C/ds.dat"},
    {"name": "150C", "result": "results/150C/BGA_Z_Disp.txt", "dat": "results/220C/ds.dat"}
  ],
  "differences": []
}
```

Keep `mode` = `detrend` and `method` = `OLS` unless the engineer asks otherwise.

## Step 9c - run

```
python TOOL_DIR\1_Scripts\level_bga_shadow.py <json>
```

| Exit | What to do |
|---|---|
| 0 | read the summary lines and the reports |
| 3 | input error: the message says what is wrong (file missing, header unit differs from `z_unit`, several value columns, files not from the same solve). Ask the engineer; never pick a column or a unit yourself |
| 2 | results are written but a `WARNING` is open. Read every warning to the engineer (missing unit in the header, nodes missing in `ds.dat`, warpage outside 0.01 to 2000 um, tilt above 2 degrees, selection not flat). Only when they accept it, set `leveling.accept_warnings` to `true`, record it in the Warnings table and run again |

## Step 9d - report the result

Per case, from `leveling\<case>\<case>_report.md` and `leveling\leveling_summary.csv`:

- warpage in um and mil, shape (Smile / Cry) and the sign convention in use (`flip_z`);
- number of nodes, the tilt that was removed;
- the files: `<case>.html` (interactive 3D surface and contour, opens offline),
  `<case>_contour.png`, `<case>_3d.png`, `<case>_leveled.csv`.

Ask the engineer to open the HTML and confirm the shape looks physical (a smooth bowl or
dome, no stripes or steps; stripes mean nodes of several surfaces or a wrong selection).

## Step 9e - comparison (decision 13)

The engineer judges the result; you help with the numbers:

- shadow moiré data of the same board, leveled the same way, at the same temperatures, is
  the primary comparison;
- JEDEC SPP-024A table 2 (flatness during reflow, by ball pitch and ball diameter, in mil)
  is a reference band, not a pass criterion for the PCB model.

Do not call a result pass or fail yourself.

## Log entry

Step 9 `done`; every case as a line of the Results table (warpage um, mil, shape, files);
unit, sign and any difference in the Decisions table; accepted warnings in the Warnings
table.
