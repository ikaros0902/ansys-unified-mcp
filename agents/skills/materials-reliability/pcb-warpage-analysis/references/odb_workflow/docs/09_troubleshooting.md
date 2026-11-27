# 09 Troubleshooting

| Message / symptom | Meaning | What to do |
|---|---|---|
| exit code 2, `STOPPED: question '...'` | a decision needs a human | read `open_questions_*.md`, fill `answers`, run again |
| `INPUT ERROR: inputs.<x>.path not found` | wrong path in the JSON | relative paths are relative to the JSON file |
| `... has 40 copper layers, the ODB++ has 42` | wrong table or wrong sheet | use the table of this board revision; set `sheet` |
| `no stackup table found in ...` | kind / name words not recognised | `08_vendor_table_formats.md` "Adding a new format" |
| `no column header contains all words of '...'` | thickness_column text does not match | the question lists all numeric columns; answer with the letter or fix the text |
| `material 'X' is not in the material library` | design table uses a material the library lacks | add the material to the library or fix the table |
| `layer n: vendor row r is cu, design row s is prepreg` | the two tables do not line up | a row is missing / extra in one table (often a solder-mask or a split PP row) |
| `coordinate records could not be parsed` | unusual features file | send the layer name and line to the tool owner; add a test |
| `output folder exists` | same timestamp twice | wait one second and run again |
| report: translator `Problems reading ODB file .../matrix/matrix` | matrix format | should not happen with the tool (D4); if it does, open the matrix and compare with `04_build_procedure.md` step 8 |
| report: `ANSYS LICENCE NOT AVAILABLE` (`Licensed number of users already reached`, `FlexNet Licensing error`) | licence busy or server unreachable (VPN) | the ODB++ is fine; later run `python run_odb_tool.py --reverify <run folder>` (writes `reverification_<ts>.md`, ~3 min, no rebuild) |
| report: layer mismatches > 0 | EDB differs from the stackup | look at the mismatch table: name (rule broken?), type, thickness (attr order, D8) |
| report: WARN 2D drawing NOT the same rectangle | ODB++ outline differs from the drawing | normal for TH5 (D10). Make sure both start at (0,0); otherwise set `origin.mode = offset_mm` |
| coverage: large `unrendered` count | text / unknown symbols on copper | small counts are harmless; a large count of `pad symbol ...` means a symbol family to add in `coverage.py` |
| coverage differs from the vendor's "copper coverage %" | vendor numbers are estimates and use other regions | the tool value is computed from the graphics; compare with the Mechanical trace-mapping mean |
| run is slow at `[4/6] copper coverage` | 42 layers x ~30 s at 1 mil, 3 workers | set `coverage.workers` higher (RAM ~1 GB per worker at 420 x 405 mm) or `resolution_mil` 2 |
| `PIL ... DecompressionBombError` | old tool version | fixed in 1.0.0 (Pillow pixel limit lifted) |
| Python: `ModuleNotFoundError` | wrong interpreter | use `%USERPROFILE%\.venvs\pcb_thermal_warpage\Scripts\python.exe` (`setup_env.ps1`) |
| SpaceClaim headless import hangs | known (D16) | import in the UI |
| LayerBuilder: `no *_workinggerber.csv in any run folder` / `no PASS verification report` | step 2 not run or not PASS for this JSON | run step 2 first, or set `layerbuilder.stackup_csv` |
| LayerBuilder: `output exists and is never overwritten` | an earlier `.scdocx` | rename / move it or set `layerbuilder.output_scdocx` |
| LayerBuilder: `ERROR: ...` right after `starting the ANSYS Geometry service` | no ANSYS / no Discovery licence on this PC | run on a PC with the licence; `--check` works without it |
| LayerBuilder: WARNING lower-left corner not at (0, 0) | wrong drawing | use the drawing whose corner is at the origin, else External Data needs an offset |
| Step 2: `inputs.material_library.path must be PCB_Material_Library.xml` | the JSON still points to the retired CSV extract | set the path of the XML library |
| Step 2: `material '...' is not in the material library` | the FR4 is not in the XML; the message says whether the workbook has it and why it was left out | the material owner completes the workbook rows and runs `Update_PCB_Material_Library`; never type values yourself |
| Step 2: WARN `... xlsx is newer than PCB_Material_Library.xml` | the workbook was edited after the last conversion | run `Update_PCB_Material_Library.bat` next to it, then step 2 again |
| Step 2: question `material_variant.<KEY>` | the library has one model with several resin contents | a human names the resin content of this board |
| v6 script: `Could not assign the material of n bodies` | Engineering Data of the system does not have the library materials | import `PCB_Material_Library.xml` in Engineering Data, add the materials to the project, refresh the Model cell |
| v6 script: `No material data. This is the template` | the template of `1_Scripts/` was run | run the copy in `runs\<run>\mechanical\` |
| v6 script: `Body '...': material X is not in the library of this script` | body name and embedded materials do not match | geometry and script are from different runs, or the body is not a stackup layer |
| Leveling: `header says '... (mm)' but leveling z_unit is 'm'` | JSON and export disagree | ask which is right, fix `leveling.z_unit` |
| Leveling: `several value columns [...]` | hand-edited export | set `leveling.value_column` after asking which column |
| Leveling: `none of the n nodes ... is in the NBLOCK` | result file and `ds.dat` are from different solves | export both from the same solve |
| Leveling: exit code 2, `DONE WITH WARNINGS` | a result needs a human look (`10_leveling.md`) | read the warnings; after acceptance set `leveling.accept_warnings` |
