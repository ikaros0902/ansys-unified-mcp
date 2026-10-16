# Contact Tool 驗證與過度約束防呆 (Overconstraint Guard)

本手冊涵蓋 Bonded Contact 批次建立（整合 `Mech_bonded.py` / `bonded_contact_creator.py` 核心邏輯）、Contact Tool 驗證判讀，以及 Error 20110 過度約束防呆機制，通用於 static、thermal、LS-DYNA 三類分析。`ContactType`、`ContactFormulation`、`PinballRadius` 等列舉與屬性已於 `ansys-mechanical/references/connections_and_contacts.md` 完整定義，本手冊**不重複列出**，僅交叉引用並補充過度約束相關的防呆邏輯。

---

## 一、Bonded Contact 批次建立（來自 2-face Named Selection）

SpaceClaim 側以 `Connect Topology` 開頭命名、恰好含 2 個面 ID 的 NS，代表一組待建立的 Bonded 介面：

```python
# ContactType, ContactPinballType 已於 ansys-mechanical/references/connections_and_contacts.md 定義，此處不重複列舉
def create_bonded_contacts_from_connect_topology(connections_group, ExtAPI, all_ns, pinball_mm=1.22, prefix="Connect Topology"):
    created, skipped_empty, skipped_not_pair = 0, 0, 0
    existing_names = [c.Name for c in connections_group.Children]

    for ns in all_ns:
        if not ns.Name.startswith(prefix):
            continue
        if ns.Entities.Count == 0:
            skipped_empty += 1
            continue

        pair_ids = ns.Location.Ids
        if len(pair_ids) != 2:
            skipped_not_pair += 1
            continue
        if ns.Name in existing_names:
            continue  # 避免重複建立同名接觸對

        face1 = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        face1.Ids = [pair_ids[0]]
        face2 = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        face2.Ids = [pair_ids[1]]

        bonded = connections_group.AddContactRegion()
        bonded.Name = ns.Name
        bonded.ContactType = ContactType.Bonded
        bonded.SourceLocation = face1
        bonded.TargetLocation = face2
        bonded.PinballRegion = ContactPinballType.Radius
        bonded.PinballRadius = Quantity(pinball_mm, "mm")
        bonded.ShellThicknessEffect = False  # 殼體厚度不納入接觸偵測範圍，避免薄板過度判定接觸
        created += 1

    return created, skipped_empty, skipped_not_pair
```

**Pinball 半徑建議值**：預設 `1.22 mm`（沿用既有 `Mech_bonded.py` 經驗值，適用於一般鈑金/塑件公差範圍）；若零件公差帶明顯更大或更小，應依實際 CAD 公差調整，而非固定套用該值。

---

## 二、Contact Tool 驗證（求解前/後必要步驟）

```python
# AddContactTool 已於 ansys-mechanical/references/connections_and_contacts.md 示範，此處聚焦判讀邏輯
def verify_contacts_with_tool(analysis):
    contact_tool = analysis.Solution.AddContactTool()
    status_res = contact_tool.AddStatus()
    penetration_res = contact_tool.AddPenetration()
    contact_tool.EvaluateAllResults()
    return contact_tool, status_res, penetration_res
```

**客觀判讀準則**（非主觀「應該沒事」）：
1. **穿透量**：應小於特徵尺寸的 0.1%，或單元尺寸的 1%，取較嚴格者。
2. **接觸狀態**：應為 `Sticking`（黏著）或 `Sliding`（滑移）；出現大量 `Far Open` 代表 Pinball 半徑不足或幾何間隙過大，需調整後重新驗證，不可直接放行求解。

### 2.1 熱接觸電阻設定（Thermal Contact Resistance）

> 來源查證：NotebookLM「Ansys Mechanical」與「Ansys Official」兩個筆記本均**查無**熱接觸電阻／熱導通係數（Thermal Conductance）的具體 API 屬性名稱、設定路徑與典型值範圍，筆記本來源以版本發布特性介紹影片為主，未涵蓋此主題的 API 層細節。以下僅記錄可從既有 ANSYS Mechanical 接觸物件模型結構合理推斷、但**尚未經官方文件逐一核對**的事項，標記處一律視為**待 api_search 查證**：

