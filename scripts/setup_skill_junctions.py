#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腳本名稱：setup_skill_junctions.py
功能說明：跨平台設定技能目錄連接點（Windows NTFS Junction 或 Linux/macOS 符號連結）。
          將專案中次要 IDE / 工具目錄（.kiro/skills 與 .cline/skills）連結至
          唯一真實來源（SKILLs/），達成「單一實體、多處相容」且零冗餘維護。
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "SKILLs"
TARGET_DIRS = [
    REPO_ROOT / ".kiro" / "skills",
    REPO_ROOT / ".cline" / "skills",
]


def is_junction_or_symlink(path: Path) -> bool:
    """判斷指定路徑是否為 NTFS Directory Junction 或符號連結 (Symlink)。"""
    if hasattr(path, "is_junction") and path.is_junction():
        return True
    try:
        if path.is_symlink():
            return True
    except OSError:
        pass
    # Windows 降級檢驗：透過 os.readlink
    if hasattr(os, "readlink"):
        try:
            os.readlink(path)
            return True
        except (OSError, ValueError):
            pass
    return False


def remove_target(target: Path) -> None:
    """安全移除連接點或目錄。"""
    if is_junction_or_symlink(target):
        if sys.platform == "win32":
            # Windows 下 Junction 若用 rmtree 可能會誤刪來源內容，故透過 cmd /c rmdir 僅解綁連接點
            ret = subprocess.run(["cmd", "/c", "rmdir", str(target)], capture_output=True, text=True)
            if ret.returncode != 0:
                # 降級嘗試 unlink
                target.unlink()
        else:
            target.unlink()
    elif target.is_dir():
        shutil.rmtree(target)
    elif target.exists():
        target.unlink()


def create_link(source: Path, target: Path, force: bool = False) -> bool:
    """
    在目標路徑建立指向來源目錄的連接點或符號連結。
    - Windows: 優先使用 NTFS Directory Junction (mklink /J)，免管理員權限
    - Linux/macOS: 使用標準目錄符號連結 (os.symlink)
    """
    if not source.exists():
        print(f"[錯誤] 來源目錄不存在：{source}", file=sys.stderr)
        return False

    target_parent = target.parent
    target_parent.mkdir(parents=True, exist_ok=True)

    if target.exists() or is_junction_or_symlink(target):
        if is_junction_or_symlink(target):
            try:
                if target.resolve() == source.resolve():
                    print(f"[已存在] 連接點已正確建立：{target} -> {source}")
                    return True
            except OSError:
                pass

        if force:
            print(f"[強制重設] 移除既有目標：{target}")
            remove_target(target)
        else:
            print(
                f"[警告] 目標已存在且未指定 --force，跳過建立：{target}",
                file=sys.stderr,
            )
            return False

    # 建立連接點或符號連結
    if sys.platform == "win32":
        cmd = ["cmd", "/c", "mklink", "/J", str(target), str(source)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[成功] 建立 NTFS Directory Junction：{target} -> {source}")
            return True
        else:
            print(f"[警告] mklink /J 失敗（{res.stderr.strip()}），嘗試使用 os.symlink...", file=sys.stderr)
            try:
                os.symlink(source, target, target_is_directory=True)
                print(f"[成功] 建立符號連結：{target} -> {source}")
                return True
            except OSError as err:
                print(f"[錯誤] 無法建立符號連結：{err}", file=sys.stderr)
                return False
    else:
        try:
            os.symlink(source, target, target_is_directory=True)
            print(f"[成功] 建立目錄符號連結：{target} -> {source}")
            return True
        except OSError as err:
            print(f"[錯誤] 無法建立符號連結：{err}", file=sys.stderr)
            return False


def verify_links() -> bool:
    """驗證所有預期連接點是否正確指向 SKILLs/。"""
    all_ok = True
    print("[驗證] 開始檢驗技能目錄連接點狀態...")

    if not SOURCE_DIR.exists():
        print(f"[失敗] 來源目錄 SKILLs 不存在：{SOURCE_DIR}", file=sys.stderr)
        return False

    for target in TARGET_DIRS:
        if not target.exists() and not is_junction_or_symlink(target):
            print(f"[失敗] 目標連接點不存在：{target}", file=sys.stderr)
            all_ok = False
            continue

        if not is_junction_or_symlink(target):
            print(f"[失敗] 目標存在但不是連接點或符號連結（可能是實體目錄）：{target}", file=sys.stderr)
            all_ok = False
            continue

        try:
            resolved_target = target.resolve()
            resolved_source = SOURCE_DIR.resolve()
            if resolved_target != resolved_source:
                print(
                    f"[失敗] 連接點指向錯誤位置：{target} -> {resolved_target} (預期：{resolved_source})",
                    file=sys.stderr,
                )
                all_ok = False
                continue
        except OSError as err:
            print(f"[失敗] 解析連接點目標失敗：{err}", file=sys.stderr)
            all_ok = False
            continue

        print(f"[通過] {target} 正確鏈接至 {SOURCE_DIR}")

    return all_ok


def main() -> int:
    parser = argparse.ArgumentParser(
        description="跨平台設定 SKILLs 連接點 (.kiro/skills, .cline/skills)"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="僅驗證連接點有效性，不修改任何目錄",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="若目標已存在實體目錄或無效連結，強制清除並重建",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="移除已建立的連接點（不影響 SKILLs/ 來源）",
    )

    args = parser.parse_args()

    if args.verify_only:
        ok = verify_links()
        return 0 if ok else 1

    if args.remove:
        for target in TARGET_DIRS:
            if target.exists() or is_junction_or_symlink(target):
                print(f"[移除] 正在解除連接點：{target}")
                remove_target(target)
        return 0

    success = True
    for target in TARGET_DIRS:
        if not create_link(SOURCE_DIR, target, force=args.force):
            success = False

    if success:
        print("[完成] 所有技能目錄連接點設定完畢。")
        return 0
    else:
        print("[警告] 部分連接點建立失敗，請檢查錯誤訊息。", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
