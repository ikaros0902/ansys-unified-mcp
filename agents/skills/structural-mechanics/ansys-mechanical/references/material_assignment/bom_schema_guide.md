# BOM 表格格式與材料關鍵字匹配規範

## 一、Excel BOM 支援格式與欄位對照

自動材料指派引擎支援標準產線與研發 BOM 表格，由動態欄位探測器解析：

| 欄位類型 | 關鍵字匹配清單 | 範例 |
| :--- | :--- | :--- |
| **料號 (Part Number)** | `PART NUMBER`, `JPN`, `DWG`, `DRAWING`, `FILE NAME`, `ITEM` | `100-2458-01`, `FAN_BRACKET.PRT` |
| **品名 (Description)** | `DESC`, `DESCRIPTION`, `COMMON NAME` | `TOP COVER SHEET METAL` |
| **材料 (Material)** | `MATERIAL` (排除 `ADDITIONAL`, `COLOR`) | `AL 6061-T6`, `SUS304`, `SECC` |

---

## 二、內建關鍵字匹配規則字典 (Keyword Fallback Rules)

若零件料號未在 BOM 中找到，引擎會依零件名稱（Part Name）自動匹配 Engineering Data 庫存材料：

- **鋁合金 (Aluminum)**：包含 `AL`, `ALU`, `6061`, `5052`, `ADC12`, `ALUMINUM` $\rightarrow$ 指派 `Aluminum Alloy`
- **不銹鋼 (Stainless Steel)**：包含 `SUS`, `304`, `301`, `316`, `STAINLESS` $\rightarrow$ 指派 `Stainless Steel`
- **電路板 (FR-4 / PCB)**：包含 `PCB`, `PCBA`, `PDB`, `BOARD`, `BACKPLANE` $\rightarrow$ 指派 `FR-4` 或正交各向異性 PCB 等效材料
- **銅箔/導熱墊 (Copper / Thermal)**：包含 `CU`, `COPPER`, `PAD`, `THERMAL_PAD` $\rightarrow$ 指派 `Copper Alloy` / `Thermal Interface Material`
- **橡膠/緩衝墊 (Rubber / Poron)**：包含 `RUBBER`, `PORON`, `FOAM`, `GASKET` $\rightarrow$ 指派 `Rubber` / 阻尼材料
