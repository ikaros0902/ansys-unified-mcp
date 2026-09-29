"""Backward-compatibility shim for ansys_unified_mcp.drivers.mechanical_driver."""
import sys
from ansys_unified_mcp.products.mechanical import driver as _driver

_this_module = sys.modules[__name__]
for _k, _v in _driver.__dict__.items():
    if not _k.startswith("__"):
        setattr(_this_module, _k, _v)