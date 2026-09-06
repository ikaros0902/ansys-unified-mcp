# -*- coding: utf-8 -*-
"""Tier 2 單元測試：純原生 SVG 圖表渲染、自包含 HTML 報告合成與對話摘要測試 (test_report_generator.py)

覆蓋 R5 規範核心要素：
1. charts.py 純原生免外網 SVG 向量圖表渲染器：
   - render_convergence_curve_svg: 半對數力平衡殘差歷史曲線 (含收斂準則)
   - render_psd_response_svg: 雙對數隨機振動 PSD 加速度頻響曲線
   - render_drop_acceleration_svg: 落摔衝擊加速度時域歷程 (含漸層填色與峰值標記)
   - render_energy_balance_svg: LS-DYNA 全域能量平衡 (動能/內能/沙漏能/總能量)
   - render_mop_surface_svg: optiSLang MOP 響應面 2.5D 彩虹色階熱力網格 (含 CoP 徽章)
   - 零外網依賴斷言：所有 SVG 輸出絕對無外部 CDN、外部字體或外部腳本引用
2. generator.py 自包含互動式 HTML 報告合成器 (ReportGenerator.build_overview_html)：
   - 單一免伺服器 HTML 產出 (overview.html)
   - 零外部 CDN 依賴 (無外部 <link>、<script>，全內嵌 CSS/SVG)
   - KPI 核心物理指標卡陣列 (應力、安全係數、變形、頻率、能量)
   - PASS / FAIL / ABORTED 工程裁決徽章與狀態樣式
   - 白底 PNG 雲圖 Base64 內嵌相簿
   - 前置安全閘門與 Sentinel 早期熔斷自愈處方箋診斷區塊
3. ReportGenerator.generate_dialog_summary 高資訊密度 Markdown 對話引用摘要：
   - 專業標準三段式結構、Emoji 狀態標識
   - 核心指標與交付物索引路徑
   - 持久化至沙盒 artifacts/report_summary.md
"""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from typing import Any, Dict, List
import pytest

from ansys_unified_mcp.jobs.manager import JobManager
from ansys_unified_mcp.jobs.models import (
    ExecutionMetadata,
    JobStatusEnum,
    PhysicalMetrics,
    SimulationSummary,
    VerdictEnum,
)
from ansys_unified_mcp.jobs.sandbox import JobSandbox
from ansys_unified_mcp.reporting.charts import (
    render_convergence_curve_svg,
    render_drop_acceleration_svg,
    render_energy_balance_svg,
    render_mop_surface_svg,
    render_psd_response_svg,
)
from ansys_unified_mcp.reporting.generator import ReportGenerator


