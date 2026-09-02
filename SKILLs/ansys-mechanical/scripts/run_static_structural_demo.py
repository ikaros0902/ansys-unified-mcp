# ==============================================================================
# 腳本名稱: run_static_structural_demo.py
# 功能描述: ANSYS Mechanical 標準靜態結構分析端到端自動化腳本（林明志標準）
# 涵蓋流程: 單位設定 -> 材料指派 -> 網格劃分與品質檢驗 -> 邊界載荷 -> 求解 -> 雲圖輸出
# 執行環境: ANSYS Mechanical ACT 腳本環境 / PyMechanical
# ==============================================================================

import os

def run_complete_static_structural_workflow(config=None):
    """
    執行端到端靜態結構自動化分析流程。
    
    :param config: 設定參數字典 (包含輸出目錄、載荷大小等)
    """
    if config is None:
        config = {
            "output_dir": "C:/Temp/Mechanical_Outputs",
            "element_size_m": 0.005,
            "force_y_n": -10000.0,
            "pressure_pa": 2000000.0,
            "image_width": 1920,
            "image_height": 1080
        }

    print("=========================================================")
    print("=== [步驟 1/7] 啟用標準單位系統與頂層物件句柄配置 ===")
    print("=========================================================")
    ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS
    model = DataModel.Project.Model
    mesh = model.Mesh
    
    # 獲取或建立靜態結構分析系統
    if len(model.Analyses) == 0:
        raise RuntimeError("模型中未發現任何分析系統，請先建立 Static Structural 分析系統。")
    analysis = model.Analyses[0]
    settings = analysis.Children[0]
    solution = analysis.Solution
    print("分析系統名稱: {}".format(analysis.Name))

    print("\n=========================================================")
    print("=== [步驟 2/7] 實體幾何材料指派與確認 ===")
    print("=========================================================")
    all_bodies = model.Geometry.GetChildren(
        Ansys.Mechanical.DataModel.Enums.DataModelObjectCategory.Body, True
    )
    print("模型共計檢測到 {} 個幾何主體 (Bodies)".format(len(all_bodies)))
    for body in all_bodies:
        # 指派預設結構鋼或現有工程材料
        if not body.Material:
            body.Material = "Structural Steel"
        print("主體 [{}] -> 材料: {}".format(body.Name, body.Material))

    print("\n=========================================================")
    print("=== [步驟 3/7] 網格劃分與前置品質強制檢驗 ===")
    print("=========================================================")
    mesh.Activate()
    mesh.ElementSize = Quantity("{} [m]".format(config["element_size_m"]))
    mesh.ElementOrder = Ansys.Mechanical.DataModel.Enums.ElementOrder.ProgramControlled
    print("正在執行全域網格劃分 (目標尺寸: {} m)...".format(config["element_size_m"]))
    mesh.GenerateMesh()
    print("網格劃分完成！單元總數: {}, 節點總數: {}".format(mesh.Elements, mesh.Nodes))

    # 強制檢驗網格品質 (遵循三大 Don'ts：未過檢禁求)
    stats = mesh.MeshStatistics
    max_skewness = stats.MaxSkewness
    min_ortho = stats.MinOrthogonalQuality
    print("網格品質指標: 最大歪斜度 = {:.4f} (門檻 < 0.85), 最小正交品質 = {:.4f} (門檻 > 0.15)".format(
        max_skewness, min_ortho
    ))

    if max_skewness > 0.95 or min_ortho < 0.05:
        raise ValueError("[致命錯誤] 網格品質極度劣質 (Skewness > 0.95 或 Ortho < 0.05)，強制終止求解！")
    elif max_skewness > 0.85 or min_ortho < 0.15:
        print("[警告] 網格品質處於警戒區，強烈建議局部細化網格以提高數值精度。")
    else:
        print("[驗證通過] 網格品質完全符合工程高精度求解標準。")

    print("\n=========================================================")
    print("=== [步驟 4/7] 裝配體接觸對配置與穩定化 ===")
    print("=========================================================")
    if len(model.Connections.Children) > 0:
        for conn_group in model.Connections.Children:
            for contact in conn_group.Children:
                if hasattr(contact, "ContactFormulation"):
                    # 採用增廣拉格朗日法
                    contact.ContactFormulation = Ansys.Mechanical.DataModel.Enums.ContactFormulation.AugmentedLagrange
                    contact.NormalStiffnessFactor = 0.1  # 提高柔度預防反彈震盪
                    contact.UpdateStiffness = Ansys.Mechanical.DataModel.Enums.UpdateContactStiffness.EachIteration
                    print("接觸對 [{}] 已配置增廣拉格朗日法與剛度動態更新。".format(contact.Name))

    print("\n=========================================================")
    print("=== [步驟 5/7] 邊界約束與工作載荷施加 (嚴防剛體位移) ===")
    print("=========================================================")
    # 檢查是否有預設的 Named Selection，若無則依面實體施加
    named_selections = model.NamedSelections.Children if hasattr(model, "NamedSelections") else []
    ns_dict = {ns.Name: ns for ns in named_selections}

    # 1. 施加固定約束
    fixed_support = analysis.AddFixedSupport()
    fixed_support.Name = "底面固定支撐"
    if "NS_FIXED_SUPPORT" in ns_dict:
        fixed_support.Location = ns_dict["NS_FIXED_SUPPORT"]
    else:
        # 自動取第一個主體的第一個面做示範約束
        sample_face = all_bodies[0].GetGeoBody().Faces[0]
        sel_info = ExtAPI.SelectionManager.CreateSelectionInfo(
            Ansys.ACT.Interfaces.Common.SelectionTypeEnum.GeometryEntities
        )
        sel_info.Entities = [sample_face]
        fixed_support.Location = sel_info
    print("已成功施加固定約束邊界條件。")

    # 2. 施加集中力分量
    force_load = analysis.AddForce()
    force_load.Name = "頂部受力"
    force_load.DefineBy = Ansys.Mechanical.DataModel.Enums.LoadDefineBy.Components
    force_load.XComponent.Output.SetDiscreteValue(0, Quantity("0 [N]"))
    force_load.YComponent.Output.SetDiscreteValue(0, Quantity("{} [N]".format(config["force_y_n"])))
    force_load.ZComponent.Output.SetDiscreteValue(0, Quantity("0 [N]"))
    if "NS_LOAD_FACES" in ns_dict:
        force_load.Location = ns_dict["NS_LOAD_FACES"]
    else:
        sample_face_2 = all_bodies[0].GetGeoBody().Faces[-1]
        sel_info_2 = ExtAPI.SelectionManager.CreateSelectionInfo(
            Ansys.ACT.Interfaces.Common.SelectionTypeEnum.GeometryEntities
        )
        sel_info_2.Entities = [sample_face_2]
        force_load.Location = sel_info_2
    print("已成功施加垂直向量外力載荷: {} N".format(config["force_y_n"]))

    print("\n=========================================================")
    print("=== [步驟 6/7] 求解器參數配置與啟動求解 ===")
    print("=========================================================")
    settings.LargeDeflection = True  # 開啟大變形
    settings.AutomaticTimeStepping = Ansys.Mechanical.DataModel.Enums.AutomaticTimeStepping.On
    settings.InitialSubsteps = 10
    settings.MinimumSubsteps = 5
    settings.MaximumSubsteps = 100
    settings.NewtonRaphsonType = Ansys.Mechanical.DataModel.Enums.NewtonRaphsonType.Full
    settings.LineSearch = Ansys.Mechanical.DataModel.Enums.LineSearchType.On

    print("啟動非線性結構求解運算 (同步等待)...")
    analysis.Solve(True)
    print("求解完成！求解狀態: {}".format(solution.Status))

    print("\n=========================================================")
    print("=== [步驟 7/7] 結果物件計算、數值提取與白底雲圖輸出 ===")
    print("=========================================================")
    # 新增結果物件
    total_disp = solution.AddTotalDeformation()
    total_disp.Name = "總變形量"
    
    von_mises = solution.AddEquivalentStress()
    von_mises.Name = "Von-Mises等效應力"

    solution.EvaluateAllResults()

    print("---------------------------------------------------------")
    print(">>> 求解數值結果摘要 <<<")
    print("最大總變形量: {} {}".format(total_disp.Maximum.Value, total_disp.Maximum.Unit))
    print("最高等效應力: {:.2f} MPa".format(von_mises.Maximum.Value / 1e6))
    print("---------------------------------------------------------")

    # 批次輸出白底 PNG 雲圖
    out_dir = config["output_dir"]
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    img_settings = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
    img_settings.Resolution = GraphicsResolutionType.NormalResolution
    img_settings.Background = GraphicsBackgroundType.White
    img_settings.Width = config["image_width"]
    img_settings.Height = config["image_height"]

    for res in [total_disp, von_mises]:
        try:
            res.Activate()
            Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Iso)
            Graphics.Camera.SetFit()
            clean_name = res.Name.replace(" ", "_")
            save_path = os.path.join(out_dir, "{}.png".format(clean_name))
            Graphics.ExportImage(save_path, GraphicsImageExportFormat.PNG, img_settings)
            print("成功導出雲圖: {}".format(save_path))
        except Exception as e:
            print("導出雲圖失敗 [{}]: {}".format(res.Name, str(e)))

    print("\n=== 全流程標準靜態結構分析作業圓滿完成！===")

# 執行入口
if __name__ == "__main__":
    run_complete_static_structural_workflow()
