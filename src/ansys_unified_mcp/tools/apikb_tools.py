"""
ANSYS API 知識庫 MCP 工具層 (API Knowledge Base MCP Tools)
提供 Agent 快速檢索 API 符號、獲取成員定義、尋找物件導航鏈、以及腳本 API 靜態校驗功能。
"""

from __future__ import annotations
from typing import Optional

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.analytics.apikb import query as kb_query
from ansys_unified_mcp.analytics.apikb import validate as kb_validate
from ansys_unified_mcp.analytics.apikb import federated_query as fed_query


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def api_search(query: str, product: str = "", kind: str = "", top_k: int = 8) -> dict:
    """Search symbols from indexed ANSYS API, SDK, and REA snapshots.

    Args:
        query: API name or search term, such as "AddFixedSupport" or "DatumPlaneCreator".
        product: Optional APIKB source key, such as "mechanical", "spaceclaim", or "act_core_rea".
        kind: Optional symbol kind: "class", "method", "property", "enum", or "keyword".
        top_k: Maximum number of results to return. Default is 8.
    """
    results = kb_query.search(query=query, product=product or None, kind=kind or None, top_k=top_k)
    return _envelope(
        {"query": query, "product": product or "all", "count": len(results), "results": results}
    )


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def api_get(
    fqname: str,
    include: str = "members,edges",
    limit: int = 50,
    product: Optional[str] = None,
    release: Optional[str] = None,
    interface: Optional[str] = None,
) -> dict:
    """Get full definition of a specific API symbol, including its methods, properties, and connected type links.

    Args:
        fqname: Fully-qualified name or class name (e.g. "Ansys.ACT.Automation.Mechanical.Analysis", "Analysis", "Part").
        include: Comma-separated list of details to include: "members,edges", "members", or "edges".
        limit: Maximum number of members and edges to return (default: 50).
        product: Optional product key, such as "optislang_core".
        release: Optional product release recorded by the snapshot.
        interface: Optional source interface name for selecting a specific snapshot.
    """
    include_tuple = tuple(item.strip() for item in include.split(",") if item.strip())
    detail = kb_query.get(
        fqname=fqname,
        include=include_tuple,
        limit=limit,
        product=product,
        release=release,
        interface=interface,
    )
    if not detail:
        return _envelope(
            {"found": False, "error": f"Symbol '{fqname}' not found in API Knowledge Base."}
        )
    if detail.get("ambiguous"):
        return _envelope(
            {
                "found": False,
                "ambiguous": True,
                "candidates": detail["candidates"],
                "error": "Specify product, release, or interface to select one API source.",
            }
        )
    return _envelope({"found": True, "symbol": detail})


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def api_path(from_type: str, to_type: str, product: str = "", max_depth: int = 4) -> dict:
    """Find object-navigation paths between two API types in the Knowledge Graph (e.g. from Analysis to EquivalentStress).

    Args:
        from_type: Source type or class name (e.g. "Analysis").
        to_type: Target type or class name (e.g. "EquivalentStress").
        product: Optional product filter.
        max_depth: Maximum navigation depth (default: 4).
    """
    paths = kb_query.path(
        from_type=from_type, to_type=to_type, product=product or None, max_depth=max_depth
    )
    return _envelope({"from": from_type, "to": to_type, "paths_count": len(paths), "paths": paths})


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def api_validate_script(
    code: str, product: str, release: str = "", interface: str = ""
) -> dict:
    """Statically validate a Python, ACT, or PyAnsys script against the official API dictionary.

    Args:
        code: Script code snippet to validate.
        product: Target product domain key (e.g. "mechanical", "spaceclaim", "pyaedt", "fluent_core", "mapdl", "dpf", "rocky", "motorcad", "speos", "reaction_chemkin").
        release: Optional exact product release filter (e.g. "v251", "v261").
        interface: Optional specific source interface filter.
    """
    report = kb_validate.validate_script(
        code=code, product=product, release=release or None, interface=interface or None
    )
    return _envelope(report)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def ans_search_official_examples(
    query: str = "", product: str = "", top_k: int = 5
) -> dict:
    """Search official PyAnsys and ANSYS verified code examples.

    Args:
        query: Keyword query for example title, purpose, or API method.
        product: Optional product filter (e.g. "mechanical", "mapdl", "fluent", "pyaedt", "geometry").
        top_k: Maximum number of ranked examples to return (default: 5).
    """
    import json
    from pathlib import Path
    from ansys_unified_mcp.analytics.docsearch.config import REPO_ROOT

    catalog_path = (
        REPO_ROOT
        / "src"
        / "ansys_unified_mcp"
        / "resources"
        / "manifests"
        / "official_examples_catalog.json"
    )
    if not catalog_path.is_file():
        return _envelope(
            {
                "ok": False,
                "error": "Official examples catalog not found. Run scrape_pyansys_examples.py first.",
            }
        )

    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog: dict[str, list[dict]] = json.load(f)
    except Exception as exc:
        return _envelope({"ok": False, "error": f"Failed to load examples catalog: {exc}"})

    results = []
    prod_lower = product.strip().lower()
    query_lower = query.strip().lower()

    for p_key, examples in catalog.items():
        if prod_lower and prod_lower not in p_key.lower():
            continue
        for ex in examples:
            score = 0
            if query_lower:
                text_blob = (
                    f"{ex.get('title', '')} {' '.join(ex.get('steps', []))} "
                    f"{ex.get('verification', '')} {ex.get('id', '')}"
                ).lower()
                if query_lower in text_blob:
                    score += 10
                else:
                    words = query_lower.split()
                    matched_words = sum(1 for w in words if w in text_blob)
                    score += matched_words * 2
                if score == 0:
                    continue
            else:
                score = 1

            results.append({"product": p_key, "score": score, "example": ex})

    results.sort(key=lambda x: x["score"], reverse=True)
    top_results = results[: max(1, min(top_k, 20))]

    return _envelope(
        {
            "ok": True,
            "query": query,
            "product": product or "all",
            "count": len(top_results),
            "results": top_results,
        }
    )


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def api_federated_path(
    from_uid: int,
    to_uid: int,
    path_semantics: str = "",
    max_hops: int = 8,
    limit: int = 10,
) -> dict:
    """Find object-navigation paths across 10 physics subgraphs using 2-Stage 8-Hop Meet-in-the-Middle Join.

    Args:
        from_uid: 64-bit deterministic symbol_uid of the source API entity.
        to_uid: 64-bit deterministic symbol_uid of the target API entity.
        path_semantics: Optional filter for path semantics: "FACTORY_CREATE", "READ_TRAVERSAL", or "CROSS_BRIDGE".
        max_hops: Maximum traversal depth between 1 and 8 hops (default: 8).
        limit: Maximum number of paths to return (default: 10).
    """
    paths = fed_query.query_api_path(
        from_uid=from_uid,
        to_uid=to_uid,
        path_semantics=path_semantics or None,
        max_hops=max_hops,
        limit=limit,
    )
    return _envelope(
        {
            "from_uid": from_uid,
            "to_uid": to_uid,
            "max_hops": max_hops,
            "paths_count": len(paths),
            "paths": paths,
        }
    )


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def api_federated_search(
    query: str,
    domain: str = "",
    kind: str = "",
    level: str = "L0",
    top_k: int = 10,
) -> dict:
    """Federated symbol search across 10 physics domains returning progressive L0/L1 cards.

    Args:
        query: Symbol name, FQN prefix, or method keyword.
        domain: Optional domain filter: "foundation", "structural", "fluids", "electromagnetics", "optics", "thermal", "multibody", "particles", "materials", "framework".
        kind: Optional symbol kind filter: "CLASS", "PROPERTY", "METHOD", "ENUM".
        level: Progressive card level: "L0" (~50 tokens summary), "L1" (~250 tokens signature), or "ALL".
        top_k: Maximum number of symbols to return (default: 10).
    """
    hits = fed_query.search_symbols_federated(
        query=query,
        domain=domain or None,
        kind=kind or None,
        level=level,
        top_k=top_k,
    )
    return _envelope(
        {
            "query": query,
            "domain": domain or "all",
            "level": level,
            "count": len(hits),
            "results": hits,
        }
    )


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def api_cross_bridge(
    coupling_type: str = "",
    source_domain: str = "",
    target_domain: str = "",
    variable_name: str = "",
) -> dict:
    """Query multiphysics interface variable pairings from multiphysics_bridge.sqlite.

    Args:
        coupling_type: Optional multiphysics coupling type: "FSI", "CHT", "MBD-DEM", "STOP".
        source_domain: Source physics domain name or ID.
        target_domain: Target physics domain name or ID.
        variable_name: Interface variable name filter (e.g. "Force", "HeatFlux", "Displacement").
    """
    bridges = fed_query.query_cross_domain_bridge(
        coupling_type=coupling_type or None,
        source_domain=source_domain or None,
        target_domain=target_domain or None,
        variable_name=variable_name or None,
    )
    return _envelope(
        {
            "coupling_type": coupling_type or "all",
            "count": len(bridges),
            "bridges": bridges,
        }
    )
