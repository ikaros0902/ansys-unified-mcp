# Session 05 技術手冊：截面控制與薄板厚度指派規範 (Section Controls & Shell Thickness)

## 1. 物理背景與幾何分類 (Physical Context & Geometry Types)

在伺服器機箱與電子設備的 LS-DYNA 動態衝擊與落摔模擬中，結構件主要分為兩大類：
1. **薄板鈑金結構 (Sheet Metal Structures)**：
   - 包含外殼（Chassis Cover/Bottom）、導風罩（Air Duct）、硬碟托盤（HDD Tray）、主機板固定架（Bracket）等。
   - 特徵為厚度（$t \le 2.0\text{ mm}$）遠小於面內尺寸（$L, W \ge 50\text{ mm}$）。
   - 幾何前處理通常抽取為 **2D 中面幾何（Mid-surface, `GeoBodySheet`）**，在數值分析時透過截面性質指定厚度。
2. **實體結構零件 (Solid Structural Components)**：
   - 包含散熱模組（Heatsink Fin/Base）、螺柱（Standoff）、壓鑄件（Die Casting）、塑料卡扣（Plastic Latches）等。
   - 在幾何前處理中保留為 **3D 實體（`GeoBodySolid`）**。

---

## 2. LS-DYNA 殼單元公式 (`*SECTION_SHELL`) 最佳實踐

### 2.1 ELFORM = 16 (Fully Integrated Shell) vs. ELFORM = 2 (Belytschko-Tsay)
- **ELFORM = 2 (Belytschko-Tsay)**：
  - 單點積分（1 in-plane integration point），計算效率極高。
  - **致命缺點**：容易激發零能量沙漏變形模式（Hourglassing）。在大加速度衝擊、高應力集中孔位（如鉚釘孔、螺絲孔）周圍，單點積分可能產生非物理的網格畸變。
- **ELFORM = 16 (Fully Integrated Shell)**：
  - 4 個面內高斯積分點（$2 \times 2$ in-plane integration points）。
  - **核心優勢**：**完全無沙漏模式（No Hourglassing）**，且完全抗剪切自鎖（Shear Locking），能精準捕捉鈑金沖孔邊緣的大曲率塑性彎曲。
  - **推薦標準**：對於衝擊、跌落等關鍵承載與破壞判定零件，強制採用 `ELFORM = 16`。

### 2.2 厚度方向積分點 (Through-Thickness Integration Points, NIP)
- **標準設定**：`NIP = 5`（高斯-洛巴托積分點 Gauss-Lobatto 或 Gauss）。
- **物理依據**：
  - 薄板受動態衝擊時，外側纖維承受拉伸、內側纖維承受壓縮，彈塑性邊界（Elastic-Plastic Boundary）自表層向中面擴展。
  - 若 `NIP = 2` 或 `3`，無法解析材料非線性硬化與塑性流動，會嚴重低估殘餘變形量。
  - `NIP = 5` 能提供高精度的厚度應力分佈與能量耗散，且計算開銷可控。

### 2.3 關鍵字卡片語法規範
```
*SECTION_SHELL
$#   secid    elform      shrf       nip     propt     qr/ir     icomp      setyp
         1        16     1.000         5         1         0         0         1
$#      t1        t2        t3        t4      nloc     marea      idof    edgset
     0.800     0.800     0.800     0.800     0.000     0.000     0.000         0
```

---

## 3. LS-DYNA 實體單元公式 (`*SECTION_SOLID`) 最佳實踐

### 3.1 四面體網格 (Tetrahedral Elements)
- **ELFORM = 10 (1-Point Tetrahedron with Stabilization)**：
  - 具備數值穩定機制的單點積分四面體單元，適用於複雜壓鑄件、連接器本體等非結構核心零件。
- **ELFORM = 13 (Nodal Pressure Tetrahedron)**：
  - 用於克服傳統 Tet4 單元的體積自鎖（Volumetric Locking），特別適合具有大塑性流動或橡膠襯墊材料的局部區域。

### 3.2 六面體網格 (Hexahedral Elements)
- **ELFORM = 1 (Constant Stress Solid)**：
  - 單點積分六面體，必須搭配沙漏控制：`*HOURGLASS` Type 4 / 5（Flanagan-Belytschko stiffness form，推薦係數 $QH = 0.05 \sim 0.1$）。
- **ELFORM = 2 (Fully Integrated S/R Solid)**：
  - 完全積分選擇性減縮積分六面體，無沙漏模式，適用於重要傳力銷軸或精密受剪區域。

---

## 4. 自動化指派驗證標準 (Automated Verification Gates)

在執行衝擊管線時，必須自動檢驗下列指標：
1. **中面薄板覆蓋率 (Sheet Thickness Coverage)**：
   - 全機未抑制之 `GeoBodySheet` 物件中，已正確指派物理厚度之比例必須為 **100%**。
2. **厚度合理性檢查 (Thickness Sanity Check)**：
   - 厚度範圍必須落在 $0.2\text{ mm} \le t \le 5.0\text{ mm}$ 之內，杜絕 0 或負厚度。
3. **實體體積檢查 (Solid Volume Check)**：
   - 全機未抑制之 `GeoBodySolid` 物件之體積必須大於 0（$\text{Volume} > 0$），防止無效退化體。
