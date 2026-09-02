# 3D 特徵成形技術專精手冊 (3D Features Reference)

本手冊規範從 2D 草圖輪廓躍遷至 3D 幾何實體的四種核心成形工藝：拉伸 (Extrude)、旋轉 (Revolve)、掃掠 (Sweep) 與混成 (Blend/Loft)，涵蓋 PyAnsys Geometry 與 SpaceClaim 原生 IronPython 雙軌 API。

---

## 一、四大 3D 成形特徵原理與選型準則

| 特徵操作 | 幾何輸入要件 | 適用工程結構 | 核心拓撲陷阱 |
|---|---|---|---|
| **拉伸 (Extrude)** | 2D 閉合草圖 + 投影法向/距離 | 機翼、散熱鰭片、結構樑、外流域外框 | 拔模角過大造成自交、草圖未完全封閉 |
| **旋轉 (Revolve)** | 2D 閉合草圖 + 旋轉中心軸 + 角度 | 噴嘴、轉子軸件、圓柱形壓力容器、輪轂 | 旋轉軸穿透草圖內部、草圖跨越軸線重疊 |
| **掃掠 (Sweep)** | 剖面草圖 (Profile) + 導引路徑 (Path) | 彎管、冷卻流道、螺旋線圈、排氣歧管 | 路徑曲率半徑小於截面特徵尺寸導致自相交 |
| **混成 (Blend/Loft)** | 兩個或多個斷面草圖 + 導引脊線 | 變截面葉片、機身漸縮段、異形轉接管 | 各截面節點數/方向不匹配造成扭轉或拓撲畸變 |

---

## 二、拉伸特徵 (Extrude) 實作

### 1. PyAnsys Geometry 模式
```python
from ansys.geometry.core.math import Point2D, Plane
from ansys.geometry.core.sketch import Sketch

def create_extruded_block(design, width=0.1, height=0.05, depth=0.3):
    """
    繪製矩形草圖並沿著法向拉伸成 3D 實體
    """
    sketch = Sketch(plane=Plane.xy())
    sketch.box(Point2D([0.0, 0.0]), width=width, height=height)
    
    # 執行拉伸特徵
    body = design.extrude_sketch(
        name="ExtrudedStructuralBody",
        sketch=sketch,
        distance=depth
    )
    return body
```

### 2. SpaceClaim 原生腳本 (IronPython)
```python
# 啟用實體模式並拉伸表面
result = ViewHelper.SetViewMode(InteractionMode.Solid)
face = result.CreatedBodies[0].Faces[0]
options = ExtrudeFaceOptions()
# 拉伸 50mm
ExtrudeFaces.Execute(face, MM(50), options)
```

---

## 三、旋轉特徵 (Revolve) 實作

旋轉特徵用於建立軸對稱或部分迴轉幾何體（如超音速拉伐爾噴管、迴轉體翼身）。

### 1. PyAnsys Geometry 模式
```python
from ansys.geometry.core.math import Point2D, Point3D, Vector3D, Plane
from ansys.geometry.core.sketch import Sketch

def create_revolved_vessel(design, r_inner=0.05, thickness=0.005, height=0.2):
    """
    在 XZ 平面繪製壓力容器半剖面壁厚並繞 Z 軸旋轉成形
    """
    sketch = Sketch(plane=Plane.xz())
    r_outer = r_inner + thickness
    
    # 定義半剖面四個角點
    p1 = Point2D([r_inner, 0.0])
    p2 = Point2D([r_outer, 0.0])
    p3 = Point2D([r_outer, height])
    p4 = Point2D([r_inner, height])
    
    sketch.segment(p1, p2)
    sketch.segment(p2, p3)
    sketch.segment(p3, p4)
    sketch.segment(p4, p1)
    
    # 繞 Z 軸旋轉 360 度
    revolved_body = design.revolve_sketch(
        name="PressureVessel",
        sketch=sketch,
        axis=Vector3D([0.0, 0.0, 1.0]),
        angle=360.0,
        rotation_origin=Point3D([0.0, 0.0, 0.0])
    )
    return revolved_body
```

### 2. SpaceClaim 原生腳本 (IronPython)
```python
# 選取面與旋轉軸並執行旋轉
selection = FaceSelection.Create(face)
axis_selection = LineSelection.Create(axis_line)
options = RevolveFaceOptions()
RevolveFaces.Execute(selection, axis_selection, DEG(360), options)
```

---

## 四、掃掠 (Sweep) 與混成 (Blend/Loft) 規範

### 1. 掃掠路徑正交與曲率安全法則
- **正交性起始**：掃掠截面法向在起點處必須嚴格平行於導引路徑在該點的切線向量（$\vec{N}_{\text{profile}} \parallel \vec{T}_{\text{path}}$）。
- **曲率半徑限制**：導引路徑的最小曲率半徑 $R_{\min}$ 必須大於截面輪廓的最大外接半徑 $r_{\max}$（即 $R_{\min} > 1.2 \times r_{\max}$），否則彎角內側將產生自相交退化面 (Self-Intersecting Face)。

### 2. 混成截面拓撲同構要求
- 多截面混成時，各截面圖元的頂點數量與連接方向（順時針/逆時針）應保持一致，避免混成後實體表面出現局部扭絞畸變。

---

## 五、成形後實體拓撲健康性檢驗

特徵生成完成後，必須立即驗證實體拓撲完整性：
1. **有效體積檢驗**：實體體積必須為嚴格正值（$V > 0$），防止產生零厚度面 (Zero-thickness) 或虛假空心殼體。
2. **表面封閉性**：實體邊界表示法 (B-Rep) 必須為完全水密流形 (Watertight Manifold)，無開放邊界 (Open Free Edges)。
3. **特徵名唯一性**：為便於下游樹狀目錄追蹤，每個成形 Body 必須被賦予具備物理語義之唯一名稱（如 `Wing_Solid`, `Nozzle_Casing`）。
