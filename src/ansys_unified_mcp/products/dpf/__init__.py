"""ANSYS Unified MCP 2.0 - DPF 垂直切片模組 (DPF Slice).

聚合 DPF 結果檔解析 (facade)。
FastMCP 工具層請由 tools 模組或 __main__.py profile 路由載入。
"""

from __future__ import annotations

from ansys_unified_mcp.products.dpf.facade import (
    DPFController,
    PRODUCT,
    controller,
)

__all__ = [
    "DPFController",
    "PRODUCT",
    "controller",
]
