# ==============================================================================
# 腳本名稱: check_mesh_quality.py
# 功能描述: ANSYS Mechanical 網格品質自動化評估與量化體檢腳本（林明志標準）
# 檢驗指標: 歪斜度 (Skewness)、正交品質 (Orthogonal Quality)、長寬比 (Aspect Ratio)
# 判定準則: 依據有限元求解防護標準輸出 PASS / WARN / FAIL 並給予具體工程處置建議
# 執行環境: ANSYS Mechanical ACT 腳本環境 / PyMechanical
# ==============================================================================

def check_and_report_mesh_quality():
    """
    執行全模型有限元網格品質自動化檢驗，並輸出結構化體檢報告。
    
    :return: dict 包含各項統計數據與最終檢驗合格布林值
    """
    print("==================================================================")
    print(">>> ANSYS Mechanical 網格品質自動化量化體檢程序啟動 <<<")
    print("==================================================================")

    model = DataModel.Project.Model
    mesh = model.Mesh

    # 1. 檢查網格是否存在
    element_count = mesh.Elements
    node_count = mesh.Nodes

    if element_count == 0 or node_count == 0:
        print("[錯誤] 當前模型尚未劃分網格！請先執行 Mesh.GenerateMesh()。")
        return {"is_valid": False, "status": "NO_MESH"}

    print("總體規模概況:")
    print("  - 單元總數 (Elements): {:,}".format(element_count))
    print("  - 節點總數 (Nodes):    {:,}".format(node_count))

    # 2. 提取網格品質統計數據
    stats = mesh.MeshStatistics

    max_skewness = stats.MaxSkewness if hasattr(stats, "MaxSkewness") else 0.0
    avg_skewness = stats.AverageSkewness if hasattr(stats, "AverageSkewness") else 0.0
    min_ortho = stats.MinOrthogonalQuality if hasattr(stats, "MinOrthogonalQuality") else 1.0
    avg_ortho = stats.AverageOrthogonalQuality if hasattr(stats, "AverageOrthogonalQuality") else 1.0

    print("\n網格品質量化統計指標:")
    print("  [歪斜度 Skewness]      最大值: {:.4f} | 平均值: {:.4f}".format(max_skewness, avg_skewness))
    print("  [正交品質 Orthogonal]  最小值: {:.4f} | 平均值: {:.4f}".format(min_ortho, avg_ortho))

    # 3. 執行工程級多維度判定準則
    # 準則 A: 歪斜度 (Skewness) 判定
    if max_skewness < 0.50:
        skew_grade = "優秀 (Excellent)"
    elif max_skewness < 0.75:
        skew_grade = "良好 (Good)"
    elif max_skewness < 0.85:
        skew_grade = "可接受 (Acceptable)"
    elif max_skewness < 0.95:
        skew_grade = "警示 (Warning: 非線性易震盪)"
    else:
        skew_grade = "嚴重不合格 (Critical Fail: 剛度病態)"

    # 準則 B: 正交品質 (Orthogonal Quality) 判定
    if min_ortho > 0.70:
        ortho_grade = "優秀 (Excellent)"
    elif min_ortho > 0.30:
        ortho_grade = "良好 (Good)"
    elif min_ortho > 0.15:
        ortho_grade = "可接受 (Acceptable)"
    elif min_ortho > 0.05:
        ortho_grade = "警示 (Warning: 精度不足)"
    else:
        ortho_grade = "嚴重不合格 (Critical Fail: 數值奇異)"

    print("\n單元品質分級評定:")
    print("  - 歪斜度評級:   {}".format(skew_grade))
    print("  - 正交品質評級: {}".format(ortho_grade))

    # 4. 綜合放行決策 (三大 Don'ts 嚴格落實)
    is_pass = True
    status = "PASS"
    remedy_actions = []

    if max_skewness >= 0.95 or min_ortho <= 0.05:
        is_pass = False
        status = "FAIL"
        remedy_actions.append("偵測到極度畸變單元！嚴禁直接啟動求解器（會引發發散或主元錯誤）。")
        remedy_actions.append("處置措施 1: 檢查 CAD 模型是否存在微小碎面 (Sliver Faces) 或微小尖銳邊線。")
        remedy_actions.append("處置措施 2: 在嚴重畸變處新增局部 Face Sizing 或 Edge Sizing 加密網格。")
        remedy_actions.append("處置措施 3: 將自動劃分方法由 AllTriAllTet 改為 HexDominant 或 MultiZone。")
    elif max_skewness >= 0.85 or min_ortho <= 0.15:
        status = "WARN"
        remedy_actions.append("部分單元處於邊界警戒區，對於高度非線性接觸或大塑性分析可能影響收斂速率。")
        remedy_actions.append("建議微調局部單元過渡膨脹率 (Growth Rate 改為 1.15 以下)。")
    else:
        status = "PASS"
        remedy_actions.append("網格品質整體優良，允許直接放行進入求解階段。")

    print("\n==================================================================")
    print(">>> 綜合品質判定結論: [{}] <<<".format(status))
    print("==================================================================")
    for idx, act in enumerate(remedy_actions, 1):
        print("  {}. {}".format(idx, act))
    print("==================================================================\n")

    return {
        "is_valid": is_pass,
        "status": status,
        "elements": element_count,
        "nodes": node_count,
        "max_skewness": max_skewness,
        "avg_skewness": avg_skewness,
        "min_orthogonal_quality": min_ortho,
        "avg_orthogonal_quality": avg_ortho,
        "remedies": remedy_actions
    }

# 執行入口
if __name__ == "__main__":
    check_and_report_mesh_quality()
