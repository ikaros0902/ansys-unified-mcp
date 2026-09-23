"""
ANSYS Workbench DesignXplorer 參數集自動化驅動與 optiSLang 雙軌選型腳本。
"""

from typing import Dict, Any, List

class WorkbenchParameterSetAutomator:
    """Workbench 原生 Parameter Set 自動化腳本生成器。"""

    def __init__(self):
        self.design_points: List[Dict[str, float]] = []

    def add_design_point(self, param_values: Dict[str, float]) -> None:
        self.design_points.append(param_values)

    def generate_workbench_journal_script(self) -> str:
        lines: List[str] = [
            "# -*- coding: utf-8 -*-",
            "# ANSYS Workbench Journal - DesignXplorer Parameter Set Batch Update",
            "parameters = Parameters",
            "designPoint_base = parameters.GetDesignPoint(Name='DP 0')",
            ""
        ]

        for idx, dp_dict in enumerate(self.design_points, start=1):
            lines.append(f"dp_{idx} = parameters.CreateDesignPoint()")
            for p_name, p_val in dp_dict.items():
                lines.append(
                    f"dp_{idx}.SetParameterExpression("
                    f"Parameter=parameters.GetParameter(Name='{p_name}'), "
                    f"Expression='{p_val}')"
                )
            lines.append("")

        lines.extend([
            "parameters.UpdateAllDesignPoints()",
            "parameters.ExportDesignPointsTable(FilePath='Parameter_Results.csv')",
            "Save(Overwrite=True)"
        ])
        return "\n".join(lines)

def evaluate_optimization_platform(
    num_parameters: int,
    is_strongly_nonlinear: bool,
    requires_robustness: bool,
    has_mixed_solvers: bool
) -> Dict[str, Any]:
    """依據工程情境推薦 Workbench DesignXplorer 或升級 optiSLang 之雙軌決策。"""
    reasons: List[str] = []
    use_optislang = False

    if num_parameters > 10:
        use_optislang = True
        reasons.append(f"設計變數數量為 {num_parameters} (> 10)，DX 易產生維度災難，optiSLang TSI 指標能自動降維。")

    if is_strongly_nonlinear:
        use_optislang = True
        reasons.append("系統具備高度非線性/數值雜訊，optiSLang MOP 能自動競賽選出最佳元模型。")

    if requires_robustness:
        use_optislang = True
        reasons.append("需要隨機分佈穩健性 (Robustness) 與可靠度分析。")

    if has_mixed_solvers:
        use_optislang = True
        reasons.append("需要跨軟體求解串聯，optiSLang 具備節點式流程編排器。")

    if not use_optislang:
        return {
            "recommended_tool": "Workbench DesignXplorer (DX)",
            "migration_required": False,
            "rationale": "參數數量適中 (<10) 且響應連續平滑，DX 原生介面操作簡捷高效。"
        }
    else:
        return {
            "recommended_tool": "ANSYS optiSLang",
            "migration_required": True,
            "rationale": " ； ".join(reasons)
        }
