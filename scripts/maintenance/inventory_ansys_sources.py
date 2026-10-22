"""盤點 ANSYS 文件來源並輸出可重建的 JSON 清冊。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, timezone


def classify(path: Path, root: Path, size: int, sample: str) -> dict:
    rel = path.relative_to(root).as_posix()
    low = rel.lower()
    product = next((p for p in ("mechanical", "ls-dyna", "lsdyna", "spaceclaim", "icepak", "sherlock", "speos", "zemax", "lumerical", "fluent") if p in low), "unknown")
    category = "tutorial" if "tutorial" in low else "api_reference" if "api" in low else "manual" if "manual" in low or path.suffix.lower() == ".pdf" else "guide"
    release = next(iter(re.findall(r"\b(?:20\d{2})\s*R[12]\b|\bv(?:251|252|261)\b", sample, re.I)), "unknown")
    suffix = path.suffix.lower()
    if size == 0:
        quality = "empty"
    elif suffix == ".pdf":
        quality = "pdf_pending_extraction"
    elif suffix in {".zip", ".7z", ".rar", ".exe", ".dll", ".png", ".jpg", ".jpeg"}:
        quality = "binary_or_archive"
    elif suffix in {".html", ".htm"} and ("{{" in sample or "{%" in sample):
        quality = "template"
    elif suffix in {".html", ".htm"}:
        quality = "html_pending_normalization"
    elif re.search(r"download|not available|coming soon|contents only", sample[:4000], re.I) and len(sample) < 12000:
        quality = "stub_or_download_page"
    elif "{{" in sample or "{%" in sample:
        quality = "template"
    elif suffix not in {".md", ".markdown", ".txt", ".json", ".xml", ".csv"}:
        quality = "unsupported_format"
    else:
        quality = "body_present"
    return {"product": product, "category": category, "release": release, "quality": quality, "source_path": str(path), "relative_path": rel}


def inventory(roots: list[Path]) -> list[dict]:
    items = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            try:
                digest = hashlib.sha256()
                sample_bytes = b""
                with path.open("rb") as stream:
                    while block := stream.read(1024 * 1024):
                        digest.update(block)
                        if len(sample_bytes) < 12000:
                            sample_bytes += block[:12000 - len(sample_bytes)]
                sample = sample_bytes.decode("utf-8", errors="replace")
                row = classify(path, root, path.stat().st_size, sample)
                row.update({"source_root": str(root), "size_bytes": path.stat().st_size,
                            "sha256": digest.hexdigest(), "extension": path.suffix.lower()})
                items.append(row)
            except OSError as exc:
                items.append({"source_root": str(root), "source_path": str(path), "quality": "unreadable", "error": str(exc)})
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", type=Path, required=True, help="來源根目錄，可重複指定")
    parser.add_argument("--output", type=Path, required=True, help="輸出 JSON 清冊位置")
    args = parser.parse_args()
    rows = inventory(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(), "sources": rows},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"output": str(args.output), "source_count": len(rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
