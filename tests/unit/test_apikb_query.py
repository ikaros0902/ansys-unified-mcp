"""
API 知識庫查詢引擎單元測試
"""
import pytest
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
