"""ANSYS Unified MCP 2.0 - 求解日誌解析器套件 (Parsers Package).

匯集 Mechanical MAPDL, LS-DYNA, Fluent 等主流求解器之串流日誌解析器。
"""

from __future__ import annotations

from typing import Any, Optional, Union

from ansys_unified_mcp.core.sentinel.parsers.fluent import (
    FluentParseResult,
    FluentResidualParser,
)
from ansys_unified_mcp.core.sentinel.parsers.lsdyna import (
    LSDynaGlstatParser,
    LSDynaParseResult,
)
from ansys_unified_mcp.core.sentinel.parsers.mechanical import (
    MechanicalMAPDLParser,
    MechanicalParseResult,
)

__all__ = [
    "MechanicalMAPDLParser",
    "MechanicalParseResult",
    "LSDynaGlstatParser",
    "LSDynaParseResult",
    "FluentResidualParser",
    "FluentParseResult",
    "create_solver_parser",
]


def create_solver_parser(
    workflow_type_or_solver: str,
    target_value: Optional[float] = None,
) -> Union[MechanicalMAPDLParser, LSDynaGlstatParser, FluentResidualParser]:
    """工廠函數：依據工作流類型或求解器名稱建立對應之日誌解析器實例。

    Args:
        workflow_type_or_solver: 工作流類型或求解器代稱
        target_value: 目標終止值 (時間秒數或迭代次數)

    Returns:
        對應求解器之專屬日誌解析器實例
    """
    key = workflow_type_or_solver.strip().lower()

    if any(k in key for k in ("lsdyna", "drop", "impact", "explicit")):
        duration = target_value if target_value is not None else 0.005
        return LSDynaGlstatParser(target_duration_s=duration)

    if any(k in key for k in ("fluent", "cfd", "flow", "fluid")):
        iters = int(target_value) if target_value is not None else 500
        return FluentResidualParser(target_iterations=iters)

    # 預設為 Mechanical / MAPDL (結構、熱、模態、振動、翹曲)
    end_time = target_value if target_value is not None else 1.0
    return MechanicalMAPDLParser(target_end_time=end_time)
