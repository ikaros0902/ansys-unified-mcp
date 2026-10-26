#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transitive Closure & Hub-Anchor Builder (Stage 3)
=================================================
負責從 ANSYS API 符號圖譜生成有界轉移閉包與樞紐錨點索引表 (api_navigation_closure)：
1. 反向/循環邊過濾 (Upward & Reflexive Edge Pruning):
   強制剔除所有反向與循環屬性（黑名單：Parent, Root, Application, DataModel, InternalObject, Owner），
   確保遍歷僅沿正向因果樹展開。
2. 樞紐錨點自動標記 (Hub-Anchor Identification):
   各領域核心容器（如 Mechanical: Model, Analysis, Solution, Mesh...；每域 <= 30 個核心節點）
   標記 is_hub_anchor = 1；頂層根入口節點標記 is_root_entry = 1（如 ExtAPI, DataModel, solver, Desktop）。
3. BFS 有界展開與多路徑語義保留:
   一般節點 d <= 4，頂層根入口放寬至 d <= 6。
   區分語義標籤: FACTORY_CREATE, READ_TRAVERSAL, CROSS_BRIDGE。
   每條路徑計算 64-bit path_hash，支援 PRIMARY KEY (from_uid, to_uid, path_semantics, path_hash)。
"""

import argparse
from collections import defaultdict, deque
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

# 專案路徑設定
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

DEFAULT_DB_PATH = REPO_ROOT / "Documentation_clean" / "api_kb.sqlite"

# 反向與循環邊黑名單 (不分大小寫)
PRUNED_EDGE_MEMBERS = {
    "parent",
    "root",
    "application",
    "datamodel",
    "internalobject",
    "owner",
}

# 領域核心根入口與知名樞紐候選定義
DOMAIN_ROOT_ENTRIES = {
    "mechanical": {"ExtAPI", "DataModel", "Model", "Tree", "Project", "Graphics"},
    "fluent": {"solver", "session", "root", "tui", "meshing"},
    "spaceclaim": {"Window", "Document", "Interaction", "Application", "SpaceClaim", "DocumentHelper", "WindowHelper", "ApplicationHelper", "DocObjectHelper"},
    "optislang": {"Application", "Optislang", "Desktop", "Project"},
    "lsdyna": {"Model", "LsPrePost", "DataCenter", "Keyword"},
    "workbench": {"Desktop", "GetProject", "Ansys"},
}

DOMAIN_HUB_ANCHORS = {
    "mechanical": [
        "Model", "Analysis", "Solution", "AnalysisSettings", "ANSYSAnalysisSettings",
        "Mesh", "Connections", "Geometry", "Materials", "CoordinateSystems",
        "NamedSelections", "MeshWorkflowControl", "SolutionInformation", "ContactRegion",
        "Body", "Part", "Environment", "Commands", "BoundaryConditions", "PreStress",
        "MeshControl", "Figures", "Tables", "EngineeringData", "InitialConditions",
    ],
    "fluent": [
        "setup", "models", "boundary_conditions", "materials", "solution",
        "initialization", "cell_zone_conditions", "monitors", "mesh", "named_expressions",
        "run_calculation", "file", "tui", "report", "graphics"
    ],
    "spaceclaim": [
        "Part", "Component", "Body", "Design", "Face", "Edge", "Selection",
        "Layers", "DatumPlane", "Beam", "BeamProfile", "Block", "Mesh", "Move",
        "MeasureHelper", "ComponentHelper", "ViewHelper", "Dimension", "Draft",
        "Extrude", "Blend", "Surface", "Assembly"
    ],
    "optislang": [
        "Project", "RootSystem", "Actor", "Node", "Parameter", "Criterion",
        "Response", "Design", "Sensitivity", "MOP", "Algorithm", "Variable",
        "Optimization", "Sampling", "Postprocessing"
    ],
    "lsdyna": [
        "CONTROL", "DATABASE", "MAT", "PART", "SECTION", "BOUNDARY", "CONTACT",
        "INITIAL", "LOAD", "NODE", "ELEMENT", "SET", "CONSTRAINED", "DEFINE", "HOURGLASS"
    ],
}

# 工廠方法命名正規表示式 (以 Add, Create, Insert 開頭)
FACTORY_METHOD_REGEX = re.compile(r"^(add|create|insert)[A-Z0-9_]|^(add_|create_|insert_)", re.IGNORECASE)

# 跨場/跨產品介面關鍵字
CROSS_BRIDGE_KEYWORDS = re.compile(r"(bridge|cross|transfer|export_to|import_from|interop|coupling|mapping)", re.IGNORECASE)


def ensure_schema(conn: sqlite3.Connection) -> None:
    """確保 symbols 與 api_navigation_closure 包含必要欄位與表結構"""
    cur = conn.cursor()

    # 檢查 symbols 欄位
    cur.execute("PRAGMA table_info(symbols)")
    existing_cols = {row[1] for row in cur.fetchall()}

    if "is_hub_anchor" not in existing_cols:
        cur.execute("ALTER TABLE symbols ADD COLUMN is_hub_anchor INTEGER DEFAULT 0")
    if "is_root_entry" not in existing_cols:
        cur.execute("ALTER TABLE symbols ADD COLUMN is_root_entry INTEGER DEFAULT 0")

    # 建立 symbols 索引
    cur.execute("CREATE INDEX IF NOT EXISTS idx_symbols_hub ON symbols(product, is_hub_anchor)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_symbols_root ON symbols(product, is_root_entry)")

    # 建立 api_navigation_closure 表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS api_navigation_closure (
            from_uid INTEGER NOT NULL,
            to_uid INTEGER NOT NULL,
            path_semantics TEXT NOT NULL,
            path_hash TEXT NOT NULL,
            product TEXT NOT NULL,
            depth INTEGER NOT NULL,
            path_nodes TEXT NOT NULL,
            path_steps TEXT NOT NULL,
            path_display TEXT,
            from_name TEXT,
            to_name TEXT,
            is_from_root INTEGER DEFAULT 0,
            is_from_hub INTEGER DEFAULT 0,
            is_to_hub INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (from_uid, to_uid, path_semantics, path_hash)
        )
    """)

    # 建立 closure 索引
    cur.execute("CREATE INDEX IF NOT EXISTS idx_closure_from ON api_navigation_closure(from_uid)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_closure_to ON api_navigation_closure(to_uid)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_closure_product ON api_navigation_closure(product)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_closure_semantics ON api_navigation_closure(path_semantics)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_closure_lookup ON api_navigation_closure(from_name, to_name)")

    conn.commit()


