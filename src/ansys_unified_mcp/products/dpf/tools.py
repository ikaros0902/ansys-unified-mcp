# -*- coding: utf-8 -*-
"""DPF MCP 工具層：向 FastMCP 暴露 DPF 結果檔解析工具。

僅處理 Mechanical 隱式結構/模態/隨機振動/熱分析之 .rst 結果檔，
不涉及 LS-DYNA 顯式 d3plot/glstat 管線。
"""

from __future__ import annotations

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.products.dpf import controller


@mcp.tool()
def dpf_extract_structural_results(rst_path: str, copy_to_sandbox: bool = True) -> dict:
    """從 Mechanical .rst 結果檔抽取結構化關鍵指標（節點/單元數、最大變形、
    最大等效應力、時間/頻率步清單）。

    Args:
        rst_path: .rst 結果檔絕對路徑。
        copy_to_sandbox: True（預設）時先複製至獨立暫存目錄再讀取，避免與
            求解器爭搶檔案鎖。
    """
    result = controller.extract_structural_results(rst_path, copy_to_sandbox=copy_to_sandbox)
    return _envelope(result)


@mcp.tool()
def dpf_get_model_summary(rst_path: str) -> dict:
    """回傳 .rst 結果檔的模型摘要：節點/單元數與可用結果資訊。

    Args:
        rst_path: .rst 結果檔絕對路徑。
    """
    result = controller.get_model_summary(rst_path)
    return _envelope(result)


@mcp.tool()
def dpf_screenshot(
    rst_path: str,
    file_path: str = "dpf_screenshot.png",
    result_type: str = "stress",
    copy_to_sandbox: bool = True,
    return_image: bool = True,
) -> dict:
    """從 Mechanical .rst 結果檔抽取真實物理極值並渲染標準白底 1920x1080 雲圖 PNG。

    Args:
        rst_path: .rst 結果檔絕對路徑。
        file_path: 輸出 PNG 影像路徑。
        result_type: 結果類型（'stress' 或 'deformation'）。
        copy_to_sandbox: True 時先複製至獨立暫存目錄再讀取，避免檔案鎖衝突。
        return_image: 是否檢查本機影像存在並回傳可讀狀態。
    """
    from ansys_unified_mcp.core.screenshot_helper import finalize_screenshot_response

    env = _envelope(
        controller.capture_result_screenshot(
            rst_path=rst_path,
            file_path=file_path,
            result_type=result_type,
            copy_to_sandbox=copy_to_sandbox,
        )
    )
    return finalize_screenshot_response(env, return_image=return_image, as_tool_result=False)
