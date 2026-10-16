# 熱邊界條件 (Thermal Boundary Conditions) 深度規範

本手冊涵蓋 Steady-State Thermal 與 Thermal-Structural 耦合分析中四類熱邊界的 API 施加方式。
結構載荷類（Fixed/Force/Pressure/Bolt Pretension）請見
[`../../ansys-mechanical/references/boundary_conditions_and_loads.md`](../../ansys-mechanical/references/boundary_conditions_and_loads.md)，本文件不重複。

所有 API 成員（`AddConvection`, `AddRadiation`, `AddHeatFlux`, `AddTemperature`, `AddHeatFlow`,
`AddInternalHeatGeneration`）已於 `docs/api_inventory/mechanical_api.json` 核實存在。

---

## 1. 對流邊界 (Convection) — Film Coefficient / HTC

對流邊界需同時指定薄膜係數（Film Coefficient，即對流換熱係數 HTC）與環境溫度：

```python
# Analysis 須為 Steady-State Thermal 或 Transient Thermal 分析系統
analysis = Model.Analyses[0]
conv = analysis.AddConvection()
conv.Name = "外殼對流散熱面"
conv.Location = ExtAPI.DataModel.GetObjectsByName("NS_ENCLOSURE_OUTER_FACES")[0]

# 薄膜係數 (Film Coefficient)，常見自然對流 5~25 W/m^2*C，強制風冷 25~250 W/m^2*C
conv.FilmCoefficient.Output.SetDiscreteValue(0, Quantity("15 [W m^-2 C^-1]"))

# 環境溫度 (Ambient Temperature)
conv.AmbientTemperature.Output.SetDiscreteValue(0, Quantity("25 [C]"))
```

> [!NOTE]
> Film Coefficient 數值需依散熱模式區分：自然對流（Natural Convection）約 5~25 W/m²·°C；
> 強制風冷（Forced Convection）依風速與散熱片設計約 25~250 W/m²·°C。確切數值建議以 Fluent CFD
> 共軛熱傳（CHT）分析或實驗量測回填，不應純憑經驗假設。

---

## 2. 輻射邊界 (Radiation) — Emissivity

輻射邊界需指定表面輻射率（Emissivity，範圍 0~1）與輻射環境溫度：

```python
rad = analysis.AddRadiation()
rad.Name = "外殼表面輻射散熱"
rad.Location = ExtAPI.DataModel.GetObjectsByName("NS_RADIATION_FACES")[0]

# 表面輻射率 (Emissivity)：拋光金屬約 0.05~0.2，陽極處理/塗層約 0.8~0.95
rad.Emissivity.Output.SetDiscreteValue(0, Quantity("0.85 [m^-1 m^-1]"))

# 輻射環境溫度 (Ambient Temperature for Radiation)
rad.AmbientTemperature.Output.SetDiscreteValue(0, Quantity("25 [C]"))
```

> [!CAUTION]
> 輻射散熱在溫差小（< 50°C）或密閉機構內部通常可忽略，僅佔總散熱量 < 5%。
> 僅在高溫（> 100°C）或真空/低對流環境（如太空、密閉真空腔）才需納入輻射邊界，
> 否則會不必要地增加非線性迭代負擔。

---

## 3. 熱流量邊界 (Heat Flux / Heat Flow)

### 3.1 表面熱流密度 (Heat Flux)
作用於單位面積的熱功率密度：

```python
hf = analysis.AddHeatFlux()
hf.Name = "晶片封裝發熱面"
hf.Location = ExtAPI.DataModel.GetObjectsByName("NS_CHIP_TOP_FACE")[0]
hf.Magnitude.Output.SetDiscreteValue(0, Quantity("50000 [W m^-2]"))  # 5 W/cm^2
```

### 3.2 總熱功率 (Heat Flow)
作用於整體面/體的總發熱功率（Watt），常用於已知元件總功耗但面積不均勻的場景：

