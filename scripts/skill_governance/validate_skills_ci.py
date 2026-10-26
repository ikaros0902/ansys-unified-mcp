#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腳本名稱：validate_skills_ci.py
功能說明：Stage 1 技能庫靜態檢查與合規門禁工具 (Skills CI & Validator)。

針對專案中的技能目錄（Tier-1: agents/skills/ 與 Tier-2: agents/skills-tier2/）
進行全方位靜態規格檢驗，確保完全符合 Stage 1 技能治理規範。

檢查項目包含：
  1. SKILL.md 行數檢查：本體行數嚴格 <= 150 行。
  2. YAML Frontmatter 結構檢查：
     - 必須包含 name（小寫連字號 kebab-case，與目錄名稱一致）。
     - 必須包含 description（字數 <= 120 words）。
  3. References 目錄檢查：
     - 若 references/*.md 單檔行數 > 300 行，強制檢查前 40 行內是否包含目錄
       （# Table of Contents 或 ## TOC 或 ## 目錄）。
     - 若 references/*.md 單檔行數 > 500 行，發出強制拆分錯誤。
  4. 4-Folder Anatomy 結構規範檢查：
     - 每個技能目錄必須包含 SKILL.md。
     - 僅允許標準 4 大資料夾：references/, scripts/, assets/, evals/。
  5. 受版控 .gitignore 檢查：
     - 透過 git check-ignore 驗證特定暫存與工作路徑被正確忽略：
       * agents/skills-workspace/dummy.txt
       * agents/skills/.zvec-grep/index
       * .agents/skills

支援命令列參數：
  --tier1-only : 僅檢查 Tier-1 技能（agents/skills/）
  --tier2-only : 僅檢查 Tier-2 技能（agents/skills-tier2/）
  --fix-toc    : 自動為超過 300 行且缺少目錄的 references/*.md 生成並注入 TOC
  --tier1-dir  : 自訂 Tier-1 技能目錄路徑
  --tier2-dir  : 自訂 Tier-2 技能目錄路徑
  --repo-root  : 自訂 Git 專案根目錄
  --verbose    : 顯示詳細檢查資訊

退出碼 (Exit Code)：
  0 : 全部檢查通過（或透過 --fix-toc 自愈後合規）
  1 : 任一項目不合規
"""

from __future__ import annotations

import argparse
import dataclasses
from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Sequence

# 強制 Windows 終端以 UTF-8 輸出，避免繁體中文亂碼
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


# ==============================================================================
# 一、常數與預設配置
# ==============================================================================

MAX_SKILL_MD_LINES = 150
MAX_DESCRIPTION_WORDS = 120
REF_TOC_LINE_THRESHOLD = 300
REF_MAX_LINE_THRESHOLD = 500
TOC_SCAN_MAX_LINES = 40

# 4-Folder Anatomy 規範定義
ALLOWED_SKILL_SUBDIRS: set[str] = {
    "references",
    "scripts",
    "assets",
    "evals",
    "__pycache__",
}

ALLOWED_SKILL_ROOT_FILES: set[str] = {
    "SKILL.md",
    "README.md",
    ".gitignore",
}

# .gitignore 驗證目標清單
GITIGNORE_AUDIT_TARGETS: list[str] = [
    "agents/skills-workspace/dummy.txt",
    "agents/skills/.zvec-grep/index",
    ".agents/skills",
]

# 目錄 (TOC) 標記正則表達式
TOC_MARKER_REGEX = re.compile(
    r"^(?:#|##|###)\s+(?:table\s+of\s+contents|toc|目錄)",
    re.IGNORECASE,
)

# Kebab-case 命名正則
KEBAB_CASE_REGEX = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


# ==============================================================================
# 二、資料結構
# ==============================================================================

@dataclass
class SkillViolation:
    """違規項目記錄"""
    category: str
    skill_name: str
    file_path: Path
    message: str
    severity: str = "ERROR"  # ERROR 或 WARNING

    def __str__(self) -> str:
        rel = self.file_path.name if self.file_path else self.skill_name
        return f"[{self.severity}] [{self.category}] {self.skill_name} ({rel}): {self.message}"


@dataclass
class SkillValidationResult:
    """單一技能之檢查結果"""
    skill_name: str
    skill_path: Path
    tier: str
    violations: list[SkillViolation] = field(default_factory=list)
    repaired_actions: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(v.severity == "ERROR" for v in self.violations)


@dataclass
class ValidationReport:
    """整体验證總結報告"""
    tier1_skills_checked: int = 0
    tier2_skills_checked: int = 0
    total_skills_checked: int = 0
    results: list[SkillValidationResult] = field(default_factory=list)
    global_violations: list[SkillViolation] = field(default_factory=list)
    repaired_actions: list[str] = field(default_factory=list)

    @property
    def total_errors(self) -> int:
        count = sum(
            sum(1 for v in r.violations if v.severity == "ERROR")
            for r in self.results
        )
        count += sum(1 for v in self.global_violations if v.severity == "ERROR")
        return count

    @property
    def total_warnings(self) -> int:
        count = sum(
            sum(1 for v in r.violations if v.severity == "WARNING")
            for r in self.results
        )
        count += sum(1 for v in self.global_violations if v.severity == "WARNING")
        return count

    @property
    def is_passed(self) -> bool:
        return self.total_errors == 0


# ==============================================================================
# 三、TOC 自動生成與修復工具
# ==============================================================================

def generate_markdown_anchor(heading_text: str) -> str:
    """
    產生符合 Markdown 錨點規範之 slug。
    支援中文與英文混排，移除標點與內嵌標籤。
    """
    # 移除 Markdown 連結 [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", heading_text)
    # 移除行內代碼 `code` -> code
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # 轉小寫
    text = text.strip().lower()
    # 保留字母、數字、中文字符、底線、減號與空白，移除其他符號
    text = re.sub(r"[^\w\s\-\u4e00-\u9fff]", "", text)
    # 連續空白轉換為減號
    text = re.sub(r"\s+", "-", text)
    # 消除多餘減號並去頭尾
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def build_markdown_toc(content: str) -> str:
    """
    掃描 Markdown 內文並產生目錄 (Table of Contents)。
    以 ## (Level 2) 與 ### (Level 3) 為主，自動跳過代碼塊與既有 TOC 標題。
    """
    lines = content.splitlines()
    headings: list[tuple[int, str, str]] = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        m = re.match(r"^(#{2,3})\s+(.+)$", stripped)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            # 若為目錄標題本身則跳過
            if TOC_MARKER_REGEX.search(stripped):
                continue
            anchor = generate_markdown_anchor(title)
            headings.append((level, title, anchor))

    if not headings:
        return ""

    toc_lines: list[str] = [
        "## Table of Contents\n",
    ]
    for level, title, anchor in headings:
        indent = "  " * (level - 2)
        toc_lines.append(f"{indent}- [{title}](#{anchor})")
    toc_lines.append("\n---\n")

    return "\n".join(toc_lines)


def inject_toc_into_markdown(content: str, toc_text: str) -> str:
    """
    將目錄文本注入 Markdown 檔案前部（通常在一級標題之後或開頭）。
    確保注入後目錄標題位於前 40 行之內。
    """
    lines = content.splitlines(keepends=True)

    # 1. 檢測開頭是否有 YAML Frontmatter (--- ... ---)
    in_fm = False
    fm_end_idx = -1
    for idx, line in enumerate(lines):
        if idx == 0 and line.strip() == "---":
            in_fm = True
            continue
        if in_fm and line.strip() == "---":
            fm_end_idx = idx
            break

    insert_idx = 0
    if fm_end_idx != -1:
        insert_idx = fm_end_idx + 1
        while insert_idx < len(lines) and not lines[insert_idx].strip():
            insert_idx += 1

    # 2. 檢測一級標題 (# Title)
    title_idx = -1
    for idx in range(insert_idx, min(len(lines), insert_idx + 30)):
        if re.match(r"^#\s+[^#]", lines[idx]):
            title_idx = idx
            break

    if title_idx != -1:
        pos = title_idx + 1
        # 跳過緊接一級標題後的空行或水平線
        if pos < len(lines) and not lines[pos].strip():
            pos += 1
        if pos < len(lines) and lines[pos].strip() == "---":
            pos += 1
        if pos < len(lines) and not lines[pos].strip():
            pos += 1
        insert_idx = pos

    before = "".join(lines[:insert_idx])
    after = "".join(lines[insert_idx:])

    res = before
    if res and not res.endswith("\n\n"):
        res = res.rstrip("\n") + "\n\n"
    res += toc_text.strip() + "\n\n"
    res += after.lstrip("\n")
    return res


# ==============================================================================
# 四、Frontmatter 解析工具
# ==============================================================================

def extract_and_parse_frontmatter(content: str) -> tuple[dict[str, str] | None, str]:
    """
    從 SKILL.md 內容中安全萃取並解析 YAML Frontmatter。
    具備雙軌容錯：
      1. 優先使用 yaml.safe_load。
      2. 若含有未引號冒號 (如 '(繁中/En):') 導致語法錯誤時，自動降級為結構化正則鍵值解析。
    回傳：(frontmatter_dict, raw_frontmatter_text)
    """
    m = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", content, re.DOTALL)
    if not m:
        return None, ""

    fm_raw = m.group(1)

    # 1. 嘗試 PyYAML
    if yaml is not None:
        try:
            loaded = yaml.safe_load(fm_raw)
            if isinstance(loaded, dict):
                return {k: str(v) if v is not None else "" for k, v in loaded.items()}, fm_raw
        except Exception:
            pass

    # 2. 結構化鍵值解析容錯降級
    data: dict[str, str] = {}
    current_key: str | None = None
    current_val_lines: list[str] = []

    for line in fm_raw.splitlines():
        key_match = re.match(r"^([a-zA-Z0-9_-]+)\s*:\s*(.*)$", line)
        if key_match:
            if current_key:
                data[current_key] = "\n".join(current_val_lines).strip()
            current_key = key_match.group(1).strip()
            current_val_lines = [key_match.group(2)]
        elif current_key:
            current_val_lines.append(line)

    if current_key:
        data[current_key] = "\n".join(current_val_lines).strip()

    return data, fm_raw


# ==============================================================================
# 五、核心檢查規則實作
# ==============================================================================

def check_skill_md_line_count(skill_dir: Path) -> list[SkillViolation]:
    """
    規則 1：SKILL.md 行數檢查。
    本體行數嚴格 <= 150 行（若超過拋出錯誤並列出行數）。
    """
    violations: list[SkillViolation] = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        violations.append(
            SkillViolation(
                category="Line Count",
                skill_name=skill_dir.name,
                file_path=skill_md,
                message="找不到 SKILL.md 本體檔案",
                severity="ERROR",
            )
        )
        return violations

    try:
        content = skill_md.read_text(encoding="utf-8", errors="replace")
        line_count = len(content.splitlines())
        if line_count > MAX_SKILL_MD_LINES:
            violations.append(
                SkillViolation(
                    category="Line Count",
                    skill_name=skill_dir.name,
                    file_path=skill_md,
                    message=f"SKILL.md 本體行數超過嚴格上限: {line_count} 行 > {MAX_SKILL_MD_LINES} 行",
                    severity="ERROR",
                )
            )
    except Exception as ex:
        violations.append(
            SkillViolation(
                category="Line Count",
                skill_name=skill_dir.name,
                file_path=skill_md,
                message=f"讀取 SKILL.md 發生例外: {ex}",
                severity="ERROR",
            )
        )

    return violations


def check_yaml_frontmatter(skill_dir: Path) -> list[SkillViolation]:
    """
    規則 2：YAML Frontmatter 結構檢查。
    必須包含 name（小寫連字號 kebab-case，且與目錄名稱完全同名）
    與 description（字數 <= 120 words）。
    """
    violations: list[SkillViolation] = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        # 行數檢查已有報錯，此處直接返回
        return violations

    content = skill_md.read_text(encoding="utf-8", errors="replace")
    fm_data, raw_fm = extract_and_parse_frontmatter(content)

    if fm_data is None:
        violations.append(
            SkillViolation(
                category="YAML Frontmatter",
                skill_name=skill_dir.name,
                file_path=skill_md,
                message="缺少合規之 YAML Frontmatter 區塊 (必須以 '---' 開始並以 '---' 結束)",
                severity="ERROR",
            )
        )
        return violations

    # 檢查 name
    name_val = fm_data.get("name", "").strip().strip("\"'")
    if not name_val:
        violations.append(
            SkillViolation(
                category="YAML Frontmatter",
                skill_name=skill_dir.name,
                file_path=skill_md,
                message="Frontmatter 缺少 'name' 欄位或為空值",
                severity="ERROR",
            )
        )
    else:
        # 1. 小寫連字號 (kebab-case) 格式檢查
        if not KEBAB_CASE_REGEX.match(name_val):
            violations.append(
                SkillViolation(
                    category="YAML Frontmatter",
                    skill_name=skill_dir.name,
                    file_path=skill_md,
                    message=f"name '{name_val}' 不符合小寫連字號 (kebab-case) 格式 (如: ansys-mechanical)",
                    severity="ERROR",
                )
            )
        # 2. 與目錄同名檢查
        if name_val != skill_dir.name:
            violations.append(
                SkillViolation(
                    category="YAML Frontmatter",
                    skill_name=skill_dir.name,
                    file_path=skill_md,
                    message=f"name '{name_val}' 與所在技能目錄名稱 '{skill_dir.name}' 不一致",
                    severity="ERROR",
                )
            )

    # 檢查 description
    desc_val = fm_data.get("description", "").strip()
    if not desc_val:
        violations.append(
            SkillViolation(
                category="YAML Frontmatter",
                skill_name=skill_dir.name,
                file_path=skill_md,
                message="Frontmatter 缺少 'description' 欄位或為空值",
                severity="ERROR",
            )
        )
    else:
        word_count = len(desc_val.split())
        if word_count > MAX_DESCRIPTION_WORDS:
            violations.append(
                SkillViolation(
                    category="YAML Frontmatter",
                    skill_name=skill_dir.name,
                    file_path=skill_md,
                    message=f"description 字數為 {word_count} words，超過上限 {MAX_DESCRIPTION_WORDS} words",
                    severity="ERROR",
                )
            )

    return violations


def check_references_directory(
    skill_dir: Path,
    fix_toc: bool = False,
) -> tuple[list[SkillViolation], list[str]]:
    """
    規則 3：References 目錄檢查。
      - 若 references/*.md 單檔行數 > 300 行，強制檢查前 40 行內是否包含目錄
        (# Table of Contents 或 ## TOC 或 ## 目錄)，缺少則報錯。
      - 若支援 --fix-toc，則自動生成目錄並回寫。
      - 若 references/*.md 單檔行數 > 500 行，發出強制拆分警告或錯誤。
    """
    violations: list[SkillViolation] = []
    repaired_actions: list[str] = []
    ref_dir = skill_dir / "references"

    if not ref_dir.exists() or not ref_dir.is_dir():
        return violations, repaired_actions

    # 遞迴檢查 references 目錄下所有 .md 檔案
    for md_file in sorted(ref_dir.rglob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
            line_count = len(lines)
            rel_file = md_file.relative_to(skill_dir)

            # 1. 行數 > 500 行檢查：發出強制拆分錯誤
            if line_count > REF_MAX_LINE_THRESHOLD:
                violations.append(
                    SkillViolation(
                        category="References Limit",
                        skill_name=skill_dir.name,
                        file_path=md_file,
                        message=(
                            f"參考文件 {rel_file} 規模過大 ({line_count} 行 > {REF_MAX_LINE_THRESHOLD} 行)，"
                            f"超出單檔安全上限，必須強制拆分為子模組！"
                        ),
                        severity="ERROR",
                    )
                )

            # 2. 行數 > 300 行檢查：前 40 行強制檢查 TOC
            if line_count > REF_TOC_LINE_THRESHOLD:
                first_lines = lines[:TOC_SCAN_MAX_LINES]
                has_toc = any(
                    TOC_MARKER_REGEX.search(ln.strip()) for ln in first_lines
                )

                if not has_toc:
                    if fix_toc:
                        # 執行自動生成並注入 TOC
                        toc_text = build_markdown_toc(content)
                        if toc_text:
                            new_content = inject_toc_into_markdown(content, toc_text)
                            md_file.write_text(new_content, encoding="utf-8")
                            action_msg = f"已為 {skill_dir.name}/{rel_file} ({line_count} 行) 自動生成並注入 Table of Contents"
                            repaired_actions.append(action_msg)
                            # 重新驗證注入後是否具備 TOC
                            check_lines = new_content.splitlines()[:TOC_SCAN_MAX_LINES]
                            if not any(TOC_MARKER_REGEX.search(ln.strip()) for ln in check_lines):
                                violations.append(
                                    SkillViolation(
                                        category="References TOC",
                                        skill_name=skill_dir.name,
                                        file_path=md_file,
                                        message=f"自動注入 TOC 失敗，前 {TOC_SCAN_MAX_LINES} 行仍未檢出 TOC 標記",
                                        severity="ERROR",
                                    )
                                )
                        else:
                            violations.append(
                                SkillViolation(
                                    category="References TOC",
                                    skill_name=skill_dir.name,
                                    file_path=md_file,
                                    message=f"檔案行數 {line_count} > {REF_TOC_LINE_THRESHOLD} 行且無二級/三級標題，無法自動生成目錄",
                                    severity="ERROR",
                                )
                            )
                    else:
                        violations.append(
                            SkillViolation(
                                category="References TOC",
                                skill_name=skill_dir.name,
                                file_path=md_file,
                                message=(
                                    f"參考文件 {rel_file} 單檔行數 {line_count} 行 > {REF_TOC_LINE_THRESHOLD} 行，"
                                    f"且前 {TOC_SCAN_MAX_LINES} 行缺少目錄標記 (# Table of Contents / ## TOC / ## 目錄)。"
                                    f"可使用 --fix-toc 參數自動生成目錄。"
                                ),
                                severity="ERROR",
                            )
                        )

        except Exception as ex:
            violations.append(
                SkillViolation(
                    category="References Check",
                    skill_name=skill_dir.name,
                    file_path=md_file,
                    message=f"檢查參考文件發生例外: {ex}",
                    severity="ERROR",
                )
            )

    return violations, repaired_actions


def check_4_folder_anatomy(skill_dir: Path) -> list[SkillViolation]:
    """
    規則 4：4-Folder Anatomy 檢查。
    檢查每個技能是否包含 SKILL.md，且按需包含 references/、scripts/、assets/、evals/。
    若出現非標準之頂層子目錄或未授權檔案，拋出違規記錄。
    """
    violations: list[SkillViolation] = []

    # 1. 必備 SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        violations.append(
            SkillViolation(
                category="4-Folder Anatomy",
                skill_name=skill_dir.name,
                file_path=skill_md,
                message="缺少 SKILL.md 核心說明本體 (4-Folder Anatomy 必備項目)",
                severity="ERROR",
            )
        )

    # 2. 檢查頂層子項目
    try:
        for child in skill_dir.iterdir():
            if child.name.startswith("."):
                continue

            if child.is_dir():
                if child.name not in ALLOWED_SKILL_SUBDIRS:
                    violations.append(
                        SkillViolation(
                            category="4-Folder Anatomy",
                            skill_name=skill_dir.name,
                            file_path=child,
                            message=(
                                f"發現非標準子目錄: '{child.name}/' "
                                f"(標準結構僅允許按需包含: references/, scripts/, assets/, evals/)"
                            ),
                            severity="ERROR",
                        )
                    )
            elif child.is_file():
                if child.name not in ALLOWED_SKILL_ROOT_FILES:
                    violations.append(
                        SkillViolation(
                            category="4-Folder Anatomy",
                            skill_name=skill_dir.name,
                            file_path=child,
                            message=(
                                f"發現非標準根層檔案: '{child.name}' "
                                f"(根層僅允許: SKILL.md, README.md, .gitignore)"
                            ),
                            severity="WARNING",
                        )
                    )
    except Exception as ex:
        violations.append(
            SkillViolation(
                category="4-Folder Anatomy",
                skill_name=skill_dir.name,
                file_path=skill_dir,
                message=f"掃描目錄結構發生例外: {ex}",
                severity="ERROR",
            )
        )

    return violations


def check_gitignore_rules(repo_root: Path) -> list[SkillViolation]:
    """
    規則 5：受版控 .gitignore 檢查。
    透過調用 git check-ignore 驗證以下關鍵路徑是否被正確忽略：
      1. agents/skills-workspace/dummy.txt
      2. agents/skills/.zvec-grep/index
      3. .agents/skills
    """
    violations: list[SkillViolation] = []

    for rel_target in GITIGNORE_AUDIT_TARGETS:
        try:
            # 呼叫 git check-ignore <path>
            res = subprocess.run(
                ["git", "check-ignore", rel_target],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            # returncode == 0 表示符合 gitignore；returncode == 1 表示未被忽略
            if res.returncode != 0:
                violations.append(
                    SkillViolation(
                        category=".gitignore Compliance",
                        skill_name="[REPO]",
                        file_path=repo_root / rel_target,
                        message=f"路徑 '{rel_target}' 未被 .gitignore 正確忽略 (git check-ignore returncode={res.returncode})",
                        severity="ERROR",
                    )
                )
        except FileNotFoundError:
            violations.append(
                SkillViolation(
                    category=".gitignore Compliance",
                    skill_name="[REPO]",
                    file_path=repo_root / rel_target,
                    message="未找到 git 執行檔，無法驗證 .gitignore 忽略規則",
                    severity="ERROR",
                )
            )
            break
        except Exception as ex:
            violations.append(
                SkillViolation(
                    category=".gitignore Compliance",
                    skill_name="[REPO]",
                    file_path=repo_root / rel_target,
                    message=f"執行 git check-ignore 發生例外: {ex}",
                    severity="ERROR",
                )
            )

    return violations


# ==============================================================================
# 六、聚合驗證流程
# ==============================================================================

def validate_single_skill(
    skill_dir: Path,
    tier: str,
    fix_toc: bool = False,
) -> SkillValidationResult:
    """對單一技能目錄執行完整靜態檢查"""
    res = SkillValidationResult(
        skill_name=skill_dir.name,
        skill_path=skill_dir,
        tier=tier,
    )

    # 1. SKILL.md 行數檢查
    res.violations.extend(check_skill_md_line_count(skill_dir))

    # 2. YAML Frontmatter 結構檢查
    res.violations.extend(check_yaml_frontmatter(skill_dir))

    # 3. References 目錄與 TOC 檢查
    ref_violations, repaired = check_references_directory(skill_dir, fix_toc=fix_toc)
    res.violations.extend(ref_violations)
    res.repaired_actions.extend(repaired)

    # 4. 4-Folder Anatomy 檢查
    res.violations.extend(check_4_folder_anatomy(skill_dir))

    return res


def run_full_validation(
    repo_root: Path,
    tier1_dir: Path | None = None,
    tier2_dir: Path | None = None,
    tier1_only: bool = False,
    tier2_only: bool = False,
    fix_toc: bool = False,
    verbose: bool = False,
) -> ValidationReport:
    """執行全量技能 CI 靜態檢查"""
    report = ValidationReport()

    t1_dir = tier1_dir or (repo_root / "agents" / "skills")
    t2_dir = tier2_dir or (repo_root / "agents" / "skills-tier2")

    # 1. 決定要檢查的 Tier 目錄
    check_t1 = not tier2_only
    check_t2 = not tier1_only

    # 2. 執行 .gitignore 檢查（全域性門禁）
    git_violations = check_gitignore_rules(repo_root)
    report.global_violations.extend(git_violations)

    # 3. 掃描 Tier-1 技能
    if check_t1:
        if not t1_dir.exists():
            report.global_violations.append(
                SkillViolation(
                    category="Directory Audit",
                    skill_name="[Tier-1]",
                    file_path=t1_dir,
                    message=f"Tier-1 技能目錄不存在: {t1_dir}",
                    severity="ERROR",
                )
            )
        else:
            t1_skill_dirs = [
                d for d in sorted(t1_dir.iterdir())
                if d.is_dir() and not d.name.startswith(".")
            ]
            report.tier1_skills_checked = len(t1_skill_dirs)
            for s_dir in t1_skill_dirs:
                res = validate_single_skill(s_dir, tier="Tier-1", fix_toc=fix_toc)
                report.results.append(res)
                report.repaired_actions.extend(res.repaired_actions)

    # 4. 掃描 Tier-2 技能
    if check_t2:
        if not t2_dir.exists():
            # 若為 tier2-only 則報錯；若為全量且目錄尚未建立則視為警告或錯誤
            severity = "ERROR" if tier2_only else "WARNING"
            report.global_violations.append(
                SkillViolation(
                    category="Directory Audit",
                    skill_name="[Tier-2]",
                    file_path=t2_dir,
                    message=f"Tier-2 技能目錄不存在: {t2_dir}",
                    severity=severity,
                )
            )
        else:
            t2_skill_dirs = [
                d for d in sorted(t2_dir.iterdir())
                if d.is_dir() and not d.name.startswith(".")
            ]
            report.tier2_skills_checked = len(t2_skill_dirs)
            for s_dir in t2_skill_dirs:
                res = validate_single_skill(s_dir, tier="Tier-2", fix_toc=fix_toc)
                report.results.append(res)
                report.repaired_actions.extend(res.repaired_actions)

    report.total_skills_checked = (
        report.tier1_skills_checked + report.tier2_skills_checked
    )
    return report


# ==============================================================================
# 七、CLI 入口與格式化輸出
# ==============================================================================

def print_cli_summary(report: ValidationReport, verbose: bool = False) -> None:
    """輸出標準繁體中文 CI 檢查報告"""
    print("\n" + "=" * 70)
    print("  Stage 1 Skills CI & Static Compliance Validator (靜態檢查門禁)")
    print("=" * 70)

    # 輸出自動修復動作
    if report.repaired_actions:
        print("\n[TOC 自動修復紀錄 (--fix-toc)]")
        for action in report.repaired_actions:
            print(f"  * {action}")

    # 輸出違規項目
    all_violations: list[SkillViolation] = []
    all_violations.extend(report.global_violations)
    for res in report.results:
        all_violations.extend(res.violations)

    if all_violations:
        print(f"\n[檢出違規項目 (共 {len(all_violations)} 項)]:")
        for idx, v in enumerate(all_violations, start=1):
            print(f"  {idx}. {v}")
    else:
        print("\n[檢查狀態] 所有檢查項目皆合規，無任何違規情事！")

    if verbose and report.results:
        print("\n[詳細技能清單]")
        for r in report.results:
            status = "PASS" if r.is_valid else "FAIL"
            print(f"  - [{r.tier}] {r.skill_name:<36} : {status}")

    print("\n" + "-" * 70)
    print(f"  檢查統計: Tier-1 技能數 = {report.tier1_skills_checked} (預期基準: 10)")
    print(f"            Tier-2 技能數 = {report.tier2_skills_checked} (預期基準: 30)")
    print(f"            總檢查技能數 = {report.total_skills_checked}")
    print(f"            錯誤 (ERROR)   = {report.total_errors}")
    print(f"            警告 (WARNING) = {report.total_warnings}")
    print("-" * 70)

    if report.is_passed:
        print("  門禁判決: [PASS] 靜態檢查全數合規，准予進入 Stage 1 下一步。")
    else:
        print("  門禁判決: [FAIL] 存在不合規項目，請修復上述錯誤後重試。")
    print("=" * 70 + "\n")


def build_arg_parser() -> argparse.ArgumentParser:
    """建立命令列參數解析器"""
    parser = argparse.ArgumentParser(
        description="Stage 1 技能庫靜態檢查與合規門禁工具 (Skills CI & Validator)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    tier_group = parser.add_mutually_exclusive_group()
    tier_group.add_argument(
        "--tier1-only",
        action="store_true",
        help="僅對 Tier-1 技能（agents/skills/）進行靜態 CI 檢查",
    )
    tier_group.add_argument(
        "--tier2-only",
        action="store_true",
        help="僅對 Tier-2 技能（agents/skills-tier2/）進行靜態 CI 檢查",
    )

    parser.add_argument(
        "--fix-toc",
        action="store_true",
        help="自動為超過 300 行但缺少 TOC 目錄的 Markdown 檔案生成並注入目錄標頭",
    )

    parser.add_argument(
        "--tier1-dir",
        type=Path,
        default=None,
        help="覆蓋預設之 Tier-1 技能目錄路徑",
    )
    parser.add_argument(
        "--tier2-dir",
        type=Path,
        default=None,
        help="覆蓋預設之 Tier-2 技能目錄路徑",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="覆蓋預設之 Git 專案根目錄路徑",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="顯示詳細之各技能檢查通過狀態清單",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """主程式入口"""
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    # 計算預設之 REPO_ROOT (相對於本腳本位於 scripts/skill_governance/)
    script_dir = Path(__file__).resolve().parent
    default_repo_root = script_dir.parents[1]
    repo_root = args.repo_root.resolve() if args.repo_root else default_repo_root

    tier1_dir = args.tier1_dir.resolve() if args.tier1_dir else None
    tier2_dir = args.tier2_dir.resolve() if args.tier2_dir else None

    report = run_full_validation(
        repo_root=repo_root,
        tier1_dir=tier1_dir,
        tier2_dir=tier2_dir,
        tier1_only=args.tier1_only,
        tier2_only=args.tier2_only,
        fix_toc=args.fix_toc,
        verbose=args.verbose,
    )

    print_cli_summary(report, verbose=args.verbose)

    # 全數合規返回 0，任一不合規返回 1
    return 0 if report.is_passed else 1


if __name__ == "__main__":
    sys.exit(main())