- 熱-結構耦合分析（Coupled Field / Thermal-Structural Simulation）中，Contact Region 物件理論上應存在對應的熱傳導介面參數（概念上對應 Workbench GUI 的 "Pipe Conductance" 或 "Thermal Conductance" 欄位），但具體 API 屬性名稱（如是否為 `ThermalConductance`、`ContactConductance` 或其他命名）**待 api_search 查證**。
- 典型工程做法是以「單位面積熱阻（m²·K/W）」或其倒數「熱導（W/m²·K）」描述介面接觸熱阻，數值高度依賴表面粗糙度、接觸壓力與是否存在填隙材料（thermal interface material），**不存在**可泛用於所有介面的通用典型值，必須依實驗量測或材料供應商數據取得，嚴禁套用單一假設數字。
- 若專案需要設定熱接觸電阻，建議先以 ANSYS 官方 API 文件（`api_search` 工具）核對 `Ansys.ACT.Automation.Mechanical.Connections.ContactRegion` 類別下是否存在熱傳導相關屬性，再落地到腳本中，不應憑記憶或猜測直接寫入屬性名稱。

### 2.2 Hertz 接觸解析解比對驗證流程

> 來源查證：兩筆記本均**查無** Hertz 接觸理論（雙圓柱線接觸、雙球體點接觸）之最大接觸壓力解析解公式，亦無 ANSYS 官方的 Hertzian benchmark 設定步驟。以下為可從通用網格收斂驗證邏輯（參考來源：「Ansys Official」筆記本中關於應力奇異點與網格收斂判讀的通用說明）改寫整理的驗證流程，**公式本身未經筆記本來源驗證**，比對前需自行核對教科書或 ANSYS 官方驗證案例（Verification Manual）中的 Hertz 公式：

1. **建立對照模型**：將欲驗證之接觸介面簡化為標準 Hertz 工況（2D 平面應變雙圓柱線接觸，或軸對稱雙球體點接觸），材料設定為線彈性，避免摩擦與塑性等非線性效應干擾比對。
2. **解析解作為基準**：依接觸幾何（曲率半徑）、材料（等效彈性模數）與施加載荷，計算理論最大接觸壓力與接觸半寬/半徑，作為數值解比對基準；公式細節**待 api_search 或教科書查證**，不可憑記憶套用。
3. **網格收斂判讀**：在接觸區域逐步加密網格，觀察數值解最大接觸應力是否隨網格細化而**收斂至解析解附近並趨於穩定**，而非持續無限制上升。若應力隨網格細化持續增加不收斂，代表該處為人工應力集中（如尖角、點載荷），而非真實的 Hertz 接觸應力分佈，需檢查幾何是否存在應消除的銳邊或點接觸簡化失真。
4. **誤差容許門檻**：數值解與解析解之最大接觸壓力差異，建議控制在工程可接受範圍內（如 5~10%），具體門檻依分析精度需求與專案規範調整，不可用單一絕對數字套用所有工況。

### 2.3 摩擦生熱設定（Friction Heat Generation）

> 來源查證：兩筆記本均**查無**摩擦生熱開關與耗散係數（Heat Dissipation Factor / Heat Generation Factor）的具體 API 屬性名稱與設定路徑。筆記本中僅確認 ANSYS Mechanical 支援 Frictional Contact（庫倫摩擦模型，摩擦力依切向滑移與摩擦係數計算）與熱-結構耦合分析（Coupled Field Static/Transient）兩項相關但非直接對應的功能。

- 概念上，摩擦生熱是將接觸面滑移過程中因摩擦力做功轉換為熱通量輸入至接觸面兩側，此機制需仰賴熱-結構耦合（Thermal-Structural Coupling）或耦合場分析類型才能生效，純結構分析不會計算此熱效應。
- 耗散係數（摩擦功轉換為熱的比例，通常介於 0~1 之間）之具體 API 屬性名稱、是否可於 Contact Region 物件直接設定，或須透過 Coupled Field 專屬物件設定，**待 api_search 查證**，嚴禁在腳本中假設或捏造屬性名稱。
- 落地前建議先以 `api_search` 工具查詢 `ContactRegion` 與 Coupled Field 相關類別下是否存在 `HeatGenerationFactor`、`FrictionHeatFactor` 或類似命名之屬性，確認存在且簽名正確後才編寫自動化腳本。

