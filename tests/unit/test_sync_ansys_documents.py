"""文件維護流程的資料保護、來源與版本驗收。"""
import hashlib
import io
import json
from pathlib import Path
import shutil
import zipfile

import pytest

from scripts.maintenance import sync_ansys_documents as sync


def product():
    return {"product": "fluent", "folder": "Fluent", "sdk_package": "ansys-fluent-core", "sdk_url": "https://fluent.docs.pyansys.com/version/stable/"}


def test_dry_run_does_not_create_corpus(tmp_path, capsys):
    sources = tmp_path / "sources.json"
    sources.write_text(json.dumps({"products": [product()]}), encoding="utf-8")
    root = tmp_path / "documents"
    assert sync.main(["sync", "--root", str(root), "--sources", str(sources)]) == 0
    assert json.loads(capsys.readouterr().out)["dry_run"] is True
    assert not root.exists()


@pytest.mark.parametrize("relative", ["../outside.pdf", "C:/outside.pdf", "/outside.pdf"])
def test_path_escape_is_rejected(tmp_path, relative):
    with pytest.raises(ValueError):
        sync.safe_path(tmp_path, relative)


def test_zip_traversal_is_rejected_before_extracting(tmp_path):
    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as package:
        package.writestr("valid.txt", "keep")
        package.writestr("../outside.txt", "escape")
    with pytest.raises(ValueError):
        sync.safe_extract(archive, tmp_path / "extracted")
    assert not (tmp_path / "extracted/valid.txt").exists()
    assert not (tmp_path / "outside.txt").exists()


def test_tar_subprocess_failure_is_persisted_and_next_bundle_continues(tmp_path, monkeypatch):
    import subprocess

    calls = []

    def fetch(url):
        return b"PK\x03\x04bad zip", url

    def extract(_archive, _destination):
        calls.append(_archive.name)
        if len(calls) == 1:
            raise subprocess.CalledProcessError(2, ["tar", "-xf"])
        return 1

    monkeypatch.setattr(sync, "fetch", fetch)
    monkeypatch.setattr(sync, "safe_extract", extract)
    sources = {"products": [], "downloads": [
        {"product": "act", "release": "v251", "url": "https://storage.ansys.com/a.zip", "path": "ACT/v251/a.zip"},
        {"product": "act", "release": "v261", "url": "https://storage.ansys.com/b.zip", "path": "ACT/v261/b.zip"},
    ]}
    result = sync.synchronize(tmp_path, sources, {"act"}, 1, 1)
    rows = {row["release"]: row for row in result["records"] if row.get("phase") == "bundle"}
    assert rows["v251"]["status"] == "failed"
    assert rows["v261"]["status"] == "downloaded"
    assert len(calls) == 2


def test_tar_fallback_checks_paths_before_extracting(tmp_path, monkeypatch):
    if not shutil.which("tar"):
        pytest.skip("tar not installed")
    archive = tmp_path / "bad-zip64.zip"
    with zipfile.ZipFile(archive, "w") as package:
        package.writestr("valid.txt", "keep")
        package.writestr("../outside.txt", "escape")

    class BadZip:
        def __init__(self, *_args, **_kwargs):
            raise zipfile.BadZipFile("ZIP64 end record")

    monkeypatch.setattr(sync.zipfile, "ZipFile", BadZip)
    with pytest.raises(ValueError):
        sync.safe_extract(archive, tmp_path / "extracted")
    assert not (tmp_path / "extracted/valid.txt").exists()
    assert not (tmp_path / "outside.txt").exists()


def test_tar_fallback_extracts_valid_zip64_compatible_archive(tmp_path, monkeypatch):
    if not shutil.which("tar"):
        pytest.skip("tar not installed")
    archive = tmp_path / "fallback.zip"
    with zipfile.ZipFile(archive, "w") as package:
        package.writestr("nested/reference.html", "official API text")

    class BadZip:
        def __init__(self, *_args, **_kwargs):
            raise zipfile.BadZipFile("ZIP64 end record")

    monkeypatch.setattr(sync.zipfile, "ZipFile", BadZip)
    destination = tmp_path / "extracted"
    assert sync.safe_extract(archive, destination) == 1
    assert (destination / "nested/reference.html").read_text() == "official API text"


