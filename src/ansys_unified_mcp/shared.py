from __future__ import annotations
import os
from typing import Callable, Any, Sequence
from fastmcp import FastMCP

mcp = FastMCP("ansys-unified-mcp")

# Environment flag: When "1", FastMCP will register deprecated alias tools.
# By default ("0"), only canonical tools are registered for a clean, lean tool surface.
EXPOSE_ALIASES: bool = os.environ.get("ANSYS_MCP_EXPOSE_ALIASES", "0").strip() == "1"

# Internal alias lookup dictionaries:
# ALIAS_REGISTRY: maps legacy alias name -> canonical name
ALIAS_REGISTRY: dict[str, str] = {}

# CANONICAL_TO_ALIASES: maps canonical name -> list of alias names
CANONICAL_TO_ALIASES: dict[str, list[str]] = {}

# TOOL_REGISTRY: maps any name (canonical or alias) -> original callable function
TOOL_REGISTRY: dict[str, Callable[..., Any]] = {}

# Metadata records of all registered aliases for on-demand synchronization
_RECORDED_ALIASES: list[dict[str, Any]] = []


def should_expose_aliases() -> bool:
    """判斷當前執行環境是否應向 FastMCP 暴露 deprecated alias 工具。"""
    # 優先支援顯式剪枝開關 ANSYS_MCP_PRUNE_ALIASES=1
    if os.environ.get("ANSYS_MCP_PRUNE_ALIASES", "").strip() == "1":
        return False
    env_expose = os.environ.get("ANSYS_MCP_EXPOSE_ALIASES")
    if env_expose is not None:
        return env_expose.strip() == "1"
    return EXPOSE_ALIASES


def get_canonical_name(name: str) -> str:
    """將任意工具名稱（別名或規範名稱）解析為規範名稱。"""
    return ALIAS_REGISTRY.get(name, name)


def get_tool_function(name: str) -> Callable[..., Any] | None:
    """根據工具名稱獲取底層實作函數。"""
    canonical = get_canonical_name(name)
    return TOOL_REGISTRY.get(canonical) or TOOL_REGISTRY.get(name)


def get_aliases(canonical_name: str) -> list[str]:
    """獲取指定規範工具的所有已註冊別名清單。"""
    return list(CANONICAL_TO_ALIASES.get(canonical_name, []))


def aliased_tool(
    name_or_mcp: str | FastMCP | None = None,
    alias_or_name: str | Sequence[str] | None = None,
    description_or_aliases: str | Sequence[str] | None = None,
    description: str | None = None,
    alias: str | Sequence[str] | None = None,
    name: str | None = None,
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    雙軌工具註冊裝飾器：
    - 支援 aliased_tool(name=..., alias=..., description=...)
    - 支援 aliased_tool(mcp, canonical_name, aliases, description=...)
    - 支援 aliased_tool("canonical_name", "alias_name")
    
    核心規則：
    1. 永遠向 FastMCP 註冊 canonical_name。
    2. 僅在 should_expose_aliases() 為 True 時，向 FastMCP 註冊帶有 [DEPRECATED ALIAS for ...] 的別名工具。
    3. 維護內部別名查表 (ALIAS_REGISTRY)，確保任何內部或運行時調用能透明解析至 canonical 實作。
    """
    if isinstance(name_or_mcp, FastMCP):
        target_mcp = name_or_mcp
        canon_name = name or (alias_or_name if isinstance(alias_or_name, str) else None)
        raw_aliases = alias or description_or_aliases or kwargs.pop("aliases", None)
        desc = description or kwargs.pop("desc", None)
    else:
        target_mcp = kwargs.pop("mcp", None) or mcp
        canon_name = name or (name_or_mcp if isinstance(name_or_mcp, str) else None)
        raw_aliases = alias or alias_or_name or kwargs.pop("aliases", None)
        desc = description or (description_or_aliases if isinstance(description_or_aliases, str) else None)

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        canonical_name = canon_name or fn.__name__
        effective_desc = desc or fn.__doc__ or ""

        # 1. 永遠註冊規範主要名稱至 FastMCP
        target_mcp.tool(name=canonical_name, description=effective_desc, **kwargs)(fn)
        TOOL_REGISTRY[canonical_name] = fn

        # 2. 處理別名清單並維護內部字典
        aliases = [raw_aliases] if isinstance(raw_aliases, str) else (raw_aliases or [])
        for a in aliases:
            if a and a != canonical_name:
                ALIAS_REGISTRY[a] = canonical_name
                alias_list = CANONICAL_TO_ALIASES.setdefault(canonical_name, [])
                if a not in alias_list:
                    alias_list.append(a)
                TOOL_REGISTRY[a] = fn

                alias_desc = f"[DEPRECATED ALIAS for {canonical_name}] {effective_desc}".strip()
                record = {
                    "mcp": target_mcp,
                    "canonical": canonical_name,
                    "alias": a,
                    "desc": alias_desc,
                    "kwargs": kwargs,
                    "fn": fn,
                    "registered": False,
                }
                _RECORDED_ALIASES.append(record)

                # 僅在 EXPOSE_ALIASES 為 True 時註冊至 FastMCP
                if should_expose_aliases():
                    target_mcp.tool(name=a, description=alias_desc, **kwargs)(fn)
                    record["registered"] = True

        return fn

    return decorator


# 攔截 FastMCP 的 list_tools, call_tool, get_tool 以達到透明去別名與執行時相容
_orig_list_tools = mcp.list_tools
_orig_call_tool = mcp.call_tool
_orig_get_tool = mcp.get_tool


async def _wrapped_list_tools(*args: Any, **kwargs: Any) -> list[Any]:
    if should_expose_aliases():
        for rec in _RECORDED_ALIASES:
            if not rec["registered"]:
                rec["mcp"].tool(name=rec["alias"], description=rec["desc"], **rec["kwargs"])(rec["fn"])
                rec["registered"] = True
        return await _orig_list_tools(*args, **kwargs)
    else:
        tools = await _orig_list_tools(*args, **kwargs)
        return [
            t for t in tools
            if not (
                t.name in ALIAS_REGISTRY or
                (t.description and t.description.startswith("[DEPRECATED ALIAS for"))
            )
        ]


async def _wrapped_call_tool(name: str, arguments: dict[str, Any] | None = None, **kwargs: Any) -> Any:
    # 支援內部或運行時透過別名調用：若 FastMCP 當前未暴露該別名，自動解析為 canonical 原語
    tools = await _orig_list_tools()
    tool_names = {t.name for t in tools}
    target_name = name
    if target_name not in tool_names and target_name in ALIAS_REGISTRY:
        target_name = ALIAS_REGISTRY[target_name]
    return await _orig_call_tool(target_name, arguments, **kwargs)


async def _wrapped_get_tool(name: str, *args: Any, **kwargs: Any) -> Any:
    if should_expose_aliases():
        for rec in _RECORDED_ALIASES:
            if not rec["registered"]:
                rec["mcp"].tool(name=rec["alias"], description=rec["desc"], **rec["kwargs"])(rec["fn"])
                rec["registered"] = True
        return await _orig_get_tool(name, *args, **kwargs)
    t = await _orig_get_tool(name, *args, **kwargs)
    if t is None and name in ALIAS_REGISTRY:
        return await _orig_get_tool(ALIAS_REGISTRY[name], *args, **kwargs)
    return t


mcp.list_tools = _wrapped_list_tools
mcp.call_tool = _wrapped_call_tool
mcp.get_tool = _wrapped_get_tool
