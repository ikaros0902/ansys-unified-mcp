"""產品清冊、多版本檢索與失敗時保留索引的行為驗證。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ansys_unified_mcp.analytics.docsearch import config, index


@pytest.fixture
def library(tmp_path: Path, monkeypatch):
    root = tmp_path / "repo"
    corpus = root / "ANSYS_Document"
    catalog = corpus / "_catalog" / "documents.json"
    catalog.parent.mkdir(parents=True)
    clean = tmp_path / "clean"
    monkeypatch.setattr(config, "REPO_ROOT", root)
    monkeypatch.setattr(config, "SOURCE_DIR", root / "Documentation_md")
    monkeypatch.setattr(config, "CLEAN_DIR", clean)
    monkeypatch.setattr(config, "INDEX_PATH", clean / "docs_index.sqlite")
    monkeypatch.setattr(config, "EXTRA_SOURCE_DIRS", [])
    monkeypatch.setattr(config, "API_DOCS", [])
    index._catalog_cache.clear()
    return corpus, catalog, clean


def document(corpus: Path, name: str, release: str = "v251", **metadata) -> dict:
    path = corpus / "Fluent" / release / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Solver API\nBeamSupport controls the solver mesh settings.\n", encoding="utf-8")
    return {
        "id": name, "title": name, "product": "fluent", "release": release,
        "sdk_package": "ansys-fluent-core", "sdk_version": "0.30.0",
        "category": "api_reference", "source_url": f"https://example.invalid/{name}",
        "path": path.relative_to(corpus).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "quality": "body_present",
        **metadata,
    }


def write_catalog(catalog: Path, documents: list[dict]) -> None:
    catalog.write_text(json.dumps({"schema_version": 1, "documents": documents}), encoding="utf-8")


def test_catalog_only_bootstrap_filters_and_chunk_readback(library):
    corpus, catalog, _ = library
    old = document(corpus, "fluent-251")
    new = document(corpus, "fluent-261", "v261", sdk_version="0.35.0")
    write_catalog(catalog, [old, new])

    built = index.build_index()
    assert built["catalog_indexed_count"] == 2
    result = index.search("BeamSupport", product="fluent", release="v251",
                          category="api_reference", sdk_version="0.30.0")
    assert result["scope"] == "api"
    assert [item["doc"] for item in result["results"]] == [old["id"]]
    hit = result["results"][0]
    assert hit["source_url"] == old["source_url"]
    assert hit["sdk_package"] == "ansys-fluent-core"
    assert "BeamSupport" in index.get_chunk(hit["doc"], hit["chunk_id"])["text"]
    assert index.search("BeamSupport", sdk_version="unavailable")["count"] == 0
    assert index.search("BeamSupport")["count"] == 1
    assert {item["release"] for item in index.list_docs()["docs"]} == {"v251", "v261"}


def test_nested_spaceclaim_skill_is_searchable_by_its_product(library):
    corpus, _, _ = library
    root = corpus.parent
    api_dir = config.SOURCE_DIR
    api_dir.mkdir(parents=True)
    (api_dir / "bootstrap.md").write_text("# Bootstrap API\nBootstrapToken\n", encoding="utf-8")
    config.API_DOCS[:] = [{
        "name": "bootstrap", "title": "Bootstrap API", "category": "api_reference",
        "product": "geometry", "style": "ansys",
    }]
    skill = root / "agents" / "skills" / "geometry-meshing" / "ansys-spaceclaim"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "# SpaceClaim API\nSpaceClaimUniqueGeometryToken models a solid body.\n",
        encoding="utf-8",
    )

    index.build_index()
    docs = index.list_docs()["docs"]
    assert any(doc["product"] == "spaceclaim" for doc in docs), docs
    result = index.search("SpaceClaimUniqueGeometryToken", product="spaceclaim", scope="all")

    assert result["count"] == 1
    assert result["results"][0]["product"] == "spaceclaim"


def test_shared_body_keeps_product_release_aliases_and_one_chunk_set(library):
    corpus, catalog, _ = library
    old = document(corpus, "fluent-old")
    new = document(corpus, "fluent-new", "v261", sdk_version="0.35.0")
    other = document(corpus, "cfx-new", "v261", product="cfx")
    write_catalog(catalog, [old, new, other])
    built = index.build_index()
    assert built["catalog_indexed_count"] == 3
    assert built["catalog_content_count"] == 1
    assert built["chunk_count"] == 1
    assert len(index.list_docs()["docs"]) == 3
    for item in (old, new, other):
        result = index.search("BeamSupport", product=item["product"], release=item["release"])
        hit = result["results"][0]
        assert hit["doc"] == item["id"]
        assert hit["source_url"] == item["source_url"]
        assert "BeamSupport" in index.get_chunk(hit["doc"], hit["chunk_id"])["text"]
        assert index.search("BeamSupport", doc=item["id"])["results"][0]["doc"] == item["id"]
    assert index.search("BeamSupport")["count"] == 1


def test_unchanged_manifest_search_does_not_rescan_corpus(library, monkeypatch):
    corpus, catalog, _ = library
    item = document(corpus, "cached")
    write_catalog(catalog, [item])
    index.build_index()

    def unexpected_scan(*_args, **_kwargs):
        raise AssertionError("unchanged manifest must not rescan source files")

    monkeypatch.setattr(index, "_catalog_documents", unexpected_scan)
    monkeypatch.setattr(index, "_catalog_fingerprint", unexpected_scan)
    assert index.search("BeamSupport")["results"][0]["doc"] == item["id"]
    replacement = catalog.with_suffix(".replacement")
    write_catalog(replacement, [{**item, "title": "updated catalog title"}])
    replacement.replace(catalog)
    assert index._needs_rebuild()


def test_default_api_scope_includes_curated_and_catalog(library, monkeypatch):
    corpus, catalog, _ = library
    source = config.SOURCE_DIR
    source.mkdir()
    (source / "Curated.md").write_text("# API\nBeamSupport official API.\n", encoding="utf-8")
    monkeypatch.setattr(config, "API_DOCS", [{"name": "Curated", "title": "Curated",
        "category": "api_reference", "product": "mechanical"}])
    write_catalog(catalog, [document(corpus, "catalog-api"),
                            document(corpus, "catalog-guide", category="guide")])
    index.build_index()
    assert {hit["doc"] for hit in index.search("BeamSupport")["results"]} == {"Curated", "catalog-api"}


def test_relocation_keeps_document_id_and_pdf_provenance(library):
    corpus, catalog, _ = library
    item = document(corpus, "persistent-id")
    pdf = corpus / "Fluent" / "manual.pdf"
    pdf.write_bytes(b"%PDF-1.4 sample source")
    item.update(text_path=item["path"], path=pdf.relative_to(corpus).as_posix(),
                sha256=hashlib.sha256(pdf.read_bytes()).hexdigest())
    write_catalog(catalog, [item])
    index.build_index()
    moved = pdf.with_name("renamed.pdf")
    pdf.rename(moved)
    item["path"] = moved.relative_to(corpus).as_posix()
    write_catalog(catalog, [item])
    hit = index.search("BeamSupport")["results"][0]
    assert hit["doc"] == "persistent-id"
    assert Path(hit["source_path"]) == moved


def test_quality_rejects_stubs_templates_and_pdf_without_text(library):
    corpus, catalog, _ = library
    valid = document(corpus, "valid")
    stub = document(corpus, "stub", quality="stub")
    template = document(corpus, "template", quality="template")
    pdf = corpus / "raw.pdf"
    pdf.write_bytes(b"%PDF-1.4 raw")
    raw = {**valid, "id": "pdf", "path": "raw.pdf",
           "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest()}
    write_catalog(catalog, [valid, stub, template, raw])
    index.build_index()
    assert [hit["doc"] for hit in index.search("BeamSupport")["results"]] == ["valid"]


def test_catalog_text_view_replaces_invalid_utf8_without_changing_source_hash(library):
    corpus, catalog, _ = library
    item = document(corpus, "mixed-encoding")
    view = corpus / "_catalog" / "legacy.md"
    view.parent.mkdir(parents=True, exist_ok=True)
    view.write_bytes(b"# Mixed\nBeamSupport legacy API. \xa1\n")
    item["text_path"] = view.relative_to(corpus).as_posix()
    write_catalog(catalog, [item])
    assert index.build_index()["catalog_indexed_count"] == 1
    result = index.search("BeamSupport", product="fluent")
    assert result["results"][0]["doc"] == item["id"]
    assert "BeamSupport" in index.get_chunk(item["id"], result["results"][0]["chunk_id"])["text"]


def test_stale_source_hash_and_missing_file_preserve_previous_index(library):
    corpus, catalog, clean = library
    item = document(corpus, "safe")
    write_catalog(catalog, [item])
    index.build_index()
    previous = config.INDEX_PATH.read_bytes()
    views = set(clean.glob("docs-views-*"))
    path = corpus / item["path"]
    path.write_text("# Changed\nChangedSupport is a new API revision.\n", encoding="utf-8")
    assert not index._needs_rebuild()
    write_catalog(catalog, [item])
    assert index._needs_rebuild()
    with pytest.raises(ValueError, match="雜湊不符"):
        index.build_index()
    assert config.INDEX_PATH.read_bytes() == previous
    assert set(clean.glob("docs-views-*")) == views
    path.unlink()
    with pytest.raises(RuntimeError, match="來源缺失"):
        index.build_index()
    assert config.INDEX_PATH.read_bytes() == previous


def test_same_claimed_hash_does_not_skip_verification_of_second_source(library):
    corpus, catalog, clean = library
    first = document(corpus, "first")
    write_catalog(catalog, [first])
    index.build_index()
    previous = config.INDEX_PATH.read_bytes()
    previous_views = set(clean.glob("docs-views-*"))

    second = document(corpus, "second", "v261")
    assert second["sha256"] == first["sha256"]
    (corpus / second["path"]).write_text("# Changed\nCorrupted second source.\n", encoding="utf-8")
    write_catalog(catalog, [first, second])
    with pytest.raises(ValueError, match="雜湊不符"):
        index.build_index()
    assert config.INDEX_PATH.read_bytes() == previous
    assert set(clean.glob("docs-views-*")) == previous_views


def test_path_escape_and_empty_catalog_do_not_replace_index(library):
    corpus, catalog, _ = library
    item = document(corpus, "safe")
    write_catalog(catalog, [item])
    index.build_index()
    previous = config.INDEX_PATH.read_bytes()
    write_catalog(catalog, [{**item, "path": "../outside.md"}])
    with pytest.raises(ValueError, match="路徑越界"):
        index.build_index()
    assert config.INDEX_PATH.read_bytes() == previous
    write_catalog(catalog, [])
    with pytest.raises(RuntimeError, match="保留現有索引"):
        index.build_index()
    assert config.INDEX_PATH.read_bytes() == previous

@pytest.mark.parametrize("invalid", ["payload", "sdk_type", "duplicate_id"])
def test_invalid_catalog_shape_preserves_index(library, invalid):
    corpus, catalog, _ = library
    item = document(corpus, "safe")
    write_catalog(catalog, [item])
    index.build_index()
    previous = config.INDEX_PATH.read_bytes()
    if invalid == "payload":
        catalog.write_text("[]", encoding="utf-8")
    elif invalid == "sdk_type":
        write_catalog(catalog, [{**item, "sdk_version": []}])
    else:
        write_catalog(catalog, [item, item])
    with pytest.raises(ValueError, match="保留現有索引"):
        index.build_index()
    assert config.INDEX_PATH.read_bytes() == previous


def test_failed_curated_rebuild_keeps_original_cleaned_view(library, monkeypatch):
    _, _, clean = library
    source = config.SOURCE_DIR
    source.mkdir()
    for name in ["One", "Two"]:
        (source / f"{name}.md").write_text(f"# {name}\nBeamSupport reference.\n", encoding="utf-8")
    monkeypatch.setattr(config, "API_DOCS", [{"name": name, "title": name,
        "category": "api_reference", "product": "mechanical"} for name in ["One", "Two"]])
    built = index.build_index()
    old_view = Path(built["views_path"]) / "One.md"
    previous_text = old_view.read_text(encoding="utf-8")
    (source / "One.md").write_text("# Changed\nUnexpected replacement.\n", encoding="utf-8")
    (source / "Two.md").unlink()
    with pytest.raises(RuntimeError, match="保留現有索引"):
        index.build_index()
    assert old_view.read_text(encoding="utf-8") == previous_text
    assert len(list(clean.glob("docs-views-*"))) == 1


def test_mcp_search_forwards_optional_filters(monkeypatch):
    from ansys_unified_mcp.tools import docs_tools

    calls = []
    monkeypatch.setattr(docs_tools.docs_index, "search", lambda *args, **kwargs:
                        calls.append((args, kwargs)) or {"ok": True, "results": []})
    docs_tools.search_ansys_docs("BeamSupport", product="fluent", release="v251",
                                category="api_reference", sdk_version="0.30.0")
    assert calls[0][1] == {"doc": None, "top_k": 5, "scope": "api", "product": "fluent",
                           "release": "v251", "category": "api_reference", "sdk_version": "0.30.0"}
