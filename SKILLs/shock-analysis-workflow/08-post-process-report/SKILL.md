---
name: shock-session-post-process-report
description: Automated post-processing and PASS/FAIL evaluation based on exact company failure index matrix.
---

# Session 08: Post-Processing & Standard Failure Criteria

## Objective
Extract simulation response fields and evaluate structural integrity against the company's quantitative failure index matrix.

## Standard Failure Criteria Matrix (PASS / FAIL Rules)

| Material | Element Type | Load Condition | Failure Phenomena | High Risk Failure Index (判定標準) |
| :--- | :--- | :--- | :--- | :--- |
| **Metal Part**<br>Steel (SGCC, SPCC, SUS) | **Shell** | Dynamic Shock | Permanent Deformation | **EPS $\ge$ 0.01** (Plastic Strain $\ge 1\%$):<br>• (1) Go-through 1 full element<br>• (2) 1-quarter circle for seam-weld hole (not-correlated)<br>• (3) 1-half circle for standoff/pin hole (correlated) |
| **Metal Part**<br>Steel (SGCC, SPCC, SUS) | **Solid** | Dynamic Shock | Permanent Deformation | **EPS $\ge$ 0.01** go-through the entire cross section |
| **Metal Part**<br>Steel (SGCC, SPCC, SUS) | **Shell / Solid** | Vibration | Fatigue Crack | **Damage $\ge$ 1.0** (Cumulative fatigue damage) |
| **Plastic Part**<br>PC+ABS (Sabic C6200) | **Solid** | Static | Permanent Deformation | **Von-Mises Stress < Yield Strength** (Y.S) |
| **Plastic Part**<br>PC+ABS (Sabic C6200) | **Solid** | Dynamic Shock | Crack | **EPS $\ge$ 0.01** & go-through the cross section (not correlated) |
| **BGA / Solder**<br>SAC305 | **Solid**<br>(0.2mm & 3-layer) | Dynamic Drop | Solder Joint Crack | **EPS $\ge$ 0.0022** (Plastic Strain $\ge 0.22\%$ correlated) |

## Automated Reporting Pipeline
1. **LSPP / Python Data Extraction**:
   - Extract maximum plastic strain (EPS) contours on metal holes, standoff bosses, plastic clips, and SAC305 BGA corners.
2. **PASS / FAIL Automatic Evaluation**:
   - **PASS**: All EPS / Stress indices below threshold.
   - **MARGINAL**: Strain within 85% ~ 100% of threshold -> Request Senior Engineer Review.
   - **FAIL**: Exceeds threshold with cross-section penetration -> Capture hot-spot viewpoints.
3. **OfficeCLI / python-pptx / openpyxl Output**:
   - Render multi-view images and export formatted summary table into `.pptx` and `.xlsx`.
