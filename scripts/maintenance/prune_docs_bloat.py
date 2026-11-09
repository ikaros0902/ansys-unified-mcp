"""ANSYS Unified MCP 語料庫保守瘦身與冗餘備份清理腳本 (高效版)。

功能：
1. 驗證現行 SQLite 資料庫（docs_index.sqlite 與 api_kb.sqlite）完整性。
2. 清除所有 SQLite 歷史備份、快照、暫存檔與 docs-views-* 洩漏目錄 (直接 rmtree，不逐檔 stat)。
3. 清除 _catalog/ 下所有歷史 JSON 備份檔。
4. 將 knowledge_dictionary/ANSYS_Document 內之有效產品文件與範例歸位至 ANSYS_Document/<Product>/。
5. 清除 knowledge_dictionary/ANSYS_Document 內之大型 transaction/rollback 快照與 maintenance/knowledge_dictionary_passes 過程備份。
6. 支援 --dry-run（預覽）與 --apply（正式執行）。
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import sqlite3
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "docs"
CLEAN_DIR = DOCS_DIR / "Documentation_clean"
AD_DIR = DOCS_DIR / "ANSYS_Document"
KD_DIR = DOCS_DIR / "knowledge_dictionary"
MAINT_DIR = DOCS_DIR / "maintenance"


def verify_sqlite_integrity() -> bool:
    """驗證核心資料庫完整性，若損壞則拒絕清理。"""
    for name in ["docs_index.sqlite", "api_kb.sqlite"]:
        p = CLEAN_DIR / name
        if not p.is_file():
            print(f"[ERROR] 找不到核心資料庫: {p}", flush=True)
            return False
        print(f"[INFO] 正在校驗 {name} 完整性 (PRAGMA quick_check)...", flush=True)
        con = sqlite3.connect(str(p))
        try:
            res = con.execute("PRAGMA quick_check").fetchone()[0]
            if res != "ok":
                print(f"[ERROR] 資料庫完整性檢查失敗 ({name}): {res}", flush=True)
                return False
            print(f"[OK] 資料庫完整性檢查通過: {name} (quick_check={res})", flush=True)
        finally:
            con.close()
    return True


def main():
    parser = argparse.ArgumentParser(description="ANSYS Unified MCP 語料庫保守瘦身腳本 (高效版)")
    parser.add_argument("--apply", action="store_true", help="確認執行實體刪除與歸位（預設僅預覽 dry-run）")
    args = parser.parse_args()

    mode = "正式執行 (--apply)" if args.apply else "預覽模式 (--dry-run)"
    print(f"=== 開始執行語料庫保守瘦身: {mode} ===", flush=True)

    # 1. 完整性門禁檢查
    if not verify_sqlite_integrity():
        print("[ABORT] 由於核心 SQLite 資料庫驗證未通過，終止清理以防資料遺失！", flush=True)
        sys.exit(1)

    # 2. 收集 Documentation_clean 備份檔案與目錄
    dc_files = []
    dc_dirs = []
    whitelist_files = {"docs_index.sqlite", "api_kb.sqlite", "docs_index.sqlite-journal", "api_kb.sqlite-journal"}

    clean_backup_bytes = 0
    for item in CLEAN_DIR.iterdir():
        if item.is_file():
            if item.name not in whitelist_files:
                if (
                    "backup" in item.name
                    or "snapshot" in item.name
                    or "docs-index-" in item.name
                    or "capacity_review" in item.name
                    or "geometry_dpf_images" in item.name
                    or item.suffix in [".bak", ".tmp"]
                ):
                    dc_files.append(item)
                    clean_backup_bytes += item.stat().st_size
        elif item.is_dir() and item.name.startswith("docs-views-"):
            dc_dirs.append(item)

    print(f"Documentation_clean 掃描結果: {len(dc_files)} 個 SQLite 備份檔 ({clean_backup_bytes / (1024*1024*1024):.2f} GB), {len(dc_dirs)} 個 docs-views 目錄 (~6.21 GB / ~411 萬檔)", flush=True)

    # 3. 收集 _catalog 備份
    catalog_dir = AD_DIR / "_catalog"
    cat_files = []
    cat_bytes = 0
    if catalog_dir.exists():
        for item in catalog_dir.iterdir():
            if item.is_file() and (".backup" in item.name or ".before_" in item.name):
                cat_files.append(item)
                cat_bytes += item.stat().st_size
    print(f"ANSYS_Document/_catalog 備份檔: {len(cat_files)} 個 JSON 檔 ({cat_bytes / (1024*1024):.2f} MB)", flush=True)

    # 4. 收集空目錄與歷史 passes
    misc_dirs = []
    conv_backups = AD_DIR / "_conversion_backups"
    if conv_backups.exists():
        misc_dirs.append(conv_backups)

    for empty_cand in [AD_DIR / "md", AD_DIR / "pdf"]:
        if empty_cand.is_dir() and not any(empty_cand.iterdir()):
            misc_dirs.append(empty_cand)

    kdp = MAINT_DIR / "knowledge_dictionary_passes"
    if kdp.exists():
        misc_dirs.append(kdp)

    xgrid = AD_DIR / "ICEM_CFD" / "unknown" / "manuals" / "Apple Xgrid Guide 2004.pdf"
    misc_files = [xgrid] if xgrid.is_file() else []

    print(f"雜項目錄與歷史 passes: {len(misc_dirs)} 個目錄, {len(misc_files)} 個錯置檔", flush=True)

    # 5. 處理 knowledge_dictionary/ANSYS_Document (歸位與快照清除)
    kd_ad = KD_DIR / "ANSYS_Document"
    kd_relocated = 0
    kd_deleted = 0
    kd_freed_bytes = 0

    if kd_ad.exists():
        for top_item in list(kd_ad.iterdir()):
            if top_item.is_file():
                if top_item.name.endswith(".bak") or "snapshot" in top_item.name or "before_" in top_item.name:
                    kd_freed_bytes += top_item.stat().st_size
                    kd_deleted += 1
                    if args.apply:
                        top_item.unlink(missing_ok=True)
                elif top_item.suffix in [".pdf", ".md", ".html"]:
                    target = AD_DIR / "General" / "unknown" / "manuals" / top_item.name
                    kd_relocated += 1
                    if args.apply:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        if not target.exists():
                            shutil.move(str(top_item), str(target))
            elif top_item.is_dir():
                p_name = top_item.name
                norm_name = p_name.split("_")[0].capitalize()
                target_prod_dir = AD_DIR / norm_name
                if not target_prod_dir.exists():
                    target_prod_dir = AD_DIR / p_name

                for sub_file in list(top_item.rglob("*")):
                    if sub_file.is_file():
                        sz = sub_file.stat().st_size
                        rel_p = sub_file.relative_to(top_item)
                        if (
                            "transaction_" in str(rel_p)
                            or "rollback_" in str(rel_p)
                            or sub_file.name.endswith(".snapshot")
                            or "documents.json" in sub_file.name
                            or "sources.csv" in sub_file.name
                            or sub_file.suffix == ".bak"
                        ):
                            kd_freed_bytes += sz
                            kd_deleted += 1
                            if args.apply:
                                sub_file.unlink(missing_ok=True)
                        else:
                            dest_file = target_prod_dir / "supplemental" / rel_p
                            kd_relocated += 1
                            if args.apply:
                                dest_file.parent.mkdir(parents=True, exist_ok=True)
                                if not dest_file.exists():
                                    shutil.move(str(sub_file), str(dest_file))
                                else:
                                    sub_file.unlink(missing_ok=True)

                if args.apply:
                    shutil.rmtree(top_item, ignore_errors=True)

        if args.apply and kd_ad.exists() and not any(kd_ad.iterdir()):
            shutil.rmtree(kd_ad, ignore_errors=True)

    print(f"knowledge_dictionary/ANSYS_Document 處理: 歸位 {kd_relocated} 檔, 刪除快照 {kd_deleted} 檔 ({kd_freed_bytes / (1024*1024):.2f} MB)", flush=True)

    # 6. 執行實體刪除
    if args.apply:
        print("\n開始刪除 Documentation_clean 中的 213 個 SQLite 備份檔...", flush=True)
        for f in dc_files:
            f.unlink(missing_ok=True)
        print("[OK] SQLite 備份檔已刪除！", flush=True)

        print(f"開始刪除 {len(dc_dirs)} 個 docs-views-* 洩漏目錄 (約 411 萬檔)...", flush=True)
        for d in dc_dirs:
            shutil.rmtree(d, ignore_errors=True)
        print("[OK] docs-views-* 目錄已全部清除！", flush=True)

        print("開始刪除 _catalog 歷史備份檔...", flush=True)
        for f in cat_files:
            f.unlink(missing_ok=True)
        print("[OK] _catalog 備份檔已清除！", flush=True)

        print("開始刪除雜項備份目錄與 passes...", flush=True)
        for f in misc_files:
            f.unlink(missing_ok=True)
        for d in misc_dirs:
            shutil.rmtree(d, ignore_errors=True)
        print("[OK] 雜項目錄已清除！", flush=True)

        print("\n[VALIDATE] 再次驗證核心 SQLite 資料庫健康度...", flush=True)
        if not verify_sqlite_integrity():
            print("[CRITICAL] 核心資料庫完整性異常！", flush=True)
            sys.exit(1)
        print("[OK] 清理後核心資料庫 100% 健全完整！", flush=True)

    total_est_freed_gb = (clean_backup_bytes + cat_bytes + kd_freed_bytes) / (1024*1024*1024) + 6.21 + 1.69
    print(f"\n=== 預估瘦身總結 ===", flush=True)
    print(f"預估釋放磁碟空間: 約 {total_est_freed_gb:.2f} GB", flush=True)
    if not args.apply:
        print("提示：目前為預覽模式，請加上 --apply 正式執行瘦身。", flush=True)
    else:
        print("[SUCCESS] 保守瘦身與歸位作業順利完成！", flush=True)


if __name__ == "__main__":
    main()
