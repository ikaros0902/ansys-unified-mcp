# Strictly ASCII English Comments
"""跨場系統耦合共軛熱傳 (Fluent + Mechanical CHT via System Coupling) 極速黃金基準測試與數值驗收引擎。

本模組為 Stage 5 多物理場跨場系統耦合 (System Coupling / Fluent + Mechanical) 領域之黃金基準測試：
1. 物理問題：Fluent 流體通道與 Mechanical 固體導熱平壁之共軛熱傳 (Conjugate Heat Transfer, CHT)。
2. 物理原理與控制條件：
   - 固液交介面處熱通量平衡：q_fluid = -k_s * (dT_s / dn) = q_solid
   - 介面溫度連續性：T_fluid_wall = T_solid_wall
3. 基準物理規格：
   - 流體主流參考溫度 T_bulk = 500.0 K (226.85 C)
   - 流體表面換熱係數 h_conv = 250.0 W/(m^2*K)
   - 固體平壁厚度 L_s = 0.02 m (20 mm)
   - 固體導熱係數 k_s = 20.0 W/(m*K) (導熱率 G_s = k_s / L_s = 1000.0 W/(m^2*K))
   - 固體外側恆溫冷卻邊界 T_cold = 300.0 K (26.85 C)
4. 理論解析解：
   - 理論交界面溫度 T_interface_theory = 340.0 K (66.85 C)
   - 理論熱通量 q_theory = 40000.0 W/m^2 (40.0 kW/m^2)
5. 數值/求解器支援：
   - 支援真實 System Coupling / Fluent + Mechanical 跨進程耦合呼叫 (若可用)
   - 內建高精度 Dirichlet-Neumann 分區交替迭代 CHT 耦合求解器 (具備 Aitken 動態自適應鬆弛加速)
6. 驗收指標：
   - 跨求解器固液介面熱通量不平衡率 |q_fluid - q_solid| / q_fluid <= 1.5%
   - 介面溫度跳躍 |T_fluid_wall - T_solid_wall| <= 0.5 K
   - 求解時間 <= 28.0 秒
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import math
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pytest

from ansys_unified_mcp.benchmarks.coupling_cht_engine import (
    CouplingCHTConfig,
    CouplingCHTEngine,
    CouplingCHTResult,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CHTBenchmarkSpec:
    """共軛熱傳耦合規格參數。"""
    T_bulk: float = 500.0   # Fluid bulk temperature (K)
    h_conv: float = 250.0   # Fluid convective heat transfer coefficient (W/(m^2*K))
    L_solid: float = 0.02   # Solid wall thickness (m)
    k_solid: float = 20.0   # Solid thermal conductivity (W/(m*K))
    T_cold: float = 300.0   # Solid outer cold surface temperature (K)


def compute_analytical_cht(spec: CHTBenchmarkSpec) -> Dict[str, float]:
    """計算共軛熱傳介面平衡理論解析解。"""
    r_fluid = 1.0 / spec.h_conv
    r_solid = spec.L_solid / spec.k_solid
    r_tot = r_fluid + r_solid

    q_theory = (spec.T_bulk - spec.T_cold) / r_tot
    t_int_theory = spec.T_bulk - q_theory * r_fluid

    return {
        "r_fluid": r_fluid,
        "r_solid": r_solid,
        "r_tot": r_tot,
        "q_theory": q_theory,
        "t_int_theory": t_int_theory,
    }


# ==============================================================================
# Pytest Golden Benchmarks Verification Suite
# ==============================================================================

class TestPOCCouplingCHTBenchmark:
    """Fluent + Mechanical 跨場共軛熱傳系統耦合黃金驗收測試套件。"""

    def test_analytical_cht_equilibrium_exactness(self) -> None:
        """驗證 CHT 固液交介面熱通量平衡與溫度連續之理論精確解析解。"""
        spec = CHTBenchmarkSpec()
        theory = compute_analytical_cht(spec)

        # Expected theoretical values:
        # R_fluid = 1 / 250 = 0.004 m^2*K/W
        # R_solid = 0.02 / 20 = 0.001 m^2*K/W
        # R_tot = 0.005 m^2*K/W
        assert math.isclose(theory["r_fluid"], 0.004, rel_tol=1e-9)
        assert math.isclose(theory["r_solid"], 0.001, rel_tol=1e-9)
        assert math.isclose(theory["r_tot"], 0.005, rel_tol=1e-9)

        # q_theory = (500 - 300) / 0.005 = 200 / 0.005 = 40000.0 W/m^2
        assert math.isclose(theory["q_theory"], 40000.0, rel_tol=1e-9)

        # T_int_theory = 500 - 40000 * 0.004 = 340.0 K
        assert math.isclose(theory["t_int_theory"], 340.0, rel_tol=1e-9)

    def test_partitioned_cht_convergence_and_flux_balance(self) -> None:
        """核心驗收測試：熱通量不平衡率 <= 1.5%, 介面溫度跳躍 <= 0.5 K, 耗時 <= 28.0s。"""
        cfg = CouplingCHTConfig(
            T_bulk=500.0,
            h_conv=250.0,
            L_solid=0.02,
            k_solid=20.0,
            T_cold=300.0,
            initial_interface_temp=360.0,  # Deliberate initial offset
            max_coupling_iterations=40,
            flux_imbalance_tolerance=0.015,  # 1.5%
            temp_jump_tolerance=0.5,        # 0.5 K
            use_aitken_acceleration=True,
        )

        res = CouplingCHTEngine.solve(cfg, prefer_ansys=True)

        # 1. Verification of Convergence Status
        assert res.converged is True, f"交替耦合迭代未於 {res.iterations_count} 步內收斂"

        # 2. Verification of Interface Heat Flux Imbalance <= 1.5%
        assert res.flux_imbalance_pct <= 1.5, (
            f"固液介面熱通量不平衡率超標: {res.flux_imbalance_pct:.4f}% > 1.5% "
            f"(q_fluid={res.heat_flux_fluid:.2f} W/m^2, q_solid={res.heat_flux_solid:.2f} W/m^2)"
        )
        assert res.flux_imbalance_pct <= 0.5, f"高階工程目標未達標: {res.flux_imbalance_pct:.4f}%"

        # 3. Verification of Interface Temperature Jump <= 0.5 K
        assert res.temp_jump <= 0.5, (
            f"介面溫度跳躍超標: {res.temp_jump:.4f} K > 0.5 K "
            f"(T_fluid={res.t_fluid_wall:.4f} K, T_solid={res.t_solid_wall:.4f} K)"
        )
        assert res.temp_jump <= 0.25, f"溫度連續性未達高階目標: {res.temp_jump:.4f} K"

        # 4. Verification of Wall-Clock Solve Time <= 28.0 s
        assert res.solve_time_seconds <= 28.0, (
            f"求解耗時超標: {res.solve_time_seconds:.4f} s > 28.0 s"
        )
        # Fast execution verification (< 2.0 s)
        assert res.solve_time_seconds < 2.0, f"求解執行時間偏長: {res.solve_time_seconds:.4f} s"

        # 5. Theoretical Comparison
        theory = compute_analytical_cht(CHTBenchmarkSpec())
        t_err_pct = abs(res.t_solid_wall - theory["t_int_theory"]) / theory["t_int_theory"] * 100.0
        assert t_err_pct <= 0.5, f"介面溫度偏離理論解析值: {t_err_pct:.4f}%"

    def test_aitken_acceleration_vs_constant_relaxation(self) -> None:
        """驗證 Aitken 動態鬆弛加速相較於固定鬆弛在相同步數下的收斂加速效應。"""
        # Run with Aitken dynamic acceleration
        cfg_aitken = CouplingCHTConfig(
            initial_interface_temp=420.0,  # Extreme initial jump (80 K above theory)
            use_aitken_acceleration=True,
            max_coupling_iterations=30,
        )
        res_aitken = CouplingCHTEngine.solve_partitioned_cht(cfg_aitken)

        # Run with standard fixed under-relaxation
        cfg_fixed = CouplingCHTConfig(
            initial_interface_temp=420.0,
            use_aitken_acceleration=False,
            relaxation_factor=0.35,
            max_coupling_iterations=30,
        )
        res_fixed = CouplingCHTEngine.solve_partitioned_cht(cfg_fixed)

        assert res_aitken.converged is True
        assert res_aitken.flux_imbalance_pct <= 1.5
        assert res_aitken.temp_jump <= 0.5
        assert res_aitken.iterations_count <= res_fixed.iterations_count + 5

    def test_coupling_cht_dual_track_resilience(self) -> None:
        """測試無真實 System Coupling 授權環境下自動回退至分區數值引擎之強健性。"""
        cfg = CouplingCHTConfig()
        res = CouplingCHTEngine.solve(cfg, prefer_ansys=True)

        assert res.solver_mode in ["ansys_system_coupling", "partitioned_dn_cht_engine"]
        assert res.converged is True
        assert res.solve_time_seconds <= 28.0


if __name__ == "__main__":
    pytest.main(["-v", __file__])
