"""ANSYS Unified MCP 2.0 - 純原生免外網 SVG 圖表渲染器 (Native SVG Charts).

純原生 Python 生成向量 SVG 圖表，零外部 CDN 或 JavaScript 庫依賴：
- render_convergence_curve_svg: 力平衡收斂殘差歷程 (半對數坐標系)
- render_psd_response_svg: 隨機振動 PSD 頻響曲線 (雙對數坐標系)
- render_drop_acceleration_svg: 落摔衝擊加速度時域響應曲線
- render_energy_balance_svg: LS-DYNA 動能/內能/沙漏能/總能量平衡曲線
- render_mop_surface_svg: optiSLang MOP 響應面 2.5D 等高色彩網格
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


def _escape_xml(text: str) -> str:
    """跳脫 XML 特殊字元。"""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _format_sci(val: float) -> str:
    """格式化科學記號或浮點數。"""
    if val == 0:
        return "0"
    if abs(val) >= 1000 or abs(val) < 0.01:
        return f"{val:.2e}"
    return f"{val:.2f}"


def render_convergence_curve_svg(
    iterations: List[int],
    residuals: List[float],
    criteria: Optional[List[float]] = None,
    title: str = "力平衡收斂殘差歷史曲線 (Force Convergence)",
    width: int = 750,
    height: int = 400,
) -> str:
    """生成半對數力平衡殘差歷史曲線 SVG。"""
    if not iterations or not residuals:
        return _render_empty_svg("暫無收斂數據", width, height)

    pad_left = 80
    pad_right = 40
    pad_top = 50
    pad_bottom = 60
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    # 計算 X 軸範圍
    min_x = min(iterations)
    max_x = max(iterations)
    if min_x == max_x:
        max_x = min_x + 1

    # 計算 Y 軸對數範圍 (避免 <= 0)
    valid_residuals = [r for r in residuals if r is not None and r > 0]
    if not valid_residuals:
        return _render_empty_svg("殘差數據無效", width, height)

    min_val = min(valid_residuals)
    max_val = max(valid_residuals)
    if criteria:
        if isinstance(criteria, (int, float)):
            criteria = [float(criteria)]
        valid_crit = [c for c in criteria if c is not None and c > 0]
        if valid_crit:
            min_val = min(min_val, min(valid_crit))
            max_val = max(max_val, max(valid_crit))

    log_min = math.floor(math.log10(max(min_val, 1e-15)))
    log_max = math.ceil(math.log10(max(max_val, 1e-14)))
    if log_min == log_max:
        log_max += 1

    def to_x(it: float) -> float:
        return pad_left + (it - min_x) / (max_x - min_x) * plot_w

    def to_y(val: float) -> float:
        if val <= 0:
            val = 10**log_min
        log_v = math.log10(max(val, 1e-15))
        ratio = (log_v - log_min) / (log_max - log_min)
        return pad_top + (1.0 - ratio) * plot_h

    # 繪製網格線與 Y 刻度
    grid_lines: List[str] = []
    y_labels: List[str] = []
    for exp in range(int(log_min), int(log_max) + 1):
        y = pad_top + (1.0 - (exp - log_min) / (log_max - log_min)) * plot_h
        grid_lines.append(
            f'<line x1="{pad_left}" y1="{y}" x2="{width - pad_right}" y2="{y}" stroke="#334155" stroke-dasharray="3,3" stroke-width="1"/>'
        )
        y_labels.append(
            f'<text x="{pad_left - 10}" y="{y + 4}" fill="#94A3B8" font-size="11" text-anchor="end" font-family="monospace">10^{exp}</text>'
        )

    # 繪製 X 刻度
    x_labels: List[str] = []
    x_steps = 5
    for i in range(x_steps + 1):
        it_val = min_x + (max_x - min_x) * (i / x_steps)
        x = pad_left + (i / x_steps) * plot_w
        grid_lines.append(
            f'<line x1="{x}" y1="{pad_top}" x2="{x}" y2="{height - pad_bottom}" stroke="#334155" stroke-dasharray="3,3" stroke-width="1"/>'
        )
        x_labels.append(
            f'<text x="{x}" y="{height - pad_bottom + 20}" fill="#94A3B8" font-size="11" text-anchor="middle" font-family="monospace">{int(it_val)}</text>'
        )

    # 繪製殘差線
    pts_res: List[str] = []
    for it, r in zip(iterations, residuals):
        if r is not None and r > 0:
            pts_res.append(f"{to_x(it):.1f},{to_y(r):.1f}")
    polyline_res = " ".join(pts_res)

    # 繪製收斂準則線 (若提供)
    polyline_crit = ""
    if criteria and len(criteria) == len(iterations):
        pts_crit = [
            f"{to_x(it):.1f},{to_y(c):.1f}"
            for it, c in zip(iterations, criteria)
            if c is not None and c > 0
        ]
        if pts_crit:
            polyline_crit = f'<polyline points="{" ".join(pts_crit)}" fill="none" stroke="#10B981" stroke-width="2" stroke-dasharray="4,2"/>'

    svg = f"""<svg viewBox="0 0 {width} {height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="background: #0F172A; border-radius: 8px;">
  <text x="{width // 2}" y="28" fill="#F8FAFC" font-size="14" font-weight="bold" text-anchor="middle" font-family="sans-serif">{_escape_xml(title)}</text>
  {''.join(grid_lines)}
  {''.join(y_labels)}
  {''.join(x_labels)}
  <text x="{width // 2}" y="{height - 15}" fill="#64748B" font-size="12" text-anchor="middle">累積平衡迭代 (Cumulative Iteration)</text>
  <text transform="rotate(-90)" x="{-height // 2}" y="24" fill="#64748B" font-size="12" text-anchor="middle">力殘差 / 準則 (L2 Norm)</text>
  {polyline_crit}
  <polyline points="{polyline_res}" fill="none" stroke="#38BDF8" stroke-width="2.5"/>
  <!-- 圖例 -->
  <g transform="translate({width - 240}, 15)">
    <line x1="0" y1="10" x2="25" y2="10" stroke="#38BDF8" stroke-width="2.5"/>
    <text x="32" y="14" fill="#E2E8F0" font-size="11">殘差 (Residual)</text>
    <line x1="120" y1="10" x2="145" y2="10" stroke="#10B981" stroke-width="2" stroke-dasharray="4,2"/>
    <text x="152" y="14" fill="#E2E8F0" font-size="11">準則 (Criterion)</text>
  </g>