def identify_and_mark_hubs_and_roots(conn: sqlite3.Connection, target_domain: Optional[str] = None) -> Dict[str, Dict[str, int]]:
    """
    識別並自動標記各領域的 Hub Anchors 與 Root Entries。
    - 每領域核心容器 <= 30 個，標記 is_hub_anchor = 1
    - 頂層根入口標記 is_root_entry = 1
    """
    cur = conn.cursor()

    # 取得現有 products
    if target_domain:
        products = [target_domain]
    else:
        cur.execute("SELECT DISTINCT product FROM symbols")
        products = [row[0] for row in cur.fetchall()]

    stats = {}

    for prod in products:
        prod_lower = prod.lower()

        # 1. 取得該領域所有符號
        cur.execute("""
            SELECT id, name, fqname, kind
            FROM symbols
            WHERE product = ?
        """, (prod,))
        symbols = cur.fetchall()
        if not symbols:
            continue

        sym_map = {row[0]: {"name": row[1], "fqname": row[2], "kind": row[3]} for row in symbols}

        # 2. 計算正向出度 (排除反向邊與自環)
        cur.execute("""
            SELECT e.src_symbol_id, count(e.id) as out_deg
            FROM edges e
            JOIN symbols s1 ON e.src_symbol_id = s1.id
            LEFT JOIN members m ON e.via_member_id = m.id
            WHERE s1.product = ?
              AND e.src_symbol_id != e.dst_symbol_id
              AND (m.name IS NULL OR LOWER(m.name) NOT IN ('parent', 'root', 'application', 'datamodel', 'internalobject', 'owner'))
            GROUP BY e.src_symbol_id
        """, (prod,))
        out_degrees = {row[0]: row[1] for row in cur.fetchall()}

        # 3. 識別 Root Entries
        root_keywords = DOMAIN_ROOT_ENTRIES.get(prod_lower, {"ExtAPI", "DataModel", "solver", "Desktop"})
        marked_roots: Set[int] = set()

        for sid, sdata in sym_map.items():
            name = sdata["name"]
            fqname = sdata["fqname"]
            if sdata["kind"] == "enum":
                continue
            # 判斷是否符合根節點名稱：短名稱完全匹配，或完整限定名稱以此類別結尾 (避免命名空間 DataModel 誤命中)
            is_root = False
            for rk in root_keywords:
                if name.lower() == rk.lower() or fqname.lower().endswith(f".{rk.lower()}"):
                    is_root = True
                    break
            if is_root:
                marked_roots.add(sid)

        # 4. 識別 Hub Anchors (每域 <= 30 個)
        hub_keywords = DOMAIN_HUB_ANCHORS.get(prod_lower, ["Model", "Analysis", "Solution", "Mesh", "setup", "models"])
        candidate_hubs = []

        # 優先加入已知核心容器
        for sid, sdata in sym_map.items():
            name = sdata["name"]
            fqname = sdata["fqname"]
            kind = sdata["kind"]
            if kind == "enum":
                continue

            deg = out_degrees.get(sid, 0)
            is_priority = False
            for hk in hub_keywords:
                if hk.lower() == name.lower() or name.lower().endswith(hk.lower()):
                    is_priority = True
                    break

            if is_priority:
                # 權重加成: 優先核心關鍵字加上正向度數
                candidate_hubs.append((sid, 10000 + deg, name))
            elif deg > 5:
                # 高出度節點補位
                candidate_hubs.append((sid, deg, name))

        # 降序排序並嚴格限制每領域 <= 30 個核心節點
        candidate_hubs.sort(key=lambda x: x[1], reverse=True)
        top_hubs = candidate_hubs[:30]
        marked_hubs: Set[int] = {item[0] for item in top_hubs}

        # 5. 更新 symbols 表 (先將該產品歸零後精確更新)
        cur.execute("UPDATE symbols SET is_hub_anchor = 0, is_root_entry = 0 WHERE product = ?", (prod,))

        if marked_roots:
            cur.executemany(
                "UPDATE symbols SET is_root_entry = 1 WHERE id = ?",
                [(sid,) for sid in marked_roots]
            )

        if marked_hubs:
            cur.executemany(
                "UPDATE symbols SET is_hub_anchor = 1 WHERE id = ?",
                [(sid,) for sid in marked_hubs]
            )

        conn.commit()
        stats[prod] = {
            "total_symbols": len(symbols),
            "root_entries_count": len(marked_roots),
            "hub_anchors_count": len(marked_hubs),
        }

    return stats


