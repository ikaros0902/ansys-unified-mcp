"""ANSYS Unified MCP 2.0 - 高階工程工況意圖工具 (Intent MCP Tools).

註冊 5 大系統級 CAE 工程工況工具：
1. run_drop_test: 電子產品落摔衝擊工作流 (LS-DYNA 顯式動力學、前置閘門與沙漏能守護)
2. run_shock_analysis: 衝擊響應與反應譜工作流 (半正弦/梯形波、DAF 動態放大係數)
3. run_random_vibration: 隨機振動工作流 (PSD 頻響、三向有效模態質量 >= 90% 硬性閘門)
4. run_thermal_warpage: PCB / 封裝熱翹曲工作流 (熱-結構直通鏈結、3-2-1 靜定支承、CTE/T_ref 閘門)
5. train_surrogate_model: optiSLang 參數尋優與 MOP 代理模型工作流 (LHS/Sobol 採樣、CoP 評估)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from ansys_unified_mcp.workflows import (
    run_drop_test as _run_drop_test,
    run_random_vibration as _run_random_vibration,
    run_shock_analysis as _run_shock_analysis,
    run_thermal_warpage as _run_thermal_warpage,
    train_surrogate_model as _train_surrogate_model,
)

logger = logging.getLogger("ansys-unified-mcp.tools.intent")

# 防禦性相容導入 FastMCP
try:
    from ansys_unified_mcp.shared import mcp
except Exception:
    try:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("ansys-unified-mcp")
    except Exception:
        class _FallbackMCP:
            def tool(self, *args, **kwargs):
                def decorator(fn):
                    return fn
                return decorator
        mcp = _FallbackMCP()


@mcp.tool()
def run_drop_test(
    cad_path: str,
    drop_height_mm: float = 1000.0,
    impact_velocity_mps: Optional[float] = None,
    gravity_direction: List[float] = [0.0, 0.0, -1.0],
    drop_orientation_angles_deg: List[float] = [0.0, 0.0, 0.0],
    floor_type: str = "rigid_wall",
    target_duration_ms: float = 5.0,
    mass_scaling_dt2ms: float = -1.0e-7,
    hourglass_type: int = 4,
    material_yield_strength_mpa: float = 310.0,
    youngs_modulus_pa: float = 7.0e10,
    density_kg_m3: float = 2700.0,
    mesh_min_size_mm: float = 1.0,
    tag: str = "drop_test",
) -> Dict[str, Any]:
    """執行電子產品落摔衝擊工作流 (整合 LS-DYNA / LS-Run / LS-Prepost)。

    包含前置安全閘門檢核（初速向量、剛性地面接觸、CFL 時間步長）、非同步沙盒排程、
    Watchdog 沙漏能與質量縮放實時物理守護、1920x1080 白底高解析雲圖產出與 HTML 報告合成。

    Args:
        cad_path: 待分析幾何模型檔案路徑
        drop_height_mm: 自由落體釋放高度 (mm，預設 1000.0 mm)
        impact_velocity_mps: 衝擊初速度 (m/s，若省略自動依 sqrt(2gh) 計算)
        gravity_direction: 重力與初速度方向向量 (預設 [0, 0, -1])
        drop_orientation_angles_deg: 著地碰撞姿態角 [rx, ry, rz]
        floor_type: 地面特性 ('rigid_wall' 或 'elastic_floor')
        target_duration_ms: 衝擊分析時長 (毫秒，預設 5.0 ms)
        mass_scaling_dt2ms: LS-DYNA 質量縮放控制參數 (預設 -1.0e-7)
        hourglass_type: 沙漏能控制演算法代碼 (預設 4: Flanagan-Belytschko)
        material_yield_strength_mpa: 材料降伏強度 (MPa)
        youngs_modulus_pa: 材料楊氏模量 (Pa)
        density_kg_m3: 材料密度 (kg/m^3)
        mesh_min_size_mm: 預估最小網格特徵尺寸 (mm)
        tag: 作業自訂標籤

    Returns:
        包含 ok, job_id, status, sandbox_dir 或前置閘門攔截處方箋報告的字典。
    """
    logger.info(f"收到 run_drop_test 呼叫: cad_path={cad_path}, height={drop_height_mm}mm")
    return _run_drop_test(
        cad_path=cad_path,
        drop_height_mm=drop_height_mm,
        impact_velocity_mps=impact_velocity_mps,
        gravity_direction=gravity_direction,
        drop_orientation_angles_deg=drop_orientation_angles_deg,
        floor_type=floor_type,
        target_duration_ms=target_duration_ms,
        mass_scaling_dt2ms=mass_scaling_dt2ms,
        hourglass_type=hourglass_type,
        material_yield_strength_mpa=material_yield_strength_mpa,
        youngs_modulus_pa=youngs_modulus_pa,
        density_kg_m3=density_kg_m3,
        mesh_min_size_mm=mesh_min_size_mm,
        tag=tag,
    )


@mcp.tool()
def run_shock_analysis(
    cad_path: str,
    pulse_shape: str = "half_sine",
    peak_acceleration_g: float = 50.0,
    pulse_duration_ms: float = 11.0,
    direction: str = "Z",
    analysis_method: str = "transient_dynamics",
    damping_ratio: float = 0.02,
    material_yield_strength_mpa: float = 250.0,
    youngs_modulus_pa: float = 2.0e11,
    density_kg_m3: float = 7850.0,
    tag: str = "shock",
) -> Dict[str, Any]:
    """執行半正弦/梯形波衝擊響應分析工作流 (含動態放大係數與反應譜)。

    Args:
        cad_path: 幾何模型檔案路徑
        pulse_shape: 衝擊波形 ('half_sine', 'trapezoidal', 'sawtooth')
        peak_acceleration_g: 衝擊加速度峰值 (G)
        pulse_duration_ms: 脈衝持續寬度 (ms)
        direction: 激振方向 ('X', 'Y', 'Z')
        analysis_method: 求解方法 ('transient_dynamics' 或 'response_spectrum')
        damping_ratio: 結構阻尼比 (預設 0.02)
        material_yield_strength_mpa: 材料降伏強度 (MPa)
        youngs_modulus_pa: 楊氏模量 (Pa)
        density_kg_m3: 材料密度 (kg/m^3)
        tag: 作業自訂標籤

    Returns:
        包含 ok, job_id, status, sandbox_dir 或前置閘門攔截處方箋報告的字典。
    """
    logger.info(f"收到 run_shock_analysis 呼叫: cad_path={cad_path}, peak_g={peak_acceleration_g}")
    return _run_shock_analysis(
        cad_path=cad_path,
        pulse_shape=pulse_shape,
        peak_acceleration_g=peak_acceleration_g,
        pulse_duration_ms=pulse_duration_ms,
        direction=direction,
        analysis_method=analysis_method,
        damping_ratio=damping_ratio,
        material_yield_strength_mpa=material_yield_strength_mpa,
        youngs_modulus_pa=youngs_modulus_pa,
        density_kg_m3=density_kg_m3,
        tag=tag,
    )


@mcp.tool()
def run_random_vibration(
    cad_path: str,
    psd_table: List[Tuple[float, float]],
    direction: str = "Z",
    num_modes: int = 50,
    damping_ratio: float = 0.02,
    sigma_levels: List[int] = [1, 2, 3],
    material_yield_strength_mpa: float = 250.0,
    effective_mass_ratio: Optional[Dict[str, float]] = None,
    cutoff_frequency_hz: Optional[float] = None,
    youngs_modulus_pa: float = 2.0e11,
    density_kg_m3: float = 7850.0,
    tag: str = "random_vibration",
) -> Dict[str, Any]:
    """執行隨機振動 PSD 頻響分析工作流 (含模態有效質量比 >= 90% 前置硬性閘門)。

    前置安全閘門嚴格檢核三向有效模態質量比 >= 90% 與截斷頻率 >= 1.5x 激振上限，
    若未達標強制阻斷並產出自愈處方箋；達標則透過 Workbench 原生拓撲直通執行隨機振動求解。

    Args:
        cad_path: 待分析幾何模型路徑
        psd_table: 功率譜密度 (PSD) 表格 [(頻率_Hz, G^2/Hz), ...]
        direction: 激振方向 ('X', 'Y', 'Z')
        num_modes: 模態提取階數 (預設 50)
        damping_ratio: 阻尼比 (預設 0.02)
        sigma_levels: 統計響應等級 (預設 [1, 2, 3])
        material_yield_strength_mpa: 材料降伏強度 (MPa)
        effective_mass_ratio: 累積有效模態質量比字典
        cutoff_frequency_hz: 模態最高截斷頻率 (Hz)
        youngs_modulus_pa: 楊氏模量 (Pa)
        density_kg_m3: 材料密度 (kg/m^3)
        tag: 作業自訂標籤

    Returns:
        包含 ok, job_id, status, sandbox_dir 或前置閘門攔截處方箋報告的字典。
    """
    logger.info(f"收到 run_random_vibration 呼叫: cad_path={cad_path}, direction={direction}")
    return _run_random_vibration(
        cad_path=cad_path,
        psd_table=psd_table,
        direction=direction,
        num_modes=num_modes,
        damping_ratio=damping_ratio,
        sigma_levels=sigma_levels,
        material_yield_strength_mpa=material_yield_strength_mpa,
        effective_mass_ratio=effective_mass_ratio,
        cutoff_frequency_hz=cutoff_frequency_hz,
        youngs_modulus_pa=youngs_modulus_pa,
        density_kg_m3=density_kg_m3,
        tag=tag,
    )


@mcp.tool()
def run_thermal_warpage(
    cad_or_stackup_file: str,
    temperature_ref_c: float = 22.0,
    temperature_operating_c: float = 125.0,
    support_type: str = "3-2-1",
    enable_rom_composite: bool = True,
    secant_cte: float = 1.6e-5,
    material_yield_strength_mpa: float = 250.0,
    youngs_modulus_pa: float = 2.4e10,
    tag: str = "thermal_warpage",
) -> Dict[str, Any]:
    """執行電子封裝與 PCB 多層疊構熱翹曲分析工作流。

    前置檢核非零割線 CTE 與合理零應力參考溫度 T_ref，透過 WorkbenchCellLinkEngine
    建立 Thermal -> Structural 原生溫度場傳遞，施加 3-2-1 靜定無拘束邊界條件，
    產出 1920x1080 白底 Z 軸翹曲雲圖 (微米級) 與 HTML 報告。

    Args:
        cad_or_stackup_file: 幾何模型或疊構檔案路徑
        temperature_ref_c: 零應力參考溫度 (常溫，°C)
        temperature_operating_c: 運作或回流焊峰值溫度 (°C)
        support_type: 支承方式 ('3-2-1' 靜定支承防止假應力)
        enable_rom_composite: 是否啟用降階均質化材料
        secant_cte: 材料割線熱膨脹係數 (1/K)
        material_yield_strength_mpa: 材料降伏強度 (MPa)
        youngs_modulus_pa: 楊氏模量 (Pa)
        tag: 作業自訂標籤

    Returns:
        包含 ok, job_id, status, sandbox_dir 或前置閘門攔截處方箋報告的字典。
    """
    logger.info(f"收到 run_thermal_warpage 呼叫: file={cad_or_stackup_file}, T_op={temperature_operating_c}C")
    return _run_thermal_warpage(
        cad_or_stackup_file=cad_or_stackup_file,
        temperature_ref_c=temperature_ref_c,
        temperature_operating_c=temperature_operating_c,
        support_type=support_type,
        enable_rom_composite=enable_rom_composite,
        secant_cte=secant_cte,
        material_yield_strength_mpa=material_yield_strength_mpa,
        youngs_modulus_pa=youngs_modulus_pa,
        tag=tag,
    )


@mcp.tool()
def train_surrogate_model(
    workflow_config: Optional[Dict[str, Any]] = None,
    design_parameters: Optional[List[Dict[str, Any]]] = None,
    target_responses: Optional[List[str]] = None,
    num_samples: int = 50,
    sampling_method: str = "LHS",
    cop_target: float = 0.80,
    tag: str = "surrogate_mop",
) -> Dict[str, Any]:
    """執行 optiSLang 代理模型 (MOP) 訓練工作流。

    進行參數化取樣 (LHS/Sobol)、批次計算、最佳預測係數 (CoP) 評估與元模型擬合，
    若 CoP >= cop_target 則匯出 ProxySolver；若未達標則給出自適應補點處方。

    Args:
        workflow_config: 底層關聯分析作業配置字典 (可選)
        design_parameters: 參數化設計變數清單 [{'name': 't', 'min': 1.0, 'max': 3.0}]
        target_responses: 目標響應輸出清單 ['max_stress', 'max_deformation']
        num_samples: 取樣樣本點數 (預設 50)
        sampling_method: 採樣演算法 ('LHS' 或 'Sobol')
        cop_target: 最佳預測係數目標合格門檻 (預設 0.80)
        tag: 作業自訂標籤

    Returns:
        包含 ok, job_id, status, sandbox_dir 或參數校驗錯誤的字典。
    """
    logger.info(f"收到 train_surrogate_model 呼叫: samples={num_samples}, method={sampling_method}")
    return _train_surrogate_model(
        workflow_config=workflow_config,
        design_parameters=design_parameters,
        target_responses=target_responses,
        num_samples=num_samples,
        sampling_method=sampling_method,
        cop_target=cop_target,
        tag=tag,
    )