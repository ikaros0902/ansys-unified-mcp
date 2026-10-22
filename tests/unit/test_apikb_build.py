"""
API 知識庫建置與資料結構單元測試
"""
import sqlite3
import pytest
from pathlib import Path

from ansys_unified_mcp.analytics.apikb import config as cfg
from ansys_unified_mcp.analytics.apikb.build import split_camel_case, clean_type_name, build_database
from ansys_unified_mcp.analytics.apikb.query import get as get_symbol

def test_split_camel_case():
    assert split_camel_case("AddFixedSupport") == "add fixed support"
    assert split_camel_case("SCLGetDataCenterFloat") == "scl get data center float"
    assert split_camel_case("create_node") == "create node"

def test_clean_type_name():
    assert clean_type_name("typing.Optional[Ansys.ACT.Automation.Mechanical.Analysis]") == "Analysis"
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
            '}}}}', encoding="utf-8"
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
    assert 5000 < mem_count < 25000, f"成員去重後數量異常: {mem_count}"

    # 檢查 edges 數量
    cur.execute("SELECT count(*) FROM edges")
    edge_count = cur.fetchone()[0]
    assert edge_count > 10000, f"型別關係邊數量過少: {edge_count}"

    # 檢查 search_fts 虛擬表
    cur.execute("SELECT count(*) FROM search_fts")
    fts_count = cur.fetchone()[0]
    assert fts_count > 10000, f"全文檢索項目過少: {fts_count}"

    conn.close()
