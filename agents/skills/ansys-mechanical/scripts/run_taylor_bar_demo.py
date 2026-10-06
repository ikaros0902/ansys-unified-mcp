# -*- coding: utf-8 -*-
"""
模組名稱：run_taylor_bar_demo.py
功能說明：ANSYS Mechanical / LS-DYNA 泰勒桿 (Taylor Bar) 高速衝擊大變形標準範例腳本
技術標準：林明志標準 顯式動力學高速撞擊、動態降伏強度估算與沙漏能佔比驗證規範
單位系統：ton, mm, s, N, MPa (OFHC 銅密度: 8.96e-9 ton/mm^3)
"""

import math
from typing import Dict, Any, List, Optional


class TaylorBarSimulationBuilder:
    """
    泰勒圓柱桿 (Taylor Bar) 高速撞擊剛性靶板分析模型生成器
    """

    def __init__(
        self,
        length_mm: float = 32.4,
        radius_mm: float = 3.2,
        impact_velocity_m_s: float = 227.0,
        density_ton_mm3: float = 8.96e-9,
        youngs_modulus_mpa: float = 1.15e5,
        poisson_ratio: float = 0.31,
        static_yield_mpa: float = 400.0,
        tangent_modulus_mpa: float = 100.0
    ):
        self.l0 = length_mm
        self.r0 = radius_mm
        self.v0 = impact_velocity_m_s * 1000.0  # 換算為 mm/s
        self.density = density_ton_mm3
        self.youngs = youngs_modulus_mpa
        self.poisson = poisson_ratio
        self.sigy = static_yield_mpa
        self.etan = tangent_modulus_mpa
        self.keyword_lines: List[str] = []
        self._build_keyword_deck()

    def _build_keyword_deck(self) -> None:
        """組裝 LS-DYNA / Mechanical 顯式衝擊關鍵字卡片"""
        end_time_s = 8.0e-5  # 80 微秒足夠完成塑性變形與彈性回彈
        dt2ms = -2.0e-8      # 局部質量縮放

        self.keyword_lines.extend([
            "$# ====================================================================",
            "$# 專案名稱: Taylor_Bar_Impact_OFHC_Copper_Demo",
            "$# 自動生成: 林明志標準 泰勒桿高速撞擊大變形模擬生成器",
            f"$# 幾何參數: 長度 L0={self.l0} mm, 半徑 R0={self.r0} mm, 初速 V0={self.v0/1000.0:.1f} m/s",
            "$# 單位系統: ton, mm, s, N, MPa",
            "$# ====================================================================",
            "*KEYWORD",
            "*TITLE",
            "Taylor_Bar_Impact_OFHC_Copper",
            "$",
            "$ ----------------------------------------------------------------------",
            "$ 1. 求解時間與質量縮放控制",
            "$ ----------------------------------------------------------------------",
            "*CONTROL_TERMINATION",
            "$#  endtim    endcyc     dtmin    endeng    rpend",
            f"{end_time_s:10.4e}         0       0.0       0.0       0.0",
            "*CONTROL_TIMESTEP",
            "$#  dtinit    tssfac      isdo    tslimt     dt2ms      lctm     erode     ms1st",
            f"       0.0      0.90         0       0.0{dt2ms:10.2e}         0         0         0",
            "*CONTROL_ENERGY",
            "$#    hgen      rwen    slnten     rylen",
            "         2         2         2         2",
            "*CONTROL_HOURGLASS",
            "$#     ihq        qh",
            "         4      0.10",
            "$",
            "$ ----------------------------------------------------------------------",
            "$ 2. 歷史數據與 D3PLOT 輸出頻率",
            "$ ----------------------------------------------------------------------",
            "*DATABASE_BINARY_D3PLOT",
            "$#      dt      lcdt      beam     npltc    psetid",
            "  1.000e-06         0         0         0         0",
            "*DATABASE_GLSTAT",
            "  5.000e-07",
            "*DATABASE_MATSUM",
            "  5.000e-07",
            "$",
            "$ ----------------------------------------------------------------------",
            "$ 3. 初始撞擊速度 (Z 軸向剛性靶板撞擊)",
            "$ ----------------------------------------------------------------------",
            "*INITIAL_VELOCITY_GENERATION",
            "$#      id      styp     omega        vx        vy        vz      ivat     icid",
            f"         1         2       0.0       0.0       0.0{-self.v0:10.2f}         0         0",
            "$",
            "$ ----------------------------------------------------------------------",
            "$ 4. 理想剛性靶板 (Z=0 平面)",
            "$ ----------------------------------------------------------------------",
            "*RIGIDWALL_PLANAR",
            "$#    nsid      nsid       box       box      dseq      dseq",
            "         0         0         0         0       0.0       0.0",
            "$#      xt        yt        zt        xh        yh        zh      fric       wvel",
            "       0.0       0.0      0.00       0.0       0.0      1.00      0.00       0.0",
            "$",
            "$ ----------------------------------------------------------------------",
            "$ 5. OFHC 無氧銅彈塑性本構模型 (*MAT_024)",
            "$ ----------------------------------------------------------------------",
            "*MAT_PIECEWISE_LINEAR_PLASTICITY",
            "$#     mid        ro         e        pr      sigy      etan      fail      tdel",
            f"         1{self.density:10.2e}{self.youngs:10.2e}{self.poisson:10.3f}{self.sigy:10.2f}{self.etan:10.2f}     0.000     0.000",
            "*END",
            ""
        ])

    def get_keyword_deck(self) -> str:
        """返回完整關鍵字卡片文字"""
        return "\n".join(self.keyword_lines)


