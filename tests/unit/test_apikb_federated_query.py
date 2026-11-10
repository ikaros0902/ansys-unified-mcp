"""
單元與基準測試：聯邦 API 知識圖譜查詢引擎 (federated_query)
測試 Stage 3 聯邦子圖查詢、O(1) 零查找路由、兩階段 8 跳 Meet-in-the-Middle 拼接、
三級漸進式卡片檢索與跨場橋接查詢。
"""

import json
import sqlite3
import time
from pathlib import Path
import pytest

from ansys_unified_mcp.analytics.apikb.federated_schemas import (
    DomainID,
    DOMAIN_SUBGRAPH_FILES,
    create_symbol_uid,
    generate_symbol_uid,
    init_subgraph_database,
    init_bridge_database,
)
from ansys_unified_mcp.analytics.apikb.federated_query import (
    FederatedQueryEngine,
    extract_domain_id,
    route_symbol_subgraph,
    query_api_path,
    search_symbols_federated,
    get_symbol_by_uid,
    query_cross_domain_bridge,
)


@pytest.fixture
def mock_federated_env(tmp_path: Path):
    """建立模擬之 10 領域子圖與橋接資料庫環境。"""
    subgraphs_dir = tmp_path / "subgraphs"
    subgraphs_dir.mkdir(parents=True, exist_ok=True)

    # 1. 初始化結構子圖 (01_structural_kb.sqlite)
    struct_db = subgraphs_dir / DOMAIN_SUBGRAPH_FILES[DomainID.STRUCTURAL]
    conn_struct = init_subgraph_database(struct_db)

    # 建立結構節點
    # u: ExtAPI (根節點)
    uid_extapi = create_symbol_uid(DomainID.STRUCTURAL, "mechanical", "Ansys.ACT.Automation.Mechanical.ExtAPI", 0)
    # h: Analysis (Hub Anchor)
    uid_analysis = create_symbol_uid(DomainID.STRUCTURAL, "mechanical", "Ansys.ACT.Automation.Mechanical.Analysis", 0)
    # v: AddTotalDeformation (目標)
    uid_deform = create_symbol_uid(DomainID.STRUCTURAL, "mechanical", "Ansys.ACT.Automation.Mechanical.Results.AddTotalDeformation", 1)
    # mid 節點 (用以測試 3 跳)
    uid_solution = create_symbol_uid(DomainID.STRUCTURAL, "mechanical", "Ansys.ACT.Automation.Mechanical.Solution", 0)
    # deep 節點 (用以測試 8 跳終點)
    uid_deep_target = create_symbol_uid(DomainID.STRUCTURAL, "mechanical", "Ansys.ACT.Automation.Mechanical.DeepProperty", 0)

    cur_s = conn_struct.cursor()

    # 插入 symbols 記錄 (含 L0/L1 卡片)
    symbols_data = [
        (
            uid_extapi, DomainID.STRUCTURAL, "ansys://structural/mechanical/Ansys.ACT.Automation.Mechanical.ExtAPI#0",
            "Ansys.ACT.Automation.Mechanical.ExtAPI", "CLASS", None, 1, 0,
            json.dumps({"summary": "Mechanical global extension API root", "domain": "structural"}),
            json.dumps({"signature": "ExtAPI", "properties": ["DataModel", "Application"], "doc": "Root API entry point."})
        ),
        (
            uid_analysis, DomainID.STRUCTURAL, "ansys://structural/mechanical/Ansys.ACT.Automation.Mechanical.Analysis#0",
            "Ansys.ACT.Automation.Mechanical.Analysis", "CLASS", None, 0, 1,  # is_hub_anchor = 1
            json.dumps({"summary": "Structural analysis environment container", "domain": "structural"}),
            json.dumps({"signature": "Analysis", "properties": ["Solution", "Name"], "doc": "Structural analysis hub."})
        ),
        (
            uid_solution, DomainID.STRUCTURAL, "ansys://structural/mechanical/Ansys.ACT.Automation.Mechanical.Solution#0",
            "Ansys.ACT.Automation.Mechanical.Solution", "CLASS", None, 0, 1,  # is_hub_anchor = 1
            json.dumps({"summary": "Structural solver and result container", "domain": "structural"}),
            json.dumps({"signature": "Solution", "methods": ["AddTotalDeformation"], "doc": "Solution hub."})
        ),
        (
            uid_deform, DomainID.STRUCTURAL, "ansys://structural/mechanical/Ansys.ACT.Automation.Mechanical.Results.AddTotalDeformation#1",
            "Ansys.ACT.Automation.Mechanical.Results.AddTotalDeformation", "METHOD", None, 0, 0,
            json.dumps({"summary": "Creates total deformation result object", "domain": "structural"}),
            json.dumps({"signature": "AddTotalDeformation() -> TotalDeformation", "returns": "TotalDeformation", "doc": "Add deformation result."})
        ),
        (
            uid_deep_target, DomainID.STRUCTURAL, "ansys://structural/mechanical/Ansys.ACT.Automation.Mechanical.DeepProperty#0",
            "Ansys.ACT.Automation.Mechanical.DeepProperty", "PROPERTY", None, 0, 0,
            json.dumps({"summary": "Deep result tensor property", "domain": "structural"}),
            json.dumps({"signature": "DeepProperty: float", "doc": "Deep target property."})
        ),
    ]

    cur_s.executemany(
        """
        INSERT INTO symbols (
            symbol_uid, domain_id, canonical_uri, fqn, symbol_kind,
            return_type_uid, is_root_entry, is_hub_anchor,
            l0_summary_json, l1_signature_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        symbols_data
    )

    # 插入 api_navigation_closure
    # 1. 直達路徑 (Stage A: ExtAPI -> Analysis, 2 跳)
    chain_ext_to_analysis = [
        {"from": "ExtAPI", "to": "DataModel", "via": ".DataModel", "rel": "READ_TRAVERSAL"},
        {"from": "DataModel", "to": "Analysis", "via": ".AnalysisByName('Static')", "rel": "READ_TRAVERSAL"},
    ]
    cur_s.execute(
        """
        INSERT INTO api_navigation_closure (
            from_uid, to_uid, path_semantics, path_hash, hop_count, is_to_hub, edge_chain_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (uid_extapi, uid_analysis, "READ_TRAVERSAL", 101, 2, 1, json.dumps(chain_ext_to_analysis))
    )

    # 2. 直達工廠路徑 (Stage A: Analysis -> AddTotalDeformation, 2 跳, FACTORY_CREATE)
    chain_analysis_to_deform = [
        {"from": "Analysis", "to": "Solution", "via": ".Solution", "rel": "READ_TRAVERSAL"},
        {"from": "Solution", "to": "AddTotalDeformation", "via": ".AddTotalDeformation()", "rel": "FACTORY_CREATE"},
    ]
    cur_s.execute(
        """
        INSERT INTO api_navigation_closure (
            from_uid, to_uid, path_semantics, path_hash, hop_count, is_to_hub, edge_chain_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (uid_analysis, uid_deform, "FACTORY_CREATE", 102, 2, 0, json.dumps(chain_analysis_to_deform))
    )

    # 3. 唯讀路徑 (Stage A: Analysis -> AddTotalDeformation, 2 跳, READ_TRAVERSAL) 用以驗證多路徑保留
    chain_analysis_to_deform_read = [
        {"from": "Analysis", "to": "Solution", "via": ".Solution", "rel": "READ_TRAVERSAL"},
        {"from": "Solution", "to": "AddTotalDeformation", "via": ".GetResults()[0]", "rel": "READ_TRAVERSAL"},
    ]
    cur_s.execute(
        """
        INSERT INTO api_navigation_closure (
            from_uid, to_uid, path_semantics, path_hash, hop_count, is_to_hub, edge_chain_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (uid_analysis, uid_deform, "READ_TRAVERSAL", 103, 2, 0, json.dumps(chain_analysis_to_deform_read))
    )

    # 4. 深度 4 跳路徑 (Analysis -> DeepProperty, 4 跳)
    chain_analysis_to_deep = [
        {"from": "Analysis", "to": "Step1", "via": ".Step1", "rel": "READ_TRAVERSAL"},
        {"from": "Step1", "to": "Step2", "via": ".Step2", "rel": "READ_TRAVERSAL"},
        {"from": "Step2", "to": "Step3", "via": ".Step3", "rel": "READ_TRAVERSAL"},
        {"from": "Step3", "to": "DeepProperty", "via": ".DeepProperty", "rel": "READ_TRAVERSAL"},
    ]
    cur_s.execute(
        """
        INSERT INTO api_navigation_closure (
            from_uid, to_uid, path_semantics, path_hash, hop_count, is_to_hub, edge_chain_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (uid_analysis, uid_deep_target, "READ_TRAVERSAL", 104, 4, 0, json.dumps(chain_analysis_to_deep))
    )

    conn_struct.commit()
    conn_struct.close()

    # 2. 初始化流體子圖 (02_fluids_kb.sqlite)
    fluids_db = subgraphs_dir / DOMAIN_SUBGRAPH_FILES[DomainID.FLUIDS]
    conn_fluids = init_subgraph_database(fluids_db)
    uid_fluent_solver = create_symbol_uid(DomainID.FLUIDS, "fluent", "Ansys.Fluent.Solver", 0)
    uid_fluent_wall_force = create_symbol_uid(DomainID.FLUIDS, "fluent", "Ansys.Fluent.Boundary.WallForce", 0)

    cur_f = conn_fluids.cursor()
    cur_f.execute(
        """
        INSERT INTO symbols (
            symbol_uid, domain_id, canonical_uri, fqn, symbol_kind,
            return_type_uid, is_root_entry, is_hub_anchor,
            l0_summary_json, l1_signature_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            uid_fluent_wall_force, DomainID.FLUIDS, "ansys://fluids/fluent/Ansys.Fluent.Boundary.WallForce#0",
            "Ansys.Fluent.Boundary.WallForce", "PROPERTY", None, 0, 1,
            json.dumps({"summary": "Fluid boundary wall shear and pressure force", "domain": "fluids"}),
            json.dumps({"signature": "WallForce: Vector3", "doc": "Wall force boundary property."})
        )
    )
    conn_fluids.commit()
    conn_fluids.close()

    # 3. 初始化跨場橋接資料庫 (multiphysics_bridge.sqlite)
    bridge_db = subgraphs_dir / DOMAIN_SUBGRAPH_FILES[DomainID.BRIDGE]
    conn_bridge = init_bridge_database(bridge_db)
    cur_b = conn_bridge.cursor()

    # 寫入 cross_domain_interfaces 表
    contract_fsi = {
        "source_variable": "WallForce",
        "target_variable": "SurfacePressure",
        "transformation": "ConservativeForceInterpolation",
        "transfer_direction": "BI_DIRECTIONAL",
        "doc": "Fluent wall force mapped to Mechanical structural face load"
    }
    cur_b.execute(
        """
        INSERT INTO cross_domain_interfaces (
            source_domain_id, source_uid, target_domain_id, target_uid,
            coupling_type, mapping_contract_json
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            DomainID.FLUIDS, uid_fluent_wall_force,
            DomainID.STRUCTURAL, uid_analysis,
            "FSI", json.dumps(contract_fsi)
        )
    )

    # 也支援建立與寫入 multiphysics_bridges 表
    cur_b.execute(
        """
        CREATE TABLE IF NOT EXISTS multiphysics_bridges (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            coupling_type     TEXT NOT NULL,
            source_domain_id  INTEGER NOT NULL,
            source_symbol_uid INTEGER NOT NULL,
            source_variable   TEXT NOT NULL,
            target_domain_id  INTEGER NOT NULL,
            target_symbol_uid INTEGER NOT NULL,
            target_variable   TEXT NOT NULL,
            transformation    TEXT,
            transfer_direction TEXT DEFAULT 'BI_DIRECTIONAL',
            doc               TEXT
        );
        """
    )
    cur_b.execute(
        """
        INSERT INTO multiphysics_bridges (
            coupling_type, source_domain_id, source_symbol_uid, source_variable,
            target_domain_id, target_symbol_uid, target_variable, transformation, doc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "CHT", DomainID.FLUIDS, uid_fluent_wall_force, "HeatFlux",
            DomainID.STRUCTURAL, uid_analysis, "FaceTemperature", "ConservativeHeatTransfer",
            "Conjugate Heat Transfer interface"
        )
    )

    conn_bridge.commit()
    conn_bridge.close()

    return {
        "subgraphs_dir": subgraphs_dir,
        "uid_extapi": uid_extapi,
        "uid_analysis": uid_analysis,
        "uid_solution": uid_solution,
        "uid_deform": uid_deform,
        "uid_deep_target": uid_deep_target,
        "uid_fluent_wall_force": uid_fluent_wall_force,
    }


class TestZeroLookupSubgraphRouter:
    """測試 O(1) 零查找子圖路由"""

    def test_bit_shift_domain_extraction(self):
        for d_id in range(10):
            uid = (d_id << 56) | 0x123456789ABCDE
            extracted = extract_domain_id(uid)
            assert extracted == d_id, f"Domain ID {d_id} 位元提取錯誤: {extracted}"

    def test_route_subgraph_path(self, mock_federated_env):
        env = mock_federated_env
        dir_path = env["subgraphs_dir"]

        # 驗證結構域 UID 路由至 01_structural_kb.sqlite
        path_struct = route_symbol_subgraph(env["uid_extapi"], subgraphs_dir=dir_path)
        assert path_struct.name == "01_structural_kb.sqlite"
        assert path_struct.exists()

        # 驗證流體域 UID 路由至 02_fluids_kb.sqlite
        path_fluids = route_symbol_subgraph(env["uid_fluent_wall_force"], subgraphs_dir=dir_path)
        assert path_fluids.name == "02_fluids_kb.sqlite"
        assert path_fluids.exists()


class TestTwoStage8HopQuery:
    """測試兩階段 8 跳路徑查詢演算法"""

    def test_stage_a_direct_closure_hit(self, mock_federated_env):
        """Stage A 直達閉包查詢 (1~4 跳)：應由轉移閉包直接命中 (熱會話耗時 < 0.5 ms)"""
        env = mock_federated_env

        # 預熱一次消除首度檔案開啟與連線快取開銷
        query_api_path(
            from_uid=env["uid_extapi"],
            to_uid=env["uid_analysis"],
            max_hops=4,
            subgraphs_dir=env["subgraphs_dir"],
        )

        t0 = time.perf_counter()
        paths = query_api_path(
            from_uid=env["uid_extapi"],
            to_uid=env["uid_analysis"],
            max_hops=4,
            subgraphs_dir=env["subgraphs_dir"],
        )
        t_elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert len(paths) >= 1
        p = paths[0]
        assert p["stage"] == "STAGE_A_DIRECT"
        assert p["hop_count"] == 2
        assert p["path_semantics"] == "READ_TRAVERSAL"
        assert len(p["edge_chain"]) == 2
        assert p["edge_chain"][0]["from"] == "ExtAPI"
        # 熱會話極速閉環，通常 < 0.5 ms，測試環境放寬至 5.0 ms
        assert t_elapsed_ms < 5.0

    def test_multipath_semantics_preservation(self, mock_federated_env):
        """多路徑保留與語義篩選 (FACTORY_CREATE vs READ_TRAVERSAL)"""
        env = mock_federated_env

        # 1. 不限語義：應同時回傳工廠路徑與唯讀路徑
        all_paths = query_api_path(
            from_uid=env["uid_analysis"],
            to_uid=env["uid_deform"],
            max_hops=4,
            subgraphs_dir=env["subgraphs_dir"],
        )
        assert len(all_paths) == 2
        semantics_set = {p["path_semantics"] for p in all_paths}
        assert "FACTORY_CREATE" in semantics_set
        assert "READ_TRAVERSAL" in semantics_set

        # 2. 指定篩選 FACTORY_CREATE
        factory_paths = query_api_path(
            from_uid=env["uid_analysis"],
            to_uid=env["uid_deform"],
            path_semantics="FACTORY_CREATE",
            max_hops=4,
            subgraphs_dir=env["subgraphs_dir"],
        )
        assert len(factory_paths) == 1
        assert factory_paths[0]["path_semantics"] == "FACTORY_CREATE"

    def test_stage_b_hub_meet_in_the_middle_join(self, mock_federated_env):
        """Stage B: 透過 is_to_hub=1 核心樞紐錨點執行二階自連接 (Meet-in-the-Middle Join，5~8 跳)"""
        env = mock_federated_env

        # ExtAPI -> Analysis (2 跳, Analysis is Hub) + Analysis -> DeepProperty (4 跳) = 6 跳
        t0 = time.perf_counter()
        paths = query_api_path(
            from_uid=env["uid_extapi"],
            to_uid=env["uid_deep_target"],
            max_hops=8,
            subgraphs_dir=env["subgraphs_dir"],
        )
        t_elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert len(paths) >= 1
        p = paths[0]
        assert p["stage"] == "STAGE_B_HUB_JOIN"
        assert p["hop_count"] == 6  # 2 + 4 = 6 跳
        assert len(p["edge_chain"]) == 6
        assert p["edge_chain"][0]["from"] == "ExtAPI"
        assert p["edge_chain"][-1]["to"] == "DeepProperty"
        assert t_elapsed_ms < 10.0


class TestCrossDomainBridgeQuery:
    """測試跨領域橋接查詢 (multiphysics_bridge.sqlite)"""

    def test_query_bridge_interfaces(self, mock_federated_env):
        env = mock_federated_env

        # 1. 查詢 FSI 介面配對
        fsi_results = query_cross_domain_bridge(
            coupling_type="FSI",
            subgraphs_dir=env["subgraphs_dir"],
        )
        assert len(fsi_results) == 1
        fsi = fsi_results[0]
        assert fsi["coupling_type"] == "FSI"
        assert fsi["source"]["domain_name"] == "fluids"
        assert fsi["target"]["domain_name"] == "structural"
        assert fsi["source"]["variable"] == "WallForce"
        assert fsi["target"]["variable"] == "SurfacePressure"

        # 2. 查詢 CHT 介面配對
        cht_results = query_cross_domain_bridge(
            coupling_type="CHT",
            variable_name="HeatFlux",
            subgraphs_dir=env["subgraphs_dir"],
        )
        assert len(cht_results) == 1
        assert cht_results[0]["coupling_type"] == "CHT"
        assert cht_results[0]["source"]["variable"] == "HeatFlux"

    def test_cross_domain_api_path(self, mock_federated_env):
        """測試從流體端 Fluent 到結構端 AddTotalDeformation 跨場路徑拼接"""
        env = mock_federated_env

        cross_paths = query_api_path(
            from_uid=env["uid_fluent_wall_force"],
            to_uid=env["uid_deform"],
            max_hops=8,
            subgraphs_dir=env["subgraphs_dir"],
        )
        assert len(cross_paths) >= 1
        cp = cross_paths[0]
        assert cp["stage"] == "CROSS_DOMAIN_BRIDGE"
        # 鏈條中必須包含 CROSS_DOMAIN_BRIDGE 邊
        bridge_edges = [e for e in cp["edge_chain"] if e.get("rel") == "CROSS_DOMAIN_BRIDGE"]
        assert len(bridge_edges) >= 1


class TestFederatedSymbolSearch:
    """測試符號與文件聯合檢索與漸進式卡片"""

    def test_search_l0_summary_card(self, mock_federated_env):
        env = mock_federated_env
        results = search_symbols_federated(
            query="Analysis",
            domain="structural",
            level="L0",
            top_k=5,
            subgraphs_dir=env["subgraphs_dir"],
        )
        assert len(results) >= 1
        hit = results[0]
        assert "Analysis" in hit["fqn"]
        assert "l0_summary" in hit
        assert "summary" in hit["l0_summary"]

    def test_search_l1_signature_card(self, mock_federated_env):
        env = mock_federated_env
        results = search_symbols_federated(
            query="AddTotalDeformation",
            level="L1",
            top_k=5,
            subgraphs_dir=env["subgraphs_dir"],
        )
        assert len(results) >= 1
        hit = results[0]
        assert "l1_signature" in hit
        assert "signature" in hit["l1_signature"]
        assert hit["l1_signature"]["returns"] == "TotalDeformation"

    def test_get_symbol_by_uid(self, mock_federated_env):
        env = mock_federated_env
        sym = get_symbol_by_uid(env["uid_analysis"], level="ALL", subgraphs_dir=env["subgraphs_dir"])
        assert sym is not None
        assert sym["fqn"] == "Ansys.ACT.Automation.Mechanical.Analysis"
        assert sym["is_hub_anchor"] is True
        assert "l0_summary" in sym
        assert "l1_signature" in sym


class TestFederatedQueryEngineObject:
    """測試高階物件封裝 FederatedQueryEngine"""

    def test_engine_context_manager(self, mock_federated_env):
        env = mock_federated_env
        with FederatedQueryEngine(subgraphs_dir=env["subgraphs_dir"]) as engine:
            path_file = engine.route_symbol(env["uid_extapi"])
            assert path_file.name == "01_structural_kb.sqlite"

            paths = engine.query_path(env["uid_extapi"], env["uid_analysis"])
            assert len(paths) >= 1

            sym = engine.get_symbol(env["uid_analysis"])
            assert sym is not None

            bridges = engine.query_bridge(coupling_type="FSI")
            assert len(bridges) == 1
