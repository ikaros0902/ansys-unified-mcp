# 具名選擇 (Named Selection) 自動標記與幾何拓撲過濾專精手冊 (Named Selections Reference)

在現代 CAE 自動化管線中，**嚴禁在網格生成後依賴臨時面 ID (Face ID) 施加邊界條件**。網格剖分過程會重構拓撲幾何，導致幾何面 ID 重新隨機洗牌。唯一穩健可靠的標準方案是在 **CAD/幾何前處理階段即完成具名選擇 (Named Selection) 的標記**。

---

## 一、具名選擇命名規範與物理語義標準

為確保下游 Fluent Meshing、PyPrimeMesh 與 Mechanical 求解器能全自動識別並對應邊界條件類型，Named Selection 應採用統一的工業規範：

| 邊界類型 | 建議 Named Selection 名稱 | 下游求解器自動映射機制 |
|---|---|---|
| **流體入口** | `INLET` / `VELOCITY_INLET` | 自動辨識為 Velocity Inlet / Mass Flow Inlet |
| **流體出口** | `OUTLET` / `PRESSURE_OUTLET` | 自動辨識為 Pressure Outlet |
| **對稱面** | `SYMMETRY` / `SYM_XZ` | 自動辨識為 Symmetry 零法向梯度邊界 |
| **遠場壁面** | `FARFIELD_WALLS` / `SLIP_WALLS` | 自動指定為 Specified Shear 或 Slip Wall |
| **固體表面** | `SOLID_WALL` / `AIRFOIL_SURFACE` | 自動生成邊界層 (Inflation Layers) 與無滑移條件 |
| **流體體域** | `FLUID_DOMAIN` / `FLUID_AIR` | 自動指定為 Fluid Cell Zone (流體連續相) |
| **固體體域** | `SOLID_CHIP` / `SOLID_FIN` | 自動指定為 Solid Cell Zone (共軛導熱相) |

---

## 二、幾何拓撲特徵自動過濾演算法

在大量批次與全無人化流程中，幾何面無法透過人工點選。本手冊定義基於**空間包圍盒坐標**與**面法向量**的高精度特徵篩選演算法。

### 1. 外包圍盒極值座標過濾法
透過流體域的總體 Bounding Box，提取邊界面幾何中心 (Face Center) 的空間極值：
- $C_x \approx X_{\min} \implies$ **INLET**
- $C_x \approx X_{\max} \implies$ **OUTLET**
- $C_z \approx Z_{\min} \implies$ **GROUND / SYMMETRY**
- $C_z \approx Z_{\max} \implies$ **TOP_WALL**

### 2. 演算法實作 (PyAnsys Geometry)
```python
from ansys.geometry.core.designer import Design

def auto_tag_cfd_boundaries(design: Design, fluid_body, tol: float = 1e-4):
    """
    自動識別流體域外邊界面並建立標準 Named Selections
    """
    bbox = fluid_body.bounding_box
    min_x, max_x = bbox.min_point.x, bbox.max_point.x
    min_y, max_y = bbox.min_point.y, bbox.max_point.y
    min_z, max_z = bbox.min_point.z, bbox.max_point.z

    inlets, outlets, symmetry, walls, internal_cavity = [], [], [], [], []

    for face in fluid_body.faces:
        center = face.box.center
        
        # 1. 判斷上游入口
        if abs(center.x - min_x) < tol:
            inlets.append(face)
        # 2. 判斷下游出口
        elif abs(center.x - max_x) < tol:
            outlets.append(face)
        # 3. 判斷底面對稱面
        elif abs(center.z - min_z) < tol:
            symmetry.append(face)
        # 4. 判斷側壁與頂部外圍邊界
        elif (abs(center.y - min_y) < tol or 
              abs(center.y - max_y) < tol or 
              abs(center.z - max_z) < tol):
            walls.append(face)
        # 5. 其餘面均為布林扣除後形成的物體內部表面
        else:
            internal_cavity.append(face)

    # 建立面具名選擇
    ns_map = {}
    if inlets:
        ns_map["INLET"] = design.create_named_selection("INLET", faces=inlets)
    if outlets:
        ns_map["OUTLET"] = design.create_named_selection("OUTLET", faces=outlets)
    if symmetry:
        ns_map["SYMMETRY"] = design.create_named_selection("SYMMETRY", faces=symmetry)
    if walls:
        ns_map["FARFIELD_WALLS"] = design.create_named_selection("FARFIELD_WALLS", faces=walls)
    if internal_cavity:
        ns_map["OBJECT_WALL"] = design.create_named_selection("OBJECT_WALL", faces=internal_cavity)

    # 建立實體體域具名選擇 (Body Named Selection)
    ns_map["FLUID_DOMAIN"] = design.create_named_selection("FLUID_DOMAIN", bodies=[fluid_body])
    
    return ns_map
```

---

## 三、SpaceClaim 原生 IronPython 具名選擇實作

```python
# ==============================================================================
# SpaceClaim Native Script (IronPython) - 自動分組具名選擇
# ==============================================================================
root_part = GetRootPart()
fluid_body = root_part.Bodies[0]

inlet_faces = []
outlet_faces = []

# 遍歷體之所有幾何面
for face in fluid_body.Faces:
    center = face.Shape.Box.Center
    if center.X < -0.59: # 依據工程座標設定門檻
        inlet_faces.append(face)
    elif center.X > 1.79:
        outlet_faces.append(face)

# 建立 Face Named Selection
if len(inlet_faces) > 0:
    sel = Selection.Create(inlet_faces)
    NamedSelection.Create(sel, Selection.Empty()).CreatedNamedSelection.Name = "INLET"

if len(outlet_faces) > 0:
    sel = Selection.Create(outlet_faces)
    NamedSelection.Create(sel, Selection.Empty()).CreatedNamedSelection.Name = "OUTLET"

# 建立 Body Named Selection
body_sel = Selection.Create(fluid_body)
NamedSelection.Create(body_sel, Selection.Empty()).CreatedNamedSelection.Name = "FLUID_DOMAIN"
```

---

## 四、完備性核驗準則 (Completeness Check)

在導出 PMDB 幾何前，必須進行具名選擇完備性稽核：
1. **面覆蓋率稽核 (Face Coverage Audit)**：確認外包圍盒 6 個宏觀邊界中，每一個面都已經被指派至專屬 Named Selection，無任何孤立無標籤外表面。
2. **重疊禁止 (No Intersection Overlap)**：確認同一幾何面未被重複加入互斥的邊界群組中（例如同一個面不可同時既是 `INLET` 又是 `WALL`）。
3. **體域標記完備性**：所有參與分析的實體（包括流體域和固體零件），均必須具有對應的 Body Named Selection，以利網格劃分自動分群。
