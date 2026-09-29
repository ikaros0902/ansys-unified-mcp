"""ANSYS Unified MCP 2.0 - Geometry 垂直切片模組 (Geometry Slice).

聚合 Session 管理 (facade) 與前處理驅動 (driver)。
FastMCP 工具層請由 tools 模組或 __main__.py profile 路由載入。
"""

from __future__ import annotations

from ansys_unified_mcp.products.geometry.facade import (
    GeometryController,
    PRODUCT,
    DEFAULT_KEY,
    controller,
)


def __getattr__(name: str):
    if name == "SpaceClaimDriver":
        from ansys_unified_mcp.products.geometry.driver import SpaceClaimDriver
        return SpaceClaimDriver
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "GeometryController",
    "PRODUCT",
    "DEFAULT_KEY",
    "controller",
    "SpaceClaimDriver",
]
