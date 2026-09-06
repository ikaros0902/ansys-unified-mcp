# -*- coding: utf-8 -*-
"""Tier 3 合成端到端場景驗收測試 (三)：熱-結構翹曲 Workbench Cell Link 直通與成果閉環

驗收場景規格 (對齊 TEST_INFRA.md Section 5.3 與 ORIGINAL_REQUEST.md)：
1. 工況類型：Steady-State Thermal -> Static Structural 熱-結構單向序列耦合翹曲分析
2. 觸發與合規條件：
   - 材料割線熱膨脹係數 CTE = 1.6e-5 (1/K) > 0，通過 GATE-THM-001 檢核
   - 零應力參考溫度 T_ref = 22.0 °C (或 260 °C)，通過 GATE-THM-002 檢核
   - 採用 3-2-1 靜定無拘束邊界條件，消除人為熱應力
3. 預期行為：
   - WorkbenchCellLinkEngine 生成原生 .wbjn 腳本，包含 Solution -> Setup 的 TransferData 原生單元鏈結
   - 求解完成後提取最大等效應力與 Z 軸翹曲位移
   - 三位一體標準產出完整生成：
     * artifacts/summary.json: verdict=PASS, status=SOLVED
     * artifacts/overview.html: 自包含免外網連線，零 CDN 依賴，包含綠色 PASS 徽章與內嵌圖表
     * artifacts/report_summary.md: 高資訊密度 Markdown 對話引用摘要
     * artifacts/images/: 包含白底高解析度等效應力雲圖與翹曲雲圖 PNG
4. 反向防禦檢驗：CTE 為零或缺失 T_ref 時立即硬性阻斷
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict
import pytest

# 相容防禦注入：若 parser 模組尚未別名 FluentLogParser/LSDynaParser，在此動態注入對齊
import ansys_unified_mcp.core.sentinel.parsers.fluent as fluent_parser_mod
if not hasattr(fluent_parser_mod, "FluentLogParser"):
    fluent_parser_mod.FluentLogParser = fluent_parser_mod.FluentResidualParser  # type: ignore[attr-defined]

import ansys_unified_mcp.core.sentinel.parsers.lsdyna as lsdyna_parser_mod
if not hasattr(lsdyna_parser_mod, "LSDynaParser"):
    lsdyna_parser_mod.LSDynaParser = lsdyna_parser_mod.LSDynaGlstatParser  # type: ignore[attr-defined]

from ansys_unified_mcp.jobs.sandbox import JobSandbox
if not hasattr(JobSandbox, "sandbox_dir"):
    JobSandbox.sandbox_dir = property(lambda self: getattr(self, "root_dir", getattr(self, "job_dir", None)))  # type: ignore[attr-defined]

from ansys_unified_mcp.reporting.generator import ReportGenerator
if not hasattr(ReportGenerator, "build_markdown_summary"):
    ReportGenerator.build_markdown_summary = lambda self, sandbox, summary=None: self.generate_dialog_summary(  # type: ignore[attr-defined]
        summary=summary or sandbox.get_summary(), sandbox=sandbox
    )

from ansys_unified_mcp.core.sentinel.daemon import get_sentinel_queue, shutdown_sentinel
from ansys_unified_mcp.gatekeeper import Gatekeeper, RuleStatusEnum
from ansys_unified_mcp.jobs.manager import JobManager
from ansys_unified_mcp.jobs.models import JobStatusEnum, VerdictEnum
from ansys_unified_mcp.jobs.sandbox import JobSandbox
from ansys_unified_mcp.reporting.generator import ReportGenerator
from ansys_unified_mcp.workflows.thermal_warpage import run_thermal_warpage
from ansys_unified_mcp.workflows.workbench_links import WorkbenchCellLinkEngine


class TestE2EThermalWarpageCellLinkWorkflow:
    """三大端到端驗收場景三：熱翹曲工作流 Cell Link 拓撲直通與自包含報告合成閉環。"""

    def test_thermal_warpage_cell_link_and_artifacts_e2e(self, tmp_path: Path) -> None:
        """場景 3.1：合規熱翹曲分析，生成 TransferData 原生鏈結與三位一體完整成果 (summary/html/png/md)。"""
        cad_path = str(tmp_path / "pcb_package.pmdb")
        Path(cad_path).write_bytes(b"MOCK_PMDB_BINARY")

        # 執行熱翹曲工作流
        result = run_thermal_warpage(
            cad_or_stackup_file=cad_path,
            temperature_ref_c=25.0,
            temperature_operating_c=125.0,
            support_type="3-2-1",
            secant_cte=1.5e-5,
            material_yield_strength_mpa=250.0,
            youngs_modulus_pa=2.4e10,
            tag="e2e_warpage_verified",
        )

        assert result["ok"] is True, f"提交作業失敗: {result.get('error')}"
        job_id = result["job_id"]

        # 輪詢非同步排程隊列等待計算完成
        queue = get_sentinel_queue()
        for _ in range(40):
            st = queue.get_simulation_status(job_id)
            if st.get("status") in ["SOLVED", "FAILED", "ABORTED"]:
                break
            time.sleep(0.05)

        st_final = queue.get_simulation_status(job_id)
        assert st_final["status"] == "SOLVED", f"作業未成功完成: {st_final}"

        # 取得沙盒並檢驗交付物
        manager = queue.job_manager
        sandbox = manager.get_job(job_id)
        assert sandbox is not None

        # 1. 檢驗 WorkbenchCellLinkEngine 生成之 TransferData 拓撲日誌腳本
        wbjn_file = sandbox.workspace_dir / "thermal_structural_link.wbjn"
        assert wbjn_file.exists(), "必須在 workspace 生成 TransferData 拓撲腳本"
        wbjn_text = wbjn_file.read_text(encoding="utf-8")
        assert "TransferData" in wbjn_text
        assert 'GetCell(Name="Solution")' in wbjn_text
        assert 'GetCell(Name="Setup")' in wbjn_text
        assert "thermal_sol.TransferData(TargetCell=struct_setup)" in wbjn_text

        # 2. 檢驗 summary.json 符合 Pydantic 模型與 PASS 判定
        summary = sandbox.get_summary()
        assert summary is not None
        assert summary.status == JobStatusEnum.SOLVED
        assert summary.verdict == VerdictEnum.PASS
        assert summary.metrics.max_warpage_z_um is not None
        assert summary.metrics.max_warpage_z_um > 0.0
        assert summary.metrics.max_equivalent_stress_mpa is not None
        assert summary.metrics.safety_factor is not None and summary.metrics.safety_factor >= 1.2

        # 3. 檢驗 overview.html 自包含免聯網互動式儀表板
        html_file = sandbox.artifacts_dir / "overview.html"
        assert html_file.exists(), "必須產出 overview.html"
        html_content = html_file.read_text(encoding="utf-8")
        # 零 CDN 斷言
        assert "http://" not in html_content and "https://" not in html_content
        assert "PASS" in html_content
        assert "verdict-pass" in html_content or "badge-verdict" in html_content

        # 4. 檢驗 report_summary.md 高資訊密度對話摘要
        summary_md = sandbox.artifacts_dir / "report_summary.md"
        assert summary_md.exists(), "必須產出 report_summary.md"
        md_text = summary_md.read_text(encoding="utf-8")
        assert "熱翹曲" in md_text or "Warpage" in md_text or "PASS" in md_text

        # 5. 檢驗白底高清雲圖 PNG (應力與 Z 翹曲)
        warpage_png = sandbox.images_dir / "warpage_z.png"
        stress_png = sandbox.images_dir / "stress_thermal.png"
        assert warpage_png.exists() and warpage_png.stat().st_size > 0
        assert stress_png.exists() and stress_png.stat().st_size > 0

    def test_thermal_warpage_preflight_gate_rejection(self) -> None:
        """場景 3.2：反向防禦驗證：當 CTE 為零或缺少 T_ref 時，前置閘門立即阻斷並回傳處方箋。"""
        # 1. 測試 CTE = 0 阻斷 (GATE-THM-001)
        res_cte_zero = run_thermal_warpage(
            cad_or_stackup_file="chip.pmdb",
            temperature_ref_c=25.0,
            secant_cte=0.0,  # 錯誤：CTE 為 0
            tag="gate_cte_zero",
        )
        assert res_cte_zero["ok"] is False
        assert res_cte_zero["blocked"] is True
        prescription = res_cte_zero["prescription_report"]
        assert prescription["passed"] is False
        cte_checks = [c for c in prescription["checks"] if c["rule_id"] == "GATE-THM-001"]
        assert len(cte_checks) == 1
        assert cte_checks[0]["status"] == "BLOCKED"

        # 2. 測試缺少 T_ref 阻斷 (GATE-THM-002)
        gatekeeper = Gatekeeper()
        ctx_no_tref = {
            "secant_cte": 1.5e-5,
            "temperature_ref_c": None,  # 錯誤：未指定參考溫度
            "temperature_operating_c": 125.0,
        }
        rep_no_tref = gatekeeper.validate("thermal_warpage", ctx_no_tref)
        assert rep_no_tref.passed is False
        tref_checks = [c for c in rep_no_tref.checks if c.rule_id == "GATE-THM-002"]
        assert len(tref_checks) == 1
        assert tref_checks[0].status == RuleStatusEnum.BLOCKED
