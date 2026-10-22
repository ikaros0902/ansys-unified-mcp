"""文件來源盤點器的品質與 hash 輸出測試。"""

from __future__ import annotations

from pathlib import Path

from scripts.maintenance.inventory_ansys_sources import classify, inventory


def test_inventory_records_hash_version_and_stub_quality(tmp_path: Path) -> None:
    root = tmp_path / "docs"
    root.mkdir()
    stub = root / "LS-DYNA_2026_R1_Manual.md"
    content = "Download the complete manual from the publisher. 2026 R1"
    stub.write_text(content, encoding="utf-8")

    rows = inventory([root])
    assert len(rows) == 1
    assert rows[0]["product"] == "ls-dyna"
    assert rows[0]["release"] == "2026 R1"
    assert rows[0]["quality"] == "stub_or_download_page"
    assert len(rows[0]["sha256"]) == 64
    assert classify(stub, root, stub.stat().st_size, content)["category"] == "manual"
