#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模組名稱：aggregate_benchmark.py
功能說明：Stage 1 基準聚合器 (Benchmark Aggregator)。
          掃描 `agents/skills-workspace/<skill>-workspace/iteration-<N>/`，
          匯總各 eval run 的 timing.json 與 grading.json，
          計算 Pass Rate 提升量、平均延遲、Token 消耗變化與觸發混淆矩陣，
          輸出標準化 benchmark.json 與 Markdown 摘要表 benchmark.md。
          支援 `-X utf8` 與 Windows UTF-8 執行環境。
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
from pathlib import Path
import re
import sys
from typing import Any


def safe_load_json(file_path: Path) -> dict[str, Any]:
    """安全載入 JSON 檔案，失敗時回傳空字典"""
    if not file_path.is_file():
        return {}
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] 警告：無法解析 JSON 檔案 {file_path}: {e}", file=sys.stderr)
        return {}


def scan_iteration_evals(iteration_dir: Path) -> list[dict[str, Any]]:
    """掃描特定 iteration 目錄下的所有 eval-* 子目錄"""
    eval_dirs = [
        d for d in iteration_dir.iterdir()
        if d.is_dir() and re.match(r"^eval-\d+$", d.name)
    ]

    # 依照 eval ID 數值排序
    eval_dirs.sort(key=lambda p: int(p.name.split("-")[1]))

    records: list[dict[str, Any]] = []

    for edir in eval_dirs:
        eval_id = int(edir.name.split("-")[1])

        with_timing = safe_load_json(edir / "with_skill" / "timing.json")
        with_grading = safe_load_json(edir / "with_skill" / "grading.json")

        without_timing = safe_load_json(edir / "without_skill" / "timing.json")
        without_grading = safe_load_json(edir / "without_skill" / "grading.json")

        with_passed = bool(with_grading.get("passed", False))
        without_passed = bool(without_grading.get("passed", False))

        with_duration = float(with_timing.get("duration_ms", 0.0))
        without_duration = float(without_timing.get("duration_ms", 0.0))

        with_tokens = with_timing.get("tokens", {})
        without_tokens = without_timing.get("tokens", {})

        with_total_tok = int(with_tokens.get("total_tokens", 0))
        without_total_tok = int(without_tokens.get("total_tokens", 0))

        if with_passed and not without_passed:
            status = "IMPROVED"
        elif not with_passed and without_passed:
            status = "REGRESSED"
        elif with_passed and without_passed:
            status = "UNCHANGED_PASS"
        else:
            status = "UNCHANGED_FAIL"

        records.append({
            "eval_id": eval_id,
            "status": status,
            "with_skill": {
                "passed": with_passed,
                "score": float(with_grading.get("score", 1.0 if with_passed else 0.0)),
                "duration_ms": with_duration,
                "tokens": with_tokens,
                "evidence": with_grading.get("evidence", ""),
            },
            "without_skill": {
                "passed": without_passed,
                "score": float(without_grading.get("score", 1.0 if without_passed else 0.0)),
                "duration_ms": without_duration,
                "tokens": without_tokens,
                "evidence": without_grading.get("evidence", ""),
            },
        })

    return records


