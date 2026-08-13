"""腳本執行前的安全檢查與審計日誌。

方案 A：偵測 + 警告 + 日誌，不阻擋執行。
在 ANSYS_MCP_SCRIPT_GUARD=strict 時升級為阻擋模式。
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

_AUDIT_LOG_DIR = Path(os.environ.get(
    "ANSYS_MCP_AUDIT_DIR",
    Path(__file__).resolve().parents[3] / "logs" / "script_audit"
))

_MODE = os.environ.get("ANSYS_MCP_SCRIPT_GUARD", "warn")  # warn | strict | off


def check_script(script: str, context: str = "") -> tuple[bool, list[str]]:
    """檢查腳本安全性。回傳 (is_safe, warnings)。"""
    if _MODE == "off":
        return True, []

    warnings = []

    # 檢查危險 import
    for line in script.splitlines():
        stripped = line.strip()
        for mod in _BLOCKED_IMPORTS:
            if re.search(rf"\bimport\s+{mod}\b", stripped) or \
               re.search(rf"\bfrom\s+{mod}\b", stripped):
                warnings.append(f"High-risk import detected: {mod}")

    # 檢查危險函式
    for pattern in _DANGEROUS_PATTERNS:
        match = pattern.search(script)
        if match:
            warnings.append(f"Dangerous call pattern: {match.group()}")

    is_safe = len(warnings) == 0

    if warnings:
        logger.warning(
            "Script guard [%s]: %d warnings in %s: %s",
            _MODE, len(warnings), context, "; ".join(warnings)
        )

    # 審計日誌
    _audit_log(script, context, warnings)

    if _MODE == "strict" and not is_safe:
        return False, warnings

    return True, warnings


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
