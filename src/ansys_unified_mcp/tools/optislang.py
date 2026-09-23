#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""optiSLang MCP Tools - 讓 AI 代理透過 PyOptiSLang 驅動 optiSLang 專案。

設計沿用「thin generic script runner」模式：以 optiSLang 原生 Python API
(run_python_script) 為主要原語，避免綁死高階 API（各版本間 API 有變動），
25R1/25R2/26R1 皆可通用。

session 生命週期委派給 products/optislang.py 的 controller，統一走
SessionRegistry（與 Mechanical 一致），不再使用模組全域 session。
"""

from __future__ import annotations

from ansys_unified_mcp.shared import mcp, aliased_tool, as_envelope as _envelope
from ansys_unified_mcp.products.optislang import controller


@aliased_tool(name="optislang_connect", alias="connect_optislang")
def connect_optislang(project_path: str = "", ini_timeout: float = 60.0) -> dict:
    """啟動並連線 optiSLang。

    Args:
        project_path: 既有 .opf 專案路徑；留空則開新專案。
        ini_timeout: 啟動連線逾時秒數（optiSLang 冷啟動較慢，預設 60）。

    Returns:
        JSON：連線結果與 optiSLang 版本字串。
    """
    return _envelope(controller.connect(project_path=project_path, ini_timeout=ini_timeout))


@aliased_tool(name="optislang_get_version", alias="optislang_version")
def optislang_version() -> dict:
    """回報目前連線 optiSLang 的已驗證版本字串（P1 冒煙用）。"""
    if not controller.is_connected():
        return _envelope({"ok": False, "error": "尚未連線 optiSLang，請先呼叫 connect_optislang。"})
    return _envelope({"ok": True, "version": controller.version_string()})


@aliased_tool(name="optislang_run_script", alias="run_optislang_script")
def run_optislang_script(script: str) -> dict:
    """在連線的 optiSLang server 執行一段 optiSLang 原生 Python 腳本。

    這是最泛用原語：建立 solver chain 節點、設定參數/響應、觸發 DoE 與
    sensitivity/MOP，皆可用 optiSLang server command 腳本達成。

    Args:
        script: optiSLang 原生 Python 腳本字串。

    Returns:
        JSON：執行輸出（原樣字串化）。
    """
    return _envelope(controller.run_script(script))


@aliased_tool(name="optislang_start_project", alias="start_optislang_project")
def start_optislang_project() -> dict:
    """執行（求解）目前 optiSLang 專案，阻塞至完成。"""
    return _envelope(controller.start_project())


@aliased_tool(name="optislang_disconnect", alias="disconnect_optislang")
def disconnect_optislang(shutdown: bool = True) -> dict:
    """關閉 optiSLang 連線並釋放資源。

    Args:
        shutdown: True 則一併關閉 optiSLang 進程（dispose）。
    """
    return _envelope(controller.disconnect(shutdown=shutdown))

