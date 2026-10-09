"""
ANSYS API 知識庫建置管線 (Build Pipeline)
解析四大模組 JSON，執行去重正規化、推導型別導航邊 (Edges) 並建立 SQLite FTS5 索引。
"""
import re
import json
import sqlite3
import hashlib
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

def build_database(force: bool = False) -> dict:
    """建置或重建 API 知識庫 SQLite 資料庫"""
    cfg.DB_DIR.mkdir(parents=True, exist_ok=True)

    if cfg.DB_PATH.exists() and not force:
        db_mtime = cfg.DB_PATH.stat().st_mtime
        sources_modified = False
        for src_path in cfg.SOURCES.values():
            if src_path.exists() and src_path.stat().st_mtime > db_mtime:
                sources_modified = True
                break
        if not sources_modified:
            return {"status": "up_to_date", "path": str(cfg.DB_PATH)}

    if cfg.DB_PATH.exists():
        try:
            cfg.DB_PATH.unlink()
        except Exception:
            pass

    conn = sqlite3.connect(str(cfg.DB_PATH))
    conn.execute("PRAGMA synchronous = OFF")
    conn.execute("PRAGMA journal_mode = MEMORY")

    # 執行 Schema 定義
    with open(cfg.SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    cur = conn.cursor()

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

    # -------------------------------------------------------------
    # 1. 處理 Mechanical API
    # -------------------------------------------------------------
    mech_src = cfg.SOURCES["mechanical"]
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
                    sig_hash = hashlib.sha256(f"method:{m_name}:{sig}:{ret_type}".encode()).hexdigest()[:16]

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
                    sig_hash = hashlib.sha256(f"property:{p_name}:{sig}:{p_type}".encode()).hexdigest()[:16]

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
    sc_src = cfg.SOURCES["spaceclaim"]
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
                sig_hash = hashlib.sha256(f"method:{m_name}:{sig}:{ret_type}".encode()).hexdigest()[:16]

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
                sig_hash = hashlib.sha256(f"property:{p_name}:{sig}:{p_type}".encode()).hexdigest()[:16]

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
    osl_src = cfg.SOURCES["optislang"]
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
                    sig_hash = hashlib.sha256(f"method:{m_name}:{sig}".encode()).hexdigest()[:16]

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
    dyna_src = cfg.SOURCES["lsdyna"]
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
                sig_hash = hashlib.sha256(f"function:{fn_name}:{sig}".encode()).hexdigest()[:16]

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
            dst_sym_ids = name_to_symbol_ids[target_name]
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
    cur.execute("SELECT id, product, fqname, name, doc FROM symbols")
    sym_rows = cur.fetchall()
    fts_sym_data = []
    for s_id, prod, fq, nm, dc in sym_rows:
        nm_split = split_camel_case(nm)
        fts_sym_data.append(("symbol", s_id, prod, fq, nm, nm_split, "", dc or ""))

    cur.executemany(
        "INSERT INTO search_fts (item_type, ref_id, product, fqname, name, name_split, signature, doc) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        fts_sym_data
    )

    # B. 索引重要 Members (過濾掉純繼承的雜訊)
    cur.execute("""
        SELECT m.id, s.product, s.fqname || '.' || m.name, m.name, m.signature, m.doc
        FROM members m
        JOIN symbol_members sm ON m.id = sm.member_id
        JOIN symbols s ON sm.symbol_id = s.id
        WHERE sm.is_inherited = 0
        GROUP BY m.id
    """)
    mem_rows = cur.fetchall()
    fts_mem_data = []
    for m_id, prod, fq, nm, sig, dc in mem_rows:
        nm_split = split_camel_case(nm)
        fts_mem_data.append(("member", m_id, prod, fq, nm, nm_split, sig or "", dc or ""))

    cur.executemany(
        "INSERT INTO search_fts (item_type, ref_id, product, fqname, name, name_split, signature, doc) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        fts_mem_data
    )

    stats["fts_entries"] = len(fts_sym_data) + len(fts_mem_data)

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "path": str(cfg.DB_PATH),
        "statistics": stats
    }

if __name__ == "__main__":
    res = build_database(force=True)
    print("建置完成:", json.dumps(res, indent=2, ensure_ascii=False))
