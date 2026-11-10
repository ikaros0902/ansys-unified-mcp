"""
單元測試：聯邦 API 知識圖譜架構與 64-bit 位元分區識別碼 (federated_schemas)
"""

import hashlib
import sqlite3
import pytest

from ansys_unified_mcp.analytics.apikb.federated_schemas import (
    DomainID,
    DOMAIN_NAMES,
    DOMAIN_SUBGRAPH_FILES,
    MASK_56_BITS,
    FederatedSymbolRecord,
    NavigationClosureRecord,
    CrossDomainInterfaceRecord,
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
    FEDERATED_SCHEMA_SQL_PATH,
)


class TestDomainEnumeration:
    """領域代碼與檔名映射測試"""

    def test_domain_enum_values(self):
        expected = {
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
            10: "bridge",
        }
        for d_id, name in expected.items():
            assert DomainID(d_id).name.lower() == name or (d_id in DOMAIN_NAMES and DOMAIN_NAMES[d_id] == name)
            assert parse_domain_id(name) == d_id
            assert parse_domain_id(d_id) == d_id
            assert get_domain_name(d_id) == name

    def test_domain_subgraph_files(self):
        assert get_subgraph_filename(DomainID.FOUNDATION) == "00_foundation_kb.sqlite"
        assert get_subgraph_filename(DomainID.STRUCTURAL) == "01_structural_kb.sqlite"
        assert get_subgraph_filename(DomainID.FLUIDS) == "02_fluids_kb.sqlite"
        assert get_subgraph_filename(DomainID.ELECTROMAGNETICS) == "03_electromagnetics_kb.sqlite"
        assert get_subgraph_filename(DomainID.OPTICS) == "04_optics_kb.sqlite"
        assert get_subgraph_filename(DomainID.THERMAL) == "05_thermal_kb.sqlite"
        assert get_subgraph_filename(DomainID.MULTIBODY) == "06_multibody_kb.sqlite"
        assert get_subgraph_filename(DomainID.PARTICLES) == "07_particles_kb.sqlite"
        assert get_subgraph_filename(DomainID.MATERIALS) == "08_materials_kb.sqlite"
        assert get_subgraph_filename(DomainID.FRAMEWORK) == "09_framework_kb.sqlite"
        assert get_subgraph_filename(DomainID.BRIDGE) == "multiphysics_bridge.sqlite"

    def test_domain_aliases(self):
        assert parse_domain_id("mechanical") == DomainID.STRUCTURAL
        assert parse_domain_id("fluent") == DomainID.FLUIDS
        assert parse_domain_id("spaceclaim") == DomainID.FRAMEWORK


class TestCanonicalURI:
    """Canonical URI 產生與解析測試"""

    def test_create_and_parse_canonical_uri(self):
        uri = create_canonical_uri(
            domain="structural",
            namespace="mechanical",
            fqn="Ansys.ACT.Automation.Mechanical.Analysis",
            arity=0,
        )
        assert uri == "ansys://structural/mechanical/Ansys.ACT.Automation.Mechanical.Analysis#0"

        parsed = parse_canonical_uri(uri)
        assert parsed["domain"] == "structural"
        assert parsed["namespace"] == "mechanical"
        assert parsed["fqn"] == "Ansys.ACT.Automation.Mechanical.Analysis"
        assert parsed["arity"] == 0

    def test_canonical_uri_without_namespace(self):
        uri = create_canonical_uri(
            domain="foundation",
            namespace="",
            fqn="Ansys.Core.BaseEntity",
            arity=2,
        )
        assert uri == "ansys://foundation/Ansys.Core.BaseEntity#2"

        parsed = parse_canonical_uri(uri)
        assert parsed["domain"] == "foundation"
        assert parsed["namespace"] == ""
        assert parsed["fqn"] == "Ansys.Core.BaseEntity"
        assert parsed["arity"] == 2


class TestBitPartitionedUID:
    """64-bit 位元分區 UID 與 O(1) 路由測試"""

    def test_uid_generation_and_routing(self):
        for d_id in range(11):
            uri = f"ansys://{DOMAIN_NAMES[d_id]}/test/Entity#{d_id}"
            uid = generate_symbol_uid(d_id, uri)

            # 驗證 64-bit 範圍且為正整數
            assert 0 <= uid < (1 << 63)

            # 驗證 O(1) 路由精確度
            routed_domain_id = extract_domain_id(uid)
            assert routed_domain_id == d_id

            # 驗證子圖檔名解析
            filename = get_subgraph_filename(uid)
            assert filename == DOMAIN_SUBGRAPH_FILES[d_id]

            # 驗證 56-bit hash 取出
            local_hash = extract_local_hash(uid)
            assert 0 <= local_hash <= MASK_56_BITS
            assert uid == (d_id << 56) | local_hash

    def test_step_by_step_uid_creation(self):
        uid = create_symbol_uid(
            domain="structural",
            namespace="mechanical",
            fqn="Ansys.ACT.Automation.Mechanical.Model",
            arity=0,
        )
        assert extract_domain_id(uid) == DomainID.STRUCTURAL
        assert get_domain_name(uid) == "structural"
        assert get_subgraph_filename(uid) == "01_structural_kb.sqlite"

    def test_hash56_fallback_consistency(self):
        uri = "ansys://fluids/fluent/Solver/iterate#1"
        h56 = compute_uri_hash56(uri)
        assert 0 <= h56 <= MASK_56_BITS
        # 相同 URI 重複計算具備確定性
        assert compute_uri_hash56(uri) == h56


