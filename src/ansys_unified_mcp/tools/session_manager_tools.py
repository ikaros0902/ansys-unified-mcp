# -*- coding: utf-8 -*-
"""統一跨產品 Session 管理 MCP 工具層。

將 ``connection/session_manager.py`` 的 ``AnsSessionManager``（統一連線門面）
接線為實際可呼叫的 MCP 工具。本模組僅做薄包裝：將呼叫轉送至
``session_manager`` 對應方法，再以 ``as_envelope`` 正規化回傳信封，不重新
實作任何連線邏輯。

**為何用 ``options: dict`` 而非具名參數或 ``**kwargs``**：
FastMCP 的工具簽名會被轉換為 JSON Schema 供客戶端呼叫，不支援 ``**kwargs``
（裝飾階段即拋 ``ValueError``）。四個產品的 controller 參數集合彼此互斥、
聯集起來多達十餘個（port/pid/batch/host/transport_mode/connect_timeout/
processors/cwd/ip/password/project_path/ini_timeout/key/shutdown），若展開
成具名可選參數會讓單一工具簽名充斥大量「其他產品才用得到」的無關欄位，
反而降低可讀性。改用單一 ``options`` 字典由呼叫端依 ``product`` 自行填入
對應產品的原生參數名稱，再於本層展開為關鍵字引數透傳給
``session_manager``，貼合其既有 ``**kwargs`` 委派設計。

支援產品：mechanical, geometry, fluent, optislang。
"""

from __future__ import annotations

from typing import Any

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.connection.session_manager import session_manager


@mcp.tool()
def ans_session_connect(product: str, options: dict[str, Any] | None = None) -> dict:
    """連線至既有的 ANSYS 實例（跨產品統一入口）。

    依 ``product`` 委派至對應 controller，各產品實際接受的參數不同，
    經 ``options`` 字典透傳：
    - mechanical: {"port": int, "pid": int}
    - geometry / fluent: 委派至該產品的 launch()（無獨立 connect），
      如 {"port": int, "host": str, "connect_timeout": int}
    - optislang: {"project_path": str, "ini_timeout": float}

    Args:
        product: 目標產品名稱，支援 "mechanical" / "geometry" / "fluent" / "optislang"。
        options: 透傳至對應產品 controller 的原生參數字典，可省略。
    """
    result = session_manager.connect(product, **(options or {}))
    return _envelope(result)


@mcp.tool()
def ans_session_launch(product: str, options: dict[str, Any] | None = None) -> dict:
    """啟動新的 ANSYS 實例（跨產品統一入口）。

    依 ``product`` 委派至對應 controller 的 launch（或對無獨立 launch 概念
    的產品委派至其對應入口，如 optiSLang 委派至 connect）。

    Args:
        product: 目標產品名稱，支援 "mechanical" / "geometry" / "fluent" / "optislang"。
        options: 透傳至對應產品 controller 的原生參數字典，可省略。
    """
    result = session_manager.launch(product, **(options or {}))
    return _envelope(result)


@mcp.tool()
def ans_session_status(product: str, options: dict[str, Any] | None = None) -> dict:
    """查詢指定產品目前的連線狀態（跨產品統一入口）。

    Args:
        product: 目標產品名稱，支援 "mechanical" / "geometry" / "fluent" / "optislang"。
        options: 透傳至對應產品 controller 的 status() 原生參數字典，可省略。
    """
    result = session_manager.status(product, **(options or {}))
    return _envelope(result)


@mcp.tool()
def ans_session_disconnect(product: str, options: dict[str, Any] | None = None) -> dict:
    """中斷指定產品的連線（跨產品統一入口）。

    依 ``product`` 委派至對應 controller 的 disconnect/close/exit（各產品
    方法名稱不同，由 session_manager 內部處理對應關係）。

    Args:
        product: 目標產品名稱，支援 "mechanical" / "geometry" / "fluent" / "optislang"。
        options: 透傳至對應產品 controller 的原生參數字典，可省略。
    """
    result = session_manager.disconnect(product, **(options or {}))
    return _envelope(result)

