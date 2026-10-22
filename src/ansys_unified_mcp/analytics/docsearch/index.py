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
import os
import tempfile
import hashlib
import re
import threading
import json
from typing import Optional
from pathlib import Path

from ansys_unified_mcp.analytics.docsearch import config as cfg
from ansys_unified_mcp.analytics.docsearch.clean import clean_markdown

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


def _connect(path=None) -> sqlite3.Connection:
    con = sqlite3.connect(str(path or cfg.INDEX_PATH))
    con.row_factory = sqlite3.Row
    return con


def _needs_rebuild() -> bool:
    if not cfg.INDEX_PATH.exists():
        return True
    try:
        con = _connect()
        cols = {r["name"] for r in con.execute("PRAGMA table_info(docs_meta)")}
        state_cols = {r["name"] for r in con.execute("PRAGMA table_info(index_state)")}
        con.close()
        if not {"source_path", "release", "content_hash", "quality", "chunk_count"} <= cols:
            return True
        if not {"key", "value"} <= state_cols:
            return True
    except sqlite3.Error:
        return True
    index_mtime = cfg.INDEX_PATH.stat().st_mtime
    for doc in cfg.API_DOCS:
        src = cfg.SOURCE_DIR / f"{doc['name']}.md"
        if src.exists() and src.stat().st_mtime > index_mtime:
            return True
    try:
        con = _connect()
        row = con.execute("SELECT value FROM index_state WHERE key='extra_source_roots'").fetchone()
        con.close()
        indexed_roots = json.loads(row["value"]) if row else []
        if indexed_roots != sorted(str(root.resolve()) for root in cfg.EXTRA_SOURCE_DIRS):
            return True
    except (sqlite3.Error, ValueError, OSError):
        return True
    return False


