#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腳本名稱：setup_skill_links.py
功能說明：跨平台三級自適應技能連結建立腳本。
          將次要 IDE 與代理目錄（.agents/skills, .cline/skills, .kiro/skills）
          連結至唯一真實來源（agents/skills/，SSOT）。

三級自適應策略：
  1. Linux / macOS (POSIX): 建立相對路徑之 POSIX Symlink
  2. Windows (NT, 同磁碟區): 優先建立無需管理員權限之 NTFS Directory Junction
  3. 跨磁碟區或權限不足 (WinError 1314): 降級為安全拷貝模式，並記錄 .sync_manifest.json (SHA-256)
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# 專案根目錄與唯一真實來源 (SSOT)
REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = REPO_ROOT / "agents" / "skills"

TARGET_REL_PATHS = [
    Path(".agents") / "skills",
    Path(".cline") / "skills",
    Path(".kiro") / "skills",
]


def compute_file_sha256(file_path: Path) -> str:
    """計算單一檔案之 SHA-256 雜湊值。"""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def generate_source_manifest(source_dir: Path) -> dict[str, str]:
    """遍歷來源目錄並產生相對路徑與 SHA-256 映射。"""
    manifest: dict[str, str] = {}
    for item in sorted(source_dir.rglob("*")):
        if item.is_file():
            rel = item.relative_to(source_dir).as_posix()
            manifest[rel] = compute_file_sha256(item)
    return manifest


def is_junction_or_symlink(path: Path) -> bool:
    """判斷指定路徑是否為 Directory Junction 或符號連結。"""
    if hasattr(path, "is_junction"):
        try:
            if path.is_junction():
                return True
        except OSError:
            pass
    try:
        if path.is_symlink():
            return True
    except OSError:
        pass
    if hasattr(os, "readlink"):
        try:
            os.readlink(path)
            return True
        except (OSError, ValueError):
            pass
    return False


def get_link_target(path: Path) -> Path | None:
    """取得連結指向的目標路徑（若為連結）。"""
    if not is_junction_or_symlink(path):
        return None
    try:
        return path.resolve()
    except OSError:
        return None


def safe_remove_target(target: Path) -> None:
    """安全解除/移除目標連結或目錄，嚴格不傷及來源目錄內容。"""
    if is_junction_or_symlink(target):
        try:
            target.unlink()
            return
        except OSError:
            pass
        if sys.platform == "win32":
            subprocess.run(["cmd", "/c", "rmdir", str(target)], capture_output=True, text=True)
            return
    if target.is_dir():
        shutil.rmtree(target)
    elif target.exists():
        target.unlink()


def create_safe_copy_fallback(source: Path, target: Path) -> tuple[bool, str]:
    """
    策略 3：安全拷貝模式並寫入 .sync_manifest.json。
    當 Junction / Symlink 均不可行時使用。
    """
    print(f"  [降級] 啟動安全拷貝模式：{target} <- {source}")
    target_parent = target.parent
    target_parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        safe_remove_target(target)

    # 執行目錄樹拷貝
    shutil.copytree(source, target, dirs_exist_ok=True)

    # 計算並寫入同步清單
    manifest_hashes = generate_source_manifest(source)
    manifest_data = {
        "synced_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": str(source.resolve().as_posix()),
        "target": str(target.resolve().as_posix()),
        "strategy": "safe_copy",
        "file_count": len(manifest_hashes),
        "hashes": manifest_hashes,
    }
    manifest_file = target / ".sync_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    return True, f"安全拷貝模式 (.sync_manifest.json 包含 {len(manifest_hashes)} 檔)"


