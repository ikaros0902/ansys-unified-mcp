"""ANSYS Unified MCP 2.0 - 模擬作業生命週期管理器 (Job Lifecycle Manager).

管理全局 jobs/ 命名空間、自動生成獨立沙盒目錄、防護路徑穿越攻擊、
並提供作業之檢索、列舉與生命週期追蹤。
"""

from __future__ import annotations

import os
import re
import shutil
import stat
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ansys_unified_mcp.jobs.models import (
    ExecutionMetadata,
    JobStatusEnum,
    PhysicalMetrics,
    SimulationSummary,
    VerdictEnum,
)
from ansys_unified_mcp.jobs.sandbox import JobSandbox


class JobManager:
    """模擬作業集中管理器。"""

    DEFAULT_JOBS_ROOT = Path("F:/Ming_python/ansys-unified-mcp/jobs")

    def __init__(self, base_jobs_dir: Optional[Path | str] = None) -> None:
        if base_jobs_dir:
            self.base_jobs_dir = Path(base_jobs_dir).resolve()
        else:
            self.base_jobs_dir = self.DEFAULT_JOBS_ROOT.resolve()
        self.base_jobs_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _validate_identifier(value: str, field_name: str) -> None:
        """安全校驗識別符，防止路徑穿越與非法字元注入。"""
        if not value or not isinstance(value, str):
            raise ValueError(f"{field_name} 不能為空且必須為字串")
        if ".." in value or "/" in value or "\\" in value:
            raise ValueError(f"Invalid job {field_name}: path traversal detected")
        if not re.match(r"^[a-zA-Z0-9_\-]+$", value):
            raise ValueError(
                f"Invalid job {field_name}: 僅允許英數字、底線與連字號，實際輸入: '{value}'"
            )

    def create_job(
        self,
        workflow_type: str,
        tag: str = "default",
        solver_name: str = "ANSYS",
        init_summary: bool = True,
    ) -> JobSandbox:
        """建立全新模擬作業沙盒。

        命名規則: jobs/{timestamp}_{workflow_type}_{tag}
        引入唯一微秒/短 UUID 後綴以防止高併發重複命名覆蓋。

        Args:
            workflow_type: 工作流類型 (如 drop_test, random_vibration, thermal_warpage)
            tag: 作業自訂標籤
            solver_name: 預期使用之求解器
            init_summary: 是否在 artifacts/ 初始化初始狀態之 summary.json

        Returns:
            JobSandbox: 初始化完畢之沙盒實例
        """
        self._validate_identifier(workflow_type, "workflow_type")
        self._validate_identifier(tag, "tag")

        now = datetime.now(timezone.utc)
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        unique_suffix = uuid.uuid4().hex[:6]
        job_id = f"{timestamp_str}_{unique_suffix}_{workflow_type}_{tag}"

        sandbox_dir = self.base_jobs_dir / job_id
        sandbox = JobSandbox(
            job_id=job_id,
            root_dir=sandbox_dir,
            workflow_type=workflow_type,
            tag=tag,
        )
        sandbox.initialize()

        if init_summary:
            initial_summary = SimulationSummary(
                job_id=job_id,
                workflow_type=workflow_type,
                tag=tag,
                status=JobStatusEnum.QUEUED,
                verdict=VerdictEnum.INCONCLUSIVE,
                metrics=PhysicalMetrics(),
                execution=ExecutionMetadata(
                    created_at=now.isoformat(),
                    solver_name=solver_name,
                    solver_version="2026 R1",
                ),
                artifacts={},
            )
            sandbox.save_summary(initial_summary)

        return sandbox

    def get_job(self, job_id: str) -> Optional[JobSandbox]:
        """依據 job_id 獲取沙盒實例，若不存在返回 None。"""
        self._validate_identifier(job_id, "job_id")
        candidate_dir = self.base_jobs_dir / job_id
        if not candidate_dir.is_dir():
            return None

        # 從 job_id 解析 workflow_type 與 tag
        parts = job_id.split("_")
        workflow_type = parts[3] if len(parts) >= 4 else "unknown"
        tag = "_".join(parts[4:]) if len(parts) >= 5 else "default"

        sandbox = JobSandbox(
            job_id=job_id,
            root_dir=candidate_dir,
            workflow_type=workflow_type,
            tag=tag,
        )
        return sandbox

    def list_jobs(self) -> List[JobSandbox]:
        """列出所有已存在之作業沙盒，依目錄建立時間由新到舊排序。"""
        if not self.base_jobs_dir.exists():
            return []

        sandboxes: List[JobSandbox] = []
        for entry in self.base_jobs_dir.iterdir():
            if entry.is_dir():
                job_id = entry.name
                parts = job_id.split("_")
                workflow_type = parts[3] if len(parts) >= 4 else "unknown"
                tag = "_".join(parts[4:]) if len(parts) >= 5 else "default"
                sandboxes.append(
                    JobSandbox(
                        job_id=job_id,
                        root_dir=entry,
                        workflow_type=workflow_type,
                        tag=tag,
                    )
                )

        # 依最後修改時間反向排序
        sandboxes.sort(
            key=lambda s: s.root_dir.stat().st_mtime if s.root_dir.exists() else 0,
            reverse=True,
        )
        return sandboxes

    def delete_job(self, job_id: str) -> bool:
        """安全移除作業沙盒目錄 (含解除唯讀屬性防止 PermissionError)。"""
        self._validate_identifier(job_id, "job_id")
        target_dir = self.base_jobs_dir / job_id
        if not target_dir.exists():
            return False

        def _remove_readonly(func, path, _):
            """Windows 唯讀檔案錯誤處理回調。"""
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except Exception:
                pass

        shutil.rmtree(target_dir, onerror=_remove_readonly)
        return True
