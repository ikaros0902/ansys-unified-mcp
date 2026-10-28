#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模組名稱：headless_skill_evaluator.py
功能說明：Stage 1 跨平台 Headless 技能評測與 A/B 對照基準引擎。
          擺脫原生 skill-creator 對 `claude -p` 與 `.claude/commands/` 的硬依賴。

核心架構：
  1. 跨平台適配器架構 (Adapter Architecture)：
     - KiroCLIAdapter：透過 `kiro-cli.exe --no-interactive -a` 派發評測提示詞。
     - GeminiSDKAdapter：透過 `google-genai` SDK 或原生 REST API 派發。
     - DeterministicMockAdapter：用於無外網/離線 CI 快速驗證評測邏輯與 Assertions 解析。
  2. 觸發率混淆矩陣判定引擎 (Trigger Judgement Engine)：
     - 直接將候選技能的 Frontmatter (`name` + `description`) 注入 System Prompt。
     - 提供 20 題測試 Query（10 正向 + 10 相鄰干擾題），解析首輪決策中的技能選取。
     - 輸出混淆矩陣：Precision, Recall, False Positive Rate (FPR), Accuracy。
  3. Windows UTF-8 與安全臨時目錄：
     - 所有 Subprocess 強制宣告 `encoding="utf-8", errors="replace"`。
     - 臨時檔案使用 `tempfile.gettempdir()`，禁止硬編碼 `/tmp`。
  4. A/B 評測輸出：
     - 依據 `evals.json` 執行 `with_skill` 與 `without_skill`。
     - 記錄 `timing.json` (duration_ms, tokens) 與 `grading.json` (passed, text, evidence)。
"""

from __future__ import annotations

import argparse
import dataclasses
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable
import uuid


# ==============================================================================
# 一、資料型別與結構定義
# ==============================================================================

@dataclass
class SkillMetadata:
    """技能詮釋資料結構"""
    name: str
    description: str
    raw_frontmatter: dict[str, Any]
    body: str
    skill_dir: Path
    skill_md_path: Path


@dataclass
class LLMTokenUsage:
    """Token 消耗記錄"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass
class LLMResponse:
    """LLM 呼叫回傳結果"""
    text: str
    duration_ms: float
    tokens: LLMTokenUsage
    model: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TriggerQuery:
    """觸發率評測單一題目"""
    query_id: int
    query: str
    expected_trigger: bool
    category: str = "positive"  # "positive" 或 "adjacent_distractor"


@dataclass
class TriggerQueryResult:
    """單題觸發率判定結果"""
    query_id: int
    query: str
    expected_trigger: bool
    predicted_trigger: bool
    selected_skill: str | None
    confidence: float
    reasoning: str
    classification: str  # "TP", "FP", "TN", "FN"


@dataclass
class ConfusionMatrix:
    """混淆矩陣統計指標"""
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0
    precision: float = 0.0
    recall: float = 0.0
    fpr: float = 0.0
    accuracy: float = 0.0
    total: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "tp": self.tp,
            "fp": self.fp,
            "tn": self.tn,
            "fn": self.fn,
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "fpr": round(self.fpr, 4),
            "accuracy": round(self.accuracy, 4),
            "total": self.total,
        }


@dataclass
class TriggerEvaluationResult:
    """完整觸發率評估結果"""
    skill_name: str
    queries_count: int
    matrix: ConfusionMatrix
    results: list[TriggerQueryResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "queries_count": self.queries_count,
            "matrix": self.matrix.to_dict(),
            "results": [dataclasses.asdict(r) for r in self.results],
        }


@dataclass
class AssertionResult:
    """單一斷言檢查結果"""
    assertion: str
    passed: bool
    evidence: str


@dataclass
class GradingResult:
    """評分結果"""
    passed: bool
    score: float
    evidence: str
    text: str
    assertions: list[AssertionResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "score": round(self.score, 4),
            "evidence": self.evidence,
            "text": self.text,
            "assertions": [dataclasses.asdict(a) for a in self.assertions],
        }


# ==============================================================================
# 二、YAML Frontmatter 解析與技能發現
# ==============================================================================

