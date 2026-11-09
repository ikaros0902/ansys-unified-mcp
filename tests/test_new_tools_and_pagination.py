"""Unit and Canary tests for enhanced MCP tools and pagination.

Covers:
- list_ansys_docs summary and pagination
- ans_get_knowledge_dictionary overview and topic queries
- api_validate_script multi-product and canary failure validation
- ans_search_official_examples search ranking
"""

from __future__ import annotations

import pytest

from ansys_unified_mcp.tools.docs_tools import (
    list_ansys_docs,
    ans_get_knowledge_dictionary,
)
from ansys_unified_mcp.tools.apikb_tools import (
    api_validate_script,
    ans_search_official_examples,
)


def test_list_ansys_docs_summary_mode():
    """Verify list_ansys_docs returns lightweight aggregate summary without overflow."""
    res = list_ansys_docs(summary_only=True)
    assert res.get("ok") is True
    assert res.get("summary_only") is True
    assert res.get("total_docs", 0) > 500_000
    assert len(res.get("product_summary", [])) > 20
    assert len(res.get("category_summary", [])) > 0


def test_list_ansys_docs_pagination():
    """Verify list_ansys_docs paginates cleanly when filtered."""
    res = list_ansys_docs(product="fluent", limit=5, offset=0, summary_only=False)
    assert res.get("ok") is True
    assert res.get("summary_only") is False
    assert res.get("count") <= 5
    assert len(res.get("docs", [])) == res.get("count")
    assert res.get("total_matches", 0) > 0


def test_ans_get_knowledge_dictionary_list():
    """Verify ans_get_knowledge_dictionary lists all 60+ product dictionaries."""
    res = ans_get_knowledge_dictionary()
    assert res.get("ok") is True
    assert res.get("total_products", 0) >= 60
    assert len(res.get("dictionaries", [])) >= 60


def test_ans_get_knowledge_dictionary_specific_product():
    """Verify ans_get_knowledge_dictionary retrieves product overview and topics."""
    res = ans_get_knowledge_dictionary(product="cfx")
    assert res.get("ok") is True
    assert res.get("product") == "cfx"
    assert res.get("topics_count", 0) > 0
    assert len(res.get("topics", [])) == res.get("topics_count")


def test_ans_get_knowledge_dictionary_specific_topic():
    """Verify ans_get_knowledge_dictionary retrieves specific topic section content."""
    res = ans_get_knowledge_dictionary(product="mapdl", topic="PyMAPDL SDK")
    assert res.get("ok") is True
    assert res.get("product") == "mapdl"
    assert "PyMAPDL" in res.get("matched_text", "")


def test_api_validate_script_canary():
    """Canary test: verify api_validate_script catches hallucinated methods."""
    # Valid call
    valid_res = api_validate_script("ExtAPI.DataModel.Project.Model.AddFixedSupport()", "mechanical")
    assert valid_res.get("ok") is True

    # Hallucinated call
    fake_res = api_validate_script("ExtAPI.DataModel.Project.Model.NonExistentHallucinatedMethodXYZ()", "mechanical")
    assert fake_res.get("ok") is True
    assert fake_res.get("valid") is False
    assert fake_res.get("error_count", 0) > 0


def test_ans_search_official_examples():
    """Verify ans_search_official_examples searches and returns ranked examples."""
    res = ans_search_official_examples(query="mixing elbow", product="fluent")
    assert res.get("ok") is True
    assert res.get("count", 0) >= 1
    top_ex = res["results"][0]["example"]
    assert "elbow" in top_ex["title"].lower() or "elbow" in top_ex["id"].lower()