def test_zip_collision_preserves_existing_content(tmp_path):
    destination = tmp_path / "files"
    destination.mkdir()
    (destination / "input.txt").write_text("user work", encoding="utf-8")
    archive = tmp_path / "bundle.zip"
    with zipfile.ZipFile(archive, "w") as package:
        package.writestr("input.txt", "other")
    with pytest.raises(FileExistsError):
        sync.safe_extract(archive, destination)
    assert (destination / "input.txt").read_text() == "user work"


def test_changed_cached_publisher_file_is_fetched_again(tmp_path, monkeypatch):
    relative = "Fluent/v251/manuals/guide.pdf"
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_bytes(b"locally changed file")
    url = "https://ansyshelp.ansys.com/public/v251/guide.pdf"
    sync.atomic_json(tmp_path / "_catalog/downloads.json", {"records": [{
        "source_url": url, "path": relative, "sha256": "0" * 64, "status": "downloaded",
    }]})
    expected = b"%PDF-official current body"
    calls = []

    def fetch(requested, *_args):
        calls.append(requested)
        return expected, requested

    monkeypatch.setattr(sync, "fetch", fetch)
    sources = {"products": [], "downloads": [{"product": "fluent", "release": "v251", "url": url, "path": relative, "category": "manual"}]}
    result = sync.synchronize(tmp_path, sources, {"fluent"}, 10, 1)
    row = next(item for item in result["records"] if item.get("source_url") == url and item["status"] == "downloaded")
    assert calls == [url]
    assert row["path"] != relative
    assert path.read_bytes() == b"locally changed file"
    assert (tmp_path / row["path"]).read_bytes() == expected


def test_non_official_source_is_rejected():
    assert sync.official_url("https://fluent.docs.pyansys.com/version/stable/")
    assert sync.official_url("https://raw.githubusercontent.com/ansys/pyfluent/main/example.py")
    assert sync.official_url("https://developer.ansys.com/docs/mechanical-scripting-interface-2025/index.md")
    assert not sync.official_url("https://docs.pyansys.com.attacker.example/")
    assert not sync.official_url("https://github.com/other/pyfluent")
    assert not sync.official_url("http://fluent.docs.pyansys.com/")


def test_html_normalization_keeps_body_code_and_absolute_source_links():
    raw = b'<html><title>PyFluent 0.38 documentation</title><nav>ignore me</nav><main><h1>Guide</h1><p>Official guide text with enough meaningful content to become a searchable document.</p><pre>x = 2\nprint(x)</pre><a href="../api/index.html">API</a></main></html>'
    title, text, links = sync.html_text(raw, "https://fluent.docs.pyansys.com/version/stable/user_guide/index.html")
    assert "ignore me" not in text
    assert "```\nx = 2" in text
    assert "https://fluent.docs.pyansys.com/version/stable/api/index.html" in links
    assert sync.quality(text) == "body_present"


def test_html_body_without_main_remains_searchable():
    raw = b"<html><title>ACT reference</title><body><h1>Method</h1><p>" + b"Official method description. " * 10 + b"</p></body></html>"
    _title, text, _links = sync.html_text(raw, "https://storage.ansys.com/ACT/v261/method.html")
    assert "Official method description." in text


def test_login_page_and_unexpanded_templates_do_not_count_as_body():
    with pytest.raises(ValueError):
        sync.html_text(b"<html><title>Sign in</title><form>login</form></html>", "https://ansyshelp.ansys.com/")
    assert sync.quality(".. toctree::\n" + "template " * 30) == "template"


def test_template_like_code_inside_fence_remains_body():
    text = "```python\nvalue = f\"{{width}}\"\n" + "# valid source line\n" * 12 + "```"
    assert sync.quality(text) == "body_present"


def test_math_placeholders_remain_body_but_jinja_control_is_template():
    text = "Matrix notation {{a,b},{c,d}} and {{domain}}. " * 8
    assert sync.quality(text) == "body_present"
    assert sync.quality("{% for page in pages %}\n" + "template " * 30) == "template"


def test_revised_download_keeps_original_bytes(tmp_path):
    original = sync.save_file(tmp_path, "Fluent/v251/guide.md", b"first version")
    revised = sync.save_file(tmp_path, "Fluent/v251/guide.md", b"revised version")
    assert original != revised
    assert original.read_bytes() == b"first version"
    assert revised.read_bytes() == b"revised version"


