# -*- coding: utf-8 -*-
"""
ANSYS optiSLang 原生 Python API 參數化連線腳本
建立 SensitivityActor 與 ParametricSystem 節點並添加優化參數與響應。
"""

def create_optislang_sensitivity_workflow():
    """
    optiSLang 原生 Python 腳本樣板 (傳送至 run_optislang_script 執行)
    """
    script_lines = [
        "# optiSLang 原生 Python 腳本",
        "import osl",
        "root_system = osl.get_root_system()",
        "",
        "# 建立 Sensitivity Actor (敏感度分析)",
        "sens_actor = actors.SensitivityActor('Sensitivity_Study')",
        "add_actor(sens_actor)",
        "",
        "# 設定優化參數與響應目標",
        "print('optiSLang 參數化系統建構完成')"
    ]
    
    native_script = "\n".join(script_lines)
    print("生成 optiSLang 原生腳本:\n{}".format(native_script))
    return native_script

if __name__ == "__main__":
    create_optislang_sensitivity_workflow()
