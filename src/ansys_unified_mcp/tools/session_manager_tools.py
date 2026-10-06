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

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope, _VISIBILITY_STATE_KEY
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




# 方案 D：per-session 工具可見性合法 product 域。
# common 工具恆可見 (不列入可選集)，workflow 為跨產品高階工況域。
_VALID_VISIBILITY_PRODUCTS = frozenset(
    {"mechanical", "fluent", "geometry", "workbench", "optislang", "dpf", "workflow"}
)


@mcp.tool()
async def ans_session_set_workspace(products: list[str] | None = None) -> dict:
    """設定當前 session 的可見工具子集 (per-session 工具可見性，方案 D)。

    單一 all-profile server 下，呼叫端可宣告本 session 只關注的 product 域，
    後續 ``list_tools`` 僅回傳該些 product 的工具加上跨域通用工具 (文件/監看/
    session 管理恆可見)，藉此壓低單一 session 的工具可見集與 context 占用。
    不影響其他 session，也不改動全域工具註冊。

    Args:
        products: 欲保留可見的 product 清單，合法值為 "mechanical" / "fluent" /
            "geometry" / "workbench" / "optislang" / "dpf" / "workflow"。傳入
            None 或空清單則清除本 session 的可見性限制 (回到可見全集)。

    Returns:
        信封 dict：成功回 {"ok": True, "visible_products": [...]}；
        含非法 product 名稱時回 {"ok": False, "error": ...}。
    """
    from fastmcp.server.dependencies import get_context

    requested = [p.strip().lower() for p in (products or []) if p and p.strip()]
    invalid = [p for p in requested if p not in _VALID_VISIBILITY_PRODUCTS]
    if invalid:
        return _envelope(
            {
                "ok": False,
                "error": f"非法 product 名稱: {invalid}；合法值: {sorted(_VALID_VISIBILITY_PRODUCTS)}",
            }
        )
    try:
        ctx = get_context()
    except Exception:
        return _envelope({"ok": False, "error": "無法取得 session context (非 MCP request 期間呼叫)"})

    # 空清單 -> 清除限制 (set_state None 即解除過濾)；Context.set_state 為 async，
    # 且值必須 JSON-serializable，故存 list (非 set)
    await ctx.set_state(_VISIBILITY_STATE_KEY, requested if requested else None)
    return _envelope({"ok": True, "visible_products": sorted(requested)})