def parse_frontmatter_yaml(content: str) -> tuple[dict[str, Any], str]:
    """
    自訂精簡 YAML Frontmatter 解析器，不依賴外部 pyyaml 套件。
    支援 --- 區隔之 key-value，並保留其餘主體文字。
    """
    frontmatter: dict[str, Any] = {}
    if not content.startswith("---"):
        return frontmatter, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return frontmatter, content

    yaml_block = parts[1]
    body = parts[2].lstrip("\r\n")

    current_key: str | None = None
    multiline_buf: list[str] = []

    for line in yaml_block.splitlines():
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith("#"):
            continue

        # 檢查 key: value
        match = re.match(r"^([a-zA-Z0-9_-]+)\s*:\s*(.*)$", line)
        if match:
            if current_key and multiline_buf:
                frontmatter[current_key] = " ".join(multiline_buf).strip().strip('"\'')
                multiline_buf = []

            key, val = match.groups()
            current_key = key
            val = val.strip()
            if val.startswith(('"', "'")) and val.endswith(('"', "'")) and len(val) >= 2:
                frontmatter[key] = val[1:-1]
            elif val in (">", "|", ">-", "|-"):
                multiline_buf = []
            elif val.lower() == "true":
                frontmatter[key] = True
            elif val.lower() == "false":
                frontmatter[key] = False
            elif val:
                frontmatter[key] = val
        elif current_key and line.startswith(("  ", "\t")):
            multiline_buf.append(line_stripped)

    if current_key and multiline_buf:
        frontmatter[current_key] = " ".join(multiline_buf).strip().strip('"\'')

    return frontmatter, body


def parse_skill_markdown(skill_md_path: Path) -> SkillMetadata:
    """讀取並解析 SKILL.md 之 Frontmatter 與主文"""
    if not skill_md_path.is_file():
        raise FileNotFoundError(f"找不到技能定義檔案：{skill_md_path}")

    raw_text = skill_md_path.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = parse_frontmatter_yaml(raw_text)

    name = str(frontmatter.get("name", skill_md_path.parent.name))
    description = str(frontmatter.get("description", ""))

    return SkillMetadata(
        name=name,
        description=description,
        raw_frontmatter=frontmatter,
        body=body,
        skill_dir=skill_md_path.parent,
        skill_md_path=skill_md_path,
    )


def find_skill_directory(skill_target: str | Path, repo_root: Path | None = None) -> Path:
    """
    智能解析技能目錄位置：
    支援直接傳入目錄、SKILL.md 路徑或純名稱（技能集中於 agents/skills/；舊 Tier-2 路徑會映射到新位置）。
    """
    path_obj = Path(skill_target)
    if path_obj.is_file() and path_obj.name == "SKILL.md":
        return path_obj.parent
    if path_obj.is_dir() and (path_obj / "SKILL.md").is_file():
        return path_obj

    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]

    skill_root = repo_root / "agents" / "skills"
    legacy_root = repo_root / "agents" / "skills-tier2"
    requested_path = path_obj if path_obj.is_absolute() else repo_root / path_obj
    try:
        legacy_relative = requested_path.resolve().relative_to(legacy_root.resolve())
    except ValueError:
        legacy_relative = None
    if legacy_relative is not None:
        migrated = skill_root / legacy_relative
        if migrated.is_file() and migrated.name == "SKILL.md":
            return migrated.parent
        if migrated.is_dir() and (migrated / "SKILL.md").is_file():
            return migrated

    candidate_roots = [
        skill_root,
        repo_root / ".kiro" / "skills",
        repo_root / ".agents" / "skills",
        repo_root / ".cline" / "skills",
    ]

    skill_name = legacy_relative.parts[0] if legacy_relative else Path(str(skill_target).strip("/\\\\")).name
    for root in candidate_roots:
        target = root / skill_name
        if target.is_dir() and (target / "SKILL.md").is_file():
            return target
        if root.is_dir():
            matches = [path.parent for path in root.rglob("SKILL.md") if path.parent.name == skill_name]
            if len(matches) == 1:
                return matches[0]

    raise FileNotFoundError(f"無法在專案候選目錄中定位技能：'{skill_target}'")


# ==============================================================================
# 三、跨平台適配器架構 (Adapter Architecture)
# ==============================================================================

class BaseLLMAdapter:
    """LLM 派發適配器基礎抽象類別"""

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        raise NotImplementedError


