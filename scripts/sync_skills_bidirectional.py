# -*- coding: utf-8 -*-
"""
腳本名稱：sync_skills_bidirectional.py
功能說明：專案目錄 (SKILLs) 與全域目錄 (skills) 雙向鏡像同步與 SHA-256 完整性驗證工具。
責任歸屬：Worker Sync M3
依據規範：林明志標準架構與雙軌制註解規範。

受控技能清單：
  1. ansys-fluent
  2. ansys-mechanical
  3. ansys-lsdyna
  4. ansys-optislang
  5. ansys-geometry-modeling
  6. ansys-spaceclaim-modeling
  7. ansys-parametric-study
  8. ansys-submodeling-dpf
  9. pcb-warpage-analysis
  10. ansys-mechanical-multiphysics
  11. ansys-lsdyna-explicit
  12. ansys-optislang-optimization
"""

import argparse
import hashlib
import os
import shutil
import sys
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

# 強制標準輸出為 UTF-8 編碼
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# 預設受控技能目錄清單
CONTROLLED_SKILLS = [
    "ansys-fluent",
    "ansys-mechanical",
    "ansys-lsdyna",
    "ansys-optislang",
    "ansys-geometry-modeling",
    "ansys-spaceclaim-modeling",
    "ansys-parametric-study",
    "ansys-submodeling-dpf",
    "pcb-warpage-analysis",
    "ansys-mechanical-multiphysics",
    "ansys-lsdyna-explicit",
    "ansys-optislang-optimization",
]

# 忽略同步之目錄與副檔名
IGNORED_DIRS = {"__pycache__", ".git", ".idea", ".vscode"}
IGNORED_EXTS = {".pyc", ".pyo", ".pyd", ".tmp"}


def calculate_sha256(filepath: str) -> str:
    """計算指定檔案之 SHA-256 雜湊值"""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def scan_skill_files(skill_dir: str) -> Dict[str, Dict[str, any]]:
    """
    掃描單一技能目錄下所有受控檔案
    回傳字典結構：{相對路徑: {'abs_path': 絕對路徑, 'sha256': 雜湊值, 'mtime': 修改時間戳, 'size': 檔案大小}}
    """
    files_map = {}
    if not os.path.exists(skill_dir):
        return files_map

    for root, dirs, files in os.walk(skill_dir):
        # 原地過濾忽略目錄
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for f in files:
            _, ext = os.path.splitext(f)
            if ext.lower() in IGNORED_EXTS:
                continue
            abs_path = os.path.join(root, f)
            rel_path = os.path.relpath(abs_path, skill_dir)
            # 正規化路徑分隔符號為正斜線以利跨平台比對
            norm_rel = rel_path.replace("\\", "/")
            try:
                stat = os.stat(abs_path)
                sha = calculate_sha256(abs_path)
                files_map[norm_rel] = {
                    "abs_path": abs_path,
                    "sha256": sha,
                    "mtime": stat.st_mtime,
                    "size": stat.st_size,
                }
            except Exception as err:
                print(f"[警告] 讀取檔案失敗: {abs_path} - {err}", file=sys.stderr)
    return files_map


