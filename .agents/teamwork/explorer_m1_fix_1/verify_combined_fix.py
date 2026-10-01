"""驗證組合修復方案在全場景下的行為表現。"""

import importlib
import sys
from pathlib import Path
import pytest

SRC_DIR = Path("F:/Ming_python/ansys-unified-mcp/src")
sys.path.insert(0, str(SRC_DIR))

# 1. 模擬修改後的 drivers/__init__.py
DRIVERS_INIT_PATCH = """
from __future__ import annotations
import importlib
from typing import TYPE_CHECKING, Any

from ansys_unified_mcp.drivers.base import (
    BaseSolverDriver,
    SolverDriverError,
    SolverExecutionError,
    SolverNotFoundError,
)

_LAZY_DRIVERS: dict[str, tuple[str, str]] = {
    "MechanicalDriver": ("ansys_unified_mcp.drivers.mechanical_driver", "MechanicalDriver"),
    "FluentDriver": ("ansys_unified_mcp.drivers.fluent_driver", "FluentDriver"),
    "IcepakDriver": ("ansys_unified_mcp.drivers.icepak_driver", "IcepakDriver"),
    "LSDynaDriver": ("ansys_unified_mcp.drivers.lsdyna_driver", "LSDynaDriver"),
    "OptislangDriver": ("ansys_unified_mcp.drivers.optislang_driver", "OptislangDriver"),
    "SpaceClaimDriver": ("ansys_unified_mcp.drivers.spaceclaim_driver", "SpaceClaimDriver"),
}

__all__ = [
    "BaseSolverDriver",
    "SolverDriverError",
    "SolverNotFoundError",
    "SolverExecutionError",
    "MechanicalDriver",
    "LSDynaDriver",
    "OptislangDriver",
    "SpaceClaimDriver",
    "FluentDriver",
    "IcepakDriver",
]

def __getattr__(name: str) -> Any:
    if name in _LAZY_DRIVERS:
        module_path, attr_name = _LAZY_DRIVERS[name]
        mod = importlib.import_module(module_path)
        val = getattr(mod, attr_name)
        globals()[name] = val
        return val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(_LAZY_DRIVERS.keys()))
"""

# 2. 模擬修改後的 drivers/mechanical_driver.py
MECHANICAL_DRIVER_PATCH = """
from __future__ import annotations
from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver

__all__ = ["MechanicalDriver"]

def __getattr__(name: str):
    from ansys_unified_mcp.products.mechanical import driver as _driver
    val = getattr(_driver, name)
    globals()[name] = val
    return val
"""

# 3. 模擬優化後的 products/mechanical/__init__.py
MECHANICAL_INIT_PATCH = """
from __future__ import annotations

from ansys_unified_mcp.products.mechanical.facade import (
    MechanicalController,
    PRODUCT,
    controller,
    _esc,
)
from ansys_unified_mcp.products.mechanical import api
from ansys_unified_mcp.products.mechanical import tools as _tools

def __getattr__(name: str):
    if name == "MechanicalDriver":
        from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver
        globals()[name] = MechanicalDriver
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
"""

from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec

class CombinedFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == "ansys_unified_mcp.drivers":
            spec = ModuleSpec(fullname, CombinedLoader("drivers_init"), is_package=True)
            spec.submodule_search_locations = [str(SRC_DIR / "ansys_unified_mcp" / "drivers")]
            return spec
        elif fullname == "ansys_unified_mcp.drivers.mechanical_driver":
            return ModuleSpec(fullname, CombinedLoader("mechanical_driver"))
        elif fullname == "ansys_unified_mcp.products.mechanical":
            spec = ModuleSpec(fullname, CombinedLoader("mechanical_init"), is_package=True)
            spec.submodule_search_locations = [str(SRC_DIR / "ansys_unified_mcp" / "products" / "mechanical")]
            return spec
        return None

class CombinedLoader(Loader):
    def __init__(self, kind):
        self.kind = kind
    def create_module(self, spec):
        return None
    def exec_module(self, module):
        if self.kind == "drivers_init":
            module.__file__ = str(SRC_DIR / "ansys_unified_mcp" / "drivers" / "__init__.py")
            module.__package__ = "ansys_unified_mcp.drivers"
            module.__path__ = [str(SRC_DIR / "ansys_unified_mcp" / "drivers")]
            exec(DRIVERS_INIT_PATCH, module.__dict__)
        elif self.kind == "mechanical_driver":
            module.__file__ = str(SRC_DIR / "ansys_unified_mcp" / "drivers" / "mechanical_driver.py")
            module.__package__ = "ansys_unified_mcp.drivers"
            exec(MECHANICAL_DRIVER_PATCH, module.__dict__)
        elif self.kind == "mechanical_init":
            module.__file__ = str(SRC_DIR / "ansys_unified_mcp" / "products" / "mechanical" / "__init__.py")
            module.__package__ = "ansys_unified_mcp.products.mechanical"
            module.__path__ = [str(SRC_DIR / "ansys_unified_mcp" / "products" / "mechanical")]
            exec(MECHANICAL_INIT_PATCH, module.__dict__)

sys.meta_path.insert(0, CombinedFinder())

# 測試各項匯入
from ansys_unified_mcp.products.mechanical import MechanicalDriver as MD1
from ansys_unified_mcp.drivers import MechanicalDriver as MD2
from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver as MD3
from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver as MD4

assert MD1 is MD2 is MD3 is MD4
print("Identity test passed: All 4 MechanicalDriver references point to identical class object:", MD1)

# 執行 test_m1_facade_adversarial_challenge.py
exit_code = pytest.main(["tests/adversarial/test_m1_facade_adversarial_challenge.py", "-v"])
assert exit_code == 0, f"Pytest failed with exit code {exit_code}"
print("All adversarial challenges passed 100%!")
