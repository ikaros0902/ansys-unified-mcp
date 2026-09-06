"""ANSYS Unified MCP 2.0 - Fluent 流體求解日誌解析器 (FluentResidualParser).

負責串流監控與解析 Fluent 求解輸出日誌 (fluent.log)：
- 提取迭代步數與各方程殘差 (continuity, x/y/z-velocity, energy, k, omega 等)
- 偵測數值異常與發散徵兆 (NaN / Inf / #ind / #qnan)
- 監控逆流警告 (reversed flow in N faces)
- 評估殘差連續指數級暴增發散
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FluentParseResult:
    """Fluent 求解日誌解析快照。"""

    current_iteration: int = 0
    residuals: Dict[str, float] = field(default_factory=dict)
    reversed_flow_faces: int = 0
    has_nan_inf: bool = False
    is_diverged: bool = False
    is_converged: bool = False
    progress_pct: float = 0.0
    warnings: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)


class FluentResidualParser:
    """Fluent fluent.log 日誌解析器。"""

    # 正則表達式
    RE_ITER_LINE = re.compile(
        r"^\s*(\d+)\s+([\d\.e\+\-]+)(?:\s+([\d\.e\+\-]+))?(?:\s+([\d\.e\+\-]+))?(?:\s+([\d\.e\+\-]+))?",
        re.IGNORECASE,
    )
    RE_REVERSED_FLOW = re.compile(r"reversed flow in (\d+) faces", re.IGNORECASE)
    RE_CONVERGED = re.compile(r"solution is converged", re.IGNORECASE)
    RE_NAN_INF = re.compile(r"\b(nan|inf|#ind|#qnan)\b", re.IGNORECASE)
    RE_HEADER = re.compile(r"iter\s+continuity", re.IGNORECASE)

    def __init__(self, target_iterations: int = 500) -> None:
        """初始化解析器。

        Args:
            target_iterations: 預期總迭代次數（用於估算進度百分比）
        """
        self.target_iterations = max(target_iterations, 1)
        self.result = FluentParseResult()
        self._residual_names = ["continuity", "x_velocity", "y_velocity", "z_velocity", "energy"]
        self._consecutive_growth_count = 0
        self._last_continuity = 0.0

    def parse_chunk(self, content: str) -> FluentParseResult:
        """增量解析 Fluent 日誌文本區塊。

        Args:
            content: 日誌片段或全文

        Returns:
            FluentParseResult: 當前解析快照
        """
        if not content:
            return self.result

        # 檢測 NaN / Inf
        if self.RE_NAN_INF.search(content):
            self.result.has_nan_inf = True
            self.result.is_diverged = True
            self.result.error_messages.append("Fluent 殘差出現 NaN/Inf 數值發散")

        for line in content.splitlines():
            line_str = line.strip()
            if not line_str:
                continue

            # 逆流警告
            rev_match = self.RE_REVERSED_FLOW.search(line_str)
            if rev_match:
                try:
                    count = int(rev_match.group(1))
                    self.result.reversed_flow_faces = count
                    msg = f"邊界層檢測到逆流: {count} 個面網格"
                    if msg not in self.result.warnings:
                        self.result.warnings.append(msg)
                except ValueError:
                    pass

            # 收斂判定
            if self.RE_CONVERGED.search(line_str):
                self.result.is_converged = True
                self.result.progress_pct = 100.0

            # 迭代與殘差行
            # 先排除標頭行
            if self.RE_HEADER.search(line_str):
                # 嘗試解析動態欄位標頭
                tokens = line_str.split()
                if len(tokens) > 1 and tokens[0].lower() == "iter":
                    self._residual_names = [t.lower().replace("-", "_") for t in tokens[1:]]
                continue

            iter_match = self.RE_ITER_LINE.match(line_str)
            if iter_match:
                try:
                    tokens = line_str.split()
                    it_num = int(tokens[0])
                    self.result.current_iteration = it_num

                    res_dict: Dict[str, float] = {}
                    for i, token in enumerate(tokens[1:]):
                        if i < len(self._residual_names):
                            name = self._residual_names[i]
                            try:
                                res_dict[name] = float(token)
                            except ValueError:
                                pass

                    if res_dict:
                        self.result.residuals = res_dict
                        cont_res = res_dict.get("continuity", 0.0)

                        # 檢測連續暴增發散 (單調增長超過 10 步且大於 1e6)
                        if cont_res > self._last_continuity and cont_res > 1.0:
                            self._consecutive_growth_count += 1
                            if self._consecutive_growth_count >= 10 and cont_res > 1e6:
                                self.result.is_diverged = True
                                self.result.error_messages.append(
                                    f"連續性殘差連續 {self._consecutive_growth_count} 步暴增至 {cont_res:.2e}，判定發散"
                                )
                        else:
                            self._consecutive_growth_count = 0
                        self._last_continuity = cont_res

                        # 更新進度百分比
                        if not self.result.is_converged:
                            pct = min(100.0, max(0.0, (it_num / self.target_iterations) * 100.0))
                            self.result.progress_pct = round(pct, 2)

                        self.result.history.append({
                            "iteration": it_num,
                            "residuals": dict(res_dict),
                        })
                except (ValueError, IndexError):
                    pass

        return self.result
