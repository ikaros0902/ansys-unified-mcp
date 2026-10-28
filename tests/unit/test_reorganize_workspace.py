from pathlib import Path

import pytest

from scripts.maintenance.reorganize_workspace import destination, execute, inside, repair_links


def test_paths_and_release_evidence(tmp_path):
    with pytest.raises(ValueError):
        inside(tmp_path, "../escape")
    with pytest.raises(ValueError):
        inside(tmp_path, ".")
    path, release, _ = destination(Path("Fluent/guides/Python.md"),
                                   "source_url: https://official.example/v251/user.html", {})
    assert path == Path("Fluent/v251/guides/Python.md")
    assert release == "v251"
    _, release, _ = destination(Path("Fluent/guides/Python.md"), "支持2025 R1和2026 R1", {})
    assert release == "unknown"


def test_migration_preserves_backup_and_refuses_collision(tmp_path):
    (tmp_path / "ANSYS_Document").mkdir()
    source = tmp_path / "docs/ARCHITECTURE.md"
    source.parent.mkdir()
    source.write_text("original", encoding="utf-8")
    preview = execute(tmp_path, apply=False, corpus_layout=False, pdf_metadata={})
    assert preview["moves"] == 1 and source.exists()
    execute(tmp_path, apply=True, corpus_layout=False, pdf_metadata={})
    assert not source.exists()
    assert (tmp_path / "docs/architecture/ARCHITECTURE.md").read_text() == "original"
    assert (tmp_path / ".runtime/folder-document-cleanup/originals/docs/ARCHITECTURE.md").read_text() == "original"
    assert execute(tmp_path, apply=True, corpus_layout=False, pdf_metadata={})["resumed"]
    source.write_text("changed", encoding="utf-8")
    with pytest.raises(FileExistsError):
        execute(tmp_path, apply=True, corpus_layout=False, pdf_metadata={})
    assert source.read_text() == "changed"


def test_named_duplicate_with_different_bytes_is_never_removed(tmp_path):
    root = tmp_path / "ANSYS_Document"
    a = root / "AnsysEM/manuals_and_training/UsersGuide_1.62.pdf"
    b = root / "TwinAI/manuals/UsersGuide_1.62.pdf"
    for p, text in [(a, b"ABC"), (b, b"XYZ")]:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text)
    with pytest.raises(ValueError):
        execute(tmp_path, apply=True, corpus_layout=False, pdf_metadata={})
    assert a.read_bytes() == b"ABC" and b.read_bytes() == b"XYZ"


def test_links_repair_is_repeatable_and_protects_later_edits(tmp_path):
    root = tmp_path / "ANSYS_Document"
    target = root / "Product/v251/guide/a.md"
    target.parent.mkdir(parents=True)
    target.write_text("[B](../api/b.md)", encoding="utf-8")
    other = root / "Product/v252/api/b.md"
    other.parent.mkdir(parents=True)
    other.write_text("API", encoding="utf-8")
    rows = [{"action": "move", "source": "ANSYS_Document/Product/guide/a.md", "target": target.relative_to(tmp_path).as_posix()},
            {"action": "move", "source": "ANSYS_Document/Product/api/b.md", "target": other.relative_to(tmp_path).as_posix()}]
    assert repair_links(tmp_path, rows) == 1
    assert target.read_text() == "[B](../../v252/api/b.md)"
    assert repair_links(tmp_path, rows) == 0
    target.write_text("User edit", encoding="utf-8")
    with pytest.raises(FileExistsError):
        repair_links(tmp_path, rows)


def test_non_utf8_manual_is_preserved_and_reported(tmp_path):
    path = tmp_path / "ANSYS_Document/Product/unknown/manuals/old.md"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"legacy\xa1")
    assert repair_links(tmp_path, []) == 0
    assert path.read_bytes() == b"legacy\xa1"
    assert "encoding_not_utf8" in (tmp_path / "ANSYS_Document/_catalog/link_repair_issues.json").read_text()
