# CAD 缺陷診斷與幾何修復判斷力庫 (CAD Diagnostics Reference)

幾何缺陷是導致下游網格劃分失敗（Meshing Failure）、網格品質惡化（Skewness > 0.98）、局部極小單元拖垮 CFL 時間步長，以及求解器數值發散的根源。本手冊建立工程師與 AI Agent 的 **CAD 缺陷判斷力庫**，定義客觀檢驗門檻與標準化修復 SOP。

---

## 一、四大 CAD 致命缺陷與判斷力指標庫

| 缺陷類型 | 幾何特徵與診斷判據 | 工程危害 | 修復策略與處置閾值 |
|---|---|---|---|
| **微小狹長面 (Sliver Faces)** | 1. 表面面積 $A < 10^{-7}\text{ m}^2$<br>2. 面長寬比 $\text{Aspect Ratio} > 50:1$<br>3. 兩相鄰邊法向夾角極小 | 造成極度扭曲的網格單元，引發負體積 (Negative Volume) 或直角金字塔畸變。 | **消除或合併**：若面寬 $< 0.1\text{ mm}$，以 SpaceClaim `FixSlivers` 工具將相鄰面縫合或以拉伸面替換。 |
| **自交邊與退化邊 (Degenerate Edges)** | 1. 曲線起訖點距離 $< 10^{-6}\text{ m}$ 但非閉合圓<br>2. 曲線曲率半徑小於自身截面半徑<br>3. 空間樣條曲線自身相交 | 破壞 B-Rep 拓撲水密性，網格生成器無法建立連續面網格。 | **重構或裁剪**：增大導引線曲率半徑，重新擬合 NURBS 樣條控制點，剔除重複邊。 |
| **極短邊 (Short Edges)** | 1. 邊長 $L < 10^{-4}\text{ m}$ ($0.1\text{ mm}$)<br>2. 邊長小於相鄰宏觀特徵尺寸的 $1/100$<br>3. 邊長小於預期網格尺寸的 $1/10$ | 迫使網格在此處局部過度密集加密，導致節點數爆增與時間步長縮小數個數量級。 | **塌陷 (Collapse)**：將短邊端點合併為單一頂點 (Vertex Merge)，或移除相鄰微小倒角。 |
| **流體滲漏 (Fluid Leakage)** | 1. 布林相減後流體域外邊界出現穿透孔洞<br>2. 裝配體零件間存在公差間隙造成流體漏出<br>3. 流體域體積 $V \le 0$ 或出現多個非連通域 | 流體邊界條件無法密封，求解器無物理意義（質量不守恆或流動穿透固體壁面）。 | **封堵修復**：在布林運算前以蓋面 (Cover Face) 封堵間隙，或調大縫合公差 (Stitching Tolerance)。 |

---

## 二、幾何特徵簡化 (Defeaturing) 工程決策準則

在將 CAD 模型送入網格剖分前，**嚴禁將未簡化的工業原始加工圖直接導入**。必須依據模擬物理場特性執行特徵過濾：

```mermaid
flowchart TD
    A[原始 CAD 幾何模型] --> B{特徵尺寸評估}
    B -->|特徵尺寸 < 0.05 × 基礎網格尺寸| C[微小裝配特徵]
    B -->|特徵尺寸 >= 0.05 × 基礎網格尺寸| D[保留主要幾何]
    C --> E{是否處於主要受力/核心流動區?}
    E -->|否 (非關鍵區域)| F[強制去特徵: 刪除圓角/倒角/螺紋/刻字]
    E -->|是 (流體分離點/應力集中區)| G[保留並建立局部加密網格控制]
    F --> H[執行幾何水密性診斷]
    D --> H
```

### 1. 必殺特徵（無條件移除）
- **非功能性刻字與標籤**：Logo、零件號碼、製造年份等微小凸起或凹槽。
- **標準緊固件螺紋 (Threads)**：將內外螺紋簡化為平滑圓柱孔與圓柱軸。
- **微小裝配倒角 (Chamfers < 0.5mm)**：在非流體分離邊緣處，一律還原為尖角（Sharp Corner）。

### 2. 慎殺特徵（評估後決策）
- **氣動分離邊緣 (Aero Separation Edges)**：如機翼前緣圓角、擾流板尖端，直接影響阻力與分離點位置，必須保留。
- **應力集中過渡圓角 (Stress Concentration Fillets)**：結構疲勞評估區必須保留。

---

## 三、SpaceClaim 原生 Repair 修復指令集

在 SpaceClaim / SCDM 中，可透過腳本批量呼叫內建 Repair 演算法修復 CAD 缺陷：

```python
# ==============================================================================
# SpaceClaim Native Script (IronPython) - 自動修復診斷
# ==============================================================================
# 1. 縫合開放曲面成實體 (Stitch Surfaces)
surfaces = FaceSelection.Create(GetRootPart().Faces)
options = StitchOptions()
options.Tolerance = MM(0.01) # 縫合公差 0.01mm
StitchFaces.Execute(surfaces, options)

# 2. 自動偵測並消除微小狹長面 (Fix Slivers)
sliver_options = FixSliversOptions()
sliver_options.MaximumWidth = MM(0.1) # 消除寬度小於 0.1mm 的面
FixSlivers.Execute(sliver_options)

# 3. 移除微小短邊 (Remove Small Edges)
edge_options = RemoveSmallEdgesOptions()
edge_options.MaximumLength = MM(0.05)
RemoveSmallEdges.Execute(edge_options)

# 4. 偵測封閉流體域滲漏與間隙 (Gap Detection)
gap_options = FindGapsOptions()
gap_options.Tolerance = MM(0.05)
gap_results = FindGaps.Execute(gap_options)
```

---

## 四、自動化 CAD 缺陷診斷指標與報告格式

所有幾何前處理腳本在導出幾何前，均應生成標準診斷稽核數據：

```json
{
  "diagnostic_summary": {
    "total_bodies": 2,
    "total_faces": 128,
    "total_edges": 312,
    "watertight": true,
    "defects_found": {
      "sliver_faces": 0,
      "short_edges": 0,
      "self_intersections": 0,
      "fluid_leakage": false
    },
    "status": "PASS_EXPORT_ALLOWED"
  }
}
```

若 `defects_found` 任一項非零或 `watertight == false`，系統應發出嚴重警告並中斷導出流程，進入幾何修復循環。
