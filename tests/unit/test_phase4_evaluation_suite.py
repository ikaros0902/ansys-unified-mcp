# -*- coding: utf-8 -*-
"""
單元測試：mcp-builder Phase 4 確定性標量評估套件測試 (test_phase4_evaluation_suite.py)
"""

from pathlib import Path
import json
import pytest

from tests.evaluations.run_mcp_evaluation import (
    load_evaluation_xml,
    compare_scalar,
    run_evaluation,
    clean_scalar_token,
    EvaluationSummary
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EVAL_XML = REPO_ROOT / "tests" / "evaluations" / "ansys_mcp_eval.xml"


def test_eval_xml_exists_and_parses():
    """驗證 tests/evaluations/ansys_mcp_eval.xml 檔案存在且可成功解析"""
    assert EVAL_XML.exists(), f"找不到評估 XML 檔: {EVAL_XML}"
    suite_name, items = load_evaluation_xml(EVAL_XML)
    assert suite_name == "ansys_mcp_eval"
    assert len(items) == 10, f"期望 10 道跨物理域評測題目，實際取得 {len(items)} 題"


def test_eval_xml_exact_10_scalar_answers():
    """驗證 10 道跨物理域標量問答規格完全符合實施計畫 v5.1 第 5.4 節"""
    _, items = load_evaluation_xml(EVAL_XML)

    expected_specs = [
        ("1", "Structural", "2"),
        ("2", "Fluids", "coupled"),
        ("3", "EM", "1"),
        ("4", "Optics", "ZOSAPI.Editors.LDE"),
        ("5", "Thermal", "Celsius"),
        ("6", "Multibody", "2"),
        ("7", "System Coupling", "Heat Rate"),
        ("8", "Materials", "Tsai-Wu"),
        ("9", "Meshing", "SKEWNESS"),
        ("10", "Governance", "DAMG_PRECONDITION_VIOLATION"),
    ]

    for item, (exp_id, exp_domain, exp_answer) in zip(items, expected_specs):
        assert item.id == exp_id
        assert item.domain == exp_domain
        assert item.expected == exp_answer
        assert len(item.question.strip()) > 0


def test_compare_scalar_logic():
    """驗證標量比對核心邏輯：精確字串、大小寫、數值容差、反引號/引號剝離"""
    # 1. 精確匹配
    passed, match_type, _ = compare_scalar("Celsius", "Celsius")
    assert passed and match_type == "EXACT"

    # 2. Markdown 行內反引號與引號
    passed, match_type, _ = compare_scalar("coupled", "`coupled`")
    assert passed and match_type == "EXACT"

    passed, match_type, _ = compare_scalar("ZOSAPI.Editors.LDE", "\"ZOSAPI.Editors.LDE\"")
    assert passed and match_type == "EXACT"

    # 3. 大小寫不敏感
    passed, match_type, _ = compare_scalar("Celsius", "celsius")
    assert passed and match_type == "CASE_INSENSITIVE"

    # 4. 嚴格模式下大小寫不匹配
    passed, match_type, _ = compare_scalar("Celsius", "celsius", strict=True)
    assert not passed and match_type == "MISMATCH"

    # 5. 數值等價
    passed, match_type, _ = compare_scalar("2", "2.0")
    assert passed and match_type == "NUMERIC"

    # 6. 空白與空值
    passed, match_type, _ = compare_scalar("2", "")
    assert not passed and match_type == "MISSING"


def test_run_evaluation_baseline_pass_rate():
    """驗證黃金基準自檢通過率為 100% 且具備客觀延遲度量"""
    summary = run_evaluation(xml_path=EVAL_XML, self_test=True)

    assert isinstance(summary, EvaluationSummary)
    assert summary.total_questions == 10
    assert summary.passed_questions == 10
    assert summary.failed_questions == 0
    assert summary.pass_rate_pct == 100.0
    assert summary.average_latency_ms >= 0.0
    assert summary.total_duration_ms > 0.0

    # 驗證輸出字典可 JSON 序列化
    serialized = json.dumps(summary.to_dict(), ensure_ascii=False)
    assert len(serialized) > 0


def test_run_evaluation_with_candidate_mismatch():
    """驗證候選答案錯誤時正確計入 failed_questions 與退出狀態"""
    candidate_answers = {
        "1": "2",
        "2": "wrong_token",
        "3": "1",
        "4": "ZOSAPI.Editors.LDE",
        "5": "Celsius",
        "6": "2",
        "7": "Heat Rate",
        "8": "Tsai-Wu",
        "9": "SKEWNESS",
        "10": "DAMG_PRECONDITION_VIOLATION",
    }
    summary = run_evaluation(xml_path=EVAL_XML, candidate_answers=candidate_answers)
    assert summary.total_questions == 10
    assert summary.passed_questions == 9
    assert summary.failed_questions == 1
    assert summary.pass_rate_pct == 90.0
    failed_item = [r for r in summary.results if not r.passed][0]
    assert failed_item.id == "2"
    assert failed_item.match_type == "MISMATCH"
