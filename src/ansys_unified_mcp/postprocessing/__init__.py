"""ANSYS Unified MCP 2.0 - 後處理與結果萃取模組 (Postprocessing Subsystem).

提供沙盒隔離之有限元結果場提取與顯式日誌解析管線：
- BaseResultReader: 結果讀取器抽象基類
- DPFSandboxReader: 基於 PyAnsys DPF 之隱式/模態/振動場數據沙盒隔離讀取器
- LSDynaExplicitReader: LS-DYNA 顯式落摔與衝擊日誌 (glstat/matter.out) 解析器
- PostprocessingRouter: 工況自動路由分發器
- JobNotReadyError: 未完工作業讀取例外
- PostprocessingError: 後處理提取異常例外
- TERMINAL_STATES: 終態集合常數
"""

from ansys_unified_mcp.postprocessing.base import (
    BaseResultReader,
    JobNotReadyError,
    PostprocessingError,
    TERMINAL_STATES,
)
from ansys_unified_mcp.postprocessing.dpf_reader import DPFSandboxReader
from ansys_unified_mcp.postprocessing.explicit_reader import LSDynaExplicitReader
from ansys_unified_mcp.postprocessing.router import PostprocessingRouter

__all__ = [
    "BaseResultReader",
    "DPFSandboxReader",
    "LSDynaExplicitReader",
    "PostprocessingRouter",
    "JobNotReadyError",
    "PostprocessingError",
    "TERMINAL_STATES",
]
