# -*- coding: utf-8 -*-
"""
測試模組：test_validate_skills_ci.py
功能說明：驗證 validate_skills_ci.py 靜態檢查門禁工具的各項檢查規則與容錯修復功能。
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import pytest

from scripts.skill_governance.validate_skills_ci import (
    MAX_SKILL_MD_LINES,
    MAX_DESCRIPTION_WORDS,
    REF_TOC_LINE_THRESHOLD,
    REF_MAX_LINE_THRESHOLD,
    SkillViolation,
    check_skill_md_line_count,
    check_yaml_frontmatter,
    check_references_directory,
    check_4_folder_anatomy,
    check_gitignore_rules,
    validate_single_skill,
    run_full_validation,
    build_markdown_toc,
    generate_markdown_anchor,
    inject_toc_into_markdown,
    main,
)


@pytest.fixture
def temp_skill_dir(tmp_path: Path) -> Path:
    """建立基礎技能目錄 fixture"""
    skill_dir = tmp_path / "test-sample-skill"
    skill_dir.mkdir(parents=True)
    return skill_dir


def test_markdown_anchor_generation():
    """驗證 Markdown 錨點生成正則與中英文轉換"""
    assert generate_markdown_anchor("ERR-SC-001: gRPC TLS 警告") == "err-sc-001-grpc-tls-警告"
    assert generate_markdown_anchor("## 2. 核心架構 (Core Architecture)") == "2-核心架構-core-architecture"
    assert generate_markdown_anchor("`rename_object` 不支援") == "rename_object-不支援"


def test_build_markdown_toc_and_injection():
    """驗證 TOC 生成與注入前 40 行功能"""
    content = (
        "# 測試標題\n\n"
        "---\n\n"
        "## 第一章：環境設定\n"
        "內文說明...\n\n"
        "### 1.1 Python 版本\n"
        "Python 3.10+\n\n"
        "## 第二章：除錯指引\n"
        "除錯內容...\n"
    )
    toc = build_markdown_toc(content)
    assert "## Table of Contents" in toc
    assert "- [第一章：環境設定](#第一章環境設定)" in toc
    assert "  - [1.1 Python 版本](#11-python-版本)" in toc

    injected = inject_toc_into_markdown(content, toc)
    lines = injected.splitlines()
    assert lines[0] == "# 測試標題"
    # 確認 Table of Contents 在前 10 行內
    assert any("Table of Contents" in line for line in lines[:10])


def test_check_skill_md_line_count_pass(temp_skill_dir: Path):
    """驗證 SKILL.md 行數 <= 150 時合規通過"""
    skill_md = temp_skill_dir / "SKILL.md"
    skill_md.write_text("\n".join([f"line {i}" for i in range(120)]), encoding="utf-8")

    violations = check_skill_md_line_count(temp_skill_dir)
    assert len(violations) == 0


def test_check_skill_md_line_count_fail(temp_skill_dir: Path):
    """驗證 SKILL.md 行數 > 150 時報錯並明確列出行數"""
    skill_md = temp_skill_dir / "SKILL.md"
    skill_md.write_text("\n".join([f"line {i}" for i in range(160)]), encoding="utf-8")

    violations = check_skill_md_line_count(temp_skill_dir)
    assert len(violations) == 1
    assert violations[0].severity == "ERROR"
    assert "160 行 > 150 行" in violations[0].message


def test_check_yaml_frontmatter_valid(temp_skill_dir: Path):
    """驗證合規 Frontmatter 通過檢查"""
    skill_md = temp_skill_dir / "SKILL.md"
    fm_content = (
        "---\n"
        f"name: {temp_skill_dir.name}\n"
        "description: 這是用於測試驗證的技能說明。觸發關鍵字 (繁中/En): 測試, Unit Test。\n"
        "---\n"
        "# 測試技能\n"
    )
    skill_md.write_text(fm_content, encoding="utf-8")

    violations = check_yaml_frontmatter(temp_skill_dir)
    assert len(violations) == 0


def test_check_yaml_frontmatter_name_mismatch(temp_skill_dir: Path):
    """驗證 Frontmatter name 與目錄名稱不一致時報錯"""
    skill_md = temp_skill_dir / "SKILL.md"
    fm_content = (
        "---\n"
        "name: different-name\n"
        "description: 測試描述。\n"
        "---\n"
    )
    skill_md.write_text(fm_content, encoding="utf-8")

    violations = check_yaml_frontmatter(temp_skill_dir)
    assert any("不一致" in v.message for v in violations)


def test_check_yaml_frontmatter_invalid_kebab_case(tmp_path: Path):
    """驗證 Frontmatter name 非小寫 kebab-case 時報錯"""
    bad_dir = tmp_path / "Bad_Skill_Name"
    bad_dir.mkdir()
    skill_md = bad_dir / "SKILL.md"
    fm_content = (
        "---\n"
        f"name: {bad_dir.name}\n"
        "description: 測試描述。\n"
        "---\n"
    )
    skill_md.write_text(fm_content, encoding="utf-8")

    violations = check_yaml_frontmatter(bad_dir)
    assert any("kebab-case" in v.message for v in violations)


def test_check_yaml_frontmatter_desc_too_long(temp_skill_dir: Path):
    """驗證 Frontmatter description 超過 120 words 時報錯"""
    skill_md = temp_skill_dir / "SKILL.md"
    long_desc = " ".join(["word"] * 135)
    fm_content = (
        "---\n"
        f"name: {temp_skill_dir.name}\n"
        f"description: {long_desc}\n"
        "---\n"
    )
    skill_md.write_text(fm_content, encoding="utf-8")

    violations = check_yaml_frontmatter(temp_skill_dir)
    assert any("超過上限 120 words" in v.message for v in violations)


def test_references_under_300_lines_pass(temp_skill_dir: Path):
    """驗證 references 檔案 <= 300 行時無須強制 TOC"""
    ref_dir = temp_skill_dir / "references"
    ref_dir.mkdir()
    doc = ref_dir / "short_doc.md"
    doc.write_text("\n".join([f"line {i}" for i in range(200)]), encoding="utf-8")

    violations, repaired = check_references_directory(temp_skill_dir, fix_toc=False)
    assert len(violations) == 0
    assert len(repaired) == 0


def test_references_over_300_lines_missing_toc_fail(temp_skill_dir: Path):
    """驗證 references 檔案 > 300 行缺少 TOC 時報錯"""
    ref_dir = temp_skill_dir / "references"
    ref_dir.mkdir()
    doc = ref_dir / "long_doc.md"
    doc.write_text("\n".join([f"line {i}" for i in range(350)]), encoding="utf-8")

    violations, repaired = check_references_directory(temp_skill_dir, fix_toc=False)
    assert len(violations) == 1
    assert "缺少目錄標記" in violations[0].message


def test_references_over_300_lines_with_toc_pass(temp_skill_dir: Path):
    """驗證 references 檔案 > 300 行但前 40 行具備 TOC 時通過"""
    ref_dir = temp_skill_dir / "references"
    ref_dir.mkdir()
    doc = ref_dir / "long_doc_with_toc.md"
    content = "# 標題\n\n## Table of Contents\n- [節 1](#節-1)\n\n" + "\n".join([f"line {i}" for i in range(350)])
    doc.write_text(content, encoding="utf-8")

    violations, repaired = check_references_directory(temp_skill_dir, fix_toc=False)
    assert len(violations) == 0


def test_references_fix_toc_auto_repair(temp_skill_dir: Path):
    """驗證 --fix-toc 能夠為 > 300 行缺少 TOC 的檔案自動修復並通過"""
    ref_dir = temp_skill_dir / "references"
    ref_dir.mkdir()
    doc = ref_dir / "long_doc_to_fix.md"
    body = "# 測試文件\n\n## 第一節\n內容\n\n## 第二節\n內容\n\n" + "\n".join([f"line {i}" for i in range(320)])
    doc.write_text(body, encoding="utf-8")

    # 執行修復模式
    violations, repaired = check_references_directory(temp_skill_dir, fix_toc=True)
    assert len(violations) == 0
    assert len(repaired) == 1
    assert "自動生成並注入" in repaired[0]

    # 驗證回寫後的檔案前 40 行包含 TOC
    re_read_lines = doc.read_text(encoding="utf-8").splitlines()[:40]
    assert any("Table of Contents" in ln for ln in re_read_lines)


def test_references_over_500_lines_fail(temp_skill_dir: Path):
    """驗證 references 檔案 > 500 行時觸發單檔上限錯誤 (強制要求拆分)"""
    ref_dir = temp_skill_dir / "references"
    ref_dir.mkdir()
    doc = ref_dir / "massive_doc.md"
    doc.write_text("# 標題\n\n## Table of Contents\n\n" + "\n".join([f"line {i}" for i in range(520)]), encoding="utf-8")

    violations, repaired = check_references_directory(temp_skill_dir, fix_toc=False)
    assert any("超出單檔安全上限" in v.message for v in violations)


def test_check_4_folder_anatomy(temp_skill_dir: Path):
    """驗證 4-Folder Anatomy 規範檢查"""
    # 建立合規檔案與目錄
    (temp_skill_dir / "SKILL.md").write_text("---\nname: test-sample-skill\ndescription: 測試\n---\n", encoding="utf-8")
    (temp_skill_dir / "references").mkdir()
    (temp_skill_dir / "scripts").mkdir()
    (temp_skill_dir / "assets").mkdir()
    (temp_skill_dir / "evals").mkdir()
    (temp_skill_dir / "README.md").write_text("# README", encoding="utf-8")

    violations = check_4_folder_anatomy(temp_skill_dir)
    assert len(violations) == 0

    # 加入非標準目錄
    bad_sub = temp_skill_dir / "random_folder"
    bad_sub.mkdir()
    violations = check_4_folder_anatomy(temp_skill_dir)
    assert any("發現非標準子目錄: 'random_folder/'" in v.message for v in violations)


def test_check_gitignore_rules():
    """驗證真實倉庫中的 .gitignore 規則檢查 (git check-ignore)"""
    repo_root = Path(__file__).resolve().parents[2]
    violations = check_gitignore_rules(repo_root)
    # 真實專案根目錄下，三條受稽核路徑皆已被忽略
    assert len(violations) == 0


def test_full_validation_on_actual_repo():
    """驗證真實專案目錄全量靜態檢查執行結果"""
    repo_root = Path(__file__).resolve().parents[2]
    report = run_full_validation(
        repo_root=repo_root,
        fix_toc=False,
    )
    # 所有檢查皆應完全通過
    assert report.is_passed
    assert report.total_errors == 0
    assert report.tier1_skills_checked == 44
    assert report.tier2_skills_checked == 0
    assert report.total_skills_checked == 44


def test_cli_execution_via_main():
    """驗證 main() CLI 介面參數解析與退出碼"""
    repo_root = Path(__file__).resolve().parents[2]
    # 測試 --tier1-only
    exit_code_t1 = main(["--tier1-only", "--repo-root", str(repo_root)])
    assert exit_code_t1 == 0

    # 測試 --tier2-only
    exit_code_t2 = main(["--tier2-only", "--repo-root", str(repo_root)])
    assert exit_code_t2 == 0
