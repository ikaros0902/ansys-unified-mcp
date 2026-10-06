# -*- coding: utf-8 -*-
"""Per-session 工具可見性 (方案 D)。

在單一 all-profile FastMCP server 下，讓不同 session 依其宣告的 product 偏好
看到不同的工具子集，藉此壓低單一 session 的工具可見集 (context 占用)，同時
不需要多進程、不需要為每個 workspace mount 子 server。

掛接方式：FastMCP ``Middleware.on_list_tools`` (協議層正確掛點，涵蓋 MCP
client 的 list_tools 請求路徑)。篩選只對回傳清單取子集，不改動全域工具註冊，
也完全不碰 ``shared.ALIAS_REGISTRY`` 的別名解析鏈 (別名解析在 shared 層的
list/call/get 包裝，與本層正交)。

分類依據：工具的來源模組 (``FunctionTool.fn.__module__``)，比工具名稱前綴
精確。因 ``on_list_tools`` 階段僅拿得到協議層 Tool (無 ``fn``)，故於啟動時
以 FunctionTool 建立一次性 ``name -> product`` 權威映射，middleware 依名稱查表。
"""

from __future__ import annotations

from typing import Any, Optional, Sequence, Set

from fastmcp.server.middleware import Middleware

# 跨域通用工具所屬的來源模組 (一律可見，不受 workspace 篩選)。
_COMMON_MODULES = frozenset(
    {
        "ansys_unified_mcp.tools.docs_tools",
        "ansys_unified_mcp.tools.sentinel_tools",
        "ansys_unified_mcp.tools.session_manager_tools",
    }
)

# 高階工況 workflow 工具 (跨產品編排)，歸類為獨立的 "workflow" 域。
_WORKFLOW_MODULE = "ansys_unified_mcp.tools.intent_tools"

# 通用工具恆可見的域名稱。
COMMON_PRODUCT = "common"


def product_of_module(module: str) -> str:
    """由來源模組字串判定所屬 product 域。

    回傳如 ``"mechanical"`` / ``"fluent"`` / ``"geometry"`` / ``"workbench"``
    / ``"optislang"`` / ``"dpf"`` / ``"workflow"`` / ``"common"``。無法判定時
    一律歸為 ``common`` (從寬可見，避免誤隱藏)。
    """
    module = module or ""
    if module in _COMMON_MODULES:
        return COMMON_PRODUCT
    if module == _WORKFLOW_MODULE:
        return "workflow"
    prefix = "ansys_unified_mcp.products."
    if module.startswith(prefix):
        name = module[len(prefix):].split(".", 1)[0]
        if name:
            return name
    return COMMON_PRODUCT


class WorkspaceVisibilityMiddleware(Middleware):
    """依 session 宣告的 product 偏好過濾 ``list_tools`` 回傳清單。

    - session 未宣告偏好 (state 未設或為空)：回全集 (向後相容)。
    - 已宣告：保留 ``common`` 工具與落在偏好集合內的工具。

    name->product 映射採延遲建立 (lazy)：首次 ``on_list_tools`` 時所有工具均已
    註冊完成，據當下 FunctionTool 快照建表並快取。
    """

    def __init__(self, mcp: Any, state_key: str) -> None:
        super().__init__()
        self._mcp = mcp
        self._state_key = state_key
        self._name_to_product: Optional[dict[str, str]] = None

    def _ensure_map(self) -> dict[str, str]:
        """以 shared.TOOL_REGISTRY (name -> fn) 同步建立 name->product 映射。

        不在 ``on_list_tools`` 內 await FastMCP 的 async 取工具 API，避免 middleware
        chain 重入導致的 coroutine 處理錯誤。首次呼叫時建表並快取。
        """
        if self._name_to_product is None:
            try:
                from ansys_unified_mcp.shared import TOOL_REGISTRY
                mapping: dict[str, str] = {}
                for name, fn in TOOL_REGISTRY.items():
                    module = getattr(fn, "__module__", "") or ""
                    mapping[name] = product_of_module(module)
                self._name_to_product = mapping
            except Exception:
                self._name_to_product = {}
        return self._name_to_product

    async def _visible_products(self, context: Any) -> Optional[Set[str]]:
        fctx = getattr(context, "fastmcp_context", None)
        if fctx is None:
            return None
        try:
            # Context.get_state 為 async，須 await；非 request 期間或未設定回 None
            products = await fctx.get_state(self._state_key)
        except Exception:
            return None
        if not products:
            return None
        return set(products)

    async def on_list_tools(self, context: Any, call_next: Any) -> Sequence[Any]:
        tools = await call_next(context)
        visible = await self._visible_products(context)
        if not visible:
            return tools
        name_to_product = self._ensure_map()
        allowed = set(visible)
        allowed.add(COMMON_PRODUCT)  # 通用工具恆可見
        # 未知名稱 (映射缺漏) 從寬保留，避免誤隱藏
        return [
            t for t in tools
            if name_to_product.get(getattr(t, "name", None), COMMON_PRODUCT) in allowed
        ]
