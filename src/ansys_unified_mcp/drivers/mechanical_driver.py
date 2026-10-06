"""Backward-compatibility shim for ansys_unified_mcp.drivers.mechanical_driver."""
from __future__ import annotations

from typing import Any
from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver

__all__ = ["MechanicalDriver"]


def __getattr__(name: str) -> Any:
    from ansys_unified_mcp.products.mechanical import driver as _driver
    val = getattr(_driver, name)
    globals()[name] = val
    return val