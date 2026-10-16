# -*- coding: utf-8 -*-
"""LS-DYNA Solver 與 LS-PrePost 整合單元測試。"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from ansys_unified_mcp.products.dyna import controller
from ansys_unified_mcp.products.dyna.tools import dyna_solve, dyna_run_prepost


def test_dyna_controller_find_solver_and_prepost():
    """驗證求解器與 PrePost 探測函式正常執行不崩潰。"""
    # 執行探測（若有安裝則回傳 Path，若無則回傳 None）
    solver = controller.find_dyna_solver()
    prepost = controller.find_prepost()
    
    # 只要執行過程無例外即代表跨平台邏輯健全
    assert solver is None or isinstance(solver, Path)
    assert prepost is None or isinstance(prepost, Path)


def test_dyna_solve_dry_run(tmp_path):
    """驗證 dyna_solve 在 dry_run=True 時正確產生執行命令。"""
    k_file = tmp_path / "test_drop.k"
    k_file.write_text("*KEYWORD\n*END\n", encoding="utf-8")

    res = controller.solve_keyword(
        k_file_path=str(k_file),
        ncpu=8,
        memory="250m",
        dry_run=True,
    )

    assert res["ok"] is True
    assert res["dry_run"] is True
    assert "command" in res
    assert "ncpu=8" in res["command"]
    assert "memory=250m" in res["command"]
    assert res["k_file"] == str(k_file)


def test_dyna_solve_missing_file():
    """驗證檔案不存在時回傳明確錯誤。"""
    res = controller.solve_keyword(
        k_file_path="C:/non_existent_path_xyz123/model.k",
        dry_run=False,
    )
    assert res["ok"] is False
    assert "不存在" in res["error"]


def test_dyna_run_prepost_dry_run():
    """驗證 run_prepost 在 dry_run=True 時正確建立無頭批次執行參數。"""
    res = controller.run_prepost(
        script_content="open d3plot\nw cfile\n",
        dry_run=True,
    )
    assert res["ok"] is True
    assert res["dry_run"] is True
    assert "-n" in res["command"]
    assert "-c" in res["command"]


def test_dyna_tools_envelope(tmp_path):
    """驗證 MCP 工具層的信封格式封裝。"""
    k_file = tmp_path / "box.k"
    k_file.write_text("*KEYWORD\n*END\n", encoding="utf-8")

    envelope = dyna_solve(
        k_file_path=str(k_file),
        ncpu=2,
        dry_run=True,
    )
    assert envelope["ok"] is True
    assert envelope["dry_run"] is True

    prepost_envelope = dyna_run_prepost(
        script_content="exit\n",
        dry_run=True,
    )
    assert prepost_envelope["ok"] is True
    assert prepost_envelope["dry_run"] is True


def test_dyna_solve_negative_ncpu_passthrough(tmp_path):
    """驗證負 ncpu（SMP 一致性模式）會原樣組進命令字串，不被攔截。"""
    k_file = tmp_path / "smp.k"
    k_file.write_text("*KEYWORD\n*END\n", encoding="utf-8")

    res = controller.solve_keyword(
        k_file_path=str(k_file),
        ncpu=-4,
        dry_run=True,
    )
    assert res["ok"] is True
    assert "ncpu=-4" in res["command"]


def test_dyna_solve_precision_default_and_sp(tmp_path):
    """驗證 precision 參數預設為 dp，且 sp 時會傳給 find_dyna_solver。"""
    k_file = tmp_path / "sp.k"
    k_file.write_text("*KEYWORD\n*END\n", encoding="utf-8")

    with patch.object(controller, "find_dyna_solver") as mock_find:
        mock_find.return_value = None
        controller.solve_keyword(k_file_path=str(k_file), dry_run=True)
        mock_find.assert_called_once_with(precision="dp")

    with patch.object(controller, "find_dyna_solver") as mock_find_sp:
        mock_find_sp.return_value = None
        controller.solve_keyword(k_file_path=str(k_file), precision="sp", dry_run=True)
        mock_find_sp.assert_called_once_with(precision="sp")


def test_dyna_solve_missing_solver_error_lists_searched_paths():
    """驗證找不到求解器時的錯誤訊息包含已搜尋的路徑說明（可行動性）。"""
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".k", delete=False) as tf:
        tf.write(b"*KEYWORD\n*END\n")
        tmp_k = tf.name
    try:
        with patch.object(controller, "find_dyna_solver", return_value=None):
            res = controller.solve_keyword(k_file_path=tmp_k, dry_run=False)
        assert res["ok"] is False
        assert "AWP_ROOT" in res["error"]
        assert "lsdyna_dp.exe" in res["error"]
    finally:
        os.unlink(tmp_k)


def test_dyna_tools_have_annotations():
    """驗證 dyna_* / lsdyna_* 工具已註冊 MCP annotations（mcp-builder 慣例）。"""
    from ansys_unified_mcp.shared import mcp
    import asyncio

    tools = asyncio.run(mcp.list_tools())
    by_name = {t.name: t for t in tools}
    for name in (
        "dyna_solve",
        "dyna_run_prepost",
        "dyna_create_keyword_deck",
        "dyna_export_keyword_file",
        "dyna_list_keyword_types",
        "lsdyna_setup_shock_analysis",
        "lsdyna_setup_drop_test",
    ):
        assert name in by_name, f"{name} 未註冊"
        assert by_name[name].annotations is not None, f"{name} 缺少 annotations"