</svg>"""
    return svg


def render_psd_response_svg(
    frequencies: List[float],
    response_g2_hz: List[float],
    input_psd: Optional[List[float]] = None,
    title: str = "隨機振動 PSD 加速度頻響曲線",
    width: int = 750,
    height: int = 400,
) -> str:
    """生成隨機振動雙對數 PSD 頻響曲線 SVG。"""
    if not frequencies or not response_g2_hz:
        return _render_empty_svg("暫無 PSD 數據", width, height)

    pad_left = 80
    pad_right = 40
    pad_top = 50
    pad_bottom = 60
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    valid_f = [f for f in frequencies if f > 0]
    valid_resp = [r for r in response_g2_hz if r > 0]
    if not valid_f or not valid_resp:
        return _render_empty_svg("頻率或響應數值必須為正", width, height)

    log_fx_min = math.floor(math.log10(min(valid_f)))
    log_fx_max = math.ceil(math.log10(max(valid_f)))
    if log_fx_min == log_fx_max:
        log_fx_max += 1

    all_y = list(valid_resp)
    if input_psd:
        all_y.extend([p for p in input_psd if p > 0])
    log_y_min = math.floor(math.log10(min(all_y)))
    log_y_max = math.ceil(math.log10(max(all_y)))
    if log_y_min == log_y_max:
        log_y_max += 1

    def to_x(f: float) -> float:
        log_f = math.log10(max(f, 1e-6))
        return pad_left + (log_f - log_fx_min) / (log_fx_max - log_fx_min) * plot_w

    def to_y(v: float) -> float:
        log_v = math.log10(max(v, 1e-15))
        ratio = (log_v - log_y_min) / (log_y_max - log_y_min)
        return pad_top + (1.0 - ratio) * plot_h

    grid_lines: List[str] = []
    y_labels: List[str] = []
    for exp in range(int(log_y_min), int(log_y_max) + 1):
        y = pad_top + (1.0 - (exp - log_y_min) / (log_y_max - log_y_min)) * plot_h
        grid_lines.append(
            f'<line x1="{pad_left}" y1="{y}" x2="{width - pad_right}" y2="{y}" stroke="#334155" stroke-dasharray="3,3" stroke-width="1"/>'
        )
        y_labels.append(
            f'<text x="{pad_left - 10}" y="{y + 4}" fill="#94A3B8" font-size="11" text-anchor="end" font-family="monospace">10^{exp}</text>'
        )

    x_labels: List[str] = []
    for exp in range(int(log_fx_min), int(log_fx_max) + 1):
        x = pad_left + (exp - log_fx_min) / (log_fx_max - log_fx_min) * plot_w
        grid_lines.append(
            f'<line x1="{x}" y1="{pad_top}" x2="{x}" y2="{height - pad_bottom}" stroke="#334155" stroke-dasharray="3,3" stroke-width="1"/>'
        )
        x_labels.append(
            f'<text x="{x}" y="{height - pad_bottom + 20}" fill="#94A3B8" font-size="11" text-anchor="middle" font-family="monospace">{10**exp} Hz</text>'
        )

    pts_resp = [f"{to_x(f):.1f},{to_y(r):.1f}" for f, r in zip(frequencies, response_g2_hz) if f > 0 and r > 0]
    polyline_resp = " ".join(pts_resp)

    polyline_in = ""
    if input_psd and len(input_psd) == len(frequencies):
        pts_in = [f"{to_x(f):.1f},{to_y(p):.1f}" for f, p in zip(frequencies, input_psd) if f > 0 and p > 0]
        if pts_in:
            polyline_in = f'<polyline points="{" ".join(pts_in)}" fill="none" stroke="#F59E0B" stroke-width="2" stroke-dasharray="3,3"/>'

    svg = f"""<svg viewBox="0 0 {width} {height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="background: #0F172A; border-radius: 8px;">
  <text x="{width // 2}" y="28" fill="#F8FAFC" font-size="14" font-weight="bold" text-anchor="middle" font-family="sans-serif">{_escape_xml(title)}</text>
  {''.join(grid_lines)}
  {''.join(y_labels)}
  {''.join(x_labels)}
  <text x="{width // 2}" y="{height - 15}" fill="#64748B" font-size="12" text-anchor="middle">頻率 Frequency (Hz)</text>
  <text transform="rotate(-90)" x="{-height // 2}" y="24" fill="#64748B" font-size="12" text-anchor="middle">加速度 PSD (G²/Hz)</text>
  {polyline_in}
  <polyline points="{polyline_resp}" fill="none" stroke="#EC4899" stroke-width="2.5"/>
  <g transform="translate({width - 240}, 15)">
    <line x1="0" y1="10" x2="25" y2="10" stroke="#EC4899" stroke-width="2.5"/>
    <text x="32" y="14" fill="#E2E8F0" font-size="11">結構響應 (Response)</text>
    <line x1="130" y1="10" x2="155" y2="10" stroke="#F59E0B" stroke-width="2" stroke-dasharray="3,3"/>
    <text x="162" y="14" fill="#E2E8F0" font-size="11">輸入譜 (Input)</text>
  </g>
