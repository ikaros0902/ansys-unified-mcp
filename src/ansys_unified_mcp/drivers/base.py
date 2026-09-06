"""ANSYS Unified MCP 2.0 - 統一求解器驅動抽象層 (BaseSolverDriver).

提供所有 ANSYS CAE 求解器驅動的抽象基類與生命週期合約：
- validate_prerequisites: 驗證環境變數、求解器路徑與授權可用性
- prepare_environment: 初始化求解器專屬環境變數 (ANSYS_LOCK, OMP 等)
- prepare_job: 在沙盒 workspace 內建立或轉換求解器輸入檔/腳本
- run_solver / launch: 啟動非同步求解子進程並重導向標準日誌
- get_log_file_path: 獲取求解器核心輸出日誌路徑
- parse_progress: 串流解析求解進度、時間步與收斂狀態
- terminate_process / abort: 安全終止進程樹並釋放授權
- extract_artifacts / extract_results: 後處理提取結果、產出白底 PNG 雲圖與指標
"""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("ansys-unified-mcp.drivers.base")


class SolverDriverError(Exception):
    """求解器驅動基本例外。"""
    pass


class SolverNotFoundError(SolverDriverError):
    """未找到求解器可執行檔或執行環境。"""
    pass


class SolverExecutionError(SolverDriverError):
    """求解器執行失敗或非正常退出。"""
    pass


class BaseSolverDriver(ABC):
    """所有 CAE 求解器驅動程式的統一抽象基類。"""

    def __init__(self, solver_name: str, solver_bin: Optional[str] = None) -> None:
        self.solver_name = solver_name
        self.solver_bin = solver_bin

    # ----------------------------------------------------------------------
    # 1. 前置驗證與環境準備
    # ----------------------------------------------------------------------
    @abstractmethod
    def validate_prerequisites(self) -> Tuple[bool, str]:
        """驗證環境變數、求解器二進位檔與授權可用性。

        Returns:
            Tuple[bool, str]: (是否可用, 狀態說明或錯誤訊息)
        """
        pass

    def prepare_environment(
        self,
        job_dir: Path,
        config: Dict[str, Any],
    ) -> Dict[str, str]:
        """準備求解器運行所需的環境變數字典。

        Args:
            job_dir: 沙盒工作目錄
            config: 作業配置字典

        Returns:
            Dict[str, str]: 注入子進程的環境變數字典
        """
        env = dict(os.environ)
        # 預設禁用 ANSYS 檔案鎖定衝突
        env["ANSYS_LOCK"] = "OFF"
        env["ANSYS_NO_GUI"] = "1"
        return env

    # ----------------------------------------------------------------------
    # 2. 作業輸入檔案與腳本準備
    # ----------------------------------------------------------------------
    @abstractmethod
    def prepare_job(self, job_dir: Path, config: Dict[str, Any]) -> Path:
        """在沙盒 workspace 中生成輸入腳本、卡片與設定檔，返回主輸入檔案路徑。

        Args:
            job_dir: 作業沙盒目錄 (內含 inputs/, workspace/, artifacts/)
            config: 工作流配置參數

        Returns:
            Path: 主輸入檔案絕對路徑 (如 .k, .jou, .mac, .py)
        """
        pass

    # ----------------------------------------------------------------------
    # 3. 求解器進程啟動與日誌導向
    # ----------------------------------------------------------------------
    def run_solver(
        self,
        job_dir: Path,
        input_file: Path,
        env: Optional[Dict[str, str]] = None,
        extra_args: Optional[List[str]] = None,
    ) -> subprocess.Popen:
        """啟動求解器子進程，標準化將 stdout/stderr 導向 workspace 日誌。

        Args:
            job_dir: 作業沙盒目錄
            input_file: 主輸入檔案路徑
            env: 環境變數字典 (可選)
            extra_args: 附加命令列引數 (可選)

        Returns:
            subprocess.Popen: 啟動之子進程物件
        """
        workspace = job_dir / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)

        cmd = self.build_command(input_file=input_file, extra_args=extra_args)
        current_env = env or self.prepare_environment(job_dir=job_dir, config={})

        stdout_path = workspace / "stdout.log"
        stderr_path = workspace / "stderr.log"

        logger.info(f"[{self.solver_name}] 啟動求解進程: {' '.join(cmd)}")
        out_f = open(stdout_path, "wb")
        err_f = open(stderr_path, "wb")

        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        proc = subprocess.Popen(
            cmd,
            cwd=str(workspace),
            env=current_env,
            stdout=out_f,
            stderr=err_f,
            creationflags=creationflags,
        )
        return proc

    def launch(self, job_dir: Path, input_file: Path) -> subprocess.Popen:
        """別名介面：啟動求解器子進程 (對齊 spec_report.md 規範)。"""
        return self.run_solver(job_dir=job_dir, input_file=input_file)

    @abstractmethod
    def build_command(
        self,
        input_file: Path,
        extra_args: Optional[List[str]] = None,
    ) -> List[str]:
        """組裝求解器啟動命令列字串清單。"""
        pass

    # ----------------------------------------------------------------------
    # 4. 日誌路徑與進度解析
    # ----------------------------------------------------------------------
    @abstractmethod
    def get_log_file_path(self, job_dir: Path) -> Path:
        """獲取該求解器主輸出日誌路徑 (如 solve.out, glstat, fluent.log)。"""
        pass

    @abstractmethod
    def parse_progress(self, job_dir: Path) -> Dict[str, Any]:
        """解析最新進度百分比、時間步、殘差與物理指標。"""
        pass

    # ----------------------------------------------------------------------
    # 5. 進程中斷與中止管理
    # ----------------------------------------------------------------------
    def terminate_process(self, proc: subprocess.Popen, timeout: float = 5.0) -> None:
        """優雅中斷求解器進程，超時則強制殺除進程樹。"""
        if proc.poll() is not None:
            return

        logger.warning(f"[{self.solver_name}] 正在終止進程 PID={proc.pid}...")
        try:
            if os.name == "nt":
                # Windows 平台上嘗試發送 CTRL_BREAK_EVENT 或 taskkill
                proc.terminate()
                try:
                    proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    logger.warning(f"[{self.solver_name}] 進程未在 {timeout}s 內退出，強制終止...")
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                        capture_output=True,
                    )
            else:
                proc.send_signal(signal.SIGTERM)
                try:
                    proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    proc.kill()
        except Exception as e:
            logger.error(f"[{self.solver_name}] 終止進程異常: {e}")

    def abort(self, proc: subprocess.Popen) -> None:
        """別名介面：優雅中斷進程 (對齊 spec_report.md 規範)。"""
        self.terminate_process(proc)

    # ----------------------------------------------------------------------
    # 6. 結果提取與產物匯出
    # ----------------------------------------------------------------------
    @abstractmethod
    def extract_artifacts(self, job_dir: Path) -> Dict[str, Any]:
        """後處理產出 summary.json 與白底 PNG 雲圖。

        Returns:
            Dict[str, Any]: 產出結果字典 (包含 metrics, artifact_paths 等)
        """
        pass

    def extract_results(self, job_dir: Path) -> Dict[str, Any]:
        """別名介面：後處理提取成果 (對齊 spec_report.md 規範)。"""
        return self.extract_artifacts(job_dir=job_dir)