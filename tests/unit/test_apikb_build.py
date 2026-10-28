"""
API 知識庫建置與資料結構單元測試
"""

import json
import sqlite3
import pytest
from pathlib import Path

from ansys_unified_mcp.analytics.apikb import config as cfg
from ansys_unified_mcp.analytics.apikb.build import (
    split_camel_case,
    clean_type_name,
    build_database,
    _schema_is_current,
    _ensure_previous_sources_available,
)
from ansys_unified_mcp.analytics.apikb.query import get as get_symbol, search as search_symbols


def test_split_camel_case():
    assert split_camel_case("AddFixedSupport") == "add fixed support"
    assert split_camel_case("SCLGetDataCenterFloat") == "scl get data center float"
    assert split_camel_case("create_node") == "create node"


def test_clean_type_name():
    assert (
        clean_type_name("typing.Optional[Ansys.ACT.Automation.Mechanical.Analysis]") == "Analysis"
    )
    assert clean_type_name("SpaceClaim.Api.V251.Scripting.Part") == "Part"
    assert clean_type_name("None") == ""


def test_same_symbol_is_ingested_per_release_without_cross_release_edges(tmp_path, monkeypatch):
    docs = tmp_path / "api_inventory"
    docs.mkdir()
    for release in ("v251", "v261"):
        (docs / f"mechanical_api_{release}.json").write_text(
            '{"version":"' + release + '","modules":{"Ansys.Test":{"classes":{'
            '"Node":{"doc":"node","methods":[{"name":"GetChild",'
            '"parameters":[],"return_type":"Ansys.Test.Child",'
            '"doc":"' + release + ' method documentation"}]},'
            '"Child":{"doc":"child","methods":[],"properties":[]}'
            "}}}}",
            encoding="utf-8",
        )
    monkeypatch.setattr(cfg, "DOCS_DIR", docs)
    monkeypatch.setattr(cfg, "SOURCES", {"mechanical": docs / "mechanical_api_v251.json"})
    monkeypatch.setattr(cfg, "DB_DIR", tmp_path / "db")
    monkeypatch.setattr(cfg, "DB_PATH", tmp_path / "db" / "api.sqlite")
    monkeypatch.setattr(cfg, "SCHEMA_PATH", cfg.SCHEMA_PATH)

    result = build_database(force=True)
    assert result["status"] == "success"
    conn = sqlite3.connect(str(cfg.DB_PATH))
    try:
        rows = conn.execute(
            "SELECT release, source_id FROM symbols WHERE fqname='Ansys.Test.Node' ORDER BY release"
        ).fetchall()
        assert [row[0] for row in rows] == ["v251", "v261"]
        edge_rows = conn.execute(
            "SELECT s.release, d.release FROM edges e "
            "JOIN symbols s ON s.id=e.src_symbol_id "
            "JOIN symbols d ON d.id=e.dst_symbol_id"
        ).fetchall()
        assert edge_rows
        assert all(src == dst for src, dst in edge_rows)
        source_count = conn.execute("SELECT count(*) FROM api_sources").fetchone()[0]
        assert source_count == 2
    finally:
        conn.close()
    v251 = get_symbol("Ansys.Test.Node", include=("members",), product="mechanical", release="v251")
    v261 = get_symbol("Ansys.Test.Node", include=("members",), product="mechanical", release="v261")
    assert v251["members"][0]["doc"] == "v251 method documentation"
    assert v261["members"][0]["doc"] == "v261 method documentation"

    indexed_bytes = cfg.DB_PATH.read_bytes()
    (docs / "mechanical_api_v261.json").unlink()
    with pytest.raises(RuntimeError, match="既有 API 來源快照暫時不可用"):
        build_database(force=True)
    assert cfg.DB_PATH.read_bytes() == indexed_bytes


