"""
API Inventory 結構與資料完整性單元測試
驗證 SpaceClaim、Mechanical、optiSLang、LS-DYNA 與 PyMAPDL API 導出檔案及 API_CATALOG.md。
"""

import json
from pathlib import Path
import pytest

from scripts.api_extraction.extract_all_apis import _rea_payload

REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_DIR = REPO_ROOT / "docs" / "api_inventory"


def test_api_catalog_markdown_exists():
    catalog_path = INVENTORY_DIR / "API_CATALOG.md"
    assert catalog_path.exists(), "API_CATALOG.md 必須存在"
    content = catalog_path.read_text(encoding="utf-8")
    assert "(API Catalog)" in content
    assert "mechanical_api.json" in content
    assert "spaceclaim_api.json" in content
    assert "optislang_api.json" in content
    assert "lsdyna_api.json" in content
    assert "mapdl_api.json" in content
    assert "optislang_core_api.json" in content
    assert "PyOptiSLang Core" in content
    for snapshot in ("act_interfaces_rea_api.json", "lsdyna_interfaces_rea_api.json", "ansysem_coredotnet_rea_api.json", "additive_rea_api.json", "aqwa_addin_rea_api.json", "cfx_addin_rea_api.json", "fluent_addin_rea_api.json", "icepak_addin_rea_api.json", "meshing_addin_rea_api.json", "polyflow_addin_rea_api.json", "sherlock_addin_rea_api.json", "hfss_addin_rea_api.json"):
        assert snapshot in content


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


def test_mapdl_api_snapshot_records_bounded_static_evidence():
    path = INVENTORY_DIR / "mapdl_api.json"
    assert path.exists(), "mapdl_api.json 必須存在"
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["version"] == "unknown"
    assert data["sdk_package"] == "ansys-mapdl-core"
    assert data["sdk_version"] == "0.74.1"
    assert data["statistics"] == {
        "total_classes": 1,
        "total_methods": 27,
        "total_properties": 38,
        "total_functions": 1,
        "unresolved_members": 2,
    }
    assert {member["name"] for member in data["unresolved_members"]} == {
        "finish_job_on_exit",
        "remove_temp_dir_on_exit",
    }
    sdk_files = data["sources"]["sdk_files"]
    sdk_paths = {item["path"] for item in sdk_files}
    assert all(len(item["sha256"]) == 64 for item in sdk_files)
    mapdl_class = data["modules"]["ansys.mapdl.core.mapdl_grpc"]["classes"]["MapdlGrpc"]
    members = mapdl_class["methods"] + mapdl_class["properties"]
    assert len(members) == 65
    member_sources = {
        member[key]
        for member in members
        for key in ("sdk_source_path", "signature_source_path")
        if member.get(key)
    }
    assert member_sources <= sdk_paths
    assert {Path(item["path"]).name for item in sdk_files} >= {
        "mapdl_core.py",
        "mapdl_extended.py",
        "errors.py",
        "misc.py",
        "mapdl_grpc.py",
        "run_controls.py",
        "parameter_definition.py",
    }
    launcher = data["modules"]["ansys.mapdl.core.launcher"]["functions"][0]
    assert launcher["sdk_source_path"] in sdk_paths
    assert launcher["signature_source_path"] in sdk_paths
    assert len(data["sources"]["api_reference"]["sha256"]) == 64


