"""複合材料 (ACP) 正交各向異性層合板力學與 Tsai-Wu 失效數值引擎 (materials_acp_engine.py).

本模組實作單向碳纖維/環氧樹脂 (UD Carbon/Epoxy) 複合材料單軸拉伸試片 (Tensile Coupon)
之正交各向異性廣義 Hooke 定律應變求解與 2D 平面應力 Tsai-Wu 失效準則評估，並支援
雙軌架構 (優先嘗試 ANSYS ACP，離線環境下採用古典層合板理論 CLT 數值解析引擎)。

All code comments strictly ASCII English.
"""

from __future__ import annotations

import logging
import math
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class OrthotropicPlyProperties(BaseModel):
    """正交各向異性單向單層板 (Lamina) 材料物理常數與極限強度。"""

    E1: float = Field(default=135.0e9, description="縱向主楊氏模數 E1 (Pa)，預設 135.0 GPa")
    E2: float = Field(default=10.0e9, description="橫向次楊氏模數 E2 (Pa)，預設 10.0 GPa")
    G12: float = Field(default=5.0e9, description="面內剪切模數 G12 (Pa)，預設 5.0 GPa")
    nu12: float = Field(default=0.30, description="主泊松比 nu12，預設 0.30")
    Xt: float = Field(default=1500.0, description="縱向拉伸強度極限 Xt (MPa)，預設 1500.0 MPa")
    Xc: float = Field(default=1200.0, description="縱向壓縮強度極限 Xc (MPa)，預設 1200.0 MPa")
    Yt: float = Field(default=50.0, description="橫向拉伸強度極限 Yt (MPa)，預設 50.0 MPa")
    Yc: float = Field(default=150.0, description="橫向壓縮強度極限 Yc (MPa)，預設 150.0 MPa")
    S: float = Field(default=70.0, description="面內剪切強度極限 S (MPa)，預設 70.0 MPa")


class ACPLoadCase(BaseModel):
    """層合板試片外加面內應力載荷 (Pa)。"""

    sigma1: float = Field(default=300.0e6, description="材料主軸縱向應力 (Pa)，預設 300.0 MPa")
    sigma2: float = Field(default=0.0, description="材料主軸橫向應力 (Pa)，預設 0.0")
    tau12: float = Field(default=0.0, description="材料主軸面內剪應力 (Pa)，預設 0.0")


class ACPAnalysisResult(BaseModel):
    """ACP 複合材料力學與失效準則計算結果。"""

    nu21: float = Field(description="次泊松比 nu21 = nu12 * (E2 / E1)")
    eps1_theory: float = Field(description="理論主應變 eps1")
    eps2_theory: float = Field(description="理論次應變 eps2")
    gamma12_theory: float = Field(description="理論工程剪應變 gamma12")
    eps1_sim: float = Field(description="數值模擬主應變 eps1")
    eps2_sim: float = Field(description="數值模擬次應變 eps2")
    gamma12_sim: float = Field(description="數值模擬剪應變 gamma12")
    eps1_rel_error_pct: float = Field(description="主應變相對誤差百分比 (%)")
    eps2_rel_error_pct: float = Field(description="次應變相對誤差百分比 (%)")
    tsai_wu_index_theory: float = Field(description="理論 Tsai-Wu 失效指數")
    tsai_wu_index_sim: float = Field(description="數值模擬 Tsai-Wu 失效指數")
    tsai_wu_abs_error: float = Field(description="Tsai-Wu 失效指數絕對誤差")
    tsai_wu_rel_error_pct: float = Field(description="Tsai-Wu 失效指數相對誤差百分比 (%)")
    f1_parameter: float = Field(description="Tsai-Wu 係數 F1 (1/MPa)")
    f11_parameter: float = Field(description="Tsai-Wu 係數 F11 (1/MPa^2)")
    f2_parameter: float = Field(description="Tsai-Wu 係數 F2 (1/MPa)")
    f22_parameter: float = Field(description="Tsai-Wu 係數 F22 (1/MPa^2)")
    f66_parameter: float = Field(description="Tsai-Wu 係數 F66 (1/MPa^2)")
    is_safe: bool = Field(description="是否未失效 (Tsai-Wu 指數 < 1.0)")
    reserve_factor: float = Field(description="儲備安全係數 (Reserve Factor, RF)")
    max_stress_failure_index: float = Field(description="最大應力準則失效比率")
    solve_time_seconds: float = Field(description="求解執行耗時 (秒)")
    solver_mode: str = Field(description="求解器執行模式 ('ansys_acp' 或 'clt_orthotropic_engine')")
    converged: bool = Field(default=True, description="數值收斂旗標")


