"""
API Inventory 結構與資料完整性單元測試
驗證 SpaceClaim、Mechanical、optiSLang、LS-DYNA 四大模組 API 導出檔案及 API_CATALOG.md。
"""
import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_DIR = REPO_ROOT / "docs" / "api_inventory"

def test_api_catalog_markdown_exists():
    catalog_path = INVENTORY_DIR / "API_CATALOG.md"
    assert catalog_path.exists(), "API_CATALOG.md 必須存在"
    content = catalog_path.read_text(encoding="utf-8")
    assert "ANSYS 機械與各模組 API" in content or "ANSYS 四大模組 API" in content
    assert "mechanical_api.json" in content
    assert "spaceclaim_api.json" in content
    assert "optislang_api.json" in content
    assert "lsdyna_api.json" in content

def test_mechanical_api_json_integrity():
    mech_path = INVENTORY_DIR / "mechanical_api.json"
    assert mech_path.exists(), "mechanical_api.json 必須存在"
    assert mech_path.stat().st_size > 1_000_000, "mechanical_api.json 大小應大於 1MB"

    with open(mech_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["module"] == "Ansys.Mechanical"
    assert "statistics" in data
    stats = data["statistics"]
    assert stats["total_classes"] > 1000, "Mechanical 類別數應大於 1000"
    assert stats["total_methods"] > 30000, "Mechanical 方法數應大於 30000"
    assert stats["total_properties"] > 30000, "Mechanical 屬性數應大於 30000"
    assert "modules" in data
    assert len(data["modules"]) > 50

def test_spaceclaim_api_json_integrity():
    sc_path = INVENTORY_DIR / "spaceclaim_api.json"
    assert sc_path.exists(), "spaceclaim_api.json 必須存在"
    assert sc_path.stat().st_size > 500_000, "spaceclaim_api.json 大小應大於 500KB"

    with open(sc_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["module"] == "SpaceClaim"
    assert "statistics" in data
    stats = data["statistics"]
    assert stats["total_types"] > 1000, "SpaceClaim 型別數應大於 1000"
    assert stats["total_methods"] > 2000, "SpaceClaim 方法數應大於 2000"
    assert stats["total_properties"] > 1000, "SpaceClaim 屬性數應大於 1000"
    assert "classes" in data
    assert "enums" in data

def test_optislang_api_json_integrity():
    osl_path = INVENTORY_DIR / "optislang_api.json"
    assert osl_path.exists(), "optislang_api.json 必須存在"
    assert osl_path.stat().st_size > 500_000, "optislang_api.json 大小應大於 500KB"

    with open(osl_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["module"] == "ansys.optislang.core"
    assert "statistics" in data
    stats = data["statistics"]
    assert stats["total_classes"] > 100, "optiSLang 類別數應大於 100"
    assert stats["total_methods"] > 1000, "optiSLang 方法數應大於 1000"
    assert "built_in_scripting_categories" in data
    assert len(data["built_in_scripting_categories"]) > 5

def test_lsdyna_api_json_integrity():
    dyna_path = INVENTORY_DIR / "lsdyna_api.json"
    assert dyna_path.exists(), "lsdyna_api.json 必須存在"

    with open(dyna_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "components" in data
    assert "ls_prepost_python" in data["components"]
    assert "ls_prepost_scl" in data["components"]
    assert "ls_dyna_keywords" in data["components"]
    stats = data["statistics"]
    assert stats["total_defined_keywords"] >= 30, "LS-DYNA 定義關鍵字數應大於等於 30"
