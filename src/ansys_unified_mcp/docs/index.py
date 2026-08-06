"""Build and query the ANSYS API-docs FTS5 index.

Pipeline: read source markdown -> clean (docs/clean.py) -> write cleaned copy to
Documentation_clean/ -> chunk -> insert into a SQLite FTS5 (trigram) table.

The trigram tokenizer gives case-insensitive English substring matching and
partial CJK matching (Chinese queries need >= 3 characters). Concept-level
Chinese-to-English matching is out of scope for keyword search and is left to a
future semantic layer.
"""

from __future__ import annotations

import sqlite3
import threading
from typing import Optional

from ansys_unified_mcp.docs import config as cfg
from ansys_unified_mcp.docs.clean import clean_markdown

_lock = threading.Lock()

# Column order in the FTS5 table: 0=doc, 1=ord, 2=heading, 3=body
_BODY_COL = 3


def _chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Split text into ~size-char chunks, snapping to line boundaries, with overlap."""
    chunks: list[str] = []
    i, n = 0, len(text)
    while i < n:
        end = min(i + size, n)
        if end < n:
            nl = text.rfind("\n", i + size - overlap, end)
            if nl > i:
                end = nl
        chunk = text[i:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        i = max(end - overlap, i + 1)
    return chunks


def _heading_of(chunk: str) -> str:
    """Best-guess label: first non-empty, non-heading-marker line, trimmed."""
    for line in chunk.splitlines():
        s = line.strip().lstrip("#").strip()
        if s:
            return s[:120]
    return ""


def _connect() -> sqlite3.Connection:
    con = sqlite3.connect(str(cfg.INDEX_PATH))
    con.row_factory = sqlite3.Row
    return con


def _needs_rebuild() -> bool:
    if not cfg.INDEX_PATH.exists():
        return True
    index_mtime = cfg.INDEX_PATH.stat().st_mtime
    for doc in cfg.API_DOCS:
        src = cfg.SOURCE_DIR / f"{doc['name']}.md"
        if src.exists() and src.stat().st_mtime > index_mtime:
            return True
    return False


def build_index() -> dict:
    """(Re)build the cleaned copies and the FTS5 index. Returns a summary."""
    cfg.CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    if cfg.INDEX_PATH.exists():
        cfg.INDEX_PATH.unlink()

    con = _connect()
    summary: list[dict] = []
    try:
        con.execute(
            "CREATE VIRTUAL TABLE chunks USING fts5("
            "doc UNINDEXED, ord UNINDEXED, heading, body, tokenize='trigram')"
        )
        con.execute(
            "CREATE TABLE docs_meta ("
            "name TEXT PRIMARY KEY, title TEXT, category TEXT, product TEXT, "
            "chunks INTEGER, chars INTEGER)"
        )

        for doc in cfg.API_DOCS:
            src = cfg.SOURCE_DIR / f"{doc['name']}.md"
            if not src.exists():
                summary.append({"name": doc["name"], "status": "source_missing"})
                continue

            raw = src.read_text(encoding="utf-8", errors="replace")
            cleaned = clean_markdown(raw, style=doc.get("style", "ansys"))
            (cfg.CLEAN_DIR / f"{doc['name']}.md").write_text(cleaned, encoding="utf-8")

            parts = _chunk_text(cleaned, cfg.CHUNK_SIZE, cfg.CHUNK_OVERLAP)
            con.executemany(
                "INSERT INTO chunks(doc, ord, heading, body) VALUES (?, ?, ?, ?)",
                [(doc["name"], i, _heading_of(p), p) for i, p in enumerate(parts)],
            )
            con.execute(
                "INSERT INTO docs_meta VALUES (?, ?, ?, ?, ?, ?)",
                (doc["name"], doc["title"], doc["category"], doc["product"],
                 len(parts), len(cleaned)),
            )
            summary.append({
                "name": doc["name"], "status": "indexed",
                "chunks": len(parts), "chars": len(cleaned),
            })
        con.commit()
    finally:
        con.close()

    return {"ok": True, "index_path": str(cfg.INDEX_PATH), "docs": summary}


def ensure_index(force: bool = False) -> Optional[dict]:
    """Build the index if missing/stale (or when forced). Thread-safe."""
    with _lock:
        if force or _needs_rebuild():
            return build_index()
    return None


def _match_query(query: str) -> str:
    """Build an FTS5 MATCH expression from a raw user query.

    Each whitespace-separated term becomes its own quoted phrase and the terms
    are AND-ed (FTS5 treats space-separated phrases as AND). This makes
    multi-word queries match documents containing all terms in any order,
    rather than requiring the exact contiguous phrase.

    The trigram tokenizer cannot match tokens shorter than 3 characters, so
    such terms are dropped. If nothing remains (e.g. an all-short query), fall
    back to quoting the whole query as a single phrase.
    """
    def quote(term: str) -> str:
        return '"' + term.replace('"', '""') + '"'

    terms = [t for t in query.split() if len(t) >= 3]
    if not terms:
        return quote(query.strip())
    return " ".join(quote(t) for t in terms)


def _run_search(con: sqlite3.Connection, query: str, doc_names: Optional[list[str]], top_k: int) -> list:
    """Run one FTS5 query, optionally restricted to a set of doc names."""
    sql = (
        "SELECT doc, ord, heading, "
        "snippet(chunks, {col}, '[[', ']]', ' … ', 16) AS snip, "
        "bm25(chunks) AS score "
        "FROM chunks WHERE chunks MATCH ?"
    ).format(col=_BODY_COL)
    params: list = [_match_query(query)]
    if doc_names:
        placeholders = ",".join("?" for _ in doc_names)
        sql += f" AND doc IN ({placeholders})"
        params.extend(doc_names)
    sql += " ORDER BY score LIMIT ?"
    params.append(int(top_k))
    return con.execute(sql, params).fetchall()


def search(query: str, doc: Optional[str] = None, top_k: int = 5, scope: str = "api") -> dict:
    """Keyword-search the docs.

    scope:
        "api" (default) - search only the crisp API docs (PRIMARY_CATEGORIES);
            if that yields nothing, transparently widen to all docs.
        "all"           - search every indexed doc (API + guide + tutorial).
        Ignored when `doc` is given (an explicit doc always wins).
    """
    ensure_index()
    if not query or not query.strip():
        return {"ok": False, "error": "query 不得為空。"}

    scope = scope if scope in ("api", "all") else "api"
    if doc:
        doc_names: Optional[list[str]] = [doc]
        used_scope = "doc"
    elif scope == "api":
        doc_names = cfg.primary_doc_names()
        used_scope = "api"
    else:
        doc_names = None
        used_scope = "all"

    con = _connect()
    try:
        rows = _run_search(con, query, doc_names, top_k)
        # Fallback: narrow API search found nothing -> widen to all docs.
        if not rows and used_scope == "api":
            rows = _run_search(con, query, None, top_k)
            used_scope = "all"
    except sqlite3.OperationalError as exc:
        return {"ok": False, "error": f"search failed: {exc}"}
    finally:
        con.close()

    results = [
        {
            "doc": r["doc"],
            "chunk_id": r["ord"],
            "heading": r["heading"],
            "snippet": r["snip"],
            "score": round(r["score"], 3),
        }
        for r in rows
    ]
    return {"ok": True, "query": query, "scope": used_scope, "count": len(results), "results": results}


def get_chunk(doc: str, chunk_id: int, context: int = 0) -> dict:
    ensure_index()
    con = _connect()
    try:
        lo = max(0, chunk_id - max(0, context))
        hi = chunk_id + max(0, context)
        rows = con.execute(
            "SELECT ord, heading, body FROM chunks "
            "WHERE doc = ? AND ord BETWEEN ? AND ? ORDER BY ord",
            (doc, lo, hi),
        ).fetchall()
    finally:
        con.close()

    if not rows:
        return {"ok": False, "error": f"No chunk {chunk_id} in doc {doc!r}."}
    body = "\n\n".join(r["body"] for r in rows)
    return {
        "ok": True, "doc": doc, "chunk_id": chunk_id,
        "range": [rows[0]["ord"], rows[-1]["ord"]],
        "heading": rows[0]["heading"], "text": body,
    }


def list_docs() -> dict:
    ensure_index()
    con = _connect()
    try:
        rows = con.execute(
            "SELECT name, title, category, product, chunks, chars "
            "FROM docs_meta ORDER BY name"
        ).fetchall()
    finally:
        con.close()
    return {"ok": True, "docs": [dict(r) for r in rows]}
