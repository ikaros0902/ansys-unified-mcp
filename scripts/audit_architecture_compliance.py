# -*- coding: utf-8 -*-
"""
腳本名稱：audit_architecture_compliance.py
功能說明：林明志標準架構審查、Markdown 死鏈檢測、繁體中文註解合規性與 Python 示範腳本語法檢驗。
責任歸屬：Worker Sync M3
依據規範：PROJECT.md 與 ORIGINAL_REQUEST.md 之林明志標準架構規範。

檢查維度：
  1. 核心 SKILL.md 行數嚴格 <= 200 行
  2. reference/*.md 與 scripts/*.py 連結無死鏈
  3. 全繁體中文註解與手冊（ACT 巨集除外）
  4. Python 示範腳本 py_compile 編譯通過率 100% (Exit Code 0)
"""

import os
import re
import sys
import py_compile
from typing import Dict, List, Tuple

# 強制標準輸出為 UTF-8 編碼
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_BASE = r"F:\Ming_python\ansys-unified-mcp\SKILLs"
GLOBAL_BASE = r"C:\Users\Ming\.gemini\config\skills"

CORE_SKILLS = [
    "ansys-fluent",
    "ansys-mechanical",
    "ansys-lsdyna",
    "ansys-optislang",
    "ansys-geometry-modeling",
    "ansys-spaceclaim-modeling",
    "ansys-parametric-study",
    "pcb-warpage-analysis",
]

ALL_CONTROLLED_SKILLS = [
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


def audit_line_counts(base_dir: str, label: str) -> Tuple[bool, List[str]]:
    """審核核心 SKILL.md 行數 (門檻 <= 200 行)"""
    logs = []
    all_pass = True
    logs.append(f"\n--- 1. 核心 SKILL.md 行數檢驗 [{label}] (門檻 <= 200 行) ---")
    for skill in CORE_SKILLS:
        skill_file = os.path.join(base_dir, skill, "SKILL.md")
        if not os.path.exists(skill_file):
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


def audit_dead_links(base_dir: str, label: str) -> Tuple[bool, List[str]]:
    """審核 Markdown 檔案中之連結，檢測死鏈"""
    logs = []
    all_pass = True
    dead_count = 0
    total_links = 0
    link_re = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    logs.append(f"\n--- 2. Markdown 超連結與路由表死鏈檢驗 [{label}] ---")
    for skill in ALL_CONTROLLED_SKILLS:
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

    status_str = "[PASS]" if dead_count == 0 else "[FAIL]"
    logs.append(f"  => 檢驗完成: 掃描 {total_links} 處連結，死鏈數: {dead_count} {status_str}")
    return all_pass, logs


def audit_traditional_chinese(base_dir: str, label: str) -> Tuple[bool, List[str]]:
    """審核所有受控檔案之中文語系，確保繁體中文"""
    logs = []
    all_pass = True
    violations = 0
    total_files = 0

    logs.append(f"\n--- 3. 繁體中文語系與註解合規性檢驗 [{label}] ---")
    for skill in ALL_CONTROLLED_SKILLS:
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

    status_str = "[PASS]" if violations == 0 else "[FAIL]"
    logs.append(f"  => 檢驗完成: 掃描 {total_files} 份檔案，簡體字違規檔案數: {violations} {status_str}")
    return all_pass, logs


def audit_python_compilation(base_dir: str, label: str) -> Tuple[bool, List[str]]:
    """檢驗所有 Python 示範腳本之語法正確性 (py_compile)"""
    logs = []
    all_pass = True
    compiled = 0
    failed = 0

    logs.append(f"\n--- 4. Python 示範腳本 py_compile 語法檢驗 [{label}] ---")
    scripts: List[str] = []
    for skill in ALL_CONTROLLED_SKILLS:
        skill_dir = os.path.join(base_dir, skill)
        if not os.path.exists(skill_dir):
            continue
        for root, dirs, files in os.walk(skill_dir):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                if f.endswith(".py"):
                    scripts.append(os.path.join(root, f))

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
    print("=" * 96)
    print("           PyAnsys 技能生態系林明志標準架構與語法全面審查報告")
    print("=" * 96)

    targets = [
        ("專案端 (Project: SKILLs)", PROJECT_BASE),
        ("全域端 (Global: config/skills)", GLOBAL_BASE),
    ]

    total_pass = True

    for label, base_path in targets:
        print(f"\n==================== 審查對象: {label} ====================")
        p1, l1 = audit_line_counts(base_path, label)
        p2, l2 = audit_dead_links(base_path, label)
        p3, l3 = audit_traditional_chinese(base_path, label)
        p4, l4 = audit_python_compilation(base_path, label)

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
