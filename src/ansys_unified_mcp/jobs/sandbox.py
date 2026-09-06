"""ANSYS Unified MCP 2.0 - 模擬作業沙盒管理環境 (Job Sandbox Environment).

提供獨立目錄結構 (inputs/, workspace/, artifacts/)、原始資產唯讀保護、
運算中繼檔案隔離與三位一體成果產物匯流。
"""

from __future__ import annotations

import ctypes
import hashlib
import os
import shutil
import stat
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from ansys_unified_mcp.jobs.models import SimulationSummary


class JobSandbox:
    """單一模擬作業專屬之隔離沙盒環境。"""

    def __init__(
        self,
        job_id: str,
        root_dir: Path | str,
        workflow_type: str = "general",
        tag: str = "default",
    ) -> None:
        self.job_id = job_id
        self.root_dir = Path(root_dir).resolve()
        self.workflow_type = workflow_type
        self.tag = tag
        self._summary_lock = threading.Lock()

        # 三層核心子目錄
        self.inputs_dir = self.root_dir / "inputs"
        self.workspace_dir = self.root_dir / "workspace"
        self.artifacts_dir = self.root_dir / "artifacts"
        self.images_dir = self.artifacts_dir / "images"

    @property
    def sandbox_dir(self) -> Path:
        """沙盒根目錄原生路徑別名（相容 PROJECT.md 與工作流合約）。"""
        return self.root_dir

    def initialize(self) -> None:
        """建立沙盒標準三層目錄結構。"""
        self.inputs_dir.mkdir(parents=True, exist_ok=True)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _compute_sha256(file_path: Path) -> str:
        """計算檔案之 SHA-256 雜湊碼以驗證資產完整性。"""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def protect_read_only(
        self, source_path: Path | str, target_name: Optional[str] = None
    ) -> Path:
        """原始資產唯讀保護機制 (Read-Only Guarantee).

        將原始 CAD (PMDB/STEP)、材料庫 XML 或分析模板複製至沙盒 inputs/，
        核驗 SHA-256 雜湊值無誤後賦予作業系統唯讀屬性，阻絕運算過程任何覆寫或污染。

        Args:
            source_path: 來源資產路徑
            target_name: 沙盒 inputs/ 中的儲存檔名 (預設為來源檔名)

        Returns:
            Path: 沙盒 inputs/ 下已設定唯讀屬性之目標檔案路徑
        """
        source = Path(source_path).resolve()
        if not source.exists():
            raise FileNotFoundError(f"來源資產檔案不存在: {source}")
        if not source.is_file():
            raise ValueError(f"來源資產必須為實體檔案而非目錄: {source}")

        dest_name = target_name or source.name
        destination = (self.inputs_dir / dest_name).resolve()

        # 邊界保護：嚴防路徑穿越超出 inputs_dir
        if not destination.is_relative_to(self.inputs_dir.resolve()):
            raise ValueError(f"目標資產寫入路徑超出 inputs 目錄範疇: {destination}")

        # 確保 inputs 目錄已就緒
        self.inputs_dir.mkdir(parents=True, exist_ok=True)

        # 計算來源檔案 SHA-256
        source_hash = self._compute_sha256(source)

        # 若目標檔案已存在且具備唯讀屬性，先解除以便覆寫更新
        if destination.exists():
            try:
                os.chmod(destination, stat.S_IWRITE)
            except OSError:
                pass

        # 採用分塊流複製，避免大檔案 OOM 並容忍外部鎖定
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(source, "rb") as src_f, open(destination, "wb") as dst_f:
            shutil.copyfileobj(src_f, dst_f, length=1024 * 1024)

        # 核驗拷貝後目標檔案 SHA-256
        dest_hash = self._compute_sha256(destination)
        if source_hash != dest_hash:
            raise IOError(f"資產複製校驗失敗: {source} 與 {destination} 雜湊值不一致")

        # 賦予唯讀權限 (移除寫入權限)
        current_mode = os.stat(destination).st_mode
        os.chmod(destination, current_mode & ~stat.S_IWRITE)

        # 在 Windows 系統上額外調用 SetFileAttributesW 確保屬性生效
        if os.name == "nt":
            try:
                FILE_ATTRIBUTE_READONLY = 0x01
                ctypes.windll.kernel32.SetFileAttributesW(
                    str(destination), FILE_ATTRIBUTE_READONLY
                )
            except Exception:
                pass

        return destination

    def write_workspace_file(
        self, relative_path: str | Path, content: str | bytes
    ) -> Path:
        """在 workspace/ 運算目錄中安全寫入運算中繼檔案 (腳本、卡片、組態)。"""
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        target = (self.workspace_dir / relative_path).resolve()

        # 邊界保護：嚴防路徑穿越超出 workspace_dir（使用 is_relative_to 阻斷前綴繞過攻擊）
        if not target.is_relative_to(self.workspace_dir.resolve()):
            raise ValueError(f"檔案寫入路徑超出 workspace 目錄範疇: {target}")

        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8")
        return target

    def save_summary(self, summary: SimulationSummary) -> Path:
        """儲存並更新沙盒成果目錄之 summary.json（線程安全）。"""
        with self._summary_lock:
            self.artifacts_dir.mkdir(parents=True, exist_ok=True)
            summary_path = self.artifacts_dir / "summary.json"

            # 登記產生物路徑
            summary.artifacts["summary_json"] = str(summary_path)
            summary.save(summary_path)
            return summary_path

    def get_summary(self) -> Optional[SimulationSummary]:
        """讀取沙盒中的 summary.json，若尚未產出則返回 None。"""
        with self._summary_lock:
            summary_path = self.artifacts_dir / "summary.json"
            if not summary_path.exists():
                return None
            return SimulationSummary.from_json_file(summary_path)

    def list_artifacts(self) -> Dict[str, str]:
        """列出 artifacts/ 目錄下所有現存產生物之對照表。"""
        result: Dict[str, str] = {}
        if not self.artifacts_dir.exists():
            return result

        for item in self.artifacts_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(self.artifacts_dir).as_posix()
                result[rel_path] = str(item.resolve())
        return result

    def validate_integrity(self) -> bool:
        """檢核沙盒目錄結構完整性。"""
        return (
            self.inputs_dir.is_dir()
            and self.workspace_dir.is_dir()
            and self.artifacts_dir.is_dir()
        )