class DeterministicMockAdapter(BaseLLMAdapter):
    """
    用於離線 CI 與單元測試之確定性 Mock 適配器。
    可依據規則匹配或自訂回調函式產生預期輸出與 Token 數據。
    """

    def __init__(
        self,
        default_response: str = "Mock response",
        rules: dict[str, str] | None = None,
        custom_handler: Callable[[str, str], str | LLMResponse] | None = None,
        duration_ms: float = 50.0,
        tokens_per_call: LLMTokenUsage | None = None,
    ):
        self.default_response = default_response
        self.rules = rules or {}
        self.custom_handler = custom_handler
        self.duration_ms = duration_ms
        self.tokens_per_call = tokens_per_call or LLMTokenUsage(150, 80, 230)
        self.calls: list[dict[str, Any]] = []

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        self.calls.append({
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        })

        if self.custom_handler:
            result = self.custom_handler(system_prompt, user_prompt)
            if isinstance(result, LLMResponse):
                return result
            return LLMResponse(
                text=result,
                duration_ms=self.duration_ms,
                tokens=self.tokens_per_call,
                model="deterministic-mock",
            )

        # 優先搜尋 rules 正則匹配
        for pattern, response_text in self.rules.items():
            if re.search(pattern, user_prompt, re.IGNORECASE) or re.search(pattern, system_prompt, re.IGNORECASE):
                return LLMResponse(
                    text=response_text,
                    duration_ms=self.duration_ms,
                    tokens=self.tokens_per_call,
                    model="deterministic-mock",
                )

        # 智慧啟發式響應（針對觸發判決與斷言評分）
        if "Determine whether the user's request should trigger" in system_prompt or '"selected":' in system_prompt:
            # 檢查是否為正向標記
            is_positive = (
                "[POSITIVE]" in user_prompt
                or "撞擊" in user_prompt
                or "d3plot" in user_prompt
                or "ls-prepost" in user_prompt.lower()
                or "mesh" in user_prompt.lower()
            )
            selected_val = "true" if is_positive else "false"
            selected_skill = '"candidate_skill"' if is_positive else "null"
            reason = "Matches skill domain criteria" if is_positive else "Not related to candidate skill"
            json_text = f'{{"selected": {selected_val}, "selected_skill": {selected_skill}, "confidence": 0.95, "reasoning": "{reason}"}}'
            return LLMResponse(
                text=json_text,
                duration_ms=self.duration_ms,
                tokens=self.tokens_per_call,
                model="deterministic-mock",
            )

        if "Does the candidate answer satisfy this assertion" in system_prompt or '"passed":' in system_prompt:
            # 斷言評分判決
            json_text = '{"passed": true, "evidence": "Verified condition against response."}'
            return LLMResponse(
                text=json_text,
                duration_ms=self.duration_ms,
                tokens=self.tokens_per_call,
                model="deterministic-mock",
            )

        return LLMResponse(
            text=self.default_response,
            duration_ms=self.duration_ms,
            tokens=self.tokens_per_call,
            model="deterministic-mock",
        )


