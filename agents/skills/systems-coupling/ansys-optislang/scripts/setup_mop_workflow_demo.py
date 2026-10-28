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
        self.optimization_settings: Dict[str, Any] = {
            "enabled": True,
            "algorithm": "NOAActor (NSGA-II)",
            "max_evaluations": 1000,
            "population_size": 50
        }

    def set_sampling_settings(
        self,
        num_samples: int = 100,
        method: str = "advanced_latin_hypercube"
    ) -> "OptislangMOPWorkflowBuilder":
        """設定 DoE 抽樣數量與演算法 (預設進階拉丁超立方 LHS)"""
        self.num_samples = num_samples
        self.sampling_method = method
        return self

    def set_optimization_settings(
        self,
        enabled: bool = True,
        algorithm: str = "NOAActor (NSGA-II)",
        max_evaluations: int = 1000,
        population_size: int = 50
    ) -> "OptislangMOPWorkflowBuilder":
        """配置基於 MOP ProxySolver 之全域/多目標最佳化設定"""
        self.optimization_settings = {
            "enabled": enabled,
            "algorithm": algorithm,
            "max_evaluations": max_evaluations,
            "population_size": population_size
        }
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
            ""
        ])

        if self.optimization_settings["enabled"]:
            algo = self.optimization_settings["algorithm"]
            max_evals = self.optimization_settings["max_evaluations"]
            pop_size = self.optimization_settings["population_size"]
            lines.extend([
                "# 5. 建立基於 MOP ProxySolver 之 Pareto 最佳化尋優節點",
                f"# opt = root_system.create_actor('{algo}')",
                f"# opt.set_setting('max_number_of_samples', {max_evals})",
                f"# opt.set_setting('population_size', {pop_size})",
                "# opt.connect_to_proxy_solver(sens.get_proxy_solver())",
                ""
            ])

        lines.extend([
            "# 6. 腳本配置完成",
            "print('optiSLang Sensitivity, MOP 與 Pareto 最佳化流程建立完畢！')"
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
    診斷代理模型過擬合 (Overfitting) 現象與複合預測品質
    """
    gap = r2 - cop
    low_cop_warning = cop < 0.60

    if gap > 0.25:
        is_overfitted = True
        risk_level = "嚴重過擬合"
        diag = f"決定係數 R^2={r2:.3f} 虛高，但預測係數 CoP={cop:.3f} 低落 (差距={gap:.3f})！模型已過度學習噪聲，強烈建議降低多項式階數或增加 LHS 樣本量。"
    elif gap > 0.15:
        is_overfitted = False
        risk_level = "輕度偏差"
        diag = f"R^2={r2:.3f} 與 CoP={cop:.3f} 差距 {gap:.3f} 在可接受邊緣，需留意局部非線性波動。"
    else:
        is_overfitted = False
        risk_level = "健康"
        diag = f"R^2={r2:.3f} 與 CoP={cop:.3f} 吻合良好 (差距={gap:.3f})，模型泛化能力可靠。"

    # 複合判定：若 CoP < 0.60，即便差距 gap <= 0.25，亦標記模型總體預測品質過低或無預測力 (Action Item 4)
    if low_cop_warning:
        diag += f" 【⚠️ 警告: 預測係數 CoP={cop:.3f} < 0.60，模型總體預測品質過低或無預測力，嚴禁作為工程優化元模型！】"
        risk_level += " (模型總體預測品質過低/無預測力)"

    return {
        "is_overfitted": is_overfitted,
        "risk_level": risk_level,
        "is_low_quality": low_cop_warning,
        "diagnosis": diag
    }


def extract_pareto_frontier(
    solutions: List[Dict[str, float]],
    objectives: List[str]
) -> List[Dict[str, float]]:
    """
    自候選解集中提取多目標非支配解 (Pareto Frontier)
    假設所有目標均為極小化 (Minimization)
    :param solutions: 包含目標值之候選解字典列表
    :param objectives: 目標鍵值名稱列表
    :return: 非支配 Pareto 最優前沿解集
    """
    pareto_front = []
    for i, sol_a in enumerate(solutions):
        dominated = False
        for j, sol_b in enumerate(solutions):
            if i == j:
                continue
            # 若 sol_b 在所有目標均不劣於 sol_a，且至少一個目標嚴格優於 sol_a，則 sol_a 被支配
            not_worse = all(sol_b[obj] <= sol_a[obj] for obj in objectives)
            strictly_better = any(sol_b[obj] < sol_a[obj] for obj in objectives)
            if not_worse and strictly_better:
                dominated = True
                break
        if not dominated:
            pareto_front.append(sol_a)
    return pareto_front


def select_compromise_solution(
    pareto_front: List[Dict[str, float]],
    objectives: List[str],
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    基於 Utopia (理想點) 歸一化歐氏距離挑選最佳折衷解 (Compromise Solution)
    :param pareto_front: Pareto 前沿解列表
    :param objectives: 目標列表
    :param weights: 各目標權重字典 (預設均等權重)
    :return: 最佳折衷點與歸一化指標
    """
    if not pareto_front:
        return {"error": "Pareto 前沿為空"}

    if weights is None:
        weights = {obj: 1.0 / len(objectives) for obj in objectives}

    # 計算各目標的最小 (理想) 與最大 (最劣) 值
    min_vals = {obj: min(s[obj] for s in pareto_front) for obj in objectives}
    max_vals = {obj: max(s[obj] for s in pareto_front) for obj in objectives}

    best_dist = float("inf")
    best_solution = None

    for sol in pareto_front:
        dist_sq = 0.0
        for obj in objectives:
            span = max_vals[obj] - min_vals[obj]
            norm_val = 0.0 if span == 0 else (sol[obj] - min_vals[obj]) / span
            dist_sq += (weights.get(obj, 1.0) * norm_val) ** 2
        dist = dist_sq ** 0.5
        if dist < best_dist:
            best_dist = dist
            best_solution = sol

    return {
        "best_compromise_solution": best_solution,
        "utopia_distance": round(best_dist, 4),
        "ideal_utopia_point": min_vals
    }


if __name__ == "__main__":
    # 範例執行 1：建立 10 桿桁架 (Ten-Bar Truss) 多目標 MOP 尋優流程
    builder = OptislangMOPWorkflowBuilder("Ten_Bar_Truss_MOP_Optimization")
    builder.set_sampling_settings(num_samples=50, method="advanced_latin_hypercube")
    builder.set_optimization_settings(enabled=True, algorithm="NOAActor (NSGA-II)", max_evaluations=1200)

    for i in range(1, 11):
        builder.add_continuous_parameter(f"Area_Bar_{i}", 0.1, 35.0, distribution="Uniform", reference_val=10.0)

    builder.add_response("Total_Mass", criterion="min", cop_threshold=0.95)
    builder.add_response("Max_Displacement", criterion="min", cop_threshold=0.85)

    script_str = builder.generate_optislang_python_script()
    print("=== 生成的 optiSLang 原生 Python 腳本 ===")
    print(script_str)

    # 範例執行 2：MOP 品質評估
    sample_cops = {
        "Total_Mass": 0.99,
        "Max_Displacement": 0.89,
        "Bar_Max_Stress": 0.74
    }
    eval_res = evaluate_mop_quality(sample_cops)
    print("\n=== MOP 品質評估報告 ===")
    print(f"全域合格狀態: {eval_res['all_passed']}")
    for k, v in eval_res["details"].items():
        print(f"- 響應 {k}: CoP={v['cop']:.2f} ({v['grade']}) -> {v['action']}")

    # 範例執行 3：TSI 敏感度過濾
    sample_tsi = {
        "Area_Bar_1": 0.38,
        "Area_Bar_3": 0.29,
        "Area_Bar_6": 0.18,
        "Area_Bar_2": 0.08,
        "Area_Bar_10": 0.02
    }
    tsi_res = filter_parameters_by_tsi(sample_tsi, threshold=0.05)
    print("\n=== TSI 降維過濾結論 ===")
    print(tsi_res["reduction_summary"])
    print(f"保留關鍵參數: {tsi_res['critical_parameters']}")
    print(f"剔除雜訊參數: {tsi_res['noise_parameters']}")

    # 範例執行 4：過擬合診斷
    overfit_check = diagnose_overfitting(r2=0.98, cop=0.62)
    print("\n=== 過擬合診斷 ===")
    print(f"風險等級: {overfit_check['risk_level']}, 評語: {overfit_check['diagnosis']}")

    # 範例執行 5：Pareto 前沿非支配解集提取與折衷解決策
    candidate_solutions = [
        {"id": 1, "Total_Mass": 1500.0, "Max_Displacement": 1.25},
        {"id": 2, "Total_Mass": 1800.0, "Max_Displacement": 0.95},
        {"id": 3, "Total_Mass": 2200.0, "Max_Displacement": 0.72},
        {"id": 4, "Total_Mass": 1900.0, "Max_Displacement": 1.10},  # 被 id 2 支配
        {"id": 5, "Total_Mass": 2500.0, "Max_Displacement": 0.65}
    ]
    pareto_pts = extract_pareto_frontier(candidate_solutions, ["Total_Mass", "Max_Displacement"])
    print(f"\n=== Pareto 前沿解集提取 (共 {len(pareto_pts)} 個非支配點) ===")
    for pt in pareto_pts:
        print(f"  - 解 ID {pt['id']}: 質量 = {pt['Total_Mass']} lb, 最大位移 = {pt['Max_Displacement']} in")

    compromise = select_compromise_solution(pareto_pts, ["Total_Mass", "Max_Displacement"])
    best_sol = compromise["best_compromise_solution"]
    print("\n=== Utopia 理想點最小歐式距離折衷解 ===")
    print(f"  -> 最優折衷方案: 解 ID {best_sol['id']} (質量={best_sol['Total_Mass']}, 位移={best_sol['Max_Displacement']})")
    print(f"  -> 歸一化 Utopia 距離: {compromise['utopia_distance']}")
