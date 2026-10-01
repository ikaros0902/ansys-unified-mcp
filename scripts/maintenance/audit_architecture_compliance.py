# -*- coding: utf-8 -*-
"""
腳本名稱：audit_architecture_compliance.py
功能說明：林明志標準架構審查、Markdown 死鏈檢測、繁體中文註解合規性與 Python 示範腳本語法檢驗。
責任歸屬：Worker Sync M3 / Worker M4 Remediation
依據規範：PROJECT.md 與 ORIGINAL_REQUEST.md 之林明志標準架構規範。

檢查維度：
  1. 核心 SKILL.md 行數嚴格 <= 200 行
  2. reference/*.md 與 scripts/*.py 連結無死鏈
  3. 全繁體中文註解與手冊（ACT 巨集除外）
  4. Python 示範腳本 py_compile 編譯通過率 100% (Exit Code 0)
"""

import argparse
import os
import re
import sys
import py_compile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 強制標準輸出為 UTF-8 編碼
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# 專案根目錄解析（scripts/maintenance/ -> scripts/ -> repo root: parents[2]）
_project_root = Path(__file__).resolve().parents[2]
_skills_candidate = _project_root / "skills"
PROJECT_BASE = str(_skills_candidate if _skills_candidate.is_dir() else _project_root / "SKILLs")
GLOBAL_BASE = str(Path.home() / ".gemini" / "config" / "skills")


def discover_skills(skills_root: str) -> List[str]:
    """
    動態掃描指定根目錄下所有含 SKILL.md 的子目錄，作為受控技能清單。

    原實作為兩份硬編碼清單（CORE_SKILLS 8 項、ALL_CONTROLLED_SKILLS 12 項），
    導致新增技能不會被稽核涵蓋——act-extension-development 與
    pymechanical-operations 的路由表死鏈因此長期未被偵測。
    改為動態掃描後，skills/ 下任何技能一律納入稽核範圍。
    """
    discovered = []
    if not os.path.isdir(skills_root):
        return discovered
    for entry in sorted(os.listdir(skills_root)):
        entry_path = os.path.join(skills_root, entry)
        if not os.path.isdir(entry_path):
            continue
        if entry.startswith(".") or entry.startswith("__"):
            continue
        if os.path.isfile(os.path.join(entry_path, "SKILL.md")):
            discovered.append(entry)
    return discovered


# 受控技能清單一律由 skills/（唯一真實來源）動態掃描取得
ALL_CONTROLLED_SKILLS = discover_skills(PROJECT_BASE)
CORE_SKILLS = ALL_CONTROLLED_SKILLS

# 純簡體字清單
PURE_SIMPLIFIED = {
    '这': '這', '个': '個', '们': '們', '关': '關', '选': '選', '择': '擇',
    '点': '點', '计': '計', '设': '設', '数': '數', '据': '據', '网': '網',
    '参': '參', '应': '應', '变': '變', '动': '動', '学': '學', '统': '統',
    '标': '標', '准': '準', '规': '規', '范': '範', '执': '執', '结': '結',
    '发': '發', '导': '導', '优': '優', '简': '簡', '体': '體', '产': '產',
    '线': '線', '两': '兩', '还': '還', '没': '沒', '为': '為', '与': '與',
    '对': '對', '门': '門', '节': '節'
}


def audit_line_counts(
    base_dir: str,
    label: str,
    skills: Optional[List[str]] = None,
    allow_missing: bool = False,
) -> Tuple[bool, List[str]]:
    """審核核心 SKILL.md 行數 (門檻 <= 200 行)"""
    target_skills = skills if skills is not None else CORE_SKILLS
    logs = []
    all_pass = True

    logs.append(f"\n--- 1. 核心 SKILL.md 行數檢驗 [{label}] (門檻 <= 200 行) ---")
    if len(target_skills) == 0:
        logs.append("  [門禁阻斷 FAIL] 受控技能數量為 0，嚴禁空跑假陽性！")
        return False, logs

    for skill in target_skills:
        skill_file = os.path.join(base_dir, skill, "SKILL.md")
        if not os.path.exists(skill_file):
            if allow_missing:
                logs.append(f"  * {skill:<28}: [檔案不存在 - 警告略過] WARNING")
            else:
                logs.append(f"  * {skill:<28}: [檔案不存在] FAIL")
                all_pass = False
            continue
        with open(skill_file, "r", encoding="utf-8") as f:
            lines = len(f.readlines())
        is_ok = lines <= 200
        if not is_ok:
            all_pass = False
        status = "[PASS]" if is_ok else "[FAIL]"
        logs.append(f"  * {skill:<28}: {lines:>3} 行 {status}")
    return all_pass, logs


