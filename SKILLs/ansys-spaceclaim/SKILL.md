---
name: ansys-spaceclaim
description: ANSYS SpaceClaim (SCDM) 幾何建模與 Python 腳本自動化技能。涵蓋 PyAnsys Geometry 與原生 SpaceClaim ACT IronPython API 雙軌控制。
Use when:
  - 需透過 SpaceClaim 執行 3D CAD 建模、草圖繪製、拉伸、旋轉或中面抽取。
  - 需生成或執行 SpaceClaim 原生 ACT 腳本（`execute_spaceclaim_script_live`）。
  - 需調用 MCP 工具：`geometry_create_block`、`geometry_create_cylinder` 等。
  - 限制: 長度尺寸強制為公尺 (m)；嚴禁重複調用 create_design 創建新設計。
  - 觸發關鍵字 (繁中/En): SpaceClaim建模, SCDM腳本, SpaceClaim幾何, 幾何前處理.
---

# ANSYS SpaceClaim 幾何建模與腳本自動化主控手冊

本技能支援透過兩種不同的 API 家族驅動 SpaceClaim 幾何：

1. **PyAnsys Geometry (`ansys.geometry.core`)**：透過 MCP `geometry_*` 工具調用，適用於現代化 Python 直驅。
2. **原生 SpaceClaim 腳本 (`SpaceClaim.Api.V<ver>`)**：透過 `execute_spaceclaim_script_live` 調用原生 IronPython API（如 `Selection`, `Midsurface`, `FixImprint`）。

---

## 一、核心設計原則與防呆邊界

> [!CAUTION]
> 1. **嚴禁重複創建新 Design**：
>    一律在當前開啟的作用中設計（Current / Active Design）直接繪製幾何，絕對不要調用 `geometry_create_design()`。
> 2. **嚴格單位換算（公尺 SI 制）**：
>    PyAnsys Geometry 工具尺寸參數強制為公尺 (m)。若使用者給予毫米 (mm)，必須先除以 1000 換算後再傳入。

---

## 二、模組路由表 (Module Router)

深入操作請查閱 `reference/` 對應文件：

### 1. PyAnsys Geometry 路線
| 功能分類 | 參考文件 | 內容說明 |
| :--- | :--- | :--- |
| **連線與 Session** | [`reference/session.md`](reference/session.md) | Modeler 啟動、連線與 Body 列舉 |
| **2D 草圖繪製** | [`reference/sketching.md`](reference/sketching.md) | `Sketch` 平面、圓形、多段線與圓弧 |
| **3D 幾何成形** | [`reference/modeling.md`](reference/modeling.md) | `extrude_sketch`、`revolve_sketch` 拉伸與旋轉 |
| **組件與具名選擇** | [`reference/design_and_bodies.md`](reference/design_and_bodies.md) | 拓撲樹、元件層級與 Named Selection |
| **模型匯入匯出** | [`reference/import_export.md`](reference/import_export.md) | STEP / IGES 匯入與導出 |

### 2. 原生 SpaceClaim IronPython 路線
| 功能分類 | 參考文件 | 內容說明 |
| :--- | :--- | :--- |
| **版本與 Session** | [`reference/native_session_and_versions.md`](reference/native_session_and_versions.md) | `SpaceClaim.Api` 載入、單位與更新步進 |
| **實體選擇器** | [`reference/native_selection.md`](reference/native_selection.md) | `Selection` 拓撲過濾與 `PowerSelection` |
| **特徵與拓撲命令** | [`reference/native_commands.md`](reference/native_commands.md) | `Midsurface` 中面、`ForceShare` 拓撲共享、`Fill` 填補 |
| **原生草圖** | [`reference/native_sketch_and_geometry.md`](reference/native_sketch_and_geometry.md) | `SketchRectangle`、`Point2D` 原生幾何建構 |
