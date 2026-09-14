---
name: shock-analysis-workflow
description: End-to-end automated pipeline for ANSYS Mechanical LS-DYNA Shock / Drop analysis, coordinating 8 modular session skills.
---

# Shock Analysis Workflow Orchestrator (LS-DYNA)

## Workflow Overview
This workflow automates the end-to-end shock analysis pipeline in ANSYS Mechanical (LS-DYNA Explicit Dynamics), orchestrating 8 specialized session skills:

1. `01-material-assignment`: Rule-based material mapping (*PCB*, *CHASSIS*, *SCREW*).
2. `02-contact-creation`: Automatic Single Surface (*CONTACT_AUTOMATIC_SINGLE_SURFACE) and Tied contacts.
3. `03-mesh-tuning`: Mesh sizing with strict explicit time-step criterion (dt >= 2e-8 s).
4. `04-connection-rm`: Remote Point / Remote Mass MPC creation.
5. `05-section-assignment`: Shell mid-surface thickness and solid element formulation (ELFORM).
6. `06-constraint-load`: Half-sine shock pulse or drop initial velocity + global damping.
7. `07-solve-monitor`: LS-DYNA solver execution and Energy Balance ratio monitoring (0.9 ~ 1.1).
8. `08-post-process-report`: Von-Mises stress/displacement extraction, PASS/FAIL check, and PPT/Excel report.

## Execution Sequence
```
[Start CAD/NS]
      │
      ▼
[01-Material] ──▶ [02-Contact] ──▶ [03-Mesh (2e-8s)] ──▶ [04-Connection/RM]
                                                                │
                                                                ▼
[08-Report] ◀── [07-Solve Monitor] ◀── [06-Constraint/Load] ◀── [05-Section]
```
