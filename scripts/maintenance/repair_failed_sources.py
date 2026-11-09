"""修復與補抓 ANSYS 官方文件爬蟲失敗記錄 (基於 Scrapling 引擎)。

功能：
1. 讀取 docs/ANSYS_Document/_catalog/downloads.json 中所有 status == 'failed' 的記錄 (共 178 筆)。
2. 清理 URL 異常字符（如結尾引號、重複路徑）。
3. 使用 Scrapling Fetcher (HTTP/2 + TLS 偽裝) 自動重新抓取。
4. 將成功抓取的技術文檔與範例以 Markdownify 精煉正文儲存至對應產品目錄。
5. 更新 downloads.json 狀態與 SHA256。
6. 支援 --dry-run 與 --apply。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
from pathlib import Path
import re
import sys
import time
import urllib.parse
from bs4 import BeautifulSoup
import markdownify
from scrapling import Fetcher

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "docs"
AD_DIR = DOCS_DIR / "ANSYS_Document"
CATALOG_DIR = AD_DIR / "_catalog"
DOWNLOADS_FILE = CATALOG_DIR / "downloads.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("repair_failed_sources")


def clean_url_str(url: str) -> str:
    url = url.strip().strip('"').strip("'").strip()
    # 修復重複 user-guide
    url = url.replace("/user-guide/user-guide/", "/user-guide/")
    # 修復 Granta MI 網域變更
    if "grantami-system.docs.pyansys.com" in url:
        url = url.replace("grantami-system.docs.pyansys.com", "bomanalytics.grantami.docs.pyansys.com")
    return url


def digest_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def compute_rel_path(product: str, url: str, is_html: bool = True) -> tuple[str, str]:
    parsed = urllib.parse.urlsplit(url)
    slug = hashlib.sha256(url.encode()).hexdigest()[:12] + "-" + (Path(parsed.path).stem or "index")
    norm_prod = product.upper() if product in {"act", "cfx", "dpf", "mapdl", "q3d", "aedt"} else product.capitalize()
    dir_path = f"{norm_prod}/supplemental/crawled"
    html_rel = f"{dir_path}/{slug}.html"
    md_rel = f"{dir_path}/{slug}.md"
    return html_rel, md_rel


def fetch_and_convert(fetcher: Fetcher, url: str, max_retries: int = 3) -> tuple[int, bytes, str, str]:
    """抓取 URL 並轉為 markdown，回傳 (status_code, raw_bytes, title, markdown_text)"""
    last_err = None
    for attempt in range(max_retries):
        try:
            resp = fetcher.get(url, timeout=20)
            status = resp.status if hasattr(resp, "status") else 200
            if status != 200:
                return status, b"", "", ""

            raw_bytes = resp.body if hasattr(resp, "body") else resp.html_content.encode("utf-8")
            html_text = resp.html_content if hasattr(resp, "html_content") else raw_bytes.decode("utf-8", errors="replace")

            soup = BeautifulSoup(html_text, "html.parser")
            title = soup.title.get_text(" ", strip=True) if soup.title else Path(url).stem

            # 抓取正文區域
            article = soup.select_one("article, main, [role=main], .document, .content, #main-content")
            if article:
                md_body = markdownify.markdownify(str(article), heading_style="ATX")
            elif hasattr(resp, "markdown"):
                md_body = resp.markdown()
            else:
                md_body = soup.get_text("\n", strip=True)

            md_content = f"---\nsource_url: {url}\ntitle: {title}\n---\n\n{md_body}\n"
            return 200, raw_bytes, title, md_content
        except Exception as e:
            last_err = e
            time.sleep(1.0 * (attempt + 1))

    logger.warning(f"Fetch failed for {url}: {last_err}")
    return 0, b"", "", str(last_err)


def main():
    parser = argparse.ArgumentParser(description="修復與補抓 ANSYS 官方文件爬蟲失敗記錄")
    parser.add_argument("--apply", action="store_true", help="確認執行實體抓取與寫入")
    parser.add_argument("--limit", type=int, default=0, help="限制處理筆數 (0 為無限制)")
    args = parser.parse_args()

    mode = "正式執行 (--apply)" if args.apply else "預覽模式 (--dry-run)"
    print(f"=== 開始執行爬蟲失敗記錄補抓作業: {mode} ===", flush=True)

    if not DOWNLOADS_FILE.is_file():
        print(f"[ERROR] 找不到 downloads.json: {DOWNLOADS_FILE}", flush=True)
        sys.exit(1)

    with open(DOWNLOADS_FILE, "r", encoding="utf-8") as f:
        catalog_data = json.load(f)

    records = catalog_data.get("records", [])
    is_dict = isinstance(records, dict)
    record_list = list(records.values()) if is_dict else records

    failed_records = [r for r in record_list if r.get("status") == "failed"]
    print(f"共發現 {len(failed_records)} 筆失敗記錄。", flush=True)

    if args.limit > 0:
        failed_records = failed_records[:args.limit]
        print(f"依參數限制處理前 {args.limit} 筆。", flush=True)

    fetcher = Fetcher()
    success_count = 0
    resolved_existing = 0
    not_found_count = 0
    error_count = 0

    for i, record in enumerate(failed_records, start=1):
        raw_url = record.get("source_url") or record.get("url", "")
        url = clean_url_str(raw_url)
        product = record.get("product", "general")

        # 1. 檢查是否為已存在檔案 (如 ACTExtensionExamples.zip)
        existing_path_str = record.get("path")
        if existing_path_str:
            candidate = AD_DIR / existing_path_str
            if candidate.is_file():
                resolved_existing += 1
                print(f"[{i}/{len(failed_records)}] [EXISTS] 實體原件已存在: {existing_path_str}", flush=True)
                if args.apply:
                    record["status"] = "downloaded"
                    record["sha256"] = digest_bytes(candidate.read_bytes())
                continue

        # 2. 若為跳過/未提供 URL 則略過
        if not url or not url.startswith("http"):
            continue

        print(f"[{i}/{len(failed_records)}] 正在抓取: {url[:70]} ...", end=" ", flush=True)
        if not args.apply:
            print("[DRY-RUN]")
            continue

        status, raw_bytes, title, md_content = fetch_and_convert(fetcher, url)
        if status == 200:
            html_rel, md_rel = compute_rel_path(product, url)
            html_path = AD_DIR / html_rel
            md_path = AD_DIR / md_rel

            html_path.parent.mkdir(parents=True, exist_ok=True)
            html_path.write_bytes(raw_bytes)
            md_path.write_text(md_content, encoding="utf-8")

            record["status"] = "downloaded"
            record["source_url"] = url
            record["path"] = html_rel
            record["text_path"] = md_rel
            record["title"] = title
            record["sha256"] = digest_bytes(raw_bytes)
            record["phase"] = record.get("phase", "repaired_scrapling")
            if "error" in record:
                del record["error"]

            success_count += 1
            print(f"[OK 200] -> {md_rel}", flush=True)
        elif status == 404:
            not_found_count += 1
            record["status"] = "not_found"
            record["error"] = "HTTP 404: Not Found on upstream server"
            print("[404 Not Found]", flush=True)
        else:
            error_count += 1
            record["error"] = f"Fetch failed with status {status}"
            print(f"[FAILED: {status}]", flush=True)

        # 稍微暫停避免觸發頻率限制
        time.sleep(0.2)

    print(f"\n=== 補抓成果統計 ===", flush=True)
    print(f"成功抓取並生成 Markdown: {success_count} 筆")
    print(f"已確認實體歸位: {resolved_existing} 筆")
    print(f"上游已下架 (404 Not Found): {not_found_count} 筆")
    print(f"其他失敗: {error_count} 筆")

    if args.apply:
        # 寫回 downloads.json
        catalog_data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(DOWNLOADS_FILE, "w", encoding="utf-8") as f:
            json.dump(catalog_data, f, indent=2, ensure_ascii=False)
        print(f"[OK] 已更新寫回 {DOWNLOADS_FILE}！", flush=True)


if __name__ == "__main__":
    main()
