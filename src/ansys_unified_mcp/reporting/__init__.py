"""ANSYS Unified MCP 2.0 - 自包含互動式 HTML 報告合成套件 (Reporting Package).

提供純原生免外網向量圖表 (SVG) 繪製、單一自包含 HTML 儀表板合成與對話引用 Markdown 摘要生成。
"""

from __future__ import annotations

from ansys_unified_mcp.reporting.charts import (
    render_convergence_curve_svg,
    render_drop_acceleration_svg,
    render_energy_balance_svg,
    render_mop_surface_svg,
    render_psd_response_svg,
)
from ansys_unified_mcp.reporting.generator import ReportGenerator

__all__ = [
    "ReportGenerator",
    "render_convergence_curve_svg",
    "render_psd_response_svg",
    "render_drop_acceleration_svg",
    "render_energy_balance_svg",
    "render_mop_surface_svg",
]
