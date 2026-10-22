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

import importlib.metadata
import importlib
import os
from pathlib import Path
from typing import Any

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope, _VISIBILITY_STATE_KEY
from ansys_unified_mcp.connection.session_manager import session_manager


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def ans_session_diagnose(product: str) -> dict:
    """唯讀檢查產品安裝、SDK 與已登錄 session；不啟動產品或修改模型。

    transport、script、model 與 license 目前僅回報為未知，因為僅憑 session
    登錄或安裝資訊不能證明通訊、模型狀態、腳本執行或授權有效。
    """
    normalized = product.strip().lower()
    products = {
        "mechanical": ("ANSYS_MECHANICAL", Path("aisol") / "bin" / "winx64" / "AnsysWBU.exe", "ansys-mechanical-core", "ansys.mechanical.core"),
        "geometry": ("ANSYS_SPACECLAIM_EXE", Path("scdm") / "SpaceClaim.exe", "ansys-geometry-core", "ansys.geometry.core"),
        "fluent": ("ANSYS_FLUENT", Path("fluent") / "ntbin" / "win64" / "fluent.exe", "ansys-fluent-core", "ansys.fluent.core"),
        "optislang": ("ANSYS_OPTISLANG_EXE", Path("optiSLang") / "optislang.exe", "ansys-optislang-core", "ansys.optislang.core"),
    }
    spec = products.get(normalized)
    if spec is None:
        return _envelope({"ok": False, "error": f"不支援的產品: {normalized}"})

    exe_env, exe_suffix, sdk_name, sdk_module = spec
    configured_exe = os.environ.get(exe_env)
    root_value = os.environ.get("ANSYS_ROOT")
    version = os.environ.get("ANSYS_VERSION", "").strip()
    root = Path(root_value) if root_value else None
    if root and version and root.name.lower() != f"v{version}".lower():
        root = root / f"v{version}"
    executable = Path(configured_exe) if configured_exe else (root / exe_suffix if root else None)
    install_check = {
        "status": "available" if executable and executable.is_file() else "missing_or_unconfigured",
        "path": str(executable) if executable else None,
        "selected_release": version or None,
    }

    import_error = None
    try:
        sdk_version = importlib.metadata.version(sdk_name)
        distribution_status = "installed"
        try:
            importlib.import_module(sdk_module)
            import_status = "imported"
        except Exception as exc:
            import_status = "failed"
            import_error = f"{type(exc).__name__}: {exc}"
    except importlib.metadata.PackageNotFoundError:
        distribution_status = "missing"
        sdk_version = None
        import_status = "not_attempted"
        import_error = None
    sdk_check = {
        "package": sdk_name,
        "module": sdk_module,
        "distribution_status": distribution_status,
        "import_status": import_status,
        "version": sdk_version,
        "compatibility": "unknown",
    }
    if import_error:
        sdk_check["import_error"] = import_error

    try:
        registered = session_manager.status(normalized)
    except Exception as exc:
        registered = {"error": f"{type(exc).__name__}: {exc}"}

    return _envelope(
        {
            "ok": True,
            "product": normalized,
            "checks": {
                "installation": install_check,
                "sdk": sdk_check,
                "registered_session": registered,
                "transport": {"status": "unknown", "reason": "未執行連線探測"},
                "script": {"status": "unknown", "reason": "診斷不執行宿主腳本"},
                "model": {"status": "unknown", "reason": "未讀取活動文件或分析狀態"},
                "license": {"status": "unknown", "reason": "未啟動求解器或查詢授權"},
            },
        }
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True})
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


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True})
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


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True})
def ans_session_status(product: str, options: dict[str, Any] | None = None) -> dict:
    """查詢指定產品目前的連線狀態（跨產品統一入口）。

    Args:
        product: 目標產品名稱，支援 "mechanical" / "geometry" / "fluent" / "optislang"。
        options: 透傳至對應產品 controller 的 status() 原生參數字典，可省略。
    """
    result = session_manager.status(product, **(options or {}))
    return _envelope(result)


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True})
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


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
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
    target_val = requested if requested else None
    await ctx.set_state(_VISIBILITY_STATE_KEY, target_val)

    # 雙軌持久化：針對 in-memory Client / STDIO 等無持久 session_id 之 transport，同步寫入連線層 lifespan_context
    req_ctx = getattr(ctx, "request_context", None)
    if req_ctx is not None:
        lifespan_ctx = getattr(req_ctx, "lifespan_context", None)
        if isinstance(lifespan_ctx, dict):
            lifespan_ctx[_VISIBILITY_STATE_KEY] = target_val

    return _envelope({"ok": True, "visible_products": sorted(requested)})
