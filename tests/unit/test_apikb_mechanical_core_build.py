import json
import sqlite3

from ansys_unified_mcp.analytics.apikb import config as cfg
from ansys_unified_mcp.analytics.apikb.build import build_database


def test_mechanical_core_snapshot_indexes_client_members_and_functions(tmp_path, monkeypatch):
    docs = tmp_path / "api_inventory"
    docs.mkdir()
    snapshot_path = docs / "mechanical_core_api.json"
    snapshot_path.write_text(
        json.dumps(
            {
                "version": "unknown",
                "sdk_version": "0.13.2",
                "modules": {
                    "ansys.mechanical.core.mechanical": {
                        "classes": {
                            "Mechanical": {
                                "doc": "Mechanical client.",
                                "methods": [{"name": "exit", "signature": "(self)", "doc": "Close client."}],
                                "properties": [{"name": "busy", "type": "bool", "doc": "Busy state."}],
                            }
                        },
                        "functions": [
                            {"name": "launch_mechanical", "signature": "(port=10000)", "doc": "Launch a client."},
                            {"name": "connect_to_mechanical", "signature": "(ip, port)", "doc": "Connect a client."},
                        ],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(cfg, "DOCS_DIR", docs)
    monkeypatch.setattr(cfg, "SOURCES", {"mechanical_core": snapshot_path})
    monkeypatch.setattr(cfg, "DB_DIR", tmp_path / "database")
    monkeypatch.setattr(cfg, "DB_PATH", cfg.DB_DIR / "api_kb.sqlite")

    result = build_database(force=True)

    assert result["status"] == "success"
    with sqlite3.connect(cfg.DB_PATH) as conn:
        source = conn.execute(
            "SELECT product, interface, sdk_version FROM api_sources"
        ).fetchone()
        symbols = conn.execute(
            "SELECT fqname,kind FROM symbols WHERE product='mechanical_core' ORDER BY kind,fqname"
        ).fetchall()
        members = conn.execute(
            "SELECT m.name,m.kind,m.doc FROM members m "
            "JOIN symbol_members sm ON sm.member_id=m.id "
            "JOIN symbols s ON s.id=sm.symbol_id WHERE s.product='mechanical_core'"
        ).fetchall()

    assert source == (
        "mechanical_core",
        "PyMechanical 0.13.2 Mechanical client and launch/connect functions",
        "0.13.2",
    )
    assert symbols == [
        ("ansys.mechanical.core.mechanical.Mechanical", "class"),
        ("ansys.mechanical.core.mechanical.connect_to_mechanical", "module_function"),
        ("ansys.mechanical.core.mechanical.launch_mechanical", "module_function"),
    ]
    assert members == [("exit", "method", "Close client."), ("busy", "property", "Busy state.")]
