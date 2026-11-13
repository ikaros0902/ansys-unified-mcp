# -*- coding: utf-8 -*-
"""檔案政策檢查工具 (File Policy Checker)

供 Agent Hook 共用的輕量檢查後端，僅依標準庫。提供三種檢查：

1. ascii      : ANSYS 內嵌腳本（ACT / APDL / SpaceClaim，IronPython 2.7）的註解與
                字串若含非 ASCII 字元，會導致解譯器編碼崩潰，必須標記。
2. abs-path   : 偵測硬編碼的機器專屬絕對路徑（如 C:/Users/... 或 D:/...），
                防止跨電腦不可攜。
3. skill-lines: SKILL.md 超過 150 行違反漸進式揭露原則（見 11-skill-evolution）。

違規時以 `<檔案>:<行號>: <說明>` 輸出並回傳 exit code 1；無違規回傳 0。
"""

import argparse
import re
import sys
from pathlib import Path

# 防止 Windows 終端機 CP950 編碼輸出報錯
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 機器專屬絕對路徑樣式：Windows 磁碟代號開頭（C:/、D:\ 等）。
# 相對路徑與純檔名不受影響。
_ABS_PATH_RE = re.compile(r"[A-Za-z]:[\\/]")

SKILL_LINE_LIMIT = 150


def _read_lines(path: Path) -> list[str]:
    """以 UTF-8 讀取檔案行（忽略無法解碼的位元組，避免檢查器自身崩潰）。"""
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def check_ascii(path: Path) -> list[tuple[int, str]]:
    """回傳含非 ASCII 字元的行 (行號, 說明)。行號從 1 起算。"""
    violations: list[tuple[int, str]] = []
    for i, line in enumerate(_read_lines(path), start=1):
        if any(ord(ch) > 127 for ch in line):
            violations.append((i, "含非 ASCII 字元（ANSYS 內嵌腳本須純英文）"))
    return violations


def check_abs_path(path: Path) -> list[tuple[int, str]]:
    """回傳含機器專屬絕對路徑的行 (行號, 說明)。"""
    violations: list[tuple[int, str]] = []
    for i, line in enumerate(_read_lines(path), start=1):
        if _ABS_PATH_RE.search(line):
            violations.append((i, "疑似硬編碼絕對路徑（請改用相對路徑或設定注入）"))
    return violations


def check_skill_lines(path: Path, limit: int = SKILL_LINE_LIMIT) -> list[tuple[int, str]]:
    """SKILL.md 超過行數上限時回傳單一違規 (超限行號, 說明)。"""
    lines = _read_lines(path)
    if len(lines) > limit:
        return [(len(lines), f"SKILL.md 共 {len(lines)} 行，超過上限 {limit} 行")]
    return []


_CHECKS = {
    "ascii": check_ascii,
    "abs-path": check_abs_path,
    "skill-lines": check_skill_lines,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="檔案政策檢查（Agent Hook 共用後端）")
    parser.add_argument("--check", required=True, choices=sorted(_CHECKS), help="檢查類型")
    parser.add_argument("paths", nargs="+", help="待檢查的檔案路徑")
    args = parser.parse_args(argv)

    check_fn = _CHECKS[args.check]
    total = 0
    for p in args.paths:
        path = Path(p)
        if not path.is_file():
            continue
        for line_no, msg in check_fn(path):
            print(f"{path}:{line_no}: {msg}")
            total += 1

    if total:
        print(f"[check-{args.check}] 發現 {total} 項違規", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
