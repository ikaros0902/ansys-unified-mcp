"""
ANSYS 腳本 API 校驗器 (Script API Validator)
靜態分析 Mechanical ACT 與 SpaceClaim Python/SCDM 腳本，檢測未定義的 API 成員呼叫並提供最相似的建議。
"""
import ast
import re
import difflib
import sqlite3
from typing import Optional

from ansys_unified_mcp.analytics.apikb import config as cfg
from ansys_unified_mcp.analytics.apikb.query import _get_connection

# 常見 Python / IronPython 內建模組或語言關鍵成員，予以忽略
BUILTIN_ATTRIBUTES = {
    "append", "extend", "insert", "pop", "clear", "index", "count", "sort", "reverse", "copy",
    "keys", "values", "items", "get", "update", "split", "join", "strip", "replace", "format",
    "lower", "upper", "startswith", "endswith", "find", "rfind", "encode", "decode",
    "read", "write", "close", "seek", "tell", "flush", "open",
    "path", "exists", "join", "dirname", "basename", "abspath", "resolve",
    "DataModel", "Project", "Model", "ExtAPI", "SelectionManager", "Tree", "Graphics",
    "Point", "Direction", "Plane", "Matrix", "Vector", "Quantity"
}

def extract_accessed_attributes(code: str) -> set[str]:
    """從代碼中靜態提取所有訪問的屬性與方法名稱"""
    accessed = set()

    # 1. 嘗試以 AST 解析
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                accessed.add(node.attr)
        return accessed
    except Exception:
        pass

    # 2. Fallback: 使用正則表達式提取 .identifier 形式的屬性
    matches = re.findall(r"\.([A-Za-z_][A-Za-z0-9_]*)", code)
    for m in matches:
        accessed.add(m)

    return accessed

def validate_script(code: str, product: str, release: Optional[str] = None,
                    interface: Optional[str] = None) -> dict:
    """以 API 名稱清單做部分靜態校驗，不驗證型別、簽名或執行行為。"""
    base = {"validation_level": "name_only", "verification_status": "partial",
            "unverified": ["type", "signature", "runtime behavior"]}
    if not code or not code.strip():
        return {**base, "valid": True, "checked_count": 0, "errors": []}

    accessed_attrs = extract_accessed_attributes(code)
    # 過濾內建通用屬性
    target_attrs = [a for a in accessed_attrs if a not in BUILTIN_ATTRIBUTES and not a.startswith("_")]

    if not target_attrs:
        return {**base, "valid": True, "checked_count": 0, "errors": []}

    conn = _get_connection()
    cur = conn.cursor()

    if release or interface:
        cur.execute(
            "SELECT 1 FROM api_sources WHERE product = ? "
            "AND (? IS NULL OR release = ?) AND (? IS NULL OR interface = ?) LIMIT 1",
            (product.lower(), release, release, interface, interface),
        )
        if cur.fetchone() is None:
            conn.close()
            return {
                **base,
                "verification_status": "coverage_unavailable",
                "coverage_available": False,
                "valid": None,
                "product": product,
                "release": release,
                "interface": interface,
                "checked_count": len(target_attrs),
                "error_count": 0,
                "errors": [],
                "message": "API 字典沒有此產品／版本／介面的來源快照；無法判定名稱是否存在。",
            }

    # 載入該產品下的所有已知有效成員名稱與符號簡稱
    clauses = ["s.product = ?"]
    params: list = [product.lower()]
    if release:
        clauses.append("s.release = ?")
        params.append(release)
    if interface:
        clauses.append("s.interface = ?")
        params.append(interface)
    where = " AND ".join(clauses)
    cur.execute(f"""
        SELECT DISTINCT m.name
        FROM members m
        JOIN symbol_members sm ON m.id = sm.member_id
        JOIN symbols s ON sm.symbol_id = s.id
        WHERE {where}
    """, params)
    valid_names = {row["name"] for row in cur.fetchall()}

    cur.execute(f"SELECT DISTINCT name FROM symbols s WHERE {where}", params)
    valid_symbols = {row["name"] for row in cur.fetchall()}
    all_valid_pool = valid_names | valid_symbols

    conn.close()

    errors = []
    for attr in target_attrs:
        if attr not in all_valid_pool:
            # 尋找最相近的建議
            suggestions = difflib.get_close_matches(attr, all_valid_pool, n=3, cutoff=0.6)
            errors.append({
                "attribute": attr,
                "suggestions": suggestions,
                "message": f"'{attr}' 未在 {product} API 字典中找到" + (f"，您是否想調用: {', '.join(suggestions)}？" if suggestions else "")
            })

    return {
        **base,
        "valid": len(errors) == 0,
        "product": product,
        "release": release,
        "interface": interface,
        "checked_count": len(target_attrs),
        "error_count": len(errors),
        "errors": errors
    }
