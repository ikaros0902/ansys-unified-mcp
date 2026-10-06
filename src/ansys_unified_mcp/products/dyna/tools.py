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
