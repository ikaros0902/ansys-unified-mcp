# -*- coding: utf-8 -*-
"""
測試名稱：test_stage1_book_to_skill_curator.py
功能說明：驗證 Stage 1 手冊思維模型提煉工具與現代 API 守護濾網：
          1. ModernAPISieve: Legacy APDL 阻絕濾網與 Obsolete IronPython UI 濾網 (AST + Regex)
          2. AntiPlagiarismAnnotator: 單段長度 <= 50 字熔斷與證據標籤標註 ([Graph Fact] / [Engineering Heuristic])
          3. PurePhysicalExtractor: 5 大物理模型（湍流選型、Rayleigh 阻尼、CFL 準則、接觸剛度、收斂排障）
          4. MarkdownCircuitBreaker: 自動 TOC (>300 行) 與多檔模組化熔斷拆分 (>500 行)
          5. CLI 介面完整性: --dry-run, --target-skill, --audit-existing, --json-report, --strict
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts" / "skill_governance"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SCRIPTS_DIR))

from book_to_skill_curator import (
    AntiPlagiarismAnnotator,
    BookToSkillCurator,
    MarkdownCircuitBreaker,
    ModernAPISieve,
    PurePhysicalExtractor,
    SieveViolation,
)


# ==============================================================================
# 1. ModernAPISieve 單元測試
# ==============================================================================

class TestModernAPISieve:
    """測試現代 API 守護濾網 (Legacy APDL & Obsolete IronPython UI)"""

    def test_legacy_apdl_processor_interception(self):
        """測試攔截 /PREP7, /SOLU, /POST1 等處理器命令"""
        legacy_text = (
            "# APDL Legacy Setup\n"
            "/PREP7\n"
            "ET, 1, SOLID185\n"
            "MP, EX, 1, 2.1E11\n"
            "/SOLU\n"
            "SOLVE\n"
            "/POST1\n"
            "PLNSOL, S, EQV\n"
        )
        violations = ModernAPISieve.check_text(legacy_text, is_modern_target=True)
        categories = [v.category for v in violations]
        assert "LEGACY_APDL" in categories
        # 應捕捉到多個 APDL 違規
        assert len(violations) >= 5

    def test_legacy_apdl_allowed_for_non_modern(self):
        """若非現代目標技能（如純古典 APDL 技能），不強制報錯"""
        legacy_text = "/PREP7\nET, 1, SOLID185\nSOLVE\n"
        violations = ModernAPISieve.check_text(legacy_text, is_modern_target=False)
        assert len(violations) == 0

    def test_obsolete_ironpython_ast_detection(self):
        """測試透過 AST 檢測 Python 區塊中的舊版 UI 參照"""
        code_block = (
            "```python\n"
            "import clr\n"
            "clr.AddReference('Ans.UI.Toolkit')\n"
            "clr.AddReference('System.Windows.Forms')\n"
            "from Ans.UI.Toolkit import Form\n"
            "```\n"
        )
        violations = ModernAPISieve.check_text(code_block)
        ui_violations = [v for v in violations if v.category == "OBSOLETE_IRONPYTHON_UI"]
        assert len(ui_violations) >= 2
        snippets = [v.snippet for v in ui_violations]
        assert any("Ans.UI" in s for s in snippets)
        assert any("System.Windows.Forms" in s for s in snippets)

    def test_obsolete_ironpython_regex_fallback(self):
        """測試透過 Regex 捕捉不在合法 Python AST 區塊內的舊版 UI 語法"""
        raw_text = "呼叫 clr.AddReference('PresentationFramework') 載入 WPF 組件。"
        violations = ModernAPISieve.check_text(raw_text)
        assert any(v.category == "OBSOLETE_IRONPYTHON_UI" for v in violations)

    def test_sanitize_replaces_violations(self):
        """測試清洗機制能自動過濾 APDL 卡片並給予提示"""
        text = "正常前導文字\n/PREP7\nET, 1, 185\n後續說明"
        sanitized, viols = ModernAPISieve.sanitize(text, is_modern_target=True)
        assert len(viols) == 2
        assert "/PREP7" not in sanitized
        assert "Modern API Sieve 攔截" in sanitized
        assert "正常前導文字" in sanitized
        assert "後續說明" in sanitized


# ==============================================================================
# 2. AntiPlagiarismAnnotator 單元測試
# ==============================================================================

class TestAntiPlagiarismAnnotator:
    """測試反剽竊單段長度限制與證據標籤標註"""

    def test_excessive_verbatim_paragraph_detection(self):
        """測試單一長段落超過 50 字詞觸發反剽竊違規"""
        long_para = "This is an excessively long verbatim paragraph from the manual " * 6  # 60+ words
        violations = AntiPlagiarismAnnotator.check_verbatim_limit(long_para)
        assert len(violations) == 1
        assert violations[0].category == "PLAGIARISM_EXCESSIVE_VERBATIM"

    def test_structured_tables_and_lists_exempt(self):
        """測試結構化表格與條列式清單不計入連續摘抄懲罰"""
        structured_content = (
            "### 參數清單\n"
            "| 參數 | 說明 | 取值 |\n"
            "| --- | --- | --- |\n"
            "| FKN | 法向剛度因子 | 1.0 |\n"
            "| FTOLN | 穿透容差因子 | 0.1 |\n"
            "\n"
            "- 第一點說明\n"
            "- 第二點說明\n"
            "- 第三點說明\n"
        )
        violations = AntiPlagiarismAnnotator.check_verbatim_limit(structured_content)
        assert len(violations) == 0

    def test_synthesize_table_has_evidence_tags(self):
        """測試結構化表格自動附加證據標籤與來源章節"""
        tbl = AntiPlagiarismAnnotator.synthesize_table(
            title="測試矩陣",
            headers=["機制", "數值"],
            rows=[["項目A", "100"]],
            source_doc="Test Manual / Ch 1",
            tag="Engineering Heuristic",
        )
        assert "[Engineering Heuristic]" in tbl
        assert "Test Manual / Ch 1" in tbl
        assert "| 機制 | 數值 | 標記 |" in tbl


# ==============================================================================
# 3. PurePhysicalExtractor 單元測試
# ==============================================================================

class TestPurePhysicalExtractor:
    """測試純物理思維模型萃取器（5 大核心物理模型）"""

    def test_turbulence_decision_matrix(self):
        """驗證湍流模型選型決策矩陣完整性"""
        doc = PurePhysicalExtractor.build_turbulence_decision_matrix()
        assert "Standard k-epsilon" in doc
        assert "Realizable k-epsilon" in doc
        assert "k-omega SST" in doc
        assert "Spalart-Allmaras" in doc
        assert "y^+" in doc or "y+" in doc
        assert "flowchart TD" in doc
        assert "[Graph Fact]" in doc
        assert "[Engineering Heuristic]" in doc

    def test_rayleigh_damping_model(self):
        """驗證 Rayleigh 阻尼計算矩陣與公式完整性"""
        doc = PurePhysicalExtractor.build_rayleigh_damping_model()
        assert "[C] = \\alpha [M] + \\beta [K]" in doc
        assert "\\zeta_i" in doc
        assert "\\alpha = 4\\pi\\zeta" in doc
        assert "\\beta =" in doc
        assert "[Graph Fact]" in doc
        assert "[Engineering Heuristic]" in doc

    def test_cfl_criterion_model(self):
        """驗證 CFL 時間步長準則完整性"""
        doc = PurePhysicalExtractor.build_cfl_criterion_model()
        assert "CFL" in doc
        assert "\\Delta t_{crit}" in doc
        assert "Mass Scaling" in doc
        assert "0.90" in doc
        assert "[Graph Fact]" in doc

    def test_contact_stiffness_model(self):
        """驗證非線性接觸剛度更新與排障決策樹完整性"""
        doc = PurePhysicalExtractor.build_contact_stiffness_model()
        assert "Augmented Lagrange" in doc
        assert "Pure Penalty" in doc
        assert "FKN" in doc
        assert "Pinball" in doc
        assert "flowchart TD" in doc

    def test_convergence_troubleshooting_model(self):
        """驗證非線性收斂排障矩陣完整性"""
        doc = PurePhysicalExtractor.build_convergence_troubleshooting_model()
        assert "Force Convergence" in doc or "力殘差" in doc
        assert "Newton-Raphson" in doc
        assert "Bisection" in doc


# ==============================================================================
# 4. MarkdownCircuitBreaker 單元測試
# ==============================================================================

class TestMarkdownCircuitBreaker:
    """測試 Markdown 行數熔斷器與自動 TOC 生成"""

    def test_short_document_no_toc(self):
        """300 行以下文檔不插入 TOC"""
        short_doc = "# Title\n\n" + "\n".join(f"Line {i}" for i in range(100))
        res = MarkdownCircuitBreaker.modular_split(short_doc, "short_test")
        assert len(res) == 1
        assert "Table of Contents" not in res["short_test.md"]

    def test_medium_document_auto_toc(self):
        """301~500 行文檔自動解析 Heading 插入頂部 TOC"""
        sections = ["# Main Title\n"]
        for i in range(5):
            sections.append(f"## Section {i}\n")
            sections.append("\n".join(f"Paragraph content line {j}" for j in range(70)))
        medium_doc = "\n".join(sections)
        line_count = len(medium_doc.splitlines())
        assert 300 < line_count <= 500

        res = MarkdownCircuitBreaker.modular_split(medium_doc, "medium_test")
        assert len(res) == 1
        content = res["medium_test.md"]
        assert "## 目錄 (Table of Contents)" in content
        assert "- [Section 0](#section-0)" in content
        assert "- [Section 4](#section-4)" in content

    def test_long_document_modular_split(self):
        """超過 500 行文檔啟動熔斷拆分，產出模組化子文檔與主索引"""
        sections = ["# Big Suite\n"]
        for i in range(10):
            sections.append(f"## Module {i}\n")
            sections.append("\n".join(f"Content line for module {i} item {j}" for j in range(80)))
        long_doc = "\n".join(sections)
        line_count = len(long_doc.splitlines())
        assert line_count > 500

        res = MarkdownCircuitBreaker.modular_split(long_doc, "big_suite")
        assert len(res) >= 2  # 包含 Part 檔案與 Index 檔案
        assert "big_suite.md" in res  # 主索引

        # 驗證每個子檔案均 <= 500 行
        for fname, fcontent in res.items():
            flines = len(fcontent.splitlines())
            assert flines <= 500, f"{fname} 行數超出 500 行上限 ({flines} 行)"

        # 驗證主索引包含子文檔連結
        index_content = res["big_suite.md"]
        assert "模組化文檔索引" in index_content
        assert "`big_suite_part1.md`" in index_content


# ==============================================================================
# 5. CLI 與整合流程測試 (Integration Tests)
# ==============================================================================

class TestCuratorCLIIntegration:
    """測試 Book-to-Skill Curator 的完整 CLI 調用與檔案輸出"""

    def test_dry_run_cli(self):
        """測試 --dry-run 命令列執行"""
        cmd = [sys.executable, str(SCRIPTS_DIR / "book_to_skill_curator.py"), "--dry-run"]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        assert result.returncode == 0
        assert "演練模式" in result.stdout
        assert "PASS" in result.stdout

    def test_curate_to_target_skill_directory(self, tmp_path):
        """測試實體產出思維模型至目標技能 references/ 目錄"""
        mock_skill = tmp_path / "mock-pymechanical"
        mock_skill.mkdir()
        (mock_skill / "SKILL.md").write_text("# Mock Skill", encoding="utf-8")

        curator = BookToSkillCurator(target_skill=str(mock_skill), dry_run=False)
        res = curator.run_curation(topic="all")
        assert res["status"] == "success"

        ref_dir = mock_skill / "references"
        assert ref_dir.is_dir()
        files = list(ref_dir.glob("*.md"))
        assert len(files) >= 1

        target_file = ref_dir / "physics_mental_models.md"
        assert target_file.exists()
        content = target_file.read_text(encoding="utf-8")
        assert "湍流模型選型決策矩陣" in content
        assert "Rayleigh 阻尼" in content
        assert "CFL 時間步長" in content
        assert "接觸剛度更新" in content

    def test_audit_existing_detects_violations(self, tmp_path):
        """測試 --audit-existing 能成功偵測 legacy APDL 與舊版 UI 檔案"""
        mock_skill = tmp_path / "mock-legacy-skill"
        ref_dir = mock_skill / "references"
        ref_dir.mkdir(parents=True)

        bad_file = ref_dir / "bad_apdl.md"
        bad_file.write_text(
            "# Legacy File\n"
            "/PREP7\n"
            "ET, 1, 185\n"
            "```python\n"
            "import clr\n"
            "clr.AddReference('Ans.UI.Toolkit')\n"
            "```\n",
            encoding="utf-8",
        )

        curator = BookToSkillCurator(target_skill=str(mock_skill))
        violations = curator.audit_directory(ref_dir)
        categories = {v.category for v in violations}
        assert "LEGACY_APDL" in categories
        assert "OBSOLETE_IRONPYTHON_UI" in categories

    def test_cli_json_report_generation(self, tmp_path):
        """測試 CLI --json-report 輸出格式正確"""
        report_file = tmp_path / "audit_report.json"
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "book_to_skill_curator.py"),
            "--dry-run",
            "--json-report",
            str(report_file),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        assert result.returncode == 0
        assert report_file.exists()
        data = json.loads(report_file.read_text(encoding="utf-8"))
        assert data["mode"] == "curation"
        assert "generated_files" in data
