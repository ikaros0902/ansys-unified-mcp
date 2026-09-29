"""ANSYS Unified MCP 2.0 - 後處理結果讀取抽象基類 (Base Result Reader).

定義求解結果讀取器的抽象介面、終態生命週期狀態與核心例外類別：
- BaseResultReader: 結果讀取器抽象介面
- JobNotReadyError: 作業尚未達到終態時拋出之例外
- PostprocessingError: 後處理提取或伺服器異常拋出之例外
- TERMINAL_STATES: 終態集合 {"SOLVED", "FAILED", "ABORTED"}
"""

from __future__ import annotations

import abc
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

logger = logging.getLogger(__name__)

# 模擬作業終態集合
TERMINAL_STATES: Set[str] = {"SOLVED", "FAILED", "ABORTED"}


class JobNotReadyError(Exception):
    """作業尚未處於終態 (TERMINAL) 時拋出之例外。"""
    pass


class PostprocessingError(Exception):
    """後處理提取、檔案讀取或伺服器不可用時拋出之例外。"""
    pass


class BaseResultReader(abc.ABC):
    """模擬求解結果讀取器抽象基類。"""

    @abc.abstractmethod
    def read_results(
        self,
        job_dir: Union[Path, str],
        allow_synthetic: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """從作業沙盒目錄讀取並提取求解結果。

        Args:
            job_dir: 作業沙盒根目錄或運算目錄。
            allow_synthetic: 若為 True，在無實體後處理伺服器或檔案時允許回傳合成指標；
                             若為 False，嚴格拋出 PostprocessingError。
            **kwargs: 額外參數（例如明確指定 job_status）。

        Returns:
            Dict[str, Any]: 提取之結果指標字典。

        Raises:
            JobNotReadyError: 作業未達到終態時。
            PostprocessingError: 後處理過程發生嚴重錯誤時。
        """
        raise NotImplementedError

    def find_summary_file(self, job_dir: Path) -> Optional[Path]:
        """在作業目錄及其相鄰目錄中尋找 summary.json 成果摘要檔案。"""
        candidates = [
            job_dir / "summary.json",
            job_dir / "artifacts" / "summary.json",
            job_dir.parent / "summary.json",
            job_dir.parent / "artifacts" / "summary.json",
        ]
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        return None

    def validate_terminal_state(
        self,
        job_dir: Path,
        job_status: Optional[str] = None,
    ) -> str:
        """驗證作業是否已處於終態 (TERMINAL)。

        Args:
            job_dir: 作業目錄路徑。
            job_status: 明確指定之作業狀態，若無則從 summary.json 讀取。

        Returns:
            str: 驗證通過之作業狀態字串。

        Raises:
            JobNotReadyError: 若作業未達終態或無法取得終態狀態。
        """
        status: Optional[str] = job_status

        if status is None:
            summary_path = self.find_summary_file(job_dir)
            if summary_path is not None:
                try:
                    data = json.loads(summary_path.read_text(encoding="utf-8"))
                    raw_status = data.get("status")
                    if raw_status:
                        status = str(raw_status).strip()
                except Exception as exc:
                    logger.warning("解析 summary.json 失敗: %s", exc)

        if status is None:
            raise JobNotReadyError(
                f"無法確認目錄 '{job_dir}' 的作業狀態（未找到 summary.json 或明確 job_status）。"
                f"作業必須處於終態 {TERMINAL_STATES} 方可進行後處理。"
            )

        status_upper = status.upper()
        if status_upper not in TERMINAL_STATES:
            raise JobNotReadyError(
                f"作業狀態為 '{status}'，尚未處於終態 ({TERMINAL_STATES})，無法進行後處理隔離讀取。"
            )

        return status_upper
