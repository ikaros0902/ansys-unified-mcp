# -*- coding: utf-8 -*-
"""目錄重構與 FastMCP 工具鏈 E2E 端到端防回歸測試套件。

本模組將目錄拓撲結構檢查與 FastMCP 工具鏈解析封裝為正規 pytest 測試，
納入專案 tests/e2e/ 測試矩陣中。
測試項目包含：
1. FastMCP 工具鏈 Canonical 原語工具與 Exposed 相容工具計數與無重複斷言。
2. 關鍵 CAE 模擬領域工具之存在性與完備性校驗。
3. 目錄拓撲驗證器 (Topology Verifier) 之對抗性與邊界情境測試（tmp_path 隔離建構）。
4. 專案根目錄拓撲現況稽核與漸進式過渡期相容判定。
5. CLI 驗證腳本獨立執行與 JSON 輸出結構完整性測試。
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest

# 確保專案根目錄與 src 加入模組搜尋路徑
REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
SCRIPTS_DIR = REPO_ROOT / "scripts"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.verify_directory_topology import (
    EXPECTED_CORE_DIRS,
    FORBIDDEN_ROOT_DIRS,
    REQUIRED_RUNTIME_SUBDIRS,
    TopologyVerificationResult,
    check_gitignore_contains_runtime,
    verify_directory_topology,
)
from scripts.verify_fastmcp_tools import (
    CANONICAL_EXPECTED_COUNT,
    CANONICAL_MIN_THRESHOLD,
    EXPOSED_EXPECTED_COUNT,
    EXPOSED_MIN_THRESHOLD,
    FastMCPVerificationResult,
    verify_fastmcp_tools,
    verify_fastmcp_tools_sync,
)


# ============================================================================
# 1. FastMCP 工具鏈解析與註冊測試
# ============================================================================


def test_fastmcp_canonical_pruned_tools_count() -> None:
    """驗證預設模式 (Pruned) 下 FastMCP Canonical 工具總數達標且無重複。"""
    result = verify_fastmcp_tools_sync()

    # 斷言 Canonical 工具數滿足歷史相容基線 (>= 143) 與當前規格 (預期 155)
    assert result.canonical_ok is True, (
        f"Canonical 工具數未達標：實際 {result.canonical_count} 個，"
        f"門檻 >={CANONICAL_MIN_THRESHOLD}，預期 {CANONICAL_EXPECTED_COUNT}"
    )
    assert result.canonical_count >= CANONICAL_MIN_THRESHOLD
    assert len(result.duplicate_canonical_names) == 0, (
        f"發現重複的 Canonical 工具名稱：{result.duplicate_canonical_names}"
    )


def test_fastmcp_exposed_aliases_tools_count() -> None:
    """驗證相容模式 (Exposed) 下包含 Deprecated Aliases 之總工具數達標。"""
    result = verify_fastmcp_tools_sync()

    # 斷言 Exposed 工具數滿足相容基線 (>= 200) 與當前規格 (預期 213)
    assert result.exposed_ok is True, (
        f"Exposed 相容工具數未達標：實際 {result.exposed_count} 個，"
        f"門檻 >={EXPOSED_MIN_THRESHOLD}，預期 {EXPOSED_EXPECTED_COUNT}"
    )
    assert result.exposed_count >= EXPOSED_MIN_THRESHOLD
    assert len(result.duplicate_exposed_names) == 0, (
        f"發現重複的 Exposed 工具名稱：{result.duplicate_exposed_names}"
    )
    assert result.is_valid is True, "FastMCP 工具鏈綜合驗證未通過"


def test_fastmcp_core_simulation_tools_presence() -> None:
    """驗證核心 CAE 物理模擬與工作流工具均完整註冊於工具清單中。"""
    result = verify_fastmcp_tools_sync()
    tool_names = set(result.canonical_tool_names)

    # 抽樣涵蓋 Workbench, Mechanical, Fluent, Geometry, DPF, Workflow 核心工具
    essential_tools = {
        "workflow_run_drop_test",
        "workflow_run_shock_analysis",
        "workflow_run_random_vibration",
        "workflow_run_thermal_warpage",
        "mechanical_solve_analysis",
        "mechanical_get_model_info",
        "fluent_iterate",
        "geometry_export",
        "dpf_extract_structural_results",
        "optislang_connect",
        "create_static_structural_system_live",
    }

    missing_tools = essential_tools - tool_names
    assert not missing_tools, f"核心模擬工具遺失，未成功註冊：{missing_tools}"


# ============================================================================
# 2. 目錄拓撲驗證器邏輯與邊界情境測試 (Tmp_Path 隔離沙盒)
# ============================================================================


def _create_mock_compliant_repo(base_dir: Path) -> Path:
    """建立一個符合 5 大目錄 + .runtime/ + .gitignore 規格的沙盒目錄。"""
    for core_dir in EXPECTED_CORE_DIRS:
        (base_dir / core_dir).mkdir(parents=True, exist_ok=True)

    for runtime_subdir in REQUIRED_RUNTIME_SUBDIRS:
        (base_dir / runtime_subdir).mkdir(parents=True, exist_ok=True)

    gitignore_path = base_dir / ".gitignore"
    gitignore_path.write_text(
        "# 暫存與執行目錄\n.runtime/\n*.log\n__pycache__/\n", encoding="utf-8"
    )
    return base_dir


def test_topology_verifier_passes_on_compliant_structure(tmp_path: Path) -> None:
    """測試拓撲驗證器在完全合規之目錄結構下應判定為 True (PASS)。"""
    mock_repo = _create_mock_compliant_repo(tmp_path / "compliant_repo")
    result: TopologyVerificationResult = verify_directory_topology(mock_repo)

    assert result.is_valid is True
    assert result.core_dirs_ok is True
    assert result.forbidden_dirs_ok is True
    assert result.runtime_structure_ok is True
    assert result.gitignore_ok is True
    assert set(result.actual_non_hidden_dirs) == EXPECTED_CORE_DIRS
    assert len(result.forbidden_dirs_present) == 0
    assert len(result.missing_runtime_dirs) == 0


def test_topology_verifier_fails_on_forbidden_directories(tmp_path: Path) -> None:
    """測試拓撲驗證器在根目錄殘留舊資料夾時能精確識別並判定失敗。"""
    mock_repo = _create_mock_compliant_repo(tmp_path / "forbidden_dirs_repo")

    # 注入被禁止的舊目錄
    (mock_repo / "jobs").mkdir()
    (mock_repo / "skills").mkdir()
    (mock_repo / "workbench_queue").mkdir()

    result: TopologyVerificationResult = verify_directory_topology(mock_repo)

    assert result.is_valid is False
    assert result.forbidden_dirs_ok is False
    assert set(result.forbidden_dirs_present) == {"jobs", "skills", "workbench_queue"}
    assert result.core_dirs_ok is False  # 非隱藏目錄多於 5 個


def test_topology_verifier_fails_on_missing_or_extra_core_dirs(
    tmp_path: Path,
) -> None:
    """測試拓撲驗證器在核心目錄數量不足或出現多餘非隱藏目錄時判定失敗。"""
    mock_repo = _create_mock_compliant_repo(tmp_path / "wrong_core_dirs_repo")

    # 刪除 docs 目錄
    (mock_repo / "docs").rmdir()
    # 增加非規範資料夾
    (mock_repo / "extra_unauthorized").mkdir()

    result: TopologyVerificationResult = verify_directory_topology(mock_repo)

    assert result.is_valid is False
    assert result.core_dirs_ok is False
    assert "docs" in result.missing_core_dirs
    assert "extra_unauthorized" in result.unexpected_dirs


def test_topology_verifier_fails_on_missing_runtime_subdirs(tmp_path: Path) -> None:
    """測試拓撲驗證器在 .runtime/ 內部缺少必要子目錄時判定失敗。"""
    mock_repo = _create_mock_compliant_repo(tmp_path / "broken_runtime_repo")

    # 移除 .runtime/queue
    (mock_repo / ".runtime" / "queue").rmdir()

    result: TopologyVerificationResult = verify_directory_topology(mock_repo)

    assert result.is_valid is False
    assert result.runtime_structure_ok is False
    assert ".runtime/queue" in result.missing_runtime_dirs


def test_topology_verifier_fails_when_gitignore_lacks_runtime(
    tmp_path: Path,
) -> None:
    """測試拓撲驗證器在 .gitignore 缺少 .runtime/ 規則時判定失敗。"""
    mock_repo = _create_mock_compliant_repo(tmp_path / "no_gitignore_runtime")

    # 覆寫 .gitignore，移除 .runtime 規則
    gitignore_path = mock_repo / ".gitignore"
    gitignore_path.write_text("# 僅有快取\n__pycache__/\n", encoding="utf-8")

    result: TopologyVerificationResult = verify_directory_topology(mock_repo)

    assert result.is_valid is False
    assert result.gitignore_ok is False
    assert result.gitignore_has_runtime is False


# ============================================================================
# 3. 專案根目錄拓撲現況稽核與漸進式相容驗證 (Progressive Testability)
# ============================================================================


def test_current_repo_directory_topology_status() -> None:
    """對目前專案根目錄執行客觀拓撲檢查，並根據遷移進度提供相容性判定。"""
    result = verify_directory_topology(REPO_ROOT)

    # 檢查是否啟用強制門禁模式（由 M4 驗收時透過環境變數傳入）
    strict_enforce = os.environ.get("TOPOLOGY_STRICT_ENFORCE") == "1"

    if strict_enforce:
        # 強制模式：必須 100% 符合 5 大核心目錄架構
        assert result.is_valid is True, (
            f"目錄拓撲嚴格門禁失敗：{result.messages}"
        )
    else:
        # 漸進式測試適配：若尚未完成 M2 物理搬遷，驗證驗證器能精確報告未收斂狀態
        if result.is_valid:
            # 已收斂完成
            assert result.core_dirs_ok is True
            assert result.forbidden_dirs_ok is True
            assert result.runtime_structure_ok is True
            assert result.gitignore_ok is True
        else:
            # 尚未收斂完成：驗證器必須如實偵測出未完成的項目，不發生非預期例外
            assert isinstance(result.actual_non_hidden_dirs, list)
            assert len(result.actual_non_hidden_dirs) > 0
            # 確保訊息包含客觀原因
            assert len(result.messages) > 0


# ============================================================================
# 4. CLI 腳本命令列獨立執行測試
# ============================================================================


def test_cli_verify_directory_topology_execution(tmp_path: Path) -> None:
    """測試 scripts/verify_directory_topology.py 透過命令列執行並輸出 JSON。"""
    mock_repo = _create_mock_compliant_repo(tmp_path / "cli_test_repo")
    script_path = SCRIPTS_DIR / "verify_directory_topology.py"

    cmd = [
        sys.executable,
        str(script_path),
        "--root",
        str(mock_repo),
        "--json",
    ]

    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", check=False
    )

    assert proc.returncode == 0, f"腳本執行失敗，stderr: {proc.stderr}"
    data = json.loads(proc.stdout)
    assert data["is_valid"] is True
    assert data["core_dirs_ok"] is True
    assert data["forbidden_dirs_ok"] is True
    assert data["runtime_structure_ok"] is True
    assert data["gitignore_ok"] is True


def test_cli_verify_fastmcp_tools_execution() -> None:
    """測試 scripts/verify_fastmcp_tools.py 透過命令列執行並輸出 JSON。"""
    script_path = SCRIPTS_DIR / "verify_fastmcp_tools.py"

    cmd = [
        sys.executable,
        str(script_path),
        "--json",
    ]

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR)

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )

    assert proc.returncode == 0, f"腳本執行失敗，stderr: {proc.stderr}"
    # 由於可能包含 logging output，擷取 JSON 部分
    stdout_text = proc.stdout.strip()
    json_start = stdout_text.find("{")
    assert json_start != -1, f"未找到 JSON 輸出：{stdout_text}"
    json_str = stdout_text[json_start:]

    data = json.loads(json_str)
    assert data["is_valid"] is True
    assert data["canonical_count"] >= CANONICAL_MIN_THRESHOLD
    assert data["exposed_count"] >= EXPOSED_MIN_THRESHOLD