def test_catalog_id_survives_move_and_body_revision_changes_id(tmp_path):
    root = tmp_path / "docs"
    path = root / "Fluent/v251/guides_and_tutorials/guide.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\nsource_url: https://ansyshelp.ansys.com/public/corp/v251/guide.html\n---\n" + "Searchable guide body. " * 20, encoding="utf-8")
    sources = {"products": [product()]}
    first = sync.make_catalog(root, sources)["documents"][0]
    moved = path.with_name("moved-guide.md")
    path.rename(moved)
    second = sync.make_catalog(root, sources)["documents"][0]
    assert first["id"] == second["id"]
    assert second["release"] == "v251"
    moved.write_text(moved.read_text() + "changed", encoding="utf-8")
    third = sync.make_catalog(root, sources)["documents"][0]
    assert second["id"] != third["id"]
    assert third["sha256"] == hashlib.sha256(moved.read_bytes()).hexdigest()


def test_sdk_document_does_not_claim_product_release_from_version_number(tmp_path):
    root = tmp_path / "docs"
    page = sync.save_file(root, "Fluent/sdk/ansys-fluent-core/0.38.0/guide/a.html", b"<main>raw</main>")
    text = sync.save_file(root, "Fluent/sdk/ansys-fluent-core/0.38.0/guide/a.md", b"A useful API guide. " * 30)
    sync.atomic_json(root / "_catalog/downloads.json", {"records": [{"status": "downloaded", "product": "fluent", "release": "unknown", "sdk_package": "ansys-fluent-core", "sdk_version": "0.38.0", "path": page.relative_to(root).as_posix(), "text_path": text.relative_to(root).as_posix(), "category": "guide", "source_url": "https://fluent.docs.pyansys.com/version/stable/user_guide/a.html"}]})
    catalog = sync.make_catalog(root, {"products": [product()]})
    assert len(catalog["documents"]) == 1
    record = catalog["documents"][0]
    assert record["release"] == "unknown"
    assert record["sdk_version"] == "0.38.0"
    assert record["quality"] == "body_present"


def test_coverage_never_calls_overview_complete(tmp_path):
    root = tmp_path / "docs"
    root.mkdir()
    result = sync.write_coverage(root, {"products": [product()]}, {"documents": []})
    assert all(row["status"] == "not_verified" for row in result["rows"])
    assert {row["release"] for row in result["rows"]} == {"unknown"}


def test_sdk_version_comes_from_publisher_options_not_stable(monkeypatch):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup('<html><title>PyMechanical</title><script src="_static/documentation_options.js?v=123"></script></html>', "html.parser")
    requested = []

    def download(url, max_bytes):
        requested.append(url)
        return b"const DOCUMENTATION_OPTIONS = {VERSION: '0.13.2'};", url

    monkeypatch.setattr(sync, "fetch", download)
    version, source = sync.sdk_metadata(soup, "https://mechanical.docs.pyansys.com/")
    assert version == "0.13.2"
    assert source == requested[0]
    assert "documentation_options.js" in source


