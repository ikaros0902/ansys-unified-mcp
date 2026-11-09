"""MCP tools for searching ANSYS API and scripting documentation.

Backed by a local SQLite FTS5 (trigram) index over cleaned API documents and
curated knowledge dictionaries. Enables rapid symbol lookups, topic inspections,
and document chunk retrievals.
"""

from __future__ import annotations

import csv
from pathlib import Path
import re
from typing import Optional

from ansys_unified_mcp.shared import mcp, as_envelope as _envelope
from ansys_unified_mcp.analytics.docsearch import index as docs_index
from ansys_unified_mcp.analytics.docsearch.config import REPO_ROOT


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def list_ansys_docs(
    product: str = "",
    category: str = "",
    query: str = "",
    limit: int = 50,
    offset: int = 0,
    summary_only: bool = True,
) -> dict:
    """List indexed ANSYS documentation with product summary or paginated document entries.

    Args:
        product: Optional product identifier, such as "fluent" or "mechanical".
        category: Optional category filter, such as "api_reference" or "tutorial".
        query: Optional substring match for document name or title.
        limit: Maximum number of document items to return (default: 50, max: 200).
        offset: Pagination offset index (default: 0).
        summary_only: When True and no filters are provided, returns product aggregate counts.
    """
    safe_limit = max(1, min(limit, 200))
    return _envelope(
        docs_index.list_docs(
            product=product or "",
            category=category or "",
            query=query or "",
            limit=safe_limit,
            offset=offset,
            summary_only=summary_only,
        )
    )


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def search_ansys_docs(
    query: str,
    doc: str = "",
    top_k: int = 5,
    scope: str = "api",
    product: str = "",
    release: str = "",
    category: str = "",
    sdk_version: str = "",
) -> dict:
    """Keyword-search the ANSYS docs; returns ranked snippets with source and chunk_id.

    Args:
        query: Search terms. English API terms match best (case-insensitive substring).
        doc: Optional document name (from list_ansys_docs) to restrict the search.
        product: Optional exact product identifier, such as "fluent".
        release: Optional exact product release recorded in the catalog, such as "v251".
        category: Optional document category, such as "api_reference" or "tutorial".
        sdk_version: Optional exact SDK version; separate from the product release.
        top_k: Maximum number of results to return.
        scope: "api" (default) searches only API reference docs; "all" searches every indexed doc.
    """
    return _envelope(
        docs_index.search(
            query,
            doc=doc or None,
            top_k=top_k,
            scope=scope,
            product=product or None,
            release=release or None,
            category=category or None,
            sdk_version=sdk_version or None,
        )
    )


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def get_ansys_doc_chunk(doc: str, chunk_id: int, context: int = 0) -> dict:
    """Fetch the full text of a documentation chunk from a search result.

    Args:
        doc: Document name (as returned by search_ansys_docs or list_ansys_docs).
        chunk_id: The chunk_id from a search result.
        context: Number of neighbouring chunks to include on each side (0 = just this chunk).
    """
    return _envelope(docs_index.get_chunk(doc, chunk_id, context=context))


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def rebuild_ansys_docs_index() -> dict:
    """Rebuild the FTS5 index from curated documents, the product catalog, and extra roots."""
    return _envelope(docs_index.build_index())


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def ans_get_knowledge_dictionary(product: str = "", topic: str = "") -> dict:
    """Read curated ANSYS knowledge dictionary pages and topics.

    Args:
        product: Optional product identifier, such as "cfx", "mechanical", or "optislang".
        topic: Optional topic heading or keyword within the product dictionary.
    """
    kd_root = REPO_ROOT / "docs" / "knowledge_dictionary"
    if not kd_root.is_dir():
        return _envelope({"ok": False, "error": "Knowledge dictionary directory not found."})

    # If no product specified, return index of available dictionaries
    if not product:
        topics_csv = kd_root / "topics.csv"
        product_topic_counts: dict[str, int] = {}
        if topics_csv.is_file():
            try:
                with open(topics_csv, "r", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        p = row.get("product", "").strip().lower()
                        if p:
                            product_topic_counts[p] = product_topic_counts.get(p, 0) + 1
            except Exception:
                pass

        dictionaries = []
        for md_file in sorted(kd_root.glob("*.md")):
            if md_file.name.lower() in {"readme.md", "conversion_status.md"}:
                continue
            p_name = md_file.stem.lower()
            dictionaries.append(
                {
                    "product": p_name,
                    "file": md_file.name,
                    "size_bytes": md_file.stat().st_size,
                    "topic_count": product_topic_counts.get(p_name, 0),
                }
            )
        return _envelope(
            {
                "ok": True,
                "total_products": len(dictionaries),
                "dictionaries": dictionaries,
                "hint": "Pass product='<name>' to view the product dictionary overview and topic list.",
            }
        )

    # Resolve product dictionary
    target_md = None
    prod_clean = product.strip().lower().replace("-", "_").replace(" ", "_")
    candidates = [
        kd_root / f"{prod_clean}.md",
        kd_root / f"{product.strip().lower()}.md",
    ]
    for c in candidates:
        if c.is_file():
            target_md = c
            break

    if target_md is None:
        for md_file in kd_root.glob("*.md"):
            if prod_clean in md_file.stem.lower():
                target_md = md_file
                break

    if target_md is None:
        return _envelope(
            {
                "ok": False,
                "error": f"Product dictionary '{product}' not found in knowledge dictionary.",
            }
        )

    content = target_md.read_text(encoding="utf-8", errors="replace")

    # If topic is empty, parse and return overview and topic sections index
    if not topic:
        headings = []
        for line in content.splitlines():
            if line.startswith("### "):
                headings.append(line.replace("### ", "").strip())
        overview_lines = []
        for line in content.splitlines()[:40]:
            if line.startswith("## "):
                break
            overview_lines.append(line)
        return _envelope(
            {
                "ok": True,
                "product": target_md.stem,
                "file": target_md.name,
                "overview": "\n".join(overview_lines).strip(),
                "topics_count": len(headings),
                "topics": headings,
                "hint": "Pass topic='<topic_name>' to fetch full text of that specific topic section.",
            }
        )

    # Search specific topic section
    sections = re.split(r"\n(?=###\s+)", content)
    matched_section = None
    query_lower = topic.strip().lower()

    for sec in sections:
        if not sec.startswith("### "):
            continue
        first_line = sec.splitlines()[0].lower()
        if query_lower in first_line:
            matched_section = sec
            break

    if not matched_section:
        for sec in sections:
            if query_lower in sec.lower():
                matched_section = sec
                break

    if matched_section:
        return _envelope(
            {
                "ok": True,
                "product": target_md.stem,
                "topic_query": topic,
                "matched_text": matched_section.strip(),
            }
        )

    return _envelope(
        {
            "ok": False,
            "product": target_md.stem,
            "error": f"Topic '{topic}' not found in {target_md.name}.",
        }
    )
