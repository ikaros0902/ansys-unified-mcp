"""ANSYS Unified MCP 2.0 - LS-DYNA 垂直切片模組 (DYNA Slice).

聚合 PyDYNA 離線 keyword deck 生成邏輯 (facade)。
FastMCP 工具層請由 tools 模組或 __main__.py profile 路由載入。
"""

from __future__ import annotations

from ansys_unified_mcp.products.dyna.facade import (
    DynaController,
    PRODUCT,
    controller,
)

__all__ = [
    "DynaController",
    "PRODUCT",
    "controller",
]
