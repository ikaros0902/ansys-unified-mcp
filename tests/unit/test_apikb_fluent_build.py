import json
import sqlite3

from ansys_unified_mcp.analytics.apikb import config as cfg
from ansys_unified_mcp.analytics.apikb.build import build_database


def test_fluent_snapshot_indexes_documented_launcher_functions(tmp_path, monkeypatch):
    docs = tmp_path / "api_inventory"
    docs.mkdir()
    snapshot_path = docs / "fluent_api.json"
    snapshot_path.write_text(
        json.dumps(
            {
                "version": "unknown",
                "sdk_version": "0.42.1",
                "modules": {
                    "ansys.fluent.core.launcher.launcher": {
                        "classes": {},
                        "functions": [
                            {
                                "name": "launch_fluent",
                                "signature": "(*, mode='solver')",
                                "doc": "Launch Fluent.",
                            },
                            {
                                "name": "connect_to_fluent",
                                "signature": "(*, ip=None, port=None)",
                                "doc": "Connect to Fluent.",
                            },
                        ],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(cfg, "DOCS_DIR", docs)
    monkeypatch.setattr(cfg, "SOURCES", {"fluent": snapshot_path})
    monkeypatch.setattr(cfg, "DB_DIR", tmp_path / "database")
    monkeypatch.setattr(cfg, "DB_PATH", cfg.DB_DIR / "api_kb.sqlite")

    result = build_database(force=True)

    assert result["status"] == "success"
    with sqlite3.connect(cfg.DB_PATH) as conn:
        source = conn.execute(
            "SELECT product, release, interface, sdk_version FROM api_sources"
        ).fetchone()
        functions = conn.execute(
            "SELECT fqname, kind, doc FROM symbols WHERE product='fluent' ORDER BY name"
        ).fetchall()

    assert source == (
        "fluent",
        "unknown (product release not recorded)",
        "PyFluent 0.42.1 launcher functions",
        "0.42.1",
    )
    assert functions == [
        (
            "ansys.fluent.core.launcher.launcher.connect_to_fluent",
            "module_function",
            "(*, ip=None, port=None)\nConnect to Fluent.",
        ),
        (
            "ansys.fluent.core.launcher.launcher.launch_fluent",
            "module_function",
            "(*, mode='solver')\nLaunch Fluent.",
        ),
    ]
