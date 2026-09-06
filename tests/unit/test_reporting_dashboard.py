# -*- coding: utf-8 -*-
"""Tier 2 單元測試：R5 自包含互動式 HTML 儀表板與報告合成器測試

覆蓋 R5 規範核心要件：
1. charts.py 純原生免外網 SVG 圖表生成 (收斂殘差、PSD 頻響、落摔加速度、能量平衡、MOP 響應面)
2. 零外部 CDN 依賴性核驗 (斷網離線自包含)
3. ReportGenerator 合成 overview.html 包含五大核心模組 (Header, KPI, Charts, Gallery, Diagnostics)
4. 白底雲圖相簿 Base64 內嵌與燈箱整合
5. generate_dialog_summary 繁體中文高資訊密度 Markdown 摘要
"""

from __future__ import annotations

from pathlib import Path
import pytest

from ansys_unified_mcp.jobs.manager import JobManager
from ansys_unified_mcp.jobs.models import (
    ExecutionMetadata,
    JobStatusEnum,
    PhysicalMetrics,
    SimulationSummary,
    VerdictEnum,
)
from ansys_unified_mcp.reporting.charts import (
    render_convergence_curve_svg,
    render_drop_acceleration_svg,
    render_energy_balance_svg,
    render_mop_surface_svg,
    render_psd_response_svg,
)
from ansys_unified_mcp.reporting.generator import ReportGenerator


class TestNativeSvgCharts:
    """測試純原生免外網向量圖表渲染。"""

    def test_render_convergence_curve_svg(self) -> None:
        """驗證力平衡收斂殘差半對數曲線 SVG 結構。"""
        iters = [1, 2, 3, 4, 5]
        residuals = [1500.0, 120.0, 15.0, 2.5, 0.45]
        criteria = [50.0, 50.0, 50.0, 50.0, 50.0]

        svg = render_convergence_curve_svg(
            iterations=iters,
            residuals=residuals,
            criteria=criteria,
            title="力收斂測試曲線",
        )

        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")
        assert "力收斂測試曲線" in svg
        assert "10^" in svg, "應包含對數坐標刻度"
        assert "polyline" in svg, "應包含折線數據元素"

    def test_render_psd_response_svg(self) -> None:
        """驗證隨機振動雙對數 PSD 曲線 SVG 結構。"""
        freqs = [20.0, 50.0, 100.0, 200.0, 500.0, 1000.0]
        resp = [0.001, 0.05, 0.85, 0.12, 0.02, 0.005]
        input_p = [0.04, 0.04, 0.04, 0.04, 0.04, 0.04]

        svg = render_psd_response_svg(
            frequencies=freqs,
            response_g2_hz=resp,
            input_psd=input_p,
            title="PSD 響應測試",
        )

        assert "<svg" in svg
        assert "PSD 響應測試" in svg
        assert "結構響應" in svg
        assert "Hz" in svg

    def test_render_drop_acceleration_svg(self) -> None:
        """驗證落摔加速度時域歷程曲線 SVG 與峰值標籤。"""
        t_ms = [0.0, 1.0, 2.0, 2.5, 3.0, 4.0, 5.0]
        acc_g = [0.0, 12.5, 85.0, 142.6, 60.0, 10.0, 0.0]

        svg = render_drop_acceleration_svg(
            time_ms=t_ms,
            acceleration_g=acc_g,
            title="落摔加速度歷程",
        )

        assert "<svg" in svg
        assert "落摔加速度歷程" in svg
        assert "峰值: 142.6G" in svg, "應自動標註加速度峰值"
        assert "polygon" in svg, "應具備漸變填色區塊"

    def test_render_energy_balance_svg(self) -> None:
        """驗證 LS-DYNA 能量平衡曲線 SVG。"""
        time_s = [0.0, 0.001, 0.002, 0.003]
        ke = [500.0, 350.0, 100.0, 20.0]
        ie = [0.0, 150.0, 390.0, 470.0]
        hg = [0.0, 2.0, 8.0, 12.0]
        tot = [500.0, 502.0, 498.0, 502.0]

        svg = render_energy_balance_svg(
            time_s=time_s,
            kinetic_e=ke,
            internal_e=ie,
            hourglass_e=hg,
            total_e=tot,
        )

        assert "<svg" in svg
        assert "動能 (KE)" in svg
        assert "沙漏能 (HG)" in svg
        assert "內能 (IE)" in svg

    def test_render_mop_surface_svg(self) -> None:
        """驗證 optiSLang MOP 響應面網格 SVG 與色階條。"""
        x_grid = [1.0, 1.5, 2.0]
        y_grid = [10.0, 20.0, 30.0]
        z_matrix = [
            [120.0, 140.0, 160.0],
            [130.0, 155.0, 180.0],
            [150.0, 175.0, 210.0],
        ]

        svg = render_mop_surface_svg(
            x_grid=x_grid,
            y_grid=y_grid,
            z_matrix=z_matrix,
            cop_score=0.88,
        )

        assert "<svg" in svg
        assert "CoP = 88.0%" in svg
        assert "rect" in svg, "應包含色塊矩陣與 ColorBar"

    def test_charts_empty_fallback(self) -> None:
        """驗證無數據時之安全降級防禦。"""
        svg = render_convergence_curve_svg([], [])
        assert "<svg" in svg
        assert "暫無" in svg


