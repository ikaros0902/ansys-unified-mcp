"""
Stage 3 聯邦知識圖譜、位元分區 64-bit UID 與轉移閉包全套單元測試
(tests/unit/test_stage3_federated_kg_and_closure.py)

驗證範圍：
1. federated_schemas.py:
   - 位元分區 64-bit symbol_uid 產生與 domain_id 雙向解析 (O(1) 路由)。
   - 全部 10 大物理領域之 ID 映射、檔名對照與 Canonical URI 規格化格式。
   - 無 xxhash 時的 hashlib.sha256 平滑降級機制。
2. federated_schema.sql 與防坍縮主鍵:
   - 建立臨時測試 SQLite 資料庫，插入起點相同、終點相同的兩條路徑
     (一條 FACTORY_CREATE，一條 READ_TRAVERSAL)，
     驗證主鍵 (from_uid, to_uid, path_semantics, path_hash) 成功共存，無 IntegrityError 且無路徑坍縮。
3. build_transitive_closure.py:
   - 反向屬性（Parent, DataModel, Root, Application 等）100% 剪枝。
   - 樞紐節點（is_hub_anchor = 1, 每域 <= 30）與根入口（is_root_entry = 1）正確標記。
4. federated_query.py 兩階段 8 跳查詢與效能：
   - 構建從 ExtAPI (0) -> DataModel (1) -> Project (2) -> Model (3) -> Analyses[0] (4) -> Solution (5) -> AddTotalDeformation() (6) 之真實 6 跳調用鏈（經由樞紐節點 Model 與 Solution）。
   - 呼叫 query_api_path，驗證成功檢索出完整 6 跳調用鏈（Stage B 樞紐二階拼接與 Stage A 直達）。
   - 延遲驗證：度量連續 100 次檢索延遲，驗證 P95 延遲嚴格小於 2.0 ms！
5. 跨子圖橋接：
   - 驗證 multiphysics_bridge 跨領域介面映射查詢與跨域調用鏈拼接。
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import patch

import pytest

# 匯入待測試之 Stage 3 核心模組
from ansys_unified_mcp.analytics.apikb.federated_schemas import (
    DOMAIN_BIT_SHIFT,
    DOMAIN_ID_MASK,
    DOMAIN_NAMES,
    DOMAIN_SUBGRAPH_FILES,
    FEDERATED_SCHEMA_SQL_PATH,
    MASK_56_BITS,
    NAME_TO_DOMAIN_ID,
    CrossDomainInterfaceRecord,
    DomainID,
    FederatedSymbolRecord,
    NavigationClosureRecord,
    compute_uri_hash56,
    create_canonical_uri,
    create_symbol_uid,
    extract_domain_id,
    extract_local_hash,
    generate_symbol_uid,
    get_domain_name,
    get_subgraph_filename,
    init_bridge_database,
    init_subgraph_database,
    parse_canonical_uri,
    parse_domain_id,
)
from scripts.api_extraction.build_transitive_closure import (
    DOMAIN_HUB_ANCHORS,
    DOMAIN_ROOT_ENTRIES,
    PRUNED_EDGE_MEMBERS,
    build_closure_for_domain,
    classify_path_semantics,
    compute_64bit_path_hash,
    ensure_schema,
    identify_and_mark_hubs_and_roots,
)
from ansys_unified_mcp.analytics.apikb.federated_query import (
    FederatedQueryEngine,
    SubgraphConnectionPool,
    get_global_pool,
    query_api_path,
    query_cross_domain_bridge,
    route_symbol_subgraph,
    search_symbols_federated,
)


# ============================================================================
# 模組 1: federated_schemas.py 單元測試
# ============================================================================

class TestFederatedSchemas:
    """測試 64-bit 位元分區識別碼、領域映射與降級機制"""

    def test_bit_partitioned_uid_generation_and_bidirectional_parsing(self):
        """驗證位元分區 64-bit symbol_uid 產生與 domain_id 雙向解析正確無誤 (O(1) 路由)"""
        for d_id in range(11):
            test_uri = f"ansys://{DOMAIN_NAMES[d_id]}/test/Component#{d_id}"
            uid = generate_symbol_uid(d_id, test_uri)

            # 驗證為 64-bit 正整數範圍
            assert isinstance(uid, int)
            assert 0 <= uid < (1 << 63), f"UID {uid} 超出 64 位元正整數上限"

            # 驗證 O(1) 雙向解析：高 8 位元精確還原 domain_id
            parsed_domain = extract_domain_id(uid)
            assert parsed_domain == d_id, f"解析 domain_id 失敗: 預期 {d_id}, 得到 {parsed_domain}"

            # 驗證低 56 位元局部雜湊提取
            local_hash = extract_local_hash(uid)
            assert 0 <= local_hash <= MASK_56_BITS
            assert uid == (d_id << DOMAIN_BIT_SHIFT) | local_hash

            # 驗證子圖檔名精確映射
            expected_file = DOMAIN_SUBGRAPH_FILES[d_id]
            assert get_subgraph_filename(uid) == expected_file
            assert get_domain_name(uid) == DOMAIN_NAMES[d_id]

    def test_all_10_physical_domains_mapping_and_uri_format(self):
        """驗證全部 10 大物理領域之 ID 映射、別名與 Canonical URI 規格化格式"""
        expected_domains = {
            0: "foundation",
            1: "structural",
            2: "fluids",
            3: "electromagnetics",
            4: "optics",
            5: "thermal",
            6: "multibody",
            7: "particles",
            8: "materials",
            9: "framework",
        }
        for d_id, name in expected_domains.items():
            assert DomainID(d_id).value == d_id
            assert DOMAIN_NAMES[d_id] == name
            assert parse_domain_id(name) == d_id
            assert parse_domain_id(d_id) == d_id
            assert get_domain_name(d_id) == name

        # 驗證別名相容映射
        aliases = {
            "mechanical": DomainID.STRUCTURAL,
            "mapdl": DomainID.STRUCTURAL,
            "lsdyna": DomainID.STRUCTURAL,
            "fluent": DomainID.FLUIDS,
            "cfx": DomainID.FLUIDS,
            "hfss": DomainID.ELECTROMAGNETICS,
            "maxwell": DomainID.ELECTROMAGNETICS,
            "speos": DomainID.OPTICS,
            "zemax": DomainID.OPTICS,
            "icepak": DomainID.THERMAL,
            "motion": DomainID.MULTIBODY,
            "rocky": DomainID.PARTICLES,
            "granta": DomainID.MATERIALS,
            "spaceclaim": DomainID.FRAMEWORK,
            "workbench": DomainID.FRAMEWORK,
            "optislang": DomainID.FRAMEWORK,
        }
        for alias, expected_enum in aliases.items():
            assert parse_domain_id(alias) == expected_enum.value

        # 驗證 Canonical URI 規格化產生與雙向解析 (有命名空間與無命名空間)
        uri1 = create_canonical_uri("structural", "mechanical", "Ansys.ACT.Automation.Mechanical.Model", 0)
        assert uri1 == "ansys://structural/mechanical/Ansys.ACT.Automation.Mechanical.Model#0"
        parsed1 = parse_canonical_uri(uri1)
        assert parsed1["domain"] == "structural"
        assert parsed1["namespace"] == "mechanical"
        assert parsed1["fqn"] == "Ansys.ACT.Automation.Mechanical.Model"
        assert parsed1["arity"] == 0

        uri2 = create_canonical_uri("foundation", "", "Ansys.Core.RootContext", 2)
        assert uri2 == "ansys://foundation/Ansys.Core.RootContext#2"
        parsed2 = parse_canonical_uri(uri2)
        assert parsed2["domain"] == "foundation"
        assert parsed2["namespace"] == ""
        assert parsed2["fqn"] == "Ansys.Core.RootContext"
        assert parsed2["arity"] == 2

    def test_sha256_smooth_fallback_when_xxhash_absent(self):
        """驗證無 xxhash 時的 hashlib.sha256 平滑降級機制"""
        test_uri = "ansys://fluids/fluent/Solver/iterate#1"

        # 模擬無 xxhash 環境 (HAS_XXHASH = False, xxhash = None)
        with patch("ansys_unified_mcp.analytics.apikb.federated_schemas.HAS_XXHASH", False), \
             patch("ansys_unified_mcp.analytics.apikb.federated_schemas.xxhash", None):
            h_fallback = compute_uri_hash56(test_uri)

            # 驗證落於 56 位元正整數遮罩區間
            assert 0 <= h_fallback <= MASK_56_BITS

            # 驗證精確匹配 sha256 截取大端序前 8 位元組 & MASK_56_BITS
            expected_raw = int.from_bytes(hashlib.sha256(test_uri.encode("utf-8")).digest()[:8], byteorder="big")
            expected_h = expected_raw & MASK_56_BITS
            assert h_fallback == expected_h

            # 驗證降級模式下的 symbol_uid 生成與 O(1) 路由依然完全正確
            uid_fallback = generate_symbol_uid(DomainID.FLUIDS, test_uri)
            assert extract_domain_id(uid_fallback) == DomainID.FLUIDS
            assert extract_local_hash(uid_fallback) == expected_h


# ============================================================================
# 模組 2: federated_schema.sql 與防坍縮主鍵測試
# ============================================================================

class TestFederatedSchemaAntiCollapsePK:
    """測試 SQLite DDL 與防坍縮複合主鍵 (from_uid, to_uid, path_semantics, path_hash)"""

    def test_schema_ddl_and_anti_collapse_primary_key_coexistence(self):
        """
        建立臨時測試 SQLite 資料庫，插入起點相同、終點相同的兩條路徑：
        - Path A: FACTORY_CREATE (例如 AddNamedSelection)
        - Path B: READ_TRAVERSAL (例如 NamedSelections[0])
        驗證主鍵 (from_uid, to_uid, path_semantics, path_hash) 成功共存，
        無 IntegrityError 且無路徑坍縮！
        """
        conn = sqlite3.connect(":memory:")
        init_subgraph_database(conn)

        # 建立起點與終點 UID (結構力學域)
        start_uid = create_symbol_uid("structural", "mechanical", "Ansys.ACT.Automation.Mechanical.Model", 0)
        target_uid = create_symbol_uid("structural", "mechanical", "Ansys.ACT.Automation.Mechanical.NamedSelection", 0)

        # 插入路徑 1: 工廠創建語義 (FACTORY_CREATE)
        path1 = NavigationClosureRecord(
            from_uid=start_uid,
            to_uid=target_uid,
            path_semantics="FACTORY_CREATE",
            path_hash=1001,
            hop_count=1,
            is_to_hub=1,
            edge_chain_json=json.dumps([{"via": "AddNamedSelection()", "rel": "FACTORY_METHOD"}]),
        )

        # 插入路徑 2: 唯讀導航遍歷語義 (READ_TRAVERSAL)
        path2 = NavigationClosureRecord(
            from_uid=start_uid,
            to_uid=target_uid,
            path_semantics="READ_TRAVERSAL",
            path_hash=2002,
            hop_count=2,
            is_to_hub=1,
            edge_chain_json=json.dumps([
                {"via": "NamedSelections", "rel": "PROPERTY"},
                {"via": "[0]", "rel": "INDEXER"}
            ]),
        )

        cur = conn.cursor()
        sql_insert = """
            INSERT INTO api_navigation_closure (
                from_uid, to_uid, path_semantics, path_hash, hop_count, is_to_hub, edge_chain_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        # 兩條相同起點與終點的路徑成功插入，不拋出任何 IntegrityError
        cur.execute(sql_insert, (
            path1.from_uid, path1.to_uid, path1.path_semantics,
            path1.path_hash, path1.hop_count, path1.is_to_hub, path1.edge_chain_json
        ))
        cur.execute(sql_insert, (
            path2.from_uid, path2.to_uid, path2.path_semantics,
            path2.path_hash, path2.hop_count, path2.is_to_hub, path2.edge_chain_json
        ))
        conn.commit()

        # 查詢並驗證兩條路徑共存 (未坍縮為單一路徑)
        cur.execute(
            "SELECT path_semantics, path_hash, hop_count FROM api_navigation_closure WHERE from_uid = ? AND to_uid = ? ORDER BY hop_count ASC",
            (start_uid, target_uid),
        )
        rows = cur.fetchall()
        assert len(rows) == 2, f"預期 2 條共存路徑，實際僅檢出 {len(rows)} 條，發生路徑坍縮！"
        assert rows[0][0] == "FACTORY_CREATE"
        assert rows[0][1] == 1001
        assert rows[0][2] == 1
        assert rows[1][0] == "READ_TRAVERSAL"
        assert rows[1][1] == 2002
        assert rows[1][2] == 2

        # 驗證完全重複的 4-tuple 插入時嚴格觸發 IntegrityError (防禦性重複主鍵約束)
        with pytest.raises(sqlite3.IntegrityError):
            cur.execute(sql_insert, (
                path1.from_uid, path1.to_uid, path1.path_semantics,
                path1.path_hash, path1.hop_count, path1.is_to_hub, path1.edge_chain_json
            ))


# ============================================================================
# 模組 3: build_transitive_closure.py 單元測試
# ============================================================================

class TestBuildTransitiveClosure:
    """測試轉移閉包生成器：反向邊剪枝與樞紐錨點標記"""

    @pytest.fixture
    def mock_db_connection(self):
        """建立測試用的 symbols, edges, members 結構記憶體資料庫"""
        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        cur.executescript("""
            CREATE TABLE symbols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product TEXT NOT NULL,
                kind TEXT NOT NULL,
                fqname TEXT NOT NULL,
                name TEXT NOT NULL,
                doc TEXT,
                release TEXT NOT NULL DEFAULT 'v251',
                interface TEXT NOT NULL DEFAULT 'act',
                source_id INTEGER
            );
            CREATE TABLE members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sig_hash TEXT UNIQUE NOT NULL,
                kind TEXT NOT NULL,
                name TEXT NOT NULL,
                signature TEXT,
                return_type TEXT,
                doc TEXT
            );
            CREATE TABLE edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                src_symbol_id INTEGER NOT NULL,
                dst_symbol_id INTEGER NOT NULL,
                rel TEXT NOT NULL,
                via_member_id INTEGER
            );
        """)
        ensure_schema(conn)
        yield conn
        conn.close()

    def test_reverse_properties_100_percent_pruned(self, mock_db_connection):
        """驗證反向屬性（Parent, DataModel, Root, Application 等）被 100% 剪枝"""
        conn = mock_db_connection
        cur = conn.cursor()

        # 插入 4 個符號：Model -> Analyses -> Analysis -> Solution
        symbols_data = [
            (1, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.Model", "Model"),
            (2, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.AnalysisCollection", "Analyses"),
            (3, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.Analysis", "Analysis"),
            (4, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.Solution", "Solution"),
        ]
        cur.executemany("""
            INSERT INTO symbols (id, product, kind, fqname, name) VALUES (?, ?, ?, ?, ?)
        """, symbols_data)

        # 插入 members (包含正向成員與反向黑名單成員)
        members_data = [
            (1, "hash_analyses", "property", "Analyses"),
            (2, "hash_parent1", "property", "Parent"),         # 反向成員
            (3, "hash_datamodel", "property", "DataModel"),     # 反向成員
            (4, "hash_get", "method", "get_Item"),
            (5, "hash_solution", "property", "Solution"),
            (6, "hash_parent2", "property", "Parent"),         # 反向成員
        ]
        cur.executemany("""
            INSERT INTO members (id, sig_hash, kind, name) VALUES (?, ?, ?, ?)
        """, members_data)

        # 插入邊：
        # 1. 正向: Model (1) -> Analyses (2) via Analyses (member 1)
        # 2. 反向: Analyses (2) -> Model (1) via Parent (member 2)  <-- 必須剪枝！
        # 3. 反向: Analysis (3) -> Model (1) via DataModel (member 3) <-- 必須剪枝！
        # 4. 正向: Analyses (2) -> Analysis (3) via get_Item (member 4)
        # 5. 正向: Analysis (3) -> Solution (4) via Solution (member 5)
        # 6. 反向: Solution (4) -> Analysis (3) via Parent (member 6) <-- 必須剪枝！
        # 7. 自環: Model (1) -> Model (1) via None                <-- 必須剪枝！
        edges_data = [
            (1, 2, "PROPERTY", 1),
            (2, 1, "PROPERTY", 2),
            (3, 1, "PROPERTY", 3),
            (2, 3, "METHOD", 4),
            (3, 4, "PROPERTY", 5),
            (4, 3, "PROPERTY", 6),
            (1, 1, "SELF_LOOP", None),
        ]
        cur.executemany("""
            INSERT INTO edges (src_symbol_id, dst_symbol_id, rel, via_member_id) VALUES (?, ?, ?, ?)
        """, edges_data)
        conn.commit()

        # 執行閉包構建
        inserted_count = build_closure_for_domain(
            conn=conn,
            product="mechanical",
            max_depth_normal=4,
            max_depth_root=6,
        )
        assert inserted_count > 0

        # 檢驗 api_navigation_closure 中的所有路徑
        cur.execute("SELECT path_steps, path_display FROM api_navigation_closure")
        closure_rows = cur.fetchall()

        for steps_json, display in closure_rows:
            steps = json.loads(steps_json)
            for step in steps:
                via = (step.get("via") or "").strip().lower()
                assert via not in PRUNED_EDGE_MEMBERS, (
                    f"反向邊未被剪枝！在路徑 '{display}' 中發現黑名單成員: '{via}'"
                )
                assert step["from_id"] != step["to_id"], f"自環邊未被剪枝: {step}"

    def test_hub_anchors_and_root_entries_marking(self, mock_db_connection):
        """驗證樞紐節點（is_hub_anchor = 1）與根入口（is_root_entry = 1）正確標記"""
        conn = mock_db_connection
        cur = conn.cursor()

        symbols_data = [
            (10, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.ExtAPI", "ExtAPI"),
            (11, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.DataModel", "DataModel"),
            (12, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.Model", "Model"),
            (13, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.Analysis", "Analysis"),
            (14, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.Solution", "Solution"),
            (15, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.CustomNode", "CustomNode"),
        ]
        cur.executemany("""
            INSERT INTO symbols (id, product, kind, fqname, name) VALUES (?, ?, ?, ?, ?)
        """, symbols_data)

        # 插入若干出度邊
        cur.executemany("""
            INSERT INTO edges (src_symbol_id, dst_symbol_id, rel) VALUES (?, ?, ?)
        """, [
            (12, 13, "PROPERTY"),
            (13, 14, "PROPERTY"),
            (14, 15, "METHOD"),
        ])
        conn.commit()

        stats = identify_and_mark_hubs_and_roots(conn, "mechanical")
        assert "mechanical" in stats

        # 檢驗根入口標記 (is_root_entry)
        cur.execute("SELECT name, is_root_entry, is_hub_anchor FROM symbols WHERE product = 'mechanical'")
        sym_status = {row[0]: {"root": bool(row[1]), "hub": bool(row[2])} for row in cur.fetchall()}

        assert sym_status["ExtAPI"]["root"] is True, "ExtAPI 未被標記為 Root Entry"
        assert sym_status["DataModel"]["root"] is True, "DataModel 未被標記為 Root Entry"

        # 檢驗樞紐錨點標記 (is_hub_anchor)
        assert sym_status["Model"]["hub"] is True, "Model 未被標記為 Hub Anchor"
        assert sym_status["Analysis"]["hub"] is True, "Analysis 未被標記為 Hub Anchor"
        assert sym_status["Solution"]["hub"] is True, "Solution 未被標記為 Hub Anchor"

        # 普通自訂節點不應被誤標為 Root 或 Hub
        assert sym_status["CustomNode"]["root"] is False
        assert sym_status["CustomNode"]["hub"] is False


# ============================================================================
# 模組 4: federated_query.py 兩階段 8 跳查詢與效能基準測試
# ============================================================================

class TestFederatedQueryEngineAndPerformance:
    """測試兩階段 8 跳 API 調用鏈檢索與 P95 < 2.0 ms 延遲驗證"""

    @pytest.fixture
    def test_environment(self, tmp_path):
        """
        在臨時目錄中建立完整的 01_structural_kb.sqlite 子圖，
        構建真實 6 跳調用鏈：
        ExtAPI (0) -> DataModel (1) -> Project (2) -> Model (3) -> Analyses[0] (4) -> Solution (5) -> AddTotalDeformation() (6)
        樞紐節點：Model (3) 與 Solution (5)。
        """
        subgraphs_dir = tmp_path / "subgraphs"
        subgraphs_dir.mkdir(parents=True, exist_ok=True)
        db_path = subgraphs_dir / get_subgraph_filename(DomainID.STRUCTURAL)

        init_subgraph_database(db_path)
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()

        # 1. 產生 7 個節點的 64-bit symbol_uid (domain_id = 1, structural)
        nodes = [
            ("ExtAPI", "Ansys.ACT.Automation.Mechanical.ExtAPI", True, False),
            ("DataModel", "Ansys.ACT.Automation.Mechanical.DataModel", False, False),
            ("Project", "Ansys.ACT.Automation.Mechanical.Project", False, False),
            ("Model", "Ansys.ACT.Automation.Mechanical.Model", False, True),  # Hub
            ("Analyses", "Ansys.ACT.Automation.Mechanical.AnalysisCollection", False, False),
            ("Solution", "Ansys.ACT.Automation.Mechanical.Solution", False, True),  # Hub
            ("TotalDeformation", "Ansys.ACT.Automation.Mechanical.Results.DeformationResults.TotalDeformation", False, False),
        ]

        uids = {}
        for name, fqn, is_root, is_hub in nodes:
            uid = create_symbol_uid(DomainID.STRUCTURAL, "mechanical", fqn, 0)
            uids[name] = uid
            cur.execute("""
                INSERT INTO symbols (
                    symbol_uid, domain_id, canonical_uri, fqn, symbol_kind,
                    return_type_uid, is_root_entry, is_hub_anchor,
                    l0_summary_json, l1_signature_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                uid,
                int(DomainID.STRUCTURAL.value),
                create_canonical_uri("structural", "mechanical", fqn, 0),
                fqn,
                "CLASS",
                None,
                1 if is_root else 0,
                1 if is_hub else 0,
                json.dumps({"summary": f"{name} object"}),
                json.dumps({"properties": []}),
            ))

        # 2. 建立閉包路徑以支援 Stage B 樞紐 Meet-in-the-Middle 拼接：
        # 前半段 (3 跳): ExtAPI -> DataModel -> Project -> Model (is_to_hub = 1)
        chain_1_to_hub = [
            {"from_name": "ExtAPI", "to_name": "DataModel", "via": "DataModel", "rel": "PROPERTY"},
            {"from_name": "DataModel", "to_name": "Project", "via": "Project", "rel": "PROPERTY"},
            {"from_name": "Project", "to_name": "Model", "via": "Model", "rel": "PROPERTY"},
        ]
        cur.execute("""
            INSERT INTO api_navigation_closure (
                from_uid, to_uid, path_semantics, path_hash, hop_count, is_to_hub, edge_chain_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            uids["ExtAPI"],
            uids["Model"],
            "READ_TRAVERSAL",
            11111,
            3,
            1,  # is_to_hub = 1
            json.dumps(chain_1_to_hub),
        ))

        # 後半段 (3 跳): Model -> Analyses -> Solution -> TotalDeformation (FACTORY_CREATE)
        chain_hub_to_end = [
            {"from_name": "Model", "to_name": "Analyses", "via": "Analyses[0]", "rel": "INDEXER"},
            {"from_name": "Analyses", "to_name": "Solution", "via": "Solution", "rel": "PROPERTY"},
            {"from_name": "Solution", "to_name": "TotalDeformation", "via": "AddTotalDeformation()", "rel": "FACTORY_METHOD"},
        ]
        cur.execute("""
            INSERT INTO api_navigation_closure (
                from_uid, to_uid, path_semantics, path_hash, hop_count, is_to_hub, edge_chain_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            uids["Model"],
            uids["TotalDeformation"],
            "FACTORY_CREATE",
            22222,
            3,
            0,
            json.dumps(chain_hub_to_end),
        ))

        conn.commit()
        conn.close()

        yield {
            "subgraphs_dir": subgraphs_dir,
            "uids": uids,
            "db_path": db_path,
        }

        # 測試清理：釋放全域連線池連線，防止 Windows 檔案佔用鎖
        get_global_pool(subgraphs_dir).close_all()

    def test_real_6_hop_call_chain_stage_b_hub_join(self, test_environment):
        """
        驗證透過樞紐節點 Model (is_to_hub=1) 的 Stage B Meet-in-the-Middle 二階拼接：
        ExtAPI -> DataModel -> Project -> Model (3 跳)
        Model -> Analyses[0] -> Solution -> AddTotalDeformation() (3 跳)
        拼接為完整 6 跳調用鏈！
        """
        subgraphs_dir = test_environment["subgraphs_dir"]
        uids = test_environment["uids"]

        uid_start = uids["ExtAPI"]
        uid_end = uids["TotalDeformation"]

        results = query_api_path(
            from_uid=uid_start,
            to_uid=uid_end,
            max_hops=8,
            subgraphs_dir=subgraphs_dir,
        )

        assert len(results) > 0, "未能檢索出 6 跳調用鏈"
        path = results[0]
        assert path["hop_count"] == 6, f"預期 6 跳，實際為 {path['hop_count']}"
        assert path["stage"] == "STAGE_B_HUB_JOIN", f"預期 STAGE_B_HUB_JOIN，實際為 {path['stage']}"
        assert path["path_semantics"] == "FACTORY_CREATE"

        # 驗證 edge_chain 完整包含全部 6 個步驟
        chain = path["edge_chain"]
        assert len(chain) == 6, f"調用鏈步驟數量不符: {len(chain)}"
        expected_vias = ["DataModel", "Project", "Model", "Analyses[0]", "Solution", "AddTotalDeformation()"]
        actual_vias = [step["via"] for step in chain]
        assert actual_vias == expected_vias, f"步驟呼叫不符: {actual_vias}"

    def test_real_6_hop_call_chain_stage_a_direct(self, test_environment):
        """驗證當轉移閉包包含直達 6 跳路徑時，Stage A 直達閉包查詢優先極速命中"""
        subgraphs_dir = test_environment["subgraphs_dir"]
        uids = test_environment["uids"]
        db_path = test_environment["db_path"]

        # 插入直達 6 跳紀錄
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        direct_chain = [
            {"via": f"step_{i}", "rel": "NAV"} for i in range(1, 7)
        ]
        cur.execute("""
            INSERT INTO api_navigation_closure (
                from_uid, to_uid, path_semantics, path_hash, hop_count, is_to_hub, edge_chain_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            uids["ExtAPI"],
            uids["TotalDeformation"],
            "DIRECT_6_HOP",
            99999,
            6,
            0,
            json.dumps(direct_chain),
        ))
        conn.commit()
        conn.close()

        results = query_api_path(
            from_uid=uids["ExtAPI"],
            to_uid=uids["TotalDeformation"],
            max_hops=8,
            subgraphs_dir=subgraphs_dir,
        )
        assert len(results) > 0
        direct_path = results[0]
        assert direct_path["stage"] == "STAGE_A_DIRECT"
        assert direct_path["hop_count"] == 6

    def test_latency_verification_100_runs_p95_under_2ms(self, test_environment):
        """
        延遲嚴格度量：
        連續執行 100 次 6 跳調用鏈檢索，統計延遲分佈，
        嚴格驗證 P95 延遲小於 2.0 ms！
        """
        subgraphs_dir = test_environment["subgraphs_dir"]
        uids = test_environment["uids"]
        uid_start = uids["ExtAPI"]
        uid_end = uids["TotalDeformation"]

        # 預熱 (Warm-up) 5 次
        for _ in range(5):
            query_api_path(uid_start, uid_end, max_hops=8, subgraphs_dir=subgraphs_dir)

        # 執行 100 次連續檢索並記錄高精度時間 (毫秒)
        latencies_ms: List[float] = []
        for _ in range(100):
            t0 = time.perf_counter()
            res = query_api_path(uid_start, uid_end, max_hops=8, subgraphs_dir=subgraphs_dir)
            t1 = time.perf_counter()
            assert len(res) > 0
            latencies_ms.append((t1 - t0) * 1000.0)

        # 計算統計數據
        latencies_ms.sort()
        p50 = latencies_ms[int(0.50 * len(latencies_ms))]
        p90 = latencies_ms[int(0.90 * len(latencies_ms))]
        p95 = latencies_ms[int(0.95 * len(latencies_ms))]
        p99 = latencies_ms[int(0.99 * len(latencies_ms))]
        mean_lat = sum(latencies_ms) / len(latencies_ms)
        max_lat = max(latencies_ms)

        print("\n[Federated Query Benchmark] 100 Runs Latency Metrics:")
        print(f"  Mean: {mean_lat:.3f} ms")
        print(f"  P50:  {p50:.3f} ms")
        print(f"  P90:  {p90:.3f} ms")
        print(f"  P95:  {p95:.3f} ms (SLA Threshold < 2.0 ms)")
        print(f"  P99:  {p99:.3f} ms")
        print(f"  Max:  {max_lat:.3f} ms")

        # 客觀完成條件：P95 延遲嚴格 < 2.0 ms
        assert p95 < 2.0, f"P95 延遲超標: {p95:.3f} ms >= 2.0 ms!"


# ============================================================================
# 模組 5: 跨子圖多物理場橋接 (multiphysics_bridge) 測試
# ============================================================================

class TestCrossSubgraphBridging:
    """測試多物理場跨領域介面映射查詢與跨圖橋接調用"""

    @pytest.fixture
    def bridge_environment(self, tmp_path):
        """建立橋接資料庫與雙領域子圖"""
        subgraphs_dir = tmp_path / "subgraphs"
        subgraphs_dir.mkdir(parents=True, exist_ok=True)
        bridge_path = subgraphs_dir / get_subgraph_filename(DomainID.BRIDGE)

        init_bridge_database(bridge_path)
        conn = sqlite3.connect(str(bridge_path))
        cur = conn.cursor()

        # 插入 FSI, CHT, STOP 介面紀錄 (遵循 cross_domain_interfaces 標準 Schema)
        s_fluid = create_symbol_uid(DomainID.FLUIDS, "fluent", "WallForce", 0)
        t_struct = create_symbol_uid(DomainID.STRUCTURAL, "mechanical", "FixedSupport", 0)
        s_optics = create_symbol_uid(DomainID.OPTICS, "zemax", "LDE.Surface", 0)

        interfaces = [
            (
                int(DomainID.FLUIDS.value),
                s_fluid,
                int(DomainID.STRUCTURAL.value),
                t_struct,
                "FSI",
                json.dumps({
                    "source_variable": "Force",
                    "target_variable": "Displacement",
                    "transformation": "ConservativeProfilePreserving",
                    "transfer_direction": "BI_DIRECTIONAL",
                    "doc": "Fluid-Structure Interaction",
                })
            ),
            (
                int(DomainID.FLUIDS.value),
                s_fluid,
                int(DomainID.STRUCTURAL.value),
                t_struct,
                "CHT",
                json.dumps({
                    "source_variable": "HeatRate",
                    "target_variable": "Temperature",
                    "transformation": "DirectFluxConserving",
                    "transfer_direction": "BI_DIRECTIONAL",
                    "doc": "Conjugate Heat Transfer",
                })
            ),
            (
                int(DomainID.STRUCTURAL.value),
                t_struct,
                int(DomainID.OPTICS.value),
                s_optics,
                "STOP",
                json.dumps({
                    "source_variable": "DeformationGrid",
                    "target_variable": "ZernikeCoefficients",
                    "transformation": "SVD_RigidBody_FringeZernike",
                    "transfer_direction": "ONE_WAY",
                    "doc": "STOP Optical Performance",
                })
            ),
        ]
        cur.executemany("""
            INSERT INTO cross_domain_interfaces (
                source_domain_id, source_uid, target_domain_id, target_uid, coupling_type, mapping_contract_json
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, interfaces)
        conn.commit()
        conn.close()

        yield {
            "subgraphs_dir": subgraphs_dir,
            "bridge_path": bridge_path,
            "s_fluid": s_fluid,
            "t_struct": t_struct,
            "s_optics": s_optics,
        }

        get_global_pool(subgraphs_dir).close_all()

    def test_multiphysics_bridge_interface_query(self, bridge_environment):
        """驗證 multiphysics_bridge 跨領域介面映射查詢"""
        subgraphs_dir = bridge_environment["subgraphs_dir"]

        # 1. 依 coupling_type 查詢 FSI
        fsi_results = query_cross_domain_bridge(
            coupling_type="FSI",
            subgraphs_dir=subgraphs_dir,
        )
        assert len(fsi_results) == 1
        assert fsi_results[0]["coupling_type"] == "FSI"
        assert fsi_results[0]["source"]["variable"] == "Force"
        assert fsi_results[0]["target"]["variable"] == "Displacement"

        # 2. 依變數名模糊查詢 CHT
        cht_results = query_cross_domain_bridge(
            variable_name="HeatRate",
            subgraphs_dir=subgraphs_dir,
        )
        assert len(cht_results) == 1
        assert cht_results[0]["coupling_type"] == "CHT"

        # 3. 依領域代碼查詢 STOP
        stop_results = query_cross_domain_bridge(
            source_domain=DomainID.STRUCTURAL,
            target_domain=DomainID.OPTICS,
            subgraphs_dir=subgraphs_dir,
        )
        assert len(stop_results) == 1
        assert stop_results[0]["coupling_type"] == "STOP"
        assert "Zernike" in stop_results[0]["transformation"]

    def test_high_level_federated_query_engine_interface(self, bridge_environment):
        """驗證 FederatedQueryEngine 高階封裝介面正常運作"""
        subgraphs_dir = bridge_environment["subgraphs_dir"]
        engine = FederatedQueryEngine(subgraphs_dir=subgraphs_dir)

        # 測試跨場橋接高階方法
        bridges = engine.query_bridge(coupling_type="FSI")
        assert len(bridges) == 1
        assert bridges[0]["coupling_type"] == "FSI"

        # 測試 O(1) 路由直達路徑
        routed_path = engine.route_symbol(bridge_environment["s_fluid"])
        assert routed_path.name == "02_fluids_kb.sqlite"

        engine.close()