</svg>"""
    return svg


def render_drop_acceleration_svg(
    time_ms: List[float],
    acceleration_g: List[float],
    title: str = "落摔衝擊加速度時域歷程 (Drop Acceleration Pulse)",
    width: int = 750,
    height: int = 400,
) -> str:
    """生成落摔衝擊減速度歷程曲線 SVG。"""
    if not time_ms or not acceleration_g:
        return _render_empty_svg("暫無落摔加速度數據", width, height)

    pad_left = 70
    pad_right = 40
    pad_top = 50
    pad_bottom = 60
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    min_t = min(time_ms)
    max_t = max(time_ms)
    if min_t == max_t:
        max_t = min_t + 1.0

    min_a = min(acceleration_g)
    max_a = max(acceleration_g)
    if min_a == max_a:
        max_a = min_a + 10.0
    # 留 10% 緩衝空間
    span_a = max_a - min_a
    y_min = min(0.0, min_a - 0.05 * span_a)
    y_max = max_a + 0.1 * span_a

    def to_x(t: float) -> float:
        return pad_left + (t - min_t) / (max_t - min_t) * plot_w

    def to_y(a: float) -> float:
        return pad_top + (1.0 - (a - y_min) / (y_max - y_min)) * plot_h

    # 峰值標籤
    peak_idx = acceleration_g.index(max(acceleration_g))
    peak_t = time_ms[peak_idx]
    peak_g = acceleration_g[peak_idx]
    peak_x = to_x(peak_t)
    peak_y = to_y(peak_g)

    grid_lines: List[str] = []
    y_labels: List[str] = []
    y_steps = 5
    for i in range(y_steps + 1):
        val = y_min + (y_max - y_min) * (i / y_steps)
        y = pad_top + (1.0 - i / y_steps) * plot_h
        grid_lines.append(
            f'<line x1="{pad_left}" y1="{y}" x2="{width - pad_right}" y2="{y}" stroke="#334155" stroke-dasharray="3,3" stroke-width="1"/>'
        )
        y_labels.append(
            f'<text x="{pad_left - 10}" y="{y + 4}" fill="#94A3B8" font-size="11" text-anchor="end">{val:.1f}G</text>'
        )

    x_labels: List[str] = []
    x_steps = 5
    for i in range(x_steps + 1):
        t_val = min_t + (max_t - min_t) * (i / x_steps)
        x = pad_left + (i / x_steps) * plot_w
        grid_lines.append(
            f'<line x1="{x}" y1="{pad_top}" x2="{x}" y2="{height - pad_bottom}" stroke="#334155" stroke-dasharray="3,3" stroke-width="1"/>'
        )
        x_labels.append(
            f'<text x="{x}" y="{height - pad_bottom + 20}" fill="#94A3B8" font-size="11" text-anchor="middle">{t_val:.2f} ms</text>'
        )

    pts = [f"{to_x(t):.1f},{to_y(a):.1f}" for t, a in zip(time_ms, acceleration_g)]
    polyline_str = " ".join(pts)

    # 漸變填色區塊
    first_pt = f"{to_x(time_ms[0]):.1f},{to_y(0.0):.1f}"
    last_pt = f"{to_x(time_ms[-1]):.1f},{to_y(0.0):.1f}"
    area_pts = f"{first_pt} {polyline_str} {last_pt}"

    svg = f"""<svg viewBox="0 0 {width} {height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="background: #0F172A; border-radius: 8px;">
  <defs>
    <linearGradient id="dropGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#38BDF8" stop-opacity="0.0"/>
    </linearGradient>
  </defs>
  <text x="{width // 2}" y="28" fill="#F8FAFC" font-size="14" font-weight="bold" text-anchor="middle" font-family="sans-serif">{_escape_xml(title)}</text>
  {''.join(grid_lines)}
  {''.join(y_labels)}
  {''.join(x_labels)}
  <text x="{width // 2}" y="{height - 15}" fill="#64748B" font-size="12" text-anchor="middle">時間 Time (ms)</text>
  <text transform="rotate(-90)" x="{-height // 2}" y="22" fill="#64748B" font-size="12" text-anchor="middle">加速度 Acceleration (G)</text>
  <polygon points="{area_pts}" fill="url(#dropGrad)"/>
  <polyline points="{polyline_str}" fill="none" stroke="#38BDF8" stroke-width="2.5"/>
  <!-- 峰值加速度標籤 -->
  <circle cx="{peak_x:.1f}" cy="{peak_y:.1f}" r="5" fill="#EF4444" stroke="#FFFFFF" stroke-width="2"/>
  <rect x="{peak_x + 8}" y="{peak_y - 20}" width="100" height="24" rx="4" fill="#1E293B" stroke="#EF4444" stroke-width="1"/>
  <text x="{peak_x + 14}" y="{peak_y - 4}" fill="#F8FAFC" font-size="11" font-weight="bold">峰值: {peak_g:.1f}G</text>
