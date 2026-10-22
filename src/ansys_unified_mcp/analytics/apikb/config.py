"""
API 知識層 (API Knowledge Base) 配置與路徑定義。
"""
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone
import re

REPO_ROOT = Path(__file__).resolve().parents[4]
DOCS_DIR = REPO_ROOT / "docs" / "api_inventory"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

# SQLite 資料庫存放路徑 (與 docsearch 一致存於 Documentation_clean)
DB_DIR = REPO_ROOT / "Documentation_clean"
DB_PATH = DB_DIR / "api_kb.sqlite"

# 來源 JSON 檔案清單
SOURCES = {
    "mechanical": DOCS_DIR / "mechanical_api.json",
    "spaceclaim": DOCS_DIR / "spaceclaim_api.json",
    "optislang": DOCS_DIR / "optislang_api.json",
    "lsdyna": DOCS_DIR / "lsdyna_api.json",
}

# 每個快照提供可追溯版本；新增版本時以獨立檔案登錄，避免覆蓋舊版。
INTERFACES = {
    "mechanical": "Mechanical ACT object model",
    "spaceclaim": "SpaceClaim embedded scripting API",
    "optislang": "PyOptiSLang and scripting API",
    "lsdyna": "LS-DYNA keyword and LS-PrePost APIs",
}


def source_snapshots() -> list[tuple[str, Path]]:
    """回傳既有來源及同產品額外快照；保留 SOURCES 的舊字典介面。"""
    snapshots = []
    for product, primary in SOURCES.items():
        candidates = [primary, *sorted(DOCS_DIR.glob(f"{product}_api_v*.json"))]
        seen = set()
        for candidate in candidates:
            if candidate.is_file() and candidate.resolve() not in seen:
                snapshots.append((product, candidate))
                seen.add(candidate.resolve())
    return snapshots


def source_metadata(product: str, path: Path) -> dict:
    """由 API JSON 的明示版本與內容 hash 建立來源紀錄。"""
    raw = path.read_bytes()
    try:
        data = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        data = {}
    version = str(data.get("version", "unknown"))
    if version == "unknown":
        filename_release = re.search(r"v(?:251|252|261)", path.stem, re.I)
        if filename_release:
            version = filename_release.group(0).lower()
    sdk_version = ""
    if product == "optislang":
        sdk_version = version
        version = "unknown (product release not recorded)"
    return {
        "product": product,
        "release": version,
        "interface": INTERFACES.get(product, "unknown"),
        "source_path": path.as_posix(),
        "sdk_version": sdk_version,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }

# 高頻通用方法白名單（出現於超過此數量類別時，標記為 is_inherited 且降低搜尋權重）
INHERITED_THRESHOLD = 50
COMMON_INHERITED_NAMES = {
    "Equals", "GetHashCode", "GetType", "ToString", "MemberwiseClone",
    "ReferenceEquals", "GetObjectData", "CopyTo", "GetChildren",
    "IsPropertyVisible", "IsPropertyEditable", "__init__", "__repr__", "__str__"
}
