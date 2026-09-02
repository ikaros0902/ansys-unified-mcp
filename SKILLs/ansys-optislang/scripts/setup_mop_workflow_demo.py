# -*- coding: utf-8 -*-
"""
模組名稱：setup_mop_workflow_demo.py
功能說明：ANSYS optiSLang 參數敏感度分析、MOP 最佳預測元模型與最佳化建立腳本
依據標準：林明志標準 預測係數 CoP >= 0.8 驗證門檻、TSI 降維過濾與過擬合診斷
"""

from typing import Dict, Any, List, Optional


class OptislangMOPWorkflowBuilder:
    """
    optiSLang 原生 Python 流程建立器 (相容於 run_optislang_script API)
    """

    def __init__(self, workflow_name: str = "Parametric_MOP_Optimization"):
        self.workflow_name = workflow_name
        self.parameters: List[Dict[str, Any]] = []
        self.responses: List[Dict[str, Any]] = []
        self.num_samples: int = 100
        self.sampling_method: str = "advanced_latin_hypercube"

    def set_sampling_settings(
        self,
        num_samples: int = 100,
        method: str = "advanced_latin_hypercube"
    ) -> "OptislangMOPWorkflowBuilder":
        """設定 DoE 抽樣數量與演算法 (預設進階拉丁超立方 LHS)"""
        self.num_samples = num_samples
        self.sampling_method = method
        return self

    def add_continuous_parameter(
        self,
        name: str,
        lower_bound: float,
        upper_bound: float,
        distribution: str = "Uniform",
        reference_val: Optional[float] = None
    ) -> "OptislangMOPWorkflowBuilder":
        """註冊連續隨機參數"""
        if reference_val is None:
            reference_val = (lower_bound + upper_bound) / 2.0
        self.parameters.append({
            "name": name,
            "lower": lower_bound,
            "upper": upper_bound,
            "distribution": distribution,
            "ref": reference_val
        })
        return self

    def add_response(
        self,
        name: str,
        criterion: str = "min",
        cop_threshold: float = 0.80
    ) -> "OptislangMOPWorkflowBuilder":
        """註冊輸出響應與目標"""
        self.responses.append({
            "name": name,
            "criterion": criterion,
            "cop_threshold": cop_threshold
        })
        return self

    def generate_optislang_python_script(self) -> str:
        """
        產生可在 optiSLang 中由 run_optislang_script 執行的原生 Python 腳本
        """
        lines: List[str] = [
            "# -*- coding: utf-8 -*-",
            f"# optiSLang 原生自動化流程建置腳本: {self.workflow_name}",
            "# 依據林明志標準: MOP 最佳模型自動競賽與 CoP >= 0.8 驗證門檻",
            "import actors",
            "",
            "# 1. 建立 Sensitivity 敏感度分析節點",
            f"sens = actors.SensitivityActor('{self.workflow_name}_Sensitivity')",
            "add_actor(sens)",
            "",
            "# 2. 設定抽樣演算法與樣本數",
            f"sens.set_setting('sampling_method', '{self.sampling_method}')",
            f"sens.set_setting('number_of_samples', {self.num_samples})",
            "sens.set_setting('criterion', 'maximin')",
            "",
            "# 3. 註冊參數空間與邊界"
        ]

        for p in self.parameters:
            lines.append(f"# 參數: {p['name']} [{p['lower']}, {p['upper']}] ({p['distribution']})")
            lines.append(f"# sens.register_parameter('{p['name']}', {p['lower']}, {p['upper']}, '{p['distribution']}')")

        lines.extend([
            "",
            "# 4. 啟用 MOP (Metamodel of Optimal Prognosis) 最佳模型自動競賽",
            "sens.set_setting('enable_mop', True)",
            "sens.set_setting('mop_polynomial', True)",
            "sens.set_setting('mop_kriging', True)",
            "sens.set_setting('mop_mls', True)",
            "sens.set_setting('cop_threshold', 0.80)",
            "",
            "# 5. 腳本配置完成",
            "print('optiSLang Sensitivity 與 MOP 流程建立完畢！')"
        ])

        return "\n".join(lines)


# ----------------------------------------------------------------------
# 【判斷力庫】客觀驗證評估函數
# ----------------------------------------------------------------------
def evaluate_mop_quality(cop_scores: Dict[str, float]) -> Dict[str, Any]:
    """
    依據林明志標準評估 MOP 代理模型之預測係數 (CoP)
    :param cop_scores: 字典 {響應名稱: CoP 數值}
    :return: 診斷評估結果
    """
    results = {}
    all_passed = True

    for resp_name, cop in cop_scores.items():
        if cop >= 0.95:
            grade = "極佳 (Excellent)"
            action = "精度極高，可直接完全取代 CAE 實體運算進行全域尋優與蒙地卡羅分析。"
            passed = True
        elif cop >= 0.80:
            grade = "良好 (Good) [合格門檻]"
            action = "達到工程驗證合格標準，可安全放行用於趨勢評估與代理模型尋優。"
            passed = True
        elif cop >= 0.60:
            grade = "中等 (Fair) [未達標]"
            action = "局部非線性失真，嚴禁直接全局尋優！建議使用自適應採樣 (Adaptive Sampling) 補充樣本點。"
            passed = False
            all_passed = False
        else:
            grade = "不合格 (Poor) [嚴重紅線]"
            action = "嚴禁交付結果！模型毫無泛化能力，需縮小參數區間或排查 CAE 求解網格噪聲。"
            passed = False
            all_passed = False

        results[resp_name] = {
            "cop": cop,
            "grade": grade,
            "passed": passed,
            "action": action
        }

    return {
        "all_passed": all_passed,
        "details": results
    }


