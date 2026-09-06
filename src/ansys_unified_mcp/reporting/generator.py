"""ANSYS Unified MCP 2.0 - 自包含 HTML 報告合成器 (ReportGenerator).

將模擬作業沙盒成果 (summary.json, 白底雲圖 PNG, 歷史收斂與物理曲線)
合成為免伺服器、單一檔案自包含之 overview.html 與對話引用 Markdown 摘要。
"""

from __future__ import annotations

import base64
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ansys_unified_mcp.jobs.models import (
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

logger = logging.getLogger("ansys-unified-mcp.reporting.generator")


class ReportGenerator:
    """CAE 報告合成器。"""

    TEMPLATE_PATH = Path(__file__).parent / "templates" / "overview.html"

    def __init__(self, template_path: Optional[Path | str] = None) -> None:
        self.template_path = Path(template_path) if template_path else self.TEMPLATE_PATH

    def build_overview_html(
        self,
        sandbox: JobSandbox,
        summary: Optional[SimulationSummary] = None,
        chart_data: Optional[Dict[str, Any]] = None,
        embed_images_base64: bool = True,
    ) -> Path:
        """合成單一檔案自包含之 overview.html。

        Args:
            sandbox: 作業沙盒環境實例
            summary: 作業成果摘要模型 (可選，預設自沙盒 artifacts/summary.json 讀取)
            chart_data: 圖表數據字典 (可包含 convergence, drop, psd, energy, mop 等數據)
            embed_images_base64: 是否將 PNG 雲圖轉為 Base64 內嵌以達成 100% 自包含

        Returns:
            Path: 生成之 overview.html 絕對路徑
        """
        if not self.template_path.exists():
            raise FileNotFoundError(f"找不到報告模板: {self.template_path}")

        template_text = self.template_path.read_text(encoding="utf-8")

        # 獲取 summary
        if summary is None:
            summary = sandbox.get_summary()
        if summary is None:
            raise ValueError(f"沙盒 [{sandbox.job_id}] 缺少 summary.json，無法生成報告")

        metrics = summary.metrics
        execution = summary.execution

        # 判定樣式與文字
        verdict_class = "verdict-pass"
        verdict_text = "✅ PASS (合格)"
        if summary.status == JobStatusEnum.ABORTED:
            verdict_class = "verdict-aborted"
            verdict_text = "⚠️ ABORTED (中斷)"
        elif summary.status == JobStatusEnum.FAILED or summary.verdict == VerdictEnum.FAIL:
            verdict_class = "verdict-fail"
            verdict_text = "❌ FAIL (不合格)"
        elif summary.verdict == VerdictEnum.INCONCLUSIVE:
            verdict_class = "verdict-aborted"
            verdict_text = "⏳ INCONCLUSIVE (待定)"

        # 核心數值格式化
        max_stress_str = (
            f"{metrics.max_equivalent_stress_mpa:.2f} MPa"
            if metrics.max_equivalent_stress_mpa is not None
            else "N/A"
        )
        yield_str = (
            f"{metrics.material_yield_strength_mpa:.2f} MPa"
            if metrics.material_yield_strength_mpa is not None
            else "未指定"
        )
        sf_str = f"{metrics.safety_factor:.2f}" if metrics.safety_factor is not None else "N/A"
        sf_status = "結構強度裕度合格" if (metrics.safety_factor or 0) >= 1.2 else "裕度不足或未檢驗"

        # 變形與翹曲
        disp_str = "N/A"
        disp_sub = "位移場指標"
        if metrics.max_total_deformation_mm is not None:
            disp_str = f"{metrics.max_total_deformation_mm:.3f} mm"
            disp_sub = "最大總變形量"
        elif metrics.max_warpage_z_um is not None:
            disp_str = f"{metrics.max_warpage_z_um:.2f} μm"
            disp_sub = "Z 軸最大翹曲位移"

        # 頻率
        freq_str = (
            f"{metrics.first_mode_frequency_hz:.2f} Hz"
            if metrics.first_mode_frequency_hz is not None
            else "N/A"
        )
        mass_parts: List[str] = []
        if metrics.effective_mass_ratio_x is not None:
            mass_parts.append(f"X:{metrics.effective_mass_ratio_x*100:.1f}%")
        if metrics.effective_mass_ratio_y is not None:
            mass_parts.append(f"Y:{metrics.effective_mass_ratio_y*100:.1f}%")
        if metrics.effective_mass_ratio_z is not None:
            mass_parts.append(f"Z:{metrics.effective_mass_ratio_z*100:.1f}%")
        modal_mass_sub = f"模態質量: {', '.join(mass_parts)}" if mass_parts else "未進行模態分析"

        # 顯式動力學
        hg_str = (
            f"{metrics.hourglass_energy_ratio_pct:.2f}%"
            if metrics.hourglass_energy_ratio_pct is not None
            else "N/A"
        )
        ms_str = (
            f"{metrics.mass_scaling_added_pct:.2f}%"
            if metrics.mass_scaling_added_pct is not None
            else "N/A"
        )

        # 代理模型
        cop_str = f"{metrics.cop_score * 100:.1f}%" if metrics.cop_score is not None else "N/A"
        res_str = (
            f"{metrics.final_convergence_residual:.2e}"
            if metrics.final_convergence_residual is not None
            else "N/A"
        )

        # 渲染圖表區塊
        charts_html = self._build_charts_html(chart_data)

        # 渲染雲圖相簿
        gallery_html = self._build_gallery_html(sandbox, embed_images_base64)

        # 渲染診斷日誌
        diagnostics_html = self._build_diagnostics_html(summary)

        # 模板標籤替換
        replacements = {
            "{{JOB_ID}}": summary.job_id,
            "{{TITLE}}": f"{summary.workflow_type.upper()} 模擬分析工程儀表板",
            "{{WORKFLOW_TYPE}}": summary.workflow_type,
            "{{TAG}}": summary.tag,
            "{{DURATION_SECONDS}}": f"{execution.duration_seconds or 0.0:.1f}",
            "{{FINISHED_AT}}": execution.finished_at or execution.created_at,
            "{{VERDICT_CLASS}}": verdict_class,
            "{{VERDICT_TEXT}}": verdict_text,
            "{{MAX_STRESS_MPA}}": max_stress_str,
            "{{YIELD_STRENGTH_MPA}}": yield_str,
            "{{SAFETY_FACTOR}}": sf_str,
            "{{SAFETY_FACTOR_STATUS}}": sf_status,
            "{{MAX_DISPLACEMENT}}": disp_str,
            "{{DISPLACEMENT_SUB}}": disp_sub,
            "{{FIRST_MODE_FREQ}}": freq_str,
            "{{MODAL_MASS_SUB}}": modal_mass_sub,
            "{{HOURGLASS_RATIO}}": hg_str,
            "{{MASS_SCALING}}": ms_str,
            "{{COP_SCORE}}": cop_str,
            "{{CONV_RESIDUAL}}": res_str,
            "{{CHARTS_HTML}}": charts_html,
            "{{GALLERY_HTML}}": gallery_html,
            "{{DIAGNOSTICS_HTML}}": diagnostics_html,
            "{{GENERATED_AT}}": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

        output_html = template_text
        for k, v in replacements.items():
            output_html = output_html.replace(k, str(v))

        # 寫入沙盒 artifacts/overview.html
        target_path = sandbox.artifacts_dir / "overview.html"
        target_path.write_text(output_html, encoding="utf-8")

        # 更新 summary 產生物索引
        summary.artifacts["overview_html"] = str(target_path)
        sandbox.save_summary(summary)

        logger.info(f"作業 [{sandbox.job_id}] 自包含 HTML 報告已生成: {target_path}")
        return target_path

    def generate_dialog_summary(
        self,
        summary: SimulationSummary,
        sandbox: Optional[JobSandbox] = None,
    ) -> str:
        """生成高資訊密度繁體中文 Markdown 摘要，供 AI 助手對話引用。"""
        status_emoji = "✅" if summary.verdict == VerdictEnum.PASS else "❌"
        if summary.status == JobStatusEnum.ABORTED:
            status_emoji = "⚠️"

        metrics = summary.metrics
        execution = summary.execution

        # 格式化數值
        stress_text = (
            f"`{metrics.max_equivalent_stress_mpa:.2f} MPa`"
            if metrics.max_equivalent_stress_mpa is not None
            else "`N/A`"
        )
        sf_text = f"`{metrics.safety_factor:.2f}`" if metrics.safety_factor is not None else "`N/A`"

        disp_text = "`N/A`"
        if metrics.max_total_deformation_mm is not None:
            disp_text = f"`{metrics.max_total_deformation_mm:.3f} mm`"
        elif metrics.max_warpage_z_um is not None:
            disp_text = f"`{metrics.max_warpage_z_um:.2f} μm`"

        freq_text = (
            f"`{metrics.first_mode_frequency_hz:.2f} Hz`"
            if metrics.first_mode_frequency_hz is not None
            else "`N/A`"
        )
        hg_text = (
            f"`{metrics.hourglass_energy_ratio_pct:.2f}%`"
            if metrics.hourglass_energy_ratio_pct is not None
            else "`N/A`"
        )
        ms_text = (
            f"`{metrics.mass_scaling_added_pct:.2f}%`"
            if metrics.mass_scaling_added_pct is not None
            else "`N/A`"
        )

        overview_path = summary.artifacts.get("overview_html", "未生成")
        summary_path = summary.artifacts.get("summary_json", "未生成")
        contour_path = summary.artifacts.get("contour_image", "未生成")

        md_content = f"""### 📊 ANSYS CAE 模擬分析報告：[{summary.job_id}]
- **分析工況**：{summary.workflow_type.upper()}（標籤：`{summary.tag}`）
- **最終判定**：{status_emoji} **{summary.verdict.value}**（狀態：`{summary.status.value}`）
- **計算耗時**：`{execution.duration_seconds or 0.0:.2f} 秒`（求解器：`{execution.solver_name}`）
- **核心工程指標**：
  - 最大等效應力：{stress_text}（安全係數：{sf_text}）
  - 最大翹曲/變形：{disp_text}
  - 一階特徵頻率：{freq_text}
  - 物理健康狀態：沙漏能 {hg_text} | 質量縮放 {ms_text}
- **標準交付物索引**：
  - 互動式儀表板：`{overview_path}`
  - 機器可讀數據：`{summary_path}`
  - 高解析白底雲圖：`{contour_path}`
"""
        # 若有熔斷或失敗原因，追加診斷說明
        if summary.failure_reasons:
            md_content += "\n**⚠️ 異常與熔斷排查記錄**：\n"
            for r in summary.failure_reasons:
                md_content += f"- {r}\n"

        if execution.circuit_breaker_triggered and execution.circuit_breaker_reason:
            md_content += f"\n**🛡️ Sentinel 早期物理熔斷處方箋**：\n- {execution.circuit_breaker_reason}\n"

        # 若提供了 sandbox，將對話摘要寫入 artifacts/report_summary.md
        if sandbox:
            target_md = sandbox.artifacts_dir / "report_summary.md"
            target_md.write_text(md_content, encoding="utf-8")
            summary.artifacts["report_summary_md"] = str(target_md)
            sandbox.save_summary(summary)

        return md_content

    def _build_charts_html(self, chart_data: Optional[Dict[str, Any]]) -> str:
        """建立圖表 HTML。"""
        if not chart_data:
            return '<div class="chart-container"><p style="color:#64748B;">未提供歷史歷程或響應圖表數據</p></div>'

        chart_elements: List[str] = []

        # 1. 力平衡收斂殘差圖
        if "convergence" in chart_data:
            c_data = chart_data["convergence"]
            svg = render_convergence_curve_svg(
                iterations=c_data.get("iterations", []),
                residuals=c_data.get("residuals", []),
                criteria=c_data.get("criteria"),
                title=c_data.get("title", "力平衡收斂殘差歷史曲線"),
            )
            chart_elements.append(f'<div class="chart-container">{svg}</div>')

        # 2. 落摔加速度圖
        if "drop" in chart_data:
            d_data = chart_data["drop"]
            svg = render_drop_acceleration_svg(
                time_ms=d_data.get("time_ms", []),
                acceleration_g=d_data.get("acceleration_g", []),
                title=d_data.get("title", "落摔衝擊加速度時域歷程"),
            )
            chart_elements.append(f'<div class="chart-container">{svg}</div>')

        # 3. 隨機振動 PSD 頻響圖
        if "psd" in chart_data:
            p_data = chart_data["psd"]
            svg = render_psd_response_svg(
                frequencies=p_data.get("frequencies", []),
                response_g2_hz=p_data.get("response_g2_hz", []),
                input_psd=p_data.get("input_psd"),
                title=p_data.get("title", "隨機振動 PSD 加速度頻響曲線"),
            )
            chart_elements.append(f'<div class="chart-container">{svg}</div>')

        # 4. LS-DYNA 能量平衡圖
        if "energy" in chart_data:
            e_data = chart_data["energy"]
            svg = render_energy_balance_svg(
                time_s=e_data.get("time_s", []),
                kinetic_e=e_data.get("kinetic_e", []),
                internal_e=e_data.get("internal_e", []),
                hourglass_e=e_data.get("hourglass_e", []),
                total_e=e_data.get("total_e"),
                title=e_data.get("title", "LS-DYNA 全域能量平衡與沙漏能曲線"),
            )
            chart_elements.append(f'<div class="chart-container">{svg}</div>')

        # 5. optiSLang MOP 響應面
        if "mop" in chart_data:
            m_data = chart_data["mop"]
            svg = render_mop_surface_svg(
                x_grid=m_data.get("x_grid", []),
                y_grid=m_data.get("y_grid", []),
                z_matrix=m_data.get("z_matrix", []),
                x_label=m_data.get("x_label", "參數 1"),
                y_label=m_data.get("y_label", "參數 2"),
                z_label=m_data.get("z_label", "響應"),
                title=m_data.get("title", "optiSLang MOP 最佳預測響應面"),
                cop_score=m_data.get("cop_score"),
            )
            chart_elements.append(f'<div class="chart-container">{svg}</div>')

        if not chart_elements:
            return '<div class="chart-container"><p style="color:#64748B;">無可渲染之圖表數據</p></div>'

        return "\n".join(chart_elements)

    def _build_gallery_html(self, sandbox: JobSandbox, embed_base64: bool) -> str:
        """建立白底雲圖相簿 HTML。"""
        images_dir = sandbox.images_dir
        if not images_dir.exists():
            return '<p style="color:#64748B; padding: 20px;">沙盒 artifacts/images/ 目錄尚未產生雲圖檔案</p>'

        image_files = sorted(
            list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg"))
        )
        if not image_files:
            return '<p style="color:#64748B; padding: 20px;">無可展示之雲圖結果（未生成或運算被中斷）</p>'

        cards: List[str] = []
        for img_p in image_files:
            title = img_p.stem.replace("_", " ").title()
            if embed_base64:
                try:
                    img_data = base64.b64encode(img_p.read_bytes()).decode("ascii")
                    ext = img_p.suffix.lstrip(".").lower()
                    mime = "image/png" if ext == "png" else "image/jpeg"
                    src = f"data:{mime};base64,{img_data}"
                except Exception:
                    src = f"images/{img_p.name}"
            else:
                src = f"images/{img_p.name}"

            card = f"""
        <div class="gallery-card" onclick="openModal('{src}')">
          <div class="gallery-img-wrap">
            <img src="{src}" alt="{title}" loading="lazy">
          </div>
          <div class="gallery-info">
            <div class="img-title">{title}</div>
            <div class="img-desc">白底高解析雲圖 (點擊放大檢視)</div>
          </div>
        </div>"""
            cards.append(card)

        return "\n".join(cards)

    def _build_diagnostics_html(self, summary: SimulationSummary) -> str:
        """建立診斷與處方箋 HTML。"""
        items: List[str] = []

        # 熔斷狀態
        if summary.execution.circuit_breaker_triggered:
            items.append(f"""
          <div class="diag-item">
            <span class="diag-badge diag-fatal">CIRCUIT BREAKER TRIGGERED</span>
            <strong>早期物理發散熔斷攔截</strong>
            <p style="color: #F87171; margin-top: 4px;">{summary.execution.circuit_breaker_reason or '未知熔斷原因'}</p>
          </div>""")
        else:
            items.append("""
          <div class="diag-item">
            <span class="diag-badge diag-pass">PASS</span>
            <strong>Sentinel 物理健康守護正常</strong>
            <p style="color: #94A3B8; margin-top: 4px;">未偵測到沙漏能超標 (>5%)、質量縮放暴增、數值 NaN/Inf 或嚴重負滑移能。</p>
          </div>""")

        # 失敗或異常清單
        if summary.failure_reasons:
            for r in summary.failure_reasons:
                items.append(f"""
          <div class="diag-item">
            <span class="diag-badge diag-warn">ISSUE</span>
            <span>{r}</span>
          </div>""")

        # 若無異常
        if not summary.failure_reasons and not summary.execution.circuit_breaker_triggered:
            items.append("""
          <div class="diag-item">
            <span class="diag-badge diag-pass">READY</span>
            <span>前置安全閘門核驗通過，無阻斷性物理衝突。</span>
          </div>""")

        return "\n".join(items)
