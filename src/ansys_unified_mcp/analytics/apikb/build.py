"""
ANSYS API 知識庫建置管線 (Build Pipeline)
解析四大模組 JSON，執行去重正規化、推導型別導航邊 (Edges) 並建立 SQLite FTS5 索引。
"""
import re
import json
import sqlite3
import hashlib
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any

from ansys_unified_mcp.analytics.apikb import config as cfg

def split_camel_case(s: str) -> str:
    """將 CamelCase 或 snake_case 拆分為空格分隔的小寫詞"""
    if not s:
        return ""
    # 處理底線
    s = s.replace("_", " ")
    # 拆分大寫字元 (例如 AddFixedSupport -> Add Fixed Support)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z0-9])", r"\1 \2", s)
    return s.lower().strip()

def clean_type_name(raw: str) -> str:
    """提取乾淨的型別簡稱或類別名稱"""
    if not raw or raw in ("None", "void", "System.Void", "object"):
        return ""
    # 移除 typing.Optional[...]、typing.List[...] 等包裝
    match = re.search(r"\[(.*?)\]", raw)
    if match:
        raw = match.group(1)
    # 取最後的點後名稱
    parts = raw.split(".")
    return parts[-1].strip()


def _schema_is_current(path: Path) -> bool:
    """檢查資料庫版本欄位，舊快照在安全替換前保留可讀。"""
    if not path.is_file():
        return False
    try:
        con = sqlite3.connect(str(path))
        symbol_cols = {row[1] for row in con.execute("PRAGMA table_info(symbols)")}
        fts_cols = {row[1] for row in con.execute("PRAGMA table_info(search_fts)")}
        con.close()
    except sqlite3.Error:
        return False
    return {"release", "interface", "source_id"} <= symbol_cols and {
        "release", "interface", "source_id"
    } <= fts_cols


def _ensure_previous_sources_available(current_sources: list[tuple[str, Path]]) -> None:
    """避免某版 API 快照暫時缺失時，用其他版本覆蓋既有知識庫。"""
    if not cfg.DB_PATH.is_file():
        return
    try:
        conn = sqlite3.connect(str(cfg.DB_PATH))
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "api_sources" not in tables:
            conn.close()
            return
        previous_paths = {
            Path(row[0]).resolve()
            for row in conn.execute("SELECT DISTINCT source_path FROM api_sources")
            if row[0]
        }
        conn.close()
    except sqlite3.Error:
        return
    current_paths = {path.resolve() for _, path in current_sources}
    missing = sorted(str(path) for path in previous_paths if not path.is_file() or path not in current_paths)
    if missing:
        raise RuntimeError(
            "既有 API 來源快照暫時不可用；保留現有資料庫，不以不完整來源重建。"
            f" missing_sources={missing}"
        )

