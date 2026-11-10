import json
import sqlite3

from ansys_unified_mcp.analytics.apikb import config as cfg
from ansys_unified_mcp.analytics.apikb.build import build_database


def test_primemesh_snapshot_indexes_client_members_and_launcher(tmp_path, monkeypatch):
    docs = tmp_path / "api_inventory"
    docs.mkdir()
    snapshot_path = docs / "primemesh_api.json"
    snapshot_path.write_text(
        json.dumps(
            {
                "version": "unknown",
                "sdk_version": "0.10.5",
                "modules": {
                    "ansys.meshing.prime": {
                        "classes": {
                            "Client": {
                                "doc": "PyPrimeMesh client.",
                                "methods": [
                                    {"name": "run_on_server", "signature": "(self, recipe)", "doc": "Run recipe."},
                                    {"name": "exit", "signature": "(self)", "doc": "Close client."},
                                ],
                                "properties": [{"name": "model", "type": "Model", "doc": "Client model."}],
                            }
                        },
                        "functions": [
                            {"name": "launch_prime", "signature": "(prime_root=None)", "doc": "Launch Prime."}
                        ],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(cfg, "DOCS_DIR", docs)
    monkeypatch.setattr(cfg, "SOURCES", {"primemesh": snapshot_path})
    monkeypatch.setattr(cfg, "DB_DIR", tmp_path / "database")
    monkeypatch.setattr(cfg, "DB_PATH", cfg.DB_DIR / "api_kb.sqlite")

    result = build_database(force=True)

    assert result["status"] == "success"
    with sqlite3.connect(cfg.DB_PATH) as conn:
        source = conn.execute(
            "SELECT product, release, interface, sdk_version FROM api_sources"
        ).fetchone()
        symbols = conn.execute(
            "SELECT fqname, kind, doc FROM symbols WHERE product='primemesh' ORDER BY name"
        ).fetchall()
        members = conn.execute(
            "SELECT m.name, m.kind FROM members m "
            "JOIN symbol_members sm ON sm.member_id=m.id "
            "JOIN symbols s ON s.id=sm.symbol_id WHERE s.product='primemesh' ORDER BY m.name"
        ).fetchall()

    assert source == (
        "primemesh",
        "unknown (product release not recorded)",
        "PyPrimeMesh 0.10.5 Client and launch_prime",
        "0.10.5",
    )
    assert symbols == [
        ("ansys.meshing.prime.Client", "class", "PyPrimeMesh client."),
        (
            "ansys.meshing.prime.launch_prime",
            "module_function",
            "(prime_root=None)\nLaunch Prime.",
        ),
    ]
    assert members == [
        ("exit", "method"),
        ("model", "property"),
        ("run_on_server", "method"),
    ]
