# Stage A - steps 1 and 2: inputs and the ANSYS-ready ODB++

You run the tool. The engineer provides the files and answers the questions.
Reference: `docs/02_input_standard.md`, `docs/05_ambiguity_rules.md`, `docs/06_verification.md`.

## Step 1 - collect the inputs

Ask for these five files and where they are. The JSON may point to them where they are
(absolute paths are fine); `PROJECT_DIR\inputs\` is only the default place for a copy when
the engineer wants one. Do not copy large vendor files without need; never edit them.

Step 1 is `done` when the intake check (step 2b) has read all files with exit code 0.

| # | File | Required | From |
|---|---|---|---|
| 1 | Vendor working-gerber ODB++ (`.tgz` / `.tar.gz` / `.tar`) | yes | PCB vendor |
| 2 | Vendor stackup table (`.xlsx` / `.xls` / `.csv`) | yes | PCB vendor |
| 3 | Design material table (`.xlsx`) | yes | design team |
| 4 | Material library `PCB_Material_Library.xml` | yes (material check, v6 script, Engineering Data) | `Material vendor` folder of the Suppliers share, next to `00_PCB Material Properties Library.xlsx` |
| 5 | 2D board drawing (`.stp`, one planar face, lower-left corner at 0,0) | needed for step 3 | mechanical |

Ask, and record in the log:

- Are the ODB++ and the vendor stackup the same revision and date?
- **Which thickness column** of the vendor stackup is to be used (decision 1)? Get the header
  text or the column letter from the engineer. If they do not know, they ask the requester.
- Is there an N+M lamination layer or another unusual layer, and which FR4 belongs to it
  (decision 2)? If the design table states the FR4 on that copper row, the tool takes it
  from there and does not ask; otherwise it asks when it finds one. A design table that can
  still be changed: suggest the design team adds it (`docs/02_input_standard.md`, section 3).

Material library: **ask the engineer for the full path of `PCB_Material_Library.xml`** on
their PC. It lies in the `Material vendor` folder of the Suppliers share, next to the
workbook `00_PCB Material Properties Library.xlsx`; the OneDrive path differs per person, so
do not guess it, and do not use the reference copy in `TOOL_DIR\3_materials\` (it is not kept
up to date; the tool warns when the JSON points at it). The file is made from the workbook by `Update_PCB_Material_Library.bat` in
the same folder (`TOOL_DIR\3_materials\README_Material_Library.md`).

- Every FR4 of the design table must be in the XML. Names are compared after removing
  everything but letters and digits (`EM370(Z)` = `EM-370(Z)` = `EM370Z`).
- A missing material is a hard stop. The tool's message says whether the workbook has the
  material and why it was left out (for example "CTE X starts at 80 C"). The material owner
  completes the workbook and runs the converter. Never type property values yourself
  (decision 4).
- `WARN ... is newer than PCB_Material_Library.xml`: the workbook was edited after the last
  conversion. Tell the engineer; they (or the material owner) run the converter, then you
  run the check again.
- Question `material_variant.<KEY>`: the library has several resin contents of one model.
  The engineer names the one of this board (decision 4).
- Open `PCB_Material_Library_report.md` next to the XML and read the engineer the
  "Assumptions and defaults" of the materials of this board once; record them in the
  Assumptions table.

## Step 2a - project JSON

1. Copy `TOOL_DIR\4_config\project_config.template.json` to
   `PROJECT_DIR\<PROJECT>_<VENDOR>.json`.
2. Fill `project.name`, `project.vendor`, the input paths (relative to the JSON, or
   absolute) and `inputs.vendor_stackup.thickness_column` with what the engineer told you.
   The template has no project values: every empty required field is yours to fill, and
   an empty `thickness_column` makes the tool ask. Leave `output_job_name` at `null`.
   Do not change `options.mechanical_script_template` (`{tool}` = TOOL_DIR).
3. Set `options.interactive` to `false` (you drive the run).
4. Leave `layerbuilder` and `leveling` as they are for now.

## Step 2b - intake check (fast, no run folder, no licence)

You may run it right after the JSON is filled, before the first status message. It writes
nothing but `open_questions_*.md` next to the JSON when a question is open.

```
python TOOL_DIR\run_odb_tool.py <json> --intake-only --non-interactive
```

| Exit | What to do |
|---|---|
| 3 | input error: the message names the file, row or column. Fix the JSON or ask for the right file. |
| 2 | no layer table is printed yet. Questions come one at a time: after each answer run again, another question can follow. Read `open_questions_<PROJECT>_<VENDOR>.md` next to the JSON. For each question apply `human_decisions.md`: ask, then add `"<key>": "<value>"` to `answers` and a `_note` (who, why, date). Run again. |
| 0 | show the engineer the printed layer table and every `DIFF` and `WARN` line. |

Checkpoint with the engineer before the full run:

- layer count = 2 x copper - 1 (83 for 42 copper layers);
- the thickness column and unit the tool reports are the ones that were agreed;
- FR4 per layer as in the design table; the FR4 of every N+M layer is the decided one (from the
  copper row of the design table, shown as an `INFO` or `DIFF` line, or from the answer);
- total thickness is what they expect.

## Step 2c - full run

Tell the engineer it takes about 10 to 15 minutes for a single-step ODB++ (up to 40 minutes
for a large multi-step archive) and uses the ANSYS 2025 R1 and 2026 R1 translator licences.

```
python TOOL_DIR\run_odb_tool.py <json> --non-interactive
```

Output: `PROJECT_DIR\runs\<PROJECT>_<VENDOR>_<timestamp>\`.

## Step 2d - read `verification_report.md`

`Result` must be **PASS**. Give the engineer:

- the acceptance-check table;
- total thickness and layer count;
- every `WARN` and `DIFF` line of "Decisions and notes" (a WARN needs their decision, see
  decision 5; the outline warning is explained in `docs/03_vendor_odb_defects.md`, D10);
- the answers that were used;
- the coverage table, and ask them to open two or three PNGs in `coverage_preview\`
  (white = copper) to see that planes and signal layers look right.

Expected warnings of the translators on a working gerber (not failures): one
`Stopped reading file .../attrlist` per copper layer, `eda/data does not exist`,
`Not translating nets ...`. Anything else: `docs/06_verification.md` and
`docs/03_vendor_odb_defects.md`.

If the report says `ANSYS LICENCE NOT AVAILABLE`: the ODB++ is fine; later run
`python TOOL_DIR\run_odb_tool.py --reverify <run folder>`.

## Log entry

Steps 1 and 2 `done` with the run folder name as evidence; the thickness column, each answer
and each accepted WARN in the Decisions / Warnings tables; total thickness and layer count in
the journal.

## Files the next stages use

| File in the run folder | Used in |
|---|---|
| `<PROJECT>_Stackup_<VENDOR>_workinggerber.csv` | step 3 |
| `<run>.tgz` | step 4 |
| `mechanical\Mech_py_EquivalentMaterial_v6.py` | step 6 |

The engineer also needs `PCB_Material_Library.xml` itself in step 4 (Engineering Data).