# ==============================================================================
# 1. charts.py 純原生免外網 SVG 圖表渲染器測試
# ==============================================================================
class TestNativeChartsRenderer:
    """測試純原生 SVG 向量圖表生成器之正確性與免外部連線自包含性。"""

    def _assert_zero_external_links(self, svg_text: str) -> None:
        """輔助斷言：驗證 SVG 中除標準 XML 命名空間外，絕無載入任何外網資源。"""
        # 移除合法的標準 SVG 命名空間
        sanitized = svg_text.replace('xmlns="http://www.w3.org/2000/svg"', "")
        assert "http://" not in sanitized, "SVG 不得包含外部 HTTP 資源連結"
        assert "https://" not in sanitized, "SVG 不得包含外部 HTTPS 資源連結"
        assert "<script" not in sanitized.lower(), "純向量圖表不得含有外部 script"

    def test_render_convergence_curve_svg_valid(self) -> None:
        """驗證半對數力平衡收斂殘差歷史曲線 SVG 渲染。"""
        iterations = [1, 2, 3, 4, 5]
        residuals = [120.0, 15.0, 1.2, 0.08, 0.012]
        criteria = [0.05, 0.05, 0.05, 0.05, 0.05]

        svg = render_convergence_curve_svg(
            iterations=iterations,
            residuals=residuals,
            criteria=criteria,
            title="Nonlinear Equilibrium Iterations",
        )

        assert svg.startswith("<svg") and svg.strip().endswith("</svg>")
        assert "Nonlinear Equilibrium Iterations" in svg
        assert "10^" in svg, "半對數坐標軸應有 10 的次冪標籤"
        assert "polyline" in svg
        assert "殘差 (Residual)" in svg
        assert "準則 (Criterion)" in svg
        self._assert_zero_external_links(svg)

    def test_render_convergence_curve_svg_empty(self) -> None:
        """驗證收斂曲線數據為空時返回安全佔位 SVG。"""
        svg = render_convergence_curve_svg(iterations=[], residuals=[])
        assert "<svg" in svg
        assert "暫無收斂數據" in svg
        self._assert_zero_external_links(svg)

    def test_render_psd_response_svg_valid(self) -> None:
        """驗證雙對數隨機振動 PSD 頻響曲線 SVG 渲染。"""
        frequencies = [20.0, 50.0, 100.0, 500.0, 1000.0, 2000.0]
        response_g2 = [0.005, 0.02, 0.85, 0.15, 0.04, 0.002]
        input_psd = [0.04, 0.04, 0.04, 0.04, 0.04, 0.04]

        svg = render_psd_response_svg(
            frequencies=frequencies,
            response_g2_hz=response_g2,
            input_psd=input_psd,
            title="Random Vibration PSD Response",
        )

        assert "<svg" in svg
        assert "Random Vibration PSD Response" in svg
        assert "Hz" in svg
        assert "G²/Hz" in svg
        assert "結構響應 (Response)" in svg
        assert "輸入譜 (Input)" in svg
        assert "polyline" in svg
        self._assert_zero_external_links(svg)

    def test_render_psd_response_svg_empty(self) -> None:
        """驗證 PSD 數據為空時返回安全佔位 SVG。"""
        svg = render_psd_response_svg(frequencies=[], response_g2_hz=[])
        assert "<svg" in svg
        assert "暫無 PSD 數據" in svg
        self._assert_zero_external_links(svg)

    def test_render_drop_acceleration_svg_valid(self) -> None:
        """驗證落摔衝擊加速度歷程圖 SVG 渲染 (含漸層與峰值標記)。"""
        time_ms = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
        acc_g = [0.0, 12.0, 55.0, 120.0, 185.4, 110.0, 45.0, 8.0, 0.0]

        svg = render_drop_acceleration_svg(
            time_ms=time_ms,
            acceleration_g=acc_g,
            title="Drop Impact Pulse",
        )

        assert "<svg" in svg
        assert "Drop Impact Pulse" in svg
        assert "linearGradient id=\"dropGrad\"" in svg, "應包含漸層定義"
        assert "polygon" in svg, "應包含漸層填色多邊形"
        assert "circle" in svg, "應標註峰值點"
        assert "峰值: 185.4G" in svg, "應明確標記峰值加速度數值"
        self._assert_zero_external_links(svg)

    def test_render_drop_acceleration_svg_empty(self) -> None:
        """驗證落摔數據為空時返回安全佔位 SVG。"""
        svg = render_drop_acceleration_svg(time_ms=[], acceleration_g=[])
        assert "<svg" in svg
        assert "暫無落摔加速度數據" in svg
        self._assert_zero_external_links(svg)

    def test_render_energy_balance_svg_valid(self) -> None:
        """驗證 LS-DYNA 全域能量平衡曲線 SVG 渲染 (動能/內能/沙漏能/總能)。"""
        time_s = [0.0005 * i for i in range(6)]
        ke = [500.0, 400.0, 250.0, 100.0, 50.0, 20.0]
        ie = [0.0, 100.0, 240.0, 380.0, 430.0, 455.0]
        hg = [0.0, 2.0, 5.0, 7.5, 8.2, 8.8]
        tot = [500.0, 502.0, 495.0, 487.5, 488.2, 483.8]

        svg = render_energy_balance_svg(
            time_s=time_s,
            kinetic_e=ke,
            internal_e=ie,
            hourglass_e=hg,
            total_e=tot,
            title="LS-DYNA Energy Balance",
        )

        assert "<svg" in svg
        assert "LS-DYNA Energy Balance" in svg
        assert "動能 (KE)" in svg
        assert "內能 (IE)" in svg
        assert "沙漏能 (HG)" in svg
        assert "總能 (Total)" in svg
        assert svg.count("polyline") >= 4, "應至少包含 4 條能量折線"
        self._assert_zero_external_links(svg)

    def test_render_mop_surface_svg_valid(self) -> None:
        """驗證 optiSLang MOP 響應面 2.5D 熱力色階網格 SVG 渲染。"""
        x_grid = [1.0, 1.5, 2.0, 2.5, 3.0]
        y_grid = [10.0, 15.0, 20.0, 25.0, 30.0]
        z_matrix = [
            [120.0 + i * 10 + j * 5 for i in range(len(x_grid))]
            for j in range(len(y_grid))
        ]

        svg = render_mop_surface_svg(
            x_grid=x_grid,
            y_grid=y_grid,
            z_matrix=z_matrix,
            x_label="Thickness (mm)",
            y_label="Width (mm)",
            z_label="Peak Stress (MPa)",
            title="MOP Stress Response Surface",
            cop_score=0.915,
        )

        assert "<svg" in svg
        assert "MOP Stress Response Surface" in svg
        assert "CoP = 91.5%" in svg, "應包含 CoP 精度百分比標籤"
        assert "Thickness (mm)" in svg
        assert "Peak Stress (MPa)" in svg
        assert "<rect" in svg
        self._assert_zero_external_links(svg)


