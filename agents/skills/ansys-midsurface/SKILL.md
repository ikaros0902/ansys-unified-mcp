---
name: ansys-midsurface
description: >-
  ANSYS SpaceClaim 板金中面抽取（Midsurface Extraction）工程主控手冊與 CLI 自動化工具集。
  涵蓋單側表皮偏置引擎（Single-Skin Continuous Offset）、沉頭孔正規化與邊界自癒（Countersink Normalization & Notch Healing）、
  沖壓折彎舌片與加強肋防破面拓撲補償（Formed Rib/Latch Patching）、板金長厚比防呆（Aspect Ratio Guard）、以及 ACT Wizard UI 佈局規範。
  提供 scripts/ 工具可直接對幾何進行 Aspect Ratio 檢驗、中面拓撲審核與無人值守批次抽取測試。
---

# ANSYS Midsurface Engineering (SpaceClaim & ACT)

## Overview

本技能封裝 ANSYS SpaceClaim (SCDM) 與 ACT 板金中面自動化抽取的全流程架構、拓撲修復工法與品質門禁標準。專門解決板金件中面抽取時常遇到的**破面、特徵遺失、沉孔孔徑異常、端部外輪廓畸變、以及非板金塊體誤判**等工程難題。

核心優勢：
* **單側表皮偏置引擎 (Single-Skin Offset)**：速度比原生 Midsurface 提升 10 倍以上，杜絕無窮面相交崩潰。
* **沉孔正規化與破口自癒 (Countersink & Notch Healing)**：自動收縮大破孔至穿孔小圓徑（$r_{\text{minor}}$），邊界缺口自動補平再重切。
* **沖壓成型特徵拓撲補償 (Formed Features Patching)**：有效辨識加強肋（Bead）與折彎舌片（Latch），縫合成單一連續實體。
* **薄壁縱橫比防呆 (Aspect Ratio Guard)**：強制 $\text{Span} / \text{Thickness} \ge 2.0$，徹底杜絕 2mm 立方體等實心塊誤判為板金。

---

## Dependencies

* **ansys-geometry-core (`ansys.geometry.core`)**：用於透過 gRPC 與本機 SpaceClaim 實例（連接埠 50051）通訊。
* **ansys-spaceclaim**：通用 SpaceClaim 幾何前處理基礎技能。
* **SpaceClaim.Api (`V24` / `V25`)**：IronPython 2.7 內嵌執行環境與 ACT Wizard 擴充外掛。

---

## Quick Start

### 1. 檢驗零件是否滿足薄壁縱橫比（Aspect Ratio Guard）
```bash
# 檢驗 2x2x2 mm 立方體（預期判定為 Solid Bulk Block 並攔截）
python scripts/midsurface_cli.py verify-sheet-metal --thickness 2.0 --span 2.0 --output check_cube.json

# 檢驗 20x20x2 mm 標準板金件（預期判定為 Sheet Metal 並通過）
python scripts/midsurface_cli.py verify-sheet-metal --thickness 2.0 --span 20.0 --output check_plate.json
```

### 2. 審核當前 SpaceClaim 中已抽取之中面品質
```bash
# 連線 SpaceClaim 並檢驗連通性、孔徑與 14.14mm 倒角
python scripts/midsurface_cli.py audit --body-name "SM-LATCH-RACK-STOP-EDR" --output audit_report.json
```

### 3. 無人值守批次中面抽取測試 (Headless Batch Harness)
```bash
python scripts/batch_midsurface_harness.py --target "SM-LATCH-RACK-STOP-EDR" --output harness_report.json
```

---

## Utility Scripts

本技能於 `scripts/` 提供兩大專用 CLI 工具：

| 腳本路徑 | 主要功能與子命令 | 參數說明與範例 |
| :--- | :--- | :--- |
| `scripts/midsurface_cli.py` | `verify-sheet-metal`<br>薄壁長厚比幾何防呆檢驗 | `--thickness` (mm), `--span` (mm), `--area` (mm²), `--min-ratio` (預設 2.0), `--output` (JSON) |
| `scripts/midsurface_cli.py` | `audit`<br>連線審核中面幾何完整性 | `--body-name` (名稱子字串), `--host`, `--port` (預設 50051), `--output` (JSON) |
| `scripts/batch_midsurface_harness.py` | 無 UI 批次中面抽取測試 Harness | `--target` (名稱過濾), `--agent-dir` (SC_midsurface_Agent 目錄), `--output` (JSON) |

