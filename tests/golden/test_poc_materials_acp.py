# Strictly ASCII English Comments
"""正交各向異性複合材料單向層合板單軸拉伸 (ACP 0 deg UD Carbon/Epoxy Tensile Coupon) 極速黃金基準測試與數值驗收引擎。

本模組為 Stage 5 複合材料力學 (Ansys ACP / Composite PrepPost) 領域之黃金基準測試：
1. 物理問題：單向碳纖維/環氧樹脂 (UD Carbon/Epoxy) 0度單向複合材料試片單軸拉伸變形與 Tsai-Wu 失效分析。
2. 材料工程規格：
   - 縱向主楊氏模量 E1 = 135.0 GPa (135.0e9 Pa)
   - 橫向次楊氏模量 E2 = 10.0 GPa (10.0e9 Pa)
   - 面內剪切模量 G12 = 5.0 GPa (5.0e9 Pa)
   - 主泊松比 nu12 = 0.30
   - 次泊松比 nu21 = nu12 * (E2 / E1) = 0.02222222
   - 強度極限：
     - 縱向拉伸強度 Xt = 1500.0 MPa
     - 縱向壓縮強度 Xc = 1200.0 MPa
     - 橫向拉伸強度 Yt = 50.0 MPa
     - 橫向壓縮強度 Yc = 150.0 MPa
     - 面內剪切強度 S = 70.0 MPa
3. 載荷條件：
   - 單軸拉伸應力 sigma1 = 300.0 MPa (300.0e6 Pa), sigma2 = 0, tau12 = 0
4. 理論解析解 (正交廣義 Hooke 定律 + Tsai-Wu 準則)：
   - 軸向主應變 eps1_theory = sigma1 / E1 = 0.0022222 (2222.2 microstrain)
   - 橫向泊松應變 eps2_theory = -nu12 * eps1_theory = -0.00066667 (-666.7 microstrain)
   - Tsai-Wu 失效張量係數 (2D 平面應力)：
     F1 = 1/Xt - 1/Xc = 1/1500 - 1/1200 = -1.6667e-4 MPa^-1
     F11 = 1 / (Xt * Xc) = 1 / (1500 * 1200) = 5.5556e-7 MPa^-2
     TW_index_theory = F1 * sigma1 + F11 * sigma1**2 = -0.0500 + 0.0500 = 0.0000 (安全，無失效)
5. 數值/求解器支援：
   - 支援真實 Ansys ACP 求解器呼叫 (若可用)
   - 內建高精度古典層合板理論 (CLT) 柔度/剛度矩陣與張量多軸失效解析模擬器 (雙軌容災)
6. 驗收指標：
   - 軸向應變 eps1 相對誤差 <= 1.0% (目標 <= 0.05%)
   - 橫向應變 eps2 相對誤差 <= 1.0% (目標 <= 0.05%)
   - Tsai-Wu 指數絕對誤差 <= 0.015 (或相對誤差 <= 1.5%)
   - 求解時間 <= 6.0 秒
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import math
import time
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pytest

from ansys_unified_mcp.benchmarks.materials_acp_engine import (
    ACPAnalysisResult,
    ACPCompositeEngine,
    ACPLoadCase,
    OrthotropicPlyProperties,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UDCarbonEpoxySpec:
    """單向碳纖維/環氧樹脂物理常數規格。"""
    E1: float = 135.0e9   # Longitudinal modulus (Pa)
    E2: float = 10.0e9    # Transverse modulus (Pa)
    G12: float = 5.0e9    # In-plane shear modulus (Pa)
    nu12: float = 0.30    # Major Poisson's ratio
    Xt: float = 1500.0    # Longitudinal tensile strength (MPa)
    Xc: float = 1200.0    # Longitudinal compressive strength (MPa)
    Yt: float = 50.0      # Transverse tensile strength (MPa)
    Yc: float = 150.0     # Transverse compressive strength (MPa)
    S: float = 70.0       # Shear strength (MPa)


def compute_analytical_acp(spec: UDCarbonEpoxySpec, sigma1_pa: float = 300.0e6) -> Dict[str, float]:
    """計算正交各向異性層合板之廣義 Hooke 定律應變與 Tsai-Wu 解析解。"""
    nu21 = spec.nu12 * (spec.E2 / spec.E1)
    eps1_theory = sigma1_pa / spec.E1
    eps2_theory = -spec.nu12 * eps1_theory

    s1_mpa = sigma1_pa * 1e-6
    f1 = (1.0 / spec.Xt) - (1.0 / spec.Xc)
    f11 = 1.0 / (spec.Xt * spec.Xc)
    tw_theory = f1 * s1_mpa + f11 * (s1_mpa ** 2)

    return {
        "nu21": nu21,
        "eps1_theory": eps1_theory,
        "eps2_theory": eps2_theory,
        "f1": f1,
        "f11": f11,
        "tw_theory": tw_theory,
    }


# ==============================================================================
# Pytest Golden Benchmarks Verification Suite
# ==============================================================================

class TestPOCMaterialsACPBenchmark:
    """ACP 正交各向異性複合材料與 Tsai-Wu 失效準則黃金驗收測試套件。"""

    def test_analytical_hooke_and_tsai_wu_exactness(self) -> None:
        """驗證正交廣義 Hooke 定律與 Tsai-Wu 2D 平面應力理論張量係數之精確解析解。"""
        spec = UDCarbonEpoxySpec()
        theory = compute_analytical_acp(spec, sigma1_pa=300.0e6)

        # 1. Verification of minor Poisson ratio nu21
        # nu21 = 0.30 * (10 / 135) = 3 / 135 = 0.02222222
        assert math.isclose(theory["nu21"], 2.0 / 90.0, rel_tol=1e-7)

        # 2. Verification of theoretical strains
        # eps1 = 300e6 / 135e9 = 1 / 450 ~ 0.00222222 (2222.22 microstrain)
        assert math.isclose(theory["eps1_theory"], 1.0 / 450.0, rel_tol=1e-7)
        assert 2220.0 <= theory["eps1_theory"] * 1e6 <= 2225.0

        # eps2 = -0.30 * (1 / 450) = -0.00066667 (-666.67 microstrain)
        assert math.isclose(theory["eps2_theory"], -0.30 / 450.0, rel_tol=1e-7)
        assert -668.0 <= theory["eps2_theory"] * 1e6 <= -665.0

        # 3. Verification of Tsai-Wu strength tensor coefficients
        # F1 = 1/1500 - 1/1200 = -1.6666667e-4 MPa^-1
        expected_f1 = (1.0 / 1500.0) - (1.0 / 1200.0)
        assert math.isclose(theory["f1"], expected_f1, rel_tol=1e-9)
        assert math.isclose(theory["f1"], -1.66666667e-4, rel_tol=1e-6)

        # F11 = 1 / (1500 * 1200) = 5.5555556e-7 MPa^-2
        expected_f11 = 1.0 / (1500.0 * 1200.0)
        assert math.isclose(theory["f11"], expected_f11, rel_tol=1e-9)
        assert math.isclose(theory["f11"], 5.55555556e-7, rel_tol=1e-6)

        # 4. Verification of Tsai-Wu Failure Index:
        # F1 * 300 = -0.0500, F11 * (300^2) = +0.0500 => TW = 0.0000 (Safe)
        assert math.isclose(theory["tw_theory"], 0.0, abs_tol=1e-12)

    def test_numerical_acp_solve_accuracy_and_performance(self) -> None:
        """核心驗收測試：軸向應變誤差 <= 1.0%, 橫向應變誤差 <= 1.0%, Tsai-Wu 誤差 <= 0.015, 時間 <= 6.0s。"""
        ply = OrthotropicPlyProperties(
            E1=135.0e9,
            E2=10.0e9,
            G12=5.0e9,
            nu12=0.30,
            Xt=1500.0,
            Xc=1200.0,
            Yt=50.0,
            Yc=150.0,
            S=70.0,
        )
        load = ACPLoadCase(sigma1=300.0e6, sigma2=0.0, tau12=0.0)

        res = ACPCompositeEngine.solve(ply, load, prefer_ansys=True)

        # 1. Verification of Axial Strain eps1 Error <= 1.0%
        assert res.eps1_rel_error_pct <= 1.0, (
            f"軸向應變 eps1 相對誤差超標: {res.eps1_rel_error_pct:.4f}% > 1.0% "
            f"(sim={res.eps1_sim:.8f}, theory={res.eps1_theory:.8f})"
        )
        assert res.eps1_rel_error_pct <= 0.01, f"高階工程目標未達標: {res.eps1_rel_error_pct:.6f}%"

        # 2. Verification of Transverse Strain eps2 Error <= 1.0%
        assert res.eps2_rel_error_pct <= 1.0, (
            f"橫向應變 eps2 相對誤差超標: {res.eps2_rel_error_pct:.4f}% > 1.0% "
            f"(sim={res.eps2_sim:.8f}, theory={res.eps2_theory:.8f})"
        )
        assert res.eps2_rel_error_pct <= 0.01, f"高階工程目標未達標: {res.eps2_rel_error_pct:.6f}%"

        # 3. Verification of Tsai-Wu Failure Index Error <= 0.015 (or rel error <= 1.5%)
        assert res.tsai_wu_abs_error <= 0.015, (
            f"Tsai-Wu 失效指數絕對誤差超標: {res.tsai_wu_abs_error:.6f} > 0.015 "
            f"(sim={res.tsai_wu_index_sim:.6f}, theory={res.tsai_wu_index_theory:.6f})"
        )
        assert res.tsai_wu_abs_error < 1e-9, f"高階精度目標未達標: {res.tsai_wu_abs_error:.12f}"

        # 4. Verification of Wall-Clock Solve Time <= 6.0 s
        assert res.solve_time_seconds <= 6.0, (
            f"ACP 求解耗時超標: {res.solve_time_seconds:.4f} s > 6.0 s"
        )
        assert res.solve_time_seconds < 0.2, f"求解延遲過大: {res.solve_time_seconds:.4f} s"

        # 5. Safety Indicator Check
        assert res.is_safe is True
        assert res.max_stress_failure_index == pytest.approx(0.20, rel=1e-3)  # 300 / 1500 = 0.20

    def test_multiaxial_load_and_failure_envelope(self) -> None:
        """驗證多軸複合載荷下的 Tsai-Wu 橢圓失效曲面正定性。"""
        ply = OrthotropicPlyProperties()

        # Pure transverse load at failure limit Yt = 50 MPa
        load_yt = ACPLoadCase(sigma1=0.0, sigma2=50.0e6, tau12=0.0)
        res_yt = ACPCompositeEngine.solve_clt_coupon(ply, load_yt)
        # At sigma2 = Yt, Tsai-Wu index must be identically 1.0
        # F2 * Yt + F22 * Yt^2 = (1/Yt - 1/Yc)*Yt + (1/(Yt*Yc))*Yt^2 = 1 - Yt/Yc + Yt/Yc = 1.0
        assert math.isclose(res_yt.tsai_wu_index_sim, 1.0, rel_tol=1e-5)

        # Pure shear load at failure limit S = 70 MPa
        load_shear = ACPLoadCase(sigma1=0.0, sigma2=0.0, tau12=70.0e6)
        res_shear = ACPCompositeEngine.solve_clt_coupon(ply, load_shear)
        # At tau12 = S, F66 * S^2 = (1/S^2) * S^2 = 1.0
        assert math.isclose(res_shear.tsai_wu_index_sim, 1.0, rel_tol=1e-5)

    def test_materials_acp_dual_track_resilience(self) -> None:
        """測試無真實 ACP 授權環境下自動切換至 CLT 數值引擎之容災能力。"""
        res = ACPCompositeEngine.solve(prefer_ansys=True)
        assert res.solver_mode in ["ansys_acp", "clt_orthotropic_engine"]
        assert res.converged is True
        assert res.solve_time_seconds <= 6.0


if __name__ == "__main__":
    pytest.main(["-v", __file__])
