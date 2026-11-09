"""額外 Markdown 語料的盤點索引、版本篩選與來源追溯測試。"""

from __future__ import annotations

from pathlib import Path
import pytest

from ansys_unified_mcp.analytics.docsearch import config, index


def test_external_markdown_index_returns_provenance_and_release_filter(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    source = tmp_path / "curated" / "Documentation_md"
    extra = tmp_path / "user_docs" / "Mechanical"
    clean = tmp_path / "clean"
    repo.mkdir()
    source.mkdir(parents=True)
    extra.mkdir(parents=True)
    (source / "Mechanical_Ref.md").write_text(
        "# Mechanical Reference\nBeamSupport API setting.\n2025 R1\n", encoding="utf-8"
    )
    external_file = extra / "random_vibration.md"
    external_file.write_text(
        "# Random Vibration\nPSD spectrum and modal damping in Mechanical.\n"
        "This guide is for 2026 R1.\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(config, "REPO_ROOT", repo)
    monkeypatch.setattr(config, "SOURCE_DIR", source)
    monkeypatch.setattr(config, "CLEAN_DIR", clean)
    monkeypatch.setattr(config, "INDEX_PATH", clean / "docs_index.sqlite")
    monkeypatch.setattr(config, "EXTRA_SOURCE_DIRS", [tmp_path / "user_docs"])
    monkeypatch.setattr(
        config,
        "API_DOCS",
        [{"name": "Mechanical_Ref", "title": "Mechanical Ref", "category": "api_reference",
          "product": "mechanical", "style": "ansys"}],
    )

    built = index.build_index()
    assert built["ok"] is True
    search = index.search("PSD spectrum", scope="all", product="mechanical", release="2026 R1")
    assert search["ok"] is True, search
    assert len(search["results"]) == 1
    result = search["results"][0]
    assert result["product"] == "mechanical"
    assert result["release"] == "2026 R1"
    assert Path(result["source_path"]) == external_file

    docs = index.list_docs()["docs"]
    external = next(item for item in docs if item["source_path"] == str(external_file))
    assert external["content_hash"]
    assert external["quality"] == "body_present"

    existing_index = config.INDEX_PATH.read_bytes()
    monkeypatch.setattr(config, "EXTRA_SOURCE_DIRS", [tmp_path / "offline_docs"])
    with pytest.raises(RuntimeError, match="外部文件來源暫時不可用"):
        index.build_index()
    assert config.INDEX_PATH.read_bytes() == existing_index


def test_scade_one_external_dictionary_uses_its_own_product(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    source = tmp_path / "curated"
    extra = tmp_path / "dictionary"
    clean = tmp_path / "clean"
    for directory in (repo, source, extra):
        directory.mkdir()
    (source / "Mechanical_Ref.md").write_text("# Reference\nBeamSupport API.\n", encoding="utf-8")
    (extra / "scade.md").write_text("# SCADE\nlegacyflow term.\n", encoding="utf-8")
    (extra / "scade_one.md").write_text("# SCADE One\nswanprimer term.\n", encoding="utf-8")
    monkeypatch.setattr(config, "REPO_ROOT", repo)
    monkeypatch.setattr(config, "DOCS_ROOT", tmp_path)
    monkeypatch.setattr(config, "SOURCE_DIR", source)
    monkeypatch.setattr(config, "CLEAN_DIR", clean)
    monkeypatch.setattr(config, "INDEX_PATH", clean / "docs_index.sqlite")
    monkeypatch.setattr(config, "EXTRA_SOURCE_DIRS", [extra])
    monkeypatch.setattr(config, "API_DOCS", [{"name": "Mechanical_Ref", "title": "Reference", "category": "api_reference", "product": "mechanical", "style": "ansys"}])

    assert index.build_index()["ok"]
    result = index.search("swanprimer", scope="all", product="scade_one")
    assert result["ok"] and len(result["results"]) == 1
    hit = result["results"][0]
    assert hit["product"] == "scade_one"
    assert index.get_chunk(hit["doc"], hit["chunk_id"])["ok"]
    assert not index.search("swanprimer", scope="all", product="scade")["results"]
    assert index.search("legacyflow", scope="all", product="scade")["count"] == 1


def test_geometry_dictionary_product_filter(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "curated"
    extra = tmp_path / "knowledge_dictionary"
    clean = tmp_path / "clean"
    source.mkdir()
    extra.mkdir()
    (source / "Mechanical_Ref.md").write_text("# Reference\nBeam support.\n", encoding="utf-8")
    (extra / "geometry.md").write_text("# Geometry\nUnique sketch guide.\n", encoding="utf-8")
    (extra / "mechanical_geometry.md").write_text("# Mechanical\nUnique mesh note.\n", encoding="utf-8")
    monkeypatch.setattr(config, "DOCS_ROOT", tmp_path)
    monkeypatch.setattr(config, "SOURCE_DIR", source)
    monkeypatch.setattr(config, "CLEAN_DIR", clean)
    monkeypatch.setattr(config, "INDEX_PATH", clean / "docs_index.sqlite")
    monkeypatch.setattr(config, "EXTRA_SOURCE_DIRS", [extra])
    monkeypatch.setattr(config, "API_DOCS", [{"name": "Mechanical_Ref", "title": "Reference", "category": "api_reference", "product": "mechanical", "style": "ansys"}])

    assert index.build_index()["ok"]
    result = index.search("Unique sketch guide", scope="all", product="geometry")
    assert result["count"] == 1
    hit = result["results"][0]
    assert hit["product"] == "geometry"
    assert index.get_chunk(hit["doc"], hit["chunk_id"])["ok"]
    assert index.search("Unique sketch guide", scope="all", product="general")["count"] == 0
    assert index.search("Unique mesh note", scope="all", product="mechanical")["count"] == 1


def test_failed_curated_rebuild_preserves_previous_index(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    source = tmp_path / "curated" / "Documentation_md"
    extra = tmp_path / "user_docs"
    clean = tmp_path / "clean"
    repo.mkdir()
    source.mkdir(parents=True)
    extra.mkdir()
    manual = source / "Mechanical_Ref.md"
    manual.write_text("# Mechanical Reference\nBeam support official reference.\n", encoding="utf-8")
    monkeypatch.setattr(config, "REPO_ROOT", repo)
    monkeypatch.setattr(config, "SOURCE_DIR", source)
    monkeypatch.setattr(config, "CLEAN_DIR", clean)
    monkeypatch.setattr(config, "INDEX_PATH", clean / "docs_index.sqlite")
    monkeypatch.setattr(config, "EXTRA_SOURCE_DIRS", [extra])
    monkeypatch.setattr(
        config,
        "API_DOCS",
        [{"name": "Mechanical_Ref", "title": "Mechanical Ref", "category": "api_reference",
          "product": "mechanical", "style": "ansys"}],
    )
    index.build_index()
    previous_index = config.INDEX_PATH.read_bytes()

    manual.unlink()
    with pytest.raises(RuntimeError, match="保留現有索引"):
        index.build_index()

    assert config.INDEX_PATH.read_bytes() == previous_index

