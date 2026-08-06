"""MCP tools for searching the ANSYS API/scripting documentation.

Backed by a local SQLite FTS5 (trigram) index over the cleaned API docs. Lets
the AI look up API/scripting details by keyword without loading whole (multi-MB)
documents into context.
"""

from __future__ import annotations

import json

from ansys_unified_mcp.shared import mcp
from ansys_unified_mcp.docs import index as docs_index


def _json(data) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


@mcp.tool()
def list_ansys_docs() -> str:
    """List the indexed ANSYS API/scripting documents (name, title, category, chunk count)."""
    return _json(docs_index.list_docs())


@mcp.tool()
def search_ansys_docs(query: str, doc: str = "", top_k: int = 5, scope: str = "api") -> str:
    """Keyword-search the ANSYS docs; returns ranked snippets with source and chunk_id.

    Args:
        query: Search terms. English API terms match best (case-insensitive
            substring). Chinese queries need >= 3 characters and only match
            Chinese text present in the docs.
        doc: Optional document name (from list_ansys_docs) to restrict the search.
        top_k: Maximum number of results to return.
        scope: "api" (default) searches only the crisp API reference/scripting
            docs, then transparently widens to everything if nothing matches;
            "all" searches every indexed doc (guides and tutorials included).
            The returned "scope" field reports which scope produced the results.
    """
    return _json(docs_index.search(query, doc=doc or None, top_k=top_k, scope=scope))


@mcp.tool()
def get_ansys_doc_chunk(doc: str, chunk_id: int, context: int = 0) -> str:
    """Fetch the full text of a documentation chunk (from a search result).

    Args:
        doc: Document name (as returned by search_ansys_docs / list_ansys_docs).
        chunk_id: The chunk_id from a search result.
        context: Number of neighbouring chunks to include on each side (0 = just this chunk).
    """
    return _json(docs_index.get_chunk(doc, chunk_id, context=context))


@mcp.tool()
def rebuild_ansys_docs_index() -> str:
    """Rebuild the cleaned copies and the FTS5 search index from Documentation_md."""
    return _json(docs_index.build_index())
