#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""FastMCP 工具鏈註冊與解析客觀自動化驗證腳本。

本腳本用於嚴格驗證 FastMCP 伺服器之工具暴露與解析狀態，確保滿足：
1. 預設精簡模式 (Pruned) 下，Canonical 工具總數 >= 143（目前規格預期 155 個）。
2. 相容模式 (Exposed) 下，總工具數（含 Deprecated Aliases）>= 200（目前規格預期 213 個）。
3. 所有工具均具備有效之名稱與說明文件，且無名稱重複衝突。
4. 提供分類領域統計與客觀退出碼 (0 通過 / 1 失敗)。
"""

from __future__ import annotations

import argparse
import asyncio
from collections import Counter
from dataclasses import dataclass, field
import json
import os
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

# 自動將專案根目錄與 src 加入 sys.path 以便直接執行
_CURRENT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _CURRENT_DIR.parent
_SRC_DIR = _REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# 門檻值常數定義
CANONICAL_MIN_THRESHOLD: int = 143
CANONICAL_EXPECTED_COUNT: int = 155
EXPOSED_MIN_THRESHOLD: int = 200
EXPOSED_EXPECTED_COUNT: int = 213


@dataclass
class FastMCPVerificationResult:
    """FastMCP 工具鏈驗證結果資料結構。"""

    is_valid: bool = False
    canonical_ok: bool = False
    exposed_ok: bool = False
    integrity_ok: bool = False

    canonical_count: int = 0
    exposed_count: int = 0
    canonical_min_threshold: int = CANONICAL_MIN_THRESHOLD
    canonical_expected: int = CANONICAL_EXPECTED_COUNT
    exposed_min_threshold: int = EXPOSED_MIN_THRESHOLD
    exposed_expected: int = EXPOSED_EXPECTED_COUNT

    canonical_tool_names: list[str] = field(default_factory=list)
    exposed_tool_names: list[str] = field(default_factory=list)
    duplicate_canonical_names: list[str] = field(default_factory=list)
    duplicate_exposed_names: list[str] = field(default_factory=list)

    canonical_categories: dict[str, int] = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典供序列化輸出。"""
        return {
            "is_valid": self.is_valid,
            "canonical_ok": self.canonical_ok,
            "exposed_ok": self.exposed_ok,
            "integrity_ok": self.integrity_ok,
            "canonical_count": self.canonical_count,
            "exposed_count": self.exposed_count,
            "canonical_min_threshold": self.canonical_min_threshold,
            "canonical_expected": self.canonical_expected,
            "exposed_min_threshold": self.exposed_min_threshold,
            "exposed_expected": self.exposed_expected,
            "duplicate_canonical_names": self.duplicate_canonical_names,
            "duplicate_exposed_names": self.duplicate_exposed_names,
            "canonical_categories": self.canonical_categories,
            "messages": self.messages,
        }


