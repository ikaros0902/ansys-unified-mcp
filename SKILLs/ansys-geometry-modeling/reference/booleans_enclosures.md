# 外流域抽取 (Enclosure) 與布林運算專精手冊 (Booleans & Enclosures Reference)

在計算流體力學 (CFD) 與共軛熱傳 (CHT) 數值模擬中，流體域往往並非由 CAD 原圖直接提供，而是需透過幾何外包覆生成「外流域 (Enclosure)」並透過「布林相減 (Boolean Subtract)」挖空標的實體。

---

## 一、CFD 外流域尺寸工程黃金比例準則

為避免邊界效應干擾流場發展、消除出口邊界數值反射，外流域尺寸必須嚴格遵循空氣動力學與 CFD 業界經驗公式（$L$ 為物體特徵長度，$W$ 為特徵寬度，$H$ 為特徵高度）：

```
                  ┌────────────────────────────────────────┐
                  │              Top Boundary              │
                  │                                        │
    ──► Inlet     │         ┌───────────┐                  │    ──► Outlet
 (2 ~ 3 L Upstream)│         │ SolidBody │                  │ (6 ~ 8 L Downstream)
                  │         └───────────┘                  │
                  │                                        │
                  └────────────────────────────────────────┘
                               Ground / Symmetry
```

1. **上游入口距離 (Upstream Inlet)**：$2.0 \sim 3.0 \times L$。確保進入物體前流場均勻，避免入口速度邊界條件直接壓迫滯止點。
2. **下游出口距離 (Downstream Outlet)**：$6.0 \sim 8.0 \times L$。確保分離渦流與尾流 (Wake) 充分發展耗散，防止出口靜壓邊界發生非物理回流 (Reverse Flow)。
3. **兩側與頂部距離 (Sides & Top)**：$2.5 \sim 3.0 \times W$ 或 $H$。控制截面**阻塞率 (Blockage Ratio) $< 3\%$**：
   $$\text{Blockage Ratio} = \frac{A_{\text{frontal}}}{A_{\text{domain}}} < 0.03$$
4. **底面 (Ground)**：
   - 外部無窮流場（飛機、無人機）：距底部 $2.5 \sim 3.0 \times H$。
   - 地面效應/車輛空氣動力學：貼合物體底面車輪接地切點，設定為 Moving Ground 或無滑移壁面。

---

## 二、布林相減操作模式：單相流 vs 共軛熱傳 (CHT)

布林相減操作的核心在於目標域與工具實體的從屬關係：
$$\text{Fluid Domain}_{\text{hollow}} = \text{Fluid Domain}_{\text{outer}} - \sum \text{Solid Bodies}$$

### 1. 單相流場模式 (Single-Phase CFD)
- **實體處置**：`keep_other = False`（或 SpaceClaim `KeepTools = False`）。
- **目的**：只保留純流體空心腔體，固體本體被完全銷毀以節省記憶體與網格節點數。

### 2. 共軛熱傳 / 流固耦合模式 (CHT / FSI)
- **實體處置**：`keep_other = True`。
- **目的**：流體域中挖出固體輪廓，但**保留固體實體**。
- **關鍵拓撲約束**：流體表面與固體外表面必須完全重合，且必須開啟**拓撲共享 (Shared Topology)**，使流固交界面節點共用，實現熱流無縫連續傳導。

---

## 三、PyAnsys Geometry 演算法實作

```python
from ansys.geometry.core.math import Point3D
from ansys.geometry.core.designer import Design

def create_cfd_enclosure_pipeline(
    design: Design,
    solid_body,
    l_char: float,
    w_char: float,
    h_char: float,
    upstream_mult: float = 2.5,
    downstream_mult: float = 7.0,
    side_mult: float = 2.5,
    top_mult: float = 2.5,
    is_cht_mode: bool = False
):
    """
    依據空氣動力學準則自動生成包覆外流域並執行布林相減
    """
    # 1. 提取固體幾何包圍盒
    bbox = solid_body.bounding_box
    min_p = bbox.min_point
    max_p = bbox.max_point
    
    # 2. 計算流體域擴展邊界
    enc_min_x = min_p.x - (upstream_mult * l_char)
    enc_max_x = max_p.x + (downstream_mult * l_char)
    enc_min_y = min_p.y - (side_mult * w_char)
    enc_max_y = max_p.y + (side_mult * w_char)
    enc_min_z = min_p.z  # 貼齊底面
    enc_max_z = max_p.z + (top_mult * h_char)
    
    len_x = enc_max_x - enc_min_x
    len_y = enc_max_y - enc_min_y
    len_z = enc_max_z - enc_min_z
    
    center_coords = [
        (enc_min_x + enc_max_x) / 2.0,
        (enc_min_y + enc_max_y) / 2.0,
        (enc_min_z + enc_max_z) / 2.0
    ]
    
    # 3. 建立外流域長方體實體
    fluid_body = design.create_block(
        name="FluidEnclosureDomain",
        length=len_x,
        width=len_y,
        height=len_z,
        center=center_coords
    )
    
    # 4. 執行布林差集扣除
    fluid_body.subtract(solid_body, keep_other=is_cht_mode)
    
    return fluid_body
```

---

## 四、SpaceClaim 原生 IronPython 腳本實作

SpaceClaim 原生具備強大的 `Enclosure.Create` 與 `Boolean` API：

```python
# ==============================================================================
# SpaceClaim Native Script (IronPython) - 外流域與布林扣除
# ==============================================================================
# 選定待包覆的固體實體
target_bodies = BodySelection.Create(GetRootPart().Bodies[0])

# 定義 6 個方向的緩衝裕度 (單位公釐 mm)
options = EnclosureOptions()
options.EnclosureType = EnclosureType.Box
options.CushionPositiveX = MM(1500)  # 下游出口
options.CushionNegativeX = MM(600)   # 上游入口
options.CushionPositiveY = MM(500)   # 側向
options.CushionNegativeY = MM(500)   # 側向
options.CushionPositiveZ = MM(600)   # 頂部
options.CushionNegativeZ = MM(0)     # 貼齊地面

# 自動生成外流域並扣除內部物體
result = Enclosure.Create(target_bodies, options)
enclosure_body = result.CreatedBodies[0]
enclosure_body.Name = "FluidDomain"
```

---

## 五、布林相減後之拓撲驗證檢核清單

在布林相減完成後，必須即刻執行下列幾何驗證，嚴禁直接導出：
1. **流體域容積正定性**：$\text{Volume}_{\text{fluid}} > 0$ 且大於原固體體積。
2. **表面特徵增生核查**：相減後流體域內部應新增對應固體外觀之內部腔面 (Cavity Walls)，表面總數量必須正確增加。
3. **無非流形接縫**：檢查接觸邊線是否形成奇異非流形邊 (Non-manifold edges)；若物體與外框切齊共面，必須確認布林運算未切穿成碎塊。
