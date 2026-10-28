---
name: 01-material-assignment
description: 自動化材料指派會話（Material Assignment Session），整合 ACT 關鍵字比對引擎、BOM 查表、SMT 元件正則匹配與小批次驗證機制。
---

# Session 01: 材料自動指派與驗證 (Material Assignment & Verification)

## 1. 目標 (Objective)
在 ANSYS Mechanical LS-DYNA 衝擊分析專案中，依據 CAD 幾何名稱、零件階層與 BOM 表，自動且精確地為全機所有 Body（實體與鈑金面）指派對應的物理材料模型（如 `*MAT_024 Piecewise Linear Plasticity` 彈塑性材料或線性彈性材料），並自動標記與隔離未匹配的孤兒物件。

---

## 2. ACT 比對引擎架構 (ACT Matching Engine Architecture)

本會話完整整合了 ACT 擴充套件 `MECH_Material_Assignment.py` 的核心匹配演算法，提供四級優先順序的比對階梯（Matching Hierarchy）：

```mermaid
flowchart TD
    A[CAD Body / Part 名稱] --> B[字串清理 clean_name_string]
    B --> C{優先級 1: BOM Lookup}
    C -- 命中 --> Z[指派材料 & 紀錄來源]
    C -- 未命中 --> D{優先級 2: 直接材料關鍵字}
    D -- 命中 --> Z
    D -- 未命中 --> E{優先級 3: 結構功能關鍵字}
    E -- 命中 --> Z
    E -- 未命中 --> F{優先級 4: SMT 元件正則表達式}
    F -- 命中 --> Z
    F -- 未命中 --> G[加入未指派清單]
    G --> H[建立 [Mat] Unassigned_Bodies NS]
```

---

## 3. 核心比對邏輯與參考手冊 (Progressive Disclosure)

- **CAD 名稱清理演算法 (`clean_name_string`)**：自動剔除 (Solid)、(Surface)、.prt.1 等 CAD 命名雜訊。
- **多階關鍵字比對字典 (`match_keyword_rules`)**：依序比對 SGCC、AL6061、SUS301、FR4、PC+ABS 及 SMT 正則。
- **孤兒物件管理 (`[Mat] Unassigned_Bodies`)**：未匹配物件自動群組建立 Named Selection，加速人工審查。
- **LS-DYNA `*MAT_024` 關鍵字卡片**：注入應變率相依 Cowper-Symonds 參數（C=40.0, P=5.0）。

> 完整演算法程式碼與 LS-DYNA 卡片定義，詳見專門手冊：
> - [`../../../ansys-mechanical/references/material_assignment/overview.md`](../../../ansys-mechanical/references/material_assignment/overview.md)

---

## 4. 小批次驗證章節 (Dedicated Verification Section)

為確保自動化指令之穩定性，禁止直接進行長時間求解。本工作流程採用 **10 個樣本 Body** 的小批次驗證機制。

### 4.1 驗證步驟
1. 透過 PyMechanical gRPC 連線至 Port 10000。
2. 隨機或循序選取 10 個幾何 Body（包含螺絲、鈑金 Surface、固定座 Solid）。
3. 執行字串清理與材料關鍵字匹配。
4. 驗證材料指派正確性及 `[Mat] Unassigned_Bodies` 建立狀態。
5. 輸出測試覆蓋率與詳細日誌。

### 4.2 獨立測試腳本執行方式
執行以下獨立測試腳本：
```powershell
python skills/shock-analysis-workflow/scripts/test_session_01.py
```

### 4.3 驗證評估指標 (Verification Metrics)
- **樣本數量 (Sample Size)**: 10 Bodies
- **匹配成功率 (Coverage Rate)**: $\ge 90\%$
- **孤兒物件標記 (Orphan Tracking)**: 未匹配物件 100% 進入 `[Mat] Unassigned_Bodies`
- **模型無污染 (Cleanliness)**: 驗證完成後無殘留垃圾變數。

---

## 5. 相關參考手冊 (Related References)

