"""
API 知識庫 MCP 工具層調用測試
"""
import pytest
pytest.importorskip("fastmcp", reason="FastMCP requires Python >= 3.10 environment")

from ansys_unified_mcp.tools.apikb_tools import api_search, api_get, api_path, api_validate_script

def test_api_search_tool():
    res = api_search("fixed support", product="mechanical", top_k=3)
    assert res["ok"] is True
    assert "results" in res
    assert len(res["results"]) > 0

def test_api_get_tool():
    res = api_get("Analysis")
    assert res["ok"] is True
    assert res["found"] is True
    assert "symbol" in res

def test_api_path_tool():
    res = api_path("Analysis", "EquivalentStress")
    assert res["ok"] is True
    assert res["paths_count"] > 0
    assert len(res["paths"]) > 0

def test_api_validate_script_tool():
    valid_code = "analysis = ExtAPI.DataModel.Project.Model.Analyses[0]\nanalysis.AddFixedSupport()"
    res = api_validate_script(valid_code, "mechanical")
    assert res["ok"] is True
    assert res["valid"] is True