def test_api_coverage_keeps_documentation_and_api_evidence_separate():
    coverage = json.loads((INVENTORY_DIR / "api_coverage.json").read_text(encoding="utf-8"))
    assert coverage["schema_version"] == 3
    assert coverage["sources"]["documentation_coverage"] == "docs/ANSYS_Document/_catalog/coverage.json"

    products = {item["product"]: item for item in coverage["products"]}
    mechanical = products["mechanical"]
    documentation = {item["release"]: item for item in mechanical["documentation_coverage"]}
    api_snapshot = next(
        item for item in mechanical["snapshots"] if "v251" in item["snapshot_version"]
    )

    assert "v251" not in documentation
    assert documentation["unknown"]["release_availability"] == "not_verified"
    assert documentation["v261"]["api_count"] == 0
    assert api_snapshot["rea_evidence"]["component"].startswith("Mechanical DataModel")
    assert api_snapshot["rea_evidence"]["path"] == "docs/api_inventory/REA_EVIDENCE.md"
    assert products["ansysem"]["snapshots"] == []
    assert products["ansysem"]["mapping_status"] == "product_component_evidence_only"
    assert products["ansysem"]["rea_evidence"]["version"] == "v251"
    assert products["ansysem"]["rea_evidence"]["component"].startswith("Ansys.Ansoft.CoreCOMScripting.dll")
    assert products["ansysem"]["rea_evidence"]["path"] == "docs/api_inventory/REA_EVIDENCE.md"
    assert products["dpf"]["rea_evidence"]["path"] == "docs/api_inventory/REA_EVIDENCE.md"
    assert "Ans.Dpf." in products["dpf"]["rea_evidence"]["component"]
    assert products["dpf"]["rea_evidence"]["version"] == "v251"
    assert products["cfx"]["rea_evidence"] == {
        "path": "docs/api_inventory/REA_EVIDENCE.md",
        "component": "Ans.CFX.CadApi.dll; Ans.CFX.CFXCore.dll",
        "version": "v251",
    }
    assert products["cfx"]["mapping_status"] in {"direct_product_id", "product_component_evidence_only"}
    assert products["aqwa"]["mapping_status"] == "product_component_evidence_only"
    assert products["aqwa"]["rea_evidence"]["component"] == "Ans.AQWA.Core.dll"
    assert products["hfss"]["mapping_status"] == "product_component_evidence_only"
    assert products["hfss"]["rea_evidence"]["component"] == "Ans.Ansoft.HFSSAddinPlugin.dll"


