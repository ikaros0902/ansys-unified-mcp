# LS-DYNA 顯式截面卡片 (`*SECTION_SHELL` / `*SECTION_SOLID`)

本手冊為 `ansys-mechanical-section-assign` 的顯式分析分支，內容整併並改寫自 `shock-analysis-workflow/05-section-assignment` 既有規範，去除衝擊分析專屬敘事，保留通用截面選型準則，供 server/機構衝擊/wireline/payment 等產品線的 LS-DYNA 顯式模型共用。

---

## 一、幾何分類前提

截面卡片的選型取決於幾何在前處理階段的分類（與分析產品線無關）：
- **殼體（`GeoBodySheet`）**：薄板鈑金件、PCB 板、導風罩等，厚度遠小於面內尺寸，走 `*SECTION_SHELL`。
- **實體（`GeoBodySolid`）**：散熱模組、連接器、螺柱等保留為 3D 實體，走 `*SECTION_SOLID`，再依網格形態（Tet/Hex）細分 ELFORM。

---

## 二、殼單元公式選型 (`*SECTION_SHELL`)

| ELFORM | 名稱 | 積分方式 | 適用場景 | 風險 |
|---|---|---|---|---|
| 2 | Belytschko-Tsay | 單點面內積分 | 非關鍵零件、計算效率優先 | 易激發沙漏模式（Hourglassing），高曲率孔邊易失真 |
| 16 | Fully Integrated Shell | $2\times2$ 面內高斯積分 | 關鍵承載/破壞判定零件（鈑金彎折區、孔緣） | 計算成本較高，但無沙漏模式且抗剪切自鎖 |

**厚度方向積分點 `NIP`**：預設 `NIP=5`（Gauss-Lobatto 或 Gauss）。`NIP < 5`（如 2、3）無法正確解析彈塑性邊界自表層向中面擴展的塑性流動，會低估殘餘變形量；`NIP=5` 為通用動態衝擊/彎曲工況的標準起點。

```
*SECTION_SHELL
$#   secid    elform      shrf       nip     propt     qr/ir     icomp      setyp
         1        16     1.000         5         1         0         0         1
$#      t1        t2        t3        t4      nloc     marea      idof    edgset
     0.800     0.800     0.800     0.800     0.000     0.000     0.000         0
```

`t1`~`t4` 四角厚度值通常填入相同厚度（除非為漸變厚度鈑金件）；`secid` 須與 `*PART` 卡片中引用的 Section ID 一致。

---

## 三、實體單元公式選型 (`*SECTION_SOLID`)

| 網格形態 | ELFORM | 名稱 | 適用場景 | 必要搭配 |
|---|---|---|---|---|
| Tet4 | 10 | 1-Point Tetrahedron w/ Stabilization | 複雜壓鑄件、連接器本體（非結構核心） | 無 |
| Tet4 | 13 | Nodal Pressure Tetrahedron | 大塑性流動或橡膠襯墊局部區域 | 克服體積自鎖 |
| Hex8 | 1 | Constant Stress Solid | 一般實體零件，計算效率優先 | 必須搭配 `*HOURGLASS`（見下） |
| Hex8 | 2 | Fully Integrated S/R Solid | 重要傳力銷軸、精密受剪區域 | 無（無沙漏模式） |

```
*SECTION_SOLID
$#   secid    elform       aet
         2        10         0
```

### 3.1 Hex8 + ELFORM=1 的強制沙漏控制
單點積分六面體必須搭配 `*HOURGLASS` 卡片（Type 4 或 5，Flanagan-Belytschko stiffness form，推薦係數 `QH = 0.05 ~ 0.1`）；缺少沙漏控制會導致零能量模式擴散，使變形結果失真。

---

## 四、截面卡片與 `*PART` 的關聯規則

每個 `*SECTION_SHELL` / `*SECTION_SOLID` 的 `secid` 必須被對應的 `*PART` 卡片引用（`*PART` 第二行的 `SECID` 欄位），且同一 `secid` 可被多個共用相同厚度/單元公式的 `*PART` 共用，避免為每個零件重複產生獨立 Section。

---

## 五、客觀驗證門檻 (Verification Gates)

執行截面指派後，必須以下列客觀條件驗證，而非主觀判斷「應該設好了」：

1. **殼體覆蓋率**：全機未抑制 `GeoBodySheet` 中，已產生對應 `*SECTION_SHELL` 卡片之比例須為 100%。
2. **厚度合理性**：卡片中 `t1`（或 `Body.Thickness` 來源值）須落在 $0.2\text{ mm} \le t \le 5.0\text{ mm}$，杜絕 0 或負厚度（若產品線厚度範圍不同，依實際工程圖調整門檻並記錄依據）。
3. **實體體積有效性**：全機未抑制 `GeoBodySolid` 之幾何體積須 $> 0$，防止退化體被指派截面。
4. **ELFORM/NIP 一致性**：關鍵承載殼體須為 `ELFORM=16, NIP=5`；非關鍵殼體若採 `ELFORM=2`，必須確認已另行配置 `*CONTROL_SHELL` 的沙漏能監控。
