"""ANSYS Unified MCP 2.0 - Workbench 垂直切片模組 (Workbench Slice).

聚合 Session 管理 (facade) 與自動化日誌腳本 (scripts)。
FastMCP 工具層請由 tools 模組或 __main__.py profile 路由載入。
"""

from __future__ import annotations

from ansys_unified_mcp.products.workbench.facade import (
    WorkbenchController,
    PRODUCT,
    controller,
    _PROBE_CACHE,
    _PROBE_TTL,
    DEFAULT_SCRIPT_TIMEOUT,
)

__all__ = [
    "WorkbenchController",
    "PRODUCT",
    "controller",
    "_PROBE_CACHE",
    "_PROBE_TTL",
    "DEFAULT_SCRIPT_TIMEOUT",
]
