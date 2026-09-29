"""Backward-compatibility shim for ansys_unified_mcp.reporting -> ansys_unified_mcp.analytics.reporting."""
from ansys_unified_mcp.analytics.reporting import *
from ansys_unified_mcp.analytics.reporting.charts import (
    render_convergence_curve_svg,
    render_drop_acceleration_svg,
    render_energy_balance_svg,
    render_mop_surface_svg,
    render_psd_response_svg,
)
from ansys_unified_mcp.analytics.reporting.generator import ReportGenerator
