# Equivalent copper/FR4 material from Trace Mapping - `Mech_py_EquivalentMaterial_v6.py`

Step 6 of the workflow. The script runs inside Mechanical (Automation > Scripting > Run
Script; ANSYS 2025 R1 and 2026 R1) after the mesh and Import Trace Mapping exist.

## One material source

All material data comes from `PCB_Material_Library.xml` (Engineering Data format), which
`3_materials/Update_PCB_Material_Library.py` writes from the material workbook. The same file
is imported into Engineering Data. `run_odb_tool.py` copies the script into
`runs\<run>\mechanical\` and embeds the XML blocks of the materials of that board and of
`Copper for Warpage`, so the script is one file and runs on any PC. No `stackup.csv` and no
material CSV is read.

To use the script by hand, set `MATERIAL_XML` at its top to the full library file (and
`MATERIAL_CHOICE` when one model has several resin contents).

`python Mech_py_EquivalentMaterial_v6.py` outside Mechanical prints the materials the script
carries; nothing else happens.

## Method

1. **Body -> material.** Body names follow LayerBuilder: `Layer_<N>_<Material>_<ratio>`,
   e.g. `Layer_53_EM370Z_0.296`. `<Material>` is compared with the library model names after
   removing everything but letters and digits (`EM-370(Z)` = `EM370Z`). The script assigns
   the Engineering Data material `<Model>_RC<nn>_Ortho` (`FR4_MODEL = "ORTHO"`) or
   `<Model>_RC<nn>_Iso` (`"ISO"`) to the body. It cannot create Engineering Data materials:
   the XML must have been imported.
2. **Copper fraction.** Every Imported Trace is exported to text; each element gets its
   fraction; the fraction is rounded half up to a 1 % bin (same as ANSYS).
3. **Mixture per (FR4, bin)**, v = copper volume fraction, at every temperature point of the
   FR4 material:

   | Property | Rule |
   |---|---|
   | Ex, Ey, Ez | v E_cu + (1 - v) E_fr4 per direction |
   | PRXY, PRYZ, PRXZ | v nu_cu + (1 - v) nu_fr4 |
   | Gxy, Gyz, Gxz | `METHOD_G = "ROM"`: v G_cu + (1 - v) G_fr4. `"FROM_E_NU"`: from the mixed E and nu |
   | CTE X, Y, Z | `ROM`: v a_cu + (1 - v) a_fr4. `TURNER`: (a_cu E_cu v + a_fr4 E_fr4 (1 - v)) / (E_cu v + E_fr4 (1 - v)) with the E of that direction |
   | density, K | volume rule |
   | Cp | mass-weighted |

   With `ROM` everywhere this is the ANSYS Imported Trace material modeling "Average". It was
   checked element by element against an ANSYS-native run (`Compare_TraceMapping_Dat.py`):
   apart from elements whose fraction lies exactly on a bin boundary, the materials agree to
   round-off. `METHOD_G = "ROM"` is the confirmed setting for an orthotropic FR4.
4. **All layer bodies** are processed: copper layers, prepreg and core. Elements in bin 0 are
   not modified; they keep the Mechanical material of the body (as ANSYS does), which is why
   the body material must be the library material.
5. **Output** in `C:\temp\trace_mapping\TM_<analysis>_<time>\`: `user_material_*.inp`
   (MPTEMP / MPDATA per FR4 and bin; material IDs 10000 + fr4_index x 101 + bin),
   `apply_<body>.inp` (`EMODIF` per element), `snippet_commands.txt`, `layer_summary.csv`,
   `run_log.txt`, and a Command Snippet `TraceMapping_v6` under the analysis. Earlier
   trace-mapping snippets are removed.

Temperature points are those of each material in the library (E and CTE points together).
Values outside the range are held constant. CTE is instantaneous (`CTEX/Y/Z`), reference
temperature `T_REF` (`MP,REFT` and `TREF`).

## Settings

| Setting | Default | Meaning |
|---|---|---|
| `FR4_MODEL` | `ORTHO` | `ORTHO` or `ISO` (isotropic elasticity, E = mean(Ex, Ey); CTE stays orthotropic) |
| `METHOD_CTE_XY`, `METHOD_CTE_Z` | `ROM` | `ROM` or `TURNER` |
| `METHOD_G` | `ROM` | `ROM` or `FROM_E_NU` |
| `T_REF`, `WRITE_TREF` | 30.0, True | reference temperature |
| `ASSIGN_MATERIALS` | True | assign body materials; False = only warn when they differ |
| `ANALYSIS_NAME` | "" | automatic: the only analysis, or the one selected in the Outline |
| `MODE` | `AUTO` | `FILES_ONLY` writes the files without creating the snippet |
| `SOLVER_UNITS` | `AUTO` | from the active unit system (mm-tonne or SI) |
| `MATERIAL_XML`, `MATERIAL_CHOICE` | "", {} | library file instead of the embedded materials |
| `BASE_MAT_ID`, `NUM_BINS`, `SKIP_ZERO_BIN` | 10000, 101, True | keep |

## Messages

| Message | Meaning |
|---|---|
| `Could not assign the material of n bodies ...` | Engineering Data does not have the named materials: import the XML, add them to the project, refresh the Model cell |
| `Body '...': material X is not in the library of this script` | the body name has a material the run did not embed: run step 2 again, or the body is not part of the stackup |
| `Body '...' is not named Layer_<N>_<Material>` | not a LayerBuilder body; left unchanged |
| `No material data. This is the template ...` | the template was run; use the copy of the run folder |
| `... fail the orthotropic Poisson/stiffness check` | a mixture is not a valid orthotropic material; check the library values |
| `Analysis '...' still has trace-mapping snippet` | another analysis has an active snippet; suppress it if that analysis is an ANSYS-native baseline |

## Comparing two runs

`python Compare_TraceMapping_Dat.py <case A folder or ds.dat> <case B folder or ds.dat> [out_dir] [--tol 1e-4]`
reads both solver inputs (materials, `EMOD` / `EMODIF`) and writes `summary.txt`,
`by_body.csv`, `elements_diff.csv`, `material_pairs.csv`, `mixing_check_A.csv` /
`mixing_check_B.csv` (which mixing rule each run follows).