def audit_dead_links(
    base_dir: str,
    label: str,
    skills: Optional[List[str]] = None,
    min_links: int = 1,
) -> Tuple[bool, List[str]]:
    """審核 Markdown 檔案中之連結，檢測死鏈"""
    target_skills = skills if skills is not None else ALL_CONTROLLED_SKILLS
    logs = []
    all_pass = True
    dead_count = 0
    total_links = 0
    link_re = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    logs.append(f"\n--- 2. Markdown 超連結與路由表死鏈檢驗 [{label}] ---")
    if len(target_skills) == 0:
        logs.append("  [門禁阻斷 FAIL] 受控技能清單為空，嚴禁空跑假陽性！")
        return False, logs

    for skill in target_skills:
        skill_dir = os.path.join(base_dir, skill)
        if not os.path.exists(skill_dir):
            continue
        for root, dirs, files in os.walk(skill_dir):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                if not f.endswith(".md"):
                    continue
                fpath = os.path.join(root, f)
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                    content = fp.read()
                # 排除程式碼區塊避免代碼語法引發誤判
                no_code = re.sub(r'```[\s\S]*?```', '', content)
                for text, link in link_re.findall(no_code):
                    if link.startswith(("http:", "https:", "#", "mailto:")):
                        continue
                    clean_link = link.split("#")[0].split("?")[0]
                    if not clean_link:
                        continue
                    total_links += 1
                    target = os.path.normpath(os.path.join(root, clean_link))
                    if not os.path.exists(target):
                        dead_count += 1
                        all_pass = False
                        rel_src = os.path.relpath(fpath, base_dir)
                        logs.append(f"  [死鏈] 檔案: {rel_src} => 無效路徑: {link}")

    # 防空跑門禁：若受控技能存在但掃描連結數未達門檻，嚴禁通過
    if total_links < min_links:
        all_pass = False
        status_str = "[FAIL - 空跑門禁阻斷: 掃描連結數為 0]"
    else:
        status_str = "[PASS]" if dead_count == 0 else "[FAIL]"

    logs.append(f"  => 檢驗完成: 掃描 {total_links} 處連結，死鏈數: {dead_count} {status_str}")
    return all_pass, logs


def audit_traditional_chinese(
    base_dir: str,
    label: str,
    skills: Optional[List[str]] = None,
    min_files: int = 1,
) -> Tuple[bool, List[str]]:
    """審核所有受控檔案之中文語系，確保繁體中文"""
    target_skills = skills if skills is not None else ALL_CONTROLLED_SKILLS
    logs = []
    all_pass = True
    violations = 0
    total_files = 0

    logs.append(f"\n--- 3. 繁體中文語系與註解合規性檢驗 [{label}] ---")
    if len(target_skills) == 0:
        logs.append("  [門禁阻斷 FAIL] 受控技能清單為空，嚴禁空跑假陽性！")
        return False, logs

    for skill in target_skills:
        skill_dir = os.path.join(base_dir, skill)
        if not os.path.exists(skill_dir):
            continue
        for root, dirs, files in os.walk(skill_dir):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                if not (f.endswith(".md") or f.endswith(".py")):
                    continue
                total_files += 1
                fpath = os.path.join(root, f)
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                    content = fp.read()
                chars_found = [c for c in content if c in PURE_SIMPLIFIED]
                if chars_found:
                    violations += 1
                    all_pass = False
                    rel_src = os.path.relpath(fpath, base_dir)
                    unique_chars = sorted(set(chars_found))
                    logs.append(f"  [簡體字違規] {rel_src}: 包含 {unique_chars}")

    # 防空跑門禁：若受控技能存在但掃描檔案數未達門檻，嚴禁通過
    if total_files < min_files:
        all_pass = False
        status_str = "[FAIL - 空跑門禁阻斷: 掃描檔案數為 0]"
    else:
        status_str = "[PASS]" if violations == 0 else "[FAIL]"

    logs.append(f"  => 檢驗完成: 掃描 {total_files} 份檔案，簡體字違規檔案數: {violations} {status_str}")
    return all_pass, logs


