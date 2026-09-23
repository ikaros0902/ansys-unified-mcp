# -*- coding: utf-8 -*-
"""DPF MCP 工具層：向 FastMCP 暴露 DPF 結果檔解析工具。

僅處理 Mechanical 隱式結構/模態/隨機振動/熱分析之 .rst 結果檔，
不涉及 LS-DYNA 顯式 d3plot/glstat 管線。
"""

from __future__ import annotations

import json

from ansys_unified_mcp.shared import mcp
from ansys_unified_mcp.products.dpf import controller


def _json(data: dict) -> str:
    """統一輸出符合標準之 JSON 信封字串。"""
    return json.dumps(data, indent=2, ensure_ascii=False)


@mcp.tool()
def dpf_extract_structural_results(rst_path: str, copy_to_sandbox: bool = True) -> str:
    """從 Mechanical .rst 結果檔抽取結構化關鍵指標（節點/單元數、最大變形、
    最大等效應力、時間/頻率步清單）。

    Args:
        rst_path: .rst 結果檔絕對路徑。
        copy_to_sandbox: True（預設）時先複製至獨立暫存目錄再讀取，避免與
            求解器爭搶檔案鎖。
    """
    result = controller.extract_structural_results(rst_path, copy_to_sandbox=copy_to_sandbox)
    return _json(result)


@mcp.tool()
def dpf_get_model_summary(rst_path: str) -> str:
    """回傳 .rst 結果檔的模型摘要：節點/單元數與可用結果資訊。

    Args:
        rst_path: .rst 結果檔絕對路徑。
    """
    result = controller.get_model_summary(rst_path)
    return _json(result)