def build_index() -> dict:
    """(Re)build the cleaned copies and the FTS5 index. Returns a summary."""
    cfg.CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="docs-index-", suffix=".sqlite", dir=str(cfg.CLEAN_DIR))
    os.close(fd)
    temp_path = temp_name
    con = _connect(temp_path)
    summary: list[dict] = []
    try:
        con.execute(
            "CREATE VIRTUAL TABLE chunks USING fts5("
            "doc UNINDEXED, ord UNINDEXED, heading, body, tokenize='trigram')"
        )
        con.execute("CREATE TABLE index_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        con.execute(
            "CREATE TABLE docs_meta ("
            "name TEXT PRIMARY KEY, title TEXT, category TEXT, product TEXT, "
            "chunk_count INTEGER, chars INTEGER, source_path TEXT, release TEXT, content_hash TEXT, quality TEXT)"
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
                "INSERT INTO docs_meta VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (doc["name"], doc["title"], doc["category"], doc["product"],
                 len(parts), len(cleaned), str(src), _release_hint(raw), hashlib.sha256(raw.encode("utf-8")).hexdigest(), _quality(raw)),
            )
            summary.append({
                "name": doc["name"], "status": "indexed",
                "chunks": len(parts), "chars": len(cleaned),
            })

        # 掃描並索引 skills 與 agents/steering/reference
        processed_names = {d["name"] for d in cfg.API_DOCS}
        if (cfg.REPO_ROOT / "agents" / "skills").is_dir():
            skills_path = cfg.REPO_ROOT / "agents" / "skills"
        elif (cfg.REPO_ROOT / "skills").is_dir():
            skills_path = cfg.REPO_ROOT / "skills"
        else:
            skills_path = cfg.REPO_ROOT / "SKILLs"
        steering_ref_path = (cfg.REPO_ROOT / "agents" / "steering" / "reference") if (cfg.REPO_ROOT / "agents" / "steering" / "reference").is_dir() else (cfg.REPO_ROOT / "steering" / "reference")
        scan_paths = [
            (skills_path, "skill"),
            (steering_ref_path, "architecture"),
        ]

        for base_dir, category in scan_paths:
            if not base_dir.exists():
                continue
            for md_file in base_dir.rglob("*.md"):
                rel_name = md_file.relative_to(cfg.REPO_ROOT).as_posix().replace("/", "_").replace(".md", "")
                if rel_name in processed_names:
                    continue
                processed_names.add(rel_name)
                title = md_file.stem.replace("_", " ").replace("-", " ").title()

                lower_path = md_file.as_posix().lower()
                if "fluent" in lower_path or "mixing_elbow" in lower_path:
                    product = "fluent"
                elif "dpf" in lower_path or "submodeling" in lower_path:
                    product = "dpf"
                elif "geometry" in lower_path:
                    product = "geometry"
                elif "spaceclaim" in lower_path:
                    product = "spaceclaim"
                elif "mechanical" in lower_path:
                    product = "mechanical"
                elif "lsdyna" in lower_path or "ls-dyna" in lower_path or "ls-prepost" in lower_path:
                    product = "lsdyna"
                elif "optislang" in lower_path:
                    product = "optislang"
                elif "icepak" in lower_path:
                    product = "icepak"
                elif "sherlock" in lower_path:
                    product = "sherlock"
                elif "speos" in lower_path or "illumination" in lower_path:
                    product = "speos"
                elif "zemax" in lower_path or "zos-api" in lower_path:
                    product = "zemax"
                elif "lumerical" in lower_path or "lumapi" in lower_path:
                    product = "lumerical"
                elif "thermal" in lower_path:
                    product = "thermal"
                elif "parametric" in lower_path:
                    product = "parametric_study"
                elif "pcb" in lower_path:
                    product = "pcb_warpage"
                elif "workbench" in lower_path:
                    product = "workbench"
                elif "error" in lower_path:
                    product = "error_catalog"
                else:
                    product = "general"

                raw_text = md_file.read_text(encoding="utf-8", errors="replace")
                if not raw_text.strip():
                    continue

                parts = _chunk_text(raw_text, cfg.CHUNK_SIZE, cfg.CHUNK_OVERLAP)
                if not parts:
                    continue

                con.executemany(
                    "INSERT INTO chunks(doc, ord, heading, body) VALUES (?, ?, ?, ?)",
                    [(rel_name, i, _heading_of(p), p) for i, p in enumerate(parts)],
                )
                con.execute(
                    "INSERT OR REPLACE INTO docs_meta VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (rel_name, title, category, product, len(parts), len(raw_text), str(md_file), _release_hint(raw_text), hashlib.sha256(raw_text.encode("utf-8")).hexdigest(), _quality(raw_text)),
                )
                summary.append({
                    "name": rel_name, "status": "indexed",
                    "chunks": len(parts), "chars": len(raw_text),
                })

        # 額外文件庫採環境設定，不將任何使用者機器路徑寫入程式碼。
        # 只收錄 Markdown；PDF/原始手冊由 inventory 工具盤點，須先轉檔再索引。
        for root in cfg.EXTRA_SOURCE_DIRS:
            if not root.is_dir():
                summary.append({"name": str(root), "status": "source_missing"})
                continue
            for md_file in root.rglob("*.md"):
                try:
                    resolved = md_file.resolve()
                    relative = resolved.relative_to(root.resolve()).as_posix()
                    raw_text = md_file.read_text(encoding="utf-8", errors="replace")
                except (OSError, ValueError):
                    continue
                if not raw_text.strip():
                    continue
                digest = hashlib.sha256(str(resolved).encode("utf-8")).hexdigest()[:12]
                rel_name = f"external_{digest}_{Path(relative).stem}"
                if rel_name in processed_names:
                    continue
                processed_names.add(rel_name)
                lower = relative.lower()
                product = next((value for key, value in (
                    ("mechanical", "mechanical"), ("ls-dyna", "lsdyna"), ("lsdyna", "lsdyna"),
                    ("ls-prepost", "ls-prepost"), ("spaceclaim", "spaceclaim"),
                    ("icepak", "icepak"), ("sherlock", "sherlock"), ("speos", "speos"),
                    ("zemax", "zemax"), ("lumerical", "lumerical"), ("fluent", "fluent"),
                    ("optislang", "optislang"), ("thermal", "thermal"),
                ) if key in lower), "general")
                category = (
                    "tutorial" if "tutorial" in lower or "example" in lower else
                    "api_reference" if "api" in lower or "reference" in lower else
                    "guide"
                )
                parts = _chunk_text(raw_text, cfg.CHUNK_SIZE, cfg.CHUNK_OVERLAP)
                con.executemany(
                    "INSERT INTO chunks(doc, ord, heading, body) VALUES (?, ?, ?, ?)",
                    [(rel_name, i, _heading_of(part), part) for i, part in enumerate(parts)],
                )
                con.execute(
                    "INSERT INTO docs_meta VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (rel_name, Path(relative).stem, category, product, len(parts), len(raw_text),
                     str(resolved), _release_hint(raw_text), hashlib.sha256(raw_text.encode("utf-8")).hexdigest(),
                     _quality(raw_text)),
                )
                summary.append({"name": rel_name, "status": "indexed", "chunks": len(parts), "chars": len(raw_text)})

        missing_extra_roots = [str(root) for root in cfg.EXTRA_SOURCE_DIRS if not root.is_dir()]
        if missing_extra_roots:
            raise RuntimeError(
                "外部文件來源暫時不可用；保留現有索引，不以不完整來源重建。"
                f" missing_roots={missing_extra_roots}"
            )

        con.execute(
            "INSERT INTO index_state(key, value) VALUES ('extra_source_roots', ?)",
            (json.dumps(sorted(str(root.resolve()) for root in cfg.EXTRA_SOURCE_DIRS)),),
        )
        con.commit()
    except Exception:
        con.close()
        Path(temp_path).unlink(missing_ok=True)
        raise
    finally:
        if con:
            con.close()

    check = _connect(temp_path)
    try:
        indexed_documents = check.execute("SELECT COUNT(*) FROM docs_meta").fetchone()[0]
        chunk_count = check.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        curated_names = [doc["name"] for doc in cfg.API_DOCS]
        placeholders = ",".join("?" for _ in curated_names)
        curated_indexed_names = {
            row[0] for row in check.execute(
                f"SELECT name FROM docs_meta WHERE name IN ({placeholders})", curated_names
            ).fetchall()
        }
        integrity = check.execute("PRAGMA integrity_check").fetchone()[0]
        bad_metadata = check.execute(
            "SELECT COUNT(*) FROM docs_meta WHERE source_path IS NULL OR content_hash IS NULL OR length(content_hash) != 64"
        ).fetchone()[0]
    finally:
        check.close()
    previous_curated_names = set()
    if cfg.INDEX_PATH.is_file():
        try:
            previous = _connect(cfg.INDEX_PATH)
            previous_curated_names = {
                row[0] for row in previous.execute(
                    f"SELECT name FROM docs_meta WHERE name IN ({placeholders})", curated_names
                ).fetchall()
            }
            previous.close()
        except sqlite3.Error:
            previous_curated_names = set()
    missing_previous = previous_curated_names - curated_indexed_names
    curated_indexed = len(curated_indexed_names)
    if (
        indexed_documents == 0
        or chunk_count == 0
        or curated_indexed == 0
        or missing_previous
        or integrity != "ok"
        or bad_metadata
    ):
        Path(temp_path).unlink(missing_ok=True)
        raise RuntimeError(
            "新文件索引未通過完整性驗證；保留現有索引。"
            f" docs={indexed_documents}, chunks={chunk_count}, curated_docs={curated_indexed}, "
            f"missing_previous_curated={sorted(missing_previous)}, "
            f"integrity={integrity}, bad_metadata={bad_metadata}"
        )

    os.replace(temp_path, cfg.INDEX_PATH)

    return {
        "ok": True,
        "index_path": str(cfg.INDEX_PATH),
        "docs": summary,
        "indexed_count": indexed_documents,
        "chunk_count": chunk_count,
        "curated_indexed_count": curated_indexed,
    }


