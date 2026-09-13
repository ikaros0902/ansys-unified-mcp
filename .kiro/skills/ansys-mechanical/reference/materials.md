# ANSYS Mechanical 材料管理與 EngineeringData 操作指南

本手冊提供 ANSYS Mechanical 環境下材料庫 XML（MatML）匯入、EngineeringData 屬性查詢、主體（Body）批次材料指派以及溫度相關（Temperature-Dependent）非線性材料處理之標準 ACT 程式碼規範。

---

## 一、EngineeringData XML (MatML) 匯入

在 ANSYS Mechanical 中，可直接透過 `Model.Materials.Import()` 載入 MatML 格式之材料資料庫檔案（包含等向性彈性、雙線性等向強化、隨溫度變化的導熱係數與熱膨脹係數）：

```python
import os

def import_material_library(xml_path):
    """
    匯入 EngineeringData MatML XML 材料庫。
    
    :param xml_path: XML 檔案絕對路徑 (如 'C:/Materials/ThermalStructural_MatML.xml')
    """
    if not os.path.exists(xml_path):
        raise FileNotFoundError("找不到指定的材料庫檔案: {}".format(xml_path))
    
    # 匯入 XML 材料庫至 Mechanical 模型
    Model.Materials.Import(xml_path)
    print("成功匯入材料庫: {}".format(xml_path))
    
    # 遍歷並輸出當前模型載入之材料名稱
    materials = [mat.Name for mat in Model.Materials.Children]
    print("已載入之材料清單 (共 {} 種):".format(len(materials)))
    for name in materials:
        print("  - {}".format(name))
    return materials
```

---

## 二、主體 (Body) 材料指定與自動化規則映射

### 1. 單一主體材料直接指派
每個幾何主體物件具備 `.Material` 屬性，可直接傳入材料名稱字串進行賦予：

```python
# 取得第一個幾何主體並指定材料
body = Model.Geometry.Children[0].Children[0]
body.Material = "Structural Steel"
```

### 2. 依名稱關鍵字批次規則對應指派
在大型裝配體中，建議定義規則字典，自動走訪所有主體並依名稱關鍵字指派對應材料：

```python
def assign_materials_by_rules(assignment_rules):
    """
    依零件名稱特徵關鍵字自動指派對應材料。
    
    :param assignment_rules: 字典，格式為 {"關鍵字": "材料名稱"}
    """
    all_bodies = Model.Geometry.GetChildren(
        Ansys.Mechanical.DataModel.Enums.DataModelObjectCategory.Body, True
    )
    
    assigned_count = 0
    for body in all_bodies:
        matched = False
        for keyword, mat_name in assignment_rules.items():
            if keyword.lower() in body.Name.lower():
                body.Material = mat_name
                print("主體 [{}] 成功指定材料 -> {}".format(body.Name, mat_name))
                assigned_count += 1
                matched = True
                break
        if not matched:
            print("提示: 主體 [{}] 未匹配到規則，保留現有材料 ({})".format(body.Name, body.Material))
            
    print("材料指派完成，共指派 {} 個實體。".format(assigned_count))

# 調用範例：
# rules = {
#     "Bracket": "Structural Steel",
#     "Shaft": "Titanium Alloy",
#     "Bushing": "Copper Alloy",
#     "Housing": "Aluminum Alloy"
# }
# assign_materials_by_rules(rules)
```

---

## 三、MaterialAssignment 物件與幾何選取集綁定

對於 ACT 擴充套件或腳本自動化，亦可透過 `MaterialAssignment` 物件將材料指派至具名選取集（Named Selection）或 `SelectionInfo`：

```python
# 透過 Materials 容器新增指派物件
mat_folder = ExtAPI.DataModel.GetObjectsByType(Ansys.ACT.Automation.Mechanical.Materials)[0]
assignment = mat_folder.AddMaterialAssignment()
assignment.Material = "Aluminum Alloy"

# 綁定至 Named Selection
named_selection = ExtAPI.DataModel.GetObjectsByName("NS_ALUMINUM_PARTS")[0]
assignment.Location = named_selection
```

---

## 四、溫度相依 (Temperature-Dependent) 與非線性材料處理

進行熱-結構耦合分析時，材料屬性（如彈性模數 $E(T)$、熱膨脹係數 $\alpha(T)$、導熱係數 $k(T)$）往往隨溫度劇烈非線性變化。

### 1. 溫變熱膨脹係數 (Secant CTE vs Instantaneous CTE)
- **割線熱膨脹係數 (Secant CTE)**：ANSYS 預設使用割線 CTE，其計算基準為參考溫度 $T_{\text{ref}}$：
  $$\epsilon_{\text{thermal}} = \alpha_{\text{secant}}(T) \cdot (T - T_{\text{ref}})$$
- **基準參考溫度設定**：在 EngineeringData 定義割線熱膨脹係數時，務必確保材料庫定義的 Reference Temperature（如 20°C）與結構分析環境的 `Environment Temperature` 完全一致，否則會在初態產生虛假初始熱應力。

### 2. 雙線性彈塑性材料 (Bilinear Isotropic Hardening, BISO)
金屬結構進入降伏後，需於 XML 材料庫中包含下列非線性參數：
- **Yield Strength (降伏強度 $\sigma_y$)**
- **Tangent Modulus (正切模數 $E_t$)**：建議值一般為彈性模數的 $1\% \sim 5\%$，嚴禁設為 0 以防數值剛度矩陣奇異（若需理想彈塑性，建議設定極小正斜率，如 $10 \sim 100 \text{ MPa}$）。

---

## 五、MCP 工具整合對照

| ACT 原生 API | ANSYS MCP 工具 | 用途描述 |
|---|---|---|
| `Model.Materials.Children` | `list_materials` | 列出專案載入的所有材料清單 |
| `body.Material = "..."` | `assign_material(body_name, material_name)` | 直接將材料指定給特定幾何主體 |
| `Model.Materials.Import(path)` | `run_mechanical_script` | 透過腳本直接導入外部 MatML XML 檔案 |
