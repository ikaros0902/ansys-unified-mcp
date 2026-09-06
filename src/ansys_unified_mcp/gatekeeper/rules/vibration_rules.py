"""ANSYS Unified MCP 2.0 - 振動與反應譜前置物理安全閘門 (Vibration Rules).

包含：
- GATE-VIB-001: 三向有效模態質量累積佔比檢核 (>= 90%)
- GATE-VIB-002: 模態截斷頻率充裕度檢核 (>= 激振上限 1.5x)
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Set

from ansys_unified_mcp.gatekeeper.prescription import (
    ActionCodeEnum,
    CheckResult,
    PrescriptionDetail,
    RuleStatusEnum,
    SeverityEnum,
)
from ansys_unified_mcp.gatekeeper.rules import BaseGateRule


class ModalEffectiveMassRatioRule(BaseGateRule):
    """GATE-VIB-001: 三向有效模態質量累積佔比檢核規則。

    在隨機振動 (Random Vibration) 或反應譜分析 (Response Spectrum) 中，
    三向（或受激振主方向）累積有效模態質量佔比必須 >= 90.0% (0.90)。
    若未達標，高頻動態質量將嚴重失真，導致應力計算大幅低估。
    """

    rule_id = "GATE-VIB-001"
    rule_name = "Effective Modal Mass Ratio Guard"
    severity = SeverityEnum.FATAL
    target_workflows: Set[str] = {
        "random_vibration",
        "response_spectrum",
        "harmonic_response",
        "modal",
    }

    MIN_EFFECTIVE_MASS_RATIO: float = 0.90

    def check(self, context: Dict[str, Any]) -> CheckResult:
        # 支援多種上下文鍵名傳入
        mass_dict = context.get("effective_mass_ratio", {})
        rx = context.get("effective_mass_ratio_x", mass_dict.get("x", mass_dict.get("X")))
        ry = context.get("effective_mass_ratio_y", mass_dict.get("y", mass_dict.get("Y")))
        rz = context.get("effective_mass_ratio_z", mass_dict.get("z", mass_dict.get("Z")))

        excitation_dir = context.get("excitation_direction", context.get("direction"))
        if excitation_dir:
            excitation_dir = str(excitation_dir).strip().upper()

        current_modes = context.get("num_modes", context.get("current_num_modes", 12))

        observed: Dict[str, Any] = {
            "ratio_x": rx,
            "ratio_y": ry,
            "ratio_z": rz,
            "excitation_direction": excitation_dir or "ALL",
        }
        threshold: Dict[str, Any] = {
            "min_ratio": self.MIN_EFFECTIVE_MASS_RATIO,
            "required_directions": [excitation_dir] if excitation_dir in {"X", "Y", "Z"} else ["X", "Y", "Z"],
        }

        # 檢查是否完全缺少模態質量數據
        if rx is None and ry is None and rz is None:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatusEnum.BLOCKED,
                severity=self.severity,
                observed_value=observed,
                required_threshold=threshold,
                diagnosis="模型尚未求解模態有效質量或未提供 effective_mass_ratio 數據，無法驗證動態質量充分性。",
                prescription=PrescriptionDetail(
                    action_code=ActionCodeEnum.INCREASE_MODES_AND_CUTOFF.value,
                    suggested_fix="請先執行模態分析並提取參與質量 (Participation Factor / Effective Mass)。",
                    code_snippet=(
                        "modal_analysis = Model.Analyses[0]\n"
                        "modal_analysis.AnalysisSettings.NumberOfModes = 30\n"
                        "modal_analysis.Solve()"
                    ),
                ),
            )

        # 依照激振方向評估 (支援 Excitation-Oriented 檢查)
        directions_to_check = {}
        if excitation_dir == "X":
            directions_to_check["X"] = rx
        elif excitation_dir == "Y":
            directions_to_check["Y"] = ry
        elif excitation_dir == "Z":
            directions_to_check["Z"] = rz
        else:
            directions_to_check = {"X": rx, "Y": ry, "Z": rz}

        deficient_directions = []
        for d, val in directions_to_check.items():
            if val is None or float(val) < self.MIN_EFFECTIVE_MASS_RATIO:
                deficient_directions.append((d, val if val is not None else 0.0))

        if deficient_directions:
            diag_parts = [
                f"{d} 軸有效模態質量僅 {float(v)*100:.1f}%"
                for d, v in deficient_directions
            ]
            diag = (
                f"{', '.join(diag_parts)}，未達 90.0% 門檻。"
                "高頻動態質量未被充分激發，隨機振動應力計算將被嚴重低估！"
            )
            suggested_modes = max(int(current_modes) * 2, 30) if isinstance(current_modes, (int, float)) else 35
            return CheckResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatusEnum.BLOCKED,
                severity=self.severity,
                observed_value=observed,
                required_threshold=threshold,
                diagnosis=diag,
                prescription=PrescriptionDetail(
                    action_code=ActionCodeEnum.INCREASE_MODES_AND_CUTOFF.value,
                    suggested_fix=(
                        f"將模態分析提取階數從目前階數擴增至至少 {suggested_modes} 階，"
                        "或調高求解器頻率上限範圍以捕獲足夠有效質量。"
                    ),
                    code_snippet=(
                        "modal_analysis = Model.Analyses[0]\n"
                        f"modal_analysis.AnalysisSettings.NumberOfModes = {suggested_modes}\n"
                        "modal_analysis.Solve()"
                    ),
                ),
            )

        # 通過放行
        return CheckResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            status=RuleStatusEnum.PASSED,
            severity=SeverityEnum.INFO,
            observed_value=observed,
            required_threshold=threshold,
            diagnosis="三向（或主激振方向）有效模態質量累積佔比皆達到或超越 90.0% 物理標準，允許送算。",
            prescription=None,
        )


class ModalCutoffFrequencyRule(BaseGateRule):
    """GATE-VIB-002: 模態截斷頻率充裕度檢核規則。

    模態最高固有頻率 f_cutoff 必須 >= 激振頻率上限之 1.5 倍 (1.5 * f_max)。
    防止在截斷頻率邊界處遺漏結構共振模態。
    """

    rule_id = "GATE-VIB-002"
    rule_name = "Cutoff Frequency Margin Guard"
    severity = SeverityEnum.FATAL
    target_workflows: Set[str] = {
        "random_vibration",
        "response_spectrum",
        "harmonic_response",
        "shock_analysis",
    }

    CUTOFF_MARGIN_MULTIPLIER: float = 1.5

    def check(self, context: Dict[str, Any]) -> CheckResult:
        cutoff_hz = context.get("cutoff_frequency_hz")
        if cutoff_hz is None:
            freq_list = context.get("modal_frequencies_hz") or context.get("frequencies_hz")
            if freq_list and isinstance(freq_list, list) and len(freq_list) > 0:
                cutoff_hz = max(float(f) for f in freq_list)

        max_excitation_hz = context.get("max_excitation_frequency_hz")
        if max_excitation_hz is None:
            psd_table = context.get("psd_table")
            if psd_table and isinstance(psd_table, list) and len(psd_table) > 0:
                # psd_table 格式: [(freq, g2_per_hz), ...]
                max_excitation_hz = max(float(point[0]) for point in psd_table)

        observed: Dict[str, Any] = {
            "cutoff_frequency_hz": cutoff_hz,
            "max_excitation_frequency_hz": max_excitation_hz,
        }

        if cutoff_hz is None or max_excitation_hz is None:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatusEnum.BLOCKED,
                severity=self.severity,
                observed_value=observed,
                required_threshold={"margin_factor": self.CUTOFF_MARGIN_MULTIPLIER},
                diagnosis="缺少模態截斷頻率 (cutoff_frequency_hz) 或激振頻率上限 (max_excitation_frequency_hz) 數據。",
                prescription=PrescriptionDetail(
                    action_code=ActionCodeEnum.EXTEND_FREQUENCY_RANGE.value,
                    suggested_fix="請在模態分析與振動載荷中明確定義最高分析頻率與激振 PSD 頻率上限。",
                    code_snippet=(
                        "modal_analysis = Model.Analyses[0]\n"
                        "modal_analysis.AnalysisSettings.RangeMaximum = Quantity(2000.0, 'Hz')"
                    ),
                ),
            )

        required_min_cutoff = float(max_excitation_hz) * self.CUTOFF_MARGIN_MULTIPLIER
        threshold: Dict[str, Any] = {
            "max_excitation_frequency_hz": max_excitation_hz,
            "required_min_cutoff_hz": required_min_cutoff,
            "margin_factor": self.CUTOFF_MARGIN_MULTIPLIER,
        }

        if float(cutoff_hz) < required_min_cutoff:
            suggested_cutoff = round(required_min_cutoff * 1.1, 1)
            return CheckResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatusEnum.BLOCKED,
                severity=self.severity,
                observed_value=observed,
                required_threshold=threshold,
                diagnosis=(
                    f"模態截斷頻率 ({float(cutoff_hz):.1f} Hz) 低於激振頻率上限 "
                    f"({float(max_excitation_hz):.1f} Hz) 之 1.5 倍門檻 ({required_min_cutoff:.1f} Hz)。"
                    "截斷邊界處之高頻動態響應將被截斷失真，存在高頻未解共振之安全隱患！"
                ),
                prescription=PrescriptionDetail(
                    action_code=ActionCodeEnum.EXTEND_FREQUENCY_RANGE.value,
                    suggested_fix=(
                        f"請調高模態提取範圍上限至至少 {required_min_cutoff:.1f} Hz "
                        f"(建議設定為 {suggested_cutoff:.1f} Hz) 並重新提取高階振型。"
                    ),
                    code_snippet=(
                        "modal_analysis = Model.Analyses[0]\n"
                        f"modal_analysis.AnalysisSettings.RangeMaximum = Quantity({suggested_cutoff:.1f}, 'Hz')\n"
                        "modal_analysis.Solve()"
                    ),
                ),
            )

        return CheckResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            status=RuleStatusEnum.PASSED,
            severity=SeverityEnum.INFO,
            observed_value=observed,
            required_threshold=threshold,
            diagnosis="模態截斷頻率滿足激振上限 1.5 倍充裕度門檻，高頻共振保護合格。",
            prescription=None,
        )
