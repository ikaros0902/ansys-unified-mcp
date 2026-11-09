"""整理官方文件來源、下載核心文件並建立可攜式搜尋清冊。"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile

from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = REPO_ROOT / "docs" / "ANSYS_Document"
DEFAULT_SOURCES = REPO_ROOT / "src" / "ansys_unified_mcp" / "resources" / "manifests" / "document_sources.json"
PDF_PYTHON = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"
HEADERS = {"User-Agent": "ANSYS-document-library/1.0 (+local archival; no solver execution)"}
KNOWN_CATEGORIES = {"api_reference", "api_scripting", "guide", "tutorial", "manual"}


def safe_path(root: Path, relative: str) -> Path:
    """拒絕絕對路徑、Windows 磁碟路徑與連結越界。"""
    if not relative or Path(relative).is_absolute() or re.match(r"^[A-Za-z]:", relative):
        raise ValueError(f"不是相對路徑: {relative}")
    candidate = (root / relative).resolve()
    candidate.relative_to(root.resolve())
    if candidate == root.resolve():
        raise ValueError("目的檔不能是文件根目錄")
    return candidate


def digest_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else default


def normalize_url(value: str, base: str = "") -> str:
    """正規化 Markdown 尖括號目的地與空白，不把語法殘留送至 HTTP。"""
    value = value.strip()
    if value.startswith("<"):
        end = value.find(">")
        if end < 0:
            raise ValueError("Markdown URL 缺少結束尖括號")
        value = value[1:end].strip()
    else:
        value = re.split(r"\s+[\"']", value, maxsplit=1)[0].strip()
    if not value or any(character in value for character in "<>") or any(ord(character) < 32 for character in value):
        raise ValueError("URL 含無效語法或控制字元")
    parsed = urllib.parse.urlsplit(urllib.parse.urljoin(base, value))
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("URL 必須是完整 HTTPS 網址")
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc,
        urllib.parse.quote(parsed.path, safe="/%:@!$&'()*+,;=-._~"),
        urllib.parse.quote(parsed.query, safe="=&?/%:@!$'()*+,;~-._"), ""))


def markdown_links(text: str, base: str) -> list[str]:
    links = []
    for value in re.findall(r"\]\(([^)]+)\)", text):
        try:
            links.append(normalize_url(value, base))
        except ValueError:
            continue
    return links


def official_url(url: str) -> bool:
    parsed = urllib.parse.urlsplit(url)
    host = (parsed.hostname or "").lower()
    return parsed.scheme == "https" and (
        host == "docs.pyansys.com" or host.endswith(".docs.pyansys.com")
        or host in {"storage.ansys.com", "ansyshelp.ansys.com", "developer.ansys.com", "developer.synopsys.com"}
        or (host in {"github.com", "raw.githubusercontent.com"} and parsed.path.startswith("/ansys/"))
    )


def fetch(url: str, max_bytes: int = 250_000_000) -> tuple[bytes, str]:
    url = normalize_url(url)
    if not official_url(url):
        raise ValueError(f"非允許的官方來源: {url}")
    # 優先嘗試以 scrapling.fetchers.Fetcher 抓取
    try:
        from scrapling.fetchers import Fetcher
        _f = Fetcher()
        resp = _f.get(url, timeout=35)
        if resp and getattr(resp, "status", 200) == 200:
            final_url = getattr(resp, "url", url)
            if official_url(final_url):
                raw = resp.body if hasattr(resp, "body") else (resp.text.encode("utf-8") if hasattr(resp, "text") else b"")
                if raw and len(raw) <= max_bytes:
                    return raw, final_url
    except Exception:
        pass
    request = urllib.request.Request(url, headers=HEADERS)
    last_error = None
    for _ in range(2):
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                if not official_url(response.url):
                    raise ValueError("來源重新導向非允許的官方網域")
                size = int(response.headers.get("Content-Length", "0"))
                if size > max_bytes:
                    raise ValueError(f"下載超出單檔限制: {size}")
                raw = response.read(max_bytes + 1)
                if len(raw) > max_bytes:
                    raise ValueError("下載超出單檔限制")
                return raw, response.url
        except urllib.error.HTTPError as exc:
            if exc.code in {401, 403, 404}:
                raise
            last_error = exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
    raise last_error


def html_text(raw: bytes, url: str) -> tuple[str, str, list[str]]:
    soup = BeautifulSoup(raw, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    article = soup.select_one("article, main, [role=main]") or soup.body
    if article is None:
        raise ValueError("找不到正文；不將登入頁或入口導覽當作核心文件")
    for element in article.select("script, style, nav, .headerlink, .sidebar, footer"):
        element.decompose()
    links = [urllib.parse.urljoin(url, a["href"]).split("#")[0] for a in article.select("a[href]")]
    for anchor in article.select("a[href]"):
        label = anchor.get_text(" ", strip=True)
        anchor.replace_with(f"[{label}]({urllib.parse.urljoin(url, anchor['href'])})")
    for pre in article.select("pre"):
        pre.replace_with("\n```\n" + pre.get_text() + "\n```\n")
    for heading in article.select("h1, h2, h3, h4, h5, h6"):
        heading.replace_with("\n" + "#" * int(heading.name[1]) + " " + heading.get_text(" ", strip=True) + "\n")
    text = article.get_text("\n", strip=True)
    if len(text) < 100 or re.search(r"^(?:sign in|access denied|log in)\b", title, re.I):
        raise ValueError("正文不足或需登入")
    return title, f"---\nsource_url: {url}\n---\n\n{text}\n", links


def normalize_release(text: str) -> str:
    match = re.search(r"(?:^|[/\s_-])(v\d{3})(?=[/\s_.-]|$)", text, re.I)
    if match:
        return match[1].lower()
    match = re.search(r"20(\d{2})[\s_-]*r([12])\b", text, re.I)
    return f"v{match[1]}{match[2]}" if match else "unknown"


def source_header(text: str) -> str:
    match = re.search(r"(?:source_url|source|Source)\s*:\s*[`\"']?(https://[^\s`\"'<>]+)", text[:3000])
    return match[1] if match else ""


def quality(text: str) -> str:
    if not text.strip():
        return "empty"
    outside_code = re.sub(r"(?ms)^[ \t]{0,3}(`{3,}|~{3,})[^\n]*\n.*?^[ \t]{0,3}\1[ \t]*$", "", text)
    jinja_control = re.search(r"\{%[-+]?\s*(?:for|if|elif|else|set|block|macro|include|extends|endfor|endif|endblock|endmacro|endwith|endfilter|raw|endraw|filter|call|with|autoescape|endautoescape|trans|pluralize|import|from|do)\b", outside_code)
    if any(token in outside_code for token in (".. toctree::", ".. automodule::", ".. autoclass::")) or jinja_control:
        return "template"
    if len(text.strip()) < 100:
        return "stub"
    return "body_present"


def document_id(product: str, release: str, sdk: str, version: str, sha256: str) -> str:
    # 內容相同的搬移不改識別碼；正文修訂才建立新的 chunk 身分。
    key = "\0".join((product, release, sdk, version, sha256))
    return "ansys_" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]


def _safe_extract_tar(archive: Path, destination: Path) -> int:
    tar = shutil.which("tar")
    if not tar:
        raise ValueError("ZIP64 格式不相容且找不到 tar 解壓工具")
    names = subprocess.run([tar, "-tf", str(archive)], capture_output=True, check=True).stdout.decode("utf-8", "replace").splitlines()
    details = subprocess.run([tar, "-tvf", str(archive)], capture_output=True, check=True).stdout.decode("utf-8", "replace").splitlines()
    if len(names) != len(details):
        raise ValueError("tar 封存清單與詳細清單筆數不同")
    members = []
    total_size = 0
    for name, detail in zip(names, details):
        fields = detail.split()
        if not fields or fields[0][0] not in {"-", "d"}:
            raise ValueError("封存包含非一般檔案或目錄")
        relative = name.replace("\\", "/").rstrip("/")
        safe_path(destination, relative)
        size = int(fields[4])
        total_size += size
        if total_size > 2_000_000_000:
            raise ValueError("解壓後總大小超過 2GB")
        members.append((relative, fields[0][0], size))

    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ansys-zip-", dir=destination.parent) as temporary:
        staging = Path(temporary)
        subprocess.run([tar, "-xf", str(archive), "-C", str(staging)], capture_output=True, check=True)
        actual = list(staging.rglob("*"))
        if any(path.is_symlink() or not path.resolve().is_relative_to(staging.resolve()) for path in actual):
            raise ValueError("解壓內容包含連結或越界路徑")
        expected_files = {name for name, kind, _ in members if kind == "-"}
        staged_files = {path.relative_to(staging).as_posix() for path in actual if path.is_file()}
        if staged_files != expected_files:
            raise ValueError("tar 解壓出的檔案與預先檢查清單不同")
        for name, kind, _ in members:
            target = safe_path(destination, name)
            if kind == "d":
                if target.exists() and not target.is_dir():
                    raise FileExistsError(f"解壓目錄與既有檔案衝突: {target}")
            elif target.exists():
                source = safe_path(staging, name)
                if not target.is_file() or digest_file(target) != digest_file(source):
                    raise FileExistsError(f"不覆蓋不同內容: {target}")
        for name, kind, _ in members:
            target = safe_path(destination, name)
            if kind == "d":
                target.mkdir(parents=True, exist_ok=True)
            elif not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                os.rename(safe_path(staging, name), target)
    return len(members)


def safe_extract(archive: Path, destination: Path) -> int:
    """先驗整包路徑與大小，再解壓；從不執行範例。"""
    try:
        package = zipfile.ZipFile(archive)
    except zipfile.BadZipFile:
        return _safe_extract_tar(archive, destination)
    try:
        with package:
            members = package.infolist()
            if sum(member.file_size for member in members) > 2_000_000_000:
                raise ValueError("解壓後總大小超過 2GB")
            for member in members:
                safe_path(destination, member.filename.replace("\\", "/"))
                if (member.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("壓縮包含符號連結")
            for member in members:
                target = safe_path(destination, member.filename.replace("\\", "/"))
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    raw = package.read(member)
                    if target.exists() and target.read_bytes() != raw:
                        raise FileExistsError(f"不覆蓋不同內容: {target}")
                    target.write_bytes(raw)
        return len(members)
    except zipfile.BadZipFile:
        return _safe_extract_tar(archive, destination)


def save_file(root: Path, relative: str, raw: bytes) -> Path:
    path = safe_path(root, relative)
    if path.is_file():
        if path.read_bytes() == raw:
            return path
        # 來源內容改版保留舊檔，新檔以內容摘要區別。
        path = path.with_name(path.stem + "-" + hashlib.sha256(raw).hexdigest()[:10] + path.suffix)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_bytes(raw)
    os.replace(temporary, path)
    return path


def section_category(url: str) -> str | None:
    path = urllib.parse.urlsplit(url).path.lower()
    if "/examples/" in path:
        return "tutorial"
    if re.search(r"/(?:api|reference|api_reference)(?:/|\.)", path):
        return "api_reference"
    if re.search(r"/(?:user_guide|getting_started|users_guide|guide)(?:/|\.)", path):
        return "guide"
    return None


def sdk_metadata(soup: BeautifulSoup, url: str) -> tuple[str, str]:
    """以 Sphinx 發布的 VERSION 字串判定 SDK，不把 stable 當版本。"""
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    match = re.search(r"(?:documentation|release)\s+(\d+\.\d+[\w.+-]*)|(\d+\.\d+[\w.+-]*)\s+documentation", title, re.I)
    if match:
        return next(group for group in match.groups() if group), url
    for script in soup.select("script[src]"):
        if "documentation_options.js" not in script["src"]:
            continue
        options_url = urllib.parse.urljoin(url, script["src"])
        try:
            options, final_url = fetch(options_url, 1_000_000)
            match = re.search(r"\bVERSION\s*:\s*['\"]([^'\"]+)['\"]", options.decode("utf-8"))
            if match and match[1].strip():
                return match[1], final_url
        except (OSError, ValueError, http.client.InvalidURL, urllib.error.URLError):
            pass
    return "unknown", ""


def cached_sdk_page(product: dict, root: Path, url: str, old_records: dict) -> tuple[bytes, str]:
    """以清冊或下載時的 URL 摘要與 Markdown 來源頭恢復已完成頁面。"""
    previous = old_records.get(url)
    if previous:
        path = safe_path(root, previous["path"])
        if path.is_file() and digest_file(path) == previous.get("sha256"):
            return path.read_bytes(), url
    prefix = hashlib.sha256(url.encode()).hexdigest()[:12] + "-"
    base = root / product["folder"] / "sdk" / product["sdk_package"]
    for path in base.glob(f"*/*/{prefix}*.html"):
        text_path = path.with_suffix(".md")
        if text_path.is_file() and source_header(text_path.read_text(encoding="utf-8", errors="replace")) == url:
            return path.read_bytes(), url
    return fetch(url, 15_000_000)


def synchronize_sdk(product: dict, root: Path, old_records: dict, max_pages: int, max_examples: int = 15) -> list[dict]:
    base_url = product["sdk_url"]
    records = []
    queue = deque([(base_url, "guide", False)])
    seen = set()
    sdk_version = "unknown"
    version_source = ""
    example_count = 0
    category_count = Counter()
    while queue and len(seen) < max_pages:
        url, category, is_core = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        if is_core and category_count[category] >= max(3, max_pages // 3):
            continue
        row = None
        try:
            raw, final_url = cached_sdk_page(product, root, url, old_records)
            title, text, links = html_text(raw, final_url)
            if len(seen) == 1:
                soup = BeautifulSoup(raw, "html.parser")
                links += [urllib.parse.urljoin(final_url, a["href"]).split("#")[0] for a in soup.select("a[href]")]
                sdk_version, version_source = sdk_metadata(soup, final_url)
            if category == "tutorial" and not url.rstrip("/").endswith(("index.html", "examples")):
                example_count += 1
                if example_count > max_examples:
                    continue
            slug = hashlib.sha256(url.encode()).hexdigest()[:12] + "-" + (Path(urllib.parse.urlsplit(url).path).stem or "index")
            directory = f"{product['folder']}/sdk/{product['sdk_package']}/{sdk_version}/{category}"
            path = save_file(root, f"{directory}/{slug}.html", raw)
            text_path = save_file(root, f"{directory}/{slug}.md", text.encode("utf-8"))
            row = {"source_url": url, "path": path.relative_to(root).as_posix(), "text_path": text_path.relative_to(root).as_posix(), "product": product["product"], "release": "unknown", "sdk_package": product["sdk_package"], "sdk_version": sdk_version, "category": category, "title": title, "sha256": digest_file(path), "status": "downloaded", "is_core": is_core, "sdk_version_source": version_source, "input_status": "not_applicable"}
            if category == "tutorial" and is_core:
                if not url.rstrip("/").endswith(("index.html", "examples")):
                    row["input_status"] = "input_pending" if re.search(r"download_file|download_example|examples\.download", text) else "ready"
                row["input_files"] = []
            records.append(row)
            category_count[category] += 1
            if not is_core:
                seeds = []
                for wanted in ("guide", "api_reference", "tutorial"):
                    candidates = sorted({link for link in links if section_category(link) == wanted}, key=lambda value: (len(urllib.parse.urlsplit(value).path), value))
                    seeds.extend(candidates[:1])
                links = seeds
            for link in links:
                if not official_url(link) or urllib.parse.urlsplit(link).netloc != urllib.parse.urlsplit(base_url).netloc:
                    continue
                linked_category = section_category(link)
                if linked_category and link.endswith((".html", "/")) and link not in seen:
                    if linked_category != "tutorial" or example_count < max_examples:
                        queue.append((link, linked_category, True))
                if category == "tutorial" and is_core and "/_downloads/" in link and link.lower().endswith((".py", ".ipynb", ".csv", ".json", ".dat", ".txt", ".pmdb", ".cas.h5", ".dat.h5", ".msh", ".msh.h5", ".stp", ".step", ".scdoc", ".agdb", ".wbpz", ".rst", ".bdf", ".cdb", ".k")):
                    attached, _ = fetch(link, 25_000_000)
                    attachment = save_file(root, f"{directory}/inputs/{Path(urllib.parse.urlsplit(link).path).name}", attached)
                    row["input_files"].append({"source_url": link, "path": attachment.relative_to(root).as_posix(), "sha256": digest_file(attachment)})
        except (OSError, ValueError, http.client.InvalidURL, urllib.error.URLError) as exc:
            if row and row.get("input_status") == "ready":
                row["input_status"] = "input_pending"
            records.append({"source_url": url, "product": product["product"], "status": "blocked" if isinstance(exc, urllib.error.HTTPError) and exc.code in {401, 403} else "failed", "error": str(exc), "category": category})
    if queue:
        records.append({"product": product["product"], "status": "partial", "reason": "核心頁面下載預算已用盡；並非全站鏡像", "remaining_discovered_urls": len(queue)})
    return records


def synchronize_portal(product: dict, root: Path, max_pages: int) -> list[dict]:
    """只追官方產品入口明列的版本連結，並保存佇列以便分批續抓。"""
    url = product.get("overview_url", "")
    if not url:
        return []
    state_path = root / "_catalog" / f"portal_crawl_{product['product']}.json"
    state = load_json(state_path, {})
    if state.get("start_url") == url:
        queue = deque(state.get("queue", []))
        seen = set(state.get("seen", []))
    else:
        queue = deque([url])
        seen = set()
    records = []
    processed = 0
    while queue and processed < max_pages:
        current = queue.popleft()
        if current in seen:
            continue
        seen.add(current)
        processed += 1
        try:
            raw, final_url = fetch(current, 15_000_000)
            if raw.lstrip().startswith((b"<", b"<!")):
                title, text, links = html_text(raw, final_url)
            else:
                text = raw.decode("utf-8")
                title = next((line.lstrip("# ") for line in text.splitlines() if line.startswith("#")), product["product"])
                links = markdown_links(text, final_url)
            release = normalize_release(final_url)
            if release == "unknown" and current != url and not current.rstrip("/").endswith("previous"):
                continue
            category = "api_reference" if re.search(r"api|reference|scripting", final_url, re.I) else "guide"
            slug = hashlib.sha256(final_url.encode()).hexdigest()[:12] + "-" + (Path(urllib.parse.urlsplit(final_url).path).stem or "index")
            directory = f"{product['folder']}/{release}/{category}"
            path = save_file(root, f"{directory}/{slug}.md", text.encode("utf-8"))
            records.append({"source_url": final_url, "path": path.relative_to(root).as_posix(), "product": product["product"], "release": release, "sdk_package": "", "sdk_version": "unknown", "category": category, "title": title, "sha256": digest_file(path), "status": "downloaded", "is_core": release != "unknown"})
            for link in links:
                if not official_url(link) or urllib.parse.urlsplit(link).hostname != "developer.synopsys.com":
                    continue
                linked_release = normalize_release(link)
                if link.rstrip("/").endswith("previous") or (linked_release != "unknown" and int(linked_release[1:]) >= 251):
                    if link not in seen:
                        queue.append(link)
        except (OSError, ValueError, http.client.InvalidURL, urllib.error.URLError) as exc:
            records.append({"source_url": current, "product": product["product"], "status": "blocked" if isinstance(exc, urllib.error.HTTPError) and exc.code in {401, 403} else "failed", "error": str(exc)})
    atomic_json(state_path, {"start_url": url, "seen": sorted(seen), "queue": list(dict.fromkeys(queue))})
    if queue:
        records.append({"product": product["product"], "status": "partial", "reason": "官方版本連結佇列已保存，後續可續抓", "remaining_discovered_urls": len(queue), "phase": "portal"})
    return records


def extract_pdf_text(root: Path, limit: int = 0, python: Path = PDF_PYTHON,
                     selected_paths: list[str] | None = None) -> dict:
    """使用既有 PDF runtime 擷取並保留頁碼；PDFium 不跨執行緒共用。"""
    if not python.is_file():
        raise FileNotFoundError("PDF runtime 不存在；請以 --pdf-python 指向既有 PDF runtime")
    paths = sorted(root.rglob("*.pdf")) if selected_paths is None else sorted({
        safe_path(root, relative) for relative in selected_paths
    })
    if any(path.suffix.lower() != ".pdf" or not path.is_file() for path in paths):
        raise ValueError("指定的 PDF 路徑不存在或不是 PDF")
    if limit:
        paths = paths[:limit]
    report_path = root / "_catalog" / ".pdf-extraction-result.json"
    payload = {"root": str(root), "paths": [str(path) for path in paths], "report_path": str(report_path)}
    program = r'''
from pathlib import Path
import json,sys,hashlib,os,re
try:
 import pypdfium2 as pdfium
except ImportError:
 pdfium=None
 from pypdf import PdfReader
data=json.load(sys.stdin);root=Path(data["root"]);out=root/"_catalog"/"pdf_text_v2";out.mkdir(parents=True,exist_ok=True)
rows=[]
for value in data["paths"]:
 p=Path(value)
 try:
  with p.open("rb") as stream: digest=hashlib.file_digest(stream,"sha256").hexdigest()
  dst=out/(digest+".md")
  if not dst.is_file():
   parts=[]
   if pdfium:
    with pdfium.PdfDocument(str(p)) as pdf:
     for i in range(len(pdf)):
      page=pdf[i]
      try:
       textpage=page.get_textpage()
       try: text=textpage.get_text_bounded().replace("\r\n","\n")
       finally: textpage.close()
      finally: page.close()
      parts.append("<!-- page %d -->\n%s" % (i+1,text))
   else:
    reader=PdfReader(str(p))
    parts=["<!-- page %d -->\n%s" % (i+1,page.extract_text() or "") for i,page in enumerate(reader.pages)]
   text="\n\n".join(parts)
   if len(re.sub(r"<!-- page \d+ -->", "", text).strip())<100: raise ValueError("PDF沒有可擷取正文，未執行OCR")
   temporary=dst.with_suffix(".part");temporary.write_text(text,encoding="utf-8");os.replace(temporary,dst)
  cached=dst.read_text(encoding="utf-8")
  if len(re.sub(r"<!-- page \d+ -->", "", cached).strip())<100: raise ValueError("PDF沒有可擷取正文，未執行OCR")
  rows.append({"path":p.relative_to(root).as_posix(),"sha256":digest,"text_path":dst.relative_to(root).as_posix(),"status":"extracted"})
 except Exception as exc: rows.append({"path":p.relative_to(root).as_posix(),"status":"failed","error":str(exc)})
Path(data["report_path"]).write_text(json.dumps({"records":rows},ensure_ascii=False),encoding="utf-8")
'''
    subprocess.run([str(python), "-c", program], input=json.dumps(payload), text=True, encoding="utf-8", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    if not report_path.is_file():
        raise RuntimeError("PDF runtime 未回傳擷取結果清冊")
    report = load_json(report_path, {"records": []})
    report_path.unlink(missing_ok=True)
    for row in report["records"]:
        if row.get("status") != "extracted":
            continue
        pdf = safe_path(root, row["path"])
        cached = safe_path(root, row["text_path"])
        markdown = safe_path(root, Path(row["path"]).with_suffix(".md").as_posix())
        cached_hash = digest_file(cached)
        if not markdown.exists():
            fd, temporary_name = tempfile.mkstemp(prefix=f".{markdown.name}.", suffix=".tmp", dir=markdown.parent)
            os.close(fd)
            temporary = Path(temporary_name)
            try:
                shutil.copyfile(cached, temporary)
                os.replace(temporary, markdown)
            except Exception:
                temporary.unlink(missing_ok=True)
                raise
            markdown_status = "created_from_cache"
        elif markdown.is_file() and digest_file(markdown) == cached_hash:
            markdown_status = "existing_matches_cache"
        else:
            markdown_status = "existing_different_preserved"
        markdown_relative = markdown.relative_to(root.resolve()).as_posix()
        row["markdown_path"] = markdown_relative
        row["markdown_status"] = markdown_status
        if markdown_status != "existing_different_preserved":
            row["text_path"] = markdown_relative
    previous = load_json(root / "_catalog/pdf_extraction.json", {"records": []})
    changed = {row["path"] for row in report["records"]}
    report["records"] = [row for row in previous["records"] if row["path"] not in changed] + report["records"]
    atomic_json(root / "_catalog/pdf_extraction.json", report)
    return report


def synchronize(root: Path, sources: dict, products: set[str], max_pages: int, workers: int, max_examples: int = 15) -> dict:
    state_path = root / "_catalog/downloads.json"
    result = load_json(state_path, {"schema_version": 1, "records": []})
    old_records = {row["source_url"]: row for row in result["records"] if row.get("path")}

    def persist(rows: list[dict], phase: str, product_name: str | None = None) -> None:
        # 每個產品完成即存檔，後續來源失敗不能抹去已下載證據。
        for row in rows:
            row["phase"] = phase
        replaced = {row["source_url"] for row in rows if row.get("source_url")}
        downloaded_urls = {row["source_url"] for row in rows if row.get("source_url") and row["status"] == "downloaded"}
        progress = {(row.get("product"), phase) for row in rows if not row.get("source_url")}
        if product_name:
            progress.add((product_name, phase))
            if phase == "portal":
                progress.add((product_name, None))
        kept = [row for row in result["records"] if (row.get("source_url") not in replaced or (row["status"] == "downloaded" and row.get("source_url") not in downloaded_urls)) and (row.get("source_url") or (row.get("product"), row.get("phase")) not in progress)]
        result.update(schema_version=1, updated_at=datetime.now(timezone.utc).isoformat(), records=kept + rows)
        atomic_json(state_path, result)
        old_records.update({row["source_url"]: row for row in rows if row.get("path") and row["status"] == "downloaded"})

    for phase, field in (("sdk", "sdk_url"), ("portal", "overview_url")):
        selected = [p for p in sources["products"] if p.get(field) and (not products or p["product"] in products)]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            pending = {pool.submit(synchronize_sdk, product, root, old_records.copy(), max_pages, max_examples) if phase == "sdk" else pool.submit(synchronize_portal, product, root, max_pages): product for product in selected}
            for future in as_completed(pending):
                product = pending[future]
                try:
                    rows = future.result()
                except Exception as exc:
                    rows = [{"product": product["product"], "source_url": product[field], "status": "failed", "error": f"{type(exc).__name__}: {exc}"}]
                persist(rows, phase, product["product"])
                print(f"{phase.upper()} {product['product']}: {dict(Counter(row['status'] for row in rows))}", flush=True)
    for source in sources.get("downloads", []):
        if products and source["product"] not in products:
            continue
        try:
            previous = old_records.get(source["url"])
            if previous and safe_path(root, previous["path"]).is_file() and digest_file(safe_path(root, previous["path"])) == previous.get("sha256"):
                path = safe_path(root, previous["path"])
            else:
                raw, _ = fetch(source["url"])
                if source["path"].endswith(".pdf") and not raw.startswith(b"%PDF-"):
                    raise ValueError("PDF 下載回應不是 PDF")
                if source["path"].endswith(".zip") and not raw.startswith(b"PK"):
                    raise ValueError("ZIP 下載回應不是 ZIP")
                path = save_file(root, source["path"], raw)
            row = {**source, "source_url": source["url"], "path": path.relative_to(root).as_posix(), "sha256": digest_file(path), "status": "downloaded"}
            if path.suffix.lower() in {".html", ".htm", ".xhtml"}:
                markdown = path.with_suffix(".md")
                if markdown.is_file() and markdown.stat().st_size:
                    row["text_path"] = markdown.relative_to(root).as_posix()
            if path.suffix.lower() == ".zip":
                row["extracted_root"] = (path.parent / path.stem).relative_to(root).as_posix()
                row["extracted_files"] = safe_extract(path, path.parent / path.stem)
            rows = [row]
        except (OSError, ValueError, http.client.InvalidURL, zipfile.BadZipFile, urllib.error.URLError, subprocess.SubprocessError) as exc:
            rows = [{**source, "source_url": source["url"], "status": "blocked" if isinstance(exc, urllib.error.HTTPError) and exc.code in {401, 403} else "failed", "error": str(exc)}]
        persist(rows, "bundle")
        print(f"BUNDLE {source['product']} {source.get('release', 'unknown')}: {rows[0]['status']}", flush=True)
    return result


def make_catalog(root: Path, sources: dict, selected_products: set[str] | None = None) -> dict:
    downloads = load_json(root / "_catalog/downloads.json", {"records": []})
    downloaded = {row["path"]: row for row in downloads["records"] if row.get("path") and row.get("status") == "downloaded"}
    rendered_paths = {row["text_path"] for row in downloaded.values() if row.get("text_path")}
    archive_records = [(row.get("extracted_root", Path(row["path"]).with_suffix("").as_posix()).rstrip("/") + "/", row) for row in downloaded.values() if row["path"].endswith(".zip") and safe_path(root, row["path"]).is_file() and digest_file(safe_path(root, row["path"])) == row.get("sha256")]
    folders = {p["folder"].lower(): p["product"] for p in sources["products"]}
    extracted = {row["path"]: row for row in load_json(root / "_catalog/pdf_extraction.json", {"records": []})["records"] if row["status"] == "extracted"}
    relocations = load_json(root / "_catalog/relocations.json", {})
    moves = relocations if isinstance(relocations, list) else relocations.get("moves", [])
    relocated = {row["new_path"]: row for row in moves}
    records = []
    if selected_products is not None:
        previous = load_json(root / "_catalog/documents.json", {"documents": []})
        records = [row for row in previous.get("documents", []) if row.get("product") not in selected_products]
    seen_ids = {row["id"] for row in records if row.get("id")}
    selected_folders = {folder for folder, product in folders.items() if selected_products and product in selected_products}
    source_paths = []
    for current, directories, filenames in os.walk(root):
        directories[:] = [name for name in directories if name != "_catalog" and (selected_products is None or Path(current) != root or name.lower() in selected_folders)]
        source_paths.extend(Path(current) / name for name in filenames)
    for index, path in enumerate(sorted(source_paths), 1):
        if index % 10_000 == 0:
            print(f"CATALOG scanned {index} filesystem entries; documents={len(records)}", flush=True)
        if not path.is_file() or path.name in {".crawl_manifest.json", "README.md", "INDEX.md"}:
            continue
        relative = path.relative_to(root).as_posix()
        if relative in rendered_paths:
            continue
        suffix = path.suffix.lower()
        if suffix not in {".md", ".markdown", ".pdf", ".html", ".htm", ".zip", ".py", ".ipynb", ".chm"}:
            continue
        bundle_prefix, bundle = next(((prefix, row) for prefix, row in archive_records if relative.startswith(prefix)), ("", {}))
        original = {**bundle, **relocated.get(relative, {}), **downloaded.get(relative, {})}
        if bundle and relative not in downloaded:
            original["source_url"] = bundle["source_url"] + "#" + urllib.parse.quote(relative[len(bundle_prefix):], safe="/")
            original.pop("text_path", None)
        text = path.read_text(encoding="utf-8", errors="replace") if suffix in {".md", ".markdown"} else ""
        source = original.get("source_url") or source_header(text)
        product = original.get("product") or folders.get(path.relative_to(root).parts[0].lower(), "general")
        if path.relative_to(root).parts[0].lower() == "optislang" and path.stem.lower().startswith("lsopt_"):
            product = "general"  # LS-OPT 手冊不是 optiSLang 文件，避免產品篩選混入錯誤語料。
        release = original.get("release") or normalize_release(source) or "unknown"
        if release == "unknown":
            release = next((value for part in path.relative_to(root).parts[:-1]
                            if (value := normalize_release(part)) != "unknown"), "unknown")
        sdk = original.get("sdk_package", "")
        sdk_version = original.get("sdk_version", "unknown")
        category = original.get("category") or ("tutorial" if any(s in relative.lower() for s in ("tutorial", "example")) else "api_reference" if "api_reference" in relative.lower() or "api-reference" in relative.lower() else "manual" if suffix == ".pdf" else "guide")
        sha = digest_file(path)
        identifier = document_id(product, release, sdk, sdk_version, sha)
        if identifier in seen_ids:
            continue
        seen_ids.add(identifier)
        text_path = original.get("text_path") or (extracted.get(relative, {}).get("text_path") if extracted.get(relative, {}).get("sha256") == sha else None)
        if suffix in {".html", ".htm"} and not text_path:
            view = root / "_catalog/html_text" / f"{sha}.md"
            try:
                if not view.is_file():
                    # shortcut: ACT 巨型目錄只保留原檔，若其內容無分頁替代再改用串流擷取。
                    if path.name.lower() == "index.html" and path.stat().st_size > 10_000_000:
                        raise ValueError("ACT 巨型目錄頁超過 10 MB，保留原檔供人工查閱")
                    raw = path.read_bytes()
                    _, rendered, _ = html_text(raw, source)
                    view.parent.mkdir(parents=True, exist_ok=True)
                    view.write_text(rendered, encoding="utf-8")
                text_path = view.relative_to(root).as_posix()
            except ValueError:
                pass
        if text_path:
            text = safe_path(root, text_path).read_text(encoding="utf-8", errors="replace")
        status = quality(text) if text else "pdf_pending_extraction" if suffix == ".pdf" else "attachment"
        input_status = original.get("input_status", "unknown")
        if category == "tutorial" and original.get("is_core", True):
            page_path = urllib.parse.urlsplit(source).path if source else relative
            is_index = page_path.rstrip("/").endswith(("index.html", "examples"))
            input_status = "not_applicable" if is_index else "input_pending" if re.search(r"download_file|download_example|examples\.download", text) else input_status
        records.append({"id": identifier, "title": original.get("title") or path.stem, "product": product, "release": release, "sdk_package": sdk, "sdk_version": sdk_version, "category": category, "source_url": source, "path": relative, "sha256": sha, "quality": status, "input_status": input_status, "is_core": original.get("is_core", True), **({"text_path": text_path} if text_path else {})})
    result = {"schema_version": 1, "updated_at": datetime.now(timezone.utc).isoformat(), "documents": records}
    atomic_json(root / "_catalog/documents.json", result)
    return result


def write_coverage(root: Path, sources: dict, catalog: dict) -> dict:
    rows = []
    downloads = load_json(root / "_catalog/downloads.json", {"records": []})["records"]
    for product in sources["products"]:
        documents = [d for d in catalog["documents"] if d["product"] == product["product"]]
        releases = {d["release"] for d in documents}
        releases.update(source["release"] for source in sources.get("downloads", []) if source["product"] == product["product"] and source.get("release"))
        for release in sorted(releases or {"unknown"}):
            subset = [d for d in documents if d["release"] == release]
            body = [d for d in subset if d["quality"] == "body_present" and d.get("is_core", True)]
            categories = Counter(d["category"] for d in body)
            guide_count = categories["guide"] + categories["manual"] + categories["api_scripting"]
            api_count = categories["api_reference"] + categories["api_scripting"]
            examples = [d for d in body if d["category"] == "tutorial" and d.get("input_status") in {"ready", "input_pending"}]
            ready_examples = sum(d.get("input_status") == "ready" for d in examples)
            missing = []
            if not guide_count:
                missing.append("guide")
            if not api_count:
                missing.append("api_reference")
            if ready_examples < 3:
                missing.append("tutorial_inputs")
            verified = release != "unknown" and any(d.get("source_url") for d in subset)
            official_release = any(s["product"] == product["product"] and s.get("release") == release for s in sources.get("downloads", []))
            availability = "observed" if verified else "publisher_linked" if official_release else "not_verified"
            status = "core_present" if not missing and availability != "not_verified" else "partial" if body else "not_acquired" if availability == "publisher_linked" else "not_verified"
            rows.append({"product": product["product"], "release": release, "files": len(subset), "indexed_candidates": len(body), "categories": dict(categories), "guide_count": guide_count, "api_count": api_count, "ready_examples": ready_examples, "required_examples": 3, "status": status, "release_availability": availability, "input_pending": len(examples) - ready_examples, "missing": missing, "failed_sources": [r.get("source_url", "") for r in downloads if r.get("product") == product["product"] and r["status"] in {"blocked", "failed"}]})
    result = {"schema_version": 1, "note": "僅列已觀察或官方明列的產品版本；unknown/SDK版本不推定產品release；範例輸入未確認不算離線完整。", "rows": rows}
    atomic_json(root / "_catalog/coverage.json", result)
    return result


def write_indexes(root: Path, sources: dict, coverage: dict) -> None:
    """重建產品導覽；原 README 先保存內容摘要備份。"""
    lines = ["# ANSYS 官方文件庫", "", "文件依產品與版本歸檔；SDK 版本獨立記錄。檔案數不代表完整覆蓋。", "", "| 產品 | 已收錄正文 | 已觀察版本 | 缺口 |", "| --- | ---: | --- | --- |"]
    for product in sources["products"]:
        rows = [r for r in coverage["rows"] if r["product"] == product["product"]]
        count = sum(r["indexed_candidates"] for r in rows)
        observed = ", ".join(r["release"] for r in rows if r["files"]) or "尚未取得"
        lines.append(f"| [{product['folder']}]({product['folder']}/README.md) | {count} | {observed} | 見產品清單 |")
        product_lines = [f"# {product['folder']} 文件", "", "本頁由官方來源清冊產生；下載範例未執行。", "", "| 版本 | 檔案 | 正文 | 待補類別 | 狀態 |", "| --- | ---: | ---: | --- | --- |"]
        for row in rows:
            product_lines.append(f"| {row['release']} | {row['files']} | {row['indexed_candidates']} | {', '.join(row['missing']) or '需檢查完整性'} | {row['status']} |")
        if product.get("overview_url"):
            product_lines.extend(["", f"官方產品入口：[{product['overview_url']}]({product['overview_url']})"])
        if product.get("sdk_url"):
            product_lines.extend(["", f"官方 SDK：[{product['sdk_url']}]({product['sdk_url']})"])
        if product.get("compatibility_note"):
            product_lines.extend(["", product["compatibility_note"]])
        path = safe_path(root, product["folder"] + "/README.md")
        if path.is_file():
            backup = root / "_catalog/readme_backups" / (digest_file(path) + ".md")
            if not backup.is_file():
                backup.parent.mkdir(parents=True, exist_ok=True)
                backup.write_bytes(path.read_bytes())
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(product_lines) + "\n", encoding="utf-8")
    lines.extend(["", "完整來源、雜湊及版本證據：[documents.json](_catalog/documents.json)。", "覆蓋與失敗項：[coverage.json](_catalog/coverage.json)。", "版本可用性為 not_verified 時，不表示官方發布過該版本。"])
    previous = root / "INDEX.md"
    if previous.is_file():
        backup = root / "_catalog/readme_backups" / (digest_file(previous) + ".md")
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.is_file():
            backup.write_bytes(previous.read_bytes())
    previous.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["sync", "catalog", "coverage"])
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--apply", action="store_true", help="明確執行；預設只顯示計畫")
    parser.add_argument("--product", action="append", default=[])
    parser.add_argument("--max-pages", type=int, default=30, help="每 SDK 本輪最多核心頁數，超額列 partial")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--max-examples", type=int, default=15, help="每項產品最多下載範例數 (預設: 15)")
    parser.add_argument("--extract-pdf", action="store_true", help="catalog 前擷取 PDF，使用既有 PDF runtime")
    parser.add_argument("--pdf-limit", type=int, default=0, help="本輪 PDF 擷取上限；0 為全部")
    parser.add_argument("--pdf-path", action="append", default=[], help="指定相對於文件根目錄的 PDF；可重複指定")
    parser.add_argument("--pdf-python", type=Path, default=PDF_PYTHON)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    sources = load_json(args.sources, {})
    if not sources.get("products") or args.max_pages < 1 or not 1 <= args.workers <= 8:
        parser.error("來源清單、max-pages 或 workers 無效")
    known_products = {p["product"] for p in sources["products"]}
    if set(args.product) - known_products:
        parser.error("--product 必須使用來源清單中的產品名稱")
    if args.pdf_path and not args.extract_pdf:
        parser.error("--pdf-path 須搭配 --extract-pdf")
    if args.pdf_path and args.pdf_limit:
        parser.error("--pdf-path 與 --pdf-limit 不可同時使用")
    if not args.apply:
        print(json.dumps({"dry_run": True, "command": args.command, "root": str(root), "products": args.product or [p["product"] for p in sources["products"]]}, ensure_ascii=False))
        return 0
    root.mkdir(parents=True, exist_ok=True)
    if args.command == "sync":
        result = synchronize(root, sources, set(args.product), args.max_pages, args.workers, args.max_examples)
        print(json.dumps(dict(Counter(r["status"] for r in result["records"])), ensure_ascii=False))
        return 1 if any(r["status"] in {"failed", "blocked"} for r in result["records"]) else 0
    if args.extract_pdf:
        extract_pdf_text(root, args.pdf_limit, args.pdf_python, args.pdf_path or None)
    catalog = make_catalog(root, sources, set(args.product) or None) if args.command == "catalog" else load_json(root / "_catalog/documents.json", {})
    if not catalog.get("documents"):
        raise ValueError("沒有有效清冊；拒絕生成空覆蓋表")
    result = write_coverage(root, sources, catalog)
    write_indexes(root, sources, result)
    print(json.dumps({"documents": len(catalog["documents"]), "quality": dict(Counter(d["quality"] for d in catalog["documents"])), "coverage_rows": len(result["rows"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
