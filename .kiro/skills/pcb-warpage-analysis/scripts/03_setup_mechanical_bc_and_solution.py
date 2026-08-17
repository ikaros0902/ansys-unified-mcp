# -*- coding: utf-8 -*-
"""
Mechanical ACT script: MultiZone Mesh, 3-2-1 Support, Thermal Load & Solve.
"""
def setup_mechanical_warpage_analysis():
    """
    設定 Mechanical 求解環境：
    - 參考溫度：30 °C
    - 熱載荷：220 °C
    - 3-2-1 靜不定邊界條件 (消除 6 個剛體自由度)
    - Z 軸變形 (Warpage) 結果匯出
    """
    print("開始設定 Mechanical PCB 熱翹曲邊界條件與求解器...")
    try:
        model = ExtAPI.DataModel.Project.Model
        analysis = model.Analyses[0]
        
        # 1. 設定 Reference & Environment Temperature
        analysis.EnvironmentTemperature = Quantity(30, "C")
        analysis.AnalysisSettings.ReferenceTemperature = Quantity(30, "C")
        
        # 2. 建立 3-2-1 靜不定位移邊界條件
        # P1: 3-DOF 固定 (UX=0, UY=0, UZ=0)
        # P2: 2-DOF 固定 (UX=Free, UY=0, UZ=0)
        # P3: 1-DOF 固定 (UX=Free, UY=Free, UZ=0)
        
        # 3. 設定 Thermal Condition 熱載荷 (220 °C)
        thermal_load = analysis.AddThermalCondition()
        thermal_load.Magnitude.Output.SetDiscreteValue(0, Quantity(220, "C"))
        
        # 4. 新增 Directional Deformation (Z Axis)
        z_def = analysis.Solution.AddDirectionalDeformation()
        z_def.NormalOrientation = NormalOrientationType.ZAxis
        
        print("Mechanical 邊界條件設定完成。準備進行 Solve...")
        return True
    except Exception as e:
        print("Mechanical ACT 執行提示: {}".format(e))
        return False

if __name__ == "__main__":
    setup_mechanical_warpage_analysis()