---

## Workflow & Execution Pipeline

```mermaid
flowchart TD
    A["輸入實體零件 (Occ or Body)"] --> B["厚度投票 (_vote_thickness_clusters)"]
    B --> C{"板金檢驗 (is_sheet_metal_body_classic)"}
    C -- "未通過 (長厚比<2.0 或非板金)" --> S["標記 SKIP (保留實體，避免誤抽)"]
    C -- "通過 (薄壁板金)" --> D["相切鏈展開 (UG1 / UG2)"]
    D --> E["主引擎：單側表皮連續偏置 (Single-Skin Offset -t/2)"]
    E --> F{"候選評估 (consider_attempt)"}
    F -- "達標 (單一實體 + 面積比 0.9~1.1)" --> G["後處理微調 (正規化與自癒)"]
    F -- "未達標 (缺面或碎片)" --> H["拓撲補償 (Patching) / Fallback 原生重試"]
    H --> G
    G --> I["沉孔正規化 (normalize_countersink_holes)"]
    I --> J["開口槽自癒 (Fill + SplitFace)"]
    J --> K["幾何審核 (Audit) & 賦予厚度屬性"]
```

### Step 1: 厚度偵測與縱橫比防呆
* 透過對立面幾何分析（`_theoretical_offset_mm`）快速投票出最可能板厚。
* 檢驗 $\text{Aspect Ratio} = \frac{\sqrt{\max(A_{\text{skin1}}, A_{\text{skin2}})}}{\text{Thickness}} \ge 2.0$。若長寬與厚度相當（如正方體），強制標記為 Solid 並拒絕抽取。

### Step 2: 單側表皮連續偏置 (Single-Skin Offset)
* 複製外皮面集至根節點，執行 `ThickenFaces -t/2`。
* 複製遠端頂面（Far Cap）並刪除過渡中間體，生成純淨中面曲面。

### Step 3: 沉頭孔正規化與開口自癒 (Countersink & Notch Healing)
* 識別錐頂半角 $\theta \in [30^\circ, 75^\circ]$ 且孔徑 $R \le 6.5\text{ mm}$ 之緊固件沉孔。
* 閉合孔直接透過 `OffsetEdges` 向內精確收縮階差 $\Delta R$。
* 破出外緣之槽口先透過 `Fill` 自動平復邊界，再以 `SplitFace.ByCurves + Delete` 打出穿孔小圓。

### Step 4: 拓撲補償與審核 (Audit & Quality Gate)
* 針對折彎舌片與加強肋等未相切面，透過 `patch_unoffset_skin_faces` 進行補償偏移並與主體 `Combine.Merge`。
* 確保最終中面達到 `components_count == 1`（100% 連續無破面）。

---

## Verification & Quality Gates

在中面抽取流程標記為成功（SUCCESS）前，必須滿足以下四項硬性指標：

1. **單一實體連通性**：`components_count == 1`，杜絕任何游離碎面與開放間隙。
2. **面積覆蓋率門檻**：中面面積與參考外皮面積比率 $\text{Ratio} \in [0.90, 1.10]$。
3. **特徵一致性**：
   - 沉孔 100% 統一為穿孔小圓徑（$r_{\text{minor}}$）。
   - 杜絕 14.14mm 等非預期 45° 倒角斜線（`has_1414 == False`），外凸平滑圓角完全保留。
   - 折彎舌片與加強肋完整存在，無白色矩形空洞破面。
4. **編碼底線**：所有 ACT 內嵌腳本全英文 ASCII 註解，防止 IronPython 解譯器崩潰。

---

## Reference Documentation

深入專題請參閱 `references/` 目錄：
* [`countersink_and_notch_healing.md`](references/countersink_and_notch_healing.md)：沉頭孔判定、孔徑收縮、破口自癒與動態防呆協議。
* [`formed_features_and_latch_patching.md`](references/formed_features_and_latch_patching.md)：沖壓折彎舌片、加強肋與凹坑翻邊補償技術。
* [`sheet_metal_aspect_ratio_guard.md`](references/sheet_metal_aspect_ratio_guard.md)：薄壁長厚比防呆公式與 2x2x2mm 邊界驗證。
* [`wizard_xml_ui_design.md`](references/wizard_xml_ui_design.md)：SpaceClaim ACT Wizard XML 人因介面排版規範。
