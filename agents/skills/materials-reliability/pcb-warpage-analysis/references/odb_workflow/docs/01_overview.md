# 01 Overview - what this tool does and why

## Goal

A PCB vendor sends a **working-gerber ODB++** (CAM output, e.g. InCAM / Genesis). It is made
for manufacturing, not for simulation. ANSYS (Workbench External Data, SpaceClaim, Mechanical
Trace Mapping, EDB) needs an ODB++ that:

1. has exactly **one step** (the single PCB, no panel, no coupons);
2. has **only the copper layers** that belong to the board;
3. has **one dielectric layer between every pair of copper layers**, each with its real
   thickness;
4. has **every layer named** so the downstream scripts can find the layer number and the FR4
   material: `LAYER_<seq>_<FR4>` (e.g. `LAYER_53_EM370Z`);
5. has the **board outline lower-left corner at (0, 0)** so it lands on the 2D drawing / 3D
   model without manual offsets;
6. is **packed** in a way the ANSYS translator can unpack;
7. is **proven** to load in ANSYS 2025 R1 and 2026 R1 with the stackup read back layer by layer.

The tool also computes the **copper coverage** of every copper layer from the ODB++ graphics
(for checking and for other models) and writes the CSV files and the Mechanical script used in
the next steps.

## Inputs (all three are required)

| # | Input | Provided by | What is taken from it |
|---|---|---|---|
| 1 | Working-gerber ODB++ (`.tgz`) | PCB vendor | copper graphics, outline, copper layer order |
| 2 | Vendor stackup (`.xlsx`/`.xls`/`.csv`) | PCB vendor | **thickness of every layer** (the column the user names, e.g. "SYE Final Thickness", "Final Thickness") |
| 3 | Design material table (`.xlsx`) | Design team | **FR4 material of every dielectric**, PP/core type, layer names (TOP, L2 .. BOT), copper oz, function, glass style |

Also needed: the material library `PCB_Material_Library.xml` (Engineering Data library made from the
material workbook, `3_materials/README_Material_Library.md`; the tool checks the material names against
it and embeds the materials of the board in the Mechanical script) and the 2D board drawing (`.stp`,
alignment check and coverage region).

## Outputs (one new time-stamped folder per run)

| File | Used by |
|---|---|
| `<project>_<vendor>_<timestamp>.tgz` | Workbench External Data, SpaceClaim, EDB |
| `<project>_Stackup_<vendor>_workinggerber.csv` | `LayerBuilder_pyansys.py` (3D stacked model) |
| `mechanical/Mech_py_EquivalentMaterial_v6.py` | Mechanical, step 6 (one file: the library materials of this board and the copper are embedded) |
| `layer_map.csv` | people: every layer in every source |
| `coverage_preview/*.png` | people: what the coverage renderer saw |
| `verification_report.md` | people / AI: PASS/FAIL with all evidence |
| `translate_v251.log`, `translate_v261.log`, `run.log` | troubleshooting |

The EDB produced during verification is deleted (only the report is kept).

## Pipeline

```
 vendor ODB++ ──scan──┐
 vendor stackup ──────┼─ intake ─(questions?)─> normalized stackup (83 layers for 42 Cu)
 design table ────────┘                │
                                       ├─ build ODB++ (1 step, 42 Cu + 41 PP, names, thickness, origin)
                                       ├─ coverage (render every copper layer)
                                       ├─ outputs (CSV, layer map, Mechanical script)
                                       └─ verify (v251 + v261 translators, EDB read back) -> report
```

Ambiguities never get guessed silently. They become **questions** with a stable key, asked in
the terminal or written to `open_questions_*.md`; the answers are stored in the project JSON
(`answers`) so they are asked only once. See `05_ambiguity_rules.md`.

## The rest of the workflow

This tool covers steps 1-2 of the 9-step thermal warpage workflow. Steps 3-9 (LayerBuilder,
Workbench, External Data, Trace Mapping, v6 material replacement, BGA shadow named selection,
supports, thermal range, Z-displacement export, BGA-shadow leveling) are described in
`07_downstream_workflow.md` and `10_leveling.md`.