def compute_64bit_path_hash(path_nodes: List[int], steps: List[Dict[str, Any]]) -> str:
    """計算 64-bit 路徑雜湊 (16-char hex 字串)"""
    parts = [str(path_nodes[0])]
    for s in steps:
        parts.append(f"->({s.get('via','')}:{s.get('rel','')})->{s.get('to_id')}")
    raw = "".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def classify_path_semantics(steps: List[Dict[str, Any]], from_prod: str, to_prod: str) -> str:
    """
    判定路徑語義:
    - 'CROSS_BRIDGE': 跨領域或介面傳遞
    - 'FACTORY_CREATE': 包含 Add*, Create*, Insert* 工廠創建方法
    - 'READ_TRAVERSAL': 純屬性或導航遍歷
    """
    # 1. 跨場/跨產品檢驗
    if from_prod.lower() != to_prod.lower():
        return "CROSS_BRIDGE"

    has_cross_bridge = False
    has_factory = False

    for s in steps:
        via = s.get("via", "")
        rel = s.get("rel", "")

        if CROSS_BRIDGE_KEYWORDS.search(via) or CROSS_BRIDGE_KEYWORDS.search(rel):
            has_cross_bridge = True
            break

        if FACTORY_METHOD_REGEX.search(via):
            has_factory = True

    if has_cross_bridge:
        return "CROSS_BRIDGE"
    if has_factory:
        return "FACTORY_CREATE"
    return "READ_TRAVERSAL"


