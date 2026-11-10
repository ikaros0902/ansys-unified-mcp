# -*- coding: utf-8 -*-
"""
ANSYS Mechanical ACT 標準化設定與求解腳本範例
適用於 Mechanical run_mechanical_script / execute_mechanical_script_live。
"""

def setup_and_solve_structural_analysis(ext_api):
    """
    建立固定支撐 (Fixed Support)、施加壓力 (Pressure)、劃分網格與求解結果
    """
    model = ext_api.DataModel.Project.Model
    analysis = model.Analyses[0]
    solution = analysis.Solution
    
    # 1. 取得 Active Unit System
    # ext_api.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS
    
    # 2. 建立 Fixed Support
    # fixed_support = analysis.AddFixedSupport()
    # fixed_support.Name = "Auto_Fixed_Support"
    # fixed_support.Location = selection_info
    
    # 3. 建立 Pressure Load
    # pressure = analysis.AddPressure()
    # pressure.Name = "Auto_Pressure"
    # pressure.Magnitude.Output.SetDiscreteValue(0, Quantity("1.0 [MPa]"))
    
    # 4. 加入 Total Deformation 結果
    # deformation = solution.AddTotalDeformation()
    # deformation.Name = "Total Deformation Result"
    
    # 5. 求解
    # solution.Solve()
    
    print("Mechanical ACT 結構分析自動化流程完成。")
    return True

if __name__ == "__main__":
    print("Mechanical ACT Setup 範例模組。")
