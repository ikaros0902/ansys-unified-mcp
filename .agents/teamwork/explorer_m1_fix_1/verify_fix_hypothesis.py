"""驗證假設：drivers/__init__.py 延遲導出能否徹底消除循環依賴。"""

import importlib
import importlib.util
import os
import sys
from pathlib import Path

# 將專案 src 加入 path
SRC_DIR = Path("F:/Ming_python/ansys-unified-mcp/src")
sys.path.insert(0, str(SRC_DIR))

# 定義假想的 drivers/__init__.py 內容
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

# 我們使用自定義 Import Hook 在記憶體中替換 ansys_unified_mcp.drivers
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec


class MockDriversFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == "ansys_unified_mcp.drivers":
            # 建立模組規格
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

print("=== 開始測試匯入順序 ===")

# 測試 1: from ansys_unified_mcp.products.mechanical import MechanicalDriver
try:
    from ansys_unified_mcp.products.mechanical import MechanicalDriver
    print("Test 1 SUCCESS: from products.mechanical import MechanicalDriver ->", MechanicalDriver)
except Exception as e:
    print("Test 1 FAILED:", e)
    import traceback
    traceback.print_exc()

# 測試 2: from ansys_unified_mcp.products.mechanical import *
try:
    # 測試 __getattr__ 支援 * 匯入
    exec("from ansys_unified_mcp.products.mechanical import *", globals())
    print("Test 2 SUCCESS: from products.mechanical import *")
except Exception as e:
    print("Test 2 FAILED:", e)
    import traceback
    traceback.print_exc()

# 測試 3: from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver
try:
    from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver as D2
    print("Test 3 SUCCESS: from products.mechanical.driver import MechanicalDriver ->", D2)
except Exception as e:
    print("Test 3 FAILED:", e)
    import traceback
    traceback.print_exc()

# 測試 4: from ansys_unified_mcp.drivers import MechanicalDriver
try:
    from ansys_unified_mcp.drivers import MechanicalDriver as D3
    print("Test 4 SUCCESS: from drivers import MechanicalDriver ->", D3)
except Exception as e:
    print("Test 4 FAILED:", e)
    import traceback
    traceback.print_exc()

# 測試 5: from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver
try:
    from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver as D4
    print("Test 5 SUCCESS: from drivers.mechanical_driver import MechanicalDriver ->", D4)
except Exception as e:
    print("Test 5 FAILED:", e)
    import traceback
    traceback.print_exc()

# 測試 6: 驗證 FluentDriver 是否也順帶解耦成功
try:
    from ansys_unified_mcp.products.fluent import driver as fluent_driver
    print("Test 6 SUCCESS: from products.fluent import driver ->", fluent_driver)
except Exception as e:
    print("Test 6 FAILED:", e)

# 測試 7: from ansys_unified_mcp.drivers import FluentDriver
try:
    from ansys_unified_mcp.drivers import FluentDriver
    print("Test 7 SUCCESS: from drivers import FluentDriver ->", FluentDriver)
except Exception as e:
    print("Test 7 FAILED:", e)

print("=== 所有假設測試完畢 ===")