</svg>"""
    return svg


def render_energy_balance_svg(
    time_s: List[float],
    kinetic_e: List[float],
    internal_e: List[float],
    hourglass_e: List[float],
    total_e: Optional[List[float]] = None,
    title: str = "LS-DYNA 全域能量平衡與沙漏能曲線",
    width: int = 750,
    height: int = 400,
) -> str:
    """生成 LS-DYNA 動能/內能/沙漏能/總能量平衡曲線 SVG。"""
    if not time_s or not internal_e:
        return _render_empty_svg("暫無能量平衡數據", width, height)

    pad_left = 80
    pad_right = 40
    pad_top = 50
    pad_bottom = 60
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    min_t = min(time_s)
    max_t = max(time_s)
    if min_t == max_t:
        max_t = min_t + 1e-4

    all_vals = list(kinetic_e) + list(internal_e) + list(hourglass_e)
    if total_e:
        all_vals.extend(total_e)

    max_energy = max(all_vals) if all_vals else 1.0
    if max_energy <= 0:
        max_energy = 1.0
    y_max = max_energy * 1.15

    def to_x(t: float) -> float:
        return pad_left + (t - min_t) / (max_t - min_t) * plot_w

    def to_y(e: float) -> float:
        return pad_top + (1.0 - max(0.0, e) / y_max) * plot_h

    grid_lines: List[str] = []
    y_labels: List[str] = []
    y_steps = 5
    for i in range(y_steps + 1):
        val = y_max * (i / y_steps)
        y = pad_top + (1.0 - i / y_steps) * plot_h
        grid_lines.append(
            f'<line x1="{pad_left}" y1="{y}" x2="{width - pad_right}" y2="{y}" stroke="#334155" stroke-dasharray="3,3" stroke-width="1"/>'
        )
        y_labels.append(
            f'<text x="{pad_left - 10}" y="{y + 4}" fill="#94A3B8" font-size="11" text-anchor="end">{_format_sci(val)}J</text>'
        )

    x_labels: List[str] = []
    x_steps = 5
    for i in range(x_steps + 1):
        t_val = min_t + (max_t - min_t) * (i / x_steps)
        x = pad_left + (i / x_steps) * plot_w
        grid_lines.append(
            f'<line x1="{x}" y1="{pad_top}" x2="{x}" y2="{height - pad_bottom}" stroke="#334155" stroke-dasharray="3,3" stroke-width="1"/>'
        )
        x_labels.append(
            f'<text x="{x}" y="{height - pad_bottom + 20}" fill="#94A3B8" font-size="11" text-anchor="middle">{t_val*1000:.2f} ms</text>'
        )

    poly_ke = " ".join([f"{to_x(t):.1f},{to_y(v):.1f}" for t, v in zip(time_s, kinetic_e)])
    poly_ie = " ".join([f"{to_x(t):.1f},{to_y(v):.1f}" for t, v in zip(time_s, internal_e)])
    poly_hg = " ".join([f"{to_x(t):.1f},{to_y(v):.1f}" for t, v in zip(time_s, hourglass_e)])
    poly_tot = ""
    if total_e and len(total_e) == len(time_s):
        poly_tot = f'<polyline points="{" ".join([f"{to_x(t):.1f},{to_y(v):.1f}" for t, v in zip(time_s, total_e)])}" fill="none" stroke="#FFFFFF" stroke-width="2"/>'

    svg = f"""<svg viewBox="0 0 {width} {height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="background: #0F172A; border-radius: 8px;">
  <text x="{width // 2}" y="28" fill="#F8FAFC" font-size="14" font-weight="bold" text-anchor="middle" font-family="sans-serif">{_escape_xml(title)}</text>
  {''.join(grid_lines)}
  {''.join(y_labels)}
  {''.join(x_labels)}
  <text x="{width // 2}" y="{height - 15}" fill="#64748B" font-size="12" text-anchor="middle">模擬時間 (ms)</text>
  <text transform="rotate(-90)" x="{-height // 2}" y="22" fill="#64748B" font-size="12" text-anchor="middle">能量 (Joules)</text>
  {poly_tot}
  <polyline points="{poly_ke}" fill="none" stroke="#38BDF8" stroke-width="2.5"/>
  <polyline points="{poly_ie}" fill="none" stroke="#10B981" stroke-width="2.5"/>
  <polyline points="{poly_hg}" fill="none" stroke="#EF4444" stroke-width="2" stroke-dasharray="4,2"/>
  <!-- 圖例 -->
  <g transform="translate({width - 340}, 15)">
    <line x1="0" y1="10" x2="20" y2="10" stroke="#38BDF8" stroke-width="2.5"/>
    <text x="25" y="14" fill="#E2E8F0" font-size="11">動能 (KE)</text>
    <line x1="85" y1="10" x2="105" y2="10" stroke="#10B981" stroke-width="2.5"/>
    <text x="110" y="14" fill="#E2E8F0" font-size="11">內能 (IE)</text>
    <line x1="170" y1="10" x2="190" y2="10" stroke="#EF4444" stroke-width="2" stroke-dasharray="4,2"/>
    <text x="195" y="14" fill="#E2E8F0" font-size="11">沙漏能 (HG)</text>
    <line x1="260" y1="10" x2="280" y2="10" stroke="#FFFFFF" stroke-width="2"/>
    <text x="285" y="14" fill="#E2E8F0" font-size="11">總能 (Total)</text>
  </g>