def test_pdf_extraction_writes_sidecar_and_preserves_existing_markdown(tmp_path, monkeypatch):
    import sys
    import json
    import hashlib
    from types import SimpleNamespace

    created_pdf = tmp_path / "SpaceClaim/v261/manuals/Guide.pdf"
    existing_pdf = tmp_path / "Mechanical/v261/manuals/Guide.pdf"
    skipped_pdf = tmp_path / "SpaceClaim/v251/manuals/Other.pdf"
    created_pdf.parent.mkdir(parents=True)
    existing_pdf.parent.mkdir(parents=True)
    skipped_pdf.parent.mkdir(parents=True)
    created_pdf.write_bytes(b"created pdf")
    existing_pdf.write_bytes(b"existing pdf")
    skipped_pdf.write_bytes(b"must not be processed")
    existing_markdown = existing_pdf.with_suffix(".md")
    existing_markdown.write_text("Existing user markdown; preserve this file.", encoding="utf-8")
    extracted = "<!-- page 1 -->\n" + "Extracted page text. " * 20

    def run(command, **kwargs):
        compile(command[2], "pdf-extraction", "exec")
        assert kwargs["encoding"] == "utf-8"
        payload = json.loads(kwargs["input"])
        report_path = Path(payload["report_path"])
        report_path.parent.mkdir(parents=True, exist_ok=True)
        rows = []
        for value in payload["paths"]:
            pdf = Path(value)
            digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
            cache_relative = f"_catalog/pdf_text_v2/{digest}.md"
            cache = Path(payload["root"]) / cache_relative
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(extracted, encoding="utf-8")
            rows.append({
                "path": pdf.relative_to(payload["root"]).as_posix(),
                "sha256": digest,
                "text_path": cache_relative,
                "status": "extracted",
            })
        report_path.write_text(json.dumps({"records": rows}), encoding="utf-8")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(sync.subprocess, "run", run)
    result = sync.extract_pdf_text(
        tmp_path,
        python=Path(sys.executable),
        selected_paths=[
            "SpaceClaim/v261/manuals/Guide.pdf",
            "Mechanical/v261/manuals/Guide.pdf",
        ],
    )
    rows = {row["path"]: row for row in result["records"]}
    created_rel = "SpaceClaim/v261/manuals/Guide.pdf"
    existing_rel = "Mechanical/v261/manuals/Guide.pdf"
    created_row = rows[created_rel]
    existing_row = rows[existing_rel]
    assert created_row["markdown_status"] == "created_from_cache"
    assert created_row["text_path"] == created_row["markdown_path"] == created_rel[:-4] + ".md"
    assert (created_pdf.with_suffix(".md")).read_text(encoding="utf-8") == extracted
    assert existing_row["markdown_status"] == "existing_different_preserved"
    assert existing_row["text_path"].startswith("_catalog/pdf_text_v2/")
    assert existing_row["markdown_path"] == existing_rel[:-4] + ".md"
    assert existing_markdown.read_text(encoding="utf-8") == "Existing user markdown; preserve this file."
    assert "SpaceClaim/v251/manuals/Other.pdf" not in rows
    assert not skipped_pdf.with_suffix(".md").exists()
    assert not (tmp_path / "_catalog" / ".pdf-extraction-result.json").exists()


def test_portal_angle_link_from_actual_failure_is_normalized(tmp_path, monkeypatch):
    entry = "https://developer.synopsys.com/docs/avxcelerate.md"
    target = "https://developer.synopsys.com/docs/avxcelerate-asset-preparation-api-2026-r1/index.md"
    requested = []

    def fetch(url, max_bytes):
        assert not any(character in url for character in " <>")
        requested.append(url)
        if url == entry:
            return b"# Overview\n[2026 R1](</docs/avxcelerate-asset-preparation-api-2026-r1/index.md >)", url
        assert url == target
        return b"# API Reference\n" + b"Publisher method reference. " * 20, url

    monkeypatch.setattr(sync, "fetch", fetch)
    records = sync.synchronize_portal({"product": "avxcelerate", "folder": "AVxcelerate", "overview_url": entry}, tmp_path, 5)
    assert requested == [entry, target]
    assert records[-1]["release"] == "v261"
    assert all(row["status"] == "downloaded" for row in records)
    assert sync.normalize_url(" <https://developer.synopsys.com/docs/a b.md > ") == "https://developer.synopsys.com/docs/a%20b.md"


def test_invalid_url_is_recorded_as_failed(tmp_path, monkeypatch):
    def invalid(*args):
        raise sync.http.client.InvalidURL("URL contains whitespace")

    monkeypatch.setattr(sync, "fetch", invalid)
    records = sync.synchronize_portal({"product": "fluent", "folder": "Fluent", "overview_url": "https://developer.synopsys.com/docs/fluent.md"}, tmp_path, 3)
    assert records[0]["status"] == "failed"
    assert "whitespace" in records[0]["error"]


