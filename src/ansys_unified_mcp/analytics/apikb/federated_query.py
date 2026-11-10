"""
ANSYS 聯邦知識圖譜查詢引擎 (Federated Query Engine & Subgraph Router)
負責跨 10 個領域子圖與跨場橋接資料庫執行超低延遲檢索。

核心功能：
1. O(1) 零查找子圖路由 (Zero-Lookup Subgraph Router):
   依據 symbol_uid 位元右移 `domain_id = (symbol_uid >> 56) & 0x7F` 零延遲定址子圖 SQLite 檔案。
2. 兩階段 8 跳路徑查詢演算法 (Two-Stage 8-Hop Navigation Engine):
   - Stage A (1~4 跳或根入口 1~6 跳): 直接查詢轉移閉包表 (api_navigation_closure)，耗時 < 0.5 ms。
   - Stage B (5~8 跳任意深層路徑): 透過 is_to_hub=1 核心樞紐錨點執行二階自連接 (Meet-in-the-Middle Join)，耗時 < 1.2 ms。
   - 支援多路徑保留與語義篩選 (FACTORY_CREATE / READ_TRAVERSAL / CROSS_BRIDGE)。
3. 符號與文件聯合檢索 (search_symbols_federated):
   支援依領域過濾、完全/前綴檢索，輸出三級漸進式卡片 (L0 ~50 tokens, L1 ~250 tokens)。
4. 跨場橋接查詢 (query_cross_domain_bridge):
   查詢 multiphysics_bridge.sqlite 中的流固耦合 (FSI)、共軛熱傳 (CHT)、MBD-DEM、STOP 介面變數配對。
"""
from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ansys_unified_mcp.analytics.apikb.federated_schemas import (
    DomainID,
    DOMAIN_NAMES,
    DOMAIN_SUBGRAPH_FILES,
    DOMAIN_BIT_SHIFT,
    DOMAIN_ID_MASK,
    MASK_56_BITS,
    extract_domain_id,
    extract_local_hash,
    generate_symbol_uid,
    create_symbol_uid,
    get_subgraph_filename,
    parse_domain_id,
    get_domain_name,
    create_canonical_uri,
    parse_canonical_uri,
    compute_uri_hash56,
    init_subgraph_database,
    init_bridge_database,
    SUBGRAPH_SCHEMA_DDL,
    BRIDGE_SCHEMA_DDL,
)

logger = logging.getLogger("ansys_unified_mcp.analytics.apikb.federated")

# 專案路徑設定
REPO_ROOT = Path(__file__).resolve().parents[4]
DOCS_CLEAN_DIR = REPO_ROOT / "docs" / "Documentation_clean"
DEFAULT_SUBGRAPHS_DIR = DOCS_CLEAN_DIR / "subgraphs"
BRIDGE_DB_FILENAME = DOMAIN_SUBGRAPH_FILES[DomainID.BRIDGE]  # multiphysics_bridge.sqlite


# ============================================================================
# 1. O(1) 零查找子圖路由演算法 (Zero-Lookup Subgraph Router)
# ============================================================================

def route_symbol_subgraph(symbol_uid: int, subgraphs_dir: Optional[Path] = None) -> Path:
    """O(1) 零查找子圖路由：直接根據 symbol_uid 回傳對應 SQLite 資料庫檔案路徑。

    計算複雜度嚴格為 O(1)：
    domain_id = (symbol_uid >> 56) & 0x7F
    """
    domain_id = extract_domain_id(symbol_uid)
    filename = get_subgraph_filename(domain_id)
    base_dir = Path(subgraphs_dir) if subgraphs_dir else DEFAULT_SUBGRAPHS_DIR
    return base_dir / filename


# ============================================================================
# 資料庫連線管理 (Connection Pool & High-Performance PRAGMA)
# ============================================================================

