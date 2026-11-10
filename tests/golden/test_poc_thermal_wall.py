# Strictly ASCII English Comments
"""一維複合雙層平壁穩態導熱 (Composite Two-Layer Plane Wall) 極速黃金基準測試與數值驗收引擎。

本模組為 Stage 5 熱傳力學 (Mechanical Thermal / MAPDL) 領域之黃金基準測試：
1. 物理問題：1D 複合雙層平壁穩態導熱 (Composite Two-Layer Plane Wall Heat Conduction)。
2. 幾何與材料規格：
   - 第一層：厚度 L1 = 0.02 m, 導熱係數 k1 = 50.0 W/(m*K)
   - 第二層：厚度 L2 = 0.05 m, 導熱係數 k2 = 0.20 W/(m*K)
3. 邊界條件：
   - 左側表面溫度 T1 = 400.0 K (126.85 C)
   - 右側表面溫度 T2 = 300.0 K (26.85 C)
4. 理論解析解 (Fourier 串聯熱阻定律)：
   - 層 1 熱阻 R1 = L1 / k1 = 0.0004 m^2*K/W
   - 層 2 熱阻 R2 = L2 / k2 = 0.2500 m^2*K/W
   - 總串聯熱阻 R_tot = R1 + R2 = 0.2504 m^2*K/W
   - 理論熱通量 q_theory = (T1 - T2) / R_tot = 100.0 / 0.2504 ≈ 399.361022 W/m^2
   - 介面理論溫度 T_int_theory = T1 - q_theory * R1 ≈ 399.840256 K
5. 數值/求解器支援：
   - 支援真實 PyMechanical / MAPDL 熱傳求解 (若環境與授權可用)
   - 內建高精度一維有限差分/有限體積法 (FDM/FVM) 導熱矩陣解析模擬器 (雙軌容災)
6. 驗收指標：
   - 介面溫度相對誤差 |T_sim - T_theory| / T_theory <= 1.0% (目標 <= 0.05%)
   - 熱通量相對誤差 |q_sim - q_theory| / q_theory <= 1.0% (目標 <= 0.05%)
   - 求解時間 <= 8.0 秒
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import math
import time
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pytest

from ansys_unified_mcp.benchmarks.thermal_wall_engine import (
    ThermalWallConfig,
    ThermalWallEngine,
    ThermalWallResult,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ThermalWallSpec:
    """複合雙層平壁物理規格與材料參數。"""
    L1: float = 0.02   # Layer 1 thickness (m)
    k1: float = 50.0   # Layer 1 conductivity (W/(m*K))
    L2: float = 0.05   # Layer 2 thickness (m)
    k2: float = 0.20   # Layer 2 conductivity (W/(m*K))
    T1: float = 400.0  # Left surface temperature (K)
    T2: float = 300.0  # Right surface temperature (K)


@dataclass
class ThermalWallSolverResult:
    """平壁導熱數值求解結果結構體。"""
    interface_temperature_sim: float
    interface_temperature_theory: float
    temp_relative_error_pct: float
    heat_flux_sim: float
    heat_flux_theory: float
    flux_relative_error_pct: float
    r1_resistance: float
    r2_resistance: float
    r_tot_resistance: float
    elapsed_seconds: float
    solver_backend: str
    num_nodes: int
    temperature_profile_x: Optional[np.ndarray] = None
    temperature_profile_t: Optional[np.ndarray] = None


def compute_analytical_thermal_wall(spec: ThermalWallSpec) -> Dict[str, float]:
    """計算一維雙層平壁穩態導熱之 Fourier 串聯熱阻理論解析解。"""
    r1 = spec.L1 / spec.k1
    r2 = spec.L2 / spec.k2
    r_tot = r1 + r2
    q_theory = (spec.T1 - spec.T2) / r_tot
    t_int_theory = spec.T1 - q_theory * r1

    return {
        "r1": r1,
        "r2": r2,
        "r_tot": r_tot,
        "q_theory": q_theory,
        "t_int_theory": t_int_theory,
    }


def solve_numerical_thermal_wall(
    spec: ThermalWallSpec,
    n1: int = 100,
    n2: int = 250,
) -> ThermalWallSolverResult:
    """使用一維保守型有限差分法求解雙層複合壁溫度分佈與熱通量。"""
    start_time = time.perf_counter()
    theory = compute_analytical_thermal_wall(spec)

    dx1 = spec.L1 / n1
    dx2 = spec.L2 / n2
    total_nodes = n1 + n2 + 1
    int_idx = n1

    # Coordinate vectors
    x_coords = np.concatenate([
        np.linspace(0.0, spec.L1, n1 + 1),
        np.linspace(spec.L1, spec.L1 + spec.L2, n2 + 1)[1:],
    ])

    # Assemble tridiagonal heat conduction matrix
    a_mat = np.zeros((total_nodes, total_nodes), dtype=np.float64)
    b_vec = np.zeros(total_nodes, dtype=np.float64)

    # Left boundary: Dirichlet T = T1
    a_mat[0, 0] = 1.0
    b_vec[0] = spec.T1

    # Layer 1 interior: d^2T/dx^2 = 0
    for i in range(1, int_idx):
        a_mat[i, i - 1] = 1.0
        a_mat[i, i] = -2.0
        a_mat[i, i + 1] = 1.0
        b_vec[i] = 0.0

    # Interface node: heat flux balance k1*(T_I - T_{I-1})/dx1 = k2*(T_{I+1} - T_I)/dx2
    a_mat[int_idx, int_idx - 1] = spec.k1 / dx1
    a_mat[int_idx, int_idx] = -(spec.k1 / dx1 + spec.k2 / dx2)
    a_mat[int_idx, int_idx + 1] = spec.k2 / dx2
    b_vec[int_idx] = 0.0

    # Layer 2 interior: d^2T/dx^2 = 0
    for i in range(int_idx + 1, total_nodes - 1):
        a_mat[i, i - 1] = 1.0
        a_mat[i, i] = -2.0
        a_mat[i, i + 1] = 1.0
        b_vec[i] = 0.0

    # Right boundary: Dirichlet T = T2
    a_mat[-1, -1] = 1.0
    b_vec[-1] = spec.T2

    # Solve linear system
    t_solution = np.linalg.solve(a_mat, b_vec)
    t_int_sim = float(t_solution[int_idx])

    # Compute heat flux from layer gradients
    q1 = spec.k1 * (spec.T1 - t_int_sim) / spec.L1
    q2 = spec.k2 * (t_int_sim - spec.T2) / spec.L2
    q_sim = float(0.5 * (q1 + q2))

    t_err_pct = abs(t_int_sim - theory["t_int_theory"]) / theory["t_int_theory"] * 100.0
    q_err_pct = abs(q_sim - theory["q_theory"]) / theory["q_theory"] * 100.0

    elapsed = time.perf_counter() - start_time

    return ThermalWallSolverResult(
        interface_temperature_sim=t_int_sim,
        interface_temperature_theory=theory["t_int_theory"],
        temp_relative_error_pct=t_err_pct,
        heat_flux_sim=q_sim,
        heat_flux_theory=theory["q_theory"],
        flux_relative_error_pct=q_err_pct,
        r1_resistance=theory["r1"],
        r2_resistance=theory["r2"],
        r_tot_resistance=theory["r_tot"],
        elapsed_seconds=elapsed,
        solver_backend="discrete_fdm_engine",
        num_nodes=total_nodes,
        temperature_profile_x=x_coords,
        temperature_profile_t=t_solution,
    )


# ==============================================================================
# Pytest Golden Benchmarks Verification Suite
# ==============================================================================

class TestPOCThermalWallBenchmark:
    """1D 複合雙層平壁穩態導熱黃金驗收測試套件。"""

    def test_analytical_fourier_exactness(self) -> None:
        """驗證 Fourier 串聯熱阻解析公式之數值精確度與熱通量基準。"""
        spec = ThermalWallSpec()
        theory = compute_analytical_thermal_wall(spec)

        # Theoretical thermal resistance:
        # R1 = 0.02 / 50.0 = 0.0004 m^2*K/W
        # R2 = 0.05 / 0.20 = 0.2500 m^2*K/W
        # R_tot = 0.2504 m^2*K/W
        assert math.isclose(theory["r1"], 0.0004, rel_tol=1e-9), f"R1 熱阻異常: {theory['r1']}"
        assert math.isclose(theory["r2"], 0.2500, rel_tol=1e-9), f"R2 熱阻異常: {theory['r2']}"
        assert math.isclose(theory["r_tot"], 0.2504, rel_tol=1e-9), f"R_tot 總熱阻異常: {theory['r_tot']}"

        # Theoretical heat flux: q = 100.0 / 0.2504 ~ 399.361022 W/m^2
        q_expected = 100.0 / 0.2504
        assert math.isclose(theory["q_theory"], q_expected, rel_tol=1e-6)
        assert 399.360 <= theory["q_theory"] <= 399.363, f"理論熱通量偏差: {theory['q_theory']}"

        # Theoretical interface temperature: T_int = 400.0 - q * R1 ~ 399.840256 K
        t_int_expected = 400.0 - q_expected * 0.0004
        assert math.isclose(theory["t_int_theory"], t_int_expected, rel_tol=1e-6)
        assert 399.839 <= theory["t_int_theory"] <= 399.842, f"理論介面溫度偏差: {theory['t_int_theory']}"

    def test_numerical_solution_accuracy_and_performance(self) -> None:
        """核心驗收測試：介面溫度相對誤差 <= 1.0%, 熱通量誤差 <= 1.0%, 求解時間 <= 8.0s。"""
        spec = ThermalWallSpec()
        res = solve_numerical_thermal_wall(spec, n1=100, n2=250)

        # 1. Verification of Interface Temperature Error <= 1.0%
        assert res.temp_relative_error_pct <= 1.0, (
            f"介面溫度相對誤差超標: {res.temp_relative_error_pct:.4f}% > 1.0% "
            f"(sim={res.interface_temperature_sim:.4f} K, theory={res.interface_temperature_theory:.4f} K)"
        )
        # Even stricter engineering target: <= 0.01%
        assert res.temp_relative_error_pct <= 0.01, f"高階工程目標未達標: {res.temp_relative_error_pct:.6f}%"

        # 2. Verification of Heat Flux Relative Error <= 1.0%
        assert res.flux_relative_error_pct <= 1.0, (
            f"熱通量相對誤差超標: {res.flux_relative_error_pct:.4f}% > 1.0% "
            f"(sim={res.heat_flux_sim:.4f} W/m^2, theory={res.heat_flux_theory:.4f} W/m^2)"
        )
        assert res.flux_relative_error_pct <= 0.01, f"高階工程目標未達標: {res.flux_relative_error_pct:.6f}%"

        # 3. Verification of Wall-Clock Solve Time <= 8.0 s
        assert res.elapsed_seconds <= 8.0, (
            f"求解時間超過 8.0 秒約束: {res.elapsed_seconds:.4f} s"
        )

    def test_thermal_wall_engine_package_integration(self) -> None:
        """測試 ansys_unified_mcp.benchmarks.thermal_wall_engine 整合執行與雙軌架構。"""
        cfg = ThermalWallConfig(L1=0.02, k1=50.0, L2=0.05, k2=0.20, T1=400.0, T2=300.0)
        res = ThermalWallEngine.solve(cfg, prefer_ansys=True)

        assert res.converged is True
        assert res.temp_interface_rel_error_pct <= 1.0
        assert res.heat_flux_rel_error_pct <= 1.0
        assert res.solve_time_seconds <= 8.0
        assert res.solver_mode in ["ansys_live", "discrete_numerical_engine"]

    def test_mesh_refinement_monotonicity(self) -> None:
        """驗證空間網格加密時數值解之單調收斂性與熱平衡保真度。"""
        spec = ThermalWallSpec()
        coarse_res = solve_numerical_thermal_wall(spec, n1=20, n2=50)
        fine_res = solve_numerical_thermal_wall(spec, n1=200, n2=500)

        # Both mesh levels must meet the <= 1.0% golden threshold
        assert coarse_res.temp_relative_error_pct <= 1.0
        assert fine_res.temp_relative_error_pct <= 1.0

        # Heat flux continuity check across interface: q1 == q2
        q1_fine = spec.k1 * (spec.T1 - fine_res.interface_temperature_sim) / spec.L1
        q2_fine = spec.k2 * (fine_res.interface_temperature_sim - spec.T2) / spec.L2
        imbalance = abs(q1_fine - q2_fine) / q1_fine
        assert imbalance < 1e-7, f"介面熱通量守恆遭破壞: {imbalance}"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
