"""ANSYS Unified MCP 2.0 - 核心 Sentinel 守護與排程套件 (Core Sentinel Package).

包含非同步排程隊列、實時物理守護線程、早期發散熔斷器與各主流求解器日誌解析器。
"""

from __future__ import annotations

from ansys_unified_mcp.core.sentinel.circuit_breaker import (
    BreakerVerdict,
    CircuitBreaker,
)
from ansys_unified_mcp.core.sentinel.daemon import (
    get_sentinel_queue,
    shutdown_sentinel,
)
from ansys_unified_mcp.core.sentinel.parsers import (
    FluentResidualParser,
    LSDynaGlstatParser,
    MechanicalMAPDLParser,
    create_solver_parser,
)
from ansys_unified_mcp.core.sentinel.queue import SentinelQueue
from ansys_unified_mcp.core.sentinel.watchdog import WatchdogDaemon

__all__ = [
    "SentinelQueue",
    "WatchdogDaemon",
    "CircuitBreaker",
    "BreakerVerdict",
    "MechanicalMAPDLParser",
    "LSDynaGlstatParser",
    "FluentResidualParser",
    "create_solver_parser",
    "get_sentinel_queue",
    "shutdown_sentinel",
]
