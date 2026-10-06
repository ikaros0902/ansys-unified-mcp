#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""專案目錄結構拓撲客觀自動化驗證腳本。

本腳本用於嚴格驗證專案目錄重構後之拓撲結構，確保滿足：
1. 專案根目錄非隱藏資料夾嚴格為 5 個：['agents', 'docs', 'scripts', 'src', 'tests']。
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

# 規格定義：嚴格允許之 5 大核心非隱藏目錄
EXPECTED_CORE_DIRS: frozenset[str] = frozenset(
    {"agents", "docs", "scripts", "src", "tests"}
)

# 規格定義：嚴格禁止存在於專案根目錄之舊資料夾
FORBIDDEN_ROOT_DIRS: frozenset[str] = frozenset(
    {"jobs", "logs", "workbench_queue", "skills", "examples"}
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

    # 1. 檢查專案根目錄下之非隱藏資料夾清單
    current_non_hidden_dirs: set[str] = set()
    for child in root.iterdir():
        if child.is_dir() and not child.name.startswith("."):
            current_non_hidden_dirs.add(child.name)

    result.actual_non_hidden_dirs = sorted(current_non_hidden_dirs)
    result.missing_core_dirs = sorted(
        EXPECTED_CORE_DIRS - current_non_hidden_dirs
    )
    result.unexpected_dirs = sorted(
        current_non_hidden_dirs - EXPECTED_CORE_DIRS
    )

    if (
        current_non_hidden_dirs == EXPECTED_CORE_DIRS
        and len(current_non_hidden_dirs) == 5
    ):
        result.core_dirs_ok = True
        result.messages.append(
            f"[通過] 根目錄核心非隱藏資料夾嚴格為 5 個：{result.actual_non_hidden_dirs}"
        )
    else:
        result.core_dirs_ok = False
        msg_parts = []
        if result.missing_core_dirs:
            msg_parts.append(f"缺少預期目錄：{result.missing_core_dirs}")
        if result.unexpected_dirs:
            msg_parts.append(f"存在多餘目錄：{result.unexpected_dirs}")
        diff_str = "；".join(msg_parts) if msg_parts else "目錄集合不相符"
        result.messages.append(
            f"[失敗] 核心資料夾不符合 5 大目錄規範（目前共 {len(current_non_hidden_dirs)} 個，{diff_str}）"
        )

    # 2. 檢查嚴格禁止存在之舊目錄
    present_forbidden: list[str] = []
    for f_dir in sorted(FORBIDDEN_ROOT_DIRS):
        target = root / f_dir
        if target.exists():
            present_forbidden.append(f_dir)

    result.forbidden_dirs_present = present_forbidden
    if not present_forbidden:
        result.forbidden_dirs_ok = True
        result.messages.append("[通過] 舊目錄已全數自根目錄移除或遷移。")
    else:
        result.forbidden_dirs_ok = False
        result.messages.append(
            f"[失敗] 根目錄仍殘留嚴格禁止之舊目錄：{present_forbidden}"
        )

    # 3. 檢查 .runtime 隱藏目錄及其子目錄結構
    missing_subdirs: list[str] = []
    for rel_subdir in REQUIRED_RUNTIME_SUBDIRS:
        target = root / rel_subdir
        if not target.is_dir():
            missing_subdirs.append(rel_subdir)

    result.missing_runtime_dirs = missing_subdirs
    if not missing_subdirs:
        result.runtime_structure_ok = True
        result.messages.append(
            "[通過] .runtime/ 目錄架構完整（包含 jobs, logs, queue）。"
        )
    else:
        result.runtime_structure_ok = False
        result.messages.append(
            f"[失敗] .runtime/ 缺少必要子目錄：{missing_subdirs}"
        )

    # 4. 檢查 .gitignore 是否包含 .runtime/ 忽略規則
    gitignore_file = root / ".gitignore"
    has_runtime_ignore = check_gitignore_contains_runtime(gitignore_file)
    result.gitignore_has_runtime = has_runtime_ignore
    result.gitignore_ok = has_runtime_ignore

    if has_runtime_ignore:
        result.messages.append(
            "[通過] .gitignore 已正確設定 .runtime/ 排除規則。"
        )
    else:
        result.messages.append(
            "[失敗] .gitignore 未找到有效的 .runtime/ 排除規則。"
        )

    # 綜合評定：四項檢查全數通過才視為有效
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
    print(f"  預期核心目錄 (5 個): {result.expected_dirs}")

    if not result.is_valid:
        print("\n修復指引與待改善項目:")
        if not result.core_dirs_ok:
            print(
                f"  - 核心目錄需收斂至嚴格 5 個：{result.expected_dirs}"
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
    default_root = Path(__file__).resolve().parents[1]
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
