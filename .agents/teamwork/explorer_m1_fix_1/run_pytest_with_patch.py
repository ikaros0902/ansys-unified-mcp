"""以 Import Hook 驗證任意 pytest 目標在修復後的執行情況。"""

import sys
from pathlib import Path
import pytest

SRC_DIR = Path("F:/Ming_python/ansys-unified-mcp/src")
sys.path.insert(0, str(SRC_DIR))

PATCHED_DRIVERS_INIT = """
from ansys_unified_mcp.drivers.base import (
    BaseSolverDriver,
    SolverDriverError,
    SolverExecutionError,
    SolverNotFoundError,
)

_LAZY_DRIVERS = {
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

def __getattr__(name: str):
    if name in _LAZY_DRIVERS:
        mod_name, attr_name = _LAZY_DRIVERS[name]
        import importlib
        mod = importlib.import_module(mod_name)
        val = getattr(mod, attr_name)
        globals()[name] = val
        return val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
"""

from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec


class MockDriversFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == "ansys_unified_mcp.drivers":
            spec = ModuleSpec(fullname, MockDriversLoader(), is_package=True)
            spec.submodule_search_locations = [str(SRC_DIR / "ansys_unified_mcp" / "drivers")]
            return spec
        return None


class MockDriversLoader(Loader):
    def create_module(self, spec):
        return None

    def exec_module(self, module):
        module.__file__ = str(SRC_DIR / "ansys_unified_mcp" / "drivers" / "__init__.py")
        module.__package__ = "ansys_unified_mcp.drivers"
        module.__path__ = [str(SRC_DIR / "ansys_unified_mcp" / "drivers")]
        exec(PATCHED_DRIVERS_INIT, module.__dict__)


sys.meta_path.insert(0, MockDriversFinder())

# 接收命令列參數作為 pytest targets，預設為 test_m1_facade_adversarial_challenge.py
args = sys.argv[1:] if len(sys.argv) > 1 else ["tests/adversarial/test_m1_facade_adversarial_challenge.py", "-v"]
exit_code = pytest.main(args)
sys.exit(exit_code)
