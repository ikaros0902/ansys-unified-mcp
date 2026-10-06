---
name: shock-session-constraint-load
description: Shock dynamic boundary conditions and exact company standard LS-DYNA Analysis Settings.
---

# Session 06: Constraint, Shock Load & Standard Analysis Settings

## Objective
Configure dynamic drop/shock boundary conditions and apply the standard LS-DYNA Explicit Solver Analysis Settings (Memory, CPU, Unit System, Hourglass Type 6, Time Step Safety Factor).

## 1. Standard LS-DYNA Analysis Settings (標準求解參數矩陣)

| Category (類別) | Parameter (設定項) | Target Value (標準值) | LS-DYNA Keyword / Context |
| :--- | :--- | :--- | :--- |
| **Time Step** | Time Step Safety Factor | **0.9** | `*CONTROL_TIMESTEP` (TSSFAC = 0.9) |
| | Maximum Number Of Cycles | **10,000,000** (1e7) | `*CONTROL_TERMINATION` (MAXCYC) |
| | Automatic Mass Scaling | **No** | DT2MS = 0 (無非物理質量縮放) |
| | Number of Cases | **0** | Single Case |
| **CPU & Memory** | Memory Allocation | **Manual** | - |
| | Memory Value (MB) | **64,000 MB** (64 GB) | `MEMORY=64000M` |
| | Number Of CPUs | **8 Cores** | `NCPU=8` (SMP/MPP) |
| | Processing Type | **Program Controlled** | - |
| **Solver Controls** | Solver Type | **Program Controlled** | - |
| | Solver Precision | **double** (Double Precision) | `lsdyna_dp.exe` (消除累積數值截斷誤差) |
| | Solver Units | **Manual** | - |
| | Solver Unit System | **nmm** (mm, ton, s, N, MPa) | Standard CAE Unit System |
| | Explicit Solution Only | **Yes** | Pure Explicit Dynamics |
| **Hourglass Controls** | Hourglass Type | **Belytschko-Bindeman** | `*CONTROL_HOURGLASS` (IHQ = **6**) |
| | LS-DYNA ID | **6** | Assumed strain co-rotational |
| | Default Hourglass Coeff. | **0.1** | `QH = 0.1` |
| **Joint Controls** | Formulation | **Program Controlled** | Penalty / Lagrange Multiplier |
| **Output Controls** | Calculate Results At | **Equally Spaced Points** | `*DATABASE_BINARY_D3PLOT` |
| | Number of Output Points | **1000 Points** | $\Delta t_{	ext{plot}} = 	ext{End Time} / 1000$ |

## 2. Dynamic Boundary Conditions (載荷與約束施加)
- **Velocity / Impact**:
  - Initial Velocity components: $\pm X$, $\pm Y$, $\pm Z$ (e.g. `Scr_Velocity_-Y_Bottom = 5420 mm/s` for 1.5m drop).
  - Half-Sine Prescribed Motion: `*BOUNDARY_PRESCRIBED_MOTION_RIGID` with curve table `*DEFINE_CURVE`.
- **Numerical Damping**:
  - Inject `*DAMPING_GLOBAL` (`VALDMP = 0.02 ~ 0.05`) to suppress high-frequency ringing without dampening primary impact impulse.

## 3. ExtAPI Automation Implementation
```python
analysis = Model.Analyses[0]
settings = analysis.AnalysisSettings

# Time Step Controls
settings.TimeStepSafetyFactor = 0.9
settings.MaximumNumberOfCycles = 10000000
settings.AutomaticMassScaling = False

# CPU and Memory Management
settings.MemoryAllocation = MemoryAllocationType.Manual
settings.MemoryValue = Quantity(64000, "MB")
settings.NumberOfCPUs = 8

# Solver Controls
settings.SolverPrecision = SolverPrecisionType.Double
settings.SolverUnitSystem = SolverUnitSystemType.Nmm
settings.ExplicitSolutionOnly = True

# Hourglass Controls (Type 6 Belytschko-Bindeman)
settings.HourglassType = HourglassType.BelytschkoBindeman
settings.DefaultHourglassCoefficient = 0.1

# Time History Output Controls (1000 points)
settings.CalculateResultsAt = CalculateResultsAtType.EquallySpacedPoints
settings.NumberOfPoints = 1000
```

## Human Intervention & Verification Gates
1. **Drop Direction & Velocity Vector**: Confirm active impact direction ($\pm X, \pm Y, \pm Z$) before initiating solve.
2. **Analysis End Time**: Confirm whether rebound capture is required (default: 15 ms).
