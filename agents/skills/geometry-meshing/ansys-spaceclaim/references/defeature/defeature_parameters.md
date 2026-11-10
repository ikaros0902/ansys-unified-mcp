# SpaceClaim 去特徵（Defeature）技術規格與演算法指引

## 一、曲面去特徵（Face Defeaturing）演算法

去特徵引擎對候選實體進行邊界面分析，採用以下多層判定機制：

1. **圓柱幾何形狀匹配**：
   - 檢查 `Face.Shape.Geometry` 是否為 `SpaceClaim.Api.Geometry.Cylinder`。
   - 讀取其半徑 `r = Face.Shape.Geometry.Radius`。
   - 若 $r \le R_{\text{max\_cylinder}}$ 且該面不屬於 `GrpNM_DONTDefeature` 排除集合，則加入待填補清單。
2. **微小曲面與倒角曲面**：
   - 對於非標準圓柱但具有凹陷特徵的自由曲面（NurbsSurface / ProceduralSurface），透過表面主曲率估計最小曲率半徑。
3. **消除呼叫**：
   - 透過 `SpaceClaim.Api.Scripting.Commands.Fill.Execute(Selection.Create(faces))` 進行消除並縫合鄰近主面。
   - 若消除失敗，引擎自動紀錄並回退，不中斷整體管線。

---

## 二、邊線去特徵（Edge Defeaturing）演算法

1. **圓弧分類 (Circle Types)**：
   - **Mode 0 (Full Circle)**：封閉圓形孔邊線，長度 $L \approx 2\pi r$。
   - **Mode 1 (Half Circle)**：半圓孔或槽邊緣，$0.49 \cdot 2\pi r \le L \le 0.51 \cdot 2\pi r$。
   - **Mode 2 (Minor Arc)**：圓角過渡短邊，$L < 0.5 \cdot 2\pi r$。
2. **XFillExecution 機制**：
   - 針對兩面垂直的倒角邊，執行垂直拉伸與面縫合 (`ExtrudeEdges`)。
   - 針對一般相交邊，呼叫自適應 `Fill.Execute()`。

---

## 三、命名選擇輸出架構 (Generated Named Selections)

執行完畢後，去特徵引擎自動建立以下 Named Selections，便於後續檢查：

| Group 名稱 | 內容說明 |
| :--- | :--- |
| `Scr_fs_def_ALL` | 所有成功消除之微小曲面歷史集合 |
| `Scr_edges_def_ALL` | 所有成功消除之圓弧邊與倒角邊線集合 |
| `Scr_fs_def_sizefilter` | 面積大於 `fs_grp_sizefilter` 之主要消除特徵面 |
| `Scr_fs_def_small` | 微小碎面群組 |
