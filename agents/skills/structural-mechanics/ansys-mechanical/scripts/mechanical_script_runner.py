# -*- coding: utf-8 -*-
"""
ANSYS Mechanical ACT Scripting Foundation & Automation Runner.
"""
def execute_mechanical_automation():
    """
    Mechanical 自動化基礎樣板腳本。
    """
    try:
        model = ExtAPI.DataModel.Project.Model
        geometry = model.Geometry
        mesh = model.Mesh
        analyses = model.Analyses
        
        print("Mechanical 模型資訊:")
        print(" -> 幾何 Body 數量: {}".format(geometry.Children.Count))
        print(" -> 網格 Nodes 數量: {}".format(mesh.Nodes))
        print(" -> 分析系統 數量: {}".format(analyses.Count))
        return True
    except NameError:
        print("提示: 請在 ANSYS Mechanical ACT Scripting Console 或透過 PyMechanical run_python_script 執行此腳本。")
        return False

if __name__ == "__main__":
    execute_mechanical_automation()
