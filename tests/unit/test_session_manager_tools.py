# -*- coding: utf-8 -*-
"""Unit tests for ansys_unified_mcp.tools.session_manager_tools.

本檔測試「工具代理層」：驗證 4 個 @mcp.tool 是否正確委派至
AnsSessionManager 對應方法、是否正確以 as_envelope 包裝回傳信封，以及
是否確實註冊進 FastMCP 工具表（import-time 註冊失敗無法靠 AST 檢查攔住，
須有實際斷言）。

委派邏輯本身（如 geometry/fluent 無獨立 connect 而委派至 launch）已由
tests/unit/test_session_manager.py 覆蓋，本檔不重複測試該部分細節。
"""

from __future__ import annotations

import asyncio

import pytest
from unittest.mock import patch

from ansys_unified_mcp.shared import mcp
from ansys_unified_mcp.tools import session_manager_tools as tools


@pytest.mark.parametrize(
    "tool_name",
    [
        "ans_session_connect",
        "ans_session_launch",
        "ans_session_status",
        "ans_session_disconnect",
    ],
)
def test_tool_registered_in_mcp(tool_name):
    """四個工具函式必須確實註冊進 FastMCP 工具表（import 階段未被靜默吞掉）。

    透過 mcp.get_tool() 實際查詢工具表而非讀取私有屬性，確保與 FastMCP 的
    公開查詢行為一致——若 @mcp.tool() 裝飾階段拋出例外（如本次修復前的
    **kwargs 簽名問題），此測試會直接因 import 失敗而報 collection error，
    等同於客觀攔截。
    """
    found = asyncio.run(mcp.get_tool(tool_name))
    assert found is not None


def test_ans_session_connect_dispatches_with_options():
    """ans_session_connect 應將 options 字典展開為關鍵字引數委派給 session_manager.connect。"""
    with patch.object(
        tools.session_manager, "connect", return_value={"ok": True, "port": 10000}
    ) as mock_connect:
        result = tools.ans_session_connect("mechanical", options={"port": 10000, "pid": 456})

    mock_connect.assert_called_once_with("mechanical", port=10000, pid=456)
    assert result == {"ok": True, "port": 10000}


def test_ans_session_connect_options_defaults_to_empty_dict():
    """省略 options 時應以空字典呼叫，而非傳入 None 造成 TypeError。"""
    with patch.object(
        tools.session_manager, "connect", return_value={"ok": True}
    ) as mock_connect:
        tools.ans_session_connect("optislang")

    mock_connect.assert_called_once_with("optislang")


def test_ans_session_launch_dispatches_with_options():
    """ans_session_launch 應委派至 session_manager.launch 並包裝信封。"""
    with patch.object(
        tools.session_manager, "launch", return_value={"ok": True, "key": "launched"}
    ) as mock_launch:
        result = tools.ans_session_launch("mechanical", options={"batch": True})

    mock_launch.assert_called_once_with("mechanical", batch=True)
    assert result == {"ok": True, "key": "launched"}


def test_ans_session_status_dispatches_with_options():
    """ans_session_status 應委派至 session_manager.status 並包裝信封。"""
    with patch.object(
        tools.session_manager, "status", return_value={"connected": True}
    ) as mock_status:
        result = tools.ans_session_status("optislang")

    mock_status.assert_called_once_with("optislang")
    assert result["ok"] is True
    assert result["connected"] is True


def test_ans_session_disconnect_dispatches_with_options():
    """ans_session_disconnect 應委派至 session_manager.disconnect 並包裝信封。"""
    with patch.object(
        tools.session_manager, "disconnect", return_value={"ok": True, "message": "Disconnected."}
    ) as mock_disconnect:
        result = tools.ans_session_disconnect("fluent")

    mock_disconnect.assert_called_once_with("fluent")
    assert result == {"ok": True, "message": "Disconnected."}


@pytest.mark.parametrize(
    "tool_fn",
    [
        tools.ans_session_connect,
        tools.ans_session_launch,
        tools.ans_session_status,
        tools.ans_session_disconnect,
    ],
)
def test_unsupported_product_returns_error_envelope(tool_fn):
    """未知產品名稱應經真實 AnsSessionManager 回傳失敗信封，不 mock 掉驗證邏輯本身。"""
    result = tool_fn("unknown_product")
    assert result["ok"] is False
    assert "不支援" in result["error"]