class TestSQLiteSchemas:
    """SQLite DDL 與 WITHOUT ROWID 行為驗證"""

    def test_federated_schema_file_exists(self):
        assert FEDERATED_SCHEMA_SQL_PATH.is_file()
        content = FEDERATED_SCHEMA_SQL_PATH.read_text(encoding="utf-8")
        assert "CREATE TABLE IF NOT EXISTS symbols" in content
        assert "CREATE TABLE IF NOT EXISTS api_navigation_closure" in content
        assert "CREATE TABLE IF NOT EXISTS cross_domain_interfaces" in content
        assert "WITHOUT ROWID" in content

    def test_subgraph_database_crud(self):
        conn = sqlite3.connect(":memory:")
        init_subgraph_database(conn)

        # 驗證 symbols 表寫入與查詢
        uid = create_symbol_uid("thermal", "icepak", "Ansys.Icepak.CadModel", 0)
        rec = FederatedSymbolRecord(
            symbol_uid=uid,
            domain_id=DomainID.THERMAL,
            canonical_uri="ansys://thermal/icepak/Ansys.Icepak.CadModel#0",
            fqn="Ansys.Icepak.CadModel",
            symbol_kind="Class",
            return_type_uid=None,
            is_root_entry=1,
            is_hub_anchor=1,
            l0_summary_json='{"desc": "Icepak CAD Model"}',
            l1_signature_json='{"props": ["Name", "Bodies"]}',
        )

        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO symbols (
                symbol_uid, domain_id, canonical_uri, fqn, symbol_kind,
                return_type_uid, is_root_entry, is_hub_anchor,
                l0_summary_json, l1_signature_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rec.symbol_uid, rec.domain_id, rec.canonical_uri, rec.fqn, rec.symbol_kind,
                rec.return_type_uid, rec.is_root_entry, rec.is_hub_anchor,
                rec.l0_summary_json, rec.l1_signature_json
            ),
        )

        cursor.execute("SELECT symbol_uid, domain_id, fqn, is_hub_anchor FROM symbols WHERE symbol_uid = ?", (uid,))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == uid
        assert row[1] == DomainID.THERMAL
        assert row[2] == "Ansys.Icepak.CadModel"
        assert row[3] == 1

        # 驗證 api_navigation_closure 表寫入與索引覆蓋查詢
        target_uid = create_symbol_uid("thermal", "icepak", "Ansys.Icepak.CadModel.Solve", 0)
        closure = NavigationClosureRecord(
            from_uid=uid,
            to_uid=target_uid,
            path_semantics="calls_method",
            path_hash=12345,
            hop_count=1,
            is_to_hub=1,
            edge_chain_json='[{"rel": "invokes"}]',
        )
        cursor.execute(
            """
            INSERT INTO api_navigation_closure (
                from_uid, to_uid, path_semantics, path_hash, hop_count, is_to_hub, edge_chain_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                closure.from_uid, closure.to_uid, closure.path_semantics,
                closure.path_hash, closure.hop_count, closure.is_to_hub, closure.edge_chain_json
            ),
        )

        cursor.execute(
            "SELECT to_uid, hop_count FROM api_navigation_closure WHERE from_uid = ? AND is_to_hub = 1",
            (uid,),
        )
        c_row = cursor.fetchone()
        assert c_row is not None
        assert c_row[0] == target_uid
        assert c_row[1] == 1

    def test_bridge_database_crud(self):
        conn = sqlite3.connect(":memory:")
        init_bridge_database(conn)

        s_uid = create_symbol_uid("structural", "mechanical", "Ansys.ACT.StructuralAnalysis", 0)
        t_uid = create_symbol_uid("thermal", "icepak", "Ansys.Icepak.ThermalModel", 0)

        bridge_rec = CrossDomainInterfaceRecord(
            interface_id=None,
            source_domain_id=DomainID.STRUCTURAL,
            source_uid=s_uid,
            target_domain_id=DomainID.THERMAL,
            target_uid=t_uid,
            coupling_type="one_way_thermal_stress",
            mapping_contract_json='{"temp_field": "body_temperatures"}',
        )

        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO cross_domain_interfaces (
                source_domain_id, source_uid, target_domain_id, target_uid, coupling_type, mapping_contract_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                bridge_rec.source_domain_id, bridge_rec.source_uid,
                bridge_rec.target_domain_id, bridge_rec.target_uid,
                bridge_rec.coupling_type, bridge_rec.mapping_contract_json,
            ),
        )

        cursor.execute("SELECT source_domain_id, target_domain_id, coupling_type FROM cross_domain_interfaces WHERE source_uid = ?", (s_uid,))
        b_row = cursor.fetchone()
        assert b_row is not None
        assert b_row[0] == DomainID.STRUCTURAL
        assert b_row[1] == DomainID.THERMAL
        assert b_row[2] == "one_way_thermal_stress"