class BidirectionalSyncEngine:
    """雙向鏡像同步與雜湊驗證引擎"""

    def __init__(
        self,
        project_base: str,
        global_base: str,
        controlled_skills: Optional[List[str]] = None,
        dry_run: bool = False,
    ):
        self.project_base = os.path.abspath(project_base)
        self.global_base = os.path.abspath(global_base)
        self.controlled_skills = controlled_skills or CONTROLLED_SKILLS
        self.dry_run = dry_run
        self.action_logs: List[str] = []

    def log(self, message: str) -> None:
        """記錄操作歷程"""
        prefix = "[DRY-RUN] " if self.dry_run else ""
        print(f"{prefix}{message}")
        self.action_logs.append(f"{prefix}{message}")

    def copy_file(self, src_path: str, dst_path: str) -> None:
        """複製單一檔案並保留時間戳"""
        dst_dir = os.path.dirname(dst_path)
        if not self.dry_run:
            os.makedirs(dst_dir, exist_ok=True)
            shutil.copy2(src_path, dst_path)
        self.log(f"  -> 複製檔案: {src_path} => {dst_path}")

    def remove_file(self, file_path: str) -> None:
        """刪除檔案"""
        if not self.dry_run:
            if os.path.exists(file_path):
                os.remove(file_path)
        self.log(f"  -> 移除孤立過時檔案: {file_path}")

    def clean_empty_dirs(self, root_dir: str) -> None:
        """遞迴清理空目錄"""
        if not os.path.exists(root_dir) or self.dry_run:
            return
        for root, dirs, _ in os.walk(root_dir, topdown=False):
            for d in dirs:
                dir_path = os.path.join(root, d)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                except Exception:
                    pass

    def sync_skill(self, skill_name: str) -> None:
        """針對單一技能執行雙向鏡像同步策略"""
        p_dir = os.path.join(self.project_base, skill_name)
        g_dir = os.path.join(self.global_base, skill_name)

        p_files = scan_skill_files(p_dir)
        g_files = scan_skill_files(g_dir)

        self.log(f"=== 同步技能: {skill_name} (專案檔案: {len(p_files)}, 全域檔案: {len(g_files)}) ===")

        # 情境 A: 專案端為唯一來源 (如 M1 新建之 ansys-fluent)
        if p_files and not g_files:
            self.log(f"[*] 技能 {skill_name} 僅存在於專案端，執行 專案端 => 全域端 完整鏡像建立")
            for rel, meta in p_files.items():
                dst = os.path.join(g_dir, rel.replace("/", os.sep))
                self.copy_file(meta["abs_path"], dst)
            return

        # 情境 B: 全域端為唯一來源
        if g_files and not p_files:
            self.log(f"[*] 技能 {skill_name} 僅存在於全域端，執行 全域端 => 專案端 完整鏡像建立")
            for rel, meta in g_files.items():
                dst = os.path.join(p_dir, rel.replace("/", os.sep))
                self.copy_file(meta["abs_path"], dst)
            return

        # 情境 C: 兩端皆存在，需依據主控規則與時間戳比對
        all_rels: Set[str] = set(p_files.keys()) | set(g_files.keys())

        # 針對 lsdyna 與 optislang，全域端為林明志標準 6 本子手冊架構來源，專案端多餘的歷史舊手冊應清理
        prune_project_orphans = skill_name in {"ansys-lsdyna", "ansys-optislang"}

        for rel in sorted(all_rels):
            p_meta = p_files.get(rel)
            g_meta = g_files.get(rel)

            # 1. 兩端皆存在
            if p_meta and g_meta:
                if p_meta["sha256"] == g_meta["sha256"]:
                    # 雜湊值一致，無需操作
                    continue
                else:
                    # 雜湊值不一致，依據修改時間戳由較新者覆蓋較舊者
                    # 註：M2 更新集中在全域端，故全域端通常較新
                    if g_meta["mtime"] > p_meta["mtime"]:
                        self.log(f"[*] 檔案 {rel} 全域端較新，執行 全域 => 專案 同步")
                        self.copy_file(g_meta["abs_path"], p_meta["abs_path"])
                    else:
                        self.log(f"[*] 檔案 {rel} 專案端較新，執行 專案 => 全域 同步")
                        self.copy_file(p_meta["abs_path"], g_meta["abs_path"])

            # 2. 僅存在於專案端
            elif p_meta and not g_meta:
                if prune_project_orphans:
                    # 清理孤立舊版手冊或腳本
                    self.remove_file(p_meta["abs_path"])
                else:
                    # 其他技能（如 pcb-warpage-analysis 的 scripts）則同步至全域端
                    dst = os.path.join(g_dir, rel.replace("/", os.sep))
                    self.log(f"[*] 檔案 {rel} 僅存在於專案端，同步至全域端")
                    self.copy_file(p_meta["abs_path"], dst)

            # 3. 僅存在於全域端
            elif g_meta and not p_meta:
                # 全域端新增檔案同步回專案端
                dst = os.path.join(p_dir, rel.replace("/", os.sep))
                self.log(f"[*] 檔案 {rel} 僅存在於全域端，同步至專案端")
                self.copy_file(g_meta["abs_path"], dst)

        # 清理可能產生的空目錄
        self.clean_empty_dirs(p_dir)
        self.clean_empty_dirs(g_dir)

    def run_sync(self) -> None:
        """執行所有受控技能之雙向鏡像同步"""
        self.log("=" * 80)
        self.log(f"啟動 PyAnsys 技能生態系雙向鏡像同步作業: {datetime.now().isoformat()}")
        self.log(f"專案路徑: {self.project_base}")
        self.log(f"全域路徑: {self.global_base}")
        self.log("=" * 80)

        for skill in self.controlled_skills:
            self.sync_skill(skill)

        self.log("=" * 80)
        self.log("雙向鏡像同步作業執行完畢！")
        self.log("=" * 80)

    def verify_integrity(self) -> Tuple[bool, List[Dict[str, any]]]:
        """
        嚴格驗證兩端所有受控技能檔案之 SHA-256 吻合率
        回傳：(是否100%全數通過, 統計報告清單)
        """
        report_list = []
        overall_pass = True

        for skill in self.controlled_skills:
            p_dir = os.path.join(self.project_base, skill)
            g_dir = os.path.join(self.global_base, skill)

            p_files = scan_skill_files(p_dir)
            g_files = scan_skill_files(g_dir)

            all_rels = sorted(set(p_files.keys()) | set(g_files.keys()))
            match_count = 0
            diff_hash_count = 0
            only_p_count = 0
            only_g_count = 0

            diff_details = []

            for rel in all_rels:
                p_meta = p_files.get(rel)
                g_meta = g_files.get(rel)

                if p_meta and g_meta:
                    if p_meta["sha256"] == g_meta["sha256"]:
                        match_count += 1
                    else:
                        diff_hash_count += 1
                        diff_details.append(f"[雜湊不符] {rel} (專案: {p_meta['sha256'][:8]} vs 全域: {g_meta['sha256'][:8]})")
                elif p_meta:
                    only_p_count += 1
                    diff_details.append(f"[僅專案端] {rel}")
                else:
                    only_g_count += 1
                    diff_details.append(f"[僅全域端] {rel}")

            total_files = len(all_rels)
            is_skill_pass = (diff_hash_count == 0 and only_p_count == 0 and only_g_count == 0 and total_files > 0)
            if not is_skill_pass:
                overall_pass = False

            report_list.append({
                "skill": skill,
                "total_files": total_files,
                "match_count": match_count,
                "diff_hash": diff_hash_count,
                "only_project": only_p_count,
                "only_global": only_g_count,
                "is_pass": is_skill_pass,
                "diff_details": diff_details,
            })

        return overall_pass, report_list


