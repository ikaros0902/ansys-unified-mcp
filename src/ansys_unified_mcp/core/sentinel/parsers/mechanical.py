"""ANSYS Unified MCP 2.0 - Mechanical / MAPDL 求解日誌解析器 (MechanicalMAPDLParser).

負責串流監控與解析 Mechanical / MAPDL 求解輸出日誌 (solve.out)：
- 提取子步、時間步長與累積平衡迭代次數
- 解析力平衡殘差 (FORCE CONVERGENCE VALUE) 與收斂準則 (CRITERION)
- 實時捕捉單元嚴重畸變 (Highly distorted)、負雅可比 (Negative Jacobian) 與發散徵兆
- 偵測數值異常 (NaN / Inf)
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MechanicalParseResult:
    """Mechanical 求解日誌解析快照。"""

    current_load_step: int = 1
    current_substep: int = 0
    current_time: float = 0.0
    cumulative_iterations: int = 0
    force_convergence_value: Optional[float] = None
    force_criterion: Optional[float] = None
    is_converged: bool = False
    has_distortion: bool = False
    distortion_warnings: List[str] = field(default_factory=list)
    has_nan_inf: bool = False
    error_messages: List[str] = field(default_factory=list)
    progress_pct: float = 0.0
    history: List[Dict[str, Any]] = field(default_factory=list)


class MechanicalMAPDLParser:
    """MAPDL / Mechanical solve.out 日誌解析器。"""

    RE_SUBSTEP = re.compile(
        r"^\s*INCREMENT\s+(\d+)\s+SUBSTEP\s+(\d+)\s+TIME=\s*([\d\.E\+\-]+)",
        re.IGNORECASE | re.MULTILINE,
    )
    RE_LOAD_STEP = re.compile(
        r"^\s*LOAD\s+STEP\s+(\d+)\s+SUBSTEP\s+(\d+)",
        re.IGNORECASE | re.MULTILINE,
    )
    RE_CUMULATIVE_ITER = re.compile(
        r"C\s*U\s*M\s*U\s*L\s*A\s*T\s*I\s*V\s*E\s+I\s*T\s*E\s*R\s*A\s*T\s*I\s*O\s*N\s*=\s*(\d+)",
        re.IGNORECASE,
    )
    RE_FORCE_CONVERGENCE = re.compile(
        r"FORCE CONVERGENCE VALUE\s*=\s*([\d\.E\+\-]+|NaN|INF)\s+CRITERION\s*=\s*([\d\.E\+\-]+)",
        re.IGNORECASE,
    )
    RE_CONVERGED = re.compile(
        r"(SOLUTION IS CONVERGED|SOLUTION CONVERGED|SUBSTEP CONVERGED|SOLUTION FINISHED|MECHANICAL SOLUTION COMPLETED)",
        re.IGNORECASE,
    )
    RE_NOT_CONVERGED = re.compile(
        r"(Substep not converged|EQUILIBRIUM ITERATION NOT CONVERGED|The system of equations was not solved)",
        re.IGNORECASE,
    )
    RE_DISTORTION = re.compile(
        r"(Element \d+ has become highly distorted|Negative jacobian|Substep not converged|"
        r"EQUILIBRIUM ITERATION NOT CONVERGED|The system of equations was not solved)",
        re.IGNORECASE,
    )
    RE_NAN_INF = re.compile(r"\b(nan|inf|#ind|#qnan)\b", re.IGNORECASE)

    def __init__(self, target_end_time: float = 1.0) -> None:
        """初始化解析器。"""
        self.target_end_time = max(target_end_time, 1e-6)
        self.result = MechanicalParseResult()

    def parse_chunk(self, content: str) -> MechanicalParseResult:
        """增量解析日誌文本區塊。"""
        if not content:
            return self.result

        # 檢測 NaN / Inf
        if self.RE_NAN_INF.search(content):
            self.result.has_nan_inf = True
            self.result.error_messages.append("檢測到數值 NaN/Inf 發散徵兆")

        has_not_converged_flag = False

        for line in content.splitlines():
            line_str = line.strip()
            if not line_str:
                continue

            # 檢驗未收斂錯誤
            if self.RE_NOT_CONVERGED.search(line_str):
                has_not_converged_flag = True

            # 檢驗單元畸變
            dist_match = self.RE_DISTORTION.search(line_str)
            if dist_match:
                self.result.has_distortion = True
                msg = dist_match.group(1)
                if msg not in self.result.distortion_warnings:
                    self.result.distortion_warnings.append(msg)

            # 解析子步與時間
            sub_match = self.RE_SUBSTEP.search(line_str)
            if sub_match:
                self.result.current_load_step = int(sub_match.group(1))
                self.result.current_substep = int(sub_match.group(2))
                try:
                    self.result.current_time = float(sub_match.group(3))
                    pct = min(100.0, max(0.0, (self.result.current_time / self.target_end_time) * 100.0))
                    self.result.progress_pct = round(pct, 2)
                except ValueError:
                    pass

            load_match = self.RE_LOAD_STEP.search(line_str)
            if load_match and not sub_match:
                self.result.current_load_step = int(load_match.group(1))
                self.result.current_substep = int(load_match.group(2))

            cum_match = self.RE_CUMULATIVE_ITER.search(line_str)
            if cum_match:
                try:
                    self.result.cumulative_iterations = int(cum_match.group(1))
                except ValueError:
                    pass

            conv_match = self.RE_FORCE_CONVERGENCE.search(line_str)
            if conv_match:
                val_str = conv_match.group(1)
                crit_str = conv_match.group(2)
                try:
                    crit = float(crit_str)
                    self.result.force_criterion = crit
                    if val_str.lower() in ("nan", "inf"):
                        self.result.has_nan_inf = True
                        val = float("nan")
                    else:
                        val = float(val_str)
                    self.result.force_convergence_value = val
                    self.result.history.append({
                        "substep": self.result.current_substep,
                        "iteration": self.result.cumulative_iterations,
                        "time": self.result.current_time,
                        "force_val": val,
                        "criterion": crit,
                        "converged": (val <= crit) if not math.isnan(val) else False,
                    })
                except ValueError:
                    pass

            if self.RE_CONVERGED.search(line_str) and not has_not_converged_flag:
                self.result.is_converged = True

        if has_not_converged_flag:
            self.result.is_converged = False

        if self.result.is_converged or self.result.current_time >= self.target_end_time:
            self.result.progress_pct = 100.0

        return self.result