def test_completed_sdk_state_survives_later_portal_failure(tmp_path, monkeypatch):
    configuration = {**product(), "overview_url": "https://developer.synopsys.com/docs/fluent.md"}

    def sdk(*args):
        return [{"product": "fluent", "source_url": configuration["sdk_url"], "status": "downloaded", "path": "Fluent/page.html", "sha256": "e" * 64}]

    def portal(*args):
        state = sync.load_json(tmp_path / "_catalog/downloads.json", {})
        assert state["records"][0]["status"] == "downloaded"
        raise RuntimeError("publisher response changed")

    monkeypatch.setattr(sync, "synchronize_sdk", sdk)
    monkeypatch.setattr(sync, "synchronize_portal", portal)
    result = sync.synchronize(tmp_path, {"products": [configuration]}, set(), 10, 1)
    assert {row["status"] for row in result["records"]} == {"downloaded", "failed"}
    persisted = sync.load_json(tmp_path / "_catalog/downloads.json", {})
    assert len(persisted["records"]) == 2


def test_orphan_sdk_cache_recovers_without_network(tmp_path, monkeypatch):
    url = "https://fluent.docs.pyansys.com/version/stable/user_guide/index.html"
    slug = hashlib.sha256(url.encode()).hexdigest()[:12] + "-index"
    directory = tmp_path / "Fluent/sdk/ansys-fluent-core/0.38.0/guide"
    directory.mkdir(parents=True)
    raw = b"<main>Cached official body</main>"
    (directory / (slug + ".html")).write_bytes(raw)
    (directory / (slug + ".md")).write_text(f"---\nsource_url: {url}\n---\nCached body", encoding="utf-8")

    def unexpected(*args):
        pytest.fail("orphan cache should avoid HTTP")

    monkeypatch.setattr(sync, "fetch", unexpected)
    assert sync.cached_sdk_page(product(), tmp_path, url, {}) == (raw, url)


def test_tutorial_runtime_download_is_not_counted_as_ready(tmp_path, monkeypatch):
    base = product()["sdk_url"]
    pages = {
        base: b'<title>Documentation 1.2</title><main>' + b"Publisher documentation overview. " * 6 + b'<a href="user_guide/index.html">Guide</a></main>',
        "https://fluent.docs.pyansys.com/version/stable/user_guide/index.html": b'<title>Guide</title><main>' + b"Guide material. " * 8 + b'<a href="../examples/index.html">Examples</a></main>',
        "https://fluent.docs.pyansys.com/version/stable/examples/index.html": b'<title>Examples</title><main>' + b"Examples overview. " * 8 + b'<a href="bracket.html">Bracket</a></main>',
        "https://fluent.docs.pyansys.com/version/stable/examples/bracket.html": b'<title>Bracket</title><main><p>' + b"Use examples.download_bracket() to fetch the input case. " * 3 + b"</p></main>",
    }

    def fetch(url, *_args):
        return pages[url], url

    monkeypatch.setattr(sync, "fetch", fetch)
    rows = sync.synchronize_sdk(product(), tmp_path, {}, 10)
    bracket = next(row for row in rows if row.get("title") == "Bracket")
    assert bracket["input_status"] == "input_pending"
    assert next(row for row in rows if row.get("title") == "Examples")["input_status"] == "not_applicable"
    assert bracket["input_files"] == []


def test_catalog_rechecks_cached_tutorial_input_status(tmp_path):
    root = tmp_path / "docs"
    path = root / "Fluent/sdk/ansys-fluent-core/1.2/tutorial/example.md"
    path.parent.mkdir(parents=True)
    path.write_text("Use examples.download_bracket() to fetch the input. " + "Example body. " * 20, encoding="utf-8")
    sync.atomic_json(root / "_catalog/downloads.json", {"records": [{
        "product": "fluent", "release": "unknown", "sdk_package": "ansys-fluent-core",
        "sdk_version": "1.2", "category": "tutorial", "title": "Cached example",
        "source_url": "https://fluent.docs.pyansys.com/example", "path": path.relative_to(root).as_posix(),
        "sha256": sync.digest_file(path), "status": "downloaded", "is_core": True, "input_status": "ready",
    }]})
    catalog = sync.make_catalog(root, {"products": [{"product": "fluent", "folder": "Fluent"}]})
    assert catalog["documents"][0]["input_status"] == "input_pending"


