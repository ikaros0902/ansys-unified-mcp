#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ansys Unified MCP - Phase 4 確定性標量評估套件執行器 (Deterministic Scalar Evaluation Runner)

遵循 mcp-builder Phase 4 規範：
- 讀取 tests/evaluations/ansys_mcp_eval.xml
- 執行 100% 確定性標量值比對 (Direct String Comparison / Scalar Comparison)
- 零 LLM-as-a-Judge 依賴，保證可重複性與客觀判定
- 輸出標準化指標：總題數、通過題數、通過率、平均延遲與判定證據
- 支援 CLI 旗標：--xml, --answers, --json-output, --verbose, --strict
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 確保 Windows 終端輸出 UTF-8 編碼正常顯示
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass



@dataclass
class EvaluationItem:
    """評估問答項目"""
    id: str
    domain: str
    question: str
    expected: str


@dataclass
class ComparisonResult:
    """單題比對結果與客觀證據"""
    id: str
    domain: str
    question: str
    expected: str
    actual: str
    passed: bool
    match_type: str  # EXACT, CASE_INSENSITIVE, NUMERIC, MISMATCH, MISSING
    latency_ms: float
    evidence: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvaluationSummary:
    """評估套件總結指標"""
    suite_name: str
    xml_path: str
    timestamp: str
    total_questions: int
    passed_questions: int
    failed_questions: int
    pass_rate_pct: float
    average_latency_ms: float
    total_duration_ms: float
    strict_mode: bool
    results: List[ComparisonResult]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["results"] = [r.to_dict() if hasattr(r, "to_dict") else r for r in self.results]
        return data


