#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腳本名稱：evict_global_ansys_skills.py
功能說明：全域技能目錄 ANSYS 重複技能清退與安全備份工具。

背景痛點：
  當專案工作區（ansys-unified-mcp/agents/skills/）與全域目錄（~/.gemini/config/skills/）
  同時存在 ANSYS 相關技能時，Agent 會同時載入兩份相同的 Prompt，造成「雙倍 Token 稅」
  與工作區修改後全域未同步的「新舊腦裂」問題。

執行邏輯：
  1. 掃描全域技能目錄（預設：C:\\Users\\Ming\\.gemini\\config\\skills\\）。
  2. 精準辨識 ANSYS 領域技能（ansys-*, pcb-warpage-analysis, shock-analysis-workflow,
     pymechanical-operations, act-extension-development, pdf-to-md 等）。
  3. 安全建立全量備份目錄（~/.gemini/config/skills_backup_<timestamp>/）並寫入清單。
  4. 從全域目錄徹底清退 ANSYS 技能，釋放 Token 負載。
  5. 嚴格保留所有通用/架構類非 ANSYS 技能（architect-discipline, code-deslop, tdd 等）。

旗標支援：
  --dry-run : 乾跑模式，僅預覽清退名單與保留名單，不修改任何檔案。
  --force   : 強制執行模式，無須終端互動確認。
  --restore : 從指定備份目錄還原技能。
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import sys
from pathlib import Path

# 預設全域技能路徑
DEFAULT_GLOBAL_SKILLS_DIR = Path.home() / ".gemini" / "config" / "skills"

# 精準辨識 ANSYS 領域技能清單
KNOWN_ANSYS_EXACT_NAMES: set[str] = {
    "act-extension-development",
    "pcb-warpage-analysis",
    "pdf-to-md",
    "pymechanical-operations",
    "shock-analysis-workflow",
    "simplify-ram",
    "simplify-heatsink",
}


def is_ansys_skill(skill_name: str) -> bool:
    """判斷技能名稱是否屬於 ANSYS 專案領域技能。"""
    name_lower = skill_name.lower().strip()
    if name_lower.startswith("ansys-") or name_lower.startswith("ansys_"):
        return True
    if name_lower in KNOWN_ANSYS_EXACT_NAMES:
        return True
    return False


def get_dir_size_and_count(dir_path: Path) -> tuple[int, int]:
    """計算目錄內檔案大小（bytes）與檔案總數。"""
    total_size = 0
    file_count = 0
    for p in dir_path.rglob("*"):
        if p.is_file():
            file_count += 1
            try:
                total_size += p.stat().st_size
            except OSError:
                pass
    return total_size, file_count


def scan_skills(global_dir: Path) -> tuple[list[Path], list[Path]]:
    """掃描全域技能目錄，分類出清退名單 (to_evict) 與保留名單 (to_preserve)。"""
    to_evict: list[Path] = []
    to_preserve: list[Path] = []

    if not global_dir.is_dir():
        return to_evict, to_preserve

    for item in sorted(global_dir.iterdir()):
        # 略過隱藏目錄（例如 .hub、.git）及非目錄檔案
        if item.name.startswith("."):
            continue
        if not item.is_dir():
            continue

        if is_ansys_skill(item.name):
            to_evict.append(item)
        else:
            to_preserve.append(item)

    return to_evict, to_preserve


def run_dry_run(global_dir: Path, to_evict: list[Path], to_preserve: list[Path]) -> None:
    """乾跑預覽輸出。"""
    print("=" * 70)
    print("【DRY-RUN 乾跑預覽】全域技能目錄清退評估")
    print(f"掃描目錄：{global_dir.resolve()}")
    print("=" * 70)

    print(f"\n[待清退清單] (共 {len(to_evict)} 個 ANSYS 重複技能，將自全域移除)：")
    total_evict_bytes = 0
    total_evict_files = 0
    for p in to_evict:
        size_b, count = get_dir_size_and_count(p)
        total_evict_bytes += size_b
        total_evict_files += count
        print(f"  - [EVICT] {p.name:<35} ({count:>3} 檔, {size_b / 1024:>7.1f} KB)")

    print(f"  => 預計釋放總計：{total_evict_files} 檔案, {total_evict_bytes / 1024 / 1024:.2f} MB")

    print(f"\n[嚴格保留清單] (共 {len(to_preserve)} 個通用/架構技能，完好保留於全域)：")
    for p in to_preserve:
        print(f"  + [KEEP]  {p.name}")

    print("\n" + "=" * 70)
    print("乾跑結束。若確定執行清退，請帶 `--force` 旗標以執行備份並移除。")
    print("=" * 70)


