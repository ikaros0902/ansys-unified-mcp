---
name: ansys-bga-modeling
description: SpaceClaim BGA 錫球陣列與銅箔焊盤（Pad）幾何建模主控手冊。涵蓋球徑、高度、上下焊盤、矩形/交錯陣列與共拓撲（Share Topology）設定。
Use when:
  - 需在 SpaceClaim 快速建立封裝 BGA（Ball Grid Array）錫球 3D 實體模型。
  - 需參數化控制錫球直徑、壓縮高度、上/下銅箔焊盤厚度與直徑。
  - 需依矩形矩陣（Rectangular Grid）或六角交錯（Staggered Grid）批量生成錫球陣列。
  - 需使錫球與主機板/晶片封裝載板精確貼合（Mating Face: Top/Bottom）。
  - 觸發關鍵字 (繁中/En): ansys-bga-modeling, BGA建模, 錫球陣列, 封裝陣列, BGA Ball, Solder Ball Array, BGA Pad.
phase_gate:
  requires: []
  produces: []
---

# SpaceClaim BGA 錫球與陣列幾何建模手冊

本技能規範利用 SpaceClaim API 自動建立半導體封裝與 PCBA 分析所需的 3D BGA 錫球（Solder Balls）及銅箔焊盤幾何模型，支援高密度規則矩陣與交錯陣列生成。

---

## 一、核心操作進入點 (Entry Points)

- **MCP 工具調用**：
  ```python
  await geometry_create_bga_array(
      bga_diameter_mm=0.65,    # 錫球直徑 (mm)
      bga_height_mm=0.51,      # 錫球壓縮高度 (mm)
      low_pad_d_mm=0.50,       # 下焊盤直徑 (mm)
      low_pad_h_mm=0.02,       # 下焊盤厚度 (mm)
      high_pad_d_mm=0.50,      # 上焊盤直徑 (mm)
      high_pad_h_mm=0.02,      # 上焊盤厚度 (mm)
      n_dir1=10,               # X 向球數
      n_dir2=10,               # Y 向球數
      pitch_dir1_mm=1.0,       # X 向間距 (mm)
      pitch_dir2_mm=1.0,       # Y 向間距 (mm)
      array_type=0             # 0: 規則矩陣, 2: 交錯陣列
  )
  ```
- **IronPython 腳本路徑**：
  - 單顆球建模：`scripts/bga_ball_creator.ironpy`
  - 陣列生成器：`scripts/bga_array_creator.ironpy`

---

## 二、BGA 建模標準流程 (Standard SOP)

```mermaid
flowchart TD
    S1[1. 參數設定<br/>確認錫球直徑 D、高度 H 與上下焊盤尺寸] --> S2[2. 基準單球成形<br/>於 (0,0,0) 建立主錫球與上下同軸圓柱 Pad]
    S2 --> S3[3. 接合面定向<br/>指定 Mating Face 為 Top 或 Bottom]
    S3 --> S4[4. 陣列複製與位移<br/>依 N1xN2 與 Pitch1/Pitch2 批量矩陣位移複製]
    S4 --> S5[5. 裝配體整合<br/>移動至封裝組件或設定 Share Topology]
```

### 1. 單顆錫球與焊盤構建
- 以球體 `Body.CreateSphere` 建立基礎錫球，並截切指定高度成鼓狀（Spheroid）。
- 於頂部與底部附加薄圓柱實體作為電路板（PCB）與封裝載板（Substrate）之微小焊盤。

### 2. 陣列排列模式
- **Mode 0 (矩形陣列)**：$X_i = i \times \text{pitch}_1$，$Y_j = j \times \text{pitch}_2$。
- **Mode 2 (交錯陣列)**：奇數列 $X$ 向偏移 $0.5 \times \text{pitch}_1$，適用於高密度三角蜂巢排布。

---

## 三、工程參數對照 (Parameter Reference)

| 參數名稱 | 典型數值 (mm) | 說明 |
| :--- | :--- | :--- |
| `bga_diameter_mm` | `0.40 ~ 0.76` | 錫球自由外徑 |
| `bga_height_mm` | `0.30 ~ 0.60` | 回焊後 Stand-off 高度 |
| `low_pad_d_mm` | `0.35 ~ 0.55` | PCB 端焊盤直徑 |
| `high_pad_d_mm` | `0.35 ~ 0.55` | 晶片載板端焊盤直徑 |
| `pitch_dir1_mm` | `0.80 ~ 1.27` | 陣列中心距 |

詳細說明請參閱 [`references/bga_parameters.md`](references/bga_parameters.md)。

---

## 四、工程禁忌與注意事項 (Don'ts)

- **嚴禁焊盤厚度設為 0 時建立實體**：若無實體焊盤需求，厚度參數必須設為 0，避免產生退化幾何。
- **避免陣列規模過大導致記憶體溢位**：若球數超過 2,000 顆，建議於 SpaceClaim 啟用批次複製或分區管理。
