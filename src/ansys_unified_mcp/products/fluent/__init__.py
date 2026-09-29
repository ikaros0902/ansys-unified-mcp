"""ANSYS Unified MCP 2.0 - Fluent 垂直切片模組 (Fluent Slice).

聚合 Session 管理 (facade) 與求解器驅動 (driver)。
FastMCP 工具層請由 tools 模組或 __main__.py profile 路由載入。
"""

from __future__ import annotations

from ansys_unified_mcp.products.fluent.facade import (
    FluentController,
    PRODUCT,
    DEFAULT_KEY,
    controller,
)


def __getattr__(name: str):
    if name == "FluentDriver":
        from ansys_unified_mcp.products.fluent.driver import FluentDriver
        return FluentDriver
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "FluentController",
    "PRODUCT",
    "DEFAULT_KEY",
    "controller",
    "FluentDriver",
]