```python
hflow = analysis.AddHeatFlow()
hflow.Name = "元件總發熱功率"
hflow.Location = ExtAPI.DataModel.GetObjectsByName("NS_COMPONENT_BODY")[0]
hflow.Magnitude.Output.SetDiscreteValue(0, Quantity("3.5 [W]"))
```

### 3.3 體積內熱生成率 (Internal Heat Generation)
作用於整個實體體積，常用於均勻發熱材料（如電阻層、電池）：

```python
ihg = analysis.AddInternalHeatGeneration()
ihg.Name = "均勻發熱體積熱源"
ihg.Location = ExtAPI.DataModel.GetObjectsByName("NS_HEAT_SOURCE_BODY")[0]
ihg.Magnitude.Output.SetDiscreteValue(0, Quantity("1.2e6 [W m^-3]"))
```

---

## 4. 溫度邊界 (Temperature BC)

直接指定幾何面/體的固定溫度，常用於已知邊界溫度（如與定溫熱沉接觸、環境艙控溫）：

```python
temp = analysis.AddTemperature()
temp.Name = "散熱底板固定溫度"
temp.Location = ExtAPI.DataModel.GetObjectsByName("NS_BASEPLATE_BOTTOM_FACE")[0]
temp.Magnitude.Output.SetDiscreteValue(0, Quantity("60 [C]"))
```

> [!IMPORTANT]
> `AddTemperature(DataRepresentation representation)` 確實存在多載簽名（來源：NotebookLM「Ansys ACT Developer's Guide Release 2026 R1」官方 API 參考手冊，`namespace Ansys.Mechanical.DataModel.MechanicalEnums.BoundaryConditions`）。
>
> `DataRepresentation` 列舉**僅有兩個成員**：`Field` 與 `Flexible`，並**不是**原先推測的 `Constant`/`Tabular`。此列舉控制的是 `Magnitude` 屬性讀取時的**回傳物件型別**，而非資料本身的定義方式：
> - `DataRepresentation.Field`：`Magnitude` 回傳 `Field` 物件。
> - `DataRepresentation.Flexible`：`Magnitude` 回傳型別依當前設定動態變化——常數模式回傳 `Quantity`，表格模式回傳 `TabularDataTable`，函式模式回傳運算式字串，Table 指派模式回傳對應 `Table` 物件。
>
> 常數/表格/函式這幾種「資料輸入方式」實際上是透過 `Magnitude.Output.DefinitionType`（`VariableDefinitionType` 列舉，如 `Formula`、`Discrete`）或 Field API 控制，與 `DataRepresentation` 是兩套不同機制，不可混淆。
>
> ```python
> from Ansys.Mechanical.DataModel.MechanicalEnums.BoundaryConditions import DataRepresentation
>
> # Flexible representation lets Magnitude type depend on current configuration
> temp_bc = analysis.AddTemperature(DataRepresentation.Flexible)
> ```
>
> 一般無參數呼叫 `analysis.AddTemperature()`（本文件第 4 節示範的用法）為最常見場景，僅在需要明確控制 `Magnitude` 回傳型別時才需使用 `DataRepresentation` 多載。

---

## 5. Thermal-Structural 耦合注意事項

熱-結構序列耦合（先解熱場、再將溫度場匯入結構分析）之完整流程已在
[`../../ansys-mechanical/SKILL.md`](../../ansys-mechanical/SKILL.md) 第三節「熱應力序列耦合 SOP」定義，
本文件僅聚焦於熱邊界條件本身的 API 施加，不重複耦合流程說明。

---

## 6. 單位制提醒

熱分析建議統一採用 SI 制或 StandardMKS（W, °C, m），嚴禁與結構 LS-DYNA 慣用的 NMM（N, mm, ms, ton）
混用於同一分析系統，避免熱流密度與熱生成率量級錯誤達 10³ 倍以上。
