# -*- coding: utf-8 -*-
"""
ACT Wizard (.wbex) 程式化操作腳本
無須 Wizard 原始碼，直接透過 ExtensionManager API 列舉、填寫與提交 ACT Wizard。
"""

def list_installed_wizards(ext_api):
    """
    列出當前環境中所有已載入外掛及其 Wizard 列表
    """
    ext_mgr = ext_api.ExtensionManager
    wizards_info = []
    
    for ext in ext_mgr.Extensions:
        print("Extension: {} | UniqueName: {}".format(ext.Name, ext.UniqueName))
        if hasattr(ext, "Wizards") and ext.Wizards:
            for w in ext.Wizards:
                print("  -> Wizard Name: {}".format(w.Name))
                wizards_info.append((ext.Name, w.Name))
    return wizards_info

def run_wizard_by_name(ext_api, wizard_name, property_updates=None):
    """
    依名稱開啟 Wizard、填寫參數並執行 Update 提交
    """
    ext_mgr = ext_api.ExtensionManager
    wizard = ext_mgr.GetWizardByName(wizard_name)
    
    if wizard is None:
        print("錯誤: 找不到名稱為 {} 的 ACT Wizard".format(wizard_name))
        return False

    # 1. 開啟 Wizard
    wizard.Open()
    
    # 2. 存取步驟 1 並設定屬性
    if len(wizard.Steps) > 0:
        step = wizard.Steps[0]
        if property_updates:
            for group_name, prop_name, val in property_updates:
                try:
                    step.Properties[group_name].Properties[prop_name].Value = val
                except Exception as e:
                    print("設定屬性 [{}][{}] 失敗: {}".format(group_name, prop_name, e))

        # 3. 程式化提交 (相當於在 GUI 按下 Update / Submit)
        step.Update()
        print("Wizard {} Step 1 已成功更新與提交！".format(wizard_name))
        return True
    return False

if __name__ == "__main__":
    print("ACT Wizard Automation 模組。")
