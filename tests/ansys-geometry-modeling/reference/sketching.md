# 2D 參數化草圖與曲線造型專精手冊 (Sketching Reference)

本手冊提供 ANSYS SpaceClaim (SCDM) 與 PyAnsys Geometry (`ansys.geometry.core`) 在 2D 參數化草圖繪製、幾何圖元約束、點陣列 NURBS 樣條曲線插值及閉合性驗證的技術規範。

---

## 一、基準面 (Plane) 定義與坐標系設置

在進行任何 2D 草圖繪製前，必須先錨定基準平面。草圖坐標系決定了後續拉伸、旋轉等 3D 成形特徵的法向與方向。

### 1. 空間標準基準面
- **XY 平面**：`Plane.xy()`，法向為 $+Z$，常用於底座、水平截面或俯視輪廓。
- **XZ 平面**：`Plane.xz()`，法向為 $+Y$，常用於對稱軸迴轉體（如噴嘴、軸件）之縱剖面。
- **YZ 平面**：`Plane.yz()`，法向為 $+X$，常用於側向導流截面。

### 2. 空間任意傾斜與偏移基準面
若需在物體表面或特定空間位置建構草圖，可透過自訂基準面原點與局部坐標軸向量：
```python
from ansys.geometry.core.math import Point3D, UnitVector3D, Plane

# 定義原點在 (0, 0, 0.15) 且法向為傾斜 45 度的基準面
custom_plane = Plane(
    origin=Point3D([0.0, 0.0, 0.15]),
    direction_x=UnitVector3D([1.0, 0.0, 0.0]),
    direction_y=UnitVector3D([0.0, 0.707106, 0.707106])
)
```

---

## 二、基礎幾何圖元繪製與尺寸約束

草圖圖元均以公尺 (m) 為法定標準單位。繪製複雜輪廓時，必須確保線段相鄰端點坐標連續性。

### 1. 直線與連續多段線 (Segment)
```python
from ansys.geometry.core.math import Point2D
from ansys.geometry.core.sketch import Sketch

sketch = Sketch(plane=Plane.xy())

# 定義外圍頂點 (寬 0.2m, 高 0.1m)
p1 = Point2D([0.0, 0.0])
p2 = Point2D([0.2, 0.0])
p3 = Point2D([0.2, 0.1])
p4 = Point2D([0.0, 0.1])

# 繪製封閉多段線
sketch.segment(p1, p2)
sketch.segment(p2, p3)
sketch.segment(p3, p4)
sketch.segment(p4, p1)  # 閉合回起點
```

### 2. 圓弧與圓 (Arc & Circle)
- **三點定弧**：`sketch.arc_from_three_points(start_pt, end_pt, pass_pt)`
- **圓心與半徑**：`sketch.circle(center_pt, radius)`
- **起點、圓心與夾角**：適用於精確倒角與流體過渡彎角。

---

## 三、點陣列平滑 NURBS 樣條曲線 (Spline) 插值

在氣動翼型 (Airfoil)、渦輪葉片 (Turbine Blade) 或流體漸縮噴管中，外形輪廓通常由離散坐標數據表定義。必須透過高階 NURBS 樣條實現 $C^2$ 平滑連續插值。

### 1. 樣條曲線生成演算法
```python
from ansys.geometry.core.math import Point2D
from ansys.geometry.core.sketch import Sketch

def build_nurbs_airfoil(sketch: Sketch, chord_len: float = 0.3):
    """
    依據歸一化座標生成封閉 NURBS 翼型草圖
    """
    # 典型對稱翼型上表面與下表面無量綱點陣列
    raw_coords = [
        (1.000, 0.0013), (0.950, 0.0084), (0.800, 0.0262),
        (0.600, 0.0456), (0.400, 0.0580), (0.200, 0.0574),
        (0.100, 0.0468), (0.050, 0.0356), (0.000, 0.0000),
        (0.050, -0.0356), (0.100, -0.0468), (0.200, -0.0574),
        (0.400, -0.0580), (0.600, -0.0456), (0.800, -0.0262),
        (0.950, -0.0084), (1.000, -0.0013)
    ]
    
    # 尺寸實體化 (轉換為公尺 m)
    spline_points = [Point2D([x * chord_len, y * chord_len]) for x, y in raw_coords]
    
    # 呼叫 NURBS 樣條曲線插值
    sketch.nurbs_from_2d_points(spline_points, tag="AirfoilProfile")
    
    # 後緣平直閉合線段 (確保輪廓形成閉合環 Loop)
    sketch.segment(spline_points[-1], spline_points[0])
    return sketch
```

---

## 四、SpaceClaim 原生 IronPython 草圖實作

在 SpaceClaim 內建腳本編輯器或 ACT 環境中，草圖繪製依賴 `ViewHelper` 與原生幾何工廠 API：

```python
# ==============================================================================
# SpaceClaim Native Script (IronPython) - 參數化草圖
# ==============================================================================
# 設定長度單位為公釐 (mm)
GetRootPart().LengthUnit = LengthUnits.Millimeter

# 1. 設置草圖基準面
ViewHelper.SetSketchPlane(Plane.PlaneXY)

# 2. 定義點並繪製線段
p1 = Point2D.Create(MM(0), MM(0))
p2 = Point2D.Create(MM(150), MM(0))
p3 = Point2D.Create(MM(150), MM(80))
p4 = Point2D.Create(MM(0), MM(80))

SketchLine.Create(p1, p2)
SketchLine.Create(p2, p3)
SketchLine.Create(p3, p4)
SketchLine.Create(p4, p1)

# 3. 固化草圖成面 (Solidify)
mode_result = ViewHelper.SetViewMode(InteractionMode.Solid)
```

---

## 五、草圖閉合性與拓撲自交檢驗規則

拉伸或旋轉特徵失敗的最主要原因，在於 2D 草圖未完全封閉或存在微小自交：

1. **節點重合容差 (Tolerance)**：草圖終點與起點的距離必須小於幾何引擎容差（預設 $10^{-6}\text{ m}$），否則系統將識別為開放線段 (Open Curve) 而無法生成實體。
2. **無重疊圖元 (No Overlapping Segments)**：禁止在同一路徑上重複繪製線段，重疊線段將造成拓撲退化。
3. **無懸垂邊 (No Dangling Edges)**：輪廓外部不得存在未閉合的孤立線段（輔助線必須在固化前轉換或刪除）。
4. **曲率連續性**：樣條曲線控制點密度不宜過高，過密控制點容易引發曲率振盪（Runge 現象）導致曲面皺褶。