def test_mapdl_snapshot_indexes_sdk_version_members_and_launcher(tmp_path, monkeypatch):
    docs = tmp_path / "api_inventory"
    docs.mkdir()
    snapshot = {
        "version": "unknown",
        "sdk_version": "0.74.1",
        "modules": {
            "ansys.mapdl.core.mapdl_grpc": {
                "classes": {
                    "MapdlGrpc": {
                        "doc": "PyMAPDL client",
                        "methods": [
                            {
                                "name": "run",
                                "signature": "(self, value=1, *, mode='fast')",
                                "doc": "Run a command.",
                            }
                        ],
                        "properties": [{"name": "busy", "type": "bool", "doc": "Server state."}],
                    }
                },
                "functions": [],
            },
            "ansys.mapdl.core.launcher": {
                "classes": {},
                "functions": [
                    {
                        "name": "launch_mapdl",
                        "signature": "(exec_file=None)",
                        "doc": "Launch MAPDL.",
                    }
                ],
            },
        },
    }
    path = docs / "mapdl_api.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")
    monkeypatch.setattr(cfg, "DOCS_DIR", docs)
    monkeypatch.setattr(cfg, "SOURCES", {"mapdl": path})
    monkeypatch.setattr(cfg, "DB_DIR", tmp_path / "db")
    monkeypatch.setattr(cfg, "DB_PATH", tmp_path / "db" / "api.sqlite")

    result = build_database(force=True)
    assert result["status"] == "success"
    client = get_symbol(
        "ansys.mapdl.core.mapdl_grpc.MapdlGrpc", include=("members",), product="mapdl"
    )
    assert {m["name"]: m["signature"] for m in client["members"]} == {
        "run": "(self, value=1, *, mode='fast')",
        "busy": ": bool",
    }
    launcher = get_symbol("ansys.mapdl.core.launcher.launch_mapdl", product="mapdl")
    assert launcher["kind"] == "module_function"
    conn = sqlite3.connect(str(cfg.DB_PATH))
    try:
        source = conn.execute(
            "SELECT release, sdk_version, source_path FROM api_sources WHERE product='mapdl'"
        ).fetchone()
        assert source[:2] == ("unknown (product release not recorded)", "0.74.1")
        assert source[2].endswith("api_inventory/mapdl_api.json")
        assert not Path(source[2]).is_absolute()
    finally:
        conn.close()


def test_rea_visibility_and_method_access_are_labeled_static(tmp_path, monkeypatch):
    docs = tmp_path / "api_inventory"
    docs.mkdir()
    snapshot = {
        "version": "2025 R1 (v251)",
        "modules": {"Ansys.ACT.Core": {"classes": {
            "SampleType": {
                "visibility": "public",
                "methods": [{"name": "Run", "signature": "()", "doc": "REA MethodDef; access=public; flags=150"}],
                "properties": [],
            },
            "OtherSampleType": {
                "visibility": "public",
                "methods": [{"name": "Run", "signature": "()", "doc": "REA MethodDef; access=family-and-assembly; flags=6276"}],
                "properties": [],
            }
        }, "functions": []}},
        "python_modules": [],
        "sources": {"assembly": {"sha256": "assembly-hash", "rea_evidence_id": "ev_test"}},
    }
    path = docs / "act_core_rea_api.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")
    monkeypatch.setattr(cfg, "DOCS_DIR", docs)
    monkeypatch.setattr(cfg, "SOURCES", {"act_core_rea": path})
    monkeypatch.setattr(cfg, "DB_DIR", tmp_path / "db")
    monkeypatch.setattr(cfg, "DB_PATH", tmp_path / "db" / "api.sqlite")

    assert build_database(force=True)["status"] == "success"
    result = search_symbols("SampleType", product="act_core_rea")[0]
    assert result["public_status"] == "public"
    assert result["validation_status"] == "static_metadata_only; runtime_unverified"
    assert result["source"]["artifact_sha256"] == "assembly-hash"
    assert result["source"]["rea_evidence_id"] == "ev_test"
    symbol = get_symbol("Ansys.ACT.Core.SampleType", product="act_core_rea", include=("members",))
    assert symbol["public_status"] == "public"
    assert symbol["source"]["artifact_sha256"] == "assembly-hash"
    assert symbol["source"]["rea_evidence_id"] == "ev_test"
    method = next(item for item in symbol["members"] if item["name"] == "Run")
    assert method["public_status"] == "public"
    assert method["validation_status"] == "static_metadata_only; runtime_unverified"
    other = get_symbol("Ansys.ACT.Core.OtherSampleType", product="act_core_rea", include=("members",))
    other_method = next(item for item in other["members"] if item["name"] == "Run")
    assert other_method["public_status"] == "family-and-assembly"


def test_empty_build_does_not_replace_existing_database(tmp_path, monkeypatch):
    db_path = tmp_path / "db" / "api.sqlite"
    db_path.parent.mkdir()
    original = b"existing-index-sentinel"
    db_path.write_bytes(original)
    monkeypatch.setattr(cfg, "DB_DIR", db_path.parent)
    monkeypatch.setattr(cfg, "DB_PATH", db_path)
    monkeypatch.setattr(cfg, "source_snapshots", lambda: [])

    with pytest.raises(RuntimeError, match="promote blocked"):
        build_database(force=True)
    assert db_path.read_bytes() == original


def test_apikb_database_integrity():
    # 確保資料庫已建置且有效
    assert cfg.DB_PATH.exists(), "api_kb.sqlite 必須存在"
    conn = sqlite3.connect(str(cfg.DB_PATH))
    cur = conn.cursor()

    # 檢查 symbols 數量
    cur.execute("SELECT count(*) FROM symbols")
    sym_count = cur.fetchone()[0]
    assert sym_count > 2500, f"符號數量過少: {sym_count}"

    # 檢查 members 數量與去重效果
    cur.execute("SELECT count(*) FROM members")
    mem_count = cur.fetchone()[0]
    assert mem_count > 70000, f"成員去重後數量過少: {mem_count}"

    # 檢查 edges 數量
    cur.execute("SELECT count(*) FROM edges")
    edge_count = cur.fetchone()[0]
    assert edge_count > 10000, f"型別關係邊數量過少: {edge_count}"

    # 檢查 search_fts 虛擬表
    cur.execute("SELECT count(*) FROM search_fts")
    fts_count = cur.fetchone()[0]
    assert fts_count > 10000, f"全文檢索項目過少: {fts_count}"

    conn.close()



