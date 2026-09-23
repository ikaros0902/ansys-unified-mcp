# -*- coding: utf-8 -*-
"""
技能生態系架構稽核納管測試。

背景：`scripts/audit_architecture_compliance.py` 原本僅能手動執行，
其 exit code 不被任何自動化關卡檢查，導致「測試全綠、稽核 FAIL」兩者互不知情。
本測試將該稽核納入 pytest，使死鏈、SKILL.md 行數超標、簡體字違規與
示範腳本語法錯誤等問題，能在測試階段即被客觀攔截。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUDIT_SCRIPT = PROJECT_ROOT / "scripts" / "audit_architecture_compliance.py"
SYNC_SCRIPT = PROJECT_ROOT / "scripts" / "sync_skills_bidirectional.py"
SKILLS_ROOT = PROJECT_ROOT / "SKILLs"


def _run(script: Path, *args: str) -> subprocess.CompletedProcess:
    """以當前 Python 解譯器執行指定腳本並擷取輸出"""
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )


@pytest.mark.skipif(not AUDIT_SCRIPT.is_file(), reason="稽核腳本不存在")
def test_skills_architecture_audit_passes():
    """稽核腳本必須以 exit code 0 結束（客觀驗收條件，非主觀判定）"""
    result = _run(AUDIT_SCRIPT)
    assert result.returncode == 0, (
        "技能架構稽核未通過 (exit code "
        f"{result.returncode})。\n--- STDOUT ---\n{result.stdout}\n"
        f"--- STDERR ---\n{result.stderr}"
    )


def test_skill_routing_tables_have_no_dead_links():
    """
    SKILL.md 路由表所指向的相對路徑檔案必須實際存在。

    此檢查與稽核腳本重疊，但獨立實作以確保死鏈本身有專屬斷言：
    稽核腳本涵蓋多項檢查，任一項失敗都會使 exit code 非 0，
    單獨斷言死鏈可讓失敗訊息直接定位問題類型。
    """
    import re

    link_pattern = re.compile(r"\]\((?!https?://|#)([^)]+)\)")
    dead_links: list[str] = []

    for skill_md in sorted(SKILLS_ROOT.glob("*/SKILL.md")):
        content = skill_md.read_text(encoding="utf-8", errors="replace")
        for rel_target in link_pattern.findall(content):
            target = rel_target.split("#", 1)[0].strip()
            if not target:
                continue
            if not (skill_md.parent / target).exists():
                dead_links.append(f"{skill_md.parent.name}/SKILL.md => {target}")

    assert not dead_links, "偵測到 SKILL.md 路由表死鏈:\n" + "\n".join(dead_links)


@pytest.mark.skipif(not SYNC_SCRIPT.is_file(), reason="同步腳本不存在")
def test_sync_does_not_delete_global_only_files_by_default():
    """
    回歸測試：雙向同步的預設行為不得刪除僅存在於全域端的檔案。

    原實作將全域端獨有檔案一律刪除，會使尚未回流專案端的 reference/ 與
    scripts/ 內容永久遺失，並導致專案端 SKILL.md 產生死鏈。
    """
    source = SYNC_SCRIPT.read_text(encoding="utf-8", errors="replace")

    assert "prune_global" in source, "同步腳本缺少 prune_global 防護旗標"
    assert "--prune-global" in source, "同步腳本未提供 --prune-global CLI 旗標"

    # 定位「僅存在於全域端」分支，確認預設路徑為回補而非刪除
    marker = "elif g_meta and not p_meta:"
    assert marker in source, "找不到全域端獨有檔案的處理分支"
    branch = source.split(marker, 1)[1][:1200]
    assert "self.prune_global" in branch, "全域端獨有檔案的刪除行為未受 prune_global 閘門保護"
    assert "copy_file" in branch, "全域端獨有檔案的預設行為應為回補至專案端"