def filter_parameters_by_tsi(tsi_dict: Dict[str, float], threshold: float = 0.05) -> Dict[str, Any]:
    """
    依據總靈敏度指數 (TSI) 進行主動降維過濾
    :param tsi_dict: 字典 {參數名: TSI 數值}
    :param threshold: 顯著性門檻 (預設 5% 即 0.05)
    """
    critical_params = []
    noise_params = []

    for param, tsi in tsi_dict.items():
        if tsi >= threshold:
            critical_params.append((param, tsi))
        else:
            noise_params.append((param, tsi))

    # 按 TSI 由大到小排序
    critical_params.sort(key=lambda x: x[1], reverse=True)
    noise_params.sort(key=lambda x: x[1], reverse=True)

    return {
        "critical_parameters": critical_params,
        "noise_parameters": noise_params,
        "reduction_summary": f"原始參數 {len(tsi_dict)} 個，篩選出關鍵驅動參數 {len(critical_params)} 個，凍結雜訊參數 {len(noise_params)} 個。"
    }


def diagnose_overfitting(r2: float, cop: float) -> Dict[str, Any]:
    """
    診斷代理模型過擬合 (Overfitting) 現象
    """
    gap = r2 - cop
    if gap > 0.25:
        return {
            "is_overfitted": True,
            "risk_level": "嚴重過擬合",
            "diagnosis": f"決定係數 R^2={r2:.3f} 虛高，但預測係數 CoP={cop:.3f} 低落 (差距={gap:.3f})！模型已過度學習噪聲，強烈建議降低多項式階數或增加 LHS 樣本量。"
        }
    elif gap > 0.15:
        return {
            "is_overfitted": False,
            "risk_level": "輕度偏差",
            "diagnosis": f"R^2={r2:.3f} 與 CoP={cop:.3f} 差距 {gap:.3f} 在可接受邊緣，需留意局部非線性波動。"
        }
    else:
        return {
            "is_overfitted": False,
            "risk_level": "健康",
            "diagnosis": f"R^2={r2:.3f} 與 CoP={cop:.3f} 吻合良好 (差距={gap:.3f})，模型泛化能力可靠。"
        }


if __name__ == "__main__":
    # 範例執行：建立 5 參數結構最佳化 MOP 流程
    builder = OptislangMOPWorkflowBuilder("Bracket_Structural_MOP")
    builder.set_sampling_settings(num_samples=80, method="advanced_latin_hypercube")
    builder.add_continuous_parameter("Rib_Thickness", 1.0, 5.0)
    builder.add_continuous_parameter("Flange_Width", 20.0, 60.0)
    builder.add_continuous_parameter("Fillet_Radius", 2.0, 8.0)
    builder.add_continuous_parameter("Hole_Diameter", 10.0, 25.0)
    builder.add_continuous_parameter("Material_Yield", 250.0, 400.0)
    builder.add_response("Max_Equivalent_Stress", criterion="min", cop_threshold=0.85)
    builder.add_response("Total_Mass", criterion="min", cop_threshold=0.95)

    script_str = builder.generate_optislang_python_script()
    print("=== 生成的 optiSLang 原生 Python 腳本 ===")
    print(script_str)

    # 執行 MOP 品質評估演示
    sample_cops = {
        "Max_Equivalent_Stress": 0.88,
        "Total_Mass": 0.98,
        "Deformation_Z": 0.68
    }
    eval_res = evaluate_mop_quality(sample_cops)
    print("\n=== MOP 品質評估報告 ===")
    print(f"全域合格狀態: {eval_res['all_passed']}")
    for k, v in eval_res["details"].items():
        print(f"- 響應 {k}: CoP={v['cop']:.2f} ({v['grade']}) -> {v['action']}")

    # 執行 TSI 降維過濾演示
    sample_tsi = {
        "Rib_Thickness": 0.52,
        "Flange_Width": 0.31,
        "Fillet_Radius": 0.08,
        "Hole_Diameter": 0.03,
        "Material_Yield": 0.01
    }
    tsi_res = filter_parameters_by_tsi(sample_tsi, threshold=0.05)
    print("\n=== TSI 降維過濾結論 ===")
    print(tsi_res["reduction_summary"])
    print(f"保留關鍵參數: {tsi_res['critical_parameters']}")
    print(f"剔除雜訊參數: {tsi_res['noise_parameters']}")

    # 執行過擬合診斷演示
    overfit_check = diagnose_overfitting(r2=0.98, cop=0.62)
    print("\n=== 過擬合診斷 ===")
    print(f"風險等級: {overfit_check['risk_level']}, 評語: {overfit_check['diagnosis']}")