def _release_hint(text: str) -> str:
    match = re.search(r"\b(20\d{2}\s*R[12]|v(?:251|252|261))\b", text[:12000], re.I)
    return match.group(1) if match else "unknown"


def _quality(text: str) -> str:
    if not text.strip():
        return "empty"
    if len(text) < 12000 and re.search(r"download|not available|contents only", text[:4000], re.I):
        return "stub_or_download_page"
    if "{{" in text or "{%" in text:
        return "template"
    return "body_present"


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


def _run_search(con: sqlite3.Connection, query: str, doc_names: Optional[list[str]], top_k: int,
                product: Optional[str] = None, release: Optional[str] = None,
                category: Optional[str] = None) -> list:
    """Run one FTS5 query, optionally restricted to a set of doc names."""
    sql = (
        "SELECT chunks.doc, chunks.ord, chunks.heading, docs_meta.source_path, "
        "docs_meta.release, docs_meta.product, "
        "snippet(chunks, {col}, '[[', ']]', ' … ', 16) AS snip, "
        "bm25(chunks) AS score "
        "FROM chunks JOIN docs_meta ON docs_meta.name=chunks.doc WHERE chunks MATCH ?"
    ).format(col=_BODY_COL)
    params: list = [_match_query(query)]
    if doc_names:
        placeholders = ",".join("?" for _ in doc_names)
        sql += f" AND doc IN ({placeholders})"
        params.extend(doc_names)
    if any((product, release, category)):
        sql += (
            " AND doc IN (SELECT name FROM docs_meta WHERE "
            "(? IS NULL OR product=?) AND (? IS NULL OR category=?) AND (? IS NULL OR release=?))"
        )
        params.extend([product, product, category, category, release, release])
    sql += " ORDER BY score LIMIT ?"
    params.append(int(top_k))
    return con.execute(sql, params).fetchall()


def search(query: str, doc: Optional[str] = None, top_k: int = 5, scope: str = "api",
           product: Optional[str] = None, release: Optional[str] = None,
           category: Optional[str] = None) -> dict:
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
        rows = _run_search(con, query, doc_names, top_k, product, release, category)
        # Fallback: narrow API search found nothing -> widen to all docs.
        if not rows and used_scope == "api":
            rows = _run_search(con, query, None, top_k, product, release, category)
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
            "source_path": r["source_path"],
            "release": r["release"],
            "product": r["product"],
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
            "SELECT name, title, category, product, release, source_path, content_hash, quality, chunk_count AS chunks, chars "
            "FROM docs_meta ORDER BY name"
        ).fetchall()
    finally:
        con.close()
    return {"ok": True, "docs": [dict(r) for r in rows]}
