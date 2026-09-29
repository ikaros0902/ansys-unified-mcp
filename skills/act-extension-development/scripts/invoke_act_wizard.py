# -*- coding: utf-8 -*-
"""
ACT Wizard Programmatic Invocation Script.
"""
def invoke_wizard_step(wizard_name="MECH_AutoMesh", step_index=0, properties=None):
    """
    透過 ExtAPI.ExtensionManager 程式化呼叫已安裝的 ACT Wizard 外掛 (.wbex)。
    """
    try:
        ext_mgr = ExtAPI.ExtensionManager
        wizard = ext_mgr.GetWizardByName(wizard_name)
        if wizard is None:
            print("未找到指定名稱的 Wizard 外掛: {}".format(wizard_name))
            return False
        
        wizard.Open()
        step = wizard.Steps[step_index]
        if properties:
            for group_name, prop_dict in properties.items():
                for prop_key, prop_val in prop_dict.items():
                    step.Properties[group_name].Properties[prop_key].Value = prop_val
        step.Update()  # 等同於按下 Submit 按鈕
        print("成功程式化執行 Wizard: {}".format(wizard_name))
        return True
    except Exception as e:
        print("執行 ACT Wizard 發生異常: {}".format(e))
        return False

if __name__ == "__main__":
    invoke_wizard_step()
