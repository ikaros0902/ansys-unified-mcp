# -*- coding: utf-8 -*-
"""SpaceClaim Headless 無頭腳本執行整合單元測試。"""

import pytest
from unittest.mock import patch
from pathlib import Path

from ansys_unified_mcp.products.geometry import controller
from ansys_unified_mcp.products.geometry.tools import spaceclaim_run_script


def test_spaceclaim_find_exe_structure():
    """驗證 SpaceClaim 執行檔探測函式執行無例外。"""
    exe = controller.find_spaceclaim_exe()
    assert exe is None or isinstance(exe, Path)


def test_spaceclaim_run_headless_dry_run():
    """驗證 run_spaceclaim_headless 在 dry_run=True 時正確組裝參數。"""
    res = controller.run_spaceclaim_headless(
        script_content="GetRootPart()\n",
        dry_run=True,
    )
    assert res["ok"] is True
    assert res["dry_run"] is True
    assert "/Headless=True" in res["command"]
    assert "/Splash=False" in res["command"]
    assert "/ExitAfter=True" in res["command"]
    assert any("/RunScript=" in arg for arg in res["command"])


def test_spaceclaim_run_headless_missing_input():
    """驗證未提供腳本內容且非 dry_run 時報錯。"""
    res = controller.run_spaceclaim_headless(
        script_content="",
        script_path="",
        dry_run=False,
    )
    assert res["ok"] is False
    assert "必須指定" in res["error"]


@pytest.mark.anyio
async def test_spaceclaim_tool_envelope():
    """驗證 spaceclaim_run_script 工具信封格式。"""
    envelope = await spaceclaim_run_script(
        script_content="print('hello')",
        dry_run=True,
    )
    assert envelope["ok"] is True
    assert envelope["dry_run"] is True