class SubgraphConnectionPool:
    """SQLite 高性能連線池，專為 < 0.5 ms 查詢設計。"""

    def __init__(self, subgraphs_dir: Optional[Path] = None):
        self.subgraphs_dir = Path(subgraphs_dir) if subgraphs_dir else DEFAULT_SUBGRAPHS_DIR
        self._connections: Dict[str, sqlite3.Connection] = {}

    def get_connection(self, db_path: Path) -> sqlite3.Connection:
        path_str = str(db_path.resolve())
        conn = self._connections.get(path_str)
        if conn is not None:
            return conn

        # 若檔案尚未建立，確保父目錄存在
        db_path.parent.mkdir(parents=True, exist_ok=True)
        # 開啟連線並配置高效 PRAGMA
        conn = sqlite3.connect(path_str, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.execute("PRAGMA cache_size = -64000;")  # 64MB 快取
            conn.execute("PRAGMA temp_store = MEMORY;")
        except sqlite3.OperationalError:
            pass

        self._connections[path_str] = conn
        return conn

    def get_domain_connection(self, domain_id: Union[int, DomainID]) -> sqlite3.Connection:
        filename = get_subgraph_filename(domain_id)
        db_path = self.subgraphs_dir / filename
        return self.get_connection(db_path)

    def get_bridge_connection(self) -> sqlite3.Connection:
        # 優先於 subgraphs_dir 尋找，其次於父目錄尋找
        primary = self.subgraphs_dir / BRIDGE_DB_FILENAME
        if primary.exists():
            return self.get_connection(primary)
        secondary = self.subgraphs_dir.parent / BRIDGE_DB_FILENAME
        if secondary.exists():
            return self.get_connection(secondary)
        return self.get_connection(primary)

    def close_all(self):
        for conn in self._connections.values():
            try:
                conn.close()
            except Exception:
                pass
        self._connections.clear()


# 全域單例連線池
_GLOBAL_POOL: Optional[SubgraphConnectionPool] = None


def get_global_pool(subgraphs_dir: Optional[Path] = None) -> SubgraphConnectionPool:
    global _GLOBAL_POOL
    if _GLOBAL_POOL is None or (subgraphs_dir and _GLOBAL_POOL.subgraphs_dir != Path(subgraphs_dir)):
        _GLOBAL_POOL = SubgraphConnectionPool(subgraphs_dir)
    return _GLOBAL_POOL


# ============================================================================
# 2. 兩階段 8 跳路徑查詢演算法 (Two-Stage 8-Hop Navigation Engine)
# ============================================================================

@dataclass
class PathResult:
    from_uid: int
    to_uid: int
    hop_count: int
    path_semantics: str
    path_hash: int
    edge_chain: List[Dict[str, Any]]
    stage: str  # 'STAGE_A_DIRECT' | 'STAGE_B_HUB_JOIN' | 'CROSS_DOMAIN_BRIDGE'
    query_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_uid": self.from_uid,
            "to_uid": self.to_uid,
            "hop_count": self.hop_count,
            "path_semantics": self.path_semantics,
            "path_hash": self.path_hash,
            "edge_chain": self.edge_chain,
            "stage": self.stage,
            "query_time_ms": round(self.query_time_ms, 3),
        }


