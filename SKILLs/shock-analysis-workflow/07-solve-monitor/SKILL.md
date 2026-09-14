---
name: shock-session-solve-monitor
description: LS-DYNA solver execution and real-time energy balance monitoring session.
---

# Session 07: Solve & Energy Balance Monitor

## Objective
Launch LS-DYNA solve process and monitor solution convergence and energy conservation in real time.

## ACT API & Scripting Path
- **Execution Transport**:
  - PyMechanical gRPC: `analysis.Solve()`
  - Batch Subprocess: `lsrun.exe -p input.k -n <cores>`
- **Real-time Monitoring Metrics**:
  - Track `glstat` (Global Statistics) and `d3hsp`.
  - Calculate `Energy Ratio = Total Energy / (Initial Energy + External Work)`.

## Human Intervention & Verification Gates
1. **Energy Balance Anomaly**:
   - If `Energy Ratio` deviates from `1.0 ± 0.1` (0.9 ~ 1.1), halt and alert user (indicates numerical instability or contact explosion).
   - If Hourglass Energy exceeds 10% of Internal Energy, suggest switching to fully-integrated formulation (ELFORM=16).
2. **Negative Volume / Premature Exit**: Alert user on severe element distortion.