---

## 三、過度約束根因與 Error 20110 防呆

### 3.1 錯誤機制
在 LS-DYNA 顯式求解器中，若多個 `Rigid` 行為的 Remote Point（或多個獨立剛體約束）同時綁定到同一薄板面或共用網格節點，會觸發：
```
Error 20110: multiple rigid bodies constrain the same node
```
根因是同一節點被兩個以上獨立的剛體自由度方程式重複約束，造成剛度矩陣過度約束而求解器直接終止。此風險並非 LS-DYNA 專屬——在 static/thermal 隱式分析中，相同的物理成因會以「Over-constrained / 奇異矩陣（Pivot Error）」的形式出現，故防呆邏輯通用於三種分析。

### 3.2 防呆策略：強制 `Deformable` Behavior
```python
# LoadBehavior 已查證存在於 Ansys.Mechanical.DataModel.Enums
def guard_screw_remote_points_behavior(remote_points_group, screw_prefix="Scr_RM_"):
    guarded = 0
    for rp in remote_points_group.Children:
        if rp.Name.startswith(screw_prefix) or "SCREW" in rp.Name.upper():
            if rp.Behavior != LoadBehavior.Deformable:
                rp.Behavior = LoadBehavior.Deformable
                guarded += 1
    return guarded
```

適用場景：螺絲孔、跨越多孔位的 MPC 連接、鈑金介面遠端點。`Deformable` 允許節點保留局部自然彎曲模態，避免與其他約束疊加成過度約束。

### 3.3 空集合過濾（防止 Scoping 例外）
```python
def filter_empty_named_selections(all_ns):
    valid, empty = [], []
    for ns in all_ns:
        if ns.Entities.Count == 0:
            empty.append(ns.Name)
        else:
            valid.append(ns)
    return valid, empty
```
任何連接建立函式（Bonded Contact / Joint / Remote Point）均**必須先呼叫此過濾**，避免對空集合 NS 進行 Scoping 操作而中斷整批流程。

### 3.4 求解前全機拓樸健全度檢查
```python
def verify_body_topology(model):
    bodies = model.Geometry.GetChildren(DataModelObjectCategory.Body, True)
    orphan_bodies = []
    for b in bodies:
        if getattr(b, "Suppressed", False):
            continue
        geo = b.GetGeoBody()
        if not geo:
            orphan_bodies.append(b.Name)
    return orphan_bodies  # 非空清單代表存在未正確掛載幾何的孤兒 Body，需人工檢查
```
此檢查為必要步驟而非選項：孤兒 Body（無有效幾何掛載）若未在連接建立前排除，會導致後續 Joint/Contact Scoping 失敗或求解階段的隱性剛體位移。

---

## 四、三種分析類型的防呆差異

| 分析類型 | 過度約束的典型表現 | 防呆重點 |
|---|---|---|
| **static** | Pivot Error（主元為零）、剛體位移警告 | 檢查 Fixed 約束 + Remote Point Rigid 疊加是否重複約束同一自由度 |
| **thermal** | 溫度場求解不收斂或結果出現非物理局部突變 | 確認 Bonded 接觸介面未因過度約束產生虛假熱傳導路徑 |
| **lsdyna_explicit** | `Error 20110`，求解立即終止 | 強制螺絲/鈑金遠端點 `Deformable`，避免多剛體共用節點 |

---

## 五、客觀驗證門檻 (Verification Gates)

1. **接觸對建立成功率**：全機 `Connect Topology*` 2-face NS 中，成功建立 Bonded Contact 之比例須為 100%（扣除確認為非配對 NS 之項目）。
2. **穿透量門檻**：Contact Tool 回報之最大穿透量須 $\le$ 單元尺寸的 1%。
3. **Deformable 覆蓋率**：所有螺絲孔/鈑金介面類 Remote Point 之 `Behavior` 須 100% 為 `Deformable`。
4. **孤兒 Body 數量**：`verify_body_topology` 回報之孤兒清單須為空；非空則視為阻斷性問題，須人工確認後才能繼續求解。
