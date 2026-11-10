# -*- coding: utf-8 -*-
"""單元測試：多版本 ANSYS 動態調度、常駐診斷工具與 ASD-STE100 合規性驗證。

依據 BUSINESS_RULES.md 之 Rule M01, Rule M02, Rule M03 進行自動化驗收。
"""

from __future__ import annotations

import os
from pathlib import Path
import pytest

from ansys_unified_mcp.config import config, discover_installed_versions, set_active_version
from ansys_unified_mcp.shared import INSTRUCTIONS, mcp
from ansys_unified_mcp.tools.connection_tools import (
    check_ansys_installation,
    ans_list_installed_versions,
    ans_set_active_version,
)


def test_discover_installed_versions():
    """驗證 discover_installed_versions 正常掃描並回傳版本字典。"""
    discovered = discover_installed_versions()
    assert isinstance(discovered, dict)
    for ver, path in discovered.items():
        assert isinstance(ver, str)
        assert ver.isdigit()
        assert isinstance(path, Path)
        assert path.is_dir()


def test_check_ansys_installation_envelope():
    """驗證 check_ansys_installation 回傳標準扁平信封。"""
    result = check_ansys_installation()
    assert isinstance(result, dict)
    assert result.get("ok") is True
    assert "version" in result
    assert "installed_versions" in result
    assert isinstance(result["installed_versions"], list)
    assert "runwb2" in result
    assert "mechanical" in result
    assert "fluent" in result
    assert "spaceclaim" in result


def test_ans_list_installed_versions():
    """驗證 ans_list_installed_versions 能列出所有本機安裝之版本資訊。"""
    result = ans_list_installed_versions()
    assert isinstance(result, dict)
    assert result.get("ok") is True
    assert "active_version" in result
    assert "installed_versions" in result
    assert "total_installed" in result
    assert isinstance(result["installed_versions"], list)


def test_dynamic_version_switching():
    """驗證 set_active_version 與 ans_set_active_version 執行期切換。"""
    discovered = discover_installed_versions()
    if not discovered:
        pytest.skip("No ANSYS installation found on this machine.")

    # 選擇目前可用的一個合法版本
    target_ver = next(iter(discovered.keys()))
    res = ans_set_active_version(target_ver)
    assert res.get("ok") is True
    assert res.get("active_version") == target_ver
    assert config.version == target_ver
    assert os.environ.get("ANSYS_VERSION") == target_ver

    # 測試切換至不存在之版本應回傳標準失敗信封，不得拋出例外
    fail_res = ans_set_active_version("99999")
    assert fail_res.get("ok") is False
    assert "not found" in fail_res.get("error", "").lower()


def test_instructions_ste100_compliance():
    """驗證 shared.INSTRUCTIONS 遵守 ASD-STE100 規範（無分號、短句、清晰規則）。"""
    assert ";" not in INSTRUCTIONS, "INSTRUCTIONS contains semicolons, violating ASD-STE100 Rule 8.1."

    # 逐句驗證長度（標題除外）
    lines = [line.strip() for line in INSTRUCTIONS.splitlines() if line.strip()]
    for line in lines:
        if line.startswith(("#", "1.", "2.", "3.", "4.", "5.")):
            continue
        # 以句點切割句子
        sentences = [s.strip() for s in line.split(".") if s.strip()]
        for s in sentences:
            words = s.split()
            assert len(words) <= 20, f"Sentence exceeds 20 words cap ({len(words)} words): '{s}'"


def test_mcp_config_example_and_clean_environment():
    """驗證開源設定範例存在且全專案核心模組無硬編碼路徑外洩。"""
    repo_root = Path(__file__).resolve().parents[2]
    example_cfg = repo_root / "mcp_config.example.json"
    assert example_cfg.is_file(), "mcp_config.example.json must exist in repository root."

    content = example_cfg.read_text(encoding="utf-8")
    assert "Ming_python" not in content, "mcp_config.example.json must not leak local username paths."

    # 檢查 config.py 與 connection_tools.py
    for py_file in ("src/ansys_unified_mcp/config.py", "src/ansys_unified_mcp/tools/connection_tools.py"):
        txt = (repo_root / py_file).read_text(encoding="utf-8")
        assert "Ming_python" not in txt, f"{py_file} must not contain hardcoded private paths."
