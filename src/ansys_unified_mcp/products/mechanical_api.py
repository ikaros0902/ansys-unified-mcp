"""Backward-compatibility shim for ansys_unified_mcp.products.mechanical_api."""
import sys
from ansys_unified_mcp.products.mechanical import api as _api

_this_module = sys.modules[__name__]
for _k, _v in _api.__dict__.items():
    if not _k.startswith("__"):
        setattr(_this_module, _k, _v)
