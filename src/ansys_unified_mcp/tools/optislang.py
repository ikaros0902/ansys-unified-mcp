#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""optiSLang MCP Tools - 讓 AI 代理透過 PyOptiSLang 驅動 optiSLang 專案。

設計沿用 mechanical_tools 的「thin generic script runner」模式：
以 optiSLang 原生 Python API（run_python_script）為主要原語，
避免綁死高階 API（各版本間 API 有變動）。這樣 25R1/25R2/26R1 都能通用。
"""

from __future__ import annotations
import json
import os

from ansys_unified_mcp.shared import mcp

# ponytail: 全域單一 Optislang session。上限=單一連線；要多專案並行時再改為 dict 管理。
_osl = None


def _json(data) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def _check_connection():
    """未連線時回統一錯誤，供各 tool 開頭呼叫。"""
    if _osl is None:
        return _json({"ok": False, "error": "尚未連線 optiSLang，請先呼叫 connect_optislang。"})
    return None


@mcp.tool()
def connect_optislang(project_path: str = "", ini_timeout: float = 60.0) -> str:
    """啟動並連線 optiSLang。

    Args:
        project_path: 既有 .opf 專案路徑；留空則開新專案。
        ini_timeout: 啟動連線逾時秒數（optiSLang 冷啟動較慢，預設 60）。

    Returns:
        JSON：連線結果與 optiSLang 版本字串。
    """
    global _osl
    try:
        from ansys.optislang.core import Optislang
    except ImportError as e:
        return _json({"ok": False, "error": f"未安裝 ansys-optislang-core：{e}"})

    try:
        if _osl is not None:
            return _json({"ok": True, "note": "已有連線，若要重連請先 disconnect_optislang。"})

        kwargs = {"ini_timeout": ini_timeout}
        if project_path:
            if not os.path.isfile(project_path):
                return _json({"ok": False, "error": f"專案檔不存在：{project_path}"})
            kwargs["project_path"] = project_path

        _osl = Optislang(**kwargs)
        return _json({"ok": True, "version": _osl_version_string(), "project": project_path or "(new)"})
    except Exception as e:
        _osl = None
        return _json({"ok": False, "error": f"連線失敗：{e}"})


def _osl_version_string() -> str:
    """跨版本取版本字串：優先屬性、退回方法（API 在不同版本有變動）。"""
    for attr in ("osl_version_string", "get_osl_version_string"):
        obj = getattr(_osl, attr, None)
        if obj is None:
            continue
        try:
            return obj() if callable(obj) else str(obj)
        except Exception:
            continue
    return "unknown"


@mcp.tool()
def optislang_version() -> str:
    """回報目前連線 optiSLang 的已驗證版本字串（P1 冒煙用）。"""
    err = _check_connection()
    if err:
        return err
    return _json({"ok": True, "version": _osl_version_string()})


@mcp.tool()
def run_optislang_script(script: str) -> str:
    """在連線的 optiSLang server 執行一段 optiSLang 原生 Python 腳本。

    這是最泛用原語：建立 solver chain 節點、設定參數/響應、觸發 DoE 與
    sensitivity/MOP，皆可用 optiSLang server command 腳本達成。

    Args:
        script: optiSLang 原生 Python 腳本字串。

    Returns:
        JSON：執行輸出（原樣字串化）。
    """
    err = _check_connection()
    if err:
        return err
    if not script or not script.strip():
        return _json({"ok": False, "error": "script 不得為空。"})
    try:
        result = _osl.run_python_script(script)
        # run_python_script 各版本可能回 str 或 (success, output) tuple，統一字串化。
        return _json({"ok": True, "output": str(result)})
    except Exception as e:
        return _json({"ok": False, "error": f"腳本執行失敗：{e}"})


@mcp.tool()
def start_optislang_project() -> str:
    """執行（求解）目前 optiSLang 專案，阻塞至完成。"""
    err = _check_connection()
    if err:
        return err
    try:
        _osl.start()  # ponytail: 同步 start；長流程若需非阻塞監控，改用 project.start(wait_for_finished=False)。
        return _json({"ok": True, "note": "專案執行完成。"})
    except Exception as e:
        return _json({"ok": False, "error": f"執行失敗：{e}"})


@mcp.tool()
def disconnect_optislang(shutdown: bool = True) -> str:
    """關閉 optiSLang 連線並釋放資源。

    Args:
        shutdown: True 則一併關閉 optiSLang 進程（dispose）。
    """
    global _osl
    if _osl is None:
        return _json({"ok": True, "note": "本來就未連線。"})
    try:
        if shutdown:
            _osl.dispose()
        _osl = None
        return _json({"ok": True})
    except Exception as e:
        _osl = None
        return _json({"ok": False, "error": f"關閉時發生例外（已強制清除連線）：{e}"})
