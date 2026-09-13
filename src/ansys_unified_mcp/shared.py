from __future__ import annotations
from typing import Callable, Any, Sequence
from fastmcp import FastMCP

mcp = FastMCP("ansys-unified-mcp")


def aliased_tool(
    name: str | None = None,
    alias: str | Sequence[str] | None = None,
    description: str | None = None,
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    雙軌工具註冊裝飾器：
    - name: 規範化的新工具名稱（如 mechanical_add_force）
    - alias: 相容性的舊名稱或別名列表（如 add_force）
    - 保證新舊名稱同時在 MCP 註冊並指向同一個實作，完全向後相容
    """
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        canonical_name = name or fn.__name__
        desc = description or fn.__doc__ or ""

        # 1. 註冊主要規範名稱
        mcp.tool(name=canonical_name, description=desc, **kwargs)(fn)

        # 2. 註冊相容舊別名（帶有廢棄提示）
        aliases = [alias] if isinstance(alias, str) else (alias or [])
        for a in aliases:
            if a and a != canonical_name:
                alias_desc = f"[DEPRECATED ALIAS for {canonical_name}] {desc}".strip()
                mcp.tool(name=a, description=alias_desc, **kwargs)(fn)
        return fn

    return decorator