def create_adaptive_skill_link(source: Path, target: Path, force: bool = False) -> tuple[bool, str]:
    """
    三級自適應技能連結建立核心邏輯：
      1. POSIX: 相對路徑符號連結
      2. Windows NT: 同磁碟區 NTFS Directory Junction
      3. 降級: 安全拷貝 + .sync_manifest.json (SHA-256)
    """
    if not source.exists():
        return False, f"來源目錄不存在：{source}"

    target_parent = target.parent
    target_parent.mkdir(parents=True, exist_ok=True)

    # 若目標已存在
    if target.exists() or is_junction_or_symlink(target):
        if is_junction_or_symlink(target):
            existing_target = get_link_target(target)
            if existing_target and existing_target == source.resolve():
                if not force:
                    return True, "已正確連結至真實來源（跳過重建）"
            print(f"  [重設] 目標連結已存在或需更新：{target}")
            safe_remove_target(target)
        elif target.is_dir():
            # 檢查是否為先前安全拷貝模式所留下的目錄
            manifest_file = target / ".sync_manifest.json"
            if manifest_file.exists() and not force:
                return True, "已存在安全拷貝副本且清單完整（跳過重設）"
            if force:
                print(f"  [強制覆寫] 清除既有實體目錄：{target}")
                safe_remove_target(target)
            else:
                return False, f"目標已存在實體目錄且非連結：{target}，請帶 --force 覆寫"
        else:
            safe_remove_target(target)

    # 策略 1：POSIX 系統 (Linux / macOS)
    if os.name == "posix":
        try:
            rel_source = os.path.relpath(source, target.parent)
            target.symlink_to(rel_source, target_is_directory=True)
            return True, f"POSIX 相對符號連結 ({rel_source})"
        except OSError as e:
            print(f"  [警告] POSIX 符號連結建立失敗 ({e})，降級至安全拷貝", file=sys.stderr)
            return create_safe_copy_fallback(source, target)

    # 策略 2：Windows 系統 (NT)
    if os.name == "nt":
        src_resolved = source.resolve()
        tgt_parent_resolved = target.parent.resolve()

        # 檢查是否為同一磁碟區 (NTFS Directory Junction 必須在同一 Volume)
        same_drive = src_resolved.drive.upper() == tgt_parent_resolved.drive.upper()
        if same_drive:
            # 優先嘗試內建 _winapi.CreateJunction (免子行程開銷)
            try:
                import _winapi

                _winapi.CreateJunction(str(src_resolved), str(target.resolve()))
                return True, "NTFS Directory Junction (_winapi)"
            except (AttributeError, OSError, ImportError):
                pass

            # 備選：呼叫系統 cmd /c mklink /J
            res = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(target.resolve()), str(src_resolved)],
                capture_output=True,
                text=True,
            )
            if res.returncode == 0:
                return True, "NTFS Directory Junction (cmd mklink /J)"
            print(f"  [警告] mklink /J 失敗：{res.stderr.strip()}", file=sys.stderr)

        # 若跨磁碟區或 Junction 失敗，嘗試 Windows 符號連結
        try:
            target.symlink_to(src_resolved, target_is_directory=True)
            return True, "Windows 符號連結 (Symlink)"
        except OSError as e:
            # 常見 WinError 1314: 用戶端沒有具備所需的權限
            win_err = getattr(e, "winerror", None)
            print(
                f"  [警告] Windows 符號連結權限不足或不支援 (WinError: {win_err})，降級至安全拷貝模式",
                file=sys.stderr,
            )

        # 策略 3：安全拷貝模式降級
        return create_safe_copy_fallback(source, target)

    # 其他未知 OS 降級
    return create_safe_copy_fallback(source, target)


def verify_all_links() -> bool:
    """驗證所有預期連結與拷貝狀態。"""
    print("=" * 60)
    print("【驗證】開始檢驗技能連結完整性與指向")
    print(f"真實來源 (SSOT)：{SOURCE_DIR.resolve()}")
    print("=" * 60)

    if not SOURCE_DIR.is_dir():
        print(f"[錯誤] 真實來源目錄不存在：{SOURCE_DIR}", file=sys.stderr)
        return False

    all_passed = True
    for rel_target in TARGET_REL_PATHS:
        target = REPO_ROOT / rel_target
        if not target.exists() and not is_junction_or_symlink(target):
            print(f"  [X] {rel_target} 不存在")
            all_passed = False
            continue

        if is_junction_or_symlink(target):
            resolved = get_link_target(target)
            if resolved == SOURCE_DIR.resolve():
                print(f"  [V] {rel_target} -> 正確指向 SSOT (Junction/Symlink)")
            else:
                print(f"  [X] {rel_target} -> 指向錯誤目標：{resolved}")
                all_passed = False
        elif target.is_dir():
            manifest_file = target / ".sync_manifest.json"
            if manifest_file.exists():
                print(f"  [V] {rel_target} -> 安全拷貝副本（附帶同步清單）")
            else:
                print(f"  [?] {rel_target} -> 獨立實體目錄（無清單，建議透過 --force 統一）")
        else:
            print(f"  [X] {rel_target} -> 未知實體檔案")
            all_passed = False

    return all_passed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="跨平台三級自適應技能目錄連結工具 (SSOT -> .agents/.cline/.kiro)"
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="強制清除既有目標目錄或舊連結並重新建立",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="僅驗證連結狀態，不執行建立或修改",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="安全移除各 IDE / 工具目錄之技能連結（絕不傷及 agents/skills）",
    )

    args = parser.parse_args()

    if args.verify:
        success = verify_all_links()
        return 0 if success else 1

    if args.remove:
        print("[移除] 正在安全解除各次要目錄之技能連結...")
        for rel_target in TARGET_REL_PATHS:
            target = REPO_ROOT / rel_target
            if target.exists() or is_junction_or_symlink(target):
                safe_remove_target(target)
                print(f"  [已移除] {rel_target}")
        print("[完成] 連結解除完畢。")
        return 0

    print("=" * 60)
    print("【執行】建立跨平台技能三級自適應連結")
    print(f"真實來源 (SSOT)：{SOURCE_DIR.resolve()}")
    print("=" * 60)

    overall_success = True
    for rel_target in TARGET_REL_PATHS:
        target = REPO_ROOT / rel_target
        ok, msg = create_adaptive_skill_link(SOURCE_DIR, target, force=args.force)
        status_tag = "[成功]" if ok else "[失敗]"
        print(f"{status_tag} {rel_target} => {msg}")
        if not ok:
            overall_success = False

    print("-" * 60)
    if overall_success:
        print("[全部完成] 所有技能目錄連結設定完畢，驗證結果：")
        verify_all_links()
        return 0
    else:
        print("[警告] 部分技能目錄連結建立失敗，請檢閱上方日誌。", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
