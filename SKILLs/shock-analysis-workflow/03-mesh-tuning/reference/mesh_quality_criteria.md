# Mesh Quality Criteria & Interference Diagnostic Scripts

本手冊為 Session 03: 網格優先級、干涉預檢與顯式時間步長調校之底層腳本、LS-DYNA 關鍵字卡片與 CFL 判據速查表。

---

### 2.1 CAD 實體干涉檢查 (`MECH_Interference_Check.py`)
透過 Mechanical Diagnostics Criteria 檢測零件間重疊體積：
```python
def check_cad_interference(model):
    ns_name = "Interference_Check_Results"
    for ns_old in list(model.NamedSelections.Children):
        if ns_old.Name == ns_name:
            ns_old.Delete()

    ns = model.AddNamedSelection()
    ns.Name = ns_name
    ns.ScopingMethod = GeometryDefineByType.Worksheet
    
    # 建立幾何體積大於 0 之重疊診斷條件
    crit0 = ns.GenerationCriteria.Add(None)
    crit0.EntityType = SelectionType.GeoBody
    crit0.Criterion = SelectionCriterionType.Size
    crit0.Operator = SelectionOperatorType.GreaterThan
    crit0.Value = Quantity("0 [mm mm mm]")
    
    crit1 = ns.GenerationCriteria.Add(None)
    crit1.Action = SelectionActionType.Diagnostics
    ns.Generate()
```

### 2.2 網格初始穿透檢查與 LS-DYNA 控制卡修正
- **問題現象**：若網格表面在初始狀態存在幾何穿透，LS-DYNA 顯式求解器會在第 1 個 cycle 產生極大的排斥力，導致單元扭曲負體積（Negative Volume）。
- **關鍵字防護**：在 `*CONTROL_CONTACT` 中設定 `IGNORE=1` 或 `IGNORE=2`，於 $t=0$ 自動將穿透節點投射回主接觸面：
```
*CONTROL_CONTACT
$#  slsfac    rwpnal    islchk    shlthk    penopt    thkchg     orien    enmass
     0.100     0.000         1         2         1         0         1         0
$#  usrstf    usrstr    sfric     dfric     edc       vfc       th        th_sf
     0.000     0.000     0.000     0.000     0.000     0.000     0.000     0.000
$#  ignore    bktchg    pastop    
         1         0         0
```

---


---

## 4. 顯式時間步長控制準則 ($\Delta t \ge 2.0 \times 10^{-8}\text{ s}$)

顯式動力學中，Courant-Friedrichs-Lewy (CFL) 穩定性條件要求時間步長滿足：
$$\Delta t \le \frac{L}{c}, \quad c = \sqrt{\frac{E}{\rho}}$$

| 材料名稱 | 彈性模數 $E\text{ (GPa)}$ | 密度 $\rho\text{ (kg/m}^3\text{)}$ | 聲速 $c\text{ (m/s)}$ | 臨界最小尺寸 $L_{\min}\text{ (mm) for }\Delta t=20\text{ ns}$ | 建議網格尺寸 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **結構鋼 (Structural Steel / SGCC)** | 200.0 | 7850 | 5047.5 | 0.101 mm | 1.5 ~ 3.0 mm |
| **鋁合金 (AL6061-T6)** | 68.9 | 2700 | 5051.6 | 0.101 mm | 1.5 ~ 3.0 mm |
| **工程塑膠 (PC+ABS / PA66)** | 2.4 | 1200 | 1414.2 | 0.028 mm | 1.0 ~ 2.0 mm |
| **FR-4 電路板** | 22.0 | 1900 | 3402.8 | 0.068 mm | 1.0 ~ 2.0 mm |

---