def test_failed_tutorial_attachment_is_not_counted_as_ready(tmp_path, monkeypatch):
    base = product()["sdk_url"]
    pages = {
        base: b'<title>Documentation 1.2</title><main>' + b"Publisher documentation overview. " * 6 + b'<a href="user_guide/index.html">Guide</a></main>',
        "https://fluent.docs.pyansys.com/version/stable/user_guide/index.html": b'<title>Guide</title><main>' + b"Guide material. " * 8 + b'<a href="../examples/index.html">Examples</a></main>',
        "https://fluent.docs.pyansys.com/version/stable/examples/index.html": b'<title>Examples</title><main>' + b"Examples overview. " * 8 + b'<a href="bracket.html">Bracket</a></main>',
        "https://fluent.docs.pyansys.com/version/stable/examples/bracket.html": b'<title>Bracket</title><main><p>' + b"Example setup. " * 15 + b'<a href="../_downloads/input.csv">Input</a></main>',
    }

    def fetch(url, *_args):
        if url.endswith("input.csv"):
            raise OSError("missing example input")
        return pages[url], url

    monkeypatch.setattr(sync, "fetch", fetch)
    rows = sync.synchronize_sdk(product(), tmp_path, {}, 10)
    bracket = next(row for row in rows if row.get("title") == "Bracket")
    assert bracket["input_status"] == "input_pending"


def test_coverage_requires_official_release_and_three_ready_examples(tmp_path):
    root = tmp_path / "docs"
    root.mkdir()
    rows = [{"product": "fluent", "release": "v251", "quality": "body_present", "is_core": True, "source_url": "https://ansyshelp.ansys.com/public/v251/guide.html", "category": category, "input_status": inputs} for category, inputs in [("guide", "not_applicable"), ("api_reference", "not_applicable"), ("tutorial", "ready"), ("tutorial", "ready"), ("tutorial", "input_pending")]]
    report = sync.write_coverage(root, {"products": [product()]}, {"documents": rows})
    assert len(report["rows"]) == 1
    assert report["rows"][0]["missing"] == ["tutorial_inputs"]
    assert report["rows"][0]["input_pending"] == 1
    rows[-1]["input_status"] = "ready"
    report = sync.write_coverage(root, {"products": [product()]}, {"documents": rows})
    assert report["rows"][0]["status"] == "core_present"


def test_tutorial_index_pages_do_not_count_as_examples(tmp_path):
    docs = [
        {"product": "fluent", "release": "v251", "quality": "body_present", "is_core": True, "source_url": "https://ansyshelp.ansys.com/public/v251/guide.html", "category": "guide", "input_status": "not_applicable"},
        {"product": "fluent", "release": "v251", "quality": "body_present", "is_core": True, "source_url": "https://ansyshelp.ansys.com/public/v251/api.html", "category": "api_reference", "input_status": "not_applicable"},
        {"product": "fluent", "release": "v251", "quality": "body_present", "is_core": True, "source_url": "https://fluent.docs.pyansys.com/version/stable/examples/index.html", "category": "tutorial", "input_status": "not_applicable"},
        *[{"product": "fluent", "release": "v251", "quality": "body_present", "is_core": True, "source_url": f"https://fluent.docs.pyansys.com/version/stable/examples/{index}.html", "category": "tutorial", "input_status": "ready"} for index in range(2)],
    ]
    report = sync.write_coverage(tmp_path, {"products": [product()]}, {"documents": docs})
    row = next(item for item in report["rows"] if item["release"] == "v251")
    assert row["ready_examples"] == 2
    assert row["missing"] == ["tutorial_inputs"]


def test_archive_reference_inherits_verified_product_release_category_and_source(tmp_path):
    root = tmp_path / "docs"
    archive = root / "ACT/v251/archives/ACTReferenceHTML.zip"
    archive.parent.mkdir(parents=True)
    html = "<html><title>ExtAPI reference</title><body><h1>AddTotalDeformation</h1><p>" + "Official API definition. " * 15 + "</p></body></html>"
    with zipfile.ZipFile(archive, "w") as package:
        package.writestr("Mechanical/ExtAPI.html", html)
    extracted = archive.parent / "ACTReferenceHTML"
    sync.safe_extract(archive, extracted)
    url = "https://storage.ansys.com/api-a/v251/ACTReferenceHTML.zip"
    sync.atomic_json(root / "_catalog/downloads.json", {"records": [{"product": "act", "release": "v251", "category": "api_reference", "source_url": url, "status": "downloaded", "path": archive.relative_to(root).as_posix(), "sha256": sync.digest_file(archive), "extracted_root": extracted.relative_to(root).as_posix()}]})
    catalog = sync.make_catalog(root, {"products": [{"product": "act", "folder": "ACT"}]})
    document = next(row for row in catalog["documents"] if row["path"].endswith("ExtAPI.html"))
    assert document["category"] == "api_reference"
    assert document["release"] == "v251"
    assert document["product"] == "act"
    assert document["source_url"] == url + "#Mechanical/ExtAPI.html"
    assert document["sha256"] == sync.digest_file(extracted / "Mechanical/ExtAPI.html")
    assert document["quality"] == "body_present"


