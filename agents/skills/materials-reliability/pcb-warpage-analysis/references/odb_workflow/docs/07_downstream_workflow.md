# 07 Downstream workflow - from the ANSYS-ready ODB++ to the BGA-shadow warpage result

The whole thermal-warpage workflow has 9 steps. This tool does steps 1-2. Steps 3-9 are
described here in enough detail to hand over or to let an AI guide someone through them.
Scripts mentioned are in `1_Scripts/`.

| Step | What | Tool / script | Automated? |
|---|---|---|---|
| 1 | Collect and define the inputs | `02_input_standard.md` | checklist |
| 2 | Build the ANSYS-ready ODB++ and the stackup files | `run_odb_tool.py` | yes |
| 3 | Build the stacked 3D PCB from the 2D drawing | `1_Scripts/LayerBuilder_pyansys.py <project>.json` | yes |
| 4 | Workbench: geometry + External Data (ODB++) | Workbench UI | manual |
| 5 | Mechanical: Import Trace Mapping | Mechanical UI | manual |
| 6 | Replace element materials by the equivalent model | `mechanical/Mech_py_EquivalentMaterial_v6.py` (from step 2) | yes (script) |
| 7 | Named selection of the BGA shadow | Mechanical UI (script not yet stable) | manual |
| 8 | Supports and thermal load 30 -> 220 C | Mechanical UI | manual |
| 9 | Export BGA-shadow Z displacement, level it, report the warpage | Mechanical UI + `1_Scripts/level_bga_shadow.py <project>.json` | export manual, leveling yes |

---

## Step 1 - Inputs

See `02_input_standard.md`. Result: a project JSON with the vendor ODB++, vendor stackup
(+ thickness column name), design material table, the material library `PCB_Material_Library.xml` and the 2D drawing.

## Step 2 - ANSYS-ready ODB++

```
python run_odb_tool.py <project>.json
```

Check `verification_report.md` = PASS. The files used next:

- `<project>_Stackup_<vendor>_workinggerber.csv` -> step 3
- `<run>.tgz` -> step 4
- `mechanical/Mech_py_EquivalentMaterial_v6.py` (one file, materials embedded) -> step 6

## Step 3 - Stacked 3D model (LayerBuilder)

Script: `1_Scripts/LayerBuilder_pyansys.py` (PyAnsys Geometry; same Python environment as
the tool, `setup_env.ps1`; needs an ANSYS Geometry service / Discovery licence).

1. Settings are read from the project JSON, section `layerbuilder`. With all keys `null` it
   takes the `*_workinggerber.csv` of the newest PASS run, the drawing of
   `inputs.step_2d_drawing.path` (one planar face, e.g. `TH5_Surface_SMB_ECAD.stp`) and writes
   `geometry/<project>_<vendor>_Stackup.scdocx` next to the JSON.
2. `python 1_Scripts/LayerBuilder_pyansys.py <project>.json --check` shows the three paths
   without starting ANSYS; without `--check` it builds (or set `CONFIG_FILE` at the top of
   the script and press Run). It extrudes the face once per CSV row (row 1 = top, highest
   Z; the last row sits on the original face), names each body `<Layer Name>_<Copper Ratio>`
   (e.g. `Layer_1_EM892K2_0.296`), deletes the original face and sets Share Topology on the
   `Stackup` component. An existing output file is never overwritten.
3. Check in SpaceClaim: 83 bodies, total thickness = report total, names as above.

Notes
- The body name is what Mechanical (step 6) parses: `Layer_<N>_<FR4>...`. Case does not
  matter. The ratio at the end is not used by the script.
- The ratio comes from the computed coverage (3 decimals, dielectrics 0). It is used by other
  models and for checking; it does not change the geometry.
- Coordinates: the drawing must have its lower-left corner at (0, 0) like the ODB++ (step 2
  report says whether the drawing and the ODB++ outline are the same rectangle).

## Step 4 - Workbench: materials, geometry and External Data

1. Workbench > new **Static Structural** (or Thermal + Static Structural if a temperature
   field is mapped later).
