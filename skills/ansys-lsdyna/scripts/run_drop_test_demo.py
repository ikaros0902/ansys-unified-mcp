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

    def add_part_and_section(
        self,
        pid: int,
        secid: int,
        mid: int,
        section_type: str = "solid",
        shell_thickness: float = 1.0,
        elform: int = 1
    ) -> "DropTestKeywordGenerator":
        """
        組裝 *PART 與對應的 *SECTION_SOLID 或 *SECTION_SHELL 拓撲關聯
        :param pid: 部件 ID
        :param secid: 斷面 ID
        :param mid: 材料 ID
        :param section_type: 'solid' (實體單元) 或 'shell' (薄殼單元)
        :param shell_thickness: 若為薄殼單元時之厚度 (mm)
        :param elform: 單元公式 (實體預設 1 常應變全域單元，薄殼預設 2 Belytschko-Tsay)
        """
        self.lines.extend([
            "$ ----------------------------------------------------------------------",
            f"$ 部件與斷面定義: PART={pid}, SECTION={secid}, MID={mid} ({section_type.upper()})",
            "$ ----------------------------------------------------------------------",
            "*PART",
            f"Part_{pid}",
            "$#     pid     secid       mid     eosid      hgid      grav    adpopt      tpid",
            f"{pid:10d}{secid:10d}{mid:10d}         0         0         0         0         0"
        ])
        if section_type.lower() == "solid":
            self.lines.extend([
                "*SECTION_SOLID",
                "$#   secid    elform       aet",
                f"{secid:10d}{elform:10d}         0",
                "$"
            ])
        else:
            self.lines.extend([
                "*SECTION_SHELL",
                "$#   secid    elform      shrf       nip     propt   qr/irid     icomp     setyp",
                f"{secid:10d}{elform:10d}      1.00         5         1         0         0         1",
                "$#      t1        t2        t3        t4      nloc     marea      idof    edgset",
                f"{shell_thickness:10.3f}{shell_thickness:10.3f}{shell_thickness:10.3f}{shell_thickness:10.3f}       0.0       0.0       0.0         0",
                "$"
            ])
        return self

    def add_strain_rate_table_mat024(
        self,
        mid: int,
        tbid: int,
        rate_curve_map: Dict[float, int],
        density: float = 7.85e-9,
        youngs: float = 2.10e5,
        poisson: float = 0.30
    ) -> "DropTestKeywordGenerator":
        """
        建立多應變率動態硬化表 *DEFINE_TABLE 與關聯之 *MAT_024 材料卡片
        :param mid: 材料 ID
        :param tbid: 表格 ID
        :param rate_curve_map: 應變率與曲線 ID 映射表，例如 {0.001: 101, 1.0: 102, 100.0: 103}
        """
        self.lines.extend([
            "$ ----------------------------------------------------------------------",
            f"$ 多應變率動態硬化表: *DEFINE_TABLE ID={tbid}",
            "$ ----------------------------------------------------------------------",
            "*DEFINE_TABLE",
            "$#    tbid      sdir",
            f"{tbid:10d}         0",
            "$#   value       lcid"
        ])
        for s_rate, lcid in sorted(rate_curve_map.items()):
            self.lines.append(f"{s_rate:10.3e}{lcid:10d}")

        self.lines.extend([
            "$ ----------------------------------------------------------------------",
            f"$ 材料本構: *MAT_024 (MID={mid}, LCSS=TABLE {tbid})",
            "$ ----------------------------------------------------------------------",
            "*MAT_PIECEWISE_LINEAR_PLASTICITY",
            "$#     mid        ro         e        pr      sigy      etan      fail      tdel",
            f"{mid:10d}{density:10.2e}{youngs:10.2e}{poisson:10.3f}       0.0       0.0     0.000     0.000",
            "$#       c         p      lcss      lcsr        vp",
            f"     0.000     0.000{tbid:10d}         0      0.00",
            "$"
        ])
        return self

    def add_mat_add_erosion(
        self,
        mid: int,
        max_failure_plastic_strain: float = 0.40,
        max_tensile_pressure: float = 0.0
    ) -> "DropTestKeywordGenerator":
        """
        為指定材料卡片附加單元失效刪除準則 (*MAT_ADD_EROSION)
        """
        self.lines.extend([
            "$ ----------------------------------------------------------------------",
            f"$ 單元斷裂失效刪除: *MAT_ADD_EROSION (MID={mid}, MXFP={max_failure_plastic_strain})",
            "$ ----------------------------------------------------------------------",
            "*MAT_ADD_EROSION",
            "$#     mid      excl    mxpres      mnsp    numfip       tcs      tdel     damp",
            f"{mid:10d}       0.0{max_tensile_pressure:10.2f}       0.0       0.0       0.0       0.0       0.0",
            "$#   volum     epsth     eps01      epsv     epst1      eps1      eps2      eps3",
            "       0.0       0.0       0.0       0.0       0.0       0.0       0.0       0.0",
            "$#    eps4      eps5      eps6      eps7      eps8      eps9     psoid      dflag",
            "       0.0       0.0       0.0       0.0       0.0       0.0         0         0",
            "$#    lcid      mnst     pconv      mxfp      epsrc     damtyp",
            f"         0       0.0       0.0{max_failure_plastic_strain:10.3f}       0.0         0",
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

    hg_ratio_total = (hourglass_energy / total_energy) * 100.0
    hg_ratio_internal = (hourglass_energy / max(internal_energy, 1e-6)) * 100.0
    passed = True
    reasons = []

    # 雙軌檢驗：總能量佔比 (< 5%) 與 內能佔比 (< 10%)，徹底杜絕高速碰撞初期動能稀釋假象
    if hg_ratio_total > 5.0 or (internal_energy > 0.01 * total_energy and hg_ratio_internal > 10.0):
        passed = False
        reasons.append(f"沙漏能超標 (總能佔比 {hg_ratio_total:.2f}%, 內能佔比 {hg_ratio_internal:.2f}%)，嚴禁放行！建議改用 IHQ=4 剛度阻尼或全積分單元。")
    elif hg_ratio_total > 2.0 or (internal_energy > 0.01 * total_energy and hg_ratio_internal > 5.0):
        reasons.append(f"沙漏能比例處於臨界區 (總能佔比 {hg_ratio_total:.2f}%, 內能佔比 {hg_ratio_internal:.2f}%)，建議抽查高應力區網格畸變。")
    else:
        reasons.append(f"沙漏能比例極低 (總能佔比 {hg_ratio_total:.2f}%, 內能佔比 {hg_ratio_internal:.2f}%)，數值品質極佳。")

    energy_drift = abs(total_energy - (kinetic_energy + internal_energy + hourglass_energy)) / total_energy
    if energy_drift > 0.10:
        passed = False
        reasons.append(f"總能量漂移量達到 {energy_drift*100:.1f}% (> 10%)，能量嚴重失衡！")

    return {
        "passed": passed,
        "hourglass_ratio_pct": hg_ratio_total,
        "hourglass_ratio_internal_pct": hg_ratio_internal,
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