| 手冊名稱 | 內容摘要 |
| :--- | :--- |
| [`../../../ansys-mechanical/references/material_assignment/overview.md`](../../../ansys-mechanical/references/material_assignment/overview.md) | 清理正規化、關鍵字比對表、孤兒 NS 建立與 *MAT_024 卡片 |




## Reference: material_mapping.md

# Material Mapping & Keyword Definitions

本手冊為 Session 01: 材料自動指派（Material Assignment）之底層演算法與 LS-DYNA 關鍵字卡片實作細節。

---

### 2.1 CAD 名稱清理演算法 (`clean_name_string`)
去除 CAD 匯入時產生的雜訊、零件編號、副檔名與實體型態後綴：
```python
import re

def clean_name_string(name_str):
    if name_str is None:
        return ""
    try:
        s = "".join([c for c in str(name_str) if ord(c) < 128])
    except:
        s = str(name_str)
    # 去除 (Solid), (Surface), (Sheet), (Body), (Part) 等後綴
    s = re.sub(r'(?i)\s*[\(\[]\s*(Solid|Surface|Sheet|Body|Part)\s*[\)\]]', '', s)
    # 去除 CAD 匯出流水號與副檔名 (例如 .prt.1, .asm.2, .sldprt)
    s = re.sub(r'(?i)(\.prt|\.asm)\.\d+$', '', s)
    s = re.sub(r'(?i)\.(asm|prt|sldprt|sldasm)$', '', s)
    s = re.sub(r':\d+$', '', s)
    return s.strip().upper()
```

### 2.2 多階關鍵字比對字典 (Matching Rule Engine)

```python
def match_keyword_rules(name_str):
    s = str(name_str).upper()
    
    # Priority 2: 直接材料關鍵字 (Direct Material Keywords)
    if 'SGCC' in s or 'SGC400' in s:
        return "SGCC", "Direct Material: SGCC"
    if '6061' in s or 'AL6061' in s or '6061-T6' in s or 'ALUMINUM' in s:
        return "Aluminum alloy, wrought, 6061, T6", "Direct Material: 6061 Aluminum"
    if '301' in s or 'SUS301' in s or 'SUS304' in s or 'STAINLESS' in s:
        return "Stainless Steel - 301 1/2H", "Direct Material: 301 Stainless"
    if 'FR4' in s or 'FR-4' in s:
        return "PCB laminate, Epoxy/Glass fiber, FR-4", "Direct Material: FR-4"
    if 'PC+ABS' in s or 'PC/ABS' in s or 'CYCOLOY' in s or 'BAYBLEND' in s or 'C6200' in s or 'C2950' in s:
        return "SABIC Cycoloy C6200 PC+ABS", "Direct Material: PC+ABS"
    if 'NYLON' in s or 'PA66' in s or 'PA6' in s:
        return "NYLON 66", "Direct Material: Nylon"
    if 'COPPER' in s or 'C1100' in s or 'CU' in s:
        return "Copper Alloy", "Direct Material: Copper"
    if 'SAE1215' in s or 'CARBON STEEL' in s:
        return "SAE1215 - STF", "Direct Material: Carbon Steel"
    if 'ZA8' in s or 'ZINC' in s:
        return "Die Casting - ZA8, Zinc Alloy", "Direct Material: Zinc ZA8"
        
    # Priority 3: 結構功能關鍵字 (Functional Structural Keywords)
    if any(k in s for k in ['CHASSIS', 'BOTTOM', 'TOP-COVER', 'COVER', 'TRAY', 'CAGE', 'BRACKET', 'BKT', 'WALL', 'WINDOW', 'BAR', 'PANEL', 'BEZEL', 'PARTITION', 'BAREBONE', 'STAKE']):
        return "SGCC", "Functional: Sheet Metal Chassis"
    if any(k in s for k in ['PCB', 'PBA', 'PCBA', 'MB_', 'DIMM', 'RISER', 'EGS-', 'MID-PLANE', 'ODP', 'CPLD', 'WHITLEY', 'CARD', 'ITS_']):
        return "PCB laminate, Epoxy/Glass fiber, FR-4", "Functional: PCB Assembly"
    if any(k in s for k in ['FIN', 'CUBASE', 'HEATPIPE', 'VAPOR', 'BASE', 'HEATSINK', '1U_CU', 'HS']):
        return "Aluminum alloy, wrought, 6061, T6" if "AL" in s else "Copper Alloy", "Functional: Thermal Heatsink"
    if any(k in s for k in ['AIR-DUCT', 'AIR_DUCT', 'DUCT', 'SHROUD', 'HOLDER', 'CLIP', 'RAIL', 'LATCH', 'HOUSING', 'PLASTIC', 'JVPLS', 'EAR-L-LATCH', 'LEVER', 'CARRIER']):
        return "SABIC Cycoloy C6200 PC+ABS", "Functional: Plastic / Shroud"
    if any(k in s for k in ['CONN', 'MCIO', 'SLIMSAS', 'FH34', 'USB', 'MINIDP', 'HEADER', 'SLOT']):
        return "SABIC Cycoloy C6200 PC+ABS", "Functional: Connector LCP"
    if any(k in s for k in ['SCREW', 'STANDOFF', 'RIVET', 'NUT', 'HDW', 'JVHDW', 'ST-', 'SI-', 'TP-', '60H', 'SCR']):
        return "SAE1215 - STF", "Functional: Hardware Fastener"
    if any(k in s for k in ['FAN', 'DFPK']):
        return "Plastic, PA6", "Functional: Fan Module"
    if any(k in s for k in ['SPRING', 'SUS']):
        return "Stainless Steel - 301 1/2H", "Functional: Spring"
    if any(k in s for k in ['DIE-CASTING', 'DIE_CASTING', 'CASTING']):
        return "Aluminum alloy, wrought, 6061, T6", "Functional: Die Casting"
        
    # Priority 4: SMT 電路板細部零件正則表達式 (SMT Regex)
    if re.match(r'^(D|J|R|C|U|L|Q|SW|LED)\d+', s):
        return "PCB laminate, Epoxy/Glass fiber, FR-4", "SMT Component (D/J/R/C/U)"
        
    return None, None
```

