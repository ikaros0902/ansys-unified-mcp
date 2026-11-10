"""Build and query the ANSYS API-docs FTS5 index.

Pipeline: read source markdown -> clean (docs/clean.py) -> write cleaned copy to
Documentation_clean/ -> chunk -> insert into a SQLite FTS5 (trigram) table.

The trigram tokenizer gives case-insensitive English substring matching and
partial CJK matching (Chinese queries need >= 3 characters). Concept-level
Chinese-to-English matching is out of scope for keyword search and is left to a
future semantic layer.
"""

from __future__ import annotations

import sqlite3
import os
import tempfile
import hashlib
import re
import threading
import json
import shutil
from typing import Optional
from pathlib import Path

from ansys_unified_mcp.analytics.docsearch import config as cfg
from ansys_unified_mcp.analytics.docsearch.clean import clean_markdown

_lock = threading.Lock()

# Column order in the FTS5 table: 0=doc, 1=ord, 2=heading, 3=body
_BODY_COL = 3


def _chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Split text into ~size-char chunks, snapping to line boundaries, with overlap."""
    chunks: list[str] = []
    i, n = 0, len(text)
    while i < n:
        end = min(i + size, n)
        if end < n:
            nl = text.rfind("\n", i + size - overlap, end)
            if nl > i:
                end = nl
        chunk = text[i:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        i = max(end - overlap, i + 1)
    return chunks


def _heading_of(chunk: str) -> str:
    """Best-guess label: first non-empty, non-heading-marker line, trimmed."""
    for line in chunk.splitlines():
        s = line.strip().lstrip("#").strip()
        if s:
            return s[:120]
    return ""


def _connect(path=None) -> sqlite3.Connection:
    con = sqlite3.connect(str(path or cfg.INDEX_PATH))
    con.row_factory = sqlite3.Row
    return con

# 來源異動須先原子更新清冊；一般搜尋只比對清冊 stat，建置時才驗證正文。
_catalog_cache: dict = {}


def _catalog_documents() -> list[dict]:
    root = (cfg.DOCS_ROOT / "ANSYS_Document").resolve()
    manifest = root / "_catalog" / "documents.json"
    if not manifest.is_file():
        return []
    payload = json.loads(manifest.read_text(encoding="utf-8-sig"))
    if (not isinstance(payload, dict) or payload.get("schema_version") != 1
            or not isinstance(payload.get("documents"), list)):
        raise ValueError("文件清冊 schema 無效；保留現有索引。")
    documents = []
    seen = set()
    required = {"id", "title", "product", "release", "sdk_package", "sdk_version",
                "category", "source_url", "path", "sha256", "quality"}
    for item in payload["documents"]:
        if not isinstance(item, dict) or not required <= item.keys():
            raise ValueError("文件清冊缺少必要欄位；保留現有索引。")
        if (not all(isinstance(item[key], str) for key in required)
                or not item["id"] or item["id"] in seen
                or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"])):
            raise ValueError("文件清冊 ID、雜湊或欄位型別無效；保留現有索引。")
        seen.add(item["id"])
        if item["id"] == "ansys_b5063da81b499621e083373c":
            item = {**item, "product": "general"}
        if item["quality"] != "body_present":
            continue
        paths = {}
        for key, relative in (("source", item["path"]), ("text", item.get("text_path") or item["path"])):
            if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
                raise ValueError("文件清冊必須使用庫內相對路徑；保留現有索引。")
            path = (root / relative).resolve()
            if not path.is_relative_to(root):
                raise ValueError("文件清冊路徑越界；保留現有索引。")
            if not path.is_file():
                raise RuntimeError(f"文件清冊正文來源缺失；保留現有索引。 path={relative}")
            paths[key] = path
        if paths["text"].suffix.lower() not in {".md", ".markdown"}:
            continue
        documents.append({**item, "_source": paths["source"], "_text": paths["text"]})
    return documents


def _catalog_fingerprint(force: bool = False, documents: list[dict] | None = None) -> str:
    manifest = cfg.DOCS_ROOT / "ANSYS_Document" / "_catalog" / "documents.json"
    try:
        stat = manifest.stat()
        key = (str(manifest.resolve()), stat.st_mtime_ns, stat.st_size)
    except FileNotFoundError:
        return ""
    if not force and _catalog_cache.get("key") == key:
        return _catalog_cache["fingerprint"]
    digest = hashlib.sha256(manifest.read_bytes())
    for item in documents if documents is not None else _catalog_documents():
        for path in (item["_source"], item["_text"]):
            stat = path.stat()
            digest.update(f"{item['id']}:{stat.st_mtime_ns}:{stat.st_size}".encode("utf-8"))
    fingerprint = digest.hexdigest()
    _catalog_cache.update(key=key, fingerprint=fingerprint)
    return fingerprint



def _needs_rebuild() -> bool:
    if not cfg.INDEX_PATH.exists():
        return True
    try:
        con = _connect()
        try:
            cols = {r["name"] for r in con.execute("PRAGMA table_info(docs_meta)")}
            if not {"source_path", "release", "content_hash", "quality", "chunk_count",
                    "source_url", "sdk_package", "sdk_version", "content_key"} <= cols:
                return True
            state = dict(con.execute("SELECT key, value FROM index_state").fetchall())
        finally:
            con.close()
        if json.loads(state.get("extra_source_roots", "[]")) != sorted(
            str(root.resolve()) for root in cfg.EXTRA_SOURCE_DIRS
        ):
            return True
        manifest = cfg.DOCS_ROOT / "ANSYS_Document" / "_catalog" / "documents.json"
        stat = manifest.stat() if manifest.is_file() else None
        manifest_stat = f"{stat.st_mtime_ns}:{stat.st_size}" if stat else ""
        if state.get("catalog_manifest_stat", "") != manifest_stat:
            return True
    except (sqlite3.Error, ValueError, OSError):
        return True
    index_mtime = cfg.INDEX_PATH.stat().st_mtime
    for doc in cfg.API_DOCS:
        src = cfg.SOURCE_DIR / f"{doc['name']}.md"
        if src.exists() and src.stat().st_mtime > index_mtime:
            return True
    return False


def build_index() -> dict:
    """(Re)build the cleaned copies and the FTS5 index. Returns a summary."""
    catalog_documents = _catalog_documents()
    catalog_fingerprint = _catalog_fingerprint(force=True, documents=catalog_documents)
    catalog_manifest_stat = (
        f"{_catalog_cache['key'][1]}:{_catalog_cache['key'][2]}" if catalog_fingerprint else ""
    )
    cfg.CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    views_dir = Path(tempfile.mkdtemp(prefix="docs-views-", dir=str(cfg.CLEAN_DIR)))
    installed = False
    temp_path = None
    try:
        fd, temp_name = tempfile.mkstemp(prefix="docs-index-", suffix=".sqlite", dir=str(cfg.CLEAN_DIR))
        os.close(fd)
        temp_path = temp_name
        con = _connect(temp_path)
        summary: list[dict] = []
        try:
            con.execute(
                "CREATE VIRTUAL TABLE chunks USING fts5("
                "doc UNINDEXED, ord UNINDEXED, heading, body, tokenize='trigram')"
            )
            con.execute("CREATE TABLE index_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            con.execute(
                "CREATE TABLE docs_meta ("
                "name TEXT PRIMARY KEY, title TEXT, category TEXT, product TEXT, "
                "chunk_count INTEGER, chars INTEGER, source_path TEXT, release TEXT, content_hash TEXT, quality TEXT, "
                "source_url TEXT DEFAULT '', sdk_package TEXT DEFAULT '', sdk_version TEXT DEFAULT '', "
                "content_key TEXT)"
            )

            for doc in cfg.API_DOCS:
                src = cfg.SOURCE_DIR / f"{doc['name']}.md"
                if not src.exists():
                    summary.append({"name": doc["name"], "status": "source_missing"})
                    continue

                raw = src.read_text(encoding="utf-8", errors="replace")
                cleaned = clean_markdown(raw, style=doc.get("style", "ansys"))
                (views_dir / f"{doc['name']}.md").write_text(cleaned, encoding="utf-8")

                parts = _chunk_text(cleaned, cfg.CHUNK_SIZE, cfg.CHUNK_OVERLAP)
                con.executemany(
                    "INSERT INTO chunks(doc, ord, heading, body) VALUES (?, ?, ?, ?)",
                    [(doc["name"], i, _heading_of(p), p) for i, p in enumerate(parts)],
                )
                con.execute(
                    "INSERT INTO docs_meta (name,title,category,product,chunk_count,chars,source_path,release,content_hash,quality) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (doc["name"], doc["title"], doc["category"], doc["product"],
                     len(parts), len(cleaned), str(src), _release_hint(raw), hashlib.sha256(raw.encode("utf-8")).hexdigest(), _quality(raw)),
                )
                summary.append({
                    "name": doc["name"], "status": "indexed",
                    "chunks": len(parts), "chars": len(cleaned),
                })

            # 掃描並索引 skills 與 agents/steering/reference
            processed_names = {d["name"] for d in cfg.API_DOCS}
            if (cfg.REPO_ROOT / "agents" / "skills").is_dir():
                skills_path = cfg.REPO_ROOT / "agents" / "skills"
            elif (cfg.REPO_ROOT / "skills").is_dir():
                skills_path = cfg.REPO_ROOT / "skills"
            else:
                skills_path = cfg.REPO_ROOT / "SKILLs"
            steering_ref_path = (cfg.REPO_ROOT / "agents" / "steering" / "reference") if (cfg.REPO_ROOT / "agents" / "steering" / "reference").is_dir() else (cfg.REPO_ROOT / "steering" / "reference")
            scan_paths = [
                (skills_path, "skill"),
                (steering_ref_path, "architecture"),
            ]

            for base_dir, category in scan_paths:
                if not base_dir.exists():
                    continue
                for md_file in base_dir.rglob("*.md"):
                    rel_name = md_file.relative_to(cfg.REPO_ROOT).as_posix().replace("/", "_").replace(".md", "")
                    if rel_name in processed_names:
                        continue
                    processed_names.add(rel_name)
                    title = md_file.stem.replace("_", " ").replace("-", " ").title()

                    lower_path = md_file.as_posix().lower()
                    if "fluent" in lower_path or "mixing_elbow" in lower_path:
                        product = "fluent"
                    elif "aqwa" in lower_path:
                        product = "aqwa"
                    elif "polyflow-icing" in lower_path:
                        product = "fensap_ice" if "icing_physics_setup" in lower_path else "polyflow"
                    elif "dpf" in lower_path or "submodeling" in lower_path:
                        product = "dpf"
                    elif "spaceclaim" in lower_path:
                        product = "spaceclaim"
                    elif "geometry" in lower_path:
                        product = "geometry"
                    elif "mechanical" in lower_path:
                        product = "mechanical"
                    elif "ls-prepost" in lower_path:
                        product = "ls-prepost"
                    elif "lsdyna" in lower_path or "ls-dyna" in lower_path:
                        product = "lsdyna"
                    elif "optislang" in lower_path:
                        product = "optislang"
                    elif "icepak" in lower_path:
                        product = "icepak"
                    elif "sherlock" in lower_path:
                        product = "sherlock"
                    elif "speos" in lower_path or "illumination" in lower_path:
                        product = "speos"
                    elif "zemax" in lower_path or "zos-api" in lower_path:
                        product = "zemax"
                    elif "lumerical" in lower_path or "lumapi" in lower_path:
                        product = "lumerical"
                    elif "thermal" in lower_path:
                        product = "thermal"
                    elif "parametric" in lower_path:
                        product = "parametric_study"
                    elif "pcb" in lower_path:
                        product = "pcb_warpage"
                    elif "workbench" in lower_path:
                        product = "workbench"
                    elif "error" in lower_path:
                        product = "error_catalog"
                    else:
                        product = "general"

                    raw_text = md_file.read_text(encoding="utf-8", errors="replace")
                    if not raw_text.strip():
                        continue

                    parts = _chunk_text(raw_text, cfg.CHUNK_SIZE, cfg.CHUNK_OVERLAP)
                    if not parts:
                        continue

                    con.executemany(
                        "INSERT INTO chunks(doc, ord, heading, body) VALUES (?, ?, ?, ?)",
                        [(rel_name, i, _heading_of(p), p) for i, p in enumerate(parts)],
                    )
                    con.execute(
                        "INSERT OR REPLACE INTO docs_meta (name,title,category,product,chunk_count,chars,source_path,release,content_hash,quality) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (rel_name, title, category, product, len(parts), len(raw_text), str(md_file), _release_hint(raw_text), hashlib.sha256(raw_text.encode("utf-8")).hexdigest(), _quality(raw_text)),
                    )
                    summary.append({
                        "name": rel_name, "status": "indexed",
                        "chunks": len(parts), "chars": len(raw_text),
                    })

            # 額外文件庫採環境設定，不將任何使用者機器路徑寫入程式碼。
            # 只收錄 Markdown；PDF/原始手冊由 inventory 工具盤點，須先轉檔再索引。
            for root in cfg.EXTRA_SOURCE_DIRS:
                if not root.is_dir():
                    summary.append({"name": str(root), "status": "source_missing"})
                    continue
                for md_file in root.rglob("*.md"):
                    low_p = md_file.as_posix().lower()
                    if any(bad in low_p for bad in ("transaction_", "rollback_", "backup", "passes", "docs-views-")):
                        continue
                    try:
                        resolved = md_file.resolve()
                        relative = resolved.relative_to(root.resolve()).as_posix()
                        raw_text = md_file.read_text(encoding="utf-8", errors="replace")
                    except (OSError, ValueError):
                        continue
                    if not raw_text.strip():
                        continue
                    digest = hashlib.sha256(str(resolved).encode("utf-8")).hexdigest()[:12]
                    rel_name = f"external_{digest}_{Path(relative).stem}"
                    if rel_name in processed_names:
                        continue
                    processed_names.add(rel_name)
                    lower = relative.lower()
                    product = next((value for key, value in (
                        ("workbench", "workbench"), ("scade_one", "scade_one"), ("scade", "scade"), ("minerva", "minerva"), ("simai", "simai"), ("act.md", "act"),
                        ("ansys_id_portal", "ansys_id_portal"), ("ansys_id_sso", "ansys_id_sso"), ("ansysem", "ansysem"), ("circuit", "circuit"), ("emit", "emit"), ("lsopt", "lsopt"), ("aqwa", "aqwa"), ("additive", "additive"), ("fensap_ice", "fensap_ice"), ("edupack", "edupack"), ("polyflow", "polyflow"), ("ls-prepost", "ls-prepost"), ("error_catalog", "error_catalog"), ("icem_cfd", "icem_cfd"),
                        ("installation_and_licensing", "installation_and_licensing"), ("pyansys", "pyansys"), ("reaction_chemkin", "reaction_chemkin"), ("saf", "saf"),
                        ("mechanical", "mechanical"), ("geometry.md", "geometry"), ("ls-dyna", "lsdyna"), ("lsdyna", "lsdyna"),
                        ("avxcelerate", "avxcelerate"), ("cff", "cff"), ("discovery", "discovery"), ("twinai", "twinai"),
                        ("rigid_body_dynamics", "rigid_body_dynamics"), ("adr", "adr"), ("turbogrid", "turbogrid"),
                        ("hfss", "hfss"), ("maxwell", "maxwell"), ("q3d", "q3d"), ("siwave", "siwave"),
                        ("dpf", "dpf"), ("cfx", "cfx"), ("mapdl", "mapdl"), ("motorcad", "motorcad"), ("rocky", "rocky"), ("sound", "sound"),
                        ("ls-prepost", "ls-prepost"), ("spaceclaim", "spaceclaim"),
                        ("icepak", "icepak"), ("sherlock", "sherlock"), ("speos", "speos"),
                        ("zemax", "zemax"), ("lumerical", "lumerical"), ("fluent", "fluent"),
                        ("optislang", "optislang"), ("motion", "motion"), ("ensight", "ensight"), ("system_coupling", "system_coupling"), ("thermal_desktop", "thermal_desktop"), ("acp", "acp"), ("primemesh", "primemesh"), ("aedt", "aedt"), ("modelcenter", "modelcenter"), ("granta_mi", "granta_mi"), ("thermal", "thermal"),
                    ) if key in lower), "general")
                    category = (
                        "tutorial" if "tutorial" in lower or "example" in lower else
                        "api_reference" if "api" in lower or "reference" in lower else
                        "guide"
                    )
                    parts = _chunk_text(raw_text, cfg.CHUNK_SIZE, cfg.CHUNK_OVERLAP)
                    release = "unknown" if root.name.lower() == "knowledge_dictionary" else _release_hint(raw_text)
                    con.executemany(
                        "INSERT INTO chunks(doc, ord, heading, body) VALUES (?, ?, ?, ?)",
                        [(rel_name, i, _heading_of(part), part) for i, part in enumerate(parts)],
                    )
                    con.execute(
                        "INSERT INTO docs_meta (name,title,category,product,chunk_count,chars,source_path,release,content_hash,quality) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (rel_name, Path(relative).stem, category, product, len(parts), len(raw_text),
                         str(resolved), release, hashlib.sha256(raw_text.encode("utf-8")).hexdigest(),
                         _quality(raw_text)),
                    )
                    summary.append({"name": rel_name, "status": "indexed", "chunks": len(parts), "chars": len(raw_text)})

            con.execute("UPDATE docs_meta SET content_key=name WHERE content_key IS NULL")
            con.execute("CREATE INDEX docs_meta_content_key ON docs_meta(content_key, name)")
            catalog_ids = []
            verified_sources = {}
            text_cache = {}
            content_stats = {}
            for item in catalog_documents:
                name = item["id"]
                if name in processed_names:
                    raise ValueError(f"清冊 ID 與既有文件衝突；保留現有索引。 id={name}")
                source_hash = item["sha256"]
                source_path = item["_source"]
                if source_path not in verified_sources:
                    with source_path.open("rb") as stream:
                        verified_sources[source_path] = hashlib.file_digest(stream, "sha256").hexdigest()
                if verified_sources[source_path] != source_hash:
                    raise ValueError(f"清冊來源雜湊不符；保留現有索引。 id={name}")
                text_key = (source_hash, item["_text"])
                if text_key not in text_cache:
                    raw = item["_text"].read_text(encoding="utf-8-sig", errors="replace")
                    if _quality(raw) in {"empty", "template"}:
                        text_cache[text_key] = None
                    else:
                        cleaned = clean_markdown(raw)
                        content_key = "catalog_" + hashlib.sha256(cleaned.encode("utf-8")).hexdigest()
                        if content_key not in content_stats:
                            parts = _chunk_text(cleaned, cfg.CHUNK_SIZE, cfg.CHUNK_OVERLAP)
                            if parts:
                                (views_dir / f"{content_key}.md").write_text(cleaned, encoding="utf-8")
                                con.executemany(
                                    "INSERT INTO chunks(doc, ord, heading, body) VALUES (?, ?, ?, ?)",
                                    [(content_key, i, _heading_of(part), part) for i, part in enumerate(parts)],
                                )
                                content_stats[content_key] = (len(parts), len(cleaned))
                        text_cache[text_key] = content_key if content_key in content_stats else None
                content_key = text_cache[text_key]
                if content_key is None:
                    summary.append({"name": name, "status": "quality_rejected"})
                    continue
                chunks, chars = content_stats[content_key]
                product = item["product"]
                # 這些文件的正文產品與清冊目錄分類不符，使用已核對的產品標籤。
                if item["path"] == "Discovery/unknown/manuals/Developers Guide_V232.pdf":
                    product = "spaceclaim"
                elif item["path"] == "TwinAI/unknown/manuals/UsersGuide_1.62.pdf":
                    product = "general"
                elif item["path"].startswith("Circuit/"):
                    product = "circuit"
                elif item["path"].startswith("EMIT/"):
                    product = "emit"
                elif item["path"].startswith("optiSLang/unknown/manuals/lsopt_2026R1_"):
                    product = "lsopt"
                con.execute(
                    "INSERT INTO docs_meta VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (name, item["title"], item["category"], product, chunks,
                     chars, str(item["_source"]), item["release"], source_hash,
                     "body_present", item["source_url"], item["sdk_package"], item["sdk_version"], content_key),
                )
                processed_names.add(name)
                catalog_ids.append(name)
                summary.append({"name": name, "status": "indexed", "chunks": chunks,
                                "chars": chars})

            missing_extra_roots = [str(root) for root in cfg.EXTRA_SOURCE_DIRS if not root.is_dir()]
            if missing_extra_roots:
                raise RuntimeError(
                    "外部文件來源暫時不可用；保留現有索引，不以不完整來源重建。"
                    f" missing_roots={missing_extra_roots}"
                )

            con.execute(
                "INSERT INTO index_state(key, value) VALUES ('extra_source_roots', ?)",
                (json.dumps(sorted(str(root.resolve()) for root in cfg.EXTRA_SOURCE_DIRS)),),
            )
            if catalog_fingerprint != _catalog_fingerprint(force=True, documents=catalog_documents):
                raise RuntimeError("建置期間文件清冊或正文已變更；保留現有索引。")
            con.execute(
                "INSERT INTO index_state(key, value) VALUES ('catalog_fingerprint', ?)",
                (catalog_fingerprint,),
            )
            con.execute(
                "INSERT INTO index_state(key, value) VALUES ('catalog_manifest_stat', ?)",
                (catalog_manifest_stat,),
            )
            con.execute(
                "INSERT INTO index_state(key, value) VALUES ('catalog_count', ?)",
                (str(len(catalog_ids)),),
            )
            con.execute(
                "INSERT INTO index_state(key, value) VALUES ('views_path', ?)",
                (str(views_dir),),
            )
            con.commit()
        except Exception:
            con.close()
            Path(temp_path).unlink(missing_ok=True)
            raise
        finally:
            if con:
                con.close()

        check = _connect(temp_path)
        try:
            indexed_documents = check.execute("SELECT COUNT(*) FROM docs_meta").fetchone()[0]
            chunk_count = check.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
            curated_names = [doc["name"] for doc in cfg.API_DOCS]
            placeholders = ",".join("?" for _ in curated_names)
            curated_indexed_names = {
                row[0] for row in check.execute(
                    f"SELECT name FROM docs_meta WHERE name IN ({placeholders})", curated_names
                ).fetchall()
            }
            integrity = check.execute("PRAGMA integrity_check").fetchone()[0]
            bad_metadata = check.execute(
                "SELECT COUNT(*) FROM docs_meta WHERE source_path IS NULL OR content_hash IS NULL "
                "OR length(content_hash) != 64 OR content_key IS NULL"
            ).fetchone()[0]
        finally:
            check.close()
        previous_curated_names = set()
        previous_catalog_count = 0
        if cfg.INDEX_PATH.is_file():
            previous = None
            try:
                previous = _connect(cfg.INDEX_PATH)
                previous_curated_names = {
                    row[0] for row in previous.execute(
                        f"SELECT name FROM docs_meta WHERE name IN ({placeholders})", curated_names
                    ).fetchall()
                }
                try:
                    row = previous.execute(
                        "SELECT value FROM index_state WHERE key='catalog_count'"
                    ).fetchone()
                    previous_catalog_count = int(row["value"]) if row else 0
                except sqlite3.Error:
                    pass
            except sqlite3.Error:
                previous_curated_names = set()
            finally:
                if previous is not None:
                    previous.close()
        missing_previous = previous_curated_names - curated_indexed_names
        curated_indexed = len(curated_indexed_names)
        if (
            indexed_documents == 0
            or chunk_count == 0
            or (curated_indexed == 0 and not catalog_ids)
            or (previous_catalog_count > 0 and not catalog_ids)
            or missing_previous
            or integrity != "ok"
            or bad_metadata
        ):
            Path(temp_path).unlink(missing_ok=True)
            raise RuntimeError(
                "新文件索引未通過完整性驗證；保留現有索引。"
                f" docs={indexed_documents}, chunks={chunk_count}, curated_docs={curated_indexed}, "
                f"missing_previous_curated={sorted(missing_previous)}, "
                f"integrity={integrity}, bad_metadata={bad_metadata}"
            )

        os.replace(temp_path, cfg.INDEX_PATH)
        installed = True
        for old_views in cfg.CLEAN_DIR.glob("docs-views-*"):
            if old_views.resolve() != views_dir.resolve() and old_views.is_dir():
                shutil.rmtree(old_views, ignore_errors=True)

        return {
            "ok": True,
            "index_path": str(cfg.INDEX_PATH),
            "docs": summary,
            "indexed_count": indexed_documents,
            "chunk_count": chunk_count,
            "curated_indexed_count": curated_indexed,
            "catalog_indexed_count": len(catalog_ids),
            "catalog_content_count": len(content_stats),
            "catalog_verified_source_count": len(verified_sources),
            "views_path": str(views_dir),
        }
    finally:
        if temp_path and not installed:
            Path(temp_path).unlink(missing_ok=True)
        if views_dir and not installed and views_dir.exists():
            if not views_dir.resolve().is_relative_to(cfg.CLEAN_DIR.resolve()):
                raise RuntimeError("暫存文字路徑越界；拒絕清理。")
            shutil.rmtree(views_dir, ignore_errors=True)


def _release_hint(text: str) -> str:
    match = re.search(r"\b(20\d{2}\s*R[12]|v(?:251|252|261))\b", text[:12000], re.I)
    return match.group(1) if match else "unknown"


def _quality(text: str) -> str:
    if not text.strip():
        return "empty"
    if len(text) < 12000 and re.search(r"download|not available|contents only", text[:4000], re.I):
        return "stub_or_download_page"
    outside_code = re.sub(r"(?ms)^[ \t]{0,3}(`{3,}|~{3,})[^\n]*\n.*?^[ \t]{0,3}\1[ \t]*$", "", text)
    jinja_control = re.search(r"\{%[-+]?\s*(?:for|if|elif|else|set|block|macro|include|extends|endfor|endif|endblock|endmacro|endwith|endfilter|raw|endraw|filter|call|with|autoescape|endautoescape|trans|pluralize|import|from|do)\b", outside_code)
    if jinja_control:
        return "template"
    return "body_present"


def ensure_index(force: bool = False) -> Optional[dict]:
    """Build the index if missing/stale (or when forced). Thread-safe."""
    with _lock:
        if force or _needs_rebuild():
            return build_index()
    return None


def _match_query(query: str) -> str:
    """Build an FTS5 MATCH expression from a raw user query.

    Each whitespace-separated term becomes its own quoted phrase and the terms
    are AND-ed (FTS5 treats space-separated phrases as AND). This makes
    multi-word queries match documents containing all terms in any order,
    rather than requiring the exact contiguous phrase.

    The trigram tokenizer cannot match tokens shorter than 3 characters, so
    such terms are dropped. If nothing remains (e.g. an all-short query), fall
    back to quoting the whole query as a single phrase.
    """
    def quote(term: str) -> str:
        return '"' + term.replace('"', '""') + '"'

    terms = [t for t in query.split() if len(t) >= 3]
    if not terms:
        return quote(query.strip())
    return " ".join(quote(t) for t in terms)


def _run_search(con: sqlite3.Connection, query: str, doc_names: Optional[list[str]], top_k: int,
                product: Optional[str] = None, release: Optional[str] = None,
                category: Optional[str] = None, sdk_version: Optional[str] = None,
                primary_only: bool = False) -> list:
    """每個正文選出一個符合篩選的文件 alias，避免跨版本重複命中。"""
    alias_sql = "SELECT name FROM docs_meta AS aliases WHERE aliases.content_key=chunks.doc"
    params: list = []
    if doc_names:
        placeholders = ",".join("?" for _ in doc_names)
        alias_sql += f" AND aliases.name IN ({placeholders})"
        params.extend(doc_names)
    if primary_only:
        placeholders = ",".join("?" for _ in cfg.PRIMARY_CATEGORIES)
        alias_sql += f" AND aliases.category IN ({placeholders})"
        params.extend(cfg.PRIMARY_CATEGORIES)
    for field, value in (("product", product), ("release", release), ("category", category),
                         ("sdk_version", sdk_version)):
        if value is not None:
            alias_sql += f" AND aliases.{field}=?"
            params.append(value)
    alias_sql += " ORDER BY aliases.name LIMIT 1"
    sql = (
        "SELECT docs_meta.name AS doc, chunks.ord, chunks.heading, docs_meta.source_path, "
        "docs_meta.release, docs_meta.product, docs_meta.category, "
        "docs_meta.source_url, docs_meta.sdk_package, docs_meta.sdk_version, "
        "snippet(chunks, {col}, '[[', ']]', ' … ', 16) AS snip, "
        "bm25(chunks) AS score "
        "FROM chunks JOIN docs_meta ON docs_meta.name=({alias_sql}) "
        "WHERE chunks MATCH ? ORDER BY score LIMIT ?"
    ).format(col=_BODY_COL, alias_sql=alias_sql)
    params.extend((_match_query(query), int(top_k)))
    return con.execute(sql, params).fetchall()


def search(query: str, doc: Optional[str] = None, top_k: int = 5, scope: str = "api",
           product: Optional[str] = None, release: Optional[str] = None,
           category: Optional[str] = None, sdk_version: Optional[str] = None) -> dict:
    """Keyword-search the docs.

    scope:
        "api" (default) - search only the crisp API docs (PRIMARY_CATEGORIES);
            if that yields nothing, transparently widen to all docs.
        "all"           - search every indexed doc (API + guide + tutorial).
        Ignored when `doc` is given (an explicit doc always wins).
    """
    ensure_index()
    if not query or not query.strip():
        return {"ok": False, "error": "query 不得為空。"}

    scope = scope if scope in ("api", "all") else "api"
    if doc:
        doc_names: Optional[list[str]] = [doc]
        used_scope = "doc"
    elif scope == "api":
        doc_names = None
        used_scope = "api"
    else:
        doc_names = None
        used_scope = "all"

    con = _connect()
    try:
        rows = _run_search(con, query, doc_names, top_k, product, release, category,
                           sdk_version, primary_only=used_scope == "api")
        # Fallback: narrow API search found nothing -> widen to all docs.
        if not rows and used_scope == "api":
            rows = _run_search(con, query, None, top_k, product, release, category, sdk_version)
            used_scope = "all"
    except sqlite3.OperationalError as exc:
        return {"ok": False, "error": f"search failed: {exc}"}
    finally:
        con.close()

    results = [
        {
            "doc": r["doc"],
            "chunk_id": r["ord"],
            "heading": r["heading"],
            "snippet": r["snip"],
            "score": round(r["score"], 3),
            "source_path": r["source_path"],
            "release": r["release"],
            "product": r["product"],
            "category": r["category"],
            "source_url": r["source_url"],
            "sdk_package": r["sdk_package"],
            "sdk_version": r["sdk_version"],
        }
        for r in rows
    ]
    return {"ok": True, "query": query, "scope": used_scope, "count": len(results), "results": results}


def get_chunk(doc: str, chunk_id: int, context: int = 0) -> dict:
    ensure_index()
    con = _connect()
    try:
        lo = max(0, chunk_id - max(0, context))
        hi = chunk_id + max(0, context)
        rows = con.execute(
            "SELECT ord, heading, body FROM chunks "
            "WHERE doc = (SELECT content_key FROM docs_meta WHERE name=?) "
            "AND ord BETWEEN ? AND ? ORDER BY ord",
            (doc, lo, hi),
        ).fetchall()
    finally:
        con.close()

    if not rows:
        return {"ok": False, "error": f"No chunk {chunk_id} in doc {doc!r}."}
    body = "\n\n".join(r["body"] for r in rows)
    return {
        "ok": True, "doc": doc, "chunk_id": chunk_id,
        "range": [rows[0]["ord"], rows[-1]["ord"]],
        "heading": rows[0]["heading"], "text": body,
    }


def list_docs(product: str = "", category: str = "", query: str = "",
              limit: int = 50, offset: int = 0, summary_only: bool = False) -> dict:
    ensure_index()
    con = _connect()
    try:
        # If summary_only is requested and no specific filters are applied, return aggregated overview
        if summary_only and not product and not category and not query:
            total_docs = con.execute("SELECT COUNT(*) FROM docs_meta").fetchone()[0]
            total_chunks = con.execute("SELECT SUM(chunk_count) FROM docs_meta").fetchone()[0] or 0
            product_rows = con.execute(
                "SELECT product, COUNT(*) AS doc_count, SUM(chunk_count) AS chunk_count "
                "FROM docs_meta GROUP BY product ORDER BY doc_count DESC"
            ).fetchall()
            category_rows = con.execute(
                "SELECT category, COUNT(*) AS doc_count "
                "FROM docs_meta GROUP BY category ORDER BY doc_count DESC"
            ).fetchall()
            return {
                "ok": True,
                "summary_only": True,
                "total_docs": total_docs,
                "total_chunks": total_chunks,
                "product_summary": [dict(r) for r in product_rows],
                "category_summary": [dict(r) for r in category_rows],
                "hint": "Specify product, category, query, or pass summary_only=False to retrieve individual document items.",
            }

        clauses = []
        params = []
        if product:
            clauses.append("LOWER(product) = LOWER(?)")
            params.append(product)
        if category:
            clauses.append("LOWER(category) = LOWER(?)")
            params.append(category)
        if query:
            clauses.append("(LOWER(name) LIKE LOWER(?) OR LOWER(title) LIKE LOWER(?))")
            params.append(f"%{query}%")
            params.append(f"%{query}%")

        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        count_sql = f"SELECT COUNT(*) FROM docs_meta {where_clause}"
        total_matches = con.execute(count_sql, params).fetchone()[0]

        safe_limit = max(1, min(limit, 200))
        safe_offset = max(0, offset)

        data_sql = (
            f"SELECT name, title, category, product, release, source_path, content_hash, quality, "
            f"source_url, sdk_package, sdk_version, chunk_count AS chunks, chars "
            f"FROM docs_meta {where_clause} ORDER BY name LIMIT ? OFFSET ?"
        )
        data_params = list(params) + [safe_limit, safe_offset]
        rows = con.execute(data_sql, data_params).fetchall()
        docs = [dict(r) for r in rows]

        return {
            "ok": True,
            "summary_only": False,
            "total_matches": total_matches,
            "limit": safe_limit,
            "offset": safe_offset,
            "has_more": (safe_offset + len(docs)) < total_matches,
            "count": len(docs),
            "docs": docs,
        }
    finally:
        con.close()
