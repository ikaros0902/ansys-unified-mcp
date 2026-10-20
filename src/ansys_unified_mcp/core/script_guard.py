"""腳本執行前的安全檢查與審計日誌。

方案 A：偵測 + 警告 + 日誌，不阻擋執行。
在 ANSYS_MCP_SCRIPT_GUARD=strict 時升級為阻擋模式。
針對無頭批次執行環境（Headless/Batch），額外提供 check_headless_boundary 防範 GUI 模態阻塞彈窗。
"""

import logging
import os
import re
import time
from pathlib import Path

logger = logging.getLogger(__name__)

# 高風險 import 模組黑名單
_BLOCKED_IMPORTS = {
    "subprocess", "shutil", "ctypes", "socket", "http",
    "urllib", "requests", "ftplib", "smtplib", "paramiko",
}

# 高風險函式呼叫模式
_DANGEROUS_PATTERNS = [
    re.compile(r"\bos\s*\.\s*system\s*\("),
    re.compile(r"\bos\s*\.\s*popen\s*\("),
    re.compile(r"\bos\s*\.\s*exec\w*\s*\("),
    re.compile(r"\b__import__\s*\("),
    re.compile(r"\beval\s*\("),
    re.compile(r"\bcompile\s*\("),
    re.compile(r"\bopen\s*\([^)]*['\"]\/etc"),  # Unix 敏感路徑
]

# 無頭環境 (Headless/Batch) 嚴禁出現之 GUI 阻塞或人機互動呼叫 (CADWorld 邊界防護)
_GUI_BLOCKING_PATTERNS = [
    re.compile(r"\bMessageBox\s*\.\s*Show\s*\("),
    re.compile(r"\bSystem\.Windows\.Forms\.MessageBox\b"),
    re.compile(r"\bctypes\.windll\.user32\.MessageBox\w*\s*\("),
    re.compile(r"(?<![.\w])input\s*\("),
    re.compile(r"(?<![.\w])raw_input\s*\("),
    re.compile(r"\bpyautogui\s*\."),
    re.compile(r"\bxdotool\b"),
    re.compile(r"\btkinter\.messagebox\b"),
]

from ansys_unified_mcp.core.paths import resolve_runtime_dir

_AUDIT_LOG_DIR = Path(os.environ.get(
    "ANSYS_MCP_AUDIT_DIR",
    resolve_runtime_dir() / "logs" / "script_audit"
))

_MODE = os.environ.get("ANSYS_MCP_SCRIPT_GUARD", "warn")  # warn | strict | off


def _strip_comments(script: str) -> str:
    """去除單行註解 (# ...)，避免註解內的示範關鍵字誤傷腳本檢查。"""
    cleaned_lines = []
    for line in script.splitlines():
        # 若整行是註解
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # 若行內有註解且非在字串中（簡單安全截斷）
        if "#" in line:
            # 僅在非引號包含的註解時截斷
            parts = line.split("#", 1)
            # 若前段引號已閉合
            prefix = parts[0]
            if (prefix.count('"') % 2 == 0) and (prefix.count("'") % 2 == 0):
                cleaned_lines.append(prefix)
                continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def check_script(
    script: str,
    context: str = "",
    block_gui_popups: bool = False,
) -> tuple[bool, list[str]]:
    """檢查腳本安全性。回傳 (is_safe, warnings)。

    Args:
        script: 待檢查的腳本字串
        context: 調用上下文說明（記錄於日誌）
        block_gui_popups: 若為 True，一旦檢測到 GUI 模態阻塞呼叫即視為 unsafe (is_safe=False)
    """
    if _MODE == "off":
        return True, []

    warnings: list[str] = []
    clean_code = _strip_comments(script)

    # 檢查危險 import
    for line in clean_code.splitlines():
        stripped = line.strip()
        for mod in _BLOCKED_IMPORTS:
            if re.search(rf"\bimport\s+{mod}\b", stripped) or \
               re.search(rf"\bfrom\s+{mod}\b", stripped):
                warnings.append(f"High-risk import detected: {mod}")

    # 檢查危險函式
    for pattern in _DANGEROUS_PATTERNS:
        match = pattern.search(clean_code)
        if match:
            warnings.append(f"Dangerous call pattern: {match.group()}")

    # 檢查 GUI 模態阻塞呼叫
    gui_blocked = False
    for pattern in _GUI_BLOCKING_PATTERNS:
        match = pattern.search(clean_code)
        if match:
            warnings.append(f"GUI-blocking call detected in headless script: {match.group()}")
            gui_blocked = True

    is_safe = (len(warnings) == 0)

    if block_gui_popups and gui_blocked:
        is_safe = False

    if warnings:
        logger.warning(
            "Script guard [%s]: %d warnings in %s: %s",
            _MODE, len(warnings), context, "; ".join(warnings)
        )

    # 審計日誌
    _audit_log(script, context, warnings)

    if _MODE == "strict" and not is_safe:
        return False, warnings

    return is_safe, warnings


def check_headless_boundary(script: str, context: str = "headless") -> tuple[bool, list[str]]:
    """專為無頭執行環境設計的硬性邊界檢查。

    拒絕空腳本，並強制阻斷任何 GUI 模態彈窗、pyautogui 或使用者互動輸入。
    """
    if not script or not script.strip():
        return False, ["Empty headless script is prohibited"]

    return check_script(script, context=context, block_gui_popups=True)


def _audit_log(script: str, context: str, warnings: list[str]):
    """將腳本執行記錄寫入審計日誌。"""
    try:
        _AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        log_file = _AUDIT_LOG_DIR / f"audit_{ts}.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"=== {time.strftime('%Y-%m-%d %H:%M:%S')} | {context} ===\n")
            if warnings:
                f.write(f"WARNINGS: {'; '.join(warnings)}\n")
            f.write(script[:2000])  # 只記前 2000 字元
            f.write("\n\n")
    except Exception:
        pass
