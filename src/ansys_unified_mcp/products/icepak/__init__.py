"""ANSYS Icepak 產品驅動程式。"""

from __future__ import annotations


def __getattr__(name: str):
    if name == "IcepakDriver":
        from ansys_unified_mcp.products.icepak.driver import IcepakDriver
        return IcepakDriver
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["IcepakDriver"]
