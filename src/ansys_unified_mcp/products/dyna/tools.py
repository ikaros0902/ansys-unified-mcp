# -*- coding: utf-8 -*-
"""LS-DYNA MCP 工具層：向 FastMCP 暴露 PyDYNA 離線 keyword deck 生成工具。

純離線設計：僅在記憶體中組裝 .k deck 文字或寫出檔案，不連線 LS-DYNA solver
或任何實機，亦不涉及求解執行與結果讀取（結果讀取見 ansys-ls-prepost 相關
技能與 drivers 中 d3plot/glstat 解析邏輯）。
"""

from __future__ import annotations

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.products.dyna import controller


@mcp.tool()
def dyna_create_keyword_deck(endtim: float, hourglass_control: bool = False) -> dict:
    """離線生成基礎 LS-DYNA keyword deck 文字（*CONTROL_TERMINATION，
    可選附加 *CONTROL_ENERGY 沙漏能控制）。

    Args:
        endtim: *CONTROL_TERMINATION 的終止時間 (endtim)。
        hourglass_control: True 時附加 *CONTROL_ENERGY 卡片，啟用沙漏能與
            滑移能追蹤，供後續能量守恆檢核使用。
    """
    result = controller.create_keyword_deck(endtim=endtim, hourglass_control=hourglass_control)
    return _envelope(result)


@mcp.tool()
def dyna_export_keyword_file(output_path: str, endtim: float, hourglass_control: bool = False) -> dict:
    """離線生成基礎 keyword deck 並寫出為 .k 檔。

    Args:
        output_path: 輸出 .k 檔絕對路徑（父目錄不存在時自動建立）。
        endtim: *CONTROL_TERMINATION 的終止時間 (endtim)。
        hourglass_control: True 時附加 *CONTROL_ENERGY 卡片。
    """
    result = controller.export_keyword_file(
        output_path=output_path, endtim=endtim, hourglass_control=hourglass_control
    )
    return _envelope(result)


@mcp.tool()
def dyna_list_keyword_types() -> dict:
    """回傳常用 LS-DYNA keyword 類別名稱清單（白名單篩選，非 PyDYNA 全集）。"""
    result = controller.list_keyword_types()
    return _envelope(result)


@mcp.tool()
def dyna_solve(
    k_file_path: str,
    ncpu: int = 4,
    memory: str = "100m",
    working_dir: str = "",
    dry_run: bool = False,
    timeout: float = 300.0,
) -> dict:
    """調度本機 LS-DYNA 求解器 (lsdyna_dp.exe / lsdyna.exe) 執行計算。

    Args:
        k_file_path: 輸入 keyword 檔案 (.k / .key) 路徑。
        ncpu: 使用的 CPU 核心數 (預設 4)。
        memory: 記憶體配置字串 (例如 "100m", "500m")。
        working_dir: 工作目錄路徑 (留空則使用 k 檔案所在目錄)。
        dry_run: 若為 True 則僅驗證並回傳預計執行的求解命令與參數，不實際啟動求解器進程。
        timeout: 求解超時秒數 (預設 300 秒)。
    """
    result = controller.solve_keyword(
        k_file_path=k_file_path,
        ncpu=ncpu,
        memory=memory,
        working_dir=working_dir,
        dry_run=dry_run,
        timeout=timeout,
    )
    return _envelope(result)


@mcp.tool()
def dyna_run_prepost(
    cfile_path: str = "",
    script_content: str = "",
    working_dir: str = "",
    dry_run: bool = False,
    timeout: float = 120.0,
) -> dict:
    """調度本機 LS-PrePost (lsprepost.exe) 以無頭批次模式執行 SCL/cfile 命令腳本。

    Args:
        cfile_path: 既有的 .cfile 命令腳本檔案路徑。
        script_content: 直接傳入的 SCL/cfile 腳本字串 (若指定則自動寫入暫存檔執行)。
        working_dir: 工作目錄路徑。
        dry_run: 若為 True 則僅驗證命令構造，不實際啟動進程。
        timeout: 執行超時秒數 (預設 120 秒)。
    """
    result = controller.run_prepost(
        cfile_path=cfile_path,
        script_content=script_content,
        working_dir=working_dir,
        dry_run=dry_run,
        timeout=timeout,
    )
    return _envelope(result)


@mcp.tool()
def lsdyna_setup_shock_analysis(
    pulse_type: str = "half_sine",
    peak_g: float = 50.0,
    duration_ms: float = 11.0,
    direction: str = "Z",
    output_k_path: str = "",
) -> dict:
    """建立標準 LS-DYNA 衝擊分析 (Shock Analysis) 關鍵字卡與脈衝載荷曲線。

    Args:
        pulse_type: 脈衝波形 ('half_sine', 'trapezoidal')。
        peak_g: 衝擊峰值加速度 (G)。
        duration_ms: 脈衝持續時間 (毫秒)。
        direction: 衝擊方向 ('X', 'Y', 'Z')。
        output_k_path: 選填輸出 .k 檔案路徑。
    """
    result = controller.setup_shock_analysis(
        pulse_type=pulse_type,
        peak_g=peak_g,
        duration_ms=duration_ms,
        direction=direction,
        output_k_path=output_k_path,
    )
    return _envelope(result)


@mcp.tool()
def lsdyna_setup_drop_test(
    drop_height_mm: float = 1000.0,
    impact_surface: str = "rigid_floor",
    gravity_g: float = 9.80665,
    output_k_path: str = "",
) -> dict:
    """建立標準 LS-DYNA 落摔試驗 (Drop Test) 關鍵字卡，自動計算衝擊初速度並配置剛性地面與接觸。

    Args:
        drop_height_mm: 落摔等效高度 (毫米)。
        impact_surface: 地面類型 ('rigid_floor', 'elastic_floor')。
        gravity_g: 重力加速度 (m/s^2, 預設 9.80665)。
        output_k_path: 選填輸出 .k 檔案路徑。
    """
    result = controller.setup_drop_test(
        drop_height_mm=drop_height_mm,
        impact_surface=impact_surface,
        gravity_g=gravity_g,
        output_k_path=output_k_path,
    )
    return _envelope(result)


