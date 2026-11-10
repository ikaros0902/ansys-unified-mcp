import json
import sqlite3

from ansys_unified_mcp.analytics.apikb import config as cfg
from ansys_unified_mcp.analytics.apikb.build import build_database


def test_dpf_snapshot_indexes_members_without_cross_class_documentation(tmp_path, monkeypatch):
    docs = tmp_path / "api_inventory"
    docs.mkdir()
    snapshot_path = docs / "dpf_api.json"
    class_snapshots = {
        "ansys.dpf.core.fields_container": ("FieldsContainer", "FieldsContainer API.", "Fields container copy.", "Fields container unit."),
        "ansys.dpf.core.meshed_region": ("MeshedRegion", "Meshed region API.", "Mesh copy.", "Mesh unit."),
    }
    modules = {}
    for module_name, (class_name, class_doc, method_doc, property_doc) in class_snapshots.items():
        modules[module_name] = {
            "classes": {
                class_name: {
                    "doc": class_doc,
                    "methods": [{"name": "deep_copy", "signature": "(self, server=None)", "doc": method_doc}],
                    "properties": [{"name": "unit", "type": "str", "doc": property_doc}],
                }
            },
            "functions": [],
        }
    snapshot_path.write_text(
        json.dumps({"version": "unknown", "sdk_version": "0.16.1", "modules": modules}),
        encoding="utf-8",
    )
    monkeypatch.setattr(cfg, "DOCS_DIR", docs)
    monkeypatch.setattr(cfg, "SOURCES", {"dpf": snapshot_path})
    monkeypatch.setattr(cfg, "DB_DIR", tmp_path / "database")
    monkeypatch.setattr(cfg, "DB_PATH", cfg.DB_DIR / "api_kb.sqlite")

    result = build_database(force=True)

    assert result["status"] == "success"
    with sqlite3.connect(cfg.DB_PATH) as conn:
        source = conn.execute(
            "SELECT product, release, interface, sdk_version FROM api_sources"
        ).fetchone()
        members = conn.execute(
            "SELECT s.fqname,m.name,m.kind,m.doc FROM symbols s "
            "JOIN symbol_members sm ON sm.symbol_id=s.id "
            "JOIN members m ON m.id=sm.member_id WHERE s.product='dpf' "
            "ORDER BY s.fqname,m.name"
        ).fetchall()

    assert source == (
        "dpf",
        "unknown (product release not recorded)",
        "PyDPF-Core 0.16.1 core data classes",
        "0.16.1",
    )
    assert members == [
        ("ansys.dpf.core.fields_container.FieldsContainer", "deep_copy", "method", "Fields container copy."),
        ("ansys.dpf.core.fields_container.FieldsContainer", "unit", "property", "Fields container unit."),
        ("ansys.dpf.core.meshed_region.MeshedRegion", "deep_copy", "method", "Mesh copy."),
        ("ansys.dpf.core.meshed_region.MeshedRegion", "unit", "property", "Mesh unit."),
    ]
