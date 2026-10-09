"""
API 知識層 (API Knowledge Base) 配置與路徑定義。
"""
from pathlib import Path

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

# 高頻通用方法白名單（出現於超過此數量類別時，標記為 is_inherited 且降低搜尋權重）
INHERITED_THRESHOLD = 50
COMMON_INHERITED_NAMES = {
    "Equals", "GetHashCode", "GetType", "ToString", "MemberwiseClone",
    "ReferenceEquals", "GetObjectData", "CopyTo", "GetChildren",
    "IsPropertyVisible", "IsPropertyEditable", "__init__", "__repr__", "__str__"
}