def execute_eviction(
    global_dir: Path,
    to_evict: list[Path],
    to_preserve: list[Path],
    custom_backup_dir: Path | None = None,
) -> bool:
    """執行完整備份與清退程序。"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = custom_backup_dir or (global_dir.parent / f"skills_backup_{timestamp}")

    print("=" * 70)
    print("【開始執行】全域 ANSYS 重複技能安全備份與清退")
    print(f"全域目錄：{global_dir.resolve()}")
    print(f"備份目錄：{backup_dir.resolve()}")
    print("=" * 70)

    # 1. 建立備份目錄
    backup_dir.mkdir(parents=True, exist_ok=True)
    manifest_records: list[dict] = []

    print("\n[階段一：安全備份副本複製]")
    for p in to_evict:
        target_sub = backup_dir / p.name
        size_b, count = get_dir_size_and_count(p)
        print(f"  -> 備份中：{p.name} ({count} 檔)...", end="", flush=True)
        shutil.copytree(p, target_sub, dirs_exist_ok=True)
        print(" [完成]")
        manifest_records.append({
            "name": p.name,
            "original_path": str(p.resolve()),
            "backup_path": str(target_sub.resolve()),
            "file_count": count,
            "size_bytes": size_b,
        })

    # 寫入備份清單 (backup_manifest.json)
    manifest_file = backup_dir / "backup_manifest.json"
    manifest_payload = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "global_skills_dir": str(global_dir.resolve()),
        "backup_dir": str(backup_dir.resolve()),
        "evicted_count": len(manifest_records),
        "evicted_skills": manifest_records,
        "preserved_count": len(to_preserve),
        "preserved_skills": [p.name for p in to_preserve],
    }
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest_payload, f, indent=2, ensure_ascii=False)
    print(f"[清單] 備份清單已寫入：{manifest_file}")

    # 2. 驗證備份完整性
    for record in manifest_records:
        b_path = Path(record["backup_path"])
        if not b_path.is_dir():
            print(f"[致命錯誤] 備份目錄未驗證通過：{b_path} 不存在！中斷清退作業。", file=sys.stderr)
            return False

    # 3. 執行全域清退
    print("\n[階段二：全域目錄清退移除]")
    for p in to_evict:
        print(f"  <- 正在從全域清退：{p.name}...", end="", flush=True)
        try:
            shutil.rmtree(p)
            print(" [已移除]")
        except OSError as e:
            print(f" [失敗: {e}]", file=sys.stderr)

    # 4. 驗證保留技能完好無損
    print("\n[階段三：驗證全域保留技能完整性]")
    missing_preserves = []
    for p in to_preserve:
        if not p.is_dir():
            missing_preserves.append(p.name)

    if missing_preserves:
        print(f"[錯誤] 以下保留技能發生異常缺失：{missing_preserves}", file=sys.stderr)
        return False

    print(f"  [驗證通過] 全域 {len(to_preserve)} 個通用/架構技能均完好保留！")
    print("=" * 70)
    print(f"[清退成功] 共備份並清退 {len(to_evict)} 個技能。")
    print(f"備份路徑：{backup_dir.resolve()}")
    print("雙倍 Token 稅與新舊腦裂已徹底消除。")
    print("=" * 70)
    return True


def execute_restore(backup_dir: Path, global_dir: Path) -> bool:
    """從備份目錄還原技能至全域目錄。"""
    manifest_file = backup_dir / "backup_manifest.json"
    if not manifest_file.exists():
        print(f"[錯誤] 找不到備份清單：{manifest_file}", file=sys.stderr)
        return False

    with open(manifest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("=" * 70)
    print(f"【執行還原】從備份目錄 {backup_dir.resolve()} 還原至 {global_dir.resolve()}")
    print("=" * 70)

    for item in data.get("evicted_skills", []):
        name = item["name"]
        src = backup_dir / name
        dst = global_dir / name
        if src.is_dir():
            print(f"  -> 還原中：{name}...", end="", flush=True)
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(" [完成]")

    print("[還原成功] 所有技能已恢復至全域目錄。")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="全域技能目錄 ANSYS 重複技能清退與安全備份工具"
    )
    parser.add_argument(
        "--global-dir",
        type=Path,
        default=DEFAULT_GLOBAL_SKILLS_DIR,
        help="指定全域技能目錄路徑 (預設: ~/.gemini/config/skills/)",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        help="指定備份存放目錄 (預設: ~/.gemini/config/skills_backup_<timestamp>/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="預覽清退名單與保留名單，不執行任何修改",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="略過互動確認，直接執行備份與清退",
    )
    parser.add_argument(
        "--restore",
        type=Path,
        default=None,
        metavar="BACKUP_PATH",
        help="從指定備份目錄還原技能至全域目錄",
    )

    args = parser.parse_args()

    # 還原模式
    if args.restore:
        ok = execute_restore(args.restore, args.global_dir)
        return 0 if ok else 1

    if not args.global_dir.is_dir():
        print(f"[錯誤] 全域技能目錄不存在：{args.global_dir}", file=sys.stderr)
        return 1

    to_evict, to_preserve = scan_skills(args.global_dir)

    if not to_evict:
        print(f"[資訊] 全域技能目錄中未發現任何 ANSYS 重複技能（已清退完畢）。")
        print(f"現存保留技能數：{len(to_preserve)}")
        return 0

    # 乾跑模式
    if args.dry_run:
        run_dry_run(args.global_dir, to_evict, to_preserve)
        return 0

    # 非強制且有 TTY 時確認
    if not args.force:
        if sys.stdin.isatty():
            run_dry_run(args.global_dir, to_evict, to_preserve)
            answer = input("\n確認執行上述備份與清退？[y/N]: ").strip().lower()
            if answer not in ("y", "yes"):
                print("[取消] 操作已中止。")
                return 0
        else:
            print("[錯誤] 非互動環境下請帶 `--force` 旗標以確認執行清退。", file=sys.stderr)
            return 1

    success = execute_eviction(
        global_dir=args.global_dir,
        to_evict=to_evict,
        to_preserve=to_preserve,
        custom_backup_dir=args.backup_dir,
    )
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
