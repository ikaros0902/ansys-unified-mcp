---
name: ansys-spaceclaim
description: ANSYS SpaceClaim (SCDM) 幾何建模與 Python 腳本自動化技能。涵蓋 PyAnsys Geometry 與原生 SpaceClaim ACT IronPython API 雙軌控制。當需要透過 SpaceClaim 執行 3D CAD 建模、草圖繪製、拉伸、旋轉、組件管理或中面抽取、需在獨立開啟的 SpaceClaim / Discovery 視窗透過 gRPC 執行自訂腳本（`geometry_run_script`）、或需調用 MCP 工具如 `geometry_create_block`、`geometry_get_bounding_box`、`geometry_simplify_ram` 時使用；長度尺寸強制為公尺 (m)，嚴禁重複調用 create_design 創建新設計。觸發關鍵字 (繁中/En): SpaceClaim建模, SCDM腳本, SpaceClaim幾何, 幾何前處理。
---

# ANSYS SpaceClaim 幾何建模與腳本自動化主控手冊

本技能支援透過三種不同的通道驅動 SpaceClaim 幾何：

1. **PyAnsys Geometry (`ansys.geometry.core`) gRPC 原生工具**：透過 MCP `geometry_*` 工具調用（如 `geometry_create_block`、`geometry_get_bounding_box`），適用於現代化 Python 直驅、無主機板 RAM 簡化與尺寸量測。
2. **即時 gRPC 腳本直驅 (`geometry_run_script` / `modeler.run_script_file`)**：透過 Port 50051 的 gRPC 通道直接將 IronPython 2.7 腳本送入獨立開啟的 SpaceClaim / Discovery 視窗執行。**不依賴 Workbench bridge，是獨立 SpaceClaim 視窗執行高階 CAD 操作（如 Share Topology、Combine、裝配體操作）的首選通道**。
3. **Workbench Bridge 路線 (`execute_spaceclaim_script_live`)**：僅適用於從 Workbench 專案啟動並掛載了 journal 輪詢的 SpaceClaim 實例。若為獨立開啟的視窗則 bridge 無法連通，不可走此路徑。

---

## 一、核心設計原則與防呆邊界

> [!CAUTION]
> 1. **通道路由防呆（獨立視窗 vs Workbench 橋接）**：
>    若 SpaceClaim 是使用者直接獨立開啟（監聽於 Port 50051），嚴禁調用 `execute_spaceclaim_script_live` 或依賴 Workbench bridge 的工具；必須走 `geometry_run_script` 或 MCP 原生 `geometry_*` gRPC 工具。
> 2. **嚴禁重複創建新 Design**：
>    一律在當前開啟的作用中設計（Current / Active Design）直接繪製幾何，絕對不要調用 `geometry_create_design()`。
> 3. **嚴格單位換算（公尺 SI 制）**：
>    PyAnsys Geometry 工具尺寸參數強制為公尺 (m)。若使用者給予毫米 (mm)，必須先除以 1000 換算後再傳入。
> 4. **IronPython 編碼安全底線**：
>    腳本內部物件命名、Named Selection 與註解一律全英文 ASCII。嚴禁在中文語系環境下對物件名稱調用 `str()`，必須使用 `unicode(obj.Name.ToString())` 防止 `UnicodeEncodeError`。

---

## 二、模組路由表 (Module Router)

深入操作請查閱 `references/` 對應文件：

### 1. PyAnsys Geometry 路線
| 功能分類 | 參考文件 | 內容說明 |
| :--- | :--- | :--- |
| **連線與 Session** | [`references/session.md`](references/session.md) | Modeler 啟動、連線與 Body 列舉 |
| **2D 草圖繪製** | [`references/sketching.md`](references/sketching.md) | `Sketch` 平面、圓形、多段線與圓弧 |
| **3D 幾何成形** | [`references/modeling.md`](references/modeling.md) | `extrude_sketch`、`revolve_sketch` 拉伸與旋轉 |
| **組件與具名選擇** | [`references/design_and_bodies.md`](references/design_and_bodies.md) | 拓撲樹、元件層級與 Named Selection |
| **模型匯入匯出** | [`references/import_export.md`](references/import_export.md) | STEP / IGES 匯入與導出 |
| **裝配體元件擷取／查表建庫** | [`ansys-spaceclaim-component-library`](../ansys-spaceclaim-component-library/SKILL.md) | 真實工作階段查證、BOM／GUI 分類、開啟元件另存、重新匯入驗證 |

### 2. 原生 SpaceClaim IronPython 路線
| 功能分類 | 參考文件 | 內容說明 |
| :--- | :--- | :--- |
| **API 查證** | `api_search(query, product="spaceclaim")` | 原生 `SpaceClaim.Api.V<ver>.Scripting` 類別/成員存在性查證，避免幻覺 API |
| **版本與 Session** | [`references/native_session_and_versions.md`](references/native_session_and_versions.md) | `SpaceClaim.Api` 載入、單位與更新步進 |
| **實體選擇器** | [`references/native_selection.md`](references/native_selection.md) | `Selection` 拓撲過濾與 `PowerSelection` |
| **特徵與拓撲命令** | [`references/native_commands.md`](references/native_commands.md) | `Midsurface` 中面、`ForceShare` 拓撲共享、`Fill` 填補 |
| **原生草圖** | [`references/native_sketch_and_geometry.md`](references/native_sketch_and_geometry.md) | `SketchRectangle`、`Point2D` 原生幾何建構 |
| **常見錯誤排查** | [`ansys-error-catalog`](../ansys-error-catalog/references/spaceclaim_pygeometry.md) | 唯讀屬性、編碼陷阱與確定性建構模式 |