def query_api_path(
    from_uid: int,
    to_uid: int,
    path_semantics: Optional[str] = None,
    max_hops: int = 8,
    limit: int = 10,
    subgraphs_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """兩階段 8 跳 API 物件導航調用鏈查詢。

    演算法核心架構：
    1. 判定領域歸屬：
       - from_domain == to_domain: 單一子圖內導航。
       - from_domain != to_domain: 跨場橋接導航。
    2. Stage A (直達閉包查詢，hop_count <= 4 或根入口 <= 6):
       - 直接查詢 `api_navigation_closure`，索引 idx_closure_lookup 命中，目標 SLA < 0.5 ms。
    3. Stage B (樞紐自連接 Meet-in-the-Middle Join，hop_count 5 ~ 8):
       - 當 Stage A 無結果或 max_hops > 4 時，透過 `c1.is_to_hub = 1 AND c1.to_uid = c2.from_uid`
         執行雙階拼接 $u \\xrightarrow{\\le 4} h \\xrightarrow{\\le 4} v$，目標 SLA < 1.2 ms。
    4. 保留多路徑與工廠/唯讀語義 (FACTORY_CREATE / READ_TRAVERSAL)。
    """
    t_start = time.perf_counter()
    pool = get_global_pool(subgraphs_dir)

    from_domain = extract_domain_id(from_uid)
    to_domain = extract_domain_id(to_uid)

    # 跨子圖情況：呼叫跨領域橋接尋路
    if from_domain != to_domain:
        results = _query_cross_domain_path(
            from_uid=from_uid,
            to_uid=to_uid,
            from_domain=from_domain,
            to_domain=to_domain,
            path_semantics=path_semantics,
            max_hops=max_hops,
            limit=limit,
            pool=pool,
            t_start=t_start,
        )
        return [r.to_dict() for r in results]

    # 同一子圖：執行 Stage A 與 Stage B
    subgraph_file = pool.subgraphs_dir / get_subgraph_filename(from_domain)
    if not subgraph_file.exists():
        logger.debug("子圖檔案尚未建立: %s", subgraph_file)
        return []

    conn = pool.get_domain_connection(from_domain)
    cur = conn.cursor()

    results: List[PathResult] = []
    seen_hashes = set()

    # ------------------------------------------------------------------------
    # Stage A: 直達轉移閉包表 (1~4 跳，根節點 1~6 跳)
    # ------------------------------------------------------------------------
    sql_a = """
        SELECT from_uid, to_uid, path_semantics, path_hash, hop_count, is_to_hub, edge_chain_json
        FROM api_navigation_closure
        WHERE from_uid = ? AND to_uid = ?
          AND (? IS NULL OR path_semantics = ?)
          AND hop_count <= ?
        ORDER BY hop_count ASC
        LIMIT ?
    """
    cur.execute(sql_a, (from_uid, to_uid, path_semantics, path_semantics, min(max_hops, 6), limit))
    rows_a = cur.fetchall()

    for r in rows_a:
        p_hash = r["path_hash"]
        if p_hash in seen_hashes:
            continue
        seen_hashes.add(p_hash)
        try:
            chain = json.loads(r["edge_chain_json"]) if r["edge_chain_json"] else []
        except Exception:
            chain = []

        results.append(PathResult(
            from_uid=r["from_uid"],
            to_uid=r["to_uid"],
            hop_count=r["hop_count"],
            path_semantics=r["path_semantics"],
            path_hash=p_hash,
            edge_chain=chain,
            stage="STAGE_A_DIRECT",
            query_time_ms=(time.perf_counter() - t_start) * 1000.0,
        ))

    # 若 Stage A 已滿足數量限制且已找到路徑，直接返回 (極速迴路 < 0.5 ms)
    if results and (len(results) >= limit or max_hops <= 4):
        return [r.to_dict() for r in results]

    # ------------------------------------------------------------------------
    # Stage B: Meet-in-the-Middle 樞紐自連接二階拼接 (5~8 跳)
    # ------------------------------------------------------------------------
    if max_hops > 4 and len(results) < limit:
        # 藉由 c1.is_to_hub = 1 樞紐錨點將 u -> h (<=4 跳) 與 h -> v (<=4 跳) 拼接為 5~8 跳
        sql_b = """
            SELECT
                c1.from_uid,
                c2.to_uid,
                c1.to_uid AS hub_uid,
                c1.hop_count + c2.hop_count AS total_hops,
                c1.path_semantics AS s1,
                c2.path_semantics AS s2,
                c1.edge_chain_json AS chain1_json,
                c2.edge_chain_json AS chain2_json,
                c1.path_hash AS h1,
                c2.path_hash AS h2
            FROM api_navigation_closure c1
            JOIN api_navigation_closure c2
              ON c1.to_uid = c2.from_uid
            WHERE c1.from_uid = ?
              AND c2.to_uid = ?
              AND c1.is_to_hub = 1
              AND (? IS NULL OR (c1.path_semantics = ? AND c2.path_semantics = ?))
              AND (c1.hop_count + c2.hop_count) BETWEEN 5 AND ?
            ORDER BY total_hops ASC
            LIMIT ?
        """
        cur.execute(sql_b, (
            from_uid,
            to_uid,
            path_semantics,
            path_semantics,
            path_semantics,
            max_hops,
            limit - len(results)
        ))
        rows_b = cur.fetchall()

        for r in rows_b:
            composite_hash = (r["h1"] ^ (r["h2"] << 1)) & 0x7FFFFFFFFFFFFFFF
            if composite_hash in seen_hashes:
                continue
            seen_hashes.add(composite_hash)

            try:
                chain1 = json.loads(r["chain1_json"]) if r["chain1_json"] else []
                chain2 = json.loads(r["chain2_json"]) if r["chain2_json"] else []
                merged_chain = chain1 + chain2
            except Exception:
                merged_chain = []

            # 確定合併語義
            sem1, sem2 = r["s1"], r["s2"]
            if sem1 == sem2:
                merged_semantics = sem1
            elif "FACTORY_CREATE" in (sem1, sem2):
                merged_semantics = "FACTORY_CREATE"
            else:
                merged_semantics = "READ_TRAVERSAL"

            results.append(PathResult(
                from_uid=r["from_uid"],
                to_uid=r["to_uid"],
                hop_count=r["total_hops"],
                path_semantics=merged_semantics,
                path_hash=composite_hash,
                edge_chain=merged_chain,
                stage="STAGE_B_HUB_JOIN",
                query_time_ms=(time.perf_counter() - t_start) * 1000.0,
            ))

            if len(results) >= limit:
                break

    return [r.to_dict() for r in results]


def _query_cross_domain_path(
    from_uid: int,
    to_uid: int,
    from_domain: int,
    to_domain: int,
    path_semantics: Optional[str],
    max_hops: int,
    limit: int,
    pool: SubgraphConnectionPool,
    t_start: float,
) -> List[PathResult]:
    """跨子圖導航：透過 multiphysics_bridge.sqlite 執行跨場橋接拼接檢索。"""
    bridge_conn = pool.get_bridge_connection()
    cur = bridge_conn.cursor()

    # 檢驗是否存在 cross_domain_interfaces 或 multiphysics_bridges 表
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

    bridges: List[Dict[str, Any]] = []

    if "cross_domain_interfaces" in tables:
        sql = """
            SELECT interface_id, source_domain_id, source_uid, target_domain_id, target_uid,
                   coupling_type, mapping_contract_json
            FROM cross_domain_interfaces
            WHERE source_domain_id = ? AND target_domain_id = ?
            LIMIT 50
        """
        try:
            for r in cur.execute(sql, (from_domain, to_domain)).fetchall():
                try:
                    contract = json.loads(r["mapping_contract_json"]) if r["mapping_contract_json"] else {}
                except Exception:
                    contract = {}
                bridges.append({
                    "source_uid": r["source_uid"],
                    "target_uid": r["target_uid"],
                    "coupling_type": r["coupling_type"],
                    "source_variable": contract.get("source_variable", "InterfaceVar"),
                    "target_variable": contract.get("target_variable", "InterfaceVar"),
                    "transformation": contract.get("transformation", "DirectMapping"),
                })
        except sqlite3.OperationalError:
            pass

    if "multiphysics_bridges" in tables:
        sql = """
            SELECT source_symbol_uid, target_symbol_uid, coupling_type,
                   source_variable, target_variable, transformation
            FROM multiphysics_bridges
            WHERE source_domain_id = ? AND target_domain_id = ?
            LIMIT 50
        """
        try:
            for r in cur.execute(sql, (from_domain, to_domain)).fetchall():
                bridges.append({
                    "source_uid": r["source_symbol_uid"],
                    "target_uid": r["target_symbol_uid"],
                    "coupling_type": r["coupling_type"],
                    "source_variable": r["source_variable"],
                    "target_variable": r["target_variable"],
                    "transformation": r["transformation"],
                })
        except sqlite3.OperationalError:
            pass

    results: List[PathResult] = []

    for b in bridges:
        bridge_src_uid = b["source_uid"]
        bridge_tgt_uid = b["target_uid"]

        # 1. 查詢來源端內部調用鏈: from_uid -> bridge_src_uid
        src_paths = query_api_path(
            from_uid=from_uid,
            to_uid=bridge_src_uid,
            max_hops=max(1, max_hops // 2),
            limit=2,
            subgraphs_dir=pool.subgraphs_dir,
        ) if from_uid != bridge_src_uid else [{
            "edge_chain": [], "hop_count": 0, "path_semantics": "READ_TRAVERSAL", "path_hash": 0
        }]

        # 2. 查詢目標端內部調用鏈: bridge_tgt_uid -> to_uid
        tgt_paths = query_api_path(
            from_uid=bridge_tgt_uid,
            to_uid=to_uid,
            max_hops=max(1, max_hops // 2),
            limit=2,
            subgraphs_dir=pool.subgraphs_dir,
        ) if bridge_tgt_uid != to_uid else [{
            "edge_chain": [], "hop_count": 0, "path_semantics": "READ_TRAVERSAL", "path_hash": 0
        }]

        for sp in src_paths:
            for tp in tgt_paths:
                total_hops = sp["hop_count"] + 1 + tp["hop_count"]
                if total_hops > max_hops:
                    continue

                bridge_edge = {
                    "rel": "CROSS_DOMAIN_BRIDGE",
                    "coupling_type": b["coupling_type"],
                    "source_var": b["source_variable"],
                    "target_var": b["target_variable"],
                    "transformation": b["transformation"],
                    "from_uid": bridge_src_uid,
                    "to_uid": bridge_tgt_uid,
                }
                merged_chain = sp["edge_chain"] + [bridge_edge] + tp["edge_chain"]
                p_hash = (sp.get("path_hash", 0) ^ 0x5A5A ^ tp.get("path_hash", 0)) & 0x7FFFFFFFFFFFFFFF

                results.append(PathResult(
                    from_uid=from_uid,
                    to_uid=to_uid,
                    hop_count=total_hops,
                    path_semantics=path_semantics or "CROSS_BRIDGE",
                    path_hash=p_hash,
                    edge_chain=merged_chain,
                    stage="CROSS_DOMAIN_BRIDGE",
                    query_time_ms=(time.perf_counter() - t_start) * 1000.0,
                ))
                if len(results) >= limit:
                    return results

    return results


# ============================================================================
# 3. 符號與文件聯合檢索 (search_symbols_federated)
# ============================================================================

def search_symbols_federated(
    query: str,
    domain: Optional[Union[int, str, DomainID]] = None,
    kind: Optional[str] = None,
    level: str = "L0",  # "L0", "L1", "ALL"
    top_k: int = 10,
    subgraphs_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """跨領域子圖聯合檢索符號定義，輸出漸進式卡片。

    引數：
    - query: 符號名稱、完全限定名 (FQN) 或方法關鍵字。
    - domain: 領域編號 (0~9) 或領域名稱 ('structural', 'fluids' 等)；若為 None 則聯邦搜尋所有子圖。
    - kind: 符號種類篩選 ('CLASS', 'PROPERTY', 'METHOD', 'ENUM', 'INDEXER')。
    - level: 卡片粒度：
      - 'L0': ~50 tokens 核心摘要卡 (fqn, kind, domain, summary)
      - 'L1': ~250 tokens 完整規格卡 (含引數、傳回型別、枚舉契約)
      - 'ALL': 同時輸出 L0 與 L1 結構。
    - top_k: 最大傳回數量。
    """
    clean_q = query.strip()
    if not clean_q:
        return []

    pool = get_global_pool(subgraphs_dir)

    # 決定要搜尋的領域清單
    if domain is not None:
        target_domains = [parse_domain_id(domain)]
    else:
        # 0 ~ 9 領域子圖 (排除 10: bridge)
        target_domains = [d for d in range(10)]

    hits: List[Dict[str, Any]] = []

    for d_id in target_domains:
        filename = get_subgraph_filename(d_id)
        db_path = pool.subgraphs_dir / filename
        if not db_path.exists():
            continue

        conn = pool.get_domain_connection(d_id)
        cur = conn.cursor()

        # 支援完全匹配、前綴匹配與包含匹配
        sql = """
            SELECT symbol_uid, domain_id, canonical_uri, fqn, symbol_kind,
                   return_type_uid, is_root_entry, is_hub_anchor,
                   l0_summary_json, l1_signature_json,
                   CASE
                       WHEN fqn = ? THEN 100
                       WHEN fqn LIKE ? THEN 80
                       WHEN fqn LIKE ? THEN 60
                       ELSE 40
                   END AS match_score
            FROM symbols
            WHERE (fqn = ? OR fqn LIKE ? OR fqn LIKE ?)
              AND (? IS NULL OR symbol_kind = ?)
            ORDER BY match_score DESC, is_root_entry DESC, is_hub_anchor DESC
            LIMIT ?
        """
        prefix_pattern = f"{clean_q}%"
        contains_pattern = f"%{clean_q}%"
        try:
            cur.execute(sql, (
                clean_q,
                prefix_pattern,
                contains_pattern,
                clean_q,
                prefix_pattern,
                contains_pattern,
                kind.upper() if kind else None,
                kind.upper() if kind else None,
                top_k,
            ))
            rows = cur.fetchall()
        except sqlite3.OperationalError:
            continue

        for r in rows:
            try:
                l0_data = json.loads(r["l0_summary_json"]) if r["l0_summary_json"] else {"summary": r["fqn"]}
            except Exception:
                l0_data = {"summary": r["fqn"]}

            try:
                l1_data = json.loads(r["l1_signature_json"]) if r["l1_signature_json"] else {}
            except Exception:
                l1_data = {}

            card: Dict[str, Any] = {
                "symbol_uid": r["symbol_uid"],
                "domain_id": r["domain_id"],
                "domain_name": get_domain_name(r["domain_id"]),
                "canonical_uri": r["canonical_uri"],
                "fqn": r["fqn"],
                "symbol_kind": r["symbol_kind"],
                "is_root_entry": bool(r["is_root_entry"]),
                "is_hub_anchor": bool(r["is_hub_anchor"]),
                "score": r["match_score"],
            }

            if level.upper() == "L0":
                card["l0_summary"] = l0_data
            elif level.upper() == "L1":
                card["l1_signature"] = l1_data
            else:  # ALL
                card["l0_summary"] = l0_data
                card["l1_signature"] = l1_data

            hits.append(card)

    # 依匹配分數降序排序並限制筆數
    hits.sort(key=lambda x: x["score"], reverse=True)
    return hits[:top_k]


def get_symbol_by_uid(
    symbol_uid: int,
    level: str = "ALL",
    subgraphs_dir: Optional[Path] = None,
) -> Optional[Dict[str, Any]]:
    """依據 64-bit symbol_uid 零查找直達子圖獲取符號定義。"""
    pool = get_global_pool(subgraphs_dir)
    domain_id = extract_domain_id(symbol_uid)
    filename = get_subgraph_filename(domain_id)
    db_path = pool.subgraphs_dir / filename
    if not db_path.exists():
        return None

    conn = pool.get_domain_connection(domain_id)
    cur = conn.cursor()
    sql = """
        SELECT symbol_uid, domain_id, canonical_uri, fqn, symbol_kind,
               return_type_uid, is_root_entry, is_hub_anchor,
               l0_summary_json, l1_signature_json
        FROM symbols
        WHERE symbol_uid = ?
    """
    try:
        cur.execute(sql, (symbol_uid,))
        r = cur.fetchone()
    except sqlite3.OperationalError:
        return None

    if not r:
        return None

    try:
        l0 = json.loads(r["l0_summary_json"]) if r["l0_summary_json"] else {}
    except Exception:
        l0 = {}
    try:
        l1 = json.loads(r["l1_signature_json"]) if r["l1_signature_json"] else {}
    except Exception:
        l1 = {}

    res = {
        "symbol_uid": r["symbol_uid"],
        "domain_id": r["domain_id"],
        "domain_name": get_domain_name(r["domain_id"]),
        "canonical_uri": r["canonical_uri"],
        "fqn": r["fqn"],
        "symbol_kind": r["symbol_kind"],
        "is_root_entry": bool(r["is_root_entry"]),
        "is_hub_anchor": bool(r["is_hub_anchor"]),
    }
    if level.upper() in ("L0", "ALL"):
        res["l0_summary"] = l0
    if level.upper() in ("L1", "ALL"):
        res["l1_signature"] = l1
    return res


# ============================================================================
# 4. 跨場橋接查詢 (query_cross_domain_bridge)
# ============================================================================

def query_cross_domain_bridge(
    coupling_type: Optional[str] = None,
    source_domain: Optional[Union[int, str, DomainID]] = None,
    target_domain: Optional[Union[int, str, DomainID]] = None,
    variable_name: Optional[str] = None,
    subgraphs_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """查詢 multiphysics_bridge.sqlite 中的多物理場介面變數配對。

    支援耦合型別：
    - 'FSI': 流固耦合 (Fluid-Structure Interaction: Fluent / CFX <-> Mechanical)
    - 'CHT': 共軛熱傳 (Conjugate Heat Transfer: Fluent <-> Mechanical / Icepak)
    - 'MBD-DEM': 機構-離散元耦合 (Motion <-> Rocky DEM)
    - 'STOP': 結構-熱-光學整合 (Structural-Thermal-Optical Performance: Mechanical <-> Zemax/Speos)

    引數：
    - coupling_type: 耦合型別篩選 ('FSI', 'CHT', 'MBD-DEM', 'STOP')。
    - source_domain: 來源物理域 (名稱、ID 或枚舉)。
    - target_domain: 目標物理域 (名稱、ID 或枚舉)。
    - variable_name: 介面變數名稱 (如 'Force', 'HeatFlux', 'Displacement')。
    """
    pool = get_global_pool(subgraphs_dir)
    bridge_conn = pool.get_bridge_connection()
    cur = bridge_conn.cursor()

    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    results: List[Dict[str, Any]] = []

    src_did = parse_domain_id(source_domain) if source_domain is not None else None
    tgt_did = parse_domain_id(target_domain) if target_domain is not None else None
    c_type = coupling_type.strip().upper() if coupling_type else None

    # 1. 查詢 cross_domain_interfaces 表
    if "cross_domain_interfaces" in tables:
        conditions = ["1=1"]
        params: List[Any] = []
        if c_type:
            conditions.append("coupling_type = ?")
            params.append(c_type)
        if src_did is not None:
            conditions.append("source_domain_id = ?")
            params.append(src_did)
        if tgt_did is not None:
            conditions.append("target_domain_id = ?")
            params.append(tgt_did)

        sql = f"""
            SELECT interface_id, source_domain_id, source_uid, target_domain_id, target_uid,
                   coupling_type, mapping_contract_json
            FROM cross_domain_interfaces
            WHERE {" AND ".join(conditions)}
            ORDER BY coupling_type, interface_id ASC
        """
        try:
            for r in cur.execute(sql, params).fetchall():
                try:
                    contract = json.loads(r["mapping_contract_json"]) if r["mapping_contract_json"] else {}
                except Exception:
                    contract = {}

                src_var = contract.get("source_variable", "InterfaceVar")
                tgt_var = contract.get("target_variable", "InterfaceVar")

                if variable_name:
                    v_clean = variable_name.strip().lower()
                    if v_clean not in src_var.lower() and v_clean not in tgt_var.lower():
                        continue

                results.append({
                    "id": r["interface_id"],
                    "coupling_type": r["coupling_type"],
                    "source": {
                        "domain_id": r["source_domain_id"],
                        "domain_name": get_domain_name(r["source_domain_id"]),
                        "symbol_uid": r["source_uid"],
                        "variable": src_var,
                    },
                    "target": {
                        "domain_id": r["target_domain_id"],
                        "domain_name": get_domain_name(r["target_domain_id"]),
                        "symbol_uid": r["target_uid"],
                        "variable": tgt_var,
                    },
                    "transformation": contract.get("transformation", "DirectMapping"),
                    "transfer_direction": contract.get("transfer_direction", "BI_DIRECTIONAL"),
                    "doc": contract.get("doc", ""),
                })
        except sqlite3.OperationalError:
            pass

    # 2. 查詢 multiphysics_bridges 表
    if "multiphysics_bridges" in tables:
        conditions = ["1=1"]
        params = []
        if c_type:
            conditions.append("coupling_type = ?")
            params.append(c_type)
        if src_did is not None:
            conditions.append("source_domain_id = ?")
            params.append(src_did)
        if tgt_did is not None:
            conditions.append("target_domain_id = ?")
            params.append(tgt_did)
        if variable_name:
            conditions.append("(source_variable LIKE ? OR target_variable LIKE ?)")
            v_pat = f"%{variable_name.strip()}%"
            params.extend([v_pat, v_pat])

        sql = f"""
            SELECT id, coupling_type, source_domain_id, source_symbol_uid, source_variable,
                   target_domain_id, target_symbol_uid, target_variable,
                   transformation, transfer_direction, doc
            FROM multiphysics_bridges
            WHERE {" AND ".join(conditions)}
            ORDER BY coupling_type, id ASC
        """
        try:
            for r in cur.execute(sql, params).fetchall():
                results.append({
                    "id": r["id"],
                    "coupling_type": r["coupling_type"],
                    "source": {
                        "domain_id": r["source_domain_id"],
                        "domain_name": get_domain_name(r["source_domain_id"]),
                        "symbol_uid": r["source_symbol_uid"],
                        "variable": r["source_variable"],
                    },
                    "target": {
                        "domain_id": r["target_domain_id"],
                        "domain_name": get_domain_name(r["target_domain_id"]),
                        "symbol_uid": r["target_symbol_uid"],
                        "variable": r["target_variable"],
                    },
                    "transformation": r["transformation"] or "DirectMapping",
                    "transfer_direction": r["transfer_direction"] or "BI_DIRECTIONAL",
                    "doc": r["doc"] or "",
                })
        except sqlite3.OperationalError:
            pass

    return results


# ============================================================================
# 5. 高階聯邦查詢介面封裝 (FederatedQueryEngine)
# ============================================================================

class FederatedQueryEngine:
    """聯邦子圖高階查詢引擎物件，供 MCP 工具層與 CAE 分析器重複調用。"""

    def __init__(self, subgraphs_dir: Optional[Path] = None):
        self.subgraphs_dir = Path(subgraphs_dir) if subgraphs_dir else DEFAULT_SUBGRAPHS_DIR
        self.pool = get_global_pool(self.subgraphs_dir)

    def route_symbol(self, symbol_uid: int) -> Path:
        """O(1) 零查找子圖定位。"""
        return route_symbol_subgraph(symbol_uid, self.subgraphs_dir)

    def query_path(
        self,
        from_uid: int,
        to_uid: int,
        path_semantics: Optional[str] = None,
        max_hops: int = 8,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """執行 Stage A/B 兩階段 8 跳路徑查詢。"""
        return query_api_path(
            from_uid=from_uid,
            to_uid=to_uid,
            path_semantics=path_semantics,
            max_hops=max_hops,
            limit=limit,
            subgraphs_dir=self.subgraphs_dir,
        )

    def search_symbols(
        self,
        query: str,
        domain: Optional[Union[int, str, DomainID]] = None,
        kind: Optional[str] = None,
        level: str = "L0",
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """跨領域聯合檢索 API 符號。"""
        return search_symbols_federated(
            query=query,
            domain=domain,
            kind=kind,
            level=level,
            top_k=top_k,
            subgraphs_dir=self.subgraphs_dir,
        )

    def get_symbol(self, symbol_uid: int, level: str = "ALL") -> Optional[Dict[str, Any]]:
        """獲取特定符號完整卡片。"""
        return get_symbol_by_uid(symbol_uid, level=level, subgraphs_dir=self.subgraphs_dir)

    def query_bridge(
        self,
        coupling_type: Optional[str] = None,
        source_domain: Optional[Union[int, str, DomainID]] = None,
        target_domain: Optional[Union[int, str, DomainID]] = None,
        variable_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """查詢跨場耦合介面變數。"""
        return query_cross_domain_bridge(
            coupling_type=coupling_type,
            source_domain=source_domain,
            target_domain=target_domain,
            variable_name=variable_name,
            subgraphs_dir=self.subgraphs_dir,
        )

    def close(self):
        """關閉所有連線釋放記憶體。"""
        self.pool.close_all()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