def calculate_metrics(eval_records: list[dict[str, Any]]) -> dict[str, Any]:
    """計算整批評測的聚合統計指標"""
    total = len(eval_records)
    if total == 0:
        return {
            "total_evals": 0,
            "with_skill": {"pass_count": 0, "pass_rate": 0.0, "avg_duration_ms": 0.0, "avg_tokens": {}},
            "without_skill": {"pass_count": 0, "pass_rate": 0.0, "avg_duration_ms": 0.0, "avg_tokens": {}},
            "delta": {"pass_rate_gain": 0.0, "duration_delta_ms": 0.0, "token_overhead": 0},
        }

    with_pass_count = sum(1 for r in eval_records if r["with_skill"]["passed"])
    without_pass_count = sum(1 for r in eval_records if r["without_skill"]["passed"])

    with_pass_rate = with_pass_count / total
    without_pass_rate = without_pass_count / total
    pass_rate_gain = with_pass_rate - without_pass_rate

    avg_dur_with = sum(r["with_skill"]["duration_ms"] for r in eval_records) / total
    avg_dur_without = sum(r["without_skill"]["duration_ms"] for r in eval_records) / total

    def avg_tok_dict(key: str) -> dict[str, int]:
        p = sum(int(r[key]["tokens"].get("prompt_tokens", 0)) for r in eval_records) // total
        c = sum(int(r[key]["tokens"].get("completion_tokens", 0)) for r in eval_records) // total
        t = sum(int(r[key]["tokens"].get("total_tokens", 0)) for r in eval_records) // total
        return {"prompt_tokens": p, "completion_tokens": c, "total_tokens": t}

    avg_tok_with = avg_tok_dict("with_skill")
    avg_tok_without = avg_tok_dict("without_skill")

    return {
        "total_evals": total,
        "with_skill": {
            "pass_count": with_pass_count,
            "pass_rate": round(with_pass_rate, 4),
            "avg_duration_ms": round(avg_dur_with, 2),
            "avg_tokens": avg_tok_with,
        },
        "without_skill": {
            "pass_count": without_pass_count,
            "pass_rate": round(without_pass_rate, 4),
            "avg_duration_ms": round(avg_dur_without, 2),
            "avg_tokens": avg_tok_without,
        },
        "delta": {
            "pass_rate_gain": round(pass_rate_gain, 4),
            "duration_delta_ms": round(avg_dur_with - avg_dur_without, 2),
            "token_overhead": avg_tok_with["total_tokens"] - avg_tok_without["total_tokens"],
        },
    }