### 2.3 孤兒物件管理與 Named Selection 生成
所有未匹配成功的 Body 將自動集合並建立 Named Selection `[Mat] Unassigned_Bodies`，提供工程師快速聚焦檢查：
```python
def update_unassigned_named_selection(model, ExtAPI, unassigned_bodies):
    ns_name = "[Mat] Unassigned_Bodies"
    existing_ns = None
    if model.NamedSelections:
        for child in model.NamedSelections.Children:
            if child.Name == ns_name:
                existing_ns = child
                break
    if unassigned_bodies:
        if not existing_ns:
            existing_ns = model.AddNamedSelection()
            existing_ns.Name = ns_name
        sel_mgr = ExtAPI.SelectionManager
        sel_info = sel_mgr.CreateSelectionInfo(Ansys.ACT.Interfaces.Common.SelectionTypeEnum.GeometryEntities)
        sel_info.Entities = [b.GetGeoBody() for b in unassigned_bodies if b.GetGeoBody()]
        existing_ns.Location = sel_info
    elif existing_ns:
        try:
            existing_ns.Delete()
        except:
            pass
```

## 3. LS-DYNA Keyword 注入 (*MAT_024 非線性塑性模型)

若 Engineering Data 中僅包含線性彈性參數，可針對金屬部件注入 `*MAT_PIECEWISE_LINEAR_PLASTICITY`（`*MAT_024`）關鍵字卡片：
```
*MAT_PIECEWISE_LINEAR_PLASTICITY
$#   mid        ro         e        pr      sigy      etan      fail      tdel
       1  7.850E-6     200.0      0.30     0.280     0.000     0.000     0.000
$#     c         p      lcss      lcsr        vp
  40.000     5.000         0         0     0.000
```
- **Cowper-Symonds 應變率敏感性參數**: $C = 40.0\text{ s}^{-1}, P = 5.0$ 用於考量衝擊高應變率下的屈服強度提升。

---
