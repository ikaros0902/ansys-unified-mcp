# -*- coding: utf-8 -*-
"""ANSYS Icepak MCP 工具層：向 FastMCP 暴露電子散熱分析工具。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import subprocess

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.products.icepak.driver import IcepakDriver


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
)
def icepak_check_connection() -> dict:
    """檢查本機 ANSYS Icepak 求解器與執行環境可用性。"""
    driver = IcepakDriver()
    valid, message = driver.validate_prerequisites()
    return _envelope({
        "available": valid,
        "solver_bin": driver.solver_bin,
        "message": message,
    })


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False}
)
def icepak_solve(
    job_dir: str,
    power_w: float = 45.0,
    ambient_temp_c: float = 25.0,
    h_coeff: float = 15.0,
    dry_run: bool = False,
    timeout: float = 300.0,
) -> dict:
    """調度 ANSYS Icepak 執行晶片/板級電子散熱模擬。

    Args:
        job_dir: 工作目錄路徑。
        power_w: 晶片總發熱功率 (Watts)。
        ambient_temp_c: 環境參考溫度 (攝氏度)。
        h_coeff: 表面自然對流換熱係數 (W/(m^2*K))。
        dry_run: 若為 True 則僅生成計算腳本與指令，不實際啟動求解器。
        timeout: 求解超時秒數。
    """
    job_path = Path(job_dir).resolve()
    job_path.mkdir(parents=True, exist_ok=True)
    driver = IcepakDriver()

    config = {
        "chip_power_w": power_w,
        "ambient_temp_c": ambient_temp_c,
        "h_coeff": h_coeff,
    }
    script_path = driver.prepare_job(job_path, config)
    cmd = driver.build_command(job_path, script_path)

    if dry_run:
        return _envelope({
            "ok": True,
            "dry_run": True,
            "command": cmd,
            "script_path": str(script_path),
            "config": config,
        })

    valid, msg = driver.validate_prerequisites()
    if not valid:
        return _envelope({
            "ok": False,
            "error": f"Icepak 求解器未就緒: {msg}",
            "command": cmd,
        })

    log_path = driver.get_log_file_path(job_path)
    with open(log_path, "w", encoding="utf-8") as log_f:
        proc = subprocess.run(cmd, cwd=str(job_path), stdout=log_f, stderr=subprocess.STDOUT, timeout=timeout)

    artifacts = driver.extract_artifacts(job_path)
    return _envelope({
        "ok": proc.returncode == 0,
        "return_code": proc.returncode,
        "log_path": str(log_path),
        "artifacts": artifacts,
    })