def generate_markdown_report(
    skill_name: str,
    iteration: int,
    metrics: dict[str, Any],
    eval_records: list[dict[str, Any]],
    trigger_eval: dict[str, Any] | None = None,
) -> str:
    """生成 Markdown 格式的標準化 Benchmark 報告"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    w = metrics["with_skill"]
    wo = metrics["without_skill"]
    d = metrics["delta"]

    gain_sign = "+" if d["pass_rate_gain"] >= 0 else ""
    gain_pct = f"{gain_sign}{d['pass_rate_gain'] * 100:.1f}%"

    lines = [
        f"# 技能基準評測報告 (Skill Benchmark Report): `{skill_name}`",
        "",
        f"- **評測輪次 (Iteration)**: iteration-{iteration}",
        f"- **評測時間 (Timestamp)**: {timestamp}",
        f"- **總案例數 (Total Cases)**: {metrics['total_evals']}",
        "",
        "---",
        "",
        "## 一、核心效能指標摘要 (Executive Summary)",
        "",
        "| 指標項目 (Metric) | 啟用技能 (With Skill) | 未啟用技能 (Without Skill) | 差異 (Delta) |",
        "| :--- | :---: | :---: | :---: |",
        f"| **通過率 (Pass Rate)** | **{w['pass_rate'] * 100:.1f}%** ({w['pass_count']}/{metrics['total_evals']}) | {wo['pass_rate'] * 100:.1f}% ({wo['pass_count']}/{metrics['total_evals']}) | **{gain_pct}** |",
        f"| **平均耗時 (Avg Duration)** | {w['avg_duration_ms']:.1f} ms | {wo['avg_duration_ms']:.1f} ms | {d['duration_delta_ms']:+.1f} ms |",
        f"| **平均 Token 消耗** | {w['avg_tokens'].get('total_tokens', 0):,} toks | {wo['avg_tokens'].get('total_tokens', 0):,} toks | {d['token_overhead']:+,} toks |",
        "",
    ]

    # 若有觸發率混淆矩陣
    if trigger_eval and "matrix" in trigger_eval:
        m = trigger_eval["matrix"]
        lines.extend([
            "## 二、首輪路由觸發率混淆矩陣 (Trigger Confusion Matrix)",
            "",
            f"測試總題數：{trigger_eval.get('queries_count', m.get('total', 20))} 題（10 正向 + 10 相鄰干擾題）",
            "",
            "| 預測 \\ 實際 | 實際正向 (Should Trigger) | 實際干擾 (Should Not Trigger) | 指標 (Metrics) |",
            "| :--- | :---: | :---: | :--- |",
            f"| **預測觸發 (Selected)** | **TP = {m.get('tp', 0)}** | **FP = {m.get('fp', 0)}** | **Precision**: {m.get('precision', 0.0) * 100:.1f}% |",
            f"| **預測略過 (Skipped)** | **FN = {m.get('fn', 0)}** | **TN = {m.get('tn', 0)}** | **Recall**: {m.get('recall', 0.0) * 100:.1f}% |",
            f"| **統計合計** | {m.get('tp', 0) + m.get('fn', 0)} 題 | {m.get('fp', 0) + m.get('tn', 0)} 題 | **FPR**: {m.get('fpr', 0.0) * 100:.1f}% / **Acc**: {m.get('accuracy', 0.0) * 100:.1f}% |",
            "",
        ])

    # 各案例明細清單
    lines.extend([
        "## 三、單一測試案例詳細比對 (Case Breakdown)",
        "",
        "| Case ID | 狀態 (Status) | With Skill 通過 | Without Skill 通過 | 耗時 (With/Without) | Token 消耗 |",
        "| :---: | :---: | :---: | :---: | :---: | :---: |",
    ])

    status_icon_map = {
        "IMPROVED": "🟢 顯著提升 (Improved)",
        "REGRESSED": "🔴 發生回退 (Regressed)",
        "UNCHANGED_PASS": "⚪ 均通過 (Both Pass)",
        "UNCHANGED_FAIL": "⚠️ 均未通過 (Both Fail)",
    }

    for r in eval_records:
        eid = r["eval_id"]
        stat = status_icon_map.get(r["status"], r["status"])
        w_p = "✅ PASS" if r["with_skill"]["passed"] else "❌ FAIL"
        wo_p = "✅ PASS" if r["without_skill"]["passed"] else "❌ FAIL"
        dur = f"{r['with_skill']['duration_ms']:.0f}ms / {r['without_skill']['duration_ms']:.0f}ms"
        tok = f"{r['with_skill']['tokens'].get('total_tokens', 0)} / {r['without_skill']['tokens'].get('total_tokens', 0)}"

        lines.append(f"| eval-{eid} | {stat} | {w_p} | {wo_p} | {dur} | {tok} |")

    lines.extend([
        "",
        "---",
        "*自動生成於 Stage 1 Headless Skill Evaluator & Benchmark Aggregator 工具鏈*",
    ])

    return "\n".join(lines)


def aggregate_iteration(iteration_dir: Path) -> dict[str, Any]:
    """
    對指定 iteration 目錄執行聚合：
    1. 讀取所有 eval-* 目錄
    2. 讀取 trigger_eval.json（若存在）
    3. 計算各項指標
    4. 輸出 benchmark.json 與 benchmark.md
    """
    iteration_dir = iteration_dir.resolve()
    if not iteration_dir.is_dir():
        raise FileNotFoundError(f"找不到指定的迭代目錄：{iteration_dir}")

    # 解析技能名稱與 iteration 編號
    iter_name = iteration_dir.name
    iter_num = int(iter_name.split("-")[1]) if "-" in iter_name else 1

    workspace_dir = iteration_dir.parent
    skill_name = workspace_dir.name.replace("-workspace", "")

    eval_records = scan_iteration_evals(iteration_dir)
    metrics = calculate_metrics(eval_records)

    trigger_file = iteration_dir / "trigger_eval.json"
    trigger_eval = safe_load_json(trigger_file) if trigger_file.is_file() else None

    report_data = {
        "skill": skill_name,
        "iteration": iter_num,
        "timestamp": datetime.datetime.now().isoformat(),
        "summary": metrics,
        "trigger_evaluation": trigger_eval,
        "evaluations": eval_records,
    }

    # 輸出 benchmark.json
    json_path = iteration_dir / "benchmark.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    # 輸出 benchmark.md
    md_content = generate_markdown_report(
        skill_name=skill_name,
        iteration=iter_num,
        metrics=metrics,
        eval_records=eval_records,
        trigger_eval=trigger_eval,
    )
    md_path = iteration_dir / "benchmark.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return report_data


def find_latest_iteration(workspace_dir: Path) -> Path | None:
    """自動尋找 workspace 下編號最新的 iteration-* 目錄"""
    if not workspace_dir.is_dir():
        return None

    iter_dirs = [
        d for d in workspace_dir.iterdir()
        if d.is_dir() and re.match(r"^iteration-\d+$", d.name)
    ]
    if not iter_dirs:
        return None

    iter_dirs.sort(key=lambda d: int(d.name.split("-")[1]))
    return iter_dirs[-1]


def main() -> int:
    """CLI 聚合工具進入點"""
    parser = argparse.ArgumentParser(
        description="Aggregate Stage 1 Skill Benchmark Results"
    )
    parser.add_argument(
        "--iteration-dir",
        default=None,
        help="指定 iteration 目錄 (如 agents/skills-workspace/ansys-ls-prepost-workspace/iteration-1)",
    )
    parser.add_argument(
        "--workspace",
        default=None,
        help="指定單一技能 workspace (自動聚合最新 iteration)",
    )
    parser.add_argument(
        "--skills-workspace-root",
        default=None,
        help="全域 skills-workspace 根目錄 (批次掃描所有技能 workspace)",
    )

    args = parser.parse_args()

    # 1. 直接指定 iteration 目錄
    if args.iteration_dir:
        target_dir = Path(args.iteration_dir)
        print(f"[*] 正在聚合迭代基準：{target_dir}")
        res = aggregate_iteration(target_dir)
        d = res["summary"]["delta"]
        gain_sign = "+" if d["pass_rate_gain"] >= 0 else ""
        print(
            f"[+] 聚合完成！通過率提升：{gain_sign}{d['pass_rate_gain'] * 100:.1f}%, "
            f"平均延遲變化：{d['duration_delta_ms']:+.1f} ms"
        )
        print(f"    - JSON: {target_dir / 'benchmark.json'}")
        print(f"    - Markdown: {target_dir / 'benchmark.md'}")
        return 0

    # 2. 指定單一技能 workspace
    if args.workspace:
        ws_dir = Path(args.workspace)
        latest_iter = find_latest_iteration(ws_dir)
        if not latest_iter:
            print(f"[!] 錯誤：在 {ws_dir} 下未發現任何 iteration-* 目錄", file=sys.stderr)
            return 1
        print(f"[*] 在 {ws_dir.name} 中定位到最新迭代：{latest_iter.name}")
        aggregate_iteration(latest_iter)
        return 0

    # 3. 掃描專案預設 skills-workspace
    repo_root = Path(__file__).resolve().parents[2]
    root_dir = Path(args.skills_workspace_root) if args.skills_workspace_root else (repo_root / "agents" / "skills-workspace")

    if not root_dir.is_dir():
        print(f"[!] 目錄不存在：{root_dir}", file=sys.stderr)
        return 1

    workspace_dirs = [d for d in root_dir.iterdir() if d.is_dir() and d.name.endswith("-workspace")]
    if not workspace_dirs:
        print(f"[*] 在 {root_dir} 下未發現任何 *-workspace 目錄。")
        return 0

    print(f"[*] 掃描到 {len(workspace_dirs)} 個技能工作區，開始批次聚合...")
    for ws in workspace_dirs:
        latest = find_latest_iteration(ws)
        if latest:
            try:
                res = aggregate_iteration(latest)
                gain = res["summary"]["delta"]["pass_rate_gain"]
                print(f"  - [{ws.name}] {latest.name}: Pass Rate Gain = {gain * 100:+.1f}%")
            except Exception as e:
                print(f"  - [!] [{ws.name}] 聚合失敗: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    if sys.stdout.encoding.lower() != "utf-8" and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