def test_schema_requires_rea_artifact_identity_columns(tmp_path):
    current = tmp_path / "current.sqlite"
    with sqlite3.connect(current) as connection:
        connection.executescript(cfg.SCHEMA_PATH.read_text(encoding="utf-8"))
        connection.execute(
            "INSERT INTO api_kb_meta (key, value) VALUES ('index_version', ?)",
            (cfg.APIKB_INDEX_VERSION,),
        )
    assert _schema_is_current(current)

    stale_index = tmp_path / "stale-index.sqlite"
    with sqlite3.connect(stale_index) as connection:
        connection.executescript(cfg.SCHEMA_PATH.read_text(encoding="utf-8"))
        connection.execute("INSERT INTO api_kb_meta (key, value) VALUES ('index_version', '1')")
    assert not _schema_is_current(stale_index)

    legacy = tmp_path / "legacy.sqlite"
    with sqlite3.connect(legacy) as connection:
        connection.executescript(
            "CREATE TABLE symbols (release TEXT, interface TEXT, source_id INTEGER);"
            "CREATE TABLE search_fts (release TEXT, interface TEXT, source_id INTEGER);"
            "CREATE TABLE api_sources (source_path TEXT, sha256 TEXT);"
        )
    assert not _schema_is_current(legacy)


def test_previous_sources_resolve_from_repo_and_match_external_hashes(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    internal = repo / "docs" / "api_inventory" / "internal.json"
    internal.parent.mkdir(parents=True)
    internal.write_text(json.dumps({"version": "v251", "sources": {"assembly": {"sha256": "direct-assembly-hash"}}}), encoding="utf-8")
    external = tmp_path / "external.json"
    external.write_text('{"version":"v251"}', encoding="utf-8")

    monkeypatch.setattr(cfg, "REPO_ROOT", repo)
    db_path = tmp_path / "api.sqlite"
    monkeypatch.setattr(cfg, "DB_PATH", db_path)
    internal_meta = cfg.source_metadata("internal", internal)
    external_meta = cfg.source_metadata("external", external)
    assert internal_meta["artifact_sha256"] == "direct-assembly-hash"
    assert internal_meta["rea_evidence_id"] == ""

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "CREATE TABLE api_sources (source_path TEXT, product TEXT, release TEXT, sha256 TEXT)"
        )
        connection.executemany(
            "INSERT INTO api_sources VALUES (?, ?, ?, ?)",
            [
                (internal_meta["source_path"], "internal", internal_meta["release"], internal_meta["sha256"]),
                (external_meta["source_path"], "external", external_meta["release"], external_meta["sha256"]),
            ],
        )

    monkeypatch.chdir(tmp_path)
    _ensure_previous_sources_available([("internal", internal), ("external", external)])



def test_spaceclaim_core_rea_candidate_is_indexed_with_artifact_evidence(tmp_path, monkeypatch):
    docs = tmp_path / "api_inventory"
    docs.mkdir()
    snapshot = {
        "version": "2025 R1 (v251)",
        "sources": {"assembly": {"sha256": "spaceclaim-core-hash", "rea_evidence_id": "ev_spaceclaim_core"}},
        "modules": {
            "SpaceClaim.Api.V251": {
                "doc": "Namespace from REA metadata.",
                "classes": {
                    "Plane": {
                        "name": "Plane",
                        "doc": "REA TypeDef; visibility=public; support unverified.",
                        "methods": [{"name": "Create", "signature": "(Point) -> Plane", "doc": "REA MethodDef; access=public; flags=150"}],
                        "properties": [],
                    }
                },
                "functions": [],
            }
        },
    }
    path = docs / "spaceclaim_core_rea_api.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")
    monkeypatch.setattr(cfg, "DOCS_DIR", docs)
    monkeypatch.setattr(cfg, "SOURCES", {"spaceclaim_core_rea": path})
    monkeypatch.setattr(cfg, "DB_DIR", tmp_path / "db")
    monkeypatch.setattr(cfg, "DB_PATH", tmp_path / "db" / "api.sqlite")

    assert build_database(force=True)["status"] == "success"
    result = search_symbols("Create", product="spaceclaim_core_rea")[0]
    assert result["signature"] == "(Point) -> Plane"
    assert result["validation_status"] == "static_metadata_only; runtime_unverified"
    assert result["source"]["artifact_sha256"] == "spaceclaim-core-hash"
    assert result["source"]["rea_evidence_id"] == "ev_spaceclaim_core"
