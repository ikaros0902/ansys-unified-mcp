# -*- coding: utf-8 -*-
"""Unit tests for unified runtime directory resolution and deprecation wrappers."""

import os
from pathlib import Path
import pytest
import warnings

from ansys_unified_mcp.core.paths import resolve_runtime_dir
from ansys_unified_mcp.core.jobs.manager import JobManager


def test_resolve_runtime_dir_env_var_priority(tmp_path, monkeypatch):
    custom_dir = tmp_path / "custom_runtime"
    monkeypatch.setenv("ANSYS_UNIFIED_MCP_RUNTIME", str(custom_dir))

    resolved = resolve_runtime_dir()
    assert resolved == custom_dir.resolve()
    assert resolved.exists()
    assert resolved.is_dir()


def test_resolve_runtime_dir_mcp_runtime_env_var(tmp_path, monkeypatch):
    monkeypatch.delenv("ANSYS_UNIFIED_MCP_RUNTIME", raising=False)
    custom_dir = tmp_path / "custom_runtime_2"
    monkeypatch.setenv("ANSYS_MCP_RUNTIME_DIR", str(custom_dir))

    resolved = resolve_runtime_dir()
    assert resolved == custom_dir.resolve()
    assert resolved.exists()


def test_resolve_runtime_dir_repo_root(monkeypatch):
    monkeypatch.delenv("ANSYS_UNIFIED_MCP_RUNTIME", raising=False)
    monkeypatch.delenv("ANSYS_MCP_RUNTIME_DIR", raising=False)

    resolved = resolve_runtime_dir()
    # In repo development environment, resolve_runtime_dir points to repo_root / ".runtime"
    repo_root = Path(__file__).resolve().parents[2]
    expected = repo_root / ".runtime"
    assert resolved == expected
    assert resolved.exists()


def test_resolve_runtime_dir_fallback(monkeypatch, tmp_path):
    monkeypatch.delenv("ANSYS_UNIFIED_MCP_RUNTIME", raising=False)
    monkeypatch.delenv("ANSYS_MCP_RUNTIME_DIR", raising=False)

    # Mock paths.py parents[3] to a dummy non-repo path without pyproject.toml
    dummy_repo = tmp_path / "not_a_repo"
    dummy_repo.mkdir(parents=True, exist_ok=True)
    fake_appdata = tmp_path / "localappdata"
    fake_appdata.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("LOCALAPPDATA", str(fake_appdata))

    import ansys_unified_mcp.core.paths as p_mod
    orig_file = p_mod.__file__
    try:
        # Simulate __file__ residing deep inside dummy_repo/src/ansys_unified_mcp/core/paths.py
        fake_paths_file = dummy_repo / "src" / "ansys_unified_mcp" / "core" / "paths.py"
        fake_paths_file.parent.mkdir(parents=True, exist_ok=True)
        fake_paths_file.touch()
        monkeypatch.setattr(p_mod, "__file__", str(fake_paths_file))

        resolved = p_mod.resolve_runtime_dir()
        if os.name == "nt":
            assert resolved == fake_appdata / "ansys-unified-mcp"
        else:
            assert ".ansys_unified_mcp" in str(resolved)
        assert resolved.exists()
    finally:
        monkeypatch.setattr(p_mod, "__file__", orig_file)


def test_job_manager_uses_resolve_runtime(monkeypatch, tmp_path):
    runtime_mock = tmp_path / "mock_runtime"
    monkeypatch.setenv("ANSYS_UNIFIED_MCP_RUNTIME", str(runtime_mock))

    jm = JobManager(base_jobs_dir=runtime_mock / "jobs")
    assert jm.base_jobs_dir == (runtime_mock / "jobs").resolve()
    assert jm.base_jobs_dir.exists()


def test_core_visibility_deprecation_warning():
    with pytest.deprecated_call():
        import importlib
        import ansys_unified_mcp.core.visibility as core_vis
        importlib.reload(core_vis)

        from ansys_unified_mcp.core.visibility import (
            WorkspaceVisibilityMiddleware,
            product_of_module,
            COMMON_PRODUCT,
        )
        assert COMMON_PRODUCT == "common"
        assert callable(product_of_module)
        assert WorkspaceVisibilityMiddleware is not None


def test_tools_visibility_clean_import():
    from ansys_unified_mcp.tools.visibility import (
        WorkspaceVisibilityMiddleware,
        product_of_module,
        COMMON_PRODUCT,
    )
    assert COMMON_PRODUCT == "common"
    assert product_of_module("ansys_unified_mcp.products.mechanical.tools") == "mechanical"
    assert WorkspaceVisibilityMiddleware is not None
