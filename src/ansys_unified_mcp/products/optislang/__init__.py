"""ANSYS Unified MCP 2.0 - optiSLang 垂直切片模組 (optiSLang Slice).

聚合 Session 管理 (facade) 與優化驅動 (driver)。
FastMCP 工具層請由 tools 模組或 __main__.py profile 路由載入。
"""

from __future__ import annotations

from ansys_unified_mcp.products.optislang.facade import (
    OptislangController,
    PRODUCT,
    KEY,
    DEFAULT_SCRIPT_TIMEOUT,
    controller,
)


def __getattr__(name: str):
    if name == "OptislangDriver":
        from ansys_unified_mcp.products.optislang.driver import OptislangDriver
        return OptislangDriver
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "OptislangController",
    "PRODUCT",
    "KEY",
    "DEFAULT_SCRIPT_TIMEOUT",
    "controller",
    "OptislangDriver",
]
