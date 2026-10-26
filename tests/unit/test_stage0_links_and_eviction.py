# -*- coding: utf-8 -*-
"""
測試名稱：test_stage0_links_and_eviction.py
功能說明：驗證 Stage 0 基礎設施：
          1. setup_skill_links.py 自適應連結、雜湊計算與清單生成。
          2. evict_global_ansys_skills.py 技能辨識、安全備份與保留保護。
          3. .gitignore 硬化規則（ASD-STE100 AGENTS.md 受版控、快取與連結目錄被忽略）。
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts" / "maintenance"

# 載入受測模組
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SCRIPTS_DIR))

import setup_skill_links
from evict_global_ansys_skills import (
    KNOWN_ANSYS_EXACT_NAMES,
    execute_eviction,
    get_dir_size_and_count,
    is_ansys_skill,
    scan_skills,
)


class TestSetupSkillLinks:
    """測試 setup_skill_links.py 之跨平台連結與降級邏輯"""

    def test_ssot_source_directory_exists(self):
        """驗證真實來源目錄 agents/skills 存在且有效"""
        assert setup_skill_links.SOURCE_DIR.is_dir()
        skill_count = len([p for p in setup_skill_links.SOURCE_DIR.iterdir() if p.is_dir()])
        assert skill_count >= 10, f"真實來源技能數量異常過低：{skill_count}"

    def test_verify_all_links_status(self):
        """驗證所有預期目錄 (.agents/skills, .cline/skills, .kiro/skills) 皆正常建立"""
        assert setup_skill_links.verify_all_links() is True

    def test_safe_copy_fallback_manifest(self, tmp_path):
        """驗證當降級為安全拷貝模式時，.sync_manifest.json 正確生成且雜湊精確"""
        src = tmp_path / "src_skills"
        src.mkdir()
        (src / "demo_skill").mkdir()
        (src / "demo_skill" / "SKILL.md").write_text("# Demo Skill Content", encoding="utf-8")

        dst = tmp_path / "dst_skills"
        ok, msg = setup_skill_links.create_safe_copy_fallback(src, dst)
        assert ok is True
        assert "安全拷貝模式" in msg

        manifest_file = dst / ".sync_manifest.json"
        assert manifest_file.is_file()

        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["strategy"] == "safe_copy"
        assert manifest["file_count"] == 1
        assert "demo_skill/SKILL.md" in manifest["hashes"]
        assert len(manifest["hashes"]["demo_skill/SKILL.md"]) == 64  # SHA-256 十六進位字串


class TestEvictGlobalAnsysSkills:
    """測試 evict_global_ansys_skills.py 之精準辨識與隔離備份"""

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("ansys-mechanical", True),
            ("ansys-fluent", True),
            ("ansys-optislang", True),
            ("ansys-spaceclaim-modeling", True),
            ("act-extension-development", True),
            ("pcb-warpage-analysis", True),
            ("shock-analysis-workflow", True),
            ("pymechanical-operations", True),
            ("pdf-to-md", True),
            ("simplify-ram", True),
            ("simplify-heatsink", True),
            ("architect-discipline", False),
            ("code-deslop", False),
            ("tdd", False),
            ("pr-craftsman", False),
            ("humanizer-zh-tw", False),
            ("book-to-skill", False),
            ("cae-code-modernization", False),
            ("graphify", False),
            ("system-one-protocols", False),
        ],
    )
    def test_is_ansys_skill_classification(self, name: str, expected: bool):
        """驗證技能分類器對 ANSYS 專案技能與通用技能之判別精準度"""
        assert is_ansys_skill(name) == expected

    def test_scan_and_evict_cycle(self, tmp_path):
        """驗證掃描、備份、清退與非 ANSYS 技能完好保留之完整閉環"""
        fake_global = tmp_path / "global_skills"
        fake_global.mkdir()

        # 模擬 ANSYS 重複技能
        (fake_global / "ansys-test").mkdir()
        (fake_global / "ansys-test" / "SKILL.md").write_text("ansys", encoding="utf-8")
        (fake_global / "pcb-warpage-analysis").mkdir()
        (fake_global / "pcb-warpage-analysis" / "SKILL.md").write_text("pcb", encoding="utf-8")

        # 模擬通用/架構技能（嚴格保留）
        (fake_global / "code-deslop").mkdir()
        (fake_global / "code-deslop" / "SKILL.md").write_text("deslop", encoding="utf-8")
        (fake_global / "tdd").mkdir()
        (fake_global / "tdd" / "SKILL.md").write_text("tdd", encoding="utf-8")

        to_evict, to_preserve = scan_skills(fake_global)
        assert len(to_evict) == 2
        assert len(to_preserve) == 2

        backup_dir = tmp_path / "backup_test"
        success = execute_eviction(fake_global, to_evict, to_preserve, custom_backup_dir=backup_dir)
        assert success is True

        # 驗證清退結果
        assert not (fake_global / "ansys-test").exists()
        assert not (fake_global / "pcb-warpage-analysis").exists()
        assert (fake_global / "code-deslop").is_dir()
        assert (fake_global / "tdd").is_dir()

        # 驗證備份目錄與清單
        assert (backup_dir / "ansys-test" / "SKILL.md").is_file()
        assert (backup_dir / "pcb-warpage-analysis" / "SKILL.md").is_file()
        manifest_file = backup_dir / "backup_manifest.json"
        assert manifest_file.is_file()

        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        assert manifest["evicted_count"] == 2
        assert manifest["preserved_count"] == 2


class TestGitignoreHardening:
    """測試 .gitignore 硬化規則"""

    def test_agents_md_is_not_ignored(self):
        """驗證 AGENTS.md 未被忽略（受 ASD-STE100 契約版本控制保護）"""
        res = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "check-ignore", "-v", "AGENTS.md"],
            capture_output=True,
            text=True,
        )
        # git check-ignore 在有 ! 否定規則時返回代碼 0，且輸出以 ! 開頭
        assert "!AGENTS.md" in res.stdout

    @pytest.mark.parametrize(
        "ignored_path",
        [
            "agents/skills-workspace/",
            "agents/skills/.zvec-grep/",
            "evals/runs/run1.json",
            "evals/review.html",
            "benchmark.json",
            ".agents/skills",
            ".cline/skills",
            ".kiro/skills",
            "ANSYS_Document/",
            "graphify-out/",
        ],
    )
    def test_hardened_patterns_are_ignored(self, ignored_path: str):
        """驗證所有 Stage 0 規範之目錄與檔案皆被 .gitignore 忽略"""
        res = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "check-ignore", ignored_path],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"路徑未被 .gitignore 忽略：{ignored_path}"
