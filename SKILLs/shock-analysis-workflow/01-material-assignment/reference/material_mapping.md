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

---

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