def print_verification_report(report_list: List[Dict[str, any]]) -> None:
    """輸出高資訊密度 ASCII 驗證報告表格"""
    print("\n" + "=" * 96)
    print("                 PyAnsys 技能兩端 SHA-256 完整性與同步狀態綜合驗證表")
    print("=" * 96)
    header = f"{'#':<3} | {'技能名稱 (Skill Name)':<30} | {'檔案數':<6} | {'吻合':<6} | {'雜湊差':<6} | {'專案獨有':<8} | {'全域獨有':<8} | {'狀態'}"
    print(header)
    print("-" * 96)

    total_files_sum = 0
    total_match_sum = 0
    total_diff_sum = 0
    total_only_p_sum = 0
    total_only_g_sum = 0

    for idx, item in enumerate(report_list, start=1):
        status_str = "[PASS]" if item["is_pass"] else "[FAIL]"
        total_files_sum += item["total_files"]
        total_match_sum += item["match_count"]
        total_diff_sum += item["diff_hash"]
        total_only_p_sum += item["only_project"]
        total_only_g_sum += item["only_global"]

        line = (
            f"{idx:<3} | {item['skill']:<30} | {item['total_files']:<6} | {item['match_count']:<6} | "
            f"{item['diff_hash']:<6} | {item['only_project']:<8} | {item['only_global']:<8} | {status_str}"
        )
        print(line)
        if item["diff_details"]:
            for d in item["diff_details"]:
                print(f"      * 異常細節: {d}")

    print("-" * 96)
    total_diffs = total_diff_sum + total_only_p_sum + total_only_g_sum
    summary_line = (
        f"{'總計':<3} | {'全部受控技能 (' + str(len(report_list)) + ' 項)':<30} | {total_files_sum:<6} | {total_match_sum:<6} | "
        f"{total_diff_sum:<6} | {total_only_p_sum:<8} | {total_only_g_sum:<8} | "
        f"{'[PASS]' if total_diffs == 0 else '[FAIL]'}"
    )
    print(summary_line)
    print("=" * 96)
    print(f"[統計] 總受控檔案數: {total_files_sum}, 100% 吻合數: {total_match_sum}, 總差異數: {total_diffs}")
    if total_diffs == 0:
        print("[結論] 兩端所有受控技能檔案 SHA-256 100% 完全一致，差異數精確為 0！(PASS)\n")
    else:
        print(f"[警告] 檢測到 {total_diffs} 處不一致，請檢閱上述明細！(FAIL)\n")


def main():
    parser = argparse.ArgumentParser(
        description="PyAnsys 技能生態系雙向鏡像同步與 SHA-256 驗證工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--project-dir",
        default=r"F:\Ming_python\ansys-unified-mcp\SKILLs",
        help=r"專案技能根目錄 (預設: F:\Ming_python\ansys-unified-mcp\SKILLs)",
    )
    parser.add_argument(
        "--global-dir",
        default=r"C:\Users\Ming\.gemini\config\skills",
        help=r"全域技能根目錄 (預設: C:\Users\Ming\.gemini\config\skills)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="僅模擬執行，不實體寫入或刪除檔案",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="僅執行 SHA-256 完整性核驗，不執行同步",
    )
    parser.add_argument(
        "--skills",
        nargs="+",
        help="指定僅同步/驗證之特定技能名稱 (預設: 全數受控 12 項技能)",
    )

    args = parser.parse_args()

    skills_to_process = args.skills if args.skills else CONTROLLED_SKILLS

    engine = BidirectionalSyncEngine(
        project_base=args.project_dir,
        global_base=args.global_dir,
        controlled_skills=skills_to_process,
        dry_run=args.dry_run,
    )

    if not args.verify_only:
        engine.run_sync()

    # 執行嚴格驗證
    all_pass, report = engine.verify_integrity()
    print_verification_report(report)

    if not all_pass:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