def audit_python_compilation(
    base_dir: str,
    label: str,
    skills: Optional[List[str]] = None,
    min_scripts: int = 1,
) -> Tuple[bool, List[str]]:
    """檢驗所有 Python 示範腳本之語法正確性 (py_compile)"""
    target_skills = skills if skills is not None else ALL_CONTROLLED_SKILLS
    logs = []
    all_pass = True
    compiled = 0
    failed = 0

    logs.append(f"\n--- 4. Python 示範腳本 py_compile 語法檢驗 [{label}] ---")
    if len(target_skills) == 0:
        logs.append("  [門禁阻斷 FAIL] 受控技能清單為空，嚴禁空跑假陽性！")
        return False, logs

    scripts: List[str] = []
    for skill in target_skills:
        skill_dir = os.path.join(base_dir, skill)
        if not os.path.exists(skill_dir):
            continue
        for root, dirs, files in os.walk(skill_dir):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                if f.endswith(".py"):
                    scripts.append(os.path.join(root, f))

    # 防空跑門禁：若未掃描到示範腳本，嚴禁通過
    if len(scripts) < min_scripts:
        logs.append(f"  [門禁阻斷 FAIL] 掃描腳本數為 0（門檻 >= {min_scripts}），嚴禁空跑假陽性！")
        return False, logs

    for sc in sorted(scripts):
        rel_sc = os.path.relpath(sc, base_dir)
        try:
            py_compile.compile(sc, doraise=True)
            compiled += 1
            logs.append(f"  * {rel_sc:<50}: [PASS]")
        except Exception as e:
            failed += 1
            all_pass = False
            logs.append(f"  * [編譯失敗] {rel_sc}: {e}")

    status_str = "[PASS]" if failed == 0 else "[FAIL]"
    logs.append(f"  => 檢驗完成: 掃描 {len(scripts)} 份腳本，編譯通過: {compiled}，失敗: {failed} {status_str}")
    return all_pass, logs


def main():
    parser = argparse.ArgumentParser(
        description="PyAnsys 技能生態系林明志標準架構與語法全面審查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--project-only",
        action="store_true",
        default=False,
        help="僅審查專案端技能（預設行為，確保單元測試與本機開發環境穩定驗證）",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="check_all",
        help="強制同時完整審查專案端與全域端（兩端均須完全合規，若全域端缺失則 Exit 1）",
    )
    parser.add_argument(
        "--include-global",
        action="store_true",
        help="包含全域端審查（若全域端缺少特定技能則提示警告，不阻斷專案端通過）",
    )
    parser.add_argument(
        "--project-dir",
        default=PROJECT_BASE,
        help=f"指定專案端技能目錄 (預設: {PROJECT_BASE})",
    )
    parser.add_argument(
        "--global-dir",
        default=GLOBAL_BASE,
        help=f"指定全域端技能目錄 (預設: {GLOBAL_BASE})",
    )

    args = parser.parse_args()

    print("=" * 96)
    print("           PyAnsys 技能生態系林明志標準架構與語法全面審查報告")
    print("=" * 96)

    # 1. 專案端受控技能動態掃描與門禁檢查
    project_skills = discover_skills(args.project_dir)
    if len(project_skills) == 0:
        print(f"\n[致命門禁阻斷] 專案技能目錄 ({args.project_dir}) 下未探索到任何技能！")
        print("[門禁阻斷] 嚴禁空跑假陽性通過！(Exit code: 1)")
        sys.exit(1)

    # 2. 定義審查目標列表: (標籤, 目錄路徑, 是否允許缺失技能)
    targets = [
        ("專案端 (Project: SKILLs)", args.project_dir, False, 1),
    ]

    if args.check_all:
        targets.append(("全域端 (Global: config/skills)", args.global_dir, False, 1))
    elif args.include_global:
        targets.append(("全域端 (Global: config/skills, 寬容模式)", args.global_dir, True, 0))

    total_pass = True

    for label, base_path, allow_missing, min_count in targets:
        print(f"\n==================== 審查對象: {label} ====================")
        p1, l1 = audit_line_counts(base_path, label, project_skills, allow_missing=allow_missing)
        p2, l2 = audit_dead_links(base_path, label, project_skills, min_links=min_count)
        p3, l3 = audit_traditional_chinese(base_path, label, project_skills, min_files=min_count)
        p4, l4 = audit_python_compilation(base_path, label, project_skills, min_scripts=min_count)

        for line in l1 + l2 + l3 + l4:
            print(line)

        if not (p1 and p2 and p3 and p4):
            total_pass = False

    print("\n" + "=" * 96)
    if total_pass:
        print("[審查總結] 林明志架構審查四大指標 (行數 <= 200、無死鏈、繁體中文、py_compile 100%) 全數 PASS！")
        print("=" * 96)
        sys.exit(0)
    else:
        print("[審查總結] 存在未達標或違規項目，請檢閱上述明細！(FAIL)")
        print("=" * 96)
        sys.exit(1)


if __name__ == "__main__":
    main()