class KiroCLIAdapter(BaseLLMAdapter):
    """
    透過本機 `kiro-cli.exe` 非互動命令列派發評測提示詞。
    使用安全臨時檔案與 Windows UTF-8 編碼保證。
    """

    def __init__(
        self,
        cli_path: str | None = None,
        model: str = "claude-sonnet-5",
        effort: str = "medium",
        timeout: float = 120.0,
    ):
        self.cli_path = cli_path or os.getenv("KIRO_CLI_PATH", "kiro-cli.exe")
        self.model = model
        self.effort = effort
        self.timeout = timeout

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        # 整合提示詞，使用 safe tempfile 避免 Windows 命令列長度限制 (8191 字符)
        temp_dir = Path(tempfile.gettempdir())
        session_id = uuid.uuid4().hex[:8]
        prompt_file = temp_dir / f"kiro_eval_prompt_{session_id}.txt"

        combined_prompt = (
            f"[SYSTEM INSTRUCTION]\n{system_prompt}\n\n"
            f"[USER QUERY]\n{user_prompt}\n"
        )

        try:
            prompt_file.write_text(combined_prompt, encoding="utf-8", errors="replace")

            # 依據全域 50-kiro-cli-dispatch.md 構建非互動命令
            cmd = [
                self.cli_path,
                "chat",
                "--no-interactive",
                "-a",
                "--model", self.model,
                "--effort", self.effort,
            ]

            start_t = time.perf_counter()
            # 透過 stdin 傳遞提示詞內容或作為引數
            process = subprocess.run(
                cmd,
                input=combined_prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout,
            )
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0

            if process.returncode != 0:
                err_snippet = (process.stderr or process.stdout or "Unknown error").strip()
                raise RuntimeError(
                    f"Kiro CLI 執行異常 (Exit {process.returncode}): {err_snippet[:300]}"
                )

            stdout_text = process.stdout.strip()
            # 粗估 Token 消耗（1 詞 ~ 1.3 token，或依字符數粗估）
            prompt_toks = max(1, len(combined_prompt) // 4)
            completion_toks = max(1, len(stdout_text) // 4)

            return LLMResponse(
                text=stdout_text,
                duration_ms=round(elapsed_ms, 2),
                tokens=LLMTokenUsage(prompt_toks, completion_toks, prompt_toks + completion_toks),
                model=self.model,
                metadata={"cli_path": self.cli_path, "exit_code": process.returncode},
            )
        finally:
            if prompt_file.exists():
                try:
                    prompt_file.unlink()
                except OSError:
                    pass


class GeminiSDKAdapter(BaseLLMAdapter):
    """
    透過 Google Gemini API 派發。
    優先嘗試 `google-genai` SDK，若未安裝則平滑降級至標準庫 HTTP 呼叫。
    """

    def __init__(
        self,
        model: str = "gemini-3.8-flash",
        api_key: str | None = None,
        timeout: float = 60.0,
    ):
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.timeout = timeout

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        if not self.api_key:
            raise ValueError(
                "GeminiSDKAdapter 缺少 API 金鑰。請設定環境變數 GEMINI_API_KEY 或 GOOGLE_API_KEY。"
            )

        start_t = time.perf_counter()

        # 1. 嘗試使用 google.genai SDK
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            resp_text = response.text or ""

            usage = getattr(response, "usage_metadata", None)
            p_tok = getattr(usage, "prompt_token_count", len(system_prompt + user_prompt) // 4) if usage else 0
            c_tok = getattr(usage, "candidates_token_count", len(resp_text) // 4) if usage else 0

            return LLMResponse(
                text=resp_text,
                duration_ms=round(elapsed_ms, 2),
                tokens=LLMTokenUsage(p_tok, c_tok, p_tok + c_tok),
                model=self.model,
            )
        except ImportError:
            pass

        # 2. 降級使用標準庫 urllib.request 進行 REST 呼叫
        import urllib.request
        import urllib.error

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                elapsed_ms = (time.perf_counter() - start_t) * 1000.0
                body = resp.read().decode("utf-8", errors="replace")
                data = json.loads(body)

                candidates = data.get("candidates", [])
                text_out = ""
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    text_out = "".join(part.get("text", "") for part in parts)

                usage = data.get("usageMetadata", {})
                p_tok = usage.get("promptTokenCount", len(system_prompt + user_prompt) // 4)
                c_tok = usage.get("candidatesTokenCount", len(text_out) // 4)

                return LLMResponse(
                    text=text_out,
                    duration_ms=round(elapsed_ms, 2),
                    tokens=LLMTokenUsage(p_tok, c_tok, p_tok + c_tok),
                    model=self.model,
                )
        except urllib.error.URLError as e:
            raise RuntimeError(f"Gemini API 呼叫失敗：{e}")


# ==============================================================================
# 四、觸發率混淆矩陣判定引擎 (Trigger Judgement Engine)
# ==============================================================================

class TriggerJudgementEngine:
    """
    技能觸發率判定引擎。
    透過注入候選技能的 Frontmatter (`name` + `description`) 至系統提示詞，
    使用 20 題測試 Query（10 正向 + 10 相鄰干擾題），解析首輪決策並計算混淆矩陣。
    """

    def __init__(self, adapter: BaseLLMAdapter):
        self.adapter = adapter

    @staticmethod
    def extract_json_block(text: str) -> dict[str, Any]:
        """從 LLM 回傳文字中容錯抽取 JSON 區塊"""
        # 尋找 ```json ... ```
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        target_str = fence_match.group(1).strip() if fence_match else text.strip()

        # 嘗試直接解析
        try:
            return json.loads(target_str)
        except json.JSONDecodeError:
            pass

        # 嘗試正則截取第一個 { 到最後一個 }
        brace_match = re.search(r"(\{[\s\S]*\})", target_str)
        if brace_match:
            try:
                return json.loads(brace_match.group(1))
            except json.JSONDecodeError:
                pass

        return {}

    @classmethod
    def generate_default_20_queries(cls, skill: SkillMetadata) -> list[TriggerQuery]:
        """
        為候選技能自動合成 20 道標準觸發評測題目：
        - 10 道正向題 (category="positive", expected_trigger=True)
        - 10 道相鄰干擾題 (category="adjacent_distractor", expected_trigger=False)
        """
        name = skill.name
        desc = skill.description

        # 抽取描述中關鍵字提示
        kw_match = re.search(r"觸發關鍵字[^\:]*:\s*([^\n\r]+)", desc)
        keywords = [k.strip() for k in kw_match.group(1).split(",")] if kw_match else [name]

        positive_queries: list[str] = [
            f"請問如何使用 {keywords[0]} 進行自動化腳本撰寫？",
            f"在 {name} 流程中，該如何設定邊界條件與前處理參數？",
            f"如何排查 {name} 執行時發生的收斂失敗與語法異常？",
            f"請提供一段針對 {keywords[min(1, len(keywords)-1)]} 的標準範例程式碼。",
            f"我在進行結構模擬分析時需要使用 {name}，具體呼叫步驟是什麼？",
            f"請幫我依據官方規範檢查 {name} 的配置檔案是否完整合規。",
            f"如何透過 Python API 呼叫 {name} 並提取雲圖與物理結果數據？",
            f"遇到 {keywords[min(2, len(keywords)-1)]} 的典型報錯時，推薦的修復順序是什麼？",
            f"請撰寫一份 {name} 的自動化執行流程並加入錯誤診斷記錄。",
            f"需要將現有模型透過 {name} 進行批次前處理與網格更新，該怎麼做？",
        ]

        # 10 道相鄰領域但非該技能職責之干擾題
        distractor_queries: list[str] = [
            "請幫我寫一個 Python 爬蟲抓取公開天氣 API 的氣溫數據並存成 CSV。",
            "Git 合併衝突時出現 HEAD 與 main 分支不同步，該如何用命令列解決？",
            "如何在 Windows 建立一個定時執行的 PowerShell 自動備份排程？",
            "請解釋物件導向程式設計中的 SOLID 原則並給出 TypeScript 範例。",
            "如何優化 PostgreSQL 資料庫的 B-Tree 索引查詢效能？",
            "請使用 Docker Compose 部署一個 Nginx 搭配 FastAPI 的微服務後端。",
            "在 React 專案中，如何使用 Zustand 管理全域跨組件狀態？",
            "請比較 Markdown 與 LaTeX 在撰寫學術論文數學公式時的語法差異。",
            "我的 VS Code 終端機編碼顯示亂碼，該如何配置 settings.json 的 UTF-8？",
            "如何使用 pytest 的 fixture 與 parametrize 撰寫單元測試？",
        ]

        queries: list[TriggerQuery] = []
        qid = 1
        for q in positive_queries:
            queries.append(TriggerQuery(qid, q, expected_trigger=True, category="positive"))
            qid += 1
        for q in distractor_queries:
            queries.append(TriggerQuery(qid, q, expected_trigger=False, category="adjacent_distractor"))
            qid += 1

        return queries

    def evaluate_skill_trigger(
        self,
        skill: SkillMetadata,
        queries: list[TriggerQuery] | None = None,
    ) -> TriggerEvaluationResult:
        """
        執行觸發率判定評測，計算混淆矩陣指標。
        """
        if queries is None:
            queries = self.generate_default_20_queries(skill)

        system_prompt = (
            "You are an objective AI system router and skill dispatcher.\n"
            "Your task is to determine whether the user request should trigger and activate the following Candidate Skill.\n\n"
            f"[Candidate Skill]\n"
            f"- Name: {skill.name}\n"
            f"- Description: {skill.description}\n\n"
            "Instructions:\n"
            "1. If the request directly requires, relates to, or benefits from the specialized domain of the Candidate Skill, select it (`\"selected\": true`).\n"
            "2. If the request belongs to generic programming, unrelated domains, or standard utility tasks, do NOT select it (`\"selected\": false`).\n"
            "3. Output MUST be valid JSON strictly adhering to the schema:\n"
            "{\n"
            '  "selected": true or false,\n'
            f'  "selected_skill": "{skill.name}" or null,\n'
            '  "confidence": <float between 0.0 and 1.0>,\n'
            '  "reasoning": "<short sentence in Traditional Chinese>"\n'
            "}"
        )

        results: list[TriggerQueryResult] = []
        tp = fp = tn = fn = 0

        for tq in queries:
            response = self.adapter.generate(
                system_prompt=system_prompt,
                user_prompt=tq.query,
                temperature=0.0,
            )
            data = self.extract_json_block(response.text)

            predicted_trigger = bool(data.get("selected", False))
            selected_skill = data.get("selected_skill")
            confidence = float(data.get("confidence", 0.0))
            reasoning = str(data.get("reasoning", ""))

            # 判定分類類別
            if tq.expected_trigger:
                if predicted_trigger:
                    tp += 1
                    classification = "TP"
                else:
                    fn += 1
                    classification = "FN"
            else:
                if predicted_trigger:
                    fp += 1
                    classification = "FP"
                else:
                    tn += 1
                    classification = "TN"

            results.append(
                TriggerQueryResult(
                    query_id=tq.query_id,
                    query=tq.query,
                    expected_trigger=tq.expected_trigger,
                    predicted_trigger=predicted_trigger,
                    selected_skill=selected_skill,
                    confidence=confidence,
                    reasoning=reasoning,
                    classification=classification,
                )
            )

        total = len(queries)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        accuracy = (tp + tn) / total if total > 0 else 0.0

        matrix = ConfusionMatrix(
            tp=tp,
            fp=fp,
            tn=tn,
            fn=fn,
            precision=precision,
            recall=recall,
            fpr=fpr,
            accuracy=accuracy,
            total=total,
        )

        return TriggerEvaluationResult(
            skill_name=skill.name,
            queries_count=total,
            matrix=matrix,
            results=results,
        )


# ==============================================================================
# 五、斷言評分引擎 (Assertion Grader)
# ==============================================================================

class AssertionGrader:
    """斷言評分器，支援 LLM-as-a-judge 與確定性規則評分"""

    def __init__(self, adapter: BaseLLMAdapter):
        self.adapter = adapter

    def grade(
        self,
        user_prompt: str,
        response_text: str,
        assertions: list[str],
    ) -> GradingResult:
        if not assertions:
            return GradingResult(
                passed=True,
                score=1.0,
                evidence="無自訂斷言要求，預設通過。",
                text=response_text,
                assertions=[],
            )

        assertion_results: list[AssertionResult] = []
        passed_count = 0

        for assertion in assertions:
            # 建構裁判評分 Prompt
            judge_sys_prompt = (
                "You are a rigorous, objective CAE engineering evaluator.\n"
                "Determine whether the Candidate Response satisfies the Assertion.\n\n"
                "Output STRICTLY valid JSON:\n"
                "{\n"
                '  "passed": true or false,\n'
                '  "evidence": "<concise explanation in Traditional Chinese>"\n'
                "}"
            )
            judge_user_prompt = (
                f"[Original Question]\n{user_prompt}\n\n"
                f"[Assertion Condition]\n{assertion}\n\n"
                f"[Candidate Response]\n{response_text}\n"
            )

            res = self.adapter.generate(
                system_prompt=judge_sys_prompt,
                user_prompt=judge_user_prompt,
                temperature=0.0,
            )
            data = TriggerJudgementEngine.extract_json_block(res.text)

            is_passed = bool(data.get("passed", False))
            evidence_str = str(data.get("evidence", "無法解析裁判回傳證據"))

            if is_passed:
                passed_count += 1

            assertion_results.append(
                AssertionResult(
                    assertion=assertion,
                    passed=is_passed,
                    evidence=evidence_str,
                )
            )

        total_assertions = len(assertions)
        score = passed_count / total_assertions if total_assertions > 0 else 0.0
        all_passed = passed_count == total_assertions

        overall_evidence = f"共 {total_assertions} 項斷言，通過 {passed_count} 項。"

        return GradingResult(
            passed=all_passed,
            score=score,
            evidence=overall_evidence,
            text=response_text,
            assertions=assertion_results,
        )


# ==============================================================================
# 六、Headless 技能評測主控器 (A/B Evaluator)
# ==============================================================================

class HeadlessSkillEvaluator:
    """
    負責協調整合 A/B 對照評測與觸發率測試：
    - 依據 evals.json 產生 with_skill 與 without_skill 之 timing.json 與 grading.json
    - 保存基準結構至 agents/skills-workspace/<skill>-workspace/iteration-<N>/
    """

    def __init__(
        self,
        skill_target: str | Path,
        adapter: BaseLLMAdapter,
        workspace_root: Path | None = None,
        evals_path: Path | None = None,
    ):
        self.skill_dir = find_skill_directory(skill_target)
        self.skill = parse_skill_markdown(self.skill_dir / "SKILL.md")
        self.adapter = adapter
        self.trigger_engine = TriggerJudgementEngine(adapter)
        self.grader = AssertionGrader(adapter)

        repo_root = Path(__file__).resolve().parents[2]
        self.workspace_root = workspace_root or (repo_root / "agents" / "skills-workspace")

        if evals_path:
            self.evals_path = Path(evals_path)
        else:
            default_evals = self.skill_dir / "evals" / "evals.json"
            self.evals_path = default_evals if default_evals.is_file() else None

    def load_evals(self) -> list[dict[str, Any]]:
        """讀取 evals.json"""
        if not self.evals_path or not self.evals_path.is_file():
            return []

        with open(self.evals_path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)

        if isinstance(data, dict):
            return data.get("evals", [])
        if isinstance(data, list):
            return data
        return []

    def get_iteration_dir(self, iteration: int = 1) -> Path:
        """取得特定 iteration 的輸出路徑"""
        target_dir = self.workspace_root / f"{self.skill.name}-workspace" / f"iteration-{iteration}"
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir

    def run_trigger_test(
        self,
        iteration: int = 1,
        queries: list[TriggerQuery] | None = None,
    ) -> TriggerEvaluationResult:
        """執行觸發率混淆矩陣評估並存檔"""
        iter_dir = self.get_iteration_dir(iteration)
        result = self.trigger_engine.evaluate_skill_trigger(self.skill, queries=queries)

        out_file = iter_dir / "trigger_eval.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

        return result

    def run_ab_evaluations(self, iteration: int = 1) -> dict[str, Any]:
        """
        執行 A/B 對照評測：
        對於 evals.json 中的每一道題目，分別以 with_skill 與 without_skill 執行並記錄：
        - eval-<N>/with_skill/timing.json
        - eval-<N>/with_skill/grading.json
        - eval-<N>/without_skill/timing.json
        - eval-<N>/without_skill/grading.json
        """
        evals_list = self.load_evals()
        if not evals_list:
            raise ValueError(f"找不到可執行的評測案例：{self.evals_path}")

        iter_dir = self.get_iteration_dir(iteration)

        summary_cases = []

        # 準備 with_skill 與 without_skill 系統提示詞
        with_skill_system = (
            "You are an expert CAE engineering assistant.\n"
            "You have access to the following specialized skill instructions. Follow them rigorously:\n\n"
            f"[SKILL INSTRUCTIONS: {self.skill.name}]\n"
            f"{self.skill.body}\n"
        )
        without_skill_system = (
            "You are a helpful engineering assistant."
        )

        for case in evals_list:
            eval_id = case.get("eval_id", 1)
            prompt = case.get("prompt", "")
            assertions = case.get("assertions", [])

            case_dir = iter_dir / f"eval-{eval_id}"

            # 1. 執行 with_skill
            with_dir = case_dir / "with_skill"
            with_dir.mkdir(parents=True, exist_ok=True)

            resp_with = self.adapter.generate(
                system_prompt=with_skill_system,
                user_prompt=prompt,
                temperature=0.0,
            )
            with open(with_dir / "timing.json", "w", encoding="utf-8") as f:
                json.dump({
                    "duration_ms": resp_with.duration_ms,
                    "tokens": resp_with.tokens.to_dict(),
                }, f, indent=2, ensure_ascii=False)

            grading_with = self.grader.grade(prompt, resp_with.text, assertions)
            with open(with_dir / "grading.json", "w", encoding="utf-8") as f:
                json.dump(grading_with.to_dict(), f, indent=2, ensure_ascii=False)

            # 2. 執行 without_skill
            without_dir = case_dir / "without_skill"
            without_dir.mkdir(parents=True, exist_ok=True)

            resp_without = self.adapter.generate(
                system_prompt=without_skill_system,
                user_prompt=prompt,
                temperature=0.0,
            )
            with open(without_dir / "timing.json", "w", encoding="utf-8") as f:
                json.dump({
                    "duration_ms": resp_without.duration_ms,
                    "tokens": resp_without.tokens.to_dict(),
                }, f, indent=2, ensure_ascii=False)

            grading_without = self.grader.grade(prompt, resp_without.text, assertions)
            with open(without_dir / "grading.json", "w", encoding="utf-8") as f:
                json.dump(grading_without.to_dict(), f, indent=2, ensure_ascii=False)

            summary_cases.append({
                "eval_id": eval_id,
                "prompt": prompt,
                "with_passed": grading_with.passed,
                "without_passed": grading_without.passed,
                "with_duration_ms": resp_with.duration_ms,
                "without_duration_ms": resp_without.duration_ms,
            })

        return {
            "skill": self.skill.name,
            "iteration": iteration,
            "cases_count": len(summary_cases),
            "cases": summary_cases,
        }


# ==============================================================================
# 七、CLI 入口與引數解析
# ==============================================================================

def create_adapter(adapter_name: str, model: str | None = None) -> BaseLLMAdapter:
    """工廠函式：建立指定類型之 LLM 適配器"""
    name = adapter_name.lower().strip()
    if name == "mock":
        return DeterministicMockAdapter()
    elif name == "kiro":
        target_model = model or "claude-sonnet-5"
        return KiroCLIAdapter(model=target_model)
    elif name in ("gemini", "gemini-sdk"):
        target_model = model or "gemini-3.8-flash"
        return GeminiSDKAdapter(model=target_model)
    else:
        raise ValueError(f"不支援的適配器類型：'{adapter_name}'。可選：'mock', 'kiro', 'gemini'。")


def main() -> int:
    """CLI 命令列進入點"""
    parser = argparse.ArgumentParser(
        description="Stage 1 Headless Skill Evaluator & Benchmark Tooling"
    )
    parser.add_argument("--skill", required=True, help="目標技能名稱或目錄路徑")
    parser.add_argument(
        "--adapter",
        default="mock",
        choices=["mock", "kiro", "gemini"],
        help="評測適配器 (預設: mock)",
    )
    parser.add_argument("--model", default=None, help="指定推理模型名稱")
    parser.add_argument("--iteration", type=int, default=1, help="迭代輪次號 (預設: 1)")
    parser.add_argument("--workspace", default=None, help="自訂 workspace 輸出目錄")
    parser.add_argument("--evals", default=None, help="自訂 evals.json 檔案路徑")
    parser.add_argument("--run-trigger", action="store_true", help="執行 20 題混淆矩陣觸發率評測")
    parser.add_argument("--run-ab", action="store_true", help="執行 A/B 對照基準評測")
    parser.add_argument("--all", action="store_true", help="同時執行觸發率與 A/B 評估")

    args = parser.parse_args()

    adapter = create_adapter(args.adapter, model=args.model)
    evaluator = HeadlessSkillEvaluator(
        skill_target=args.skill,
        adapter=adapter,
        workspace_root=Path(args.workspace) if args.workspace else None,
        evals_path=Path(args.evals) if args.evals else None,
    )

    should_run_trigger = args.run_trigger or args.all or (not args.run_ab and not args.run_trigger)
    should_run_ab = args.run_ab or args.all

    print(f"[*] 載入技能：{evaluator.skill.name} (來自: {evaluator.skill_dir})")
    print(f"[*] 使用適配器：{args.adapter} | Iteration: {args.iteration}")

    if should_run_trigger:
        print("[*] 啟動觸發率混淆矩陣判定...")
        trigger_res = evaluator.run_trigger_test(iteration=args.iteration)
        m = trigger_res.matrix
        print(
            f"[+] 混淆矩陣完成：Precision={m.precision:.2f}, Recall={m.recall:.2f}, "
            f"FPR={m.fpr:.2f}, Accuracy={m.accuracy:.2f} (TP={m.tp}, FP={m.fp}, TN={m.tn}, FN={m.fn})"
        )

    if should_run_ab:
        print("[*] 啟動 A/B 對照評測...")
        ab_res = evaluator.run_ab_evaluations(iteration=args.iteration)
        print(f"[+] A/B 評測完成：共評估 {ab_res['cases_count']} 個案例。")

    return 0


if __name__ == "__main__":
    # 強制宣告控制台 UTF-8
    if sys.stdout.encoding.lower() != "utf-8" and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
