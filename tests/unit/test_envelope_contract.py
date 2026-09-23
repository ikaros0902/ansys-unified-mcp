# -*- coding: utf-8 -*-
"""
工具層回傳信封契約測試。

背景：工具層原本混用兩種回傳型別——128 處 ``-> str``（JSON 字串）與
30 處 ``-> dict``，連同一個檔案內部都不一致。代價是 ``tools/mechanical.py``
必須自行養四個正規化 helper，且呼叫端無法以 ``result["ok"]`` 統一判斷成敗，
使「工具回傳 ok 為真且數值落在物理容許範圍」這類客觀驗收條件無法撰寫。

本測試以 AST 靜態掃描全部工具模組（不依賴 TOOL_REGISTRY，因為裸
``@mcp.tool`` 註冊的工具不會進入該字典），確保任一工具漏改時即失敗。

信封慣例見 ARCHITECTURE.md 第 3 節：
- 成功：``{"ok": True, ...其他欄位}``
- 失敗：``{"ok": False, "error": "可讀的錯誤訊息"}``
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ansys_unified_mcp.shared import as_envelope, error_envelope, looks_like_error

TOOLS_DIR = Path(__file__).resolve().parents[2] / "src" / "ansys_unified_mcp" / "tools"

# 工具註冊裝飾器辨識：不採白名單，改以名稱是否含 "tool" 判斷。
# 理由：除裸 @mcp.tool 與 @aliased_tool 之外，sim_tools.py 另有自製裝飾器
# 工廠 @tool_fluent / @tool_geometry；白名單會讓這 38 個工具逃過守門。
_TOOL_DECORATOR_HINT = "tool"


def _decorator_names(node: ast.FunctionDef) -> set[str]:
    """擷取函式所有裝飾器的最末層屬性名稱（含 @x.tool() 形式）"""
    names: set[str] = set()
    for dec in node.decorator_list:
        target = dec.func if isinstance(dec, ast.Call) else dec
        if isinstance(target, ast.Attribute):
            names.add(target.attr)
        elif isinstance(target, ast.Name):
            names.add(target.id)
    return names


def _is_tool_function(node: ast.FunctionDef) -> bool:
    """判斷函式是否為 MCP 工具（任一裝飾器名稱含 tool 即視為工具註冊）"""
    return any(_TOOL_DECORATOR_HINT in name for name in _decorator_names(node))


def _iter_tool_functions():
    """走訪所有工具模組，產出 (檔名, 函式名, 行號, 回傳標註節點)"""
    for py_file in sorted(TOOLS_DIR.glob("*.py")):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not _is_tool_function(node):
                continue
            yield py_file.name, node.name, node.lineno, node.returns


def test_tool_modules_are_discoverable():
    """先確認掃描器確實抓到工具，避免測試因路徑錯誤而空過"""
    found = list(_iter_tool_functions())
    assert len(found) >= 50, f"工具掃描結果異常偏少（{len(found)} 個），請檢查 TOOLS_DIR 或裝飾器辨識邏輯"


def test_all_mcp_tools_return_dict():
    """所有 MCP 工具的回傳標註必須為 dict，不得為 str（否則客觀驗收斷言無法成立）"""
    offenders: list[str] = []
    for file_name, func_name, lineno, returns in _iter_tool_functions():
        if returns is None:
            offenders.append(f"{file_name}:{lineno} {func_name}() 缺少回傳型別標註")
            continue
        annotation = ast.unparse(returns).replace(" ", "")
        if annotation not in {"dict", "dict[str,Any]", "dict[str,any]", "Dict[str,Any]"}:
            offenders.append(f"{file_name}:{lineno} {func_name}() -> {annotation}")

    assert not offenders, (
        "以下 MCP 工具未回傳 dict 信封，違反 ARCHITECTURE.md 第 3 節慣例:\n"
        + "\n".join(offenders)
    )


@pytest.mark.parametrize(
    "raw, expected_ok",
    [
        (None, True),
        ({}, True),
        ({"ok": True, "value": 1}, True),
        ({"ok": False, "error": "boom"}, False),
        ({"error": "boom"}, False),
        ({"value": 1}, True),
        ('{"ok": true, "value": 1}', True),
        ('{"ok": false, "error": "boom"}', False),
        ("plain text output", True),
        (42, True),
    ],
)
def test_as_envelope_always_yields_bool_ok(raw, expected_ok):
    """as_envelope 對任何輸入都必須產出含 bool 型別 ok 欄位的 dict"""
    env = as_envelope(raw)
    assert isinstance(env, dict)
    assert isinstance(env["ok"], bool)
    assert env["ok"] is expected_ok


def test_as_envelope_preserves_payload():
    """正規化不得丟失既有欄位"""
    env = as_envelope({"ok": True, "max_stress_mpa": 123.4, "nodes": 5000})
    assert env["max_stress_mpa"] == 123.4
    assert env["nodes"] == 5000


def test_as_envelope_parses_json_string_payload():
    """既有回傳 JSON 字串的工具，正規化後欄位須可直接存取"""
    env = as_envelope('{"ok": true, "frequencies_hz": [12.5, 48.1]}')
    assert env["ok"] is True
    assert env["frequencies_hz"] == [12.5, 48.1]


def test_as_envelope_wraps_non_json_string_as_output():
    """非 JSON 字串（如求解器原始輸出）須包裝於 output 欄位而非丟棄"""
    env = as_envelope("Solution completed. 3 iterations.")
    assert env["ok"] is True
    assert env["output"] == "Solution completed. 3 iterations."


@pytest.mark.parametrize(
    "text",
    [
        "❌ 連線失敗",
        "設定錯誤：找不到區域",
        "Mesh generation failed",
        "Error: zone not found",
        "Exception: NullReference",
        "Traceback (most recent call last):",
        "502 Bad Gateway",
    ],
)
def test_as_envelope_marks_error_strings_as_failure(text):
    """
    純文字失敗輸出不得被回報為成功。

    回歸防護：信封統一前，sim_tools 的本地 _envelope 具備 ❌ / 錯誤 / fail /
    error 啟發式；若共用實作漏掉此判定，Fluent 與 Geometry 工具失敗時會回
    ok=True，使錯誤在自動化流程中被無聲放行。
    """
    env = as_envelope(text)
    assert env["ok"] is False, f"失敗輸出被誤判為成功: {text}"
    assert env["output"] == text


def test_as_envelope_does_not_flag_plain_success_output():
    """一般成功輸出不得被誤判為失敗"""
    env = as_envelope("Mesh generated: 120000 nodes, 65000 elements.")
    assert env["ok"] is True


def test_looks_like_error_ignores_non_string():
    """非字串輸入不得觸發錯誤判定"""
    assert looks_like_error("") is False
    assert looks_like_error(None) is False


def test_error_envelope_shape():
    """error_envelope 須產出 ok=False 並保留額外診斷欄位"""
    env = error_envelope("連線失敗", port=10000)
    assert env["ok"] is False
    assert env["error"] == "連線失敗"
    assert env["port"] == 10000
