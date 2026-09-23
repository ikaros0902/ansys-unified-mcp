# -*- coding: utf-8 -*-
"""
測試名稱：test_skills_integrity.py
功能說明：驗證 SKILLs/（唯一真實來源）與 .kiro/skills/ 之間所有受控技能檔案
          的 1:1 對應與 SHA-256 位元級一致性。
"""

import hashlib
import sys
from pathlib import Path

import pytest

# 匯入同步引擎的共用掃描/發現函式，避免重複實作邏輯
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from sync_skills_bidirectional import (  # noqa: E402
    discover_controlled_skills,
    scan_skill_files,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "SKILLs"
KIRO_ROOT = REPO_ROOT / ".kiro" / "skills"


def _controlled_skills():
    """回傳 SKILLs/ 下所有受控技能名稱（動態掃描，與同步腳本邏輯一致）"""
    return discover_controlled_skills(str(SOURCE_ROOT))


CONTROLLED_SKILLS = _controlled_skills()


@pytest.fixture(scope="module")
def controlled_skills():
    """提供受控技能清單；若清單為空，判定前置環境有誤，直接失敗"""
    skills = CONTROLLED_SKILLS
    assert skills, "SKILLs/ 目錄下未掃描到任何含 SKILL.md 的受控技能，請確認來源目錄存在"
    return skills


def test_controlled_skills_nonempty(controlled_skills):
    """受控技能清單不得為空"""
    assert len(controlled_skills) > 0


@pytest.mark.parametrize("skill_name", CONTROLLED_SKILLS)
def test_skill_exists_in_kiro(skill_name):
    """每個受控技能在 .kiro/skills/ 下必須存在對應目錄"""
    kiro_skill_dir = KIRO_ROOT / skill_name
    assert kiro_skill_dir.is_dir(), (
        f"技能 '{skill_name}' 存在於 SKILLs/ 但缺失於 .kiro/skills/"
    )


@pytest.mark.parametrize("skill_name", CONTROLLED_SKILLS)
def test_skill_files_match_byte_for_byte(skill_name):
    """
    每個受控技能：SKILLs/ 與 .kiro/skills/ 底下的檔案集合須完全一致，
    且每個相同相對路徑的檔案 SHA-256 雜湊須逐位元組相符。
    """
    source_dir = SOURCE_ROOT / skill_name
    kiro_dir = KIRO_ROOT / skill_name

    source_files = scan_skill_files(str(source_dir))
    kiro_files = scan_skill_files(str(kiro_dir))

    source_rels = set(source_files.keys())
    kiro_rels = set(kiro_files.keys())

    missing_in_kiro = source_rels - kiro_rels
    extra_in_kiro = kiro_rels - source_rels

    assert not missing_in_kiro, (
        f"技能 '{skill_name}': 以下檔案存在於 SKILLs/ 但缺失於 .kiro/skills/: "
        f"{sorted(missing_in_kiro)}"
    )
    assert not extra_in_kiro, (
        f"技能 '{skill_name}': 以下檔案僅存在於 .kiro/skills/（孤立檔案）: "
        f"{sorted(extra_in_kiro)}"
    )

    hash_mismatches = []
    for rel in sorted(source_rels):
        src_meta = source_files[rel]
        dst_meta = kiro_files[rel]
        if src_meta["sha256"] != dst_meta["sha256"]:
            hash_mismatches.append(rel)

    assert not hash_mismatches, (
        f"技能 '{skill_name}': 以下檔案 SHA-256 不一致（非位元級相符): "
        f"{hash_mismatches}"
    )


def test_overall_sha256_parity_summary(controlled_skills):
    """
    彙總驗證：計算所有受控技能檔案的整體 SHA-256 吻合率，
    必須 100% 吻合（總差異數精確為 0）。
    """
    total_files = 0
    total_diffs = 0
    diff_details = []

    for skill_name in controlled_skills:
        source_dir = SOURCE_ROOT / skill_name
        kiro_dir = KIRO_ROOT / skill_name

        source_files = scan_skill_files(str(source_dir))
        kiro_files = scan_skill_files(str(kiro_dir))

        all_rels = sorted(set(source_files.keys()) | set(kiro_files.keys()))
        total_files += len(all_rels)

        for rel in all_rels:
            src_meta = source_files.get(rel)
            dst_meta = kiro_files.get(rel)
            if src_meta and dst_meta:
                if src_meta["sha256"] != dst_meta["sha256"]:
                    total_diffs += 1
                    diff_details.append(f"[雜湊不符] {skill_name}/{rel}")
            elif src_meta:
                total_diffs += 1
                diff_details.append(f"[僅專案端] {skill_name}/{rel}")
            else:
                total_diffs += 1
                diff_details.append(f"[僅.kiro端] {skill_name}/{rel}")

    assert total_diffs == 0, (
        f"預期 100% SHA-256 吻合，實際發現 {total_diffs} 處差異（共 {total_files} 檔案）: "
        f"{diff_details}"
    )
