"""ANSYS Unified MCP 2.0 - 統一求解器驅動層 (Drivers Package).

匯出標準求解器驅動類別：
- BaseSolverDriver: 抽象基類
- BaseDualTrackDriver: 雙軌求解器基類
- MechanicalDriver: ANSYS Mechanical / MAPDL 結構與熱分析
- LSDynaDriver: LS-DYNA 顯式動力學與落摔衝擊
- OptislangDriver: optiSLang 參數尋優與 MOP 代理模型
- SpaceClaimDriver: SpaceClaim / Discovery 幾何前處理
- FluentDriver: ANSYS Fluent 計算流體力學
- IcepakDriver: ANSYS Icepak 電子散熱分析
- AEDTDriver: ANSYS Electronics Desktop 電磁與射頻分析
- OpticsDriver: Lumerical / Zemax / Speos 光學光子學分析
- SystemsDriver: System Coupling / TwinAI 系統耦合與數位孿生
- RockyDriver: Rocky DEM 顆粒離散元力學分析
- GrantaDriver: Granta MI 材料情報與環保管規
- SherlockDriver: Sherlock 電子可靠度物理與壽命預測
- MotorCADDriver: Motor-CAD 電機電磁與熱效率分析
- AqwaDriver: Aqwa 水動力學與離岸海事結構
- ChemkinDriver: Chemkin-Pro 化學反應動力學分析
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

from ansys_unified_mcp.drivers.base import (
    BaseDualTrackDriver,
    BaseSolverDriver,
    SolverDriverError,
    SolverExecutionError,
    SolverNotFoundError,
)

# 支援靜態類型檢查 (IDE 自動補齊與 mypy/pyright)
if TYPE_CHECKING:
    from ansys_unified_mcp.products.aedt.driver import AEDTDriver
    from ansys_unified_mcp.products.aqwa.driver import AqwaDriver
    from ansys_unified_mcp.products.chemkin.driver import ChemkinDriver
    from ansys_unified_mcp.products.dyna.driver import LSDynaDriver
    from ansys_unified_mcp.products.fluent.driver import FluentDriver
    from ansys_unified_mcp.products.geometry.driver import SpaceClaimDriver
    from ansys_unified_mcp.products.granta.driver import GrantaDriver
    from ansys_unified_mcp.products.icepak.driver import IcepakDriver
    from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver
    from ansys_unified_mcp.products.motorcad.driver import MotorCADDriver
    from ansys_unified_mcp.products.optics.driver import OpticsDriver
    from ansys_unified_mcp.products.optislang.driver import OptislangDriver
    from ansys_unified_mcp.products.rocky.driver import RockyDriver
    from ansys_unified_mcp.products.sherlock.driver import SherlockDriver
    from ansys_unified_mcp.products.systems.driver import SystemsDriver

_LAZY_DRIVERS: dict[str, tuple[str, str]] = {
    "MechanicalDriver": ("ansys_unified_mcp.products.mechanical.driver", "MechanicalDriver"),
    "FluentDriver": ("ansys_unified_mcp.products.fluent.driver", "FluentDriver"),
    "IcepakDriver": ("ansys_unified_mcp.products.icepak.driver", "IcepakDriver"),
    "LSDynaDriver": ("ansys_unified_mcp.products.dyna.driver", "LSDynaDriver"),
    "OptislangDriver": ("ansys_unified_mcp.products.optislang.driver", "OptislangDriver"),
    "SpaceClaimDriver": ("ansys_unified_mcp.products.geometry.driver", "SpaceClaimDriver"),
    "AEDTDriver": ("ansys_unified_mcp.products.aedt.driver", "AEDTDriver"),
    "OpticsDriver": ("ansys_unified_mcp.products.optics.driver", "OpticsDriver"),
    "SystemsDriver": ("ansys_unified_mcp.products.systems.driver", "SystemsDriver"),
    "RockyDriver": ("ansys_unified_mcp.products.rocky.driver", "RockyDriver"),
    "GrantaDriver": ("ansys_unified_mcp.products.granta.driver", "GrantaDriver"),
    "SherlockDriver": ("ansys_unified_mcp.products.sherlock.driver", "SherlockDriver"),
    "MotorCADDriver": ("ansys_unified_mcp.products.motorcad.driver", "MotorCADDriver"),
    "AqwaDriver": ("ansys_unified_mcp.products.aqwa.driver", "AqwaDriver"),
    "ChemkinDriver": ("ansys_unified_mcp.products.chemkin.driver", "ChemkinDriver"),
}

__all__ = [
    "BaseSolverDriver",
    "BaseDualTrackDriver",
    "SolverDriverError",
    "SolverNotFoundError",
    "SolverExecutionError",
    "MechanicalDriver",
    "LSDynaDriver",
    "OptislangDriver",
    "SpaceClaimDriver",
    "FluentDriver",
    "IcepakDriver",
    "AEDTDriver",
    "OpticsDriver",
    "SystemsDriver",
    "RockyDriver",
    "GrantaDriver",
    "SherlockDriver",
    "MotorCADDriver",
    "AqwaDriver",
    "ChemkinDriver",
]


def __getattr__(name: str) -> Any:
    """PEP 562 模組級延遲載入，徹底消除循環依賴死結。"""
    if name in _LAZY_DRIVERS:
        module_path, attr_name = _LAZY_DRIVERS[name]
        mod = importlib.import_module(module_path)
        val = getattr(mod, attr_name)
        globals()[name] = val  # 寫入模組字典，後續存取 O(1) 快取
        return val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """支援 IDE 自動補齊與 dir() 反射。"""
    return sorted(list(globals().keys()) + list(_LAZY_DRIVERS.keys()))