2. **Engineering Data**: import `PCB_Material_Library.xml` (File > Import Engineering Data, or
   add it under Engineering Data Sources) and add the materials of the board to the project:
   `<Model>_RC<nn>_Ortho`, `<Model>_RC<nn>_Iso` and `Copper for Warpage`. The names of the
   board are in the step-2 report (`library materials of this board`). Body materials are
   assigned by the script of step 6, not by hand.
3. Geometry: import the `.scdocx` of step 3. Keep Share Topology.
4. Add **External Data** (Component Systems > External Data). In its Setup:
   - add the ODB++ `.tgz` of step 2 as an ECAD file (format ODB++);
   - the layers appear as `layer_<seq>_<fr4>` (lower case is normal, D-facts in 03);
   - no position offset is needed: the ODB++ outline lower-left is at (0, 0) and the drawing
     too. Do not move it manually.
5. Connect External Data > Setup of the Static Structural system; Update.
6. Check: open the ECAD preview; the copper of `layer_1_...` must match the top of the model.

If the copper looks shifted: compare the report line "2D drawing ... ODB++ profile after
shift". TH5: the ODB++ profile is 420 x 405 mm, the SMB drawing 420 x 380 mm (D10); both
start at (0, 0), so the extra 25 mm strip is beyond the model edge and is not mapped.

## Step 5 - Mechanical: Import Trace Mapping

1. Generate the mesh (layered bodies: at least 1 element through each thin layer is typical;
   there is no mesh standard yet, TH5 used 5 mm as an example).
2. In the External Data imported load folder: **Import Trace Mapping**. Scoping = **all
   bodies**. One Imported Trace for all bodies is fine. Trace metal = `Copper for Warpage`.
3. Do not suppress the Imported Trace. Right-click > Import.
4. Result: every element has a copper fraction from the ODB++ of the layer it belongs to
   (dielectric elements 0 or close to 0).
5. No trace renaming is needed: the v6 script reads body names, not trace names.

## Step 6 - Equivalent material per element (v6 script)

Script: `mechanical/Mech_py_EquivalentMaterial_v6.py` from the step-2 output folder. The
library materials of this board and the copper are embedded in it (a cut-out of
`PCB_Material_Library.xml`), so it is one file and needs no CSV. Do not run the template copy
in `1_Scripts/`.

What it does:

1. reads every body name `Layer_<N>_<Material>_<ratio>`, finds the material in its library
   and assigns the Engineering Data material `<name>_Ortho` or `<name>_Iso` to the body;
2. exports the copper fraction per element from the Imported Trace, 1 % bins, round half up;
3. writes one material per (FR4, bin): volume rule of mixtures of copper and FR4 for every
   property, which is the ANSYS "Average" material modeling; the CTE can use Turner instead;
4. writes the APDL files and a Command Snippet (`EMODIF` per element). All layer bodies are
   processed (copper layers, prepreg, core); elements in bin 0 keep the Mechanical material.

Settings at the top of the script:

| Setting | Meaning | Default |
|---|---|---|
| `FR4_MODEL` | `ORTHO` = orthotropic FR4, `ISO` = isotropic elasticity (CTE orthotropic in both) | ORTHO |
| `METHOD_CTE_XY`, `METHOD_CTE_Z` | CTE mixing: `ROM` (= ANSYS) or `TURNER` | ROM, ROM |
| `METHOD_G` | shear moduli: `ROM` (confirmed against ANSYS) or `FROM_E_NU` | ROM |
| `T_REF` | stress-free (reference) temperature, C | 30 |
| `ASSIGN_MATERIALS` | assign the body materials from the body names | True |
| `MODE` | `AUTO` (files + Command Snippet) / `FILES_ONLY` | AUTO |
| `SOLVER_UNITS` | `AUTO` | AUTO |

Run: Mechanical > Automation > Scripting > Run Script. Read the output:

- `Library :` shows `embedded (PCB_Material_Library.xml sha256 ...)` with the same characters
  as the step-2 report.
