import json
import sqlite3

from ansys_unified_mcp.analytics.apikb import config as cfg
from ansys_unified_mcp.analytics.apikb.build import build_database


def test_geometry_core_snapshot_indexes_modeler_members_and_launcher(tmp_path, monkeypatch):
    docs = tmp_path / "api_inventory"
    docs.mkdir()
    snapshot_path = docs / "geometry_core_api.json"
    snapshot_path.write_text(
        json.dumps(
            {
                "version": "unknown",
                "sdk_version": "0.17.1",
                "modules": {
                    "ansys.geometry.core.modeler": {
                        "classes": {
                            "Modeler": {
                                "doc": "Geometry modeler.",
                                "methods": [
                                    {"name": "create_design", "signature": "(self, name)", "doc": "Create design."}
                                ],
                                "properties": [{"name": "design", "type": "Design", "doc": "Active design."}],
                            }
                        },
                        "functions": [],
                    },
                    "ansys.geometry.core.connection.launcher": {
                        "classes": {},
                        "functions": [
                            {"name": "launch_modeler", "signature": "(mode=None)", "doc": "Launch modeler."}
                        ],
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(cfg, "DOCS_DIR", docs)
    monkeypatch.setattr(cfg, "SOURCES", {"geometry_core": snapshot_path})
    monkeypatch.setattr(cfg, "DB_DIR", tmp_path / "database")
    monkeypatch.setattr(cfg, "DB_PATH", cfg.DB_DIR / "api_kb.sqlite")

    result = build_database(force=True)

    assert result["status"] == "success"
    with sqlite3.connect(cfg.DB_PATH) as conn:
        source = conn.execute(
            "SELECT product, interface, sdk_version FROM api_sources"
        ).fetchone()
        symbols = conn.execute(
            "SELECT fqname,kind FROM symbols WHERE product='geometry_core' ORDER BY kind,fqname"
        ).fetchall()
        members = conn.execute(
            "SELECT m.name,m.kind,m.doc FROM members m "
            "JOIN symbol_members sm ON sm.member_id=m.id "
            "JOIN symbols s ON s.id=sm.symbol_id WHERE s.product='geometry_core'"
        ).fetchall()

    assert source == (
        "geometry_core",
        "PyAnsys Geometry 0.17.1 Modeler and launch_modeler",
        "0.17.1",
    )
    assert symbols == [
        ("ansys.geometry.core.modeler.Modeler", "class"),
        ("ansys.geometry.core.connection.launcher.launch_modeler", "module_function"),
    ]
    assert members == [
        ("create_design", "method", "Create design."),
        ("design", "property", "Active design."),
    ]
