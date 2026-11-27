# 03 Vendor ODB++ defects and their fixes

Every problem met so far (TH5 SYE, TH5 Founder, MZ08, TL10), the symptom, how to recognise
it, the root cause and the fix. The tool handles D1-D14 automatically; the "Manual" column
says what to do if you work without the tool.

| ID | Symptom (where you see it) | Root cause | Fix in the tool | Manual fix |
|---|---|---|---|---|
| D1 | Translator: `ODB++ Translator does not support multistep designs (panelization).` | Job has several steps (Founder: 17 steps: pcb, panel, coupon, net, org ...) | Keep only the single-board step (`pcb`, `unit` ... or asked) | Delete the other `steps/<x>` folders and their `STEP {}` blocks |
| D2 | SpaceClaim/Workbench shows a board with zero thickness, no stackup | Working gerber has no stackup: no dielectric layers, `.layer_dielectric`/`.copper_weight` = 0 | Insert `LAYER_<n>_<FR4>` DIELECTRIC layers with `.layer_dielectric` (inch); copper `.copper_weight` = mil / 1.4 | Same edits by hand (see 04) |
| D3 | Translator ignores the thickness of named PP layers (0.0) and adds `Dielectric_1..n` itself -> 124 layers | ODB++ 6.x job: DIELECTRIC matrix layers only exist from ODB++ 8.x | Stamp `misc/info` to `ODB_VERSION_MAJOR=8`, `MINOR=1` when < 8 | Edit `misc/info` |
| D4 | Translator: `Error: Problems reading ODB file '...matrix/matrix'` (Founder) | InCAM 8.x writes a `VERSION=0` line before the first block; v251/v261 cannot read it, **even the vendor's own matrix fails** | Matrix rewritten in the classic form: no `VERSION` line, only ROW CONTEXT TYPE NAME POLARITY [DIELECTRIC_TYPE DIELECTRIC_NAME] START_NAME END_NAME OLD_NAME | Delete the `VERSION=0` line and the InCAM fields (LATIN_NAME, FLIP_NAME, ORIENTATION, SEGMENT_TYPE, ATTACHED_LYRS) |
| D5 | Translator: `matrix/matrix does not exist` after re-packing | gzip header stores a file name; the translator's 7-Zip then unpacks the gzip layer to that name and never sees the tar | Pack with GNU tar, gzip **without** stored name (`GzipFile(filename="")`), one top-level job folder | `tar -cf job.tar job` then gzip with `-n` |
| D6 | Board appears far from the origin in SpaceClaim / External Data does not land on the model (MZ08 offset ~ (227, 293) mm; TH5 y = -0.493 in) | Vendor CAM origin is not the board corner (panel coordinates, datum) | Shift every feature, the profile and `stephdr` datum so the profile lower-left = (0, 0) | Shift all coordinates in `features`, `profile` |
| D7 | `features.Z` cannot be edited | Unix `compress` (LZW) files | Decompress (unlzw3, 7-Zip fallback), write plain `features`, delete `.sum` | 7-Zip "extract" on the .Z file |
| D8 | Translator log: `Stopped reading file .../attrlist at this input: Ignored since this file is optional.` (one per layer) | The reader stops at the first InCAM attribute it does not know; anything after it is lost | Thickness attributes are written **right after the `UNITS=` line** | Put `.copper_weight` / `.layer_dielectric` at the top |
| D9 | Translator log: `Not translating nets, padstacks, or components because of errors reading eda data file` | Working gerbers have no `eda/data` (no netlist, components) | Expected. Only copper graphics + stackup are needed for External Data / Trace Mapping | none |
| D10 | Copper outside the board / External Data mapped to the wrong area | ODB++ profile is larger than the SMB drawing (TH5: profile 420 x 405 mm, drawing/fab note 420 x 380 mm; Founder COMP copper reaches 0.115 in beyond the profile) | Report compares profile and 2D drawing; coverage computed for both regions; nothing is cropped | Decide which outline is right with the requester; crop only if asked |
| D11 | `netlists`, `chk`, `tha`, `pstack_info`, `eda`, `boxes` refer to deleted layers / old coordinates | InCAM caches | Removed from the step | Delete them |
| D12 | Translator warnings `use of symbol bfr100 / hex_l... is not yet supported`, `Not translating ODB line #; use of symbol  is not yet supported`, `User defined symbol 'hdi_lj' does not have any graphics` (Founder: 17 such warnings) | The translator reads every user symbol in `symbols/`; some vendor symbols (coupon marks, logos) contain unsupported sub-symbols. Checked on Founder: none of them is used on a copper layer | Harmless; the job-level `symbols/` folder is kept because copper pads may use user symbols. The coverage table shows per layer what was not rendered | If such a warning names a symbol used on copper, the copper of that pad is missing in ANSYS: ask the vendor for standard symbols |
| D13 | Several thousand files of CAM history (`input`, `output`, `user`, `forms`, `flows`, `wheels`, `ext`, `cam_guides`) | CAM job folders | Not copied (only matrix, misc, steps, symbols, fonts) | Delete |
| D14 | Layer names with `(`, `)`, spaces or > 64 characters rejected | ODB++ names: A-Z 0-9 `_ + - .` | Material normalized: `EM370(Z)` -> `EM370Z`; name checked before writing | Rename |
| D15 | Translator: `Cannot checkout Elec_Solve_2 ... Licensed number of users already reached`, or `FlexNet Licensing error:-96 ... Host not found` (licence server unreachable, VPN) | Licence busy or not reachable - **not an ODB++ problem** | Verification runs sequentially and retries 4 x after 90 s; the report marks it "ANSYS LICENCE NOT AVAILABLE". Re-check later without rebuilding: `python run_odb_tool.py --reverify <run folder>` | Run one at a time; check VPN |
| D16 | Headless SpaceClaim import of the ODB++ hangs (no output after 15 min) | SpaceClaim ECAD import needs the UI | Not automated; test manually (`07_downstream_workflow.md` step 4) | Open SpaceClaim, File > Open |
| D17 | Command `anstranslator JVPCB1108062A.tgz ...` -> `Input file C:/WINDOWS/system32/... doesn't exist` | Relative path, translator runs in system32 | Tool always passes absolute paths | Use full paths |
| D18 | Translator writes `<random>.anstranslator\` folders of hundreds of MB next to the input (seen on OneDrive) | It unpacks beside its input | The tool copies the archive to `%TEMP%` and translates there | Translate from a local folder |
| D19 | Vendor stackup re-formatted between versions (SYE: thickness moved from column J to N, then "SYE Final Thickness" added in R) | Excel edited by people | Columns found by header text each run, never by fixed letter | - |
| D20 | Vendor sheet total row differs from the sum of rows by 0.001-0.01 mil | Rounding in the sheet | Total = sum of the chosen rows; difference only reported | - |

## Facts about the ANSYS ODB++ reader (verified 2026-11, v251 and v261)

- A copper layer's `.layer_dielectric` (inch) creates a dielectric **below** it named
  `Dielectric_n`. Set it to 0 when DIELECTRIC layers are present, otherwise layers double.
- `.copper_weight` (oz) becomes copper thickness at **1.4 mil per oz** (0.1 oz -> 0.14 mil).
- DIELECTRIC layers are honoured only in ODB++ 8.x; their thickness is `.layer_dielectric`
  (inch) in **their own** attrlist.
- The EDB stackup can be read without any ANSYS API from `edb.def`:
  `SLayer(Layer(N='name', T='signal'|'dielectric', ...), SubL(Th='2.82mil', ...))`.
- EDB layer names are lower case (`LAYER_1_EM892K2` -> `layer_1_em892k2`). This does not
  affect Mechanical: the v6 script reads **body** names, case-insensitive.
- The control-file route (`anstranslator ... -c=stackup.xml`) also works but changes only the
  EDB, not the ODB++; External Data and SpaceClaim read the ODB++, so the ODB++ itself must be
  edited. In the control file the namespace must be prefixed:
  `<c:Stackup xmlns:c="http://www.ansys.com/stackup" schemaVersion="1.0">`.

## What to ask the vendor for (prevents most of the above)

1. A **single-board step only** (no panel, no coupons) in the ODB++ delivered for simulation.
2. Origin at the **lower-left corner of the board outline**.
3. The **stackup inside the ODB++** (ODB++ 8.x dielectric layers with thickness), or at least
   a stackup table with one "final thickness" column in mil.
4. ODB++ 8.1 without the `VERSION=0` matrix line, or ODB++ 7.x.
5. Same revision/date for ODB++ and stackup table.