# ----------------------------------------------------------------------
# 【判斷力庫】泰勒動態降伏強度估算與結果客觀評估
# ----------------------------------------------------------------------

def estimate_taylor_dynamic_yield(
    length_initial_mm: float,
    length_final_mm: float,
    length_undeformed_mm: float,
    impact_velocity_m_s: float,
    density_ton_mm3: float = 8.96e-9
) -> Dict[str, Any]:
    """
    依據經典泰勒一維衝擊理論 (Taylor Formula) 由撞擊前後幾何尺寸推算動態降伏強度：
    sigma_yd = [rho * v0^2 * (L0 - X)] / [2 * (L0 - Lf) * ln(L0 / X)]
    
    :param length_initial_mm: 撞擊前原始長度 L0 (mm)
    :param length_final_mm: 撞擊後殘餘總長度 Lf (mm)
    :param length_undeformed_mm: 桿件尾端未變形部分長度 X (mm)
    :param impact_velocity_m_s: 撞擊初始速度 V0 (m/s)
    :param density_ton_mm3: 材料密度 (ton/mm^3)
    :return: 包含動態降伏強度及幾何變形評估之字典
    """
    l0 = length_initial_mm
    lf = length_final_mm
    x = length_undeformed_mm
    v0_mm_s = impact_velocity_m_s * 1000.0

    if lf >= l0 or x >= l0 or x <= 0:
        return {"valid": False, "reason": "輸入長度數據違反幾何變形物理約束 (Lf < L0 且 0 < X < L0)"}

    numerator = density_ton_mm3 * (v0_mm_s ** 2) * (l0 - x)
    denominator = 2.0 * (l0 - lf) * math.log(l0 / x)

    if denominator <= 0:
        return {"valid": False, "reason": "分母計算非正數，變形量幾何比例異常"}

    sigma_yd_mpa = numerator / denominator
    mushroom_ratio = (l0 - lf) / l0

    return {
        "valid": True,
        "dynamic_yield_mpa": round(sigma_yd_mpa, 2),
        "length_reduction_pct": round(mushroom_ratio * 100.0, 2),
        "undeformed_ratio_pct": round((x / l0) * 100.0, 2)
    }


