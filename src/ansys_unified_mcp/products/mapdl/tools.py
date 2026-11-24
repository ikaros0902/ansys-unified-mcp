# -*- coding: utf-8 -*-
"""ANSYS MAPDL (Mechanical APDL) MCP 工具層：向 FastMCP 暴露經典有限元素求解工具。"""

from __future__ import annotations

from ansys_unified_mcp.products.mapdl.facade import controller
from ansys_unified_mcp.shared import mcp, as_envelope as _envelope


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def mapdl_check_connection() -> dict:
    """檢查本機 ANSYS MAPDL (ANSYS.exe) 可執行檔與求解環境狀態。"""
    return _envelope(controller.check_connection())


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False}
)
def mapdl_solve_input(
    input_path: str,
    job_name: str = "ansys_job",
    np: int = 4,
    working_dir: str = "",
    dry_run: bool = False,
    timeout: float = 300.0,
) -> dict:
    """調度本機 MAPDL 求解器以批次模式 (-b) 執行 APDL 輸入腳本檔 (.inp / .dat / .mac)。

    Args:
        input_path: APDL 輸入檔絕對路徑。
        job_name: 工作名稱 (Jobname)，決定生成之 .out, .rst, .log 檔名。
        np: 使用的並行計算核心數 (預設 4)。
        working_dir: 工作目錄 (留空則使用 input_path 所在目錄)。
        dry_run: 若為 True 則僅驗證並構造執行命令，不實際啟動進程。
        timeout: 求解超時秒數 (預設 300 秒)。
    """
    return _envelope(
        controller.solve_input(
            input_path=input_path,
            job_name=job_name,
            np=np,
            working_dir=working_dir,
            dry_run=dry_run,
            timeout=timeout,
        )
    )


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False}
)
def mapdl_run_apdl(
    apdl_commands: str,
    job_name: str = "ansys_inline",
    working_dir: str = "",
    dry_run: bool = False,
    timeout: float = 120.0,
) -> dict:
    """直接傳入 APDL 命令字串並以批次模式執行。

    Args:
        apdl_commands: 內聯 APDL 命令序列 (純文字)。
        job_name: 工作名稱。
        working_dir: 工作目錄。
        dry_run: 僅驗證與寫入暫存檔，不啟動求解。
        timeout: 超時秒數。
    """
    return _envelope(
        controller.run_apdl(
            apdl_commands=apdl_commands,
            job_name=job_name,
            working_dir=working_dir,
            dry_run=dry_run,
            timeout=timeout,
        )
    )
