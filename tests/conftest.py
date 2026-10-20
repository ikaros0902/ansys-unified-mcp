# -*- coding: utf-8 -*-
"""Global pytest configuration and test environment isolation fixtures."""

from __future__ import annotations

from pathlib import Path
import pytest


@pytest.fixture(autouse=True)
def isolate_session_registry(request: pytest.FixtureRequest):
    """隔離全域 core.sessions.registry 單例與 facade 層探活快取。

    與 isolate_jobs_directory 平行存在、互不相依：該 fixture 處理
    JobManager/sentinel 沙盒目錄，本 fixture 處理 SessionRegistry 連線
    快取與各 Controller 的 _PROBE_CACHE。

    同步清空 MechanicalController/WorkbenchController 的 _PROBE_CACHE
    （以 str(id(session)) 為鍵的類別層級字典）：CPython 可能在前一個
    session 物件被 GC 後，把同一個 id 重新分配給下一個測試新建的 mock
    session，若不清這個快取，可能讓已死亡 session 的 id 被新 session
    重用後誤判為「仍存活」而跳過探活。

    pytest -m integration 下略過清空：整合測試連接真實 ANSYS 服務，
    `owned=True` 的連線記錄代表服務自行啟動的實例，若在測試前後被這個
    fixture 清空會丟失追蹤，導致該行程無法經由 cleanup_owned() 正常
    終止而洩漏（連線不會被真的斷開，只是記憶體記錄被清掉）。
    """
    if "integration" in request.node.keywords:
        yield
        return

    from ansys_unified_mcp.core.sessions import registry
    from ansys_unified_mcp.products.mechanical.facade import MechanicalController
    from ansys_unified_mcp.products.workbench.facade import WorkbenchController

    def _clear():
        registry.clear_all()
        MechanicalController._PROBE_CACHE.clear()
        WorkbenchController._PROBE_CACHE.clear()

    _clear()
    yield
    _clear()


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
