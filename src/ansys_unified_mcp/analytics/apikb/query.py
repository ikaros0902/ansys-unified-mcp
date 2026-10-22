"""
ANSYS API 知識庫查詢引擎 (Query Engine)
提供 FTS5 全文檢索、單一 API 詳細符號調用、以及型別物件導航鏈搜尋 (Pathfinding)。
"""
import re
import sqlite3
from typing import Optional, Any
from collections import deque

from ansys_unified_mcp.analytics.apikb import config as cfg
from ansys_unified_mcp.analytics.apikb.build import build_database
from ansys_unified_mcp.analytics.apikb.build import _schema_is_current

def _get_connection() -> sqlite3.Connection:
    if not _schema_is_current(cfg.DB_PATH):
        build_database(force=True)
    conn = sqlite3.connect(str(cfg.DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def search(
    query: str,
    product: Optional[str] = None,
    kind: Optional[str] = None,
    top_k: int = 8,
    release: Optional[str] = None,
    interface: Optional[str] = None,
) -> list[dict]:
    """檢索 API 符號與成員 (FTS5 trigram 匹配)"""
    if not query or not query.strip():
        return []

    # 去除特殊符號避免語法錯誤
    clean_q = re.sub(r'["\';]', "", query.strip())
    if not clean_q:
        return []

    conn = _get_connection()
    cur = conn.cursor()

    words = clean_q.split()
    query_variants = [f'"{clean_q}"']
    if len(words) > 1:
        query_variants.append(" AND ".join(f'"{w}"' for w in words))
        query_variants.append(" OR ".join(f'"{w}"' for w in words))

    rows = []
    base_sql = """
        SELECT f.item_type, f.ref_id, f.product, f.fqname, f.name, f.signature, f.doc,
               f.release, f.interface, a.source_path, a.sha256, a.sdk_version,
               bm25(search_fts) as rank
        FROM search_fts AS f
        LEFT JOIN api_sources AS a ON a.id = CAST(f.source_id AS INTEGER)
        WHERE search_fts MATCH ?
    """
    if product:
        base_sql += " AND f.product = ?"
    if release:
        base_sql += " AND f.release = ?"
    if interface:
        base_sql += " AND f.interface = ?"
    base_sql += " ORDER BY rank LIMIT ?"

    for fts_expr in query_variants:
        params = [fts_expr]
        if product:
            params.append(product.lower())
        if release:
            params.append(release)
        if interface:
            params.append(interface)
        params.append(top_k * 3)

        try:
            cur.execute(base_sql, params)
            rows = cur.fetchall()
            if rows:
                break
        except Exception:
            continue

    results = []
    seen = set()

    for r in rows:
        fqname = r["fqname"]
        version_key = (r["product"], r["release"], r["interface"], fqname)
        if version_key in seen:
            continue
        seen.add(version_key)

        doc_snippet = (r["doc"] or "").strip().replace("\n", " ")
        if len(doc_snippet) > 160:
            doc_snippet = doc_snippet[:157] + "..."

        results.append({
            "item_type": r["item_type"],
            "product": r["product"],
            "fqname": fqname,
            "name": r["name"],
            "signature": r["signature"] or "",
            "doc": doc_snippet,
            "score": round(-float(r["rank"]), 3),
            "release": r["release"],
            "interface": r["interface"],
            "source": {
                "path": r["source_path"], "sha256": r["sha256"],
                "sdk_version": r["sdk_version"],
            },
        })

        if len(results) >= top_k:
            break

    conn.close()
    return results

def get(
    fqname: str,
    include: tuple[str, ...] = ("members", "edges"),
    limit: int = 50,
    product: Optional[str] = None,
    release: Optional[str] = None,
    interface: Optional[str] = None,
) -> Optional[dict]:
    """獲取特定符號 (Symbol) 之詳細定義、所屬成員與相連型別"""
    conn = _get_connection()
    cur = conn.cursor()

    # 先以完全限定名稱查詢，若無則以簡稱查詢
    clauses = ["(fqname = ? OR name = ?)"]
    params: list = [fqname, fqname]
    for column, value in (("product", product), ("release", release), ("interface", interface)):
        if value:
            clauses.append(f"{column} = ?")
            params.append(value.lower() if column == "product" else value)
    rows = cur.execute(
        "SELECT id, product, kind, fqname, name, doc, release, interface, source_id "
        "FROM symbols WHERE " + " AND ".join(clauses) + " ORDER BY product, release, interface",
        params,
    ).fetchall()

    if not rows:
        conn.close()
        return None

    versions = {(row["product"], row["release"], row["interface"]) for row in rows}
    if len(versions) > 1:
        candidates = [
            {"product": p, "release": r, "interface": i}
            for p, r, i in sorted(versions)
        ]
        conn.close()
        return {"ambiguous": True, "candidates": candidates}
    row = rows[0]

    sym_id = row["id"]
    symbol_info = {
        "id": sym_id,
        "product": row["product"],
        "kind": row["kind"],
        "fqname": row["fqname"],
        "name": row["name"],
        "doc": row["doc"] or "",
        "release": row["release"],
        "interface": row["interface"],
        "members": [],
        "edges_out": [],
        "edges_in": []
    }
    source = cur.execute(
        "SELECT source_path, sha256, sdk_version FROM api_sources WHERE id = ?",
        (row["source_id"],),
    ).fetchone()
    symbol_info["source"] = dict(source) if source else {}

    if "members" in include:
        cur.execute("""
            SELECT m.kind, m.name, m.signature, m.return_type, m.doc, sm.is_inherited
            FROM members m
            JOIN symbol_members sm ON m.id = sm.member_id
            WHERE sm.symbol_id = ?
            ORDER BY sm.is_inherited ASC, m.name ASC
            LIMIT ?
        """, (sym_id, limit))
        for m in cur.fetchall():
            symbol_info["members"].append({
                "kind": m["kind"],
                "name": m["name"],
                "signature": m["signature"] or "",
                "return_type": m["return_type"] or "",
                "is_inherited": bool(m["is_inherited"]),
                "doc": (m["doc"] or "").strip()
            })

    if "edges" in include:
        # 出邊 (此型別返回或擁有哪些型別)
        cur.execute("""
            SELECT e.rel, s.fqname as target_fqname, s.name as target_name, m.name as via_member
            FROM edges e
            JOIN symbols s ON e.dst_symbol_id = s.id
            LEFT JOIN members m ON e.via_member_id = m.id
            WHERE e.src_symbol_id = ?
            LIMIT ?
        """, (sym_id, limit))
        for e in cur.fetchall():
            symbol_info["edges_out"].append({
                "rel": e["rel"],
                "target": e["target_fqname"],
                "target_name": e["target_name"],
                "via": e["via_member"] or ""
            })

        # 入邊 (哪些型別可以導向此型別)
        cur.execute("""
            SELECT e.rel, s.fqname as source_fqname, s.name as source_name, m.name as via_member
            FROM edges e
            JOIN symbols s ON e.src_symbol_id = s.id
            LEFT JOIN members m ON e.via_member_id = m.id
            WHERE e.dst_symbol_id = ?
            LIMIT ?
        """, (sym_id, limit))
        for e in cur.fetchall():
            symbol_info["edges_in"].append({
                "rel": e["rel"],
                "source": e["source_fqname"],
                "source_name": e["source_name"],
                "via": e["via_member"] or ""
            })

    conn.close()
    return symbol_info

def path(
    from_type: str,
    to_type: str,
    product: Optional[str] = None,
    max_depth: int = 4,
    release: Optional[str] = None,
    interface: Optional[str] = None,
    report_ambiguity: bool = False,
) -> list[dict] | dict:
    """在型別關係圖上進行 BFS 搜尋，找出物件存取路徑"""
    start = get(from_type, include=(), limit=0, product=product,
                release=release, interface=interface)
    target = get(to_type, include=(), limit=0, product=product,
                 release=release, interface=interface)
    if (start or {}).get("ambiguous") or (target or {}).get("ambiguous"):
        if report_ambiguity:
            return {
                "ambiguous": True,
                "from_candidates": (start or {}).get("candidates", []),
                "to_candidates": (target or {}).get("candidates", []),
            }
        return []
    if not start or not target:
        return []

    conn = _get_connection()
    cur = conn.cursor()

    start_row = cur.execute(
        "SELECT id, fqname, name, release, interface FROM symbols WHERE id = ?",
        (start["id"],),
    ).fetchone()
    target_row = cur.execute(
        "SELECT id, fqname, name FROM symbols WHERE id = ?", (target["id"],)
    ).fetchone()
    start_id, target_id = start_row["id"], target_row["id"]

    if start_id == target_id:
        conn.close()
        return [{"path": [start_row["name"]], "steps": [],
                 "release": start_row["release"], "interface": start_row["interface"]}]

    # BFS 隊列: (current_symbol_id, current_path_names, steps_list)
    queue = deque([(start_id, [start_row["name"]], [])])
    visited = {start_id}
    found_paths = []

    while queue and len(found_paths) < 3:
        curr_id, path_names, steps = queue.popleft()

        if len(steps) >= max_depth:
            continue

        cur.execute("""
            SELECT e.dst_symbol_id, s.name as dst_name, s.fqname as dst_fqname, e.rel, m.name as via_member
            FROM edges e
            JOIN symbols s ON e.dst_symbol_id = s.id
            LEFT JOIN members m ON e.via_member_id = m.id
            WHERE e.src_symbol_id = ? AND s.release = ? AND s.interface = ?
        """, (curr_id, start_row["release"], start_row["interface"]))

        for edge in cur.fetchall():
            nxt_id = edge["dst_symbol_id"]
            dst_name = edge["dst_name"]
            via = edge["via_member"] or "get()"
            rel = edge["rel"]

            new_step = {
                "from": path_names[-1],
                "to": dst_name,
                "via": via,
                "rel": rel
            }

            if nxt_id == target_id:
                found_paths.append({
                    "path_display": " -> ".join(path_names + [f"{via} -> {dst_name}"]),
                    "nodes": path_names + [dst_name],
                    "steps": steps + [new_step],
                    "release": start_row["release"],
                    "interface": start_row["interface"],
                })
                break
            elif nxt_id not in visited and len(steps) + 1 < max_depth:
                visited.add(nxt_id)
                queue.append((nxt_id, path_names + [dst_name], steps + [new_step]))

    conn.close()
    return found_paths
