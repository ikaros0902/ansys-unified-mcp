# -*- coding: utf-8 -*-
"""
測試名稱：test_headless_skill_evaluator.py
功能說明：驗證 Stage 1 Headless 評測與基準聚合工具鏈：
          1. Frontmatter 解析與跨目錄技能定位
          2. DeterministicMockAdapter、KiroCLIAdapter 與 GeminiSDKAdapter
          3. 觸發率混淆矩陣判定引擎 (20 題 positive / distractor, Precision / Recall / FPR / Acc)
          4. 斷言評分引擎 (AssertionGrader) 與容錯 JSON 解析
          5. A/B 對照基準評測流程 (timing.json, grading.json)
          6. Benchmark 聚合與 Markdown 報告生成 (aggregate_benchmark.py)
          7. Windows UTF-8 與安全臨時目錄
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts" / "skill_governance"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SCRIPTS_DIR))

from aggregate_benchmark import (
    aggregate_iteration,
    calculate_metrics,
    find_latest_iteration,
    generate_markdown_report,
    scan_iteration_evals,
)
from headless_skill_evaluator import (
    AssertionGrader,
    BaseLLMAdapter,
    ConfusionMatrix,
    DeterministicMockAdapter,
    GeminiSDKAdapter,
    HeadlessSkillEvaluator,
    KiroCLIAdapter,
    LLMResponse,
    LLMTokenUsage,
    SkillMetadata,
    TriggerJudgementEngine,
    TriggerQuery,
    find_skill_directory,
    parse_frontmatter_yaml,
    parse_skill_markdown,
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def mock_skill_dir(tmp_path: Path) -> Path:
    """建立一個標準的 Mock Skill 目錄與 evals.json"""
    skill_dir = tmp_path / "mock-ls-prepost"
    skill_dir.mkdir(parents=True)

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: mock-ls-prepost\n"
        "description: ANSYS LS-PrePost 腳本前處理與後處理主控手冊。觸發關鍵字: ls-prepost, d3plot, cfile\n"
        "---\n\n"
        "# Mock LS-PrePost Manual\n"
        "This is mock body content for testing headless evaluation.\n",
        encoding="utf-8",
    )

    evals_dir = skill_dir / "evals"
    evals_dir.mkdir(parents=True)
    evals_file = evals_dir / "evals.json"
    evals_data = {
        "skill": "mock-ls-prepost",
        "evals": [
            {
                "eval_id": 1,
                "prompt": "d3plot 打開後要量兩個零件在撞擊瞬間的最小間隙？",
                "assertions": [
                    "有提到使用 Measure 工具下的 Separation 量測功能",
                    "有提醒 Displacement Scale Factor 設回 1.0",
                ],
            },
            {
                "eval_id": 2,
                "prompt": "如何用 cfile 輸出特定時刻雲圖？",
                "assertions": [
                    "有給出正確的 ls-prepost 截圖指令",
                ],
            },
        ],
    }
    evals_file.write_text(json.dumps(evals_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return skill_dir


# ==============================================================================
# 1. Frontmatter 解析與技能定位測試
# ==============================================================================

class TestFrontmatterAndDiscovery:
    """測試 Frontmatter 解析與跨目錄搜尋能力"""

    def test_parse_frontmatter_yaml_normal(self):
        text = (
            "---\n"
            "name: test-skill\n"
            "description: 測試用技能說明\n"
            "custom_field: true\n"
            "---\n\n"
            "# 標題\n"
            "正文內容"
        )
        fm, body = parse_frontmatter_yaml(text)
        assert fm["name"] == "test-skill"
        assert fm["description"] == "測試用技能說明"
        assert fm["custom_field"] is True
        assert body.startswith("# 標題")

    def test_parse_frontmatter_yaml_no_frontmatter(self):
        text = "# 僅有主文\n無 Frontmatter"
        fm, body = parse_frontmatter_yaml(text)
        assert fm == {}
        assert body == text

    def test_parse_skill_markdown(self, mock_skill_dir: Path):
        meta = parse_skill_markdown(mock_skill_dir / "SKILL.md")
        assert meta.name == "mock-ls-prepost"
        assert "LS-PrePost" in meta.description
        assert "Mock LS-PrePost Manual" in meta.body

    def test_find_skill_directory_by_path(self, mock_skill_dir: Path):
        found = find_skill_directory(mock_skill_dir)
        assert found == mock_skill_dir

        found_from_md = find_skill_directory(mock_skill_dir / "SKILL.md")
        assert found_from_md == mock_skill_dir

    def test_find_skill_directory_from_legacy_tier2_path(self, tmp_path: Path):
        legacy_skill = tmp_path / "agents" / "skills-tier2" / "demo-skill"
        current_skill = tmp_path / "agents" / "skills" / "demo-skill"
        current_skill.mkdir(parents=True)
        (current_skill / "SKILL.md").write_text("---\nname: demo-skill\ndescription: demo\n---\n", encoding="utf-8")

        found = find_skill_directory(legacy_skill, repo_root=tmp_path)

        assert found == current_skill


    def test_find_nested_skill_from_legacy_tier2_markdown_path(self, tmp_path: Path):
        current_skill = tmp_path / "agents" / "skills" / "fluids-cfd" / "demo-skill"
        current_skill.mkdir(parents=True)
        (current_skill / "SKILL.md").write_text("---\nname: demo-skill\ndescription: demo\n---\n", encoding="utf-8")
        legacy_markdown = tmp_path / "agents" / "skills-tier2" / "demo-skill" / "SKILL.md"

        assert find_skill_directory(legacy_markdown, repo_root=tmp_path) == current_skill

    def test_find_skill_directory_nonexistent_raises(self):
        with pytest.raises(FileNotFoundError, match="無法在專案候選目錄中定位技能"):
            find_skill_directory("completely-non-existent-skill-xyz")


# ==============================================================================
# 2. 適配器架構測試
# ==============================================================================

class TestAdapters:
    """測試各類 LLM 適配器與調度行為"""

    def test_deterministic_mock_adapter_rules(self):
        adapter = DeterministicMockAdapter(
            default_response="Default answer",
            rules={r"hello": "Hello World!", r"count": "123"},
            duration_ms=42.0,
            tokens_per_call=LLMTokenUsage(10, 20, 30),
        )
        resp1 = adapter.generate("system", "Say hello to me")
        assert resp1.text == "Hello World!"
        assert resp1.duration_ms == 42.0
        assert resp1.tokens.total_tokens == 30

        resp2 = adapter.generate("system", "Just checking")
        assert resp2.text == "Default answer"
        assert len(adapter.calls) == 2

    def test_deterministic_mock_adapter_custom_handler(self):
        def custom(sys_p: str, user_p: str):
            return f"Echo: {user_p.upper()}"

        adapter = DeterministicMockAdapter(custom_handler=custom)
        resp = adapter.generate("sys", "ping")
        assert resp.text == "Echo: PING"

    @patch("subprocess.run")
    def test_kiro_cli_adapter_command_and_utf8(self, mock_run: MagicMock):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Kiro output response"
        mock_proc.stderr = ""
        mock_run.return_value = mock_proc

        adapter = KiroCLIAdapter(cli_path="kiro-cli.exe", model="claude-sonnet-5", effort="high")
        resp = adapter.generate("System instruction", "User query")

        assert resp.text == "Kiro output response"
        assert mock_run.called

        # 驗證 Windows UTF-8 與命令列參數
        call_args, call_kwargs = mock_run.call_args
        cmd = call_args[0]
        assert "kiro-cli.exe" in cmd[0]
        assert "--no-interactive" in cmd
        assert "-a" in cmd
        assert "--model" in cmd
        assert "claude-sonnet-5" in cmd
        assert "--effort" in cmd
        assert "high" in cmd
        assert call_kwargs.get("encoding") == "utf-8"
        assert call_kwargs.get("errors") == "replace"

    @patch("subprocess.run")
    def test_kiro_cli_adapter_error_handling(self, mock_run: MagicMock):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stdout = ""
        mock_proc.stderr = "Fatal error: invalid token"
        mock_run.return_value = mock_proc

        adapter = KiroCLIAdapter(cli_path="kiro-cli.exe")
        with pytest.raises(RuntimeError, match="Kiro CLI 執行異常"):
            adapter.generate("sys", "user")

    def test_gemini_sdk_adapter_missing_key_raises(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

        adapter = GeminiSDKAdapter()
        with pytest.raises(ValueError, match="缺少 API 金鑰"):
            adapter.generate("sys", "user")


# ==============================================================================
# 3. 觸發率混淆矩陣判定引擎測試
# ==============================================================================

class TestTriggerJudgementEngine:
    """測試 20 題觸發率判定與混淆矩陣指標計算"""

    def test_extract_json_block_formats(self):
        # 1. 直接 JSON
        assert TriggerJudgementEngine.extract_json_block('{"selected": true}') == {"selected": True}

        # 2. Markdown 程式碼區塊
        md_text = "Here is decision:\n```json\n{\"selected\": false, \"reasoning\": \"ok\"}\n```\nDone."
        extracted = TriggerJudgementEngine.extract_json_block(md_text)
        assert extracted.get("selected") is False
        assert extracted.get("reasoning") == "ok"

        # 3. 帶雜訊文字的內嵌 JSON
        noise_text = "Decision: {\"selected\": true, \"confidence\": 0.9} thank you"
        assert TriggerJudgementEngine.extract_json_block(noise_text).get("selected") is True

        # 4. 無效文字容錯
        assert TriggerJudgementEngine.extract_json_block("Random non-json text") == {}

    def test_generate_default_20_queries(self, mock_skill_dir: Path):
        skill = parse_skill_markdown(mock_skill_dir / "SKILL.md")
        queries = TriggerJudgementEngine.generate_default_20_queries(skill)

        assert len(queries) == 20
        positives = [q for q in queries if q.expected_trigger]
        distractors = [q for q in queries if not q.expected_trigger]

        assert len(positives) == 10
        assert len(distractors) == 10
        assert all(q.category == "positive" for q in positives)
        assert all(q.category == "adjacent_distractor" for q in distractors)

    def test_confusion_matrix_calculation(self, mock_skill_dir: Path):
        skill = parse_skill_markdown(mock_skill_dir / "SKILL.md")

        # 使用 DeterministicMockAdapter
        adapter = DeterministicMockAdapter()
        engine = TriggerJudgementEngine(adapter)

        # 傳入 4 道受控題目：2 正向 + 2 干擾
        # 題目中正向題包含 "[POSITIVE]" 標記
        test_queries = [
            TriggerQuery(1, "[POSITIVE] 撞擊後 d3plot 讀取", expected_trigger=True),
            TriggerQuery(2, "[POSITIVE] ls-prepost 腳本呼叫", expected_trigger=True),
            TriggerQuery(3, "如何撰寫 React 前端組件？", expected_trigger=False),
            TriggerQuery(4, "Git 分支合併衝突處理", expected_trigger=False),
        ]

        result = engine.evaluate_skill_trigger(skill, queries=test_queries)
        m = result.matrix

        # 預期：2 TP, 0 FP, 2 TN, 0 FN
        assert m.tp == 2
        assert m.fp == 0
        assert m.tn == 2
        assert m.fn == 0
        assert m.precision == 1.0
        assert m.recall == 1.0
        assert m.fpr == 0.0
        assert m.accuracy == 1.0
        assert m.total == 4

    def test_confusion_matrix_zero_division_guard(self):
        m = ConfusionMatrix(tp=0, fp=0, tn=0, fn=0, total=0)
        assert m.precision == 0.0
        assert m.recall == 0.0
        assert m.fpr == 0.0
        assert m.accuracy == 0.0


# ==============================================================================
# 4. 斷言評分引擎測試
# ==============================================================================

class TestAssertionGrader:
    """測試斷言評分解析與分數計算"""

    def test_grade_all_passed(self):
        adapter = DeterministicMockAdapter()  # 預設對 passed 詢問回傳 {"passed": true}
        grader = AssertionGrader(adapter)

        result = grader.grade(
            user_prompt="測試題目",
            response_text="受測回答文字",
            assertions=["斷言 1: 有提到關鍵字 A", "斷言 2: 有提到關鍵字 B"],
        )

        assert result.passed is True
        assert result.score == 1.0
        assert len(result.assertions) == 2
        assert all(a.passed for a in result.assertions)

    def test_grade_partially_failed(self):
        def custom_judge(sys_p: str, user_p: str):
            if "關鍵字 B" in user_p:
                return '{"passed": false, "evidence": "未提及關鍵字 B"}'
            return '{"passed": true, "evidence": "符合條件"}'

        adapter = DeterministicMockAdapter(custom_handler=custom_judge)
        grader = AssertionGrader(adapter)

        result = grader.grade(
            user_prompt="測試題目",
            response_text="受測回答文字",
            assertions=["斷言 1: 有提到關鍵字 A", "斷言 2: 需含有關鍵字 B"],
        )

        assert result.passed is False
        assert result.score == 0.5
        assert result.assertions[0].passed is True
        assert result.assertions[1].passed is False

    def test_grade_empty_assertions(self):
        adapter = DeterministicMockAdapter()
        grader = AssertionGrader(adapter)
        result = grader.grade("prompt", "text", [])
        assert result.passed is True
        assert result.score == 1.0


# ==============================================================================
# 5. A/B 評測與工作區輸出測試
# ==============================================================================

class TestHeadlessSkillEvaluatorAB:
    """測試 HeadlessSkillEvaluator 之完整 A/B 流程與檔案生成"""

    def test_ab_evaluations_and_artifacts(self, mock_skill_dir: Path, tmp_path: Path):
        workspace_dir = tmp_path / "skills-workspace"
        adapter = DeterministicMockAdapter(
            duration_ms=88.0,
            tokens_per_call=LLMTokenUsage(120, 60, 180),
        )

        evaluator = HeadlessSkillEvaluator(
            skill_target=mock_skill_dir,
            adapter=adapter,
            workspace_root=workspace_dir,
        )

        # 1. 執行 A/B 評測
        ab_summary = evaluator.run_ab_evaluations(iteration=1)
        assert ab_summary["cases_count"] == 2
        assert ab_summary["iteration"] == 1

        iter_dir = workspace_dir / "mock-ls-prepost-workspace" / "iteration-1"
        assert iter_dir.is_dir()

        # 2. 驗證每個案例的輸出目錄結構
        for eval_id in (1, 2):
            case_dir = iter_dir / f"eval-{eval_id}"
            assert (case_dir / "with_skill" / "timing.json").is_file()
            assert (case_dir / "with_skill" / "grading.json").is_file()
            assert (case_dir / "without_skill" / "timing.json").is_file()
            assert (case_dir / "without_skill" / "grading.json").is_file()

            # 檢查 timing.json 結構
            with open(case_dir / "with_skill" / "timing.json", "r", encoding="utf-8") as f:
                timing = json.load(f)
                assert timing["duration_ms"] == 88.0
                assert timing["tokens"]["total_tokens"] == 180

            # 檢查 grading.json 結構
            with open(case_dir / "with_skill" / "grading.json", "r", encoding="utf-8") as f:
                grading = json.load(f)
                assert "passed" in grading
                assert "score" in grading
                assert "assertions" in grading

        # 3. 執行觸發率測試
        trigger_res = evaluator.run_trigger_test(iteration=1)
        assert (iter_dir / "trigger_eval.json").is_file()
        assert trigger_res.matrix.total == 20


# ==============================================================================
# 6. Benchmark 聚合與 Markdown 報告測試
# ==============================================================================

class TestAggregateBenchmark:
    """測試 aggregate_benchmark.py 之統計計算與報告生成"""

    def test_aggregate_iteration(self, mock_skill_dir: Path, tmp_path: Path):
        workspace_dir = tmp_path / "skills-workspace"
        adapter = DeterministicMockAdapter()
        evaluator = HeadlessSkillEvaluator(
            skill_target=mock_skill_dir,
            adapter=adapter,
            workspace_root=workspace_dir,
        )

        evaluator.run_ab_evaluations(iteration=1)
        evaluator.run_trigger_test(iteration=1)

        iter_dir = workspace_dir / "mock-ls-prepost-workspace" / "iteration-1"

        # 執行聚合
        benchmark_data = aggregate_iteration(iter_dir)

        assert benchmark_data["skill"] == "mock-ls-prepost"
        assert benchmark_data["iteration"] == 1
        assert "summary" in benchmark_data
        assert "with_skill" in benchmark_data["summary"]
        assert "without_skill" in benchmark_data["summary"]
        assert "delta" in benchmark_data["summary"]
        assert "trigger_evaluation" in benchmark_data

        # 驗證實體檔案
        assert (iter_dir / "benchmark.json").is_file()
        assert (iter_dir / "benchmark.md").is_file()

        md_text = (iter_dir / "benchmark.md").read_text(encoding="utf-8")
        assert "# 技能基準評測報告" in md_text
        assert "mock-ls-prepost" in md_text
        assert "混淆矩陣" in md_text
        assert "單一測試案例詳細比對" in md_text

    def test_calculate_metrics_delta(self):
        records = [
            {
                "eval_id": 1,
                "status": "IMPROVED",
                "with_skill": {
                    "passed": True,
                    "score": 1.0,
                    "duration_ms": 1000.0,
                    "tokens": {"prompt_tokens": 800, "completion_tokens": 200, "total_tokens": 1000},
                },
                "without_skill": {
                    "passed": False,
                    "score": 0.0,
                    "duration_ms": 600.0,
                    "tokens": {"prompt_tokens": 200, "completion_tokens": 100, "total_tokens": 300},
                },
            },
            {
                "eval_id": 2,
                "status": "UNCHANGED_PASS",
                "with_skill": {
                    "passed": True,
                    "score": 1.0,
                    "duration_ms": 1200.0,
                    "tokens": {"prompt_tokens": 900, "completion_tokens": 300, "total_tokens": 1200},
                },
                "without_skill": {
                    "passed": True,
                    "score": 1.0,
                    "duration_ms": 700.0,
                    "tokens": {"prompt_tokens": 250, "completion_tokens": 150, "total_tokens": 400},
                },
            },
        ]

        metrics = calculate_metrics(records)
        assert metrics["total_evals"] == 2
        assert metrics["with_skill"]["pass_count"] == 2
        assert metrics["with_skill"]["pass_rate"] == 1.0
        assert metrics["without_skill"]["pass_count"] == 1
        assert metrics["without_skill"]["pass_rate"] == 0.5
        assert metrics["delta"]["pass_rate_gain"] == 0.5
        assert metrics["delta"]["duration_delta_ms"] == 450.0  # 1100 - 650
        assert metrics["delta"]["token_overhead"] == 750  # 1100 - 350


# ==============================================================================
# 7. CLI 指令進入點整合測試
# ==============================================================================

class TestCLIIntegration:
    """測試命令列工具在 Windows UTF-8 環境下的執行"""

    def test_headless_evaluator_cli_help(self):
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPTS_DIR / "headless_skill_evaluator.py"), "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0
        assert "--skill" in result.stdout
        assert "--adapter" in result.stdout

    def test_aggregate_benchmark_cli_help(self):
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPTS_DIR / "aggregate_benchmark.py"), "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0
        assert "--iteration-dir" in result.stdout
        assert "--workspace" in result.stdout