# ==============================================================================
# 2. generator.py 自包含 HTML 報告合成器測試
# ==============================================================================
class TestOverviewHtmlGeneration:
    """測試 ReportGenerator 生成自包含、免伺服器之 overview.html。"""

    def _create_sample_summary(
        self,
        job_id: str,
        status: JobStatusEnum = JobStatusEnum.SOLVED,
        verdict: VerdictEnum = VerdictEnum.PASS,
        is_breaker: bool = False,
    ) -> SimulationSummary:
        """輔助建立標準測試 SimulationSummary。"""
        return SimulationSummary(
            job_id=job_id,
            workflow_type="thermal_warpage",
            tag="pcb_cooling",
            status=status,
            verdict=verdict,
            failure_reasons=[] if verdict == VerdictEnum.PASS else ["物理門檻超標"],
            metrics=PhysicalMetrics(
                max_equivalent_stress_mpa=94.25,
                material_yield_strength_mpa=180.0,
                safety_factor=1.91,
                max_total_deformation_mm=0.128,
                max_warpage_z_um=128.0,
                first_mode_frequency_hz=145.5,
                effective_mass_ratio_x=0.925,
                effective_mass_ratio_y=0.912,
                effective_mass_ratio_z=0.940,
                hourglass_energy_ratio_pct=1.5,
                mass_scaling_added_pct=0.05,
                cop_score=0.88,
                final_convergence_residual=0.0035,
            ),
            execution=ExecutionMetadata(
                created_at="2026-09-06T09:00:00Z",
                finished_at="2026-09-06T09:02:15Z",
                duration_seconds=135.0,
                solver_name="ANSYS Mechanical",
                solver_version="2026 R1",
                pid=54321,
                exit_code=0 if verdict == VerdictEnum.PASS else 1,
                circuit_breaker_triggered=is_breaker,
                circuit_breaker_reason="[CB-DYNA-003] 沙漏能超標 6.65%" if is_breaker else None,
            ),
            artifacts={},
        )

    def test_build_overview_html_pass_verdict(self, tmp_path: Path) -> None:
        """驗證 PASS 裁決之 overview.html 自包含性、零外網 CDN 依賴與 KPI 卡片呈現。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("thermal_warpage", tag="pcb_run")
        summary = self._create_sample_summary(sandbox.job_id, status=JobStatusEnum.SOLVED, verdict=VerdictEnum.PASS)
        sandbox.save_summary(summary)

        generator = ReportGenerator()
        chart_data = {
            "convergence": {
                "iterations": [1, 2, 3],
                "residuals": [10.0, 1.0, 0.01],
                "criteria": [0.05, 0.05, 0.05],
            },
            "drop": {
                "time_ms": [0.0, 1.0, 2.0],
                "acceleration_g": [0.0, 50.0, 0.0],
            },
        }

        html_path = generator.build_overview_html(
            sandbox=sandbox,
            summary=summary,
            chart_data=chart_data,
            embed_images_base64=True,
        )

        assert html_path.exists(), "overview.html 檔案必須成功生成"
        content = html_path.read_text(encoding="utf-8")

        # 1. 嚴格驗證自包含性 (Zero External CDN Guarantee)
        assert not re.search(r'<link[^>]+href=["\']http', content, re.IGNORECASE), "禁止外部 CDN CSS 連結"
        assert not re.search(r'<script[^>]+src=["\']http', content, re.IGNORECASE), "禁止外部 CDN JS 腳本"
        assert not re.search(r'@import\s+url\(["\']?http', content, re.IGNORECASE), "禁止外部字體載入"
        assert "<style>" in content, "樣式必須內嵌於 <style> 標籤中"
        assert "<svg" in content, "圖表必須以內嵌 SVG 呈現"

        # 2. 驗證 Header 與 PASS 徽章
        assert sandbox.job_id in content
        assert "verdict-pass" in content
        assert "PASS" in content

        # 3. 驗證 KPI 核心數值與單位
        assert "94.25 MPa" in content
        assert "180.00 MPa" in content
        assert "1.91" in content
        assert "0.128 mm" in content
        assert "145.50 Hz" in content
        assert "1.50%" in content  # 沙漏能
        assert "88.0%" in content   # CoP

        # 4. 驗證產生物索引已持久化回 summary.json
        updated_summary = sandbox.get_summary()
        assert updated_summary is not None
        assert "overview_html" in updated_summary.artifacts
        assert str(html_path) == updated_summary.artifacts["overview_html"]

    def test_build_overview_html_aborted_with_circuit_breaker(self, tmp_path: Path) -> None:
        """驗證早期發散熔斷 (ABORTED) 狀態之 HTML 標記與自愈處方箋區塊展示。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("drop_test", tag="aborted_run")
        summary = self._create_sample_summary(
            sandbox.job_id,
            status=JobStatusEnum.ABORTED,
            verdict=VerdictEnum.FAIL,
            is_breaker=True,
        )
        sandbox.save_summary(summary)

        generator = ReportGenerator()
        html_path = generator.build_overview_html(sandbox=sandbox, summary=summary)
        content = html_path.read_text(encoding="utf-8")

        assert "verdict-aborted" in content
        assert "ABORTED" in content
        assert "CIRCUIT BREAKER TRIGGERED" in content
        assert "[CB-DYNA-003] 沙漏能超標 6.65%" in content

    def test_build_overview_html_with_base64_embedded_images(self, tmp_path: Path) -> None:
        """驗證當沙盒內有 PNG 雲圖時，自動轉為 Base64 內嵌以達成離線免伺服器檢視。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("static_structural", tag="contour_test")
        summary = self._create_sample_summary(sandbox.job_id)
        sandbox.save_summary(summary)

        # 建立模擬 PNG 檔案
        test_png = sandbox.images_dir / "stress_von_mises.png"
        sample_png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\xf8\xff\xff"
            b"?\x00\x05\xfe\x02\xfe\xa74e\xd8\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        test_png.write_bytes(sample_png_bytes)

        generator = ReportGenerator()
        html_path = generator.build_overview_html(sandbox=sandbox, summary=summary, embed_images_base64=True)
        content = html_path.read_text(encoding="utf-8")

        # 斷言包含 Base64 圖片編碼
        assert "data:image/png;base64," in content
        expected_b64 = base64.b64encode(sample_png_bytes).decode("ascii")
        assert expected_b64 in content
        assert "Stress Von Mises" in content

    def test_build_overview_html_missing_summary_raises_error(self, tmp_path: Path) -> None:
        """驗證當沙盒缺少 summary.json 時，拋出適當之 ValueError。"""
        sandbox = JobSandbox("test_missing", tmp_path / "sandbox")
        sandbox.initialize()
        generator = ReportGenerator()

        with pytest.raises(ValueError, match="缺少 summary.json"):
            generator.build_overview_html(sandbox=sandbox, summary=None)


# ==============================================================================
# 3. ReportGenerator.generate_dialog_summary Markdown 摘要生成測試
# ==============================================================================
class TestDialogSummaryGeneration:
    """測試 generate_dialog_summary 生成高資訊密度 Markdown 對話摘要。"""

    def test_generate_dialog_summary_pass_format(self, tmp_path: Path) -> None:
        """驗證 PASS 裁決之 Markdown 格式符合林明志專家架構對齊要求。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("shock_analysis", tag="half_sine")

        summary = SimulationSummary(
            job_id=sandbox.job_id,
            workflow_type="shock_analysis",
            tag="half_sine",
            status=JobStatusEnum.SOLVED,
            verdict=VerdictEnum.PASS,
            metrics=PhysicalMetrics(
                max_equivalent_stress_mpa=112.5,
                material_yield_strength_mpa=250.0,
                safety_factor=2.22,
                max_total_deformation_mm=0.345,
                first_mode_frequency_hz=88.2,
                hourglass_energy_ratio_pct=1.2,
                mass_scaling_added_pct=0.01,
            ),
            execution=ExecutionMetadata(
                created_at="2026-09-06T09:00:00Z",
                duration_seconds=42.5,
                solver_name="LS-DYNA",
            ),
            artifacts={
                "overview_html": "F:/jobs/overview.html",
                "summary_json": "F:/jobs/summary.json",
                "contour_image": "F:/jobs/stress.png",
            },
        )

        generator = ReportGenerator()
        md_text = generator.generate_dialog_summary(summary=summary, sandbox=sandbox)

        # 斷言標頭與工況
        assert f"### 📊 ANSYS CAE 模擬分析報告：[{sandbox.job_id}]" in md_text
        assert "- **分析工況**：SHOCK_ANALYSIS（標籤：`half_sine`）" in md_text
        assert "- **最終判定**：✅ **PASS**" in md_text

        # 斷言工程指標
        assert "最大等效應力：`112.50 MPa`" in md_text
        assert "安全係數：`2.22`" in md_text
        assert "最大翹曲/變形：`0.345 mm`" in md_text
        assert "一階特徵頻率：`88.20 Hz`" in md_text
        assert "沙漏能 `1.20%`" in md_text
        assert "質量縮放 `0.01%`" in md_text

        # 斷言標準交付物索引
        assert "互動式儀表板：`F:/jobs/overview.html`" in md_text
        assert "機器可讀數據：`F:/jobs/summary.json`" in md_text

        # 斷言持久化至沙盒 artifacts/report_summary.md
        saved_md = sandbox.artifacts_dir / "report_summary.md"
        assert saved_md.exists(), "Markdown 摘要應儲存至 artifacts/report_summary.md"
        assert saved_md.read_text(encoding="utf-8") == md_text

    def test_generate_dialog_summary_aborted_with_prescription(self) -> None:
        """驗證早期熔斷 (ABORTED) 之對話摘要包含警告 Emoji 與自愈處方箋段落。"""
        summary = SimulationSummary(
            job_id="20260906_090000_abort_test",
            workflow_type="drop_test",
            tag="fall_1m",
            status=JobStatusEnum.ABORTED,
            verdict=VerdictEnum.FAIL,
            failure_reasons=["沙漏能超標 6.65% > 5.0%"],
            metrics=PhysicalMetrics(hourglass_energy_ratio_pct=6.65),
            execution=ExecutionMetadata(
                created_at="2026-09-06T09:00:00Z",
                duration_seconds=12.0,
                solver_name="LS-DYNA",
                circuit_breaker_triggered=True,
                circuit_breaker_reason="[CB-DYNA-003] 改用剛度型沙漏 (IHQ=4/5)",
            ),
            artifacts={},
        )

        generator = ReportGenerator()
        md_text = generator.generate_dialog_summary(summary=summary)

        assert "⚠️ **FAIL**（狀態：`ABORTED`）" in md_text
        assert "**⚠️ 異常與熔斷排查記錄**：" in md_text
        assert "沙漏能超標 6.65% > 5.0%" in md_text
        assert "**🛡️ Sentinel 早期物理熔斷處方箋**：" in md_text
        assert "[CB-DYNA-003] 改用剛度型沙漏" in md_text
