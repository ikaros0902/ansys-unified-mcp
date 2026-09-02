# -*- coding: utf-8 -*-
"""
模組名稱：run_drop_test_demo.py
功能說明：LS-DYNA 落摔衝擊試驗 (Drop Test) 關鍵字卡片自動化生成器
依據標準：林明志標準顯式動力學 CFL 準則、能量守恆與質量縮放自動診斷規範
單位系統：ton, mm, s, N, MPa
"""

import math
from typing import Dict, Any, List, Optional


class DropTestKeywordGenerator:
    """
    LS-DYNA 落摔衝擊試驗關鍵字卡片 (*.k) 自動組裝器
    """

    def __init__(self, title: str = "Standard_Electronic_Drop_Test"):
        self.title = title
        self.lines: List[str] = []
        self._init_header()

    def _init_header(self) -> None:
        """寫入標準關鍵字檔頭與單位標註"""
        self.lines.extend([
            "$# ====================================================================",
            f"$# 專案名稱: {self.title}",
            "$# 自動生成: 林明志標準 LS-DYNA 顯式動力學落摔生成器",
            "$# 單位系統: ton, mm, s, N, MPa (g = 9806.65 mm/s^2)",
            "$# ====================================================================",
            "*KEYWORD",
            "*TITLE",
            self.title,
            "$"
        ])

    def configure_controls(
        self,
        end_time: float = 0.005,
        tssfac: float = 0.90,
        dt2ms: float = -1.0e-7,
        ihq: int = 4,
        qh: float = 0.10
    ) -> "DropTestKeywordGenerator":
        """
        配置求解器步長控制、終止時間與剛度型沙漏阻尼
        :param end_time: 分析終止時間 (秒)
        :param tssfac: 時間步長安全係數 (落摔建議 0.85 ~ 0.90)
        :param dt2ms: 局部質量縮放臨界時間步長 (負值代表選擇性質量縮放)
        :param ihq: 沙漏控制形式 (4 為 Flanagan-Belytschko 剛度阻尼)
        :param qh: 沙漏係數 (建議 0.10)
        """
        self.lines.extend([
            "$ ----------------------------------------------------------------------",
            "$ 1. 求解與控制卡片: *CONTROL_TERMINATION, *CONTROL_TIMESTEP, *CONTROL_ENERGY",
            "$ ----------------------------------------------------------------------",
            "*CONTROL_TERMINATION",
            "$#  endtim    endcyc     dtmin    endeng    rpend",
            f"{end_time:10.4e}         0       0.0       0.0       0.0",
            "*CONTROL_TIMESTEP",
            "$#  dtinit    tssfac      isdo    tslimt     dt2ms      lctm     erode     ms1st",
            f"       0.0{tssfac:10.2f}         0       0.0{dt2ms:10.2e}         0         0         0",
            "*CONTROL_ENERGY",
            "$#    hgen      rwen    slnten     rylen",
            "         2         2         2         2",
            "*CONTROL_HOURGLASS",
            "$#     ihq        qh",
            f"{ihq:10d}{qh:10.2f}",
            "$"
        ])
        return self

    def configure_outputs(
        self,
        d3plot_dt: float = 1.0e-4,
        history_dt: float = 1.0e-5
    ) -> "DropTestKeywordGenerator":
        """配置 3D 雲圖與時間歷程輸出頻率"""
        self.lines.extend([
            "$ ----------------------------------------------------------------------",
            "$ 2. 歷程輸出卡片: *DATABASE_BINARY_D3PLOT, glstat, matsum, sleout",
            "$ ----------------------------------------------------------------------",
            "*DATABASE_BINARY_D3PLOT",
            "$#      dt      lcdt      beam     npltc    psetid",
            f"{d3plot_dt:10.4e}         0         0         0         0",
            "*DATABASE_GLSTAT",
            f"{history_dt:10.4e}",
            "*DATABASE_MATSUM",
            f"{history_dt:10.4e}",
            "*DATABASE_SLEOUT",
            f"{history_dt:10.4e}",
            "$"
        ])
        return self

    def add_drop_initial_velocity(
        self,
        part_id: int,
        drop_height_mm: float = 1000.0,
        g_accel: float = 9806.65
    ) -> "DropTestKeywordGenerator":
        """
        依據物理自由落體公式 v = -sqrt(2gh) 自動計算撞擊初速度並施加於部件
        """
        v_impact = -math.sqrt(2.0 * g_accel * drop_height_mm)
        self.lines.extend([
            "$ ----------------------------------------------------------------------",
            f"$ 3. 初始速度設定: 落摔高度 = {drop_height_mm} mm, 計算撞擊初速度 = {v_impact:.2f} mm/s",
            "$ ----------------------------------------------------------------------",
            "*INITIAL_VELOCITY_GENERATION",
            "$#      id      styp     omega        vx        vy        vz      ivat     icid",
            f"{part_id:10d}         2       0.0       0.0       0.0{v_impact:10.2f}         0         0",
            "$"
        ])
        return self

    def add_planar_rigidwall(
        self,
        z_floor: float = 0.0,
        friction: float = 0.30
    ) -> "DropTestKeywordGenerator":
        """建立剛性地面"""
        self.lines.extend([
            "$ ----------------------------------------------------------------------",
            f"$ 4. 剛性撞擊地面: 平面位置 Z = {z_floor} mm, 摩擦係數 = {friction}",
            "$ ----------------------------------------------------------------------",
            "*RIGIDWALL_PLANAR",
            "$#    nsid      nsid       box       box      dseq      dseq",
            "         0         0         0         0       0.0       0.0",
            "$#      xt        yt        zt        xh        yh        zh      fric       wvel",
            f"       0.0       0.0{z_floor:10.2f}       0.0       0.0      1.00{friction:10.2f}       0.0",
            "$"
        ])
        return self

    def add_mat_024_metal(
        self,
        mid: int,
        density: float = 7.85e-9,
        youngs: float = 2.10e5,
        poisson: float = 0.30,
        yield_stress: float = 350.0,
        tangent_modulus: float = 1500.0,
        fail_strain: float = 0.25
    ) -> "DropTestKeywordGenerator":
        """加入標準 MAT_024 彈塑性金屬材料"""
        self.lines.extend([
            "$ ----------------------------------------------------------------------",
            f"$ 5. 材料本構: *MAT_024 (MID={mid}), 降伏應力={yield_stress} MPa",
            "$ ----------------------------------------------------------------------",
            "*MAT_PIECEWISE_LINEAR_PLASTICITY",
            "$#     mid        ro         e        pr      sigy      etan      fail      tdel",
            f"{mid:10d}{density:10.2e}{youngs:10.2e}{poisson:10.3f}{yield_stress:10.2f}{tangent_modulus:10.2f}{fail_strain:10.3f}     0.000",
            "$"
        ])
        return self

    def build_deck(self) -> str:
        """完成卡片輸出並加上 *END"""
        output_lines = list(self.lines)
        output_lines.extend(["*END", ""])
        return "\n".join(output_lines)


