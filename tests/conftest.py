# -*- coding: utf-8 -*-
"""Global pytest configuration and test environment isolation fixtures."""

from __future__ import annotations

from pathlib import Path
import pytest


@pytest.fixture(autouse=True)
def isolate_jobs_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """將所有測試期間的 Job 沙盒與 Sentinel 隊列隔離至 pytest tmp_path，徹底防止磁碟殘留與專案污染。"""
    try:
        from ansys_unified_mcp.core.jobs.manager import JobManager
        from ansys_unified_mcp.core.sentinel.daemon import get_sentinel_queue, shutdown_sentinel

        test_jobs_root = tmp_path / "jobs"
        test_jobs_root.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(JobManager, "DEFAULT_JOBS_ROOT", test_jobs_root)

        # 重置並隔離 Sentinel 單例隊列，綁定至暫存目錄
        shutdown_sentinel()
        queue = get_sentinel_queue()
        monkeypatch.setattr(queue, "job_manager", JobManager(base_jobs_dir=test_jobs_root))

        yield

        shutdown_sentinel()
    except ImportError:
        yield
