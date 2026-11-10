import json
import sqlite3

from ansys_unified_mcp.analytics.apikb import config as cfg
from ansys_unified_mcp.analytics.apikb.build import build_database


def test_sound_snapshot_keeps_same_named_members_scoped_to_their_classes(tmp_path, monkeypatch):
    docs = tmp_path / "api_inventory"
    docs.mkdir()
    snapshot_path = docs / "sound_api.json"
    modules = {
        "ansys.sound.core.sound_composer.sound_composer": {
            "classes": {
                "SoundComposer": {
                    "doc": "Composer API.",
                    "methods": [
                        {"name": "process", "signature": "(self)", "doc": "Process composer."},
                        {"name": "get_output", "signature": "(self)", "doc": "Composer output."},
                    ],
                    "properties": [{"name": "name", "type": "str", "doc": "Composer name."}],
                }
            },
            "functions": [],
        },
        "ansys.sound.core.sound_composer.track": {
            "classes": {
                "Track": {
                    "doc": "Track API.",
                    "methods": [
                        {"name": "process", "signature": "(self)", "doc": "Process track."},
                        {"name": "get_output", "signature": "(self)", "doc": "Track output."},
                    ],
                    "properties": [{"name": "name", "type": "str", "doc": "Track name."}],
                }
            },
            "functions": [],
        },
    }
    snapshot_path.write_text(
        json.dumps({"version": "unknown", "sdk_version": "0.3.0", "modules": modules}),
        encoding="utf-8",
    )
    monkeypatch.setattr(cfg, "DOCS_DIR", docs)
    monkeypatch.setattr(cfg, "SOURCES", {"sound": snapshot_path})
    monkeypatch.setattr(cfg, "DB_DIR", tmp_path / "database")
    monkeypatch.setattr(cfg, "DB_PATH", cfg.DB_DIR / "api_kb.sqlite")

    result = build_database(force=True)

    assert result["status"] == "success"
    with sqlite3.connect(cfg.DB_PATH) as conn:
        source = conn.execute(
            "SELECT product, interface, sdk_version FROM api_sources"
        ).fetchone()
        members = conn.execute(
            "SELECT s.fqname, m.name, m.doc FROM symbols s "
            "JOIN symbol_members sm ON sm.symbol_id=s.id "
            "JOIN members m ON m.id=sm.member_id WHERE s.product='sound' "
            "ORDER BY s.fqname, m.name"
        ).fetchall()

    assert source == ("sound", "PyAnsys Sound 0.3.0 SoundComposer and Track", "0.3.0")
    assert members == [
        ("ansys.sound.core.sound_composer.sound_composer.SoundComposer", "get_output", "Composer output."),
        ("ansys.sound.core.sound_composer.sound_composer.SoundComposer", "name", "Composer name."),
        ("ansys.sound.core.sound_composer.sound_composer.SoundComposer", "process", "Process composer."),
        ("ansys.sound.core.sound_composer.track.Track", "get_output", "Track output."),
        ("ansys.sound.core.sound_composer.track.Track", "name", "Track name."),
        ("ansys.sound.core.sound_composer.track.Track", "process", "Process track."),
    ]