# ----------------------------------------------------------------------
# 【判斷力庫】客觀驗證評估函數
# ----------------------------------------------------------------------
def verify_glstat_energy_balance(
    kinetic_energy: float,
    internal_energy: float,
    hourglass_energy: float,
    total_energy: float
) -> Dict[str, Any]:
    """
    依據顯式動力學能量守恆與沙漏能準則進行客觀診斷
    :return: 診斷字典包含判定結論與工程建議
    """
    if total_energy <= 0:
        return {"passed": False, "reason": "總能量非正數，數值可能發散"}

    hg_ratio = (hourglass_energy / total_energy) * 100.0
    passed = True
    reasons = []

    if hg_ratio > 5.0:
        passed = False
        reasons.append(f"沙漏能比例高達 {hg_ratio:.2f}% (超過 5% 嚴格紅線)，嚴禁放行結果！建議改用 IHQ=4 剛度阻尼或全積分單元。")
    elif hg_ratio > 2.0:
        reasons.append(f"沙漏能比例為 {hg_ratio:.2f}% (介於 2%~5% 合格邊緣)，建議抽查高應力區網格畸變。")
    else:
        reasons.append(f"沙漏能比例為 {hg_ratio:.2f}% (< 2%)，數值品質極佳。")

    energy_drift = abs(total_energy - (kinetic_energy + internal_energy + hourglass_energy)) / total_energy
    if energy_drift > 0.10:
        passed = False
        reasons.append(f"總能量漂移量達到 {energy_drift*100:.1f}% (> 10%)，能量嚴重失衡！")

    return {
        "passed": passed,
        "hourglass_ratio_pct": hg_ratio,
        "diagnosis": " ； ".join(reasons)
    }


def check_mass_scaling_validity(added_mass_pct: float) -> Dict[str, Any]:
    """
    依據林明志標準質量縮放規則進行檢驗
    """
    if added_mass_pct > 5.0:
        return {
            "valid": False,
            "level": "紅線拒收",
            "message": f"質量增加比例高達 {added_mass_pct:.2f}% (> 5%)，慣性力嚴重失真，判定分析無效！"
        }
    elif added_mass_pct > 2.0:
        return {
            "valid": True,
            "level": "黃燈警示",
            "message": f"質量增加比例為 {added_mass_pct:.2f}% (介於 2%~5%)，必須確認新增質量未集中於主撞擊衝擊區域。"
        }
    else:
        return {
            "valid": True,
            "level": "綠燈合格",
            "message": f"質量增加比例為 {added_mass_pct:.2f}% (< 2%)，符合高精度衝擊分析要求。"
        }


if __name__ == "__main__":
    # 範例執行：生成高度 1.2m 落摔分析關鍵字卡片
    gen = DropTestKeywordGenerator(title="Phone_Drop_Impact_Test")
    gen.configure_controls(end_time=0.006, tssfac=0.90, dt2ms=-1.0e-7, ihq=4, qh=0.10)
    gen.configure_outputs(d3plot_dt=1.0e-4, history_dt=1.0e-5)
    gen.add_drop_initial_velocity(part_id=1, drop_height_mm=1200.0)
    gen.add_planar_rigidwall(z_floor=0.0, friction=0.35)
    gen.add_mat_024_metal(mid=1, density=7.85e-9, youngs=2.10e5, yield_stress=355.0)

    deck_str = gen.build_deck()
    print("=== 生成的 LS-DYNA 落摔關鍵字卡片片段 ===")
    print(deck_str[:600] + "\n... [其餘省略] ...\n*END")

    # 執行能量與質量縮放驗證演示
    energy_check = verify_glstat_energy_balance(
        kinetic_energy=150.0,
        internal_energy=820.0,
        hourglass_energy=12.0,
        total_energy=982.0
    )
    print("\n=== 能量診斷評估結論 ===")
    print(f"通過狀態: {energy_check['passed']}, 診斷: {energy_check['diagnosis']}")

    mass_check = check_mass_scaling_validity(added_mass_pct=1.45)
    print("\n=== 質量縮放檢驗結論 ===")
    print(f"等級: {mass_check['level']}, 評語: {mass_check['message']}")
