import json
import sqlite3

from ansys_unified_mcp.analytics.apikb import config as cfg
from ansys_unified_mcp.analytics.apikb.build import build_database


def test_optislang_core_snapshot_indexes_client_with_distinct_sdk_metadata(tmp_path, monkeypatch):
    docs = tmp_path / "api_inventory"
    docs.mkdir()
    snapshot_path = docs / "optislang_core_api.json"
    snapshot_path.write_text(
        json.dumps(
            {
                "version": "unknown",
                "sdk_version": "1.6.0",
                "modules": {
                    "ansys.optislang.core.optislang": {
                        "classes": {
                            "Optislang": {
                                "doc": "Client for optiSLang.",
                                "methods": [{"name": "shutdown", "signature": "(self, force=False)", "doc": "Stop the client."}],
                                "properties": [{"name": "project", "type": "Project", "doc": "Active project."}],
                            }
                        },
                        "functions": [],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(cfg, "DOCS_DIR", docs)
    monkeypatch.setattr(cfg, "SOURCES", {"optislang_core": snapshot_path})
    monkeypatch.setattr(cfg, "DB_DIR", tmp_path / "database")
    monkeypatch.setattr(cfg, "DB_PATH", cfg.DB_DIR / "api_kb.sqlite")

    result = build_database(force=True)

    assert result["status"] == "success"
    with sqlite3.connect(cfg.DB_PATH) as conn:
        source = conn.execute("SELECT product,interface,sdk_version FROM api_sources").fetchone()
        symbols = conn.execute("SELECT fqname,kind FROM symbols").fetchall()
        members = conn.execute("SELECT name,kind FROM members ORDER BY name").fetchall()

    assert source == ("optislang_core", "PyOptiSLang 1.6.0 Optislang client", "1.6.0")
    assert symbols == [("ansys.optislang.core.optislang.Optislang", "class")]
    assert members == [("project", "property"), ("shutdown", "method")]