def test_coverage_report_preserves_curated_rea_evidence(tmp_path, monkeypatch):
    import importlib.util
    import json
    from pathlib import Path

    module_path = Path(__file__).resolve().parents[2] / "scripts" / "api_extraction" / "build_coverage_report.py"
    spec = importlib.util.spec_from_file_location("build_coverage_report_under_test", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    output_path = tmp_path / "api_coverage.json"
    output_path.write_text(
        json.dumps(
            {
                "products": [
                    {
                        "product": "acp",
                        "rea_evidence": {
                            "path": "docs/api_inventory/REA_EVIDENCE.md",
                            "component": "ACP.dll",
                            "version": "v251",
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(module, "_load_products", lambda: [{"product": "acp"}])
    monkeypatch.setattr(module, "_load_snapshots", lambda: {})
    monkeypatch.setattr(module, "_load_document_coverage", lambda: {})

    product = module.build_report()["products"][0]

    assert product["mapping_status"] == "product_component_evidence_only"
    assert product["rea_evidence"]["component"] == "ACP.dll"
    assert module.SNAPSHOT_PRODUCT_ALIASES["sherlock_core"] == "sherlock"


def test_api_coverage_detects_versioned_snapshots(tmp_path, monkeypatch):
    import importlib.util

    script = REPO_ROOT / "scripts" / "api_extraction" / "build_coverage_report.py"
    spec = importlib.util.spec_from_file_location("coverage_report", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    api_dir = tmp_path / "docs" / "api_inventory"
    api_dir.mkdir(parents=True)
    versions = {
        "mechanical_api_v251.json": "2025 R1 (v251)",
        "mechanical_api_v2510.json": "v2510",
        "spaceclaim_api_v251.json": "2025 R1 (v251)",
        "spaceclaim_api_v252.json": "2025 R2 (v252)",
    }
    for filename, version in versions.items():
        (api_dir / filename).write_text(
            json.dumps({"version": version, "statistics": {"total_methods": 1}}),
            encoding="utf-8",
        )
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "API_DIR", api_dir)

    result = module._load_snapshots()
    mechanical = {item["snapshot_version"]: item for item in result["mechanical"]}
    spaceclaim = {item["snapshot_version"]: item for item in result["spaceclaim"]}

    assert mechanical["2025 R1 (v251)"]["snapshot_path"].endswith("mechanical_api_v251.json")
    assert mechanical["2025 R1 (v251)"]["rea_evidence"]["component"].startswith("Mechanical DataModel")
    assert "rea_evidence" not in mechanical["v2510"]
    assert spaceclaim["2025 R1 (v251)"]["rea_evidence"]["component"].startswith("SpaceClaim.Api.V251.dll")
    assert "rea_evidence" not in spaceclaim["2025 R2 (v252)"]


def test_mapdl_snapshot_is_direct_coverage_with_sdk_metadata():
    coverage = json.loads((INVENTORY_DIR / "api_coverage.json").read_text(encoding="utf-8"))
    mapdl = next(item for item in coverage["products"] if item["product"] == "mapdl")

    assert mapdl["snapshot_status"] == "direct_snapshot"
    assert mapdl["mapping_status"] == "direct_product_id"
    assert len(mapdl["snapshots"]) >= 1
    direct_snap = next(s for s in mapdl["snapshots"] if s["snapshot_path"].endswith("mapdl_api.json"))
    assert direct_snap["statistics"]["total_methods"] == 27

def test_pydyna_snapshot_maps_to_lsdyna_manifest_product_id(tmp_path, monkeypatch):
    import importlib.util

    script = REPO_ROOT / "scripts" / "api_extraction" / "build_coverage_report.py"
    spec = importlib.util.spec_from_file_location("coverage_report", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    api_dir = tmp_path / "docs" / "api_inventory"
    api_dir.mkdir(parents=True)
    (api_dir / "pydyna_api.json").write_text(
        json.dumps({"version": "unknown", "statistics": {"total_methods": 19}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "API_DIR", api_dir)

    snapshots = module._load_snapshots()

    assert "pydyna" not in snapshots
    assert len(snapshots["lsdyna"]) == 1
    assert snapshots["lsdyna"][0]["snapshot_path"].endswith("pydyna_api.json")
    assert snapshots["lsdyna"][0]["statistics"]["total_methods"] == 19

def test_mechanical_core_snapshot_maps_to_mechanical_manifest_product_id(tmp_path, monkeypatch):
    import importlib.util

    script = REPO_ROOT / "scripts" / "api_extraction" / "build_coverage_report.py"
    spec = importlib.util.spec_from_file_location("coverage_report", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    api_dir = tmp_path / "docs" / "api_inventory"
    api_dir.mkdir(parents=True)
    (api_dir / "mechanical_core_api.json").write_text(
        json.dumps({"version": "unknown", "statistics": {"total_methods": 20}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "API_DIR", api_dir)

    snapshots = module._load_snapshots()

    assert "mechanical_core" not in snapshots
    assert len(snapshots["mechanical"]) == 1
    assert snapshots["mechanical"][0]["snapshot_path"].endswith("mechanical_core_api.json")
    assert snapshots["mechanical"][0]["statistics"]["total_methods"] == 20

def test_geometry_core_snapshot_maps_to_geometry_manifest_product_id(tmp_path, monkeypatch):
    import importlib.util

    script = REPO_ROOT / "scripts" / "api_extraction" / "build_coverage_report.py"
    spec = importlib.util.spec_from_file_location("coverage_report", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    api_dir = tmp_path / "docs" / "api_inventory"
    api_dir.mkdir(parents=True)
    (api_dir / "geometry_core_api.json").write_text(
        json.dumps({"version": "unknown", "statistics": {"total_methods": 1}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "API_DIR", api_dir)

    snapshots = module._load_snapshots()

    assert "geometry_core" not in snapshots
    assert len(snapshots["geometry"]) == 1
    assert snapshots["geometry"][0]["snapshot_path"].endswith("geometry_core_api.json")
    assert snapshots["geometry"][0]["statistics"]["total_methods"] == 1


def test_optislang_core_snapshot_maps_to_optislang_manifest_product_id(tmp_path, monkeypatch):
    import importlib.util

    script = REPO_ROOT / "scripts" / "api_extraction" / "build_coverage_report.py"
    spec = importlib.util.spec_from_file_location("coverage_report", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    api_dir = tmp_path / "docs" / "api_inventory"
    api_dir.mkdir(parents=True)
    (api_dir / "optislang_core_api.json").write_text(
        json.dumps({"version": "unknown", "sdk_version": "1.6.0", "statistics": {"total_methods": 18}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "API_DIR", api_dir)

    snapshots = module._load_snapshots()

    assert "optislang_core" not in snapshots
    assert len(snapshots["optislang"]) == 1
    assert snapshots["optislang"][0]["snapshot_path"].endswith("optislang_core_api.json")
    assert snapshots["optislang"][0]["snapshot_version"] == "unknown"



def test_rea_payload_supports_direct_and_wrapped_output():
    normalized = {"metadata": {"status": "complete"}}
    assert _rea_payload({"normalized_result": normalized}) == {"normalized_result": normalized}
    assert _rea_payload({"data": {"normalized_result": normalized}}) == {"normalized_result": normalized}



def test_additive_rea_snapshot_preserves_type_method_ownership():
    path = INVENTORY_DIR / "additive_rea_api.json"
    snapshot = json.loads(path.read_text(encoding="utf-8"))
    classes = [cls for module in snapshot["modules"].values() for cls in module["classes"].values()]

    assert len(classes) == snapshot["statistics"]["total_classes"] == 208
    assert sum(len(cls["methods"]) for cls in classes) == snapshot["statistics"]["total_methods"] == 2314


def test_v251_product_addin_rea_snapshots_preserve_owner_methods():
    expected = {
        "aqwa_addin_rea": (290, 3464),
        "cfx_addin_rea": (240, 2505),
        "fluent_addin_rea": (482, 7652),
        "icepak_addin_rea": (115, 1588),
        "meshing_addin_rea": (399, 3925),
        "polyflow_addin_rea": (283, 3263),
        "sherlock_addin_rea": (465, 5357),
        "hfss_addin_rea": (2, 8),
    }
    for product, (type_count, method_count) in expected.items():
        snapshot = json.loads((INVENTORY_DIR / f"{product}_api.json").read_text(encoding="utf-8"))
        classes = [
            cls for module in snapshot["modules"].values() for cls in module["classes"].values()
        ]
        assert len(classes) == snapshot["statistics"]["total_classes"] == type_count
        assert (
            sum(len(cls["methods"]) for cls in classes)
            == snapshot["statistics"]["total_methods"]
            == method_count
        )
        assert snapshot["sources"]["assembly"]["sha256"]
        assert snapshot["sources"]["assembly"]["rea_evidence_id"]



def test_spaceclaim_core_rea_snapshot_preserves_type_method_ownership():
    snapshot = json.loads(
        (INVENTORY_DIR / "spaceclaim_core_rea_api.json").read_text(encoding="utf-8")
    )
    classes = [
        cls for module in snapshot["modules"].values() for cls in module["classes"].values()
    ]
    assert len(classes) == snapshot["statistics"]["total_classes"] == 3904
    assert (
        sum(len(cls["methods"]) for cls in classes)
        == snapshot["statistics"]["total_methods"]
        == 21426
    )
    artifact = snapshot["sources"]["assembly"]
    assert artifact["sha256"] == "329adf81f2678da5ffaf671a10691ec6cb41963b92f652f2baaa555646a0b55d"
    assert artifact["mvid"] == "df791fca-9ae8-4699-98d4-a6e792f098bf"
    assert artifact["rea_evidence_id"] == "ev_1ff332940176d8fd198d0005264756f2ae91929b8c01d558ec4f029788de79fd"