- `layer bodies with a library material` = number of layers (83 for TH5).
- one `Layer_<n>` line per layer; `Cu mean` of a copper layer is close to its coverage in the
  step-2 report.
- no unexplained `WARNING`; the last lines are `RESULT  :` and `Output dir:`.
- `Could not assign the material ...` = the materials are not in Engineering Data (step 4).
- After the first solve: `solve.out` no errors; `ds.dat` contains `EMODIF` and material IDs >= 10000.

Re-run the script after: re-meshing, re-doing Trace Mapping, a new step-2 run, a new material
library, changing any setting (old snippets are removed automatically).

To compare two solver inputs element by element (ANSYS-native against v6, or two settings):
`python 1_Scripts/Compare_TraceMapping_Dat.py <case A> <case B> <output folder>`.

More detail on the method: `1_Scripts/README_TraceMapping.md`. Material rules:
`3_materials/README_Material_Library.md`.

## Step 7 - BGA shadow named selection

Goal: the nodes on the PCB top (or bottom) surface under the BGA package footprint.

1. Get the BGA footprint rectangle(s) in board coordinates (from the layout / ODB++ top copper
   pad field; origin (0, 0) = board lower-left).
2. Mechanical > Named Selection > Worksheet: `Geometry Type = Face` on the top body
   (`Layer_1_...`), then `Node` by `Location X/Y` ranges (Range criteria) inside the footprint.
   Name it e.g. `NS_BGA_SHADOW_U1`.
3. One named selection per BGA if several are evaluated.
4. Check the node count and a picture of the selection.

(A script exists but is not stable yet; keep it manual until it is.)

## Step 8 - Supports and thermal range

Warpage needs a statically determinate support that does not constrain thermal expansion:

| Support | Where | Constrains |
|---|---|---|
| Fixed Support (vertex) | one corner node / point A | X, Y, Z |
| Displacement | point B on the same edge as A | Y = 0, Z = 0 (free in X) - "fix YZ" |
| Displacement | point C, third corner | Z = 0 - "fix Z" |

(Use small vertices or remote points so no area is clamped.)

Thermal load: reference temperature = `T_REF` (30 C, same as the v6 script). Apply a body
temperature (Thermal Condition) on all bodies, stepped from 30 C to 220 C (e.g. 30, 100, 150,
183, 200, 220 C or the reflow profile points), one load step per temperature.

## Step 9 - Export BGA-shadow Z displacement and level it

1. Directional Deformation Z, scoped to `NS_BGA_SHADOW_*`, one result per temperature of
   interest.
2. Export (right-click > Export > Text File): `Node Number`, `Directional Deformation (mm)`.
3. Copy `ds.dat` of the same solve (Solution > Open Solver Files Directory): its NBLOCK has
   the node coordinates.
4. List the cases in the `leveling` section of the project JSON and run
   `python 1_Scripts/level_bga_shadow.py <project>.json`. It looks up X/Y per node, removes
   the least-squares plane of the shadow and writes the warpage (um, mil, Smile/Cry), a
   leveled CSV, an interactive HTML and PNG pictures per case. Details, warnings and the
   optional difference of two temperatures: `10_leveling.md`.
5. Compare with shadow moiré leveled the same way at the same temperatures; JEDEC SPP-024A
   table 2 is a reference band.

---

## Hand-over checklist per project

- [ ] step 2 report PASS (v251 and v261)
- [ ] LayerBuilder .scdocx: 83 bodies, names `Layer_<N>_<FR4>_<ratio>`
- [ ] External Data loads the ODB++ without offset
- [ ] Trace Mapping imported on all bodies
- [ ] Engineering Data has the library materials of the board and `Copper for Warpage`
- [ ] v6 output: all layer bodies have a library material, no unexplained WARNING, `Library :` = the XML of this run
- [ ] BGA named selections checked
- [ ] supports A/B/C and T_REF = 30 C
- [ ] Z export + ds.dat for every temperature; leveling run without open warnings