def clean_scalar_token(val: Any) -> str:
    """
    清理標量字串（去除前後空白、引號、Markdown 行內代碼反引號）
    """
    if val is None:
        return ""
    s = str(val).strip()
    # 移除行內反引號包裹 (如 `coupled` -> coupled)
    if len(s) >= 2 and s.startswith("`") and s.endswith("`"):
        s = s[1:-1].strip()
    # 移除外層成對引號 (如 "coupled" -> coupled)
    if len(s) >= 2 and ((s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'"))):
        s = s[1:-1].strip()
    return s


def compare_scalar(
    expected: str,
    actual: str,
    strict: bool = False
) -> Tuple[bool, str, str]:
    """
    確定性標量比對核心邏輯
    回傳: (passed, match_type, evidence)
    """
    exp_clean = clean_scalar_token(expected)
    act_clean = clean_scalar_token(actual)

    if not act_clean and act_clean != "0":
        return False, "MISSING", f"候選答案為空，期望值為: '{exp_clean}'"

    # 1. 嚴格直接字串比對 (Direct String Comparison)
    if exp_clean == act_clean:
        return True, "EXACT", f"精確字串匹配: '{act_clean}' == '{exp_clean}'"

    if strict:
        return False, "MISMATCH", f"嚴格模式不匹配: 實際值 '{act_clean}' != 期望值 '{exp_clean}'"

    # 2. 大小寫不敏感比對 (Case-Insensitive String Comparison)
    if exp_clean.casefold() == act_clean.casefold():
        return True, "CASE_INSENSITIVE", f"大小寫不敏感匹配: '{act_clean}' =~ '{exp_clean}'"

    # 3. 數值標量比對 (Numeric Scalar Comparison)
    try:
        exp_num = float(exp_clean)
        act_num = float(act_clean)
        if math.isclose(exp_num, act_num, rel_tol=1e-7, abs_tol=1e-7):
            return True, "NUMERIC", f"數值等價匹配: {act_num} == {exp_num}"
    except (ValueError, TypeError):
        pass

    return False, "MISMATCH", f"標量比對不符合: 實際值 '{act_clean}' != 期望值 '{exp_clean}'"


def load_evaluation_xml(xml_path: Path) -> Tuple[str, List[EvaluationItem]]:
    """
    解析評估 XML 檔案
    """
    if not xml_path.exists():
        raise FileNotFoundError(f"找不到評估 XML 檔案: {xml_path}")

    tree = ET.parse(str(xml_path))
    root = tree.getroot()
    suite_name = root.attrib.get("name", "ansys_mcp_eval")

    items: List[EvaluationItem] = []
    for idx, qa in enumerate(root.findall("qa_pair"), start=1):
        item_id = qa.attrib.get("id", str(idx))
        domain = qa.attrib.get("domain", f"Domain_{idx}")
        
        q_elem = qa.find("question")
        a_elem = qa.find("answer")

        question = q_elem.text.strip() if (q_elem is not None and q_elem.text) else ""
        answer = a_elem.text.strip() if (a_elem is not None and a_elem.text) else ""

        items.append(EvaluationItem(
            id=item_id,
            domain=domain,
            question=question,
            expected=answer
        ))

    return suite_name, items


def load_candidate_answers(answers_path: Optional[Path]) -> Optional[Dict[str, str]]:
    """
    載入候選答案檔（支援 JSON）
    支援格式：
    1. {"1": "2", "2": "coupled", ...}
    2. {"Structural": "2", "Fluids": "coupled", ...}
    3. [{"id": "1", "answer": "2"}, ...]
    4. ["2", "coupled", "1", ...]
    """
    if answers_path is None:
        return None

    if not answers_path.exists():
        raise FileNotFoundError(f"找不到候選答案檔案: {answers_path}")

    content = answers_path.read_text(encoding="utf-8")
    data = json.loads(content)

    answers_map: Dict[str, str] = {}
    if isinstance(data, dict):
        for k, v in data.items():
            answers_map[str(k).strip()] = str(v).strip()
    elif isinstance(data, list):
        for idx, item in enumerate(data, start=1):
            if isinstance(item, dict):
                ans_id = str(item.get("id", idx)).strip()
                ans_val = str(item.get("answer", item.get("actual", ""))).strip()
                answers_map[ans_id] = ans_val
                if "domain" in item:
                    answers_map[str(item["domain"]).strip()] = ans_val
            else:
                answers_map[str(idx)] = str(item).strip()
    return answers_map


def run_evaluation(
    xml_path: Path,
    candidate_answers: Optional[Dict[str, str]] = None,
    strict: bool = False,
    self_test: bool = False
) -> EvaluationSummary:
    """
    執行確定性標量評估
    """
    t_start = time.perf_counter()
    suite_name, items = load_evaluation_xml(xml_path)

    results: List[ComparisonResult] = []
    latencies: List[float] = []

    for item in items:
        item_t0 = time.perf_counter()

        # 決定實際答案
        if self_test or candidate_answers is None:
            # 自檢基準模式：使用期望答案進行自閉環驗證
            actual_val = item.expected
        else:
            # 從 candidate_answers 中尋找 (優先依據 id，其次 domain)
            actual_val = candidate_answers.get(item.id, candidate_answers.get(item.domain, ""))

        passed, match_type, evidence = compare_scalar(item.expected, actual_val, strict=strict)
        item_latency_ms = (time.perf_counter() - item_t0) * 1000.0
        latencies.append(item_latency_ms)

        results.append(ComparisonResult(
            id=item.id,
            domain=item.domain,
            question=item.question,
            expected=item.expected,
            actual=actual_val,
            passed=passed,
            match_type=match_type,
            latency_ms=round(item_latency_ms, 4),
            evidence=evidence
        ))

    total_duration_ms = (time.perf_counter() - t_start) * 1000.0
    passed_count = sum(1 for r in results if r.passed)
    total_count = len(results)
    pass_rate = (passed_count / total_count * 100.0) if total_count > 0 else 0.0
    avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0

    return EvaluationSummary(
        suite_name=suite_name,
        xml_path=str(xml_path.resolve()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        total_questions=total_count,
        passed_questions=passed_count,
        failed_questions=total_count - passed_count,
        pass_rate_pct=round(pass_rate, 2),
        average_latency_ms=round(avg_latency, 4),
        total_duration_ms=round(total_duration_ms, 2),
        strict_mode=strict,
        results=results
    )


def format_table(summary: EvaluationSummary, verbose: bool = False) -> str:
    """
    格式化評估終端輸出報表
    """
    lines = []
    lines.append("=" * 88)
    lines.append(f"  ANSYS UNIFIED MCP - DETERMINISTIC SCALAR EVALUATION SUITE")
    lines.append(f"  Specification: mcp-builder Phase 4 | Suite: {summary.suite_name}")
    lines.append(f"  XML File: {summary.xml_path}")
    lines.append(f"  Timestamp: {summary.timestamp}")
    lines.append("=" * 88)

    # 標頭
    header = f"{'ID':<4} | {'Domain':<16} | {'Status':<6} | {'Match':<16} | {'Expected':<18} | {'Actual':<18} | {'Latency':<8}"
    lines.append(header)
    lines.append("-" * 88)

    for r in summary.results:
        status_str = "PASS" if r.passed else "FAIL"
        exp_disp = (r.expected[:15] + "...") if len(r.expected) > 18 else r.expected
        act_disp = (r.actual[:15] + "...") if len(r.actual) > 18 else r.actual
        row = f"{r.id:<4} | {r.domain:<16} | {status_str:<6} | {r.match_type:<16} | {exp_disp:<18} | {act_disp:<18} | {r.latency_ms:6.3f}ms"
        lines.append(row)
        if verbose:
            lines.append(f"     [Evidence] {r.evidence}")
            lines.append(f"     [Question] {r.question}")
            lines.append("-" * 88)

    if not verbose:
        lines.append("-" * 88)

    # 統計指標
    lines.append("【標準化評估指標 (Standardized Evaluation Metrics)】")
    lines.append(f"  - 總題數 (Total Questions)        : {summary.total_questions}")
    lines.append(f"  - 通過題數 (Passed Questions)     : {summary.passed_questions}")
    lines.append(f"  - 失敗題數 (Failed Questions)     : {summary.failed_questions}")
    lines.append(f"  - 通過率 (Pass Rate)              : {summary.pass_rate_pct:.1f}%")
    lines.append(f"  - 平均判定延遲 (Average Latency)  : {summary.average_latency_ms:.4f} ms")
    lines.append(f"  - 總執行耗時 (Total Duration)     : {summary.total_duration_ms:.2f} ms")
    lines.append(f"  - 嚴格比對模式 (Strict Mode)      : {summary.strict_mode}")
    lines.append(f"  - 評測保證 (Evaluation Guarantee) : 100% Deterministic (Zero LLM-as-a-Judge Dependency)")
    lines.append("=" * 88)

    return "\n".join(lines)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ANSYS Unified MCP - Phase 4 確定性標量評估執行器 (Deterministic Scalar Evaluation Runner)"
    )
    # 預設路徑定位
    script_dir = Path(__file__).resolve().parent
    default_xml = script_dir / "ansys_mcp_eval.xml"

    parser.add_argument(
        "--xml",
        type=Path,
        default=default_xml,
        help=f"評估 XML 檔案路徑 (預設: {default_xml})"
    )
    parser.add_argument(
        "--answers",
        type=Path,
        default=None,
        help="候選答案 JSON 檔案路徑 (若未提供則預設執行基準自檢評測)"
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=None,
        help="將評估結果指標輸出為 JSON 檔案的路徑"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="強制嚴格直接字串精確比對（停用大小寫不敏感與數值容差）"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="啟用詳細輸出（顯示每題題目內文與比對客觀證據）"
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="執行黃金基準自檢（驗證評估套件完整性與解析正確性）"
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    try:
        candidate_answers = load_candidate_answers(args.answers) if args.answers else None
        summary = run_evaluation(
            xml_path=args.xml,
            candidate_answers=candidate_answers,
            strict=args.strict,
            self_test=args.self_test or (candidate_answers is None)
        )

        # 輸出終端報表
        print(format_table(summary, verbose=args.verbose))

        # 匯出 JSON 報表
        if args.json_output:
            args.json_output.parent.mkdir(parents=True, exist_ok=True)
            args.json_output.write_text(
                json.dumps(summary.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            print(f"[INFO] 評估指標 JSON 已輸出至: {args.json_output.resolve()}")

        # 退出碼：通過率 100% 回傳 0，否則回傳 1
        return 0 if summary.pass_rate_pct == 100.0 else 1

    except Exception as exc:
        print(f"[ERROR] 評估套件執行失敗: {exc}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
