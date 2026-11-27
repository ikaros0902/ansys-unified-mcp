# Stage C - steps 4 to 6: Workbench, Trace Mapping, equivalent material

The engineer works in ANSYS Workbench and Mechanical. You cannot see their screen. Give
**one step**, name the evidence you need, check it, log it, then give the next step.
Full detail: `docs/07_downstream_workflow.md` (steps 4 to 6).

Before you start, tell the engineer which four files they need:

- `PROJECT_DIR\geometry\<...>_Stackup.scdocx` (step 3);
- `PROJECT_DIR\runs\<run>\<run>.tgz` (step 2);
- `PROJECT_DIR\runs\<run>\mechanical\Mech_py_EquivalentMaterial_v6.py` (step 2);
- `PCB_Material_Library.xml` = the file of `inputs.material_library.path` in the JSON.

The first three must come from the same run. Check the run name in the log. The XML must be
the file the run used: the report line `material library: ... (sha256 ...)` and the line
`LIBRARY_INFO` at the top of the v6 script show the same 12 characters.

## Step 4 - Workbench: materials, geometry and External Data

Tell the engineer:

1. New **Static Structural** system.
2. **Engineering Data**: import `PCB_Material_Library.xml` (File > Import Engineering Data,
   or add it under Engineering Data Sources) and add to the project the materials of this
   board. The names are in the report line `library materials of this board`, each as
   `<name>_Ortho` and `<name>_Iso`, plus `Copper for Warpage`. Adding all of them is fine.
3. Geometry: import the `.scdocx`. Keep Share Topology.
4. Add **External Data** (Component Systems). In its Setup add the run `.tgz`; Format Type
   `ODB++ TGZ`. Leave Origin X/Y/Z and Theta at 0: the ODB++ corner is already at (0, 0).
5. Connect External Data > Setup to the **Model** cell of the Static Structural system and
   update.

The engineer does not assign materials to the 83 bodies by hand: the v6 script does it in
step 6. The trace metal of the Imported Trace is `Copper for Warpage`.

Evidence to ask for:

- the material names now listed in Engineering Data of the system;
- the layer list of the ECAD file shows `layer_1_<fr4>` ... `layer_<N>_<fr4>` (lower case is
  normal) and its count;
- the copper picture of `layer_1_...` lies on the top of the model (a screenshot or their
  statement);
- no manual offset was entered.

If the copper looks shifted: compare the report line "2D drawing ... ODB++ profile after
shift" with the model size (`docs/03_vendor_odb_defects.md`, D6 and D10). Do not suggest an
offset before the engineer has decided which outline is right (decision 5).

## Step 5 - mesh and Import Trace Mapping

1. **Ask for the mesh settings (decision 7)**: element size, elements through each layer.
   There is no standard yet; TH5 used 5 mm as an example. Record what they choose.
2. They generate the mesh.
3. In the imported-load folder of External Data: **Import Trace Mapping**, scoping = all
   bodies. One Imported Trace for all bodies is enough. Do not suppress it. Right-click >
   Import.

Evidence: node and element count, that the import finished without error, and that the
body names in Mechanical still read `Layer_<n>_<FR4>_<ratio>`.

## Step 6 - equivalent material per element (v6 script)

The script reads the material from every body name, assigns the Engineering Data material
to the body, and replaces the material of every element by a copper/FR4 mixture of its
copper fraction (copper layers, prepreg and core alike).

1. **Confirm the settings at the top of the script (decision 6)** with the engineer, even
   when they keep the defaults:

   | Setting | Default | Meaning |
   |---|---|---|
   | `FR4_MODEL` | `ORTHO` | `ORTHO` = orthotropic FR4 (`_Ortho` materials), `ISO` = isotropic elasticity (`_Iso`); the CTE is orthotropic in both |
   | `METHOD_CTE_XY` | `ROM` | in-plane CTE: `ROM` (same as ANSYS Average) or `TURNER` |
   | `METHOD_CTE_Z` | `ROM` | through-thickness CTE: `ROM` or `TURNER` |
   | `METHOD_G` | `ROM` | shear moduli mixed linearly (checked against ANSYS); leave it |
   | `T_REF` | 30.0 | stress-free temperature, C |
   | `ASSIGN_MATERIALS` | `True` | the script assigns the body materials |
   | `MODE` / `SOLVER_UNITS` | `AUTO` / `AUTO` | writes files and the Command Snippet |

   With the defaults the result equals the ANSYS Imported Trace "Average" material modeling.
   You may edit these values in the script copy inside the run folder when the engineer asks
   for other values; write the change into the log.
2. They run it: Mechanical > Automation > Scripting > Run Script, the file from
   `runs\<run>\mechanical\`.
3. **Ask them to paste the complete script output.** Check:

   | Line in the output | Must be |
   |---|---|
   | `Library :` | `embedded (PCB_Material_Library.xml sha256 <same 12 characters as the report>; materials ...)` |
   | `Copper  :` | E=110000 MPa, nu=0.34, CTE=1.7e-05, rho=8960 |
   | `FR4 <key>:` lines | one per FR4 of the board, the material name ends with `_Ortho` or `_Iso` as chosen |
   | `Methods :` | the settings that were agreed |
   | `layer bodies with a library material` | = layer count of step 2 (83 for 42 copper layers) |
   | `Layer_<n>` lines | one per layer; copper layers: `Cu mean` close to the coverage of the same layer in the step-2 report; dielectric layers: `Cu mean` 0 % or close to 0 |
   | `WARNING` lines | none unexplained. A body "left unchanged" means its name has no library material |
   | `RESULT  :` | present (the script ran to the end) |

4. The script stops with `Could not assign the material ...` when Engineering Data does not
   have the materials: go back to step 4, point 2, refresh the Model cell, run again.
5. Reference temperature: ask them to confirm that the environment temperature / reference
   temperature of the analysis is `T_REF` (30 C by default).

The script must be run again after: a new mesh, a new Trace Mapping, a new step-2 run, any
changed setting. Old snippets are removed by the script.

After the first solve (stage D): `solve.out` has no errors and `ds.dat` contains `EMODIF`
and material IDs of 10000 or more.

## Optional check: compare two solver inputs

`1_Scripts/Compare_TraceMapping_Dat.py` compares the final material of every element of two
`ds.dat` files, for example an ANSYS-native Imported Trace run and the v6 run of the same
model, or two runs with different settings:

```
python TOOL_DIR\1_Scripts\Compare_TraceMapping_Dat.py <case A folder or ds.dat> <case B folder or ds.dat> <output folder>
```

It writes `summary.txt`, `by_body.csv`, `elements_diff.csv`, `material_pairs.csv` and
`mixing_check_*.csv`. Offer it when the engineer wants to prove that a change of method,
library or mesh did what was intended; it is not a required step. Expected for ANSYS-native
against v6 with the defaults: only a few elements whose copper fraction lies exactly on a
bin boundary differ.

## Log entries

Step 4, 5 and 6 each `done` with the evidence above (material names, layer count,
node/element count, the key lines of the script output). Mesh settings and v6 settings in
the Decisions table; the defaults and assumptions of the materials (from
`PCB_Material_Library_report.md`, section of each material) in the Assumptions table.
