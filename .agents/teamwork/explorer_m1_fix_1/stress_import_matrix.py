"""全面壓測各種匯入順序與路徑組合（每個組合於乾淨子進程執行）。"""

import subprocess
import sys
from pathlib import Path

PYTHON_EXE = sys.executable
SRC_DIR = str(Path("F:/Ming_python/ansys-unified-mcp/src"))

TEST_CASES = [
    # 組合 1: 先 products.mechanical 再 MechanicalDriver
    "from ansys_unified_mcp.products.mechanical import MechanicalDriver; print('Case 1 OK')",
    
    # 組合 2: 直接 products.mechanical import *
    "from ansys_unified_mcp.products.mechanical import *; print('Case 2 OK', MechanicalDriver)",
    
    # 組合 3: 先 products.mechanical.driver 再 MechanicalDriver
    "from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver; print('Case 3 OK')",
    
    # 組合 4: 先 drivers 再 MechanicalDriver
    "from ansys_unified_mcp.drivers import MechanicalDriver; print('Case 4 OK')",
    
    # 組合 5: 直接 drivers import *
    "from ansys_unified_mcp.drivers import *; print('Case 5 OK', MechanicalDriver, FluentDriver)",
    
    # 組合 6: 先 drivers.mechanical_driver 再 MechanicalDriver
    "from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver; print('Case 6 OK')",
    
    # 組合 7: 逆向交叉匯入（先 mechanical 再 drivers）
    "import ansys_unified_mcp.products.mechanical; import ansys_unified_mcp.drivers; print('Case 7 OK')",
    
    # 組合 8: 順向交叉匯入（先 drivers 再 mechanical）
    "import ansys_unified_mcp.drivers; import ansys_unified_mcp.products.mechanical; print('Case 8 OK')",
    
    # 組合 9: FluentDriver 直接從 product 匯入
    "from ansys_unified_mcp.products.fluent.driver import FluentDriver; print('Case 9 OK')",
    
    # 組合 10: OptislangDriver 直接從 product 匯入
    "from ansys_unified_mcp.products.optislang.driver import OptislangDriver; print('Case 10 OK')",
    
    # 組合 11: SpaceClaimDriver 直接從 product 匯入
    "from ansys_unified_mcp.products.geometry.driver import SpaceClaimDriver; print('Case 11 OK')",
    
    # 組合 12: 全部 drivers 同時匯入
    "from ansys_unified_mcp.drivers import (BaseSolverDriver, MechanicalDriver, FluentDriver, LSDynaDriver, OptislangDriver, SpaceClaimDriver, IcepakDriver); print('Case 12 OK')",
]

# 包裝帶有 Import Hook 的前導代碼
WRAPPER_TEMPLATE = """
import sys
from pathlib import Path
SRC_DIR = Path("F:/Ming_python/ansys-unified-mcp/src")
sys.path.insert(0, str(SRC_DIR))

PATCHED_DRIVERS_INIT = '''
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
'''

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

# 測試本體
{test_code}
"""

all_passed = True
for idx, case in enumerate(TEST_CASES, 1):
    full_code = WRAPPER_TEMPLATE.replace("{test_code}", case)
    proc = subprocess.run(
        [PYTHON_EXE, "-c", full_code],
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        print(f"[{idx:02d}/12] PASS: {case.split(';')[0]}")
    else:
        print(f"[{idx:02d}/12] FAIL: {case.split(';')[0]}")
        print("  Error:", proc.stderr.strip())
        all_passed = False

if all_passed:
    print("\n>>> 全部 12 組匯入矩陣壓測 100% 通過！<<<")
else:
    print("\n>>> 部分測試失敗，請檢驗錯誤資訊！<<<")
    sys.exit(1)
