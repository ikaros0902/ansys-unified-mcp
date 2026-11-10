#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""專案目錄結構拓撲客觀自動化驗證腳本。

本腳本用於嚴格驗證專案目錄重構後之拓撲結構，確保滿足：
1. 專案根目錄須包含五個正式內容目錄（agents、docs、scripts、src、tests）；本機語料及生成輸出可選存在。
2. 舊目錄（jobs, logs, workbench_queue, skills, examples）完全不在根目錄。
3. .runtime/ 隱藏目錄及其子目錄（.runtime/jobs, .runtime/logs, .runtime/queue）存在。
4. .gitignore 檔案包含 .runtime/ 忽略規則。
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import io
import json
from pathlib import Path
import sys
from typing import Any

# Windows 終端編碼相容性保護
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# 規格定義：正式領域目錄必須存在；生成輸出目錄可選存在
EXPECTED_CORE_DIRS: frozenset[str] = frozenset(
    {
        "agents",
        "docs",
        "scripts",
        "src",
        "tests",
    }
)
OPTIONAL_ROOT_DIRS: frozenset[str] = frozenset(
    {
        "ANSYS_Document",
        "Documentation_clean",
        "__pycache__",
        "artifacts",
        "dist",
        "graphify-out",
    }
)

# 規格定義：嚴格禁止存在於專案根目錄之舊資料夾
FORBIDDEN_ROOT_DIRS: frozenset[str] = frozenset(
    {"jobs", "logs", "workbench_queue", "skills", "examples"}
)

# 程式碼樹中不應保存的歷史 runtime 目錄。
FORBIDDEN_PACKAGE_DIRS: tuple[str, ...] = (
    "src/ansys_unified_mcp/workbench_queue",
)

# 規格定義：.runtime 下必須存在之子目錄
REQUIRED_RUNTIME_SUBDIRS: tuple[str, ...] = (
    ".runtime/jobs",
    ".runtime/logs",
    ".runtime/queue",
)