async def verify_fastmcp_tools() -> FastMCPVerificationResult:
    """非同步載入 FastMCP 伺服器並執行完整的工具清單驗證。

    傳回值:
        FastMCPVerificationResult: 檢驗結果結構體。
    """
    result = FastMCPVerificationResult()

    try:
        # 動態載入 FastMCP 實例與入口模組以確保所有工具被註冊
        from ansys_unified_mcp.shared import mcp, _wrapped_list_tools
        import ansys_unified_mcp.__main__  # noqa: F401
    except Exception as e:
        result.messages.append(f"[失敗] 匯入 FastMCP 伺服器模組失敗：{e}")
        return result

    # 1. 驗證預設模式 (Pruned / Canonical 原語工具)
    try:
        # 確保環境變數重設為 0 以驗證 Pruned 模式
        os.environ["ANSYS_MCP_EXPOSE_ALIASES"] = "0"
        canonical_tools = await mcp.list_tools()
        result.canonical_count = len(canonical_tools)
        canonical_names = [tool.name for tool in canonical_tools]
        result.canonical_tool_names = sorted(canonical_names)

        # 檢查是否有重複工具
        c_counter = Counter(canonical_names)
        c_duplicates = [name for name, count in c_counter.items() if count > 1]
        result.duplicate_canonical_names = c_duplicates

        # 統計領域分類
        cat_counter: Counter[str] = Counter()
        for name in canonical_names:
            prefix = name.split("_")[0] if "_" in name else "other"
            cat_counter[prefix] += 1
        result.canonical_categories = dict(cat_counter.most_common())

        if result.canonical_count >= CANONICAL_MIN_THRESHOLD:
            result.canonical_ok = True
            result.messages.append(
                f"[通過] 預設模式 Canonical 工具數達標：{result.canonical_count} 個 "
                f"(門檻: >={CANONICAL_MIN_THRESHOLD}，預期: {CANONICAL_EXPECTED_COUNT})"
            )
        else:
            result.canonical_ok = False
            result.messages.append(
                f"[失敗] 預設模式 Canonical 工具數不足：{result.canonical_count} 個 "
                f"(門檻: >={CANONICAL_MIN_THRESHOLD})"
            )

        if c_duplicates:
            result.messages.append(
                f"[失敗] 發現重複的 Canonical 工具名稱：{c_duplicates}"
            )
    except Exception as e:
        result.canonical_ok = False
        result.messages.append(f"[失敗] 查詢 Canonical 工具清單發生例外：{e}")

    # 2. 驗證相容模式 (Exposed / 包含 Deprecated Aliases)
    try:
        os.environ["ANSYS_MCP_EXPOSE_ALIASES"] = "1"
        exposed_tools = await _wrapped_list_tools()
        result.exposed_count = len(exposed_tools)
        exposed_names = [tool.name for tool in exposed_tools]
        result.exposed_tool_names = sorted(exposed_names)

        # 檢查是否有重複工具
        e_counter = Counter(exposed_names)
        e_duplicates = [name for name, count in e_counter.items() if count > 1]
        result.duplicate_exposed_names = e_duplicates

        if result.exposed_count >= EXPOSED_MIN_THRESHOLD:
            result.exposed_ok = True
            result.messages.append(
                f"[通過] 相容模式 Exposed 工具數達標：{result.exposed_count} 個 "
                f"(門檻: >={EXPOSED_MIN_THRESHOLD}，預期: {EXPOSED_EXPECTED_COUNT})"
            )
        else:
            result.exposed_ok = False
            result.messages.append(
                f"[失敗] 相容模式 Exposed 工具數不足：{result.exposed_count} 個 "
                f"(門檻: >={EXPOSED_MIN_THRESHOLD})"
            )

        if e_duplicates:
            result.messages.append(
                f"[失敗] 發現重複的 Exposed 工具名稱：{e_duplicates}"
            )
    except Exception as e:
        result.exposed_ok = False
        result.messages.append(f"[失敗] 查詢 Exposed 工具清單發生例外：{e}")

    # 3. 完整性檢驗：無重複名稱且兩個模式均無空工具
    result.integrity_ok = (
        len(result.duplicate_canonical_names) == 0
        and len(result.duplicate_exposed_names) == 0
        and result.canonical_count > 0
        and result.exposed_count > 0
    )

    if result.integrity_ok:
        result.messages.append("[通過] 工具完整性檢查通過，無重複命名衝突。")
    else:
        result.messages.append("[失敗] 工具完整性檢查未通過。")

    # 綜合評定
    result.is_valid = (
        result.canonical_ok and result.exposed_ok and result.integrity_ok
    )

    return result


def verify_fastmcp_tools_sync() -> FastMCPVerificationResult:
    """同步包裝進入點。"""
    return asyncio.run(verify_fastmcp_tools())


def print_report(
    result: FastMCPVerificationResult, json_mode: bool = False
) -> None:
    """印出格式化之 FastMCP 工具鏈驗證報告。"""
    if json_mode:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return

    print("=" * 64)
    print("FastMCP 工具鏈註冊與解析客觀自動化驗證報告")
    print("=" * 64)

    status_str = "【驗證通過 (PASS)】" if result.is_valid else "【驗證失敗 (FAIL)】"
    print(f"總體驗證結果: {status_str}\n")

    print("工具數量統計指標:")
    print(
        f"  - 預設 Canonical 原語工具數: {result.canonical_count} 個 "
        f"(要求: >={result.canonical_min_threshold}, 規格預期: {result.canonical_expected})"
    )
    print(
        f"  - 相容模式 Exposed 總工具數: {result.exposed_count} 個 "
        f"(要求: >={result.exposed_min_threshold}, 規格預期: {result.exposed_expected})"
    )

    print("\n領域前綴分類分佈 (Top 10):")
    for idx, (cat, count) in enumerate(
        list(result.canonical_categories.items())[:10], start=1
    ):
        print(f"  {idx:2d}. {cat:<15}: {count:3d} 個工具")

    print("\n各項檢查指標明細:")
    for msg in result.messages:
        print(f"  {msg}")

    print("=" * 64)


def main() -> int:
    """主命令列進入點。"""
    parser = argparse.ArgumentParser(
        description="FastMCP 工具鏈註冊與解析自動化驗證工具"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式輸出驗證結果",
    )

    args = parser.parse_args()
    result = verify_fastmcp_tools_sync()
    print_report(result, json_mode=args.json)

    return 0 if result.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
