# Mechanical 隱式/熱分析殼厚度與截面 API

本手冊涵蓋 ANSYS Mechanical 原生物件屬性路徑（static/thermal/modal 分析），不涉及 LS-DYNA 關鍵字卡片。所有列出之 API 均已於 `docs/api_inventory/mechanical_api.json` 查證存在；未查證項目明確標註「待 api_search 查證」。

---

## 一、殼體厚度指派 (`Body.Thickness`)

**API 狀態**：已查證存在。`Ansys.ACT.Automation.Mechanical.Body.Thickness` 屬性型別為 `Ansys.Core.Units.Quantity`（可讀寫）。

```python
# 一般繁體中文註解：遍歷未抑制 Body，僅對殼體（GeoBodySheet）指派厚度
def assign_shell_thickness_implicit(model, thickness_mm=0.8):
    assigned, skipped = 0, 0
    bodies = model.Geometry.GetChildren(DataModelObjectCategory.Body, True)
    for body in bodies:
        if body.Suppressed:
            skipped += 1
            continue
        geo_body = body.GetGeoBody()
        if geo_body and str(geo_body.BodyType) == "GeoBodySheet":
            body.Thickness = Quantity(thickness_mm, "mm")
            assigned += 1
        else:
            skipped += 1
    return assigned, skipped
```

> [!NOTE]
> `Quantity(value, "mm")` 建構式與 shock-analysis-workflow 既有腳本一致（見 `shock-analysis-workflow/05-section-assignment/references/section_controls_and_shell_thickness.md`），於隱式分析同樣適用，因 `Thickness` 屬性本身與分析類型（static/thermal/modal）無關，僅與 `BodyType` 相關。

### 1.1 殼單元偏移 (Offset Type) — 待 api_search 查證
若需控制殼單元中面偏移方向（Top/Bottom/Middle），`references` 範本中未發現對應 API 直接呼叫範例；若需使用，請先以 `api_search("Thickness Offset ShellOffsetType", product="mechanical")` 查證後再實作，嚴禁憑記憶假設 `ShellOffsetType` 列舉存在。

---

## 二、梁/線體截面指派 (`Model.CrossSections` + `Body.CrossSectionSelection`)

**API 狀態**：已查證存在（來源：NotebookLM「Ansys ACT Developer's Guide Release 2026 R1」，官方 API 參考手冊）。

> [!IMPORTANT]
> 原先標註為「待查證」的 `AddCrossSection()` 經查證**並不存在**；ACT API 並無單一通用建立方法，而是依截面形狀分別提供對應方法，統一掛載於 `Model.CrossSections` 這個 Folder 物件下（`Ansys.ACT.Automation.Mechanical.CrossSections`）。若 `Model` 底下尚無 `CrossSections` 群組，須先呼叫 `Model.AddCrossSections()` 建立。

### 2.1 建立截面：依形狀選用對應方法

| 方法 | 回傳型別 |
|---|---|
| `Model.CrossSections.AddRectangularCrossSection()` | `RectangularCrossSection` |
| `Model.CrossSections.AddCircularCrossSection()` | `CircularCrossSection` |
| `Model.CrossSections.AddCircularTubeCrossSection()` | `CircularTubeCrossSection` |
| `Model.CrossSections.AddChannelCrossSection()` | `ChannelCrossSection` |
| `Model.CrossSections.AddHatCrossSection()` | `HatCrossSection` |
| `Model.CrossSections.AddHollowRectangularCrossSection()` | `HollowRectangularCrossSection` |
| `Model.CrossSections.AddICrossSection()` | `ICrossSection` |
| `Model.CrossSections.AddLCrossSection()` | `LCrossSection` |
| `Model.CrossSections.AddTCrossSection()` | `TCrossSection` |
| `Model.CrossSections.AddUserDefinedCrossSection()` | `UserDefinedCrossSection` |
| `Model.CrossSections.AddZCrossSection()` | `ZCrossSection` |

### 2.2 尺寸屬性：並無通用 `Dim1`/`Dim2`，各形狀獨立命名

API 不採用泛用維度命名，每種截面類別皆有自己的 `Quantity` 屬性組：

- **`RectangularCrossSection`**：`Width`、`Height`
- **`CircularCrossSection`**：`Radius`
- **`CircularTubeCrossSection`**：`InnerRadius`、`OuterRadius`
- **`ChannelCrossSection` / `ICrossSection`**：`Width1~3`、`Thick1~3`
- **`HollowRectangularCrossSection`**：`Width1~2`、`Thick1~4`
- **`LCrossSection` / `TCrossSection`**：`Width1~2`、`Thick1~2`

`CrossSectionType` 列舉型別本身（`Ansys.Mechanical.DataModel.Enums.CrossSectionType`）已於 `docs/api_inventory/mechanical_api.json` 查證存在。列舉成員清單（`Rectangular`、`Circular`、`CircularTube`、`Channel`、`HatBeam`、`HollowRectangular`、`IBeam`、`LBeam`、`MeshBeam`、`Quadrilateral`、`TBeam`、`UserDefined`、`ZBeam`、`UndefinedType`）來源為 NotebookLM 查詢結果，`api_inventory` 僅記錄型別本身未逐一列舉成員值，**成員名稱待 api_search 進一步查證**。此列舉主要用於讀取既有截面類型，建立截面物件時仍以 2.1 節的專用方法為主。

### 2.3 指派截面給線體（梁單元）

```python
# 一般繁體中文註解：建立矩形截面並指派給線體（梁單元）
def assign_beam_cross_section(model, body, width_mm=10.0, height_mm=5.0):
    rect_cs = model.CrossSections.AddRectangularCrossSection()
    rect_cs.Width = Quantity(width_mm, "mm")
    rect_cs.Height = Quantity(height_mm, "mm")
    # 指派屬性為 CrossSectionSelection，非 CrossSection
    body.CrossSectionSelection = rect_cs
    return rect_cs
```

指派屬性為 **`Body.CrossSectionSelection`**（型別 `CrossSection`），非原先假設的 `Body.CrossSection`。相關唯讀屬性：`Body.CrossSectionName`、`Body.CrossSectionArea`、`Body.CrossSectionIYY`、`Body.CrossSectionIZZ`。低階拓撲層（`IGeoBody.CrossSection`）另有獨立屬性，供 CAD 幾何介面直接讀寫，一般 ACT 腳本不需使用。

本技能的 server/機構衝擊/wireline/payment 典型應用以殼體（鈑金件）為主，梁截面為次要分支，預設腳本僅提供殼體路徑的完整實作。

---

## 三、BodyType 判斷與過濾慣例

與 `ansys-mechanical/references/mesh.md`、`shock-analysis-workflow/05-section-assignment` 一致，統一透過：

```python
geo_body = body.GetGeoBody()
body_type_str = str(geo_body.BodyType)  # "GeoBodySheet" 或 "GeoBodySolid"
```

`GetGeoBody()` 已於 `mechanical_api.json` 查證存在（約第 96498 行）。嚴禁用 `body.Dimension` 或其他未查證屬性替代判斷依據。

---

## 四、與熱分析（Thermal）的交叉適用性

殼厚度（`Thickness`）屬性為幾何層級屬性，不隨分析系統（Static Structural / Steady-State Thermal / Modal）切換而改變行為；同一個 `body.Thickness` 寫入後，所有共享該幾何的分析系統（Linked Geometry）皆會套用相同厚度。因此本手冊的隱式路徑程式碼對 static/thermal/modal 三類分析皆通用，無需為每種分析類型重複撰寫指派邏輯。
