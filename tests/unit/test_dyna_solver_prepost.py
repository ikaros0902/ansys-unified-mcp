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

