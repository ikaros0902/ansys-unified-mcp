# -*- coding: utf-8 -*-
"""
LS-DYNA Mesh Criteria & Keyword Generation Helper Script.
"""
def apply_lsdyna_mesh_criteria():
    """
    定義與套用 LS-DYNA 網格品質標準（Warpage, Aspect Ratio, Skew, Jacobian, Time Step）。
    """
    shell_criterion = {
        "Mesh_Range_Max": 2.0,
        "Mesh_Range_Min": 0.5,
        "Edge_Length": 0.5,
        "Warpage": 20.0,
        "Aspect_Ratio": 5.0,
        "Skew": 45.0,
        "Jacobian": 0.65,
        "Time_Step": 5e-8
    }
    solid_criterion = {
        "Mesh_Range_Max": 3.0,
        "Mesh_Range_Min": 1.0,
        "Edge_Length": 0.5,
        "Warpage": 20.0,
        "Aspect_Ratio": 5.0,
        "Skew": 45.0,
        "Jacobian": 0.65,
        "Time_Step": 5e-8
    }
    print("LS-DYNA 網格品質驗收標準套用完成:")
    print("Shell 網格標準: {}".format(shell_criterion))
    print("Solid 網格標準: {}".format(solid_criterion))
    return shell_criterion, solid_criterion

if __name__ == "__main__":
    apply_lsdyna_mesh_criteria()
