"""ANSYS Unified MCP 2.0 - 統一求解器驅動層 (Drivers Package).

匯出標準求解器驅動類別：
- BaseSolverDriver: 抽象基類
- MechanicalDriver: ANSYS Mechanical / MAPDL 結構與熱分析
- LSDynaDriver: LS-DYNA 顯式動力學與落摔衝擊
- OptislangDriver: optiSLang 參數尋優與 MOP 代理模型
- SpaceClaimDriver: SpaceClaim / Discovery 幾何前處理
- FluentDriver: ANSYS Fluent 計算流體力學
- IcepakDriver: ANSYS Icepak 電子散熱分析
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

from ansys_unified_mcp.drivers.base import (
    BaseSolverDriver,
    SolverDriverError,
    SolverExecutionError,
    SolverNotFoundError,
)

# 支援靜態類型檢查 (IDE 自動補齊與 mypy/pyright)
if TYPE_CHECKING:
    from ansys_unified_mcp.drivers.fluent_driver import FluentDriver
    from ansys_unified_mcp.drivers.icepak_driver import IcepakDriver
    from ansys_unified_mcp.drivers.lsdyna_driver import LSDynaDriver
    from ansys_unified_mcp.drivers.mechanical_driver import MechanicalDriver
    from ansys_unified_mcp.drivers.optislang_driver import OptislangDriver
    from ansys_unified_mcp.drivers.spaceclaim_driver import SpaceClaimDriver

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