# Shock Analysis Examples (35G 6-Direction Pipeline)

This directory contains production-grade automated scripts for setting up and auditing 35G LS-DYNA shock analyses inside ANSYS Mechanical via gRPC (PyMechanical / MechanicalController).

## Workflow Overview

The shock pipeline automates standard half-sine pulse shock simulations (35G, 11 ms duration, 16.5 ms total analysis time) across 6 directions (`+X`, `-X`, `+Y`, `-Y`, `+Z`, `-Z`).

### Scripts Included

1. **`execute_full_shock_act_pipeline.py`**
   - **Purpose**: Full end-to-end shock analysis automation covering Sessions 01 to 08.
   - **Session 01**: Material auto-assignment mapping CAD names to materials (SGCC, AL6061-T6, SUS301, FR-4, Cycoloy C6200, STF, etc.).
   - **Session 02**: Contact & Joint creation (automatic Revolute Joint extraction for lever mechanisms).
   - **Session 03**: Mesh controls (MultiZone solid meshing and localized sizing on critical components).
   - **Session 04**: Remote Point generation (rigid behavior) for mass balancing and constraints.
   - **Session 05**: Section assignment (shell thickness 0.8 mm on sheet/surface bodies, ELFORM=16, NIP=5).
   - **Session 06**: LS-DYNA explicit analysis settings (16.5 ms end time, 0.9 safety factor, 8 NCPUs, double precision, Type 6 hourglass control) and `.k` deck generation.
   - **Session 07**: Solve dispatch and real-time `glstat` energy balance monitoring (0.90 ~ 1.10 tolerance gate).
   - **Session 08**: Quantitative structural failure evaluation (Metal EPS < 0.01, BGA EPS < 0.0022, PASS/MARGINAL/FAIL) and automated reporting.

2. **`run_shock_35g_pipeline.py`**
   - **Purpose**: Rapid 35G shock load setup and deck export.
   - Generates 6-direction half-sine velocity waveforms and assigns initial conditions and boundary velocity profiles to fixture locations.
   - Configures active direction (default: `-Y_Bottom`) and exports `analysis_35g_shock.k`.

3. **`audit_rm_deep.py`**
   - **Purpose**: Deep audit of Remote Point over-constraining and unconstrained bodies.
   - Identifies bodies tied to excessive Remote Points (>= 10 RPs) and identifies unconstrained bodies prone to flying off during explicit dynamics.

## Prerequisites & Execution

These scripts connect to an active Mechanical session via gRPC:
- **Port**: Default is `10000`.
- **Execution**:
  ```powershell
  python examples/shock_analysis/run_shock_35g_pipeline.py
  python examples/shock_analysis/execute_full_shock_act_pipeline.py
  python examples/shock_analysis/audit_rm_deep.py
  ```