class TestReportGenerator:
    """測試報告合成器與自包含 overview.html。"""

    def test_build_overview_html_complete_bundle(self, tmp_path: Path) -> None:
        """驗證 overview.html 生成：包含 KPI、圖表、Base64 雲圖、診斷日誌，零外網依賴。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("drop_test", tag="html_report_test")

        # 寫入測試雲圖
        dummy_png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
            b"\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
            b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        (sandbox.images_dir / "stress_von_mises.png").write_bytes(dummy_png)
        (sandbox.images_dir / "deformation_total.png").write_bytes(dummy_png)

        # 更新 summary 物理數值
        summary = sandbox.get_summary()
        assert summary is not None
        summary.status = JobStatusEnum.SOLVED
        summary.verdict = VerdictEnum.PASS
        summary.metrics = PhysicalMetrics(
            max_equivalent_stress_mpa=185.4,
            material_yield_strength_mpa=310.0,
            safety_factor=1.67,
            max_total_deformation_mm=0.428,
            first_mode_frequency_hz=145.2,
            hourglass_energy_ratio_pct=2.15,
            mass_scaling_added_pct=0.45,
            cop_score=0.92,
        )
        summary.execution = ExecutionMetadata(
            created_at="2026-09-06T08:00:00Z",
            finished_at="2026-09-06T08:05:32Z",
            duration_seconds=332.0,
            solver_name="LS-DYNA",
            solver_version="R14.1",
        )
        sandbox.save_summary(summary)

        # 提供圖表數據
        chart_data = {
            "drop": {
                "time_ms": [0.0, 1.0, 2.0, 3.0, 4.0],
                "acceleration_g": [0.0, 40.0, 120.5, 45.0, 5.0],
            },
            "energy": {
                "time_s": [0.0, 0.001, 0.002, 0.003, 0.004],
                "kinetic_e": [300.0, 200.0, 50.0, 10.0, 5.0],
                "internal_e": [0.0, 98.0, 245.0, 280.0, 290.0],
                "hourglass_e": [0.0, 1.2, 4.5, 6.0, 6.2],
            },
        }

        generator = ReportGenerator()
        html_path = generator.build_overview_html(
            sandbox=sandbox,
            summary=summary,
            chart_data=chart_data,
            embed_images_base64=True,
        )

        assert html_path.exists()
        content = html_path.read_text(encoding="utf-8")

        # 檢核關鍵工程要素
        assert summary.job_id in content
        assert "185.40 MPa" in content
        assert "310.00 MPa" in content
        assert "1.67" in content
        assert "0.428 mm" in content
        assert "145.20 Hz" in content
        assert "PASS" in content
        assert "data:image/png;base64," in content, "應包含 Base64 內嵌雲圖"

        # 檢核零外部 CDN 依賴 (無外部 script 或外部 stylesheet link)
        assert "<script src=\"http" not in content
        assert "<link rel=\"stylesheet\" href=\"http" not in content
        assert "cdn" not in content.lower()

    def test_generate_dialog_summary_markdown(self, tmp_path: Path) -> None:
        """驗證 Markdown 對話摘要高資訊密度產出。"""
        manager = JobManager(base_jobs_dir=tmp_path / "jobs")
        sandbox = manager.create_job("random_vibration", tag="pcb_vib")

        summary = sandbox.get_summary()
        assert summary is not None
        summary.status = JobStatusEnum.SOLVED
        summary.verdict = VerdictEnum.PASS
        summary.metrics = PhysicalMetrics(
            max_equivalent_stress_mpa=95.6,
            safety_factor=2.45,
            max_total_deformation_mm=0.125,
            first_mode_frequency_hz=215.0,
            hourglass_energy_ratio_pct=0.0,
            mass_scaling_added_pct=0.0,
        )
        sandbox.save_summary(summary)

        generator = ReportGenerator()
        md_text = generator.generate_dialog_summary(summary=summary, sandbox=sandbox)

        assert "### 📊 ANSYS CAE 模擬分析報告" in md_text
        assert summary.job_id in md_text
        assert "95.60 MPa" in md_text
        assert "2.45" in md_text
        assert "0.125 mm" in md_text
        assert "215.00 Hz" in md_text
        assert "PASS" in md_text
        assert (sandbox.artifacts_dir / "report_summary.md").exists()
