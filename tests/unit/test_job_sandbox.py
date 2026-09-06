# -*- coding: utf-8 -*-
"""Tier 2 單元測試：模擬作業沙盒生命週期與資產保護測試

覆蓋 R1 規範核心要素：
1. JobSandbox 命名空間隔離與三層目錄結構 (inputs/, workspace/, artifacts/)
2. 原始資產唯讀保護 (SHA-256 一致性與唯讀權限鎖定)
3. 路徑穿透攻擊防護 (Path traversal prevention)
4. 三位一體標準產出 summary.json 結構與 Pydantic 資料驗證
5. 多作業空間環境隔離性
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import pytest

from ansys_unified_mcp.jobs.manager import JobManager
from ansys_unified_mcp.jobs.sandbox import JobSandbox
from ansys_unified_mcp.jobs.models import (
    SimulationSummary,
    PhysicalMetrics,
    ExecutionMetadata,
    JobStatusEnum,
    VerdictEnum,
)


class TestJobSandboxLifecycle:
    """測試沙盒建立、三層目錄拓撲與路徑安全。"""

    def test_sandbox_directory_creation(self, tmp_path: Path) -> None:
        """驗證沙盒建立時自動生成 inputs/, workspace/, artifacts/ 三層目錄。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("drop_test", tag="box_drop")

        sandbox_dir = getattr(sandbox, "root_dir", getattr(sandbox, "job_dir", None))
        assert sandbox_dir is not None and sandbox_dir.exists(), "沙盒主目錄應存在"
        assert sandbox.inputs_dir.exists(), "inputs 目錄應存在"
        assert sandbox.workspace_dir.exists(), "workspace 目錄應存在"
        assert sandbox.artifacts_dir.exists(), "artifacts 目錄應存在"
        assert sandbox.images_dir.exists(), "artifacts/images 目錄應存在"

        # 斷言沙盒命名規則包含 timestamp、workflow_type 與 tag
        assert "drop_test" in sandbox_dir.name
        assert "box_drop" in sandbox_dir.name

    def test_path_traversal_attack_prevention(self, tmp_path: Path) -> None:
        """驗證當傳入帶有路徑穿越之 tag 時，強制拒絕並拋出 ValueError。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")

        with pytest.raises(ValueError, match="path traversal detected"):
            manager.create_job("static_structural", tag="../../etc/passwd")

        with pytest.raises(ValueError, match="path traversal detected"):
            manager.create_job("modal", tag="..\\system32\\calc")

    def test_workspace_isolation_between_jobs(self, tmp_path: Path) -> None:
        """驗證不同 Job 之間的 workspace 彼此完全隔離，互不干擾。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        job1 = manager.create_job("thermal", tag="run1")
        job2 = manager.create_job("thermal", tag="run2")

        # 在 job1 workspace 建立運算暫存檔
        temp_file_job1 = job1.workspace_dir / "solve.out"
        temp_file_job1.write_text("JOB1 LOG STREAM", encoding="utf-8")

        # 斷言 job2 workspace 絕不受影響
        temp_file_job2 = job2.workspace_dir / "solve.out"
        assert not temp_file_job2.exists(), "Job2 的工作區不應包含 Job1 的檔案"


class TestAssetProtection:
    """測試原始 CAD/XML 資產之唯讀保護機制。"""

    def test_read_only_protection_and_hash_integrity(self, tmp_path: Path) -> None:
        """驗證原始資產拷貝前後 SHA-256 不變，且 inputs/ 下之複本具備唯讀保護。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("thermal_warpage", tag="pcb_layer")

        # 建立外部來源資產
        source_dir = tmp_path / "source_assets"
        source_dir.mkdir(parents=True, exist_ok=True)
        cad_file = source_dir / "sample_model.pmdb"
        cad_content = b"ORIGINAL_BINARY_CAD_DATA_V2026_BLOCK"
        cad_file.write_bytes(cad_content)

        # 計算原始 SHA-256
        orig_hash = hashlib.sha256(cad_content).hexdigest()

        # 執行唯讀保護拷貝 (支援單一 Path 或 list)
        if hasattr(sandbox, "protect_read_only"):
            try:
                target_file = sandbox.protect_read_only(cad_file)
            except (TypeError, ValueError):
                target_file = sandbox.protect_read_only([cad_file])[0]
        else:
            target_file = sandbox.inputs_dir / cad_file.name

        # 1. 斷言複本哈希值完全吻合
        copied_hash = hashlib.sha256(target_file.read_bytes()).hexdigest()
        assert copied_hash == orig_hash, "拷貝至 inputs/ 之資產哈希值必須完全吻合"

        # 2. 斷言 inputs/ 檔案已設定唯讀保護 (在 Windows 下寫入應拋出 PermissionError)
        with pytest.raises(PermissionError):
            with open(target_file, "a", encoding="utf-8") as f:
                f.write("OVERWRITE_ATTEMPT")

        # 3. 清理：解除唯讀屬性以利 tmp_path 自動刪除
        os.chmod(target_file, stat.S_IWRITE)


class TestSummaryJsonGeneration:
    """測試 summary.json 標準產出與指標結構校驗。"""

    def test_summary_json_schema_and_metrics(self, tmp_path: Path) -> None:
        """驗證標準 summary.json 包含所有核心物理純量指標與狀態裁決。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("random_vibration", tag="bracket_psd")

        now = datetime.now(timezone.utc)
        summary = SimulationSummary(
            job_id=sandbox.job_id,
            workflow_type="random_vibration",
            tag="bracket_psd",
            status=JobStatusEnum.SOLVED,
            verdict=VerdictEnum.PASS,
            failure_reasons=[],
            metrics=PhysicalMetrics(
                max_equivalent_stress_mpa=185.4,
                material_yield_strength_mpa=250.0,
                safety_factor=1.348,
                max_total_deformation_mm=0.42,
                first_mode_frequency_hz=128.5,
                effective_mass_ratio_x=0.932,
                effective_mass_ratio_y=0.915,
                effective_mass_ratio_z=0.908,
            ),
            execution=ExecutionMetadata(
                created_at=now.isoformat(),
                started_at=now.isoformat(),
                finished_at=now.isoformat(),
                duration_seconds=135.0,
                solver_name="ANSYS Mechanical",
                solver_version="2026 R1",
                pid=54321,
                exit_code=0,
            ),
            artifacts={
                "summary_json": str(sandbox.artifacts_dir / "summary.json"),
                "overview_html": str(sandbox.artifacts_dir / "overview.html"),
            },
        )

        # 儲存 summary.json
        summary_path = sandbox.save_summary(summary)
        assert summary_path.exists(), "summary.json 應成功生成於 artifacts/ 目錄"

        # 讀取並校驗內容
        loaded = sandbox.get_summary()
        assert loaded is not None
        assert loaded.job_id == sandbox.job_id
        assert loaded.verdict == VerdictEnum.PASS
        assert loaded.metrics.safety_factor == pytest.approx(1.348, rel=1e-3)
        assert loaded.metrics.effective_mass_ratio_z >= 0.90