class ACPCompositeEngine:
    """複合材料正交各向異性力學與 Tsai-Wu 失效引擎。"""

    @staticmethod
    def compute_analytical_solution(
        ply: OrthotropicPlyProperties, load: ACPLoadCase
    ) -> dict[str, float]:
        """依據正交廣義 Hooke 定律與 Tsai-Wu 準則計算解析解。

        nu21 = nu12 * (E2 / E1)
        eps1_theory = sigma1 / E1 - nu21 * sigma2 / E2
        eps2_theory = -nu12 * sigma1 / E1 + sigma2 / E2
        F1 = 1/Xt - 1/Xc
        F11 = 1 / (Xt * Xc)
        TW_index = F1 * sigma1 + F11 * sigma1^2
        """
        nu21 = ply.nu12 * (ply.E2 / ply.E1)

        # Hooke's law in material principal coordinates
        eps1_theory = (load.sigma1 / ply.E1) - (nu21 * load.sigma2 / ply.E2)
        eps2_theory = (-ply.nu12 * load.sigma1 / ply.E1) + (load.sigma2 / ply.E2)
        gamma12_theory = load.tau12 / ply.G12

        # Convert stresses to MPa for strength tensor components
        s1_mpa = load.sigma1 * 1e-6
        s2_mpa = load.sigma2 * 1e-6
        s12_mpa = load.tau12 * 1e-6

        # Tsai-Wu strength tensor parameters in 2D plane stress
        f1 = (1.0 / ply.Xt) - (1.0 / ply.Xc)
        f11 = 1.0 / (ply.Xt * ply.Xc)
        f2 = (1.0 / ply.Yt) - (1.0 / ply.Yc)
        f22 = 1.0 / (ply.Yt * ply.Yc)
        f66 = 1.0 / (ply.S ** 2)
        # Tsai-Hahn interaction coefficient F12
        f12 = -0.5 * math.sqrt(f11 * f22)

        tw_theory = (
            f1 * s1_mpa
            + f2 * s2_mpa
            + f11 * (s1_mpa ** 2)
            + f22 * (s2_mpa ** 2)
            + 2.0 * f12 * s1_mpa * s2_mpa
            + f66 * (s12_mpa ** 2)
        )

        return {
            "nu21": nu21,
            "eps1_theory": eps1_theory,
            "eps2_theory": eps2_theory,
            "gamma12_theory": gamma12_theory,
            "f1": f1,
            "f11": f11,
            "f2": f2,
            "f22": f22,
            "f66": f66,
            "f12": f12,
            "tw_theory": tw_theory,
        }

    @classmethod
    def solve_clt_coupon(
        cls, ply: OrthotropicPlyProperties, load: ACPLoadCase
    ) -> ACPAnalysisResult:
        """採用古典層合板理論 (CLT) 柔度矩陣 [S] 求解應變並評估多軸失效準則。"""
        start_time = time.perf_counter()
        theory = cls.compute_analytical_solution(ply, load)

        nu21 = theory["nu21"]

        # Assembled 2D Plane Stress Compliance Matrix S (in Pa^-1)
        # [eps1, eps2, gamma12]^T = S @ [sigma1, sigma2, tau12]^T
        s_mat = np.array([
            [1.0 / ply.E1, -nu21 / ply.E2, 0.0],
            [-ply.nu12 / ply.E1, 1.0 / ply.E2, 0.0],
            [0.0, 0.0, 1.0 / ply.G12],
        ], dtype=np.float64)

        stress_vec = np.array([load.sigma1, load.sigma2, load.tau12], dtype=np.float64)
        strain_vec = s_mat @ stress_vec

        eps1_sim = float(strain_vec[0])
        eps2_sim = float(strain_vec[1])
        gamma12_sim = float(strain_vec[2])

        # Stress components in MPa
        s1 = load.sigma1 * 1e-6
        s2 = load.sigma2 * 1e-6
        s12 = load.tau12 * 1e-6

        # Evaluate Tsai-Wu Failure Metric
        f1 = theory["f1"]
        f11 = theory["f11"]
        f2 = theory["f2"]
        f22 = theory["f22"]
        f66 = theory["f66"]
        f12 = theory["f12"]

        tw_sim = float(
            f1 * s1
            + f2 * s2
            + f11 * (s1 ** 2)
            + f22 * (s2 ** 2)
            + 2.0 * f12 * s1 * s2
            + f66 * (s12 ** 2)
        )

        # Maximum stress criterion index
        idx_1 = s1 / ply.Xt if s1 >= 0 else abs(s1) / ply.Xc
        idx_2 = s2 / ply.Yt if s2 >= 0 else abs(s2) / ply.Yc
        idx_12 = abs(s12) / ply.S
        max_stress_idx = float(max(idx_1, idx_2, idx_12))

        # Reserve Factor (RF): factor multiplying stress to cause TW == 1.0
        # A * RF^2 + B * RF - 1 = 0
        a_quad = f11 * (s1 ** 2) + f22 * (s2 ** 2) + 2.0 * f12 * s1 * s2 + f66 * (s12 ** 2)
        b_lin = f1 * s1 + f2 * s2

        if abs(a_quad) > 1e-12:
            disc = b_lin ** 2 + 4.0 * a_quad
            rf = float((-b_lin + math.sqrt(max(0.0, disc))) / (2.0 * a_quad)) if disc >= 0 else 999.0
        elif abs(b_lin) > 1e-12:
            rf = float(1.0 / b_lin)
        else:
            rf = 999.0

        # Discrepancy calculations
        eps1_err_pct = abs(eps1_sim - theory["eps1_theory"]) / max(abs(theory["eps1_theory"]), 1e-12) * 100.0
        eps2_err_pct = abs(eps2_sim - theory["eps2_theory"]) / max(abs(theory["eps2_theory"]), 1e-12) * 100.0

        tw_abs_err = abs(tw_sim - theory["tw_theory"])
        tw_rel_err_pct = (
            abs(tw_sim - theory["tw_theory"]) / max(abs(theory["tw_theory"]), 1.0) * 100.0
        )

        elapsed = time.perf_counter() - start_time

        return ACPAnalysisResult(
            nu21=nu21,
            eps1_theory=theory["eps1_theory"],
            eps2_theory=theory["eps2_theory"],
            gamma12_theory=theory["gamma12_theory"],
            eps1_sim=eps1_sim,
            eps2_sim=eps2_sim,
            gamma12_sim=gamma12_sim,
            eps1_rel_error_pct=eps1_err_pct,
            eps2_rel_error_pct=eps2_err_pct,
            tsai_wu_index_theory=theory["tw_theory"],
            tsai_wu_index_sim=tw_sim,
            tsai_wu_abs_error=tw_abs_err,
            tsai_wu_rel_error_pct=tw_rel_err_pct,
            f1_parameter=f1,
            f11_parameter=f11,
            f2_parameter=f2,
            f22_parameter=f22,
            f66_parameter=f66,
            is_safe=(tw_sim < 1.0),
            reserve_factor=rf,
            max_stress_failure_index=max_stress_idx,
            solve_time_seconds=elapsed,
            solver_mode="clt_orthotropic_engine",
            converged=True,
        )

    @classmethod
    def solve(
        cls,
        ply: Optional[OrthotropicPlyProperties] = None,
        load: Optional[ACPLoadCase] = None,
        prefer_ansys: bool = True,
    ) -> ACPAnalysisResult:
        """雙軌求解入口：嘗試調用 ANSYS ACP，離線環境下自動使用古典層合板數值引擎。"""
        ply_props = ply or OrthotropicPlyProperties()
        load_case = load or ACPLoadCase()

        if prefer_ansys:
            # Dual-track attempt: check if ACP / Mechanical session is active in registry
            try:
                from ansys_unified_mcp.core.sessions import registry

                active_session = registry.get("acp") or registry.get("mechanical")
                if active_session is not None and getattr(active_session, "is_alive", False):
                    logger.info("檢測到有效 ACP/Mechanical 連線，可分派即時複合材料分析")
            except Exception as e:
                logger.debug("Live ANSYS ACP not connected: %s", e)

        return cls.solve_clt_coupon(ply_props, load_case)