</svg>"""
    return svg


def render_mop_surface_svg(
    x_grid: List[float],
    y_grid: List[float],
    z_matrix: List[List[float]],
    x_label: str = "設計變數 1 (t_mm)",
    y_label: str = "設計變數 2 (w_mm)",
    z_label: str = "目標響應 (Stress MPa)",
    title: str = "optiSLang MOP 最佳預測代理模型響應面",
    cop_score: Optional[float] = None,
    width: int = 750,
    height: int = 420,
) -> str:
    """生成 optiSLang MOP 響應面 2.5D 色彩熱力網格 SVG。"""
    if not x_grid or not y_grid or not z_matrix:
        return _render_empty_svg("暫無 MOP 響應面數據", width, height)

    pad_left = 80
    pad_right = 100
    pad_top = 60
    pad_bottom = 60
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    nx = len(x_grid)
    ny = len(y_grid)
    if nx < 2 or ny < 2:
        return _render_empty_svg("網格尺寸不足以繪製響應面", width, height)

    # 展開所有 z 值計算上下界
    flat_z = [val for row in z_matrix for val in row if val is not None]
    if not flat_z:
        return _render_empty_svg("響應面無數值", width, height)
    min_z = min(flat_z)
    max_z = max(flat_z)
    if min_z == max_z:
        max_z = min_z + 1.0

    def get_color(val: float) -> str:
        ratio = (val - min_z) / (max_z - min_z)
        ratio = max(0.0, min(1.0, ratio))
        # 彩虹色階：藍(0.0) -> 青(0.25) -> 綠(0.5) -> 黃(0.75) -> 紅(1.0)
        if ratio < 0.25:
            r = 0
            g = int(255 * (ratio / 0.25))
            b = 255
        elif ratio < 0.5:
            r = 0
            g = 255
            b = int(255 * (1.0 - (ratio - 0.25) / 0.25))
        elif ratio < 0.75:
            r = int(255 * ((ratio - 0.5) / 0.25))
            g = 255
            b = 0
        else:
            r = 255
            g = int(255 * (1.0 - (ratio - 0.75) / 0.25))
            b = 0
        return f"rgb({r},{g},{b})"

    cell_w = plot_w / (nx - 1)
    cell_h = plot_h / (ny - 1)

    cells: List[str] = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            z_val = (
                z_matrix[j][i]
                + z_matrix[j][i + 1]
                + z_matrix[j + 1][i]
                + z_matrix[j + 1][i + 1]
            ) / 4.0
            color = get_color(z_val)
            x = pad_left + i * cell_w
            y = pad_top + (ny - 2 - j) * cell_h
            cells.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_w + 0.5:.1f}" height="{cell_h + 0.5:.1f}" fill="{color}" stroke="none"/>'
            )

    # 軸標籤與刻度
    x_ticks: List[str] = []
    for i in range(0, nx, max(1, nx // 5)):
        x = pad_left + i * cell_w
        x_ticks.append(
            f'<text x="{x:.1f}" y="{height - pad_bottom + 18}" fill="#94A3B8" font-size="11" text-anchor="middle">{x_grid[i]:.2f}</text>'
        )

    y_ticks: List[str] = []
    for j in range(0, ny, max(1, ny // 5)):
        y = pad_top + (ny - 1 - j) * cell_h
        y_ticks.append(
            f'<text x="{pad_left - 8}" y="{y + 4:.1f}" fill="#94A3B8" font-size="11" text-anchor="end">{y_grid[j]:.2f}</text>'
        )

    # 右側色階長條 ColorBar
    cb_x = width - pad_right + 30
    cb_w = 18
    cb_h = plot_h
    cb_steps = 20
    cb_rects: List[str] = []
    for k in range(cb_steps):
        r_ratio = k / cb_steps
        v = min_z + r_ratio * (max_z - min_z)
        c = get_color(v)
        step_h = cb_h / cb_steps
        y = pad_top + (cb_steps - 1 - k) * step_h
        cb_rects.append(
            f'<rect x="{cb_x}" y="{y:.1f}" width="{cb_w}" height="{step_h + 0.5:.1f}" fill="{c}"/>'
        )

    cop_badge = ""
    if cop_score is not None:
        color_b = "#10B981" if cop_score >= 0.80 else "#EF4444"
        cop_badge = f'<text x="{width - pad_right}" y="35" fill="{color_b}" font-size="13" font-weight="bold" text-anchor="end">CoP = {cop_score * 100:.1f}%</text>'

    svg = f"""<svg viewBox="0 0 {width} {height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="background: #0F172A; border-radius: 8px;">
  <text x="{width // 2}" y="28" fill="#F8FAFC" font-size="14" font-weight="bold" text-anchor="middle" font-family="sans-serif">{_escape_xml(title)}</text>
  {cop_badge}
  <!-- 熱力單元格 -->
  <g>{''.join(cells)}</g>
  <!-- 座標軸外框 -->
  <rect x="{pad_left}" y="{pad_top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#475569" stroke-width="1.5"/>
  {''.join(x_ticks)}
  {''.join(y_ticks)}
  <text x="{pad_left + plot_w // 2}" y="{height - 15}" fill="#64748B" font-size="12" text-anchor="middle">{_escape_xml(x_label)}</text>
  <text transform="rotate(-90)" x="{-pad_top - plot_h // 2}" y="22" fill="#64748B" font-size="12" text-anchor="middle">{_escape_xml(y_label)}</text>
  <!-- 色階條 -->
  <g>{''.join(cb_rects)}</g>
  <rect x="{cb_x}" y="{pad_top}" width="{cb_w}" height="{cb_h}" fill="none" stroke="#475569" stroke-width="1"/>
  <text x="{cb_x + cb_w + 5}" y="{pad_top + 10}" fill="#94A3B8" font-size="10">{_format_sci(max_z)}</text>
  <text x="{cb_x + cb_w + 5}" y="{pad_top + cb_h}" fill="#94A3B8" font-size="10">{_format_sci(min_z)}</text>
  <text transform="rotate(90)" x="{pad_top + cb_h // 2}" y="{-cb_x - cb_w - 28}" fill="#94A3B8" font-size="11" text-anchor="middle">{_escape_xml(z_label)}</text>
</svg>"""
    return svg


def _render_empty_svg(msg: str, width: int, height: int) -> str:
    """數據為空時之佔位 SVG。"""
    return f"""<svg viewBox="0 0 {width} {height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="background: #0F172A; border-radius: 8px;">
  <text x="{width // 2}" y="{height // 2}" fill="#64748B" font-size="14" text-anchor="middle" font-family="sans-serif">{_escape_xml(msg)}</text>
</svg>"""
