"""
API 知識庫查詢引擎單元測試
"""
import json
import sqlite3

import pytest
from ansys_unified_mcp.analytics.apikb import config as cfg
from ansys_unified_mcp.analytics.apikb.build import build_database
from ansys_unified_mcp.analytics.apikb.query import search, get, path

def test_search_by_name_and_split():
    # 搜尋 "fixed support"
    results = search("fixed support", top_k=5)
    assert len(results) > 0
    names = [r["name"] for r in results]
    assert any("FixedSupport" in n for n in names)

def test_search_with_product_filter():
    # 限制 spaceclaim 產品
    sc_results = search("Part", product="spaceclaim", top_k=5)
    assert len(sc_results) > 0
    for r in sc_results:
        assert r["product"] == "spaceclaim"

def test_get_symbol_detail():
    # 查詢 Analysis 類別
    detail = get("Analysis")
    assert detail is not None
    assert detail["name"] == "Analysis"
    assert len(detail["members"]) > 0
    # 檢查是否包含出邊
    assert len(detail["edges_out"]) > 0

def test_path_navigation():
    # 尋找 Analysis 到 EquivalentStress 的路徑
    paths = path("Analysis", "EquivalentStress")
    assert len(paths) > 0
    best_path = paths[0]
    assert "Analysis" in best_path["nodes"]
    assert "EquivalentStress" in best_path["nodes"]
    assert any("Solution" in n for n in best_path["nodes"])


def test_existing_kb_rebuilds_when_a_snapshot_is_added(tmp_path, monkeypatch):
    docs = tmp_path / "api_inventory"
    docs.mkdir()
    mechanical = docs / "mechanical_api.json"
    mechanical.write_text(
        json.dumps({"version": "test", "modules": {"Ansys.Test": {"classes": {"Node": {"methods": []}}}}}),
        encoding="utf-8",
    )
    mapdl = docs / "mapdl_api.json"
    mapdl.write_text(
        json.dumps(
            {
                "version": "unknown",
                "sdk_version": "0.74.1",
                "modules": {
                    "ansys.mapdl.core.launcher": {
                        "classes": {},
                        "functions": [
                            {"name": "launch_mapdl", "signature": "(exec_file=None)", "doc": "Launch MAPDL."}
                        ],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(cfg, "DOCS_DIR", docs)
    monkeypatch.setattr(cfg, "SOURCES", {"mechanical": mechanical})
    monkeypatch.setattr(cfg, "DB_DIR", tmp_path / "db")
    monkeypatch.setattr(cfg, "DB_PATH", tmp_path / "db" / "api.sqlite")
    build_database(force=True)

    monkeypatch.setattr(cfg, "SOURCES", {"mechanical": mechanical, "mapdl": mapdl})
    results = search("launch_mapdl", product="mapdl", top_k=5)

    assert len(results) == 1
    assert results[0]["source"]["sdk_version"] == "0.74.1"
    monkeypatch.setitem(cfg.INTERFACES, "mapdl", "PyMAPDL test interface")
    results = search("launch_mapdl", product="mapdl", top_k=5)
    assert results[0]["interface"] == "PyMAPDL test interface"
    conn = sqlite3.connect(cfg.DB_PATH)
    try:
        assert conn.execute("SELECT count(*) FROM api_sources").fetchone()[0] == 2
        assert conn.execute("SELECT count(*) FROM symbols WHERE product='mapdl'").fetchone()[0] == 1
    finally:
        conn.close()