def test_catalog_normalizes_existing_html_and_keeps_publisher_release(tmp_path):
    root = tmp_path / "docs"
    path = root / "ACT/v251/api_reference/reference.html"
    path.parent.mkdir(parents=True)
    path.write_text('<html><title>Mechanical API</title><body><h1>AddTotalDeformation</h1><p>' + 'Official method definition. ' * 20 + '</p></body></html>', encoding="utf-8")
    sources = {"products": [{"product": "act", "folder": "ACT"}]}
    catalog = sync.make_catalog(root, sources)
    row = catalog["documents"][0]
    assert row["quality"] == "body_present"
    assert row["release"] == "v251"
    assert "AddTotalDeformation" in (root / row["text_path"]).read_text(encoding="utf-8")


def test_catalog_keeps_oversized_html_as_source_attachment(tmp_path):
    root = tmp_path / "docs"
    path = root / "ACT/v261/api_reference/Mechanical/index.html"
    path.parent.mkdir(parents=True)
    path.write_text("<html>" + "x" * 10_000_001 + "</html>", encoding="utf-8")
    catalog = sync.make_catalog(root, {"products": [{"product": "act", "folder": "ACT"}]})
    row = catalog["documents"][0]
    assert row["quality"] == "attachment"
    assert row.get("text_path") is None


def test_catalog_indexes_large_mechanical_api_class_page(tmp_path):
    root = tmp_path / "docs"
    path = root / "ACT/v261/archives/ACTReferenceHTML/Mechanical/Reference.type.Ansys.ACT.Automation.Mechanical.DataModelObject.html"
    path.parent.mkdir(parents=True)
    text = "<html><title>DataModelObject</title><main><h1>DataModelObject</h1><p>" + "Official Mechanical API property description. " * 3_000 + "</p></main></html>"
    path.write_text(text, encoding="utf-8")
    catalog = sync.make_catalog(root, {"products": [{"product": "act", "folder": "ACT"}]})
    row = catalog["documents"][0]
    assert row["quality"] == "body_present"
    assert row.get("text_path")


def test_catalog_does_not_infer_release_from_filename_only(tmp_path):
    root = tmp_path / "docs"
    path = root / "SpaceClaim/unknown/api_reference/Developers Guide_V271.pdf"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"%PDF-unverified local guide")
    catalog = sync.make_catalog(root, {"products": [{"product": "spaceclaim", "folder": "SpaceClaim"}]})
    assert catalog["documents"][0]["release"] == "unknown"


def test_catalog_does_not_classify_lsopt_manual_as_optislang(tmp_path):
    root = tmp_path / "docs"
    pdf = root / "optiSLang/unknown/manuals/lsopt_2026R1_manual.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"%PDF-LS-OPT")
    text_path = root / "_catalog/pdf_text_v2/lsopt_manual.md"
    text_path.parent.mkdir(parents=True)
    text_path.write_text("# LS-OPT 2026 R1\n" + "LS-OPT manual text. " * 20, encoding="utf-8")
    sync.atomic_json(root / "_catalog/pdf_extraction.json", {"records": [{
        "path": pdf.relative_to(root).as_posix(),
        "sha256": sync.digest_file(pdf),
        "text_path": text_path.relative_to(root).as_posix(),
        "status": "extracted",
    }]})

    catalog = sync.make_catalog(root, {"products": [{"product": "optislang", "folder": "optiSLang"}]})

    assert catalog["documents"][0]["product"] == "general"
    assert catalog["documents"][0]["quality"] == "body_present"
