"""
API 知識庫 MCP 工具層調用測試
"""
import pytest
pytest.importorskip("fastmcp", reason="FastMCP requires Python >= 3.10 environment")

from ansys_unified_mcp.tools import apikb_tools
from ansys_unified_mcp.tools.apikb_tools import (
    api_search,
    api_get,
    api_path,
    api_validate_script,
    api_federated_path,
    api_federated_search,
    api_cross_bridge,
)


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


def test_api_get_tool_selects_optislang_core_snapshot():
    res = api_get(
        "ansys.optislang.core.optislang.Optislang",
        include="members",
        product="optislang_core",
        interface="PyOptiSLang 1.6.0 Optislang client",
    )

    assert res["ok"] is True
    assert res["found"] is True
    assert res["symbol"]["product"] == "optislang_core"
    assert res["symbol"]["source"]["sdk_version"] == "1.6.0"


def test_api_get_tool_reports_ambiguous_source_candidates(monkeypatch):
    candidates = [
        {"product": "optislang", "release": "unknown", "interface": "PyOptiSLang and scripting API"},
        {"product": "optislang_core", "release": "unknown", "interface": "PyOptiSLang 1.6.0 Optislang client"},
    ]
    monkeypatch.setattr(
        apikb_tools.kb_query,
        "get",
        lambda **kwargs: {"ambiguous": True, "candidates": candidates},
    )

    res = api_get("ansys.optislang.core.optislang.Optislang")

    assert res["ok"] is False
    assert res["found"] is False
    assert res["ambiguous"] is True
    assert res["candidates"] == candidates


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


def test_api_federated_tools_graceful():
    """驗證聯邦 MCP 工具在空/無子圖環境下具備安全優雅降級行為"""
    res_path = api_federated_path(from_uid=1, to_uid=2)
    assert res_path["ok"] is True
    assert "paths" in res_path

    res_search = api_federated_search(query="NonExistentSymbol")
    assert res_search["ok"] is True
    assert "results" in res_search

    res_bridge = api_cross_bridge(coupling_type="FSI")
    assert res_bridge["ok"] is True
    assert "bridges" in res_bridge
