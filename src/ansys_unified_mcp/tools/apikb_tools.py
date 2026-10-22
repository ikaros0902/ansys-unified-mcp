"""
ANSYS API 知識庫 MCP 工具層 (API Knowledge Base MCP Tools)
提供 Agent 快速檢索 API 符號、獲取成員定義、尋找物件導航鏈、以及腳本 API 靜態校驗功能。
"""
from __future__ import annotations
from typing import Optional

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.analytics.apikb import query as kb_query
from ansys_unified_mcp.analytics.apikb import validate as kb_validate

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def api_search(query: str, product: str = "", kind: str = "", top_k: int = 8) -> dict:
    """Search ANSYS API symbols (class, method, property, enum, keyword) across Mechanical, SpaceClaim, optiSLang, and LS-DYNA.

    Args:
        query: Search term or keyword (e.g. "AddFixedSupport", "fixed support", "Midsurface", "Optislang", "CONTROL_TERMINATION").
        product: Optional filter by product: "mechanical", "spaceclaim", "optislang", or "lsdyna".
        kind: Optional filter by kind: "class", "method", "property", "enum", "keyword".
        top_k: Maximum number of ranked results to return (default: 8).
    """
    results = kb_query.search(query=query, product=product or None, kind=kind or None, top_k=top_k)
    return _envelope({
        "query": query,
        "product": product or "all",
        "count": len(results),
        "results": results
    })

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def api_get(fqname: str, include: str = "members,edges", limit: int = 50) -> dict:
    """Get full definition of a specific API symbol, including its methods, properties, and connected type links.

    Args:
        fqname: Fully-qualified name or class name (e.g. "Ansys.ACT.Automation.Mechanical.Analysis", "Analysis", "Part").
        include: Comma-separated list of details to include: "members,edges", "members", or "edges".
        limit: Maximum number of members and edges to return (default: 50).
    """
    include_tuple = tuple(item.strip() for item in include.split(",") if item.strip())
    detail = kb_query.get(fqname=fqname, include=include_tuple, limit=limit)
    if not detail:
        return _envelope({
            "found": False,
            "error": f"Symbol '{fqname}' not found in API Knowledge Base."
        })
    return _envelope({
        "found": True,
        "symbol": detail
    })

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def api_path(from_type: str, to_type: str, product: str = "", max_depth: int = 4) -> dict:
    """Find object-navigation paths between two API types in the Knowledge Graph (e.g. from Analysis to EquivalentStress).

    Args:
        from_type: Source type or class name (e.g. "Analysis").
        to_type: Target type or class name (e.g. "EquivalentStress").
        product: Optional product filter.
        max_depth: Maximum navigation depth (default: 4).
    """
    paths = kb_query.path(from_type=from_type, to_type=to_type, product=product or None, max_depth=max_depth)
    return _envelope({
        "from": from_type,
        "to": to_type,
        "paths_count": len(paths),
        "paths": paths
    })

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def api_validate_script(code: str, product: str) -> dict:
    """Statically validate a Python, ACT, or SpaceClaim script against the official API dictionary to catch hallucinated methods/attributes.

    Args:
        code: Script code snippet to validate.
        product: Target product domain: "mechanical" or "spaceclaim".
    """
    report = kb_validate.validate_script(code=code, product=product)
    return _envelope(report)
