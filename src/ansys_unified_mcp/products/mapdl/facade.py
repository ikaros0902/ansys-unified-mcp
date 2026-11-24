# -*- coding: utf-8 -*-
"""ANSYS MAPDL (Mechanical APDL) 產品控制器 (Facade)。

封裝 MAPDL 批次求解調度、APDL 內聯腳本寫入與工作名稱 (Jobname) 路徑安全防護，
使工具層僅維持薄包裝與信封正規化職責。
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess

from ansys_unified_mcp.config import config

PRODUCT = "mapdl"

_JOB_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def sanitize_job_name(job_name: str) -> str:
    """驗證並消毒 MAPDL 工作名稱，阻擋路徑穿越、斜線、絕對路徑與非法字元。"""
    if not isinstance(job_name, str) or not job_name:
        raise ValueError(f"非法的工作名稱: {job_name!r}")
    if (
        ".." in job_name
        or "/" in job_name
        or "\\" in job_name
        or job_name == "."
        or Path(job_name).is_absolute()
        or _JOB_NAME_PATTERN.fullmatch(job_name) is None
    ):
        raise ValueError(f"非法的工作名稱: {job_name!r}")
    return job_name


class MapdlController:
    """負責 MAPDL 執行檔檢查與批次求解調度的產品控制器。"""

    def check_connection(self) -> dict:
        """檢查本機 ANSYS MAPDL (ANSYS.exe) 可執行檔與求解環境狀態。"""
        exe_path = config.mapdl_exe
        exists = exe_path.is_file() if exe_path else False
        return {
            "ok": True,
            "available": exists,
            "executable": str(exe_path) if exe_path else None,
            "version": "v251" if "v251" in str(exe_path) else "detected",
        }

    def solve_input(
        self,
        input_path: str,
        job_name: str = "ansys_job",
        np: int = 4,
        working_dir: str = "",
        dry_run: bool = False,
        timeout: float = 300.0,
    ) -> dict:
        """調度本機 MAPDL 求解器以批次模式 (-b) 執行 APDL 輸入腳本檔 (.inp / .dat / .mac)。"""
        try:
            safe_job_name = sanitize_job_name(job_name)
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}

        inp_file = Path(input_path).resolve()
        if not inp_file.is_file():
            return {"ok": False, "error": f"找不到輸入檔: {input_path}"}

        work_path = Path(working_dir).resolve() if working_dir else inp_file.parent
        out_file = work_path / f"{safe_job_name}.out"
        if out_file.resolve().parent != work_path.resolve():
            return {"ok": False, "error": f"輸出日誌路徑越界工作目錄: {out_file}"}

        work_path.mkdir(parents=True, exist_ok=True)
        exe_path = config.mapdl_exe

        cmd = [
            str(exe_path),
            "-b",
            "-i",
            str(inp_file),
            "-o",
            str(out_file),
            "-j",
            safe_job_name,
            "-np",
            str(np),
        ]

        if dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "command": cmd,
                "working_dir": str(work_path),
                "output_log": str(out_file),
            }

        if not exe_path or not exe_path.is_file():
            return {"ok": False, "error": f"MAPDL 未安裝或路徑不存在: {exe_path}"}

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(work_path),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "ok": proc.returncode == 0,
                "return_code": proc.returncode,
                "output_log": str(out_file),
                "command": cmd,
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": f"MAPDL 求解超時 ({timeout}s)"}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def run_apdl(
        self,
        apdl_commands: str,
        job_name: str = "ansys_inline",
        working_dir: str = "",
        dry_run: bool = False,
        timeout: float = 120.0,
    ) -> dict:
        """將內聯 APDL 命令字串寫入工作目錄並委派批次求解。"""
        try:
            safe_job_name = sanitize_job_name(job_name)
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}

        work_path = (
            Path(working_dir).resolve()
            if working_dir
            else (Path.cwd() / ".runtime" / "mapdl_jobs").resolve()
        )
        inp_file = work_path / f"{safe_job_name}.inp"
        if inp_file.resolve().parent != work_path.resolve():
            return {"ok": False, "error": f"輸入檔路徑越界工作目錄: {inp_file}"}

        work_path.mkdir(parents=True, exist_ok=True)
        inp_file.write_text(apdl_commands, encoding="utf-8")

        return self.solve_input(
            input_path=str(inp_file),
            job_name=safe_job_name,
            working_dir=str(work_path),
            dry_run=dry_run,
            timeout=timeout,
        )


controller = MapdlController()
