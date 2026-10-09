"""
API 知識庫建置與資料結構單元測試
"""
import sqlite3
import pytest
from pathlib import Path

from ansys_unified_mcp.analytics.apikb import config as cfg
from ansys_unified_mcp.analytics.apikb.build import split_camel_case, clean_type_name, build_database

def test_split_camel_case():
    assert split_camel_case("AddFixedSupport") == "add fixed support"
    assert split_camel_case("SCLGetDataCenterFloat") == "scl get data center float"
    assert split_camel_case("create_node") == "create node"

def test_clean_type_name():
    assert clean_type_name("typing.Optional[Ansys.ACT.Automation.Mechanical.Analysis]") == "Analysis"
    assert clean_type_name("SpaceClaim.Api.V251.Scripting.Part") == "Part"
    assert clean_type_name("None") == ""

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
