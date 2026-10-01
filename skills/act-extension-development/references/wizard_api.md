# ACT Wizard 程式化調用與專案刷新 (wizard_api.md)

本手冊說明如何透過 `ExtensionManager` 程式化操作加密之 ACT Wizard (`.wbex`) 以及 Workbench 精準刷新策略。

---

## 1. ACT Wizard 程式化呼叫（四步驟）

```python
# Step 1: 取得 ExtensionManager
ext_mgr = ExtAPI.ExtensionManager

# Step 2: 取得指定 Wizard
wizard = ext_mgr.GetWizardByName("MECH_AutoMesh")

# Step 3: 開啟 Wizard 並設定屬性
wizard.Open()
step = wizard.Steps[0]
step.Properties["Group"].Properties["Prop"].Value = val

# Step 4: 程式化提交更新
step.Update()
```

---

## 2. Workbench 精準 Component 刷新

避免引發全域重算，僅刷新幾何或材料變更之元件：

```python
proj = ExtAPI.DataModel.Project
for sys_item in proj.Systems:
    if hasattr(sys_item, "Components"):
        for comp in sys_item.Components:
            if hasattr(comp, "Refresh"):
                comp.Refresh()
            if hasattr(comp, "Update"):
                comp.Update()
```