def build_database(force: bool = False) -> dict:
    """建置或重建 API 知識庫 SQLite 資料庫"""
    cfg.DB_DIR.mkdir(parents=True, exist_ok=True)
    current_sources = cfg.source_snapshots()
    _ensure_previous_sources_available(current_sources)

    if cfg.DB_PATH.exists() and not force and _schema_is_current(cfg.DB_PATH):
        db_mtime = cfg.DB_PATH.stat().st_mtime
        sources_modified = False
        for _, src_path in current_sources:
            if src_path.exists() and src_path.stat().st_mtime > db_mtime:
                sources_modified = True
                break
        if not sources_modified:
            return {"status": "up_to_date", "path": str(cfg.DB_PATH)}

    fd, temp_name = tempfile.mkstemp(
        prefix=f"{cfg.DB_PATH.stem}.", suffix=".tmp", dir=str(cfg.DB_DIR)
    )
    os.close(fd)
    temp_path = Path(temp_name)
    conn = sqlite3.connect(str(temp_path))
    conn.execute("PRAGMA synchronous = OFF")
    conn.execute("PRAGMA journal_mode = MEMORY")

    # 執行 Schema 定義
    with open(cfg.SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    cur = conn.cursor()

    source_records = []
    for product, source_path in current_sources:
        if not source_path.is_file():
            continue
        source = cfg.source_metadata(product, source_path)
        source["ingested_at"] = datetime.now(timezone.utc).isoformat()
        cur.execute(
            "INSERT INTO api_sources "
            "(product, release, interface, source_path, sdk_version, sha256, ingested_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            tuple(source[key] for key in (
                "product", "release", "interface", "source_path", "sdk_version", "sha256", "ingested_at"
            )),
        )
        source_records.append((product, source_path, source, cur.lastrowid))

    stats = {
        "symbols": 0,
        "unique_members": 0,
        "symbol_members": 0,
        "edges": 0,
        "fts_entries": 0,
    }

    # 符號與成員快取
    # symbols_map: fqname -> symbol_id, simple_name_map: name -> list[symbol_id]
    symbols_map = {}
    name_to_symbol_ids = {}

    # members_map: sig_hash -> member_id
    members_map = {}
    member_counts = {}  # member_id -> count of classes using it
    pending_symbol_members = [] # (symbol_id, member_id, is_inherited)
    pending_edges = []          # (src_symbol_id, target_type_str, rel, via_member_id)

    for product, source_path, source_info, source_id in source_records:
        before_symbol_id = cur.execute("SELECT COALESCE(MAX(id), 0) FROM symbols").fetchone()[0]
        # -------------------------------------------------------------
        # 1. 處理 Mechanical API
        # -------------------------------------------------------------
        mech_src = source_path if product == "mechanical" else Path("__missing__")
        if mech_src.exists():
            with open(mech_src, "r", encoding="utf-8") as f:
                mech_data = json.load(f)

            for mod_name, mod_info in mech_data.get("modules", {}).items():
                for cls_name, cls_info in mod_info.get("classes", {}).items():
                    fqname = f"{mod_name}.{cls_name}"
                    doc = cls_info.get("doc", "")
                    cur.execute(
                        "INSERT INTO symbols (product, kind, fqname, name, doc) VALUES (?, ?, ?, ?, ?)",
                        ("mechanical", "class", fqname, cls_name, doc)
                    )
                    sym_id = cur.lastrowid
                    symbols_map[fqname] = sym_id
                    name_to_symbol_ids.setdefault(cls_name, []).append(sym_id)
                    stats["symbols"] += 1

                    # 處理 Methods
                    for m in cls_info.get("methods", []):
                        m_name = m["name"]
                        params = ", ".join(f"{p['name']}: {p['type']}" for p in m.get("parameters", []))
                        sig = f"({params}) -> {m.get('return_type', '')}"
                        ret_type = m.get("return_type", "")
                        m_doc = m.get("doc", "")
                        sig_hash = hashlib.sha256(f"{source_id}:method:{m_name}:{sig}:{ret_type}".encode()).hexdigest()[:16]

                        if sig_hash not in members_map:
                            cur.execute(
                                "INSERT INTO members (sig_hash, kind, name, signature, return_type, doc) VALUES (?, ?, ?, ?, ?, ?)",
                                (sig_hash, "method", m_name, sig, ret_type, m_doc)
                            )
                            mem_id = cur.lastrowid
                            members_map[sig_hash] = mem_id
                            member_counts[mem_id] = 0
                            stats["unique_members"] += 1
                        else:
                            mem_id = members_map[sig_hash]

                        member_counts[mem_id] += 1
                        pending_symbol_members.append((sym_id, mem_id, m_name))
                        if ret_type:
                            pending_edges.append((sym_id, ret_type, "returns", mem_id))

                    # 處理 Properties
                    for p in cls_info.get("properties", []):
                        p_name = p["name"]
                        p_type = p.get("type", "")
                        p_doc = p.get("doc", "")
                        sig = f": {p_type}"
                        sig_hash = hashlib.sha256(f"{source_id}:property:{p_name}:{sig}:{p_type}".encode()).hexdigest()[:16]

                        if sig_hash not in members_map:
                            cur.execute(
                                "INSERT INTO members (sig_hash, kind, name, signature, return_type, doc) VALUES (?, ?, ?, ?, ?, ?)",
                                (sig_hash, "property", p_name, sig, p_type, p_doc)
                            )
                            mem_id = cur.lastrowid
                            members_map[sig_hash] = mem_id
                            member_counts[mem_id] = 0
                            stats["unique_members"] += 1
                        else:
                            mem_id = members_map[sig_hash]

                        member_counts[mem_id] += 1
                        pending_symbol_members.append((sym_id, mem_id, p_name))
                        if p_type:
                            pending_edges.append((sym_id, p_type, "prop_type", mem_id))

        # -------------------------------------------------------------
        # 2. 處理 SpaceClaim API
        # -------------------------------------------------------------
        sc_src = source_path if product == "spaceclaim" else Path("__missing__")
        if sc_src.exists():
            with open(sc_src, "r", encoding="utf-8") as f:
                sc_data = json.load(f)

            for fqname, cls_info in sc_data.get("classes", {}).items():
                name = cls_info.get("name", fqname.split(".")[-1])
                kind = "interface" if cls_info.get("is_interface") else "class"
                cur.execute(
                    "INSERT INTO symbols (product, kind, fqname, name, doc) VALUES (?, ?, ?, ?, ?)",
                    ("spaceclaim", kind, fqname, name, "")
                )
                sym_id = cur.lastrowid
                symbols_map[fqname] = sym_id
                name_to_symbol_ids.setdefault(name, []).append(sym_id)
                stats["symbols"] += 1

                for m in cls_info.get("methods", []):
                    m_name = m["name"]
                    params = ", ".join(f"{p['name']}: {p['type']}" for p in m.get("parameters", []))
                    sig = f"({params}) -> {m.get('return_type', '')}"
                    ret_type = m.get("return_type", "")
                    sig_hash = hashlib.sha256(f"{source_id}:method:{m_name}:{sig}:{ret_type}".encode()).hexdigest()[:16]

                    if sig_hash not in members_map:
                        cur.execute(
                            "INSERT INTO members (sig_hash, kind, name, signature, return_type, doc) VALUES (?, ?, ?, ?, ?, ?)",
                            (sig_hash, "method", m_name, sig, ret_type, "")
                        )
                        mem_id = cur.lastrowid
                        members_map[sig_hash] = mem_id
                        member_counts[mem_id] = 0
                        stats["unique_members"] += 1
                    else:
                        mem_id = members_map[sig_hash]

                    member_counts[mem_id] += 1
                    pending_symbol_members.append((sym_id, mem_id, m_name))
                    if ret_type:
                        pending_edges.append((sym_id, ret_type, "returns", mem_id))

                for p in cls_info.get("properties", []):
                    p_name = p["name"]
                    p_type = p.get("property_type", "")
                    sig = f": {p_type}"
                    sig_hash = hashlib.sha256(f"{source_id}:property:{p_name}:{sig}:{p_type}".encode()).hexdigest()[:16]

                    if sig_hash not in members_map:
                        cur.execute(
                            "INSERT INTO members (sig_hash, kind, name, signature, return_type, doc) VALUES (?, ?, ?, ?, ?, ?)",
                            (sig_hash, "property", p_name, sig, p_type, "")
                        )
                        mem_id = cur.lastrowid
                        members_map[sig_hash] = mem_id
                        member_counts[mem_id] = 0
                        stats["unique_members"] += 1
                    else:
                        mem_id = members_map[sig_hash]

                    member_counts[mem_id] += 1
                    pending_symbol_members.append((sym_id, mem_id, p_name))
                    if p_type:
                        pending_edges.append((sym_id, p_type, "prop_type", mem_id))

            # 處理 SpaceClaim Enums
            for fqname, enum_info in sc_data.get("enums", {}).items():
                name = enum_info.get("name", fqname.split(".")[-1])
                doc = "Values: " + ", ".join(enum_info.get("values", []))
                cur.execute(
                    "INSERT INTO symbols (product, kind, fqname, name, doc) VALUES (?, ?, ?, ?, ?)",
                    ("spaceclaim", "enum", fqname, name, doc)
                )
                sym_id = cur.lastrowid
                symbols_map[fqname] = sym_id
                name_to_symbol_ids.setdefault(name, []).append(sym_id)
                stats["symbols"] += 1

        # -------------------------------------------------------------
        # 3. 處理 optiSLang API
        # -------------------------------------------------------------
        osl_src = source_path if product == "optislang" else Path("__missing__")
        if osl_src.exists():
            with open(osl_src, "r", encoding="utf-8") as f:
                osl_data = json.load(f)

            for mod_name, mod_info in osl_data.get("modules", {}).items():
                for cls_name, cls_info in mod_info.get("classes", {}).items():
                    fqname = f"{mod_name}.{cls_name}"
                    doc = cls_info.get("doc", "")
                    cur.execute(
                        "INSERT INTO symbols (product, kind, fqname, name, doc) VALUES (?, ?, ?, ?, ?)",
                        ("optislang", "class", fqname, cls_name, doc)
                    )
                    sym_id = cur.lastrowid
                    symbols_map[fqname] = sym_id
                    name_to_symbol_ids.setdefault(cls_name, []).append(sym_id)
                    stats["symbols"] += 1

                    for m in cls_info.get("methods", []):
                        m_name = m["name"]
                        sig = m.get("signature", "")
                        m_doc = m.get("doc", "")
                        sig_hash = hashlib.sha256(f"{source_id}:method:{m_name}:{sig}".encode()).hexdigest()[:16]

                        if sig_hash not in members_map:
                            cur.execute(
                                "INSERT INTO members (sig_hash, kind, name, signature, return_type, doc) VALUES (?, ?, ?, ?, ?, ?)",
                                (sig_hash, "method", m_name, sig, "", m_doc)
                            )
                            mem_id = cur.lastrowid
                            members_map[sig_hash] = mem_id
                            member_counts[mem_id] = 0
                            stats["unique_members"] += 1
                        else:
                            mem_id = members_map[sig_hash]

                        member_counts[mem_id] += 1
                        pending_symbol_members.append((sym_id, mem_id, m_name))

                for fn in mod_info.get("functions", []):
                    fn_name = fn["name"]
                    fqname = f"{mod_name}.{fn_name}"
                    sig = fn.get("signature", "")
                    doc = fn.get("doc", "")
                    cur.execute(
                        "INSERT INTO symbols (product, kind, fqname, name, doc) VALUES (?, ?, ?, ?, ?)",
                        ("optislang", "module_function", fqname, fn_name, f"{sig}\n{doc}")
                    )
                    sym_id = cur.lastrowid
                    symbols_map[fqname] = sym_id
                    name_to_symbol_ids.setdefault(fn_name, []).append(sym_id)
                    stats["symbols"] += 1

        # -------------------------------------------------------------
        # 4. 處理 LS-DYNA API
        # -------------------------------------------------------------
        dyna_src = source_path if product == "lsdyna" else Path("__missing__")
        if dyna_src.exists():
            with open(dyna_src, "r", encoding="utf-8") as f:
                dyna_data = json.load(f)

            # LSPP Python
            lspp_py = dyna_data.get("components", {}).get("ls_prepost_python", {}).get("modules", {})
            for mod_name, mod_info in lspp_py.items():
                fqname = f"LsPrePost.{mod_name}"
                cur.execute(
                    "INSERT INTO symbols (product, kind, fqname, name, doc) VALUES (?, ?, ?, ?, ?)",
                    ("lsdyna", "class", fqname, mod_name, mod_info.get("description", ""))
                )
                sym_id = cur.lastrowid
                symbols_map[fqname] = sym_id
                name_to_symbol_ids.setdefault(mod_name, []).append(sym_id)
                stats["symbols"] += 1

                for fn in mod_info.get("functions", []):
                    fn_name = fn["name"]
                    sig = fn.get("signature", "")
                    doc = fn.get("description", "")
                    sig_hash = hashlib.sha256(f"{source_id}:function:{fn_name}:{sig}".encode()).hexdigest()[:16]

                    if sig_hash not in members_map:
                        cur.execute(
                            "INSERT INTO members (sig_hash, kind, name, signature, return_type, doc) VALUES (?, ?, ?, ?, ?, ?)",
                            (sig_hash, "method", fn_name, sig, "", doc)
                        )
                        mem_id = cur.lastrowid
                        members_map[sig_hash] = mem_id
                        member_counts[mem_id] = 0
                        stats["unique_members"] += 1
                    else:
                        mem_id = members_map[sig_hash]

                    member_counts[mem_id] += 1
                    pending_symbol_members.append((sym_id, mem_id, fn_name))

            # Keywords
            kw_cats = dyna_data.get("components", {}).get("ls_dyna_keywords", {}).get("categories", {})
            for cat_name, cards in kw_cats.items():
                for card in cards:
                    card_name = card["card"]
                    purpose = card.get("purpose", "")
                    fqname = f"LS-DYNA.{cat_name}.{card_name}"
                    cur.execute(
                        "INSERT INTO symbols (product, kind, fqname, name, doc) VALUES (?, ?, ?, ?, ?)",
                        ("lsdyna", "keyword", fqname, card_name, purpose)
                    )
                    sym_id = cur.lastrowid
                    symbols_map[fqname] = sym_id
                    name_to_symbol_ids.setdefault(card_name, []).append(sym_id)
                    stats["symbols"] += 1

        cur.execute(
            "UPDATE symbols SET release = ?, interface = ?, source_id = ? WHERE id > ? AND product = ?",
            (source_info["release"], source_info["interface"], source_id, before_symbol_id, product),
        )

    # -------------------------------------------------------------
    # 5. 批次寫入 symbol_members (標記 is_inherited)
    # -------------------------------------------------------------
    sm_rows = []
    for sym_id, mem_id, m_name in pending_symbol_members:
        cnt = member_counts.get(mem_id, 0)
        is_inh = 1 if (m_name in cfg.COMMON_INHERITED_NAMES or cnt > cfg.INHERITED_THRESHOLD) else 0
        sm_rows.append((sym_id, mem_id, is_inh))

    cur.executemany(
        "INSERT OR IGNORE INTO symbol_members (symbol_id, member_id, is_inherited) VALUES (?, ?, ?)",
        sm_rows
    )
    stats["symbol_members"] = len(sm_rows)

    # -------------------------------------------------------------
    # 6. 推導並批次寫入型別導航邊 (Edges)
    # -------------------------------------------------------------
    edge_rows = []
    for src_sym_id, raw_type, rel, via_mem_id in pending_edges:
        target_name = clean_type_name(raw_type)
        if target_name and target_name in name_to_symbol_ids:
            src_source_id = cur.execute(
                "SELECT source_id FROM symbols WHERE id = ?", (src_sym_id,)
            ).fetchone()[0]
            dst_sym_ids = [
                dst_id for dst_id in name_to_symbol_ids[target_name]
                if cur.execute(
                    "SELECT source_id FROM symbols WHERE id = ?", (dst_id,)
                ).fetchone()[0] == src_source_id
            ]
            for dst_id in dst_sym_ids:
                if dst_id != src_sym_id:
                    edge_rows.append((src_sym_id, dst_id, rel, via_mem_id))

    cur.executemany(
        "INSERT INTO edges (src_symbol_id, dst_symbol_id, rel, via_member_id) VALUES (?, ?, ?, ?)",
        edge_rows
    )
    stats["edges"] = len(edge_rows)

    # -------------------------------------------------------------
    # 7. 構建 FTS5 全文檢索索引 (search_fts)
    # -------------------------------------------------------------
    # A. 索引所有 Symbols
    cur.execute(
        "SELECT id, product, fqname, name, doc, release, interface, source_id FROM symbols"
    )
    sym_rows = cur.fetchall()
    fts_sym_data = []
    for s_id, prod, fq, nm, dc, release, interface, source_id in sym_rows:
        nm_split = split_camel_case(nm)
        fts_sym_data.append(
            ("symbol", s_id, prod, fq, nm, nm_split, "", dc or "", release, interface, source_id)
        )

    cur.executemany(
        "INSERT INTO search_fts "
        "(item_type, ref_id, product, fqname, name, name_split, signature, doc, release, interface, source_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        fts_sym_data
    )

    # B. 索引重要 Members (過濾掉純繼承的雜訊)
    cur.execute("""
        SELECT m.id, s.product, s.fqname || '.' || m.name, m.name, m.signature, m.doc,
               s.release, s.interface, s.source_id
        FROM members m
        JOIN symbol_members sm ON m.id = sm.member_id
        JOIN symbols s ON sm.symbol_id = s.id
        WHERE sm.is_inherited = 0
        GROUP BY m.id, s.release, s.interface, s.source_id
    """)
    mem_rows = cur.fetchall()
    fts_mem_data = []
    for m_id, prod, fq, nm, sig, dc, release, interface, source_id in mem_rows:
        nm_split = split_camel_case(nm)
        fts_mem_data.append(
            ("member", m_id, prod, fq, nm, nm_split, sig or "", dc or "", release, interface, source_id)
        )

    cur.executemany(
        "INSERT INTO search_fts "
        "(item_type, ref_id, product, fqname, name, name_split, signature, doc, release, interface, source_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        fts_mem_data
    )

    stats["fts_entries"] = len(fts_sym_data) + len(fts_mem_data)

    conn.commit()
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
    if not source_records or stats["symbols"] == 0 or stats["fts_entries"] == 0:
        conn.close()
        temp_path.unlink(missing_ok=True)
        raise RuntimeError("API KB promote blocked: no valid source snapshot or indexed symbols/FTS entries")
    if integrity != "ok" or fk_errors:
        conn.close()
        temp_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"API KB promote blocked: integrity={integrity!r}, foreign_key_errors={len(fk_errors)}"
        )
    conn.close()
    os.replace(temp_path, cfg.DB_PATH)

    return {
        "status": "success",
        "path": str(cfg.DB_PATH),
        "statistics": stats
    }

if __name__ == "__main__":
    res = build_database(force=True)
    print("建置完成:", json.dumps(res, indent=2, ensure_ascii=False))