def verify_taylor_bar_energy(
    internal_energy: float,
    kinetic_energy: float,
    hourglass_energy: float,
    total_energy: float
) -> Dict[str, Any]:
    """
    泰勒桿衝擊顯式動力學能量守恆與沙漏能客觀診斷
    """
    if total_energy <= 0:
        return {"passed": False, "diagnosis": "總能量異常 (非正值)"}

    hg_ratio_total = (hourglass_energy / total_energy) * 100.0
    hg_ratio_internal = (hourglass_energy / max(internal_energy, 1e-6)) * 100.0
    drift_pct = abs(total_energy - (internal_energy + kinetic_energy + hourglass_energy)) / total_energy * 100.0

    reasons = []
    passed = True

    # 雙軌檢驗：總能量佔比 (< 5%) 與 內能佔比 (< 10%)，徹底杜絕高速碰撞初期動能稀釋假象
    if hg_ratio_total > 5.0 or (internal_energy > 0.01 * total_energy and hg_ratio_internal > 10.0):
        passed = False
        reasons.append(f"沙漏能超標 (總能佔比 {hg_ratio_total:.2f}%, 內能佔比 {hg_ratio_internal:.2f}%)，嚴禁放行！建議採用全積分單元或細化網格")
    elif hg_ratio_total > 2.0 or (internal_energy > 0.01 * total_energy and hg_ratio_internal > 5.0):
        reasons.append(f"沙漏能佔比 (總能 {hg_ratio_total:.2f}%, 內能 {hg_ratio_internal:.2f}%) 處於合格邊緣")
    else:
        reasons.append(f"沙漏能佔比 (總能 {hg_ratio_total:.2f}%, 內能 {hg_ratio_internal:.2f}%)，數值品質優良")

    if drift_pct > 5.0:
        passed = False
        reasons.append(f"能量不守恆漂移量 {drift_pct:.2f}% (> 5%)")

    return {
        "passed": passed,
        "hourglass_pct": round(hg_ratio_total, 2),
        "hourglass_internal_pct": round(hg_ratio_internal, 2),
        "energy_drift_pct": round(drift_pct, 2),
        "diagnosis": " ； ".join(reasons)
    }


if __name__ == "__main__":
    print("================================================================================")
    print("      ANSYS Mechanical / LS-DYNA 泰勒桿高速撞擊大變形示範 (Taylor Bar Demo)     ")
    print("================================================================================")

    # 1. 生成經典 OFHC 銅泰勒桿撞擊卡片
    builder = TaylorBarSimulationBuilder(
        length_mm=32.4,
        radius_mm=3.2,
        impact_velocity_m_s=227.0,
        static_yield_mpa=400.0
    )
    deck = builder.get_keyword_deck()
    print("[步驟 1/3] 泰勒桿衝擊分析關鍵字卡片已組裝完成 (預覽前 350 字元):")
    print(deck[:350] + "\n... [其餘省略] ...\n*END\n")

    # 2. 執行撞擊後動態降伏強度估算
    print("[步驟 2/3] 執行經典泰勒一維理論動態降伏強度推算...")
    yield_res = estimate_taylor_dynamic_yield(
        length_initial_mm=32.4,
        length_final_mm=27.2,
        length_undeformed_mm=18.5,
        impact_velocity_m_s=227.0,
        density_ton_mm3=8.96e-9
    )
    print(f"  -> 動態降伏應力推算值: {yield_res['dynamic_yield_mpa']} MPa")
    print(f"  -> 桿長鐓粗壓縮率: {yield_res['length_reduction_pct']}%")
    print(f"  -> 尾端未變形長度佔比: {yield_res['undeformed_ratio_pct']}%")

    # 3. 執行顯式求解能量平衡與沙漏能品質診斷
    print("\n[步驟 3/3] 顯式動力學能量守恆與沙漏能診斷...")
    energy_check = verify_taylor_bar_energy(
        internal_energy=2140.0,
        kinetic_energy=35.0,
        hourglass_energy=28.0,
        total_energy=2203.0
    )
    print(f"  -> 能量驗證狀態: {'通過' if energy_check['passed'] else '拒收'}")
    print(f"  -> 沙漏能佔比: {energy_check['hourglass_pct']}%")
    print(f"  -> 診斷建議: {energy_check['diagnosis']}")
    print("================================================================================")
