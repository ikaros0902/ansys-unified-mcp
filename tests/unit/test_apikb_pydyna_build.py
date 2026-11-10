import json
import sqlite3

from ansys_unified_mcp.analytics.apikb import config as cfg
from ansys_unified_mcp.analytics.apikb.build import build_database


def test_pydyna_snapshot_indexes_deck_members_with_sdk_metadata(tmp_path, monkeypatch):
    docs = tmp_path / "api_inventory"
    docs.mkdir()
    snapshot_path = docs / "pydyna_api.json"
    snapshot_path.write_text(
        json.dumps(
            {
                "version": "unknown",
                "sdk_version": "0.12.1",
                "modules": {
                    "ansys.dyna.core.lib.deck": {
                        "classes": {
                            "Deck": {
                                "doc": "Deck class.",
                                "methods": [
                                    {"name": "append", "signature": "(self, keyword)", "doc": "Append keyword."}
                                ],
                                "properties": [{"name": "keywords", "type": "KeywordCollection", "doc": "Deck keywords."}],
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
    monkeypatch.setattr(cfg, "SOURCES", {"pydyna": snapshot_path})
    monkeypatch.setattr(cfg, "DB_DIR", tmp_path / "database")
    monkeypatch.setattr(cfg, "DB_PATH", cfg.DB_DIR / "api_kb.sqlite")

    result = build_database(force=True)

    assert result["status"] == "success"
    with sqlite3.connect(cfg.DB_PATH) as conn:
        source = conn.execute(
            "SELECT product, interface, sdk_version FROM api_sources"
        ).fetchone()
        members = conn.execute(
            "SELECT m.name,m.kind,m.doc FROM members m "
            "JOIN symbol_members sm ON sm.member_id=m.id "
            "JOIN symbols s ON s.id=sm.symbol_id WHERE s.product='pydyna' ORDER BY m.name"
        ).fetchall()

    assert source == ("pydyna", "PyDyna 0.12.1 Deck class", "0.12.1")
    assert members == [
        ("append", "method", "Append keyword."),
        ("keywords", "property", "Deck keywords."),
    ]
