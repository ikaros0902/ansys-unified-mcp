"""ANSYS Unified MCP 2.0 - Mechanical 垂直切片模組 (Mechanical Slice).

聚合 Session 管理 (facade)、業務邏輯 (api)、求解器驅動 (driver)、
工具整合 (tools) 與 ACT 插件 (plugins)。
"""

from __future__ import annotations

from ansys_unified_mcp.products.mechanical.facade import (
    MechanicalController,
    PRODUCT,
    controller,
    _esc,
)
from ansys_unified_mcp.products.mechanical import api
from ansys_unified_mcp.products.mechanical import tools as _tools  # noqa: F401 - Register MCP tools


def __getattr__(name: str):
    if name == "MechanicalDriver":
        from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver
        return MechanicalDriver
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "MechanicalController",
    "PRODUCT",
    "controller",
    "_esc",
    "api",
    "MechanicalDriver",
]