def build_closure_for_domain(
    conn: sqlite3.Connection,
    product: str,
    max_depth_normal: int = 4,
    max_depth_root: int = 6,
    max_paths_per_pair: int = 3,
    sample_nodes: Optional[List[int]] = None,
) -> int:
    """
    為指定領域建構有界轉移閉包，並寫入 api_navigation_closure。
    支援一般節點 d <= 4，根節點 d <= 6。
    """
    cur = conn.cursor()

    # 1. 讀取符號資訊
    cur.execute("""
        SELECT id, name, fqname, product, is_hub_anchor, is_root_entry
        FROM symbols
        WHERE product = ?
    """, (product,))
    symbol_rows = cur.fetchall()
    if not symbol_rows:
        return 0

    sym_dict = {}
    for r in symbol_rows:
        sym_dict[r[0]] = {
            "id": r[0],
            "name": r[1],
            "fqname": r[2],
            "product": r[3],
            "is_hub": bool(r[4]),
            "is_root": bool(r[5]),
        }

    # 2. 構建鄰接表，執行反向邊與循環屬性過濾 (Upward & Reflexive Edge Pruning)
    cur.execute("""
        SELECT e.src_symbol_id, e.dst_symbol_id, m.name, e.rel, s2.product
        FROM edges e
        JOIN symbols s1 ON e.src_symbol_id = s1.id
        JOIN symbols s2 ON e.dst_symbol_id = s2.id
        LEFT JOIN members m ON e.via_member_id = m.id
        WHERE s1.product = ?
    """, (product,))

    adj = defaultdict(list)
    pruned_count = 0

    for src_id, dst_id, m_name, rel, dst_prod in cur.fetchall():
        # 自環過濾
        if src_id == dst_id:
            pruned_count += 1
            continue

        # 反向與循環黑名單過濾
        via_clean = (m_name or "").strip()
        if via_clean.lower() in PRUNED_EDGE_MEMBERS:
            pruned_count += 1
            continue

        adj[src_id].append({
            "dst_id": dst_id,
            "via": via_clean,
            "rel": rel,
            "dst_prod": dst_prod,
        })

    # 3. 確定起點節點
    if sample_nodes is not None:
        start_node_ids = [nid for nid in sample_nodes if nid in sym_dict]
    else:
        start_node_ids = list(sym_dict.keys())

    records_to_insert = []
    total_inserted = 0
    batch_size = 5000

    # 4. BFS 有界展開
    for start_id in start_node_ids:
        start_info = sym_dict[start_id]
        is_root = start_info["is_root"]
        is_from_hub = start_info["is_hub"]
        max_d = max_depth_root if is_root else max_depth_normal

        # 隊列項目: (current_id, path_nodes_list, steps_list)
        queue = deque([(start_id, [start_id], [])])
        # 追蹤特定 (dst_id, semantics) 收集的路徑條數
        collected_semantics_counts = defaultdict(int)
        # 追蹤中繼節點 enqueue 次數，防止深度爆炸 (Frontier Throttling)
        enqueue_counts = defaultdict(int)

        while queue:
            curr_id, path_nodes, steps = queue.popleft()
            curr_depth = len(steps)

            if curr_depth >= max_d:
                continue

            for edge in adj[curr_id]:
                nxt_id = edge["dst_id"]

                # 避免路徑內部出現循環
                if nxt_id in path_nodes:
                    continue

                nxt_info = sym_dict.get(nxt_id)
                if not nxt_info:
                    continue

                via_name = edge["via"] or "get()"
                new_step = {
                    "from_id": curr_id,
                    "to_id": nxt_id,
                    "via": via_name,
                    "rel": edge["rel"],
                    "from_name": sym_dict[curr_id]["name"],
                    "to_name": nxt_info["name"],
                }

                nxt_path_nodes = path_nodes + [nxt_id]
                nxt_steps = steps + [new_step]
                nxt_depth = len(nxt_steps)

                # 計算路徑語義
                semantics = classify_path_semantics(nxt_steps, start_info["product"], nxt_info["product"])

                # 限制每個 (from, to, semantics) 最多保留 max_paths_per_pair 條
                pair_sem_key = (nxt_id, semantics)
                if collected_semantics_counts[pair_sem_key] < max_paths_per_pair:
                    collected_semantics_counts[pair_sem_key] += 1

                    # 計算 64-bit 雜湊
                    path_hash = compute_64bit_path_hash(nxt_path_nodes, nxt_steps)

                    # 格式化可讀導航路徑
                    path_display = f"{start_info['name']}"
                    for s in nxt_steps:
                        path_display += f".{s['via']} -> {s['to_name']}"

                    records_to_insert.append((
                        start_id,
                        nxt_id,
                        semantics,
                        path_hash,
                        start_info["product"],
                        nxt_depth,
                        json.dumps(nxt_path_nodes),
                        json.dumps(nxt_steps, ensure_ascii=False),
                        path_display,
                        start_info["name"],
                        nxt_info["name"],
                        1 if is_root else 0,
                        1 if is_from_hub else 0,
                        1 if nxt_info["is_hub"] else 0,
                    ))

                # 若深度尚未達到上限，且該中繼節點 enqueue 次數未達上限，繼續推進 BFS (Frontier Throttling)
                if nxt_depth < max_d and enqueue_counts[nxt_id] < max_paths_per_pair:
                    enqueue_counts[nxt_id] += 1
                    queue.append((nxt_id, nxt_path_nodes, nxt_steps))

            # 批次寫入
            if len(records_to_insert) >= batch_size:
                cur.executemany("""
                    INSERT OR REPLACE INTO api_navigation_closure (
                        from_uid, to_uid, path_semantics, path_hash,
                        product, depth, path_nodes, path_steps, path_display,
                        from_name, to_name, is_from_root, is_from_hub, is_to_hub
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, records_to_insert)
                conn.commit()
                total_inserted += len(records_to_insert)
                records_to_insert.clear()

    # 寫入剩餘記錄
    if records_to_insert:
        cur.executemany("""
            INSERT OR REPLACE INTO api_navigation_closure (
                from_uid, to_uid, path_semantics, path_hash,
                product, depth, path_nodes, path_steps, path_display,
                from_name, to_name, is_from_root, is_from_hub, is_to_hub
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records_to_insert)
        conn.commit()
        total_inserted += len(records_to_insert)
        records_to_insert.clear()

    return total_inserted


def build_closure(
    db_path: Path,
    domain: Optional[str] = None,
    all_subgraphs: bool = False,
    sample_build: bool = False,
    sample_size: int = 50,
) -> Dict[str, Any]:
    """轉移閉包與樞紐錨點建構總流程"""
    start_time = time.time()
    db_path = Path(db_path).resolve()
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at: {db_path}")

    conn = sqlite3.connect(str(db_path))
    ensure_schema(conn)

    # 1. 識別並自動標記各領域 Hub-Anchors 與 Root-Entries
    marking_stats = identify_and_mark_hubs_and_roots(conn, target_domain=domain if not all_subgraphs else None)

    # 2. 確定要建構閉包的 domains
    cur = conn.cursor()
    if domain and not all_subgraphs:
        domains_to_process = [domain.lower()]
    else:
        cur.execute("SELECT DISTINCT product FROM symbols")
        domains_to_process = [r[0].lower() for r in cur.fetchall()]

    closure_stats = {}
    total_paths_built = 0

    for prod in domains_to_process:
        sample_nodes = None
        if sample_build:
            # 抽樣模式：取得所有 Root、所有 Hub 以及部分節點
            cur.execute("""
                SELECT id FROM symbols
                WHERE product = ? AND (is_hub_anchor = 1 OR is_root_entry = 1)
            """, (prod,))
            core_nodes = [r[0] for r in cur.fetchall()]

            # 補充隨機或普通節點直到 sample_size
            remaining_slots = max(0, sample_size - len(core_nodes))
            cur.execute("""
                SELECT id FROM symbols
                WHERE product = ? AND is_hub_anchor = 0 AND is_root_entry = 0
                LIMIT ?
            """, (prod, remaining_slots))
            extra_nodes = [r[0] for r in cur.fetchall()]

            sample_nodes = list(set(core_nodes + extra_nodes))

        paths_count = build_closure_for_domain(
            conn=conn,
            product=prod,
            sample_nodes=sample_nodes,
        )
        closure_stats[prod] = paths_count
        total_paths_built += paths_count

    conn.close()
    elapsed = time.time() - start_time

    return {
        "status": "success",
        "elapsed_seconds": round(elapsed, 2),
        "marking_stats": marking_stats,
        "closure_stats": closure_stats,
        "total_paths_built": total_paths_built,
    }


def main():
    parser = argparse.ArgumentParser(description="ANSYS API Transitive Closure & Hub-Anchor Builder (Stage 3)")
    parser.add_argument("--db-path", type=str, default=str(DEFAULT_DB_PATH), help="Path to api_kb.sqlite database")
    parser.add_argument("--domain", type=str, default=None, help="Target domain (e.g. mechanical, fluent, spaceclaim, optislang, lsdyna)")
    parser.add_argument("--all-subgraphs", action="store_true", help="Build closure for all product subgraphs in the database")
    parser.add_argument("--sample-build", action="store_true", help="Run fast sample build covering Hubs, Roots, and top sample nodes")
    parser.add_argument("--sample-size", type=int, default=50, help="Number of sample starting nodes per domain for sample-build")

    args = parser.parse_args()

    print("=" * 70)
    print("ANSYS API 轉移閉包與樞紐錨點建構工具 (Stage 3)")
    print("=" * 70)
    print(f"資料庫路徑: {args.db_path}")
    print(f"指定領域: {args.domain or 'ALL'}")
    print(f"全子圖建構: {args.all_subgraphs}")
    print(f"抽樣建構模式: {args.sample_build}")
    print("-" * 70)

    res = build_closure(
        db_path=Path(args.db_path),
        domain=args.domain,
        all_subgraphs=args.all_subgraphs,
        sample_build=args.sample_build,
        sample_size=args.sample_size,
    )

    print("\n[SUCCESS] 建構完成！執行摘要:")
    print(f"- 耗時: {res['elapsed_seconds']} 秒")
    print("- 領域核心標記統計 (Hub <= 30 / 領域):")
    for prod, stat in res["marking_stats"].items():
        print(f"  * {prod}: 符號數={stat['total_symbols']}, 根入口={stat['root_entries_count']}, 樞紐錨點={stat['hub_anchors_count']}")
    print("- 轉移閉包路徑產出統計:")
    for prod, cnt in res["closure_stats"].items():
        print(f"  * {prod}: {cnt} 條路徑")
    print(f"- 總寫入路徑數: {res['total_paths_built']}")
    print("=" * 70)


if __name__ == "__main__":
    main()
