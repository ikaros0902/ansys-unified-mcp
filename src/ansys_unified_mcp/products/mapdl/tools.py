# -*- coding: utf-8 -*-
"""ANSYS MAPDL (Mechanical APDL) MCP 工具層：向 FastMCP 暴露經典有限元素求解工具。"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import Optional

from ansys_unified_mcp.config import config
from ansys_unified_mcp.shared import mcp, as_envelope as _envelope


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def mapdl_check_connection() -> dict:
    """檢查本機 ANSYS MAPDL (ANSYS.exe) 可執行檔與求解環境狀態。"""
    exe_path = config.mapdl_exe
    exists = exe_path.is_file() if exe_path else False
    return _envelope({
        "available": exists,
        "executable": str(exe_path) if exe_path else None,
        "version": "v251" if "v251" in str(exe_path) else "detected",
    })


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
    inp_file = Path(input_path).resolve()
    if not inp_file.is_file():
        return _envelope({"ok": False, "error": f"找不到輸入檔: {input_path}"})

    work_path = Path(working_dir).resolve() if working_dir else inp_file.parent
    work_path.mkdir(parents=True, exist_ok=True)

    out_file = work_path / f"{job_name}.out"
    exe_path = config.mapdl_exe

    cmd = [
        str(exe_path),
        "-b",
        "-i", str(inp_file),
        "-o", str(out_file),
        "-j", job_name,
        "-np", str(np),
    ]

    if dry_run:
        return _envelope({
            "ok": True,
            "dry_run": True,
            "command": cmd,
            "working_dir": str(work_path),
            "output_log": str(out_file),
        })

    if not exe_path.is_file():
        return _envelope({"ok": False, "error": f"MAPDL 未安裝或路徑不存在: {exe_path}"})

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(work_path),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return _envelope({
            "ok": proc.returncode == 0,
            "return_code": proc.returncode,
            "output_log": str(out_file),
            "command": cmd,
        })
    except subprocess.TimeoutExpired:
        return _envelope({"ok": False, "error": f"MAPDL 求解超時 ({timeout}s)"})
    except Exception as e:
        return _envelope({"ok": False, "error": str(e)})


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
    work_path = Path(working_dir).resolve() if working_dir else Path.cwd() / ".runtime" / "mapdl_jobs"
    work_path.mkdir(parents=True, exist_ok=True)

    inp_file = work_path / f"{job_name}.inp"
    inp_file.write_text(apdl_commands, encoding="utf-8")

    return mapdl_solve_input(
        input_path=str(inp_file),
        job_name=job_name,
        working_dir=str(work_path),
        dry_run=dry_run,
        timeout=timeout,
    )
