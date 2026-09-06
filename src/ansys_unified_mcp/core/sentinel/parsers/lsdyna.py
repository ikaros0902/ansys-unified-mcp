"""ANSYS Unified MCP 2.0 - LS-DYNA 顯式動力學日誌解析器 (LSDynaGlstatParser).

負責串流監控與解析 LS-DYNA 能量平衡與質量縮放日誌 (glstat, matter.out, d3hsp, stdout)：
- 提取當前模擬時間與時間步長 dt
- 解析動能、內能、沙漏能、總能量與滑移接觸能
- 提取質量縮放增加百分比 (added mass ratio)
- 計算沙漏能佔比與接觸滑移能異常
- 偵測數值異常 (NaN / Inf) 與發散徵兆
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LSDynaParseResult:
    """LS-DYNA 顯式動力學日誌解析快照。"""

    current_time: float = 0.0
    current_dt: float = 0.0
    kinetic_energy: float = 0.0
    internal_energy: float = 0.0
    hourglass_energy: float = 0.0
    total_energy: float = 0.0
    sliding_energy: float = 0.0
    hourglass_ratio_pct: float = 0.0  # (hourglass / internal) * 100
    hourglass_total_ratio_pct: float = 0.0  # (hourglass / total) * 100
    added_mass_pct: float = 0.0  # 質量縮放百分比
    has_nan_inf: bool = False
    is_completed: bool = False
    progress_pct: float = 0.0
    error_messages: List[str] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)


class LSDynaGlstatParser:
    """LS-DYNA glstat / matter.out 日誌解析器。"""

    RE_TIME_DT = re.compile(
        r"time\s*=\s*([\d\.E\+\-]+)\s+dt\s*=\s*([\d\.E\+\-]+)", re.IGNORECASE
    )
    RE_KINETIC = re.compile(r"kinetic\s+energy\s*=\s*([\d\.E\+\-]+)", re.IGNORECASE)
    RE_INTERNAL = re.compile(r"internal\s+energy\s*=\s*([\d\.E\+\-]+)", re.IGNORECASE)
    RE_HOURGLASS = re.compile(r"hourglass\s+energy\s*=\s*([\d\.E\+\-]+)", re.IGNORECASE)
    RE_TOTAL_ENERGY = re.compile(r"total\s+energy\s*=\s*([\d\.E\+\-]+)", re.IGNORECASE)
    RE_SLIDING = re.compile(
        r"(sliding\s+interface\s+energy|sliding\s+energy)\s*=\s*([\d\.E\+\-]+)",
        re.IGNORECASE,
    )
    RE_MASS_SCALING = re.compile(
        r"added\s+mass\s*=\s*[\d\.E\+\-]+\s*\(ratio\s*=\s*([\d\.E\+\-]+)\s*%\)",
        re.IGNORECASE,
    )
    RE_MASS_SCALING_D3HSP = re.compile(
        r"added\s+mass\s+percentage\s*=\s*([\d\.E\+\-]+)", re.IGNORECASE
    )
    RE_TERMINATION = re.compile(
        r"(N\s*o\s*r\s*m\s*a\s*l\s+t\s*e\s*r\s*m\s*i\s*n\s*a\s*t\s*i\s*o\s*n|Normal termination)",
        re.IGNORECASE,
    )
    RE_NAN_INF = re.compile(r"\b(nan|inf|#ind|#qnan)\b", re.IGNORECASE)

    def __init__(self, target_duration_s: float = 0.005) -> None:
        """初始化解析器。"""
        self.target_duration_s = max(target_duration_s, 1e-9)
        self.result = LSDynaParseResult()

    def parse_chunk(self, content: str) -> LSDynaParseResult:
        """解析 LS-DYNA 日誌字串區塊。"""
        if not content:
            return self.result

        # 檢測 NaN / Inf
        if self.RE_NAN_INF.search(content):
            self.result.has_nan_inf = True
            self.result.error_messages.append("LS-DYNA 能量或時間步出現 NaN/Inf 發散")

        # 檢測正常終止
        if self.RE_TERMINATION.search(content):
            self.result.is_completed = True
            self.result.progress_pct = 100.0

        for line in content.splitlines():
            line_str = line.strip()
            if not line_str:
                continue

            # 時間與時間步長
            time_match = self.RE_TIME_DT.search(line_str)
            if time_match:
                try:
                    t = float(time_match.group(1))
                    dt = float(time_match.group(2))
                    self.result.current_time = t
                    self.result.current_dt = dt
                    if not self.result.is_completed:
                        pct = min(100.0, max(0.0, (t / self.target_duration_s) * 100.0))
                        self.result.progress_pct = round(pct, 2)
                except ValueError:
                    pass

            # 動能
            ke_match = self.RE_KINETIC.search(line_str)
            if ke_match:
                try:
                    self.result.kinetic_energy = float(ke_match.group(1))
                except ValueError:
                    pass

            # 內能
            ie_match = self.RE_INTERNAL.search(line_str)
            if ie_match:
                try:
                    self.result.internal_energy = float(ie_match.group(1))
                except ValueError:
                    pass

            # 沙漏能
            hg_match = self.RE_HOURGLASS.search(line_str)
            if hg_match:
                try:
                    self.result.hourglass_energy = float(hg_match.group(1))
                except ValueError:
                    pass

            # 總能量
            te_match = self.RE_TOTAL_ENERGY.search(line_str)
            if te_match:
                try:
                    self.result.total_energy = float(te_match.group(1))
                except ValueError:
                    pass

            # 接觸滑移能
            sl_match = self.RE_SLIDING.search(line_str)
            if sl_match:
                try:
                    self.result.sliding_energy = float(sl_match.group(2))
                except ValueError:
                    pass

            # 質量縮放比例（代表一個步長的數據已完整）
            ms_match = self.RE_MASS_SCALING.search(line_str)
            ms_d3_match = self.RE_MASS_SCALING_D3HSP.search(line_str) if not ms_match else None

            if ms_match or ms_d3_match:
                try:
                    val = float(ms_match.group(1)) if ms_match else float(ms_d3_match.group(1))
                    self.result.added_mass_pct = val
                except ValueError:
                    pass

                # 計算能量健康指標
                if self.result.internal_energy > 1e-12:
                    self.result.hourglass_ratio_pct = (
                        self.result.hourglass_energy / self.result.internal_energy
                    ) * 100.0
                else:
                    self.result.hourglass_ratio_pct = 0.0

                if self.result.total_energy > 1e-12:
                    self.result.hourglass_total_ratio_pct = (
                        self.result.hourglass_energy / self.result.total_energy
                    ) * 100.0
                else:
                    self.result.hourglass_total_ratio_pct = 0.0

                # 記錄單步快照至 history
                self.result.history.append({
                    "time": self.result.current_time,
                    "dt": self.result.current_dt,
                    "kinetic_e": self.result.kinetic_energy,
                    "internal_e": self.result.internal_energy,
                    "hourglass_e": self.result.hourglass_energy,
                    "total_e": self.result.total_energy,
                    "sliding_e": self.result.sliding_energy,
                    "hg_ratio_pct": round(self.result.hourglass_ratio_pct, 3),
                    "mass_scaling_pct": self.result.added_mass_pct,
                })

        # 最終再次更新指標
        if self.result.internal_energy > 1e-12:
            self.result.hourglass_ratio_pct = (
                self.result.hourglass_energy / self.result.internal_energy
            ) * 100.0

        if self.result.total_energy > 1e-12:
            self.result.hourglass_total_ratio_pct = (
                self.result.hourglass_energy / self.result.total_energy
            ) * 100.0

        return self.result