@dataclass
class TopologyVerificationResult:
    """目錄拓撲驗證結果資料結構。"""

    is_valid: bool = False
    core_dirs_ok: bool = False
    forbidden_dirs_ok: bool = False
    runtime_structure_ok: bool = False
    gitignore_ok: bool = False

    actual_non_hidden_dirs: list[str] = field(default_factory=list)
    expected_dirs: list[str] = field(
        default_factory=lambda: sorted(EXPECTED_CORE_DIRS)
    )
    unexpected_dirs: list[str] = field(default_factory=list)
    missing_core_dirs: list[str] = field(default_factory=list)
    forbidden_dirs_present: list[str] = field(default_factory=list)
    missing_runtime_dirs: list[str] = field(default_factory=list)
    gitignore_has_runtime: bool = False
    messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典供序列化輸出。"""
        return {
            "is_valid": self.is_valid,
            "core_dirs_ok": self.core_dirs_ok,
            "forbidden_dirs_ok": self.forbidden_dirs_ok,
            "runtime_structure_ok": self.runtime_structure_ok,
            "gitignore_ok": self.gitignore_ok,
            "actual_non_hidden_dirs": self.actual_non_hidden_dirs,
            "expected_dirs": self.expected_dirs,
            "unexpected_dirs": self.unexpected_dirs,
            "missing_core_dirs": self.missing_core_dirs,
            "forbidden_dirs_present": self.forbidden_dirs_present,
            "missing_runtime_dirs": self.missing_runtime_dirs,
            "gitignore_has_runtime": self.gitignore_has_runtime,
            "messages": self.messages,
        }


def check_gitignore_contains_runtime(gitignore_path: Path) -> bool:
    """檢查 .gitignore 內容是否包含有效之 .runtime/ 排除規則。

    參數:
        gitignore_path: .gitignore 檔案路徑。

    傳回值:
        若包含有效規則傳回 True，否則傳回 False。
    """
    if not gitignore_path.is_file():
        return False

    try:
        content = gitignore_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = gitignore_path.read_text(encoding="latin-1", errors="replace")

    for raw_line in content.splitlines():
        line = raw_line.strip()
        # 跳過空白行與註解行
        if not line or line.startswith("#"):
            continue

        # 規範比對：檢查是否有針對 .runtime 的規則
        # 例如：.runtime, .runtime/, .runtime/*, **/.runtime, **/.runtime/
        normalized = line.rstrip("/")
        if normalized in {".runtime", "**/.runtime"} or line.startswith(
            (".runtime/", "**/.runtime/")
        ):
            return True

    return False


def verify_directory_topology(
    repo_root: Path | str,
) -> TopologyVerificationResult:
    """針對指定的專案根目錄執行完整的拓撲結構驗證。

    參數:
        repo_root: 專案根目錄路徑。

    傳回值:
        TopologyVerificationResult 物件，包含各項檢查布林值與詳細訊息。
    """
    root = Path(repo_root).resolve()
    result = TopologyVerificationResult()

    if not root.is_dir():
        result.messages.append(f"錯誤：指定之路徑不存在或非資料夾：{root}")
        return result

    current_non_hidden_dirs = {
        child.name
        for child in root.iterdir()
        if child.is_dir() and not child.name.startswith(".")
    }
    allowed_root_dirs = EXPECTED_CORE_DIRS | OPTIONAL_ROOT_DIRS
    result.actual_non_hidden_dirs = sorted(current_non_hidden_dirs)
    result.missing_core_dirs = sorted(EXPECTED_CORE_DIRS - current_non_hidden_dirs)
    result.unexpected_dirs = sorted(current_non_hidden_dirs - allowed_root_dirs)

    if not result.missing_core_dirs and not result.unexpected_dirs:
        result.core_dirs_ok = True
        optional = sorted(current_non_hidden_dirs & OPTIONAL_ROOT_DIRS)
        result.messages.append(
            "[通過] 五個正式目錄齊全；可選本機資料／生成目錄："
            f"{optional}。根目錄目錄：{result.actual_non_hidden_dirs}"
        )
    else:
        result.core_dirs_ok = False
        msg_parts = []
        if result.missing_core_dirs:
            msg_parts.append(f"缺少正式目錄：{result.missing_core_dirs}")
        if result.unexpected_dirs:
            msg_parts.append(f"未分類目錄：{result.unexpected_dirs}")
        diff_str = "；".join(msg_parts)
        result.messages.append(
            f"[失敗] 根目錄拓撲不符合規範（正式目錄 {len(EXPECTED_CORE_DIRS)} 個，{diff_str}）"
        )

    present_forbidden = sorted(
        [name for name in FORBIDDEN_ROOT_DIRS if (root / name).exists()]
        + [path for path in FORBIDDEN_PACKAGE_DIRS if (root / path).exists()]
    )
    result.forbidden_dirs_present = present_forbidden
    result.forbidden_dirs_ok = not present_forbidden
    if result.forbidden_dirs_ok:
        result.messages.append("[通過] 舊目錄已全數自根目錄移除或遷移。")
    else:
        result.messages.append(
            f"[失敗] 專案仍殘留嚴格禁止之舊路徑：{present_forbidden}"
        )

    missing_subdirs = [
        rel_subdir
        for rel_subdir in REQUIRED_RUNTIME_SUBDIRS
        if not (root / rel_subdir).is_dir()
    ]
    result.missing_runtime_dirs = missing_subdirs
    result.runtime_structure_ok = not missing_subdirs
    if result.runtime_structure_ok:
        result.messages.append(
            "[通過] .runtime/ 目錄架構完整（包含 jobs, logs, queue）。"
        )
    else:
        result.messages.append(
            f"[失敗] .runtime/ 缺少必要子目錄：{missing_subdirs}"
        )

    has_runtime_ignore = check_gitignore_contains_runtime(root / ".gitignore")
    result.gitignore_has_runtime = has_runtime_ignore
    result.gitignore_ok = has_runtime_ignore
    if has_runtime_ignore:
        result.messages.append("[通過] .gitignore 已正確設定 .runtime/ 排除規則。")
    else:
        result.messages.append("[失敗] .gitignore 未找到有效的 .runtime/ 排除規則。")

    result.is_valid = (
        result.core_dirs_ok
        and result.forbidden_dirs_ok
        and result.runtime_structure_ok
        and result.gitignore_ok
    )
    return result


def print_report(
    result: TopologyVerificationResult, root: Path, json_mode: bool = False
) -> None:
    """印出格式化之驗證報告。"""
    if json_mode:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return

    print("=" * 64)
    print("專案目錄結構拓撲客觀自動化驗證報告")
    print(f"檢驗根目錄路徑: {root}")
    print("=" * 64)

    status_str = "【驗證通過 (PASS)】" if result.is_valid else "【驗證失敗 (FAIL)】"
    print(f"總體驗證結果: {status_str}\n")

    print("各項檢查指標明細:")
    for msg in result.messages:
        print(f"  {msg}")

    print("\n資料夾拓撲現況:")
    print(
        f"  實際非隱藏目錄 ({len(result.actual_non_hidden_dirs)} 個): {result.actual_non_hidden_dirs}"
    )
    print(f"  預期核心目錄 ({len(result.expected_dirs)} 個): {result.expected_dirs}")

    if not result.is_valid:
        print("\n修復指引與待改善項目:")
        if not result.core_dirs_ok:
            print(
                f"  - 補齊正式目錄並處理未分類目錄：{result.missing_core_dirs}、{result.unexpected_dirs}"
            )
        if not result.forbidden_dirs_ok:
            print(
                f"  - 請將舊目錄遷移或清除：{result.forbidden_dirs_present}"
            )
        if not result.runtime_structure_ok:
            print(
                f"  - 請確保 .runtime/ 子資料夾建立完成：{result.missing_runtime_dirs}"
            )
        if not result.gitignore_ok:
            print("  - 請於 .gitignore 加入 .runtime/ 規則避免暫存被提交。")

    print("=" * 64)


def main() -> int:
    """主命令列進入點。"""
    parser = argparse.ArgumentParser(
        description="專案目錄拓撲結構自動化驗證工具"
    )
    default_root = Path(__file__).resolve().parents[2]
    parser.add_argument(
        "--root",
        type=str,
        default=str(default_root),
        help=f"指定要驗證的專案根目錄 (預設: {default_root})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式輸出驗證結果",
    )

    args = parser.parse_args()
    target_root = Path(args.root).resolve()

    result = verify_directory_topology(target_root)
    print_report(result, target_root, json_mode=args.json)

    return 0 if result.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
