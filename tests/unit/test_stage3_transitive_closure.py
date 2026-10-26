#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for Stage 3: Transitive Closure & Hub-Anchor Builder
==============================================================
驗證 build_transitive_closure.py 的六大核心保證：
1. 反向/循環邊過濾 (Upward & Reflexive Edge Pruning)
2. 樞紐錨點自動標記 (Hub-Anchor Identification, 每域 <= 30)
3. 頂層根入口標記 (Root-Entry Identification)
4. 多路徑語義保留與分類 (FACTORY_CREATE, READ_TRAVERSAL, CROSS_BRIDGE)
5. 64-bit path_hash 計算與主鍵防覆蓋
6. 有界 BFS 展開深度約束 (一般 <= 4, Root <= 6)
"""

import json
from pathlib import Path
import sqlite3
import pytest

from scripts.api_extraction.build_transitive_closure import (
    PRUNED_EDGE_MEMBERS,
    ensure_schema,
    identify_and_mark_hubs_and_roots,
    compute_64bit_path_hash,
    classify_path_semantics,
    build_closure_for_domain,
    build_closure,
)


@pytest.fixture
def mock_db_conn(tmp_path: Path):
    """建立包含典型因果樹、工廠創建、反向回環與跨場邊之記憶體測試資料庫"""
    db_file = tmp_path / "test_api_kb.sqlite"
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()

    # 建立基礎表格
    cur.execute("""
        CREATE TABLE symbols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            kind TEXT NOT NULL,
            fqname TEXT NOT NULL,
            name TEXT NOT NULL,
            doc TEXT,
            release TEXT NOT NULL DEFAULT '2025R1',
            interface TEXT NOT NULL DEFAULT 'ACT'
        )
    """)
    cur.execute("""
        CREATE TABLE members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sig_hash TEXT UNIQUE NOT NULL,
            kind TEXT NOT NULL,
            name TEXT NOT NULL,
            signature TEXT,
            return_type TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_symbol_id INTEGER NOT NULL,
            dst_symbol_id INTEGER NOT NULL,
            rel TEXT NOT NULL,
            via_member_id INTEGER
        )
    """)

    # 插入測試符號 (Mechanical)
    symbols_data = [
        # id=1: Model (Root & Hub)
        (1, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.Model", "Model"),
        # id=2: Analysis (Hub)
        (2, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.Analysis", "Analysis"),
        # id=3: Solution (Hub)
        (3, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.Solution", "Solution"),
        # id=4: TotalDeformation
        (4, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.Results.TotalDeformation", "TotalDeformation"),
        # id=5: Mesh (Hub)
        (5, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.Mesh", "Mesh"),
        # id=6: MeshMethod
        (6, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.MeshMethod", "MeshMethod"),
        # id=7: Connections (Hub)
        (7, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.Connections", "Connections"),
        # id=8: ContactRegion
        (8, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.ContactRegion", "ContactRegion"),
        # id=9: Vector3D
        (9, "mechanical", "class", "Ansys.ACT.Automation.Mechanical.Vector3D", "Vector3D"),
        # id=10: CrossBridgeGeometry (跨場幾何)
        (10, "spaceclaim", "class", "SpaceClaim.Api.V251.Part", "Part"),
    ]
    cur.executemany("INSERT INTO symbols (id, product, kind, fqname, name) VALUES (?, ?, ?, ?, ?)", symbols_data)

    # 插入測試成員
    members_data = [
        # 正向導航屬性 (READ_TRAVERSAL)
        (1, "sig1", "property", "Analyses", "() -> Analysis", "Analysis"),
        (2, "sig2", "property", "Solution", "() -> Solution", "Solution"),
        (3, "sig3", "property", "Mesh", "() -> Mesh", "Mesh"),
        (4, "sig4", "property", "Connections", "() -> Connections", "Connections"),
        # 工廠創建方法 (FACTORY_CREATE)
        (5, "sig5", "method", "AddTotalDeformation", "() -> TotalDeformation", "TotalDeformation"),
        (6, "sig6", "method", "InsertMeshMethod", "() -> MeshMethod", "MeshMethod"),
        (7, "sig7", "method", "CreateContactRegion", "() -> ContactRegion", "ContactRegion"),
        # 反向屬性 (黑名單)
        (8, "sig8", "property", "Parent", "() -> Model", "Model"),
        (9, "sig9", "property", "Root", "() -> Model", "Model"),
        (10, "sig10", "property", "Application", "() -> App", "App"),
        (11, "sig11", "property", "DataModel", "() -> DataModel", "DataModel"),
        (12, "sig12", "property", "InternalObject", "() -> Object", "Object"),
        (13, "sig13", "property", "Owner", "() -> Object", "Object"),
        # 跨場介面傳遞 (CROSS_BRIDGE)
        (14, "sig14", "method", "ExportToCADBridge", "() -> Part", "Part"),
        (15, "sig15", "method", "CrossProduct", "() -> Vector3D", "Vector3D"),
    ]
    cur.executemany("INSERT INTO members (id, sig_hash, kind, name, signature, return_type) VALUES (?, ?, ?, ?, ?, ?)", members_data)

    # 插入邊
    edges_data = [
        # 正向導航
        (1, 2, "prop_type", 1),    # Model -> Analysis (Analyses)
        (2, 3, "prop_type", 2),    # Analysis -> Solution (Solution)
        (1, 5, "prop_type", 3),    # Model -> Mesh (Mesh)
        (1, 7, "prop_type", 4),    # Model -> Connections (Connections)
        # 工廠創建
        (3, 4, "returns", 5),      # Solution -> TotalDeformation (AddTotalDeformation)
        (5, 6, "returns", 6),      # Mesh -> MeshMethod (InsertMeshMethod)
        (7, 8, "returns", 7),      # Connections -> ContactRegion (CreateContactRegion)
        # 跨場傳遞
        (1, 10, "returns", 14),    # Model -> Part (ExportToCADBridge)
        (4, 9, "returns", 15),     # TotalDeformation -> Vector3D (CrossProduct)
        # 反向回環邊 (黑名單)
        (2, 1, "prop_type", 8),    # Analysis -> Model (Parent)
        (3, 2, "prop_type", 8),    # Solution -> Analysis (Parent)
        (4, 3, "prop_type", 8),    # TotalDeformation -> Solution (Parent)
        (4, 1, "prop_type", 9),    # TotalDeformation -> Model (Root)
        (3, 1, "prop_type", 10),   # Solution -> Model (Application)
        (3, 1, "prop_type", 11),   # Solution -> Model (DataModel)
        (3, 1, "prop_type", 12),   # Solution -> Model (InternalObject)
        (3, 1, "prop_type", 13),   # Solution -> Model (Owner)
        # 自環邊 (Reflexive)
        (1, 1, "prop_type", 1),    # Model -> Model
    ]
    cur.executemany("INSERT INTO edges (src_symbol_id, dst_symbol_id, rel, via_member_id) VALUES (?, ?, ?, ?)", edges_data)
    conn.commit()

    ensure_schema(conn)
    yield conn
    conn.close()


def test_schema_creation(mock_db_conn):
    """驗證 symbols 欄位擴充與 api_navigation_closure 表建立"""
    cur = mock_db_conn.cursor()
    cur.execute("PRAGMA table_info(symbols)")
    cols = {row[1] for row in cur.fetchall()}
    assert "is_hub_anchor" in cols
    assert "is_root_entry" in cols

    cur.execute("PRAGMA table_info(api_navigation_closure)")
    closure_cols = {row[1] for row in cur.fetchall()}
    assert "from_uid" in closure_cols
    assert "to_uid" in closure_cols
    assert "path_semantics" in closure_cols
    assert "path_hash" in closure_cols
    assert "depth" in closure_cols


def test_hub_and_root_identification(mock_db_conn):
    """驗證樞紐錨點與根入口自動標記 (每域核心容器 <= 30)"""
    stats = identify_and_mark_hubs_and_roots(mock_db_conn)
    cur = mock_db_conn.cursor()

    # 驗證根節點標記 (Model)
    cur.execute("SELECT name, is_root_entry, is_hub_anchor FROM symbols WHERE name = 'Model'")
    row = cur.fetchone()
    assert row[1] == 1, "Model 應標記為根入口 is_root_entry = 1"
    assert row[2] == 1, "Model 同時為核心容器 is_hub_anchor = 1"

    # 驗證 Hub 標記
    cur.execute("SELECT name FROM symbols WHERE is_hub_anchor = 1")
    hub_names = {r[0] for r in cur.fetchall()}
    for expected_hub in ["Model", "Analysis", "Solution", "Mesh", "Connections"]:
        assert expected_hub in hub_names

    # 驗證每領域 Hub 數量不超過 30 個核心節點
    for prod, s in stats.items():
        assert s["hub_anchors_count"] <= 30, f"{prod} Hub 數量應 <= 30"


def test_upward_and_reflexive_edge_pruning(mock_db_conn):
    """驗證反向邊（Parent, Root...）與自環邊在閉包中 100% 被剃除"""
    identify_and_mark_hubs_and_roots(mock_db_conn)
    build_closure_for_domain(mock_db_conn, "mechanical")

    cur = mock_db_conn.cursor()
    cur.execute("SELECT path_steps, path_display FROM api_navigation_closure")
    rows = cur.fetchall()
    assert len(rows) > 0, "應成功產出轉移閉包路徑"

    # 檢查所有路徑步驟中絕無黑名單屬性
    for steps_json, display in rows:
        steps = json.loads(steps_json)
        for s in steps:
            via = s.get("via", "").lower()
            assert via not in PRUNED_EDGE_MEMBERS, f"路徑中包含黑名單反向屬性: {via} in {display}"
            assert s["from_id"] != s["to_id"], f"路徑中包含自環邊: {display}"


def test_path_semantics_classification():
    """驗證 FACTORY_CREATE, READ_TRAVERSAL, CROSS_BRIDGE 語義判斷"""
    # 1. 工廠創建
    factory_steps = [
        {"via": "AddTotalDeformation", "rel": "returns"},
    ]
    assert classify_path_semantics(factory_steps, "mechanical", "mechanical") == "FACTORY_CREATE"

    insert_steps = [
        {"via": "InsertMeshMethod", "rel": "returns"},
    ]
    assert classify_path_semantics(insert_steps, "mechanical", "mechanical") == "FACTORY_CREATE"

    # 2. 純讀取導航
    traversal_steps = [
        {"via": "Analyses", "rel": "prop_type"},
        {"via": "Solution", "rel": "prop_type"},
    ]
    assert classify_path_semantics(traversal_steps, "mechanical", "mechanical") == "READ_TRAVERSAL"

    # 3. 跨場介面傳遞
    bridge_steps = [
        {"via": "ExportToCADBridge", "rel": "returns"},
    ]
    assert classify_path_semantics(bridge_steps, "mechanical", "mechanical") == "CROSS_BRIDGE"

    cross_prod_steps = [
        {"via": "Analyses", "rel": "prop_type"},
    ]
    assert classify_path_semantics(cross_prod_steps, "spaceclaim", "mechanical") == "CROSS_BRIDGE"


def test_64bit_path_hash_and_uniqueness():
    """驗證 64-bit path_hash 計算長度與多路徑替代防碰撞"""
    path_nodes = [1, 2, 3]
    steps_a = [
        {"from_id": 1, "to_id": 2, "via": "Analyses", "rel": "prop_type"},
        {"from_id": 2, "to_id": 3, "via": "Solution", "rel": "prop_type"},
    ]
    steps_b = [
        {"from_id": 1, "to_id": 2, "via": "GetAnalysis", "rel": "returns"},
        {"from_id": 2, "to_id": 3, "via": "Solution", "rel": "prop_type"},
    ]

    hash_a = compute_64bit_path_hash(path_nodes, steps_a)
    hash_b = compute_64bit_path_hash(path_nodes, steps_b)

    assert len(hash_a) == 16, "64-bit 雜湊應為 16 碼十六進制字串"
    assert len(hash_b) == 16
    assert hash_a != hash_b, "不同路徑步驟應產生不同 path_hash 以防碰撞"


def test_closure_bfs_depth_bounded(mock_db_conn):
    """驗證 BFS 有界深度約束 (一般 <= 4, Root <= 6)"""
    identify_and_mark_hubs_and_roots(mock_db_conn)
    build_closure_for_domain(mock_db_conn, "mechanical", max_depth_normal=4, max_depth_root=6)

    cur = mock_db_conn.cursor()
    # 檢查一般節點 (is_from_root = 0) 之最大深度
    cur.execute("SELECT MAX(depth) FROM api_navigation_closure WHERE is_from_root = 0")
    max_normal_depth = cur.fetchone()[0] or 0
    assert max_normal_depth <= 4, f"一般節點最大深度應 <= 4, 當前={max_normal_depth}"

    # 檢查根節點 (is_from_root = 1) 之最大深度
    cur.execute("SELECT MAX(depth) FROM api_navigation_closure WHERE is_from_root = 1")
    max_root_depth = cur.fetchone()[0] or 0
    assert max_root_depth <= 6, f"根節點最大深度應 <= 6, 當前={max_root_depth}"


def test_build_closure_runner(tmp_path: Path, mock_db_conn):
    """驗證完整 build_closure 呼叫與統計產出"""
    db_file = tmp_path / "test_api_kb.sqlite"
    res = build_closure(db_path=db_file, domain="mechanical", sample_build=True)

    assert res["status"] == "success"
    assert "mechanical" in res["marking_stats"]
    assert res["total_paths_built"] > 0
