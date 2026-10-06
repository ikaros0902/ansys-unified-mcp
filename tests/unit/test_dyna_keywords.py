# -*- coding: utf-8 -*-
"""LS-DYNA PyDYNA 離線 keyword deck 生成冒煙測試。

純離線驗證：不需 LS-DYNA solver、不需實機、不做網路，僅驗證 PyDYNA Deck
物件模型組裝之 .k 文字內容與工具層信封回傳格式。
"""

from __future__ import annotations

import pytest

pytest.importorskip("ansys.dyna", reason="選用依賴 ansys-dyna-core 未安裝")

from ansys_unified_mcp.products.dyna.facade import controller


def test_create_keyword_deck_contains_control_termination():
    """deck 生成須含 *CONTROL_TERMINATION 卡片且 endtim 數值正確寫入文字中。"""
    result = controller.create_keyword_deck(endtim=5.0)
    assert result["ok"] is True
    assert "*CONTROL_TERMINATION" in result["deck_text"]
    assert "*CONTROL_TERMINATION" in result["cards"]
    # endtim 以浮點數格式寫入卡片內容（PyDYNA 預設固定寬度格式輸出 5.0）
    assert "5.0" in result["deck_text"]
    assert result["endtim"] == 5.0


def test_create_keyword_deck_with_hourglass_control():
    """啟用 hourglass_control 時須附加 *CONTROL_ENERGY 卡片。"""
    result = controller.create_keyword_deck(endtim=2.5, hourglass_control=True)
    assert result["ok"] is True
    assert "*CONTROL_ENERGY" in result["deck_text"]
    assert "*CONTROL_ENERGY" in result["cards"]
    assert "*CONTROL_TERMINATION" in result["cards"]


def test_export_keyword_file_writes_k_file(tmp_path):
    """export 工具須寫出 .k 檔，內容含 *KEYWORD，測完由 tmp_path 自動清理。"""
    output_file = tmp_path / "smoke_test_deck.k"
    result = controller.export_keyword_file(output_path=str(output_file), endtim=10.0)

    assert result["ok"] is True
    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")
    assert "*KEYWORD" in content
    assert "*CONTROL_TERMINATION" in content
    assert result["file_path"] == str(output_file)


def test_list_keyword_types_returns_envelope():
    """keyword 類別清單工具須回傳 ok=True 與非空清單。"""
    result = controller.list_keyword_types()
    assert result["ok"] is True
    assert isinstance(result["keyword_types"], list)
    assert len(result["keyword_types"]) > 0
    assert "ControlTermination" in result["keyword_types"]


def test_tools_return_envelope_ok_true():
    """經由 MCP 工具層包裝後（_envelope），回傳信封須含 ok=True。"""
    from ansys_unified_mcp.shared import as_envelope

    raw = controller.create_keyword_deck(endtim=1.0)
    enveloped = as_envelope(raw)
    assert enveloped["ok"] is True
    assert "deck_text" in enveloped
