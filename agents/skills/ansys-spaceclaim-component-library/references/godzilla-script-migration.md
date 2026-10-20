# Godzilla 腳本的通用化對照

Godzilla 工作資料夾中的原始腳本保留作為該次操作證據與案例，不是技能依賴。以下對照說明哪些邏輯已抽成可重用流程，以及哪些內容只能作診斷參考。

## 已整理為通用工具

| 原始腳本 | 通用位置 | 使用方式 |
| --- | --- | --- |
| `inspect_tree.py`、`probe_components.py` | `scripts/inventory_components.py` | 傳 `name_contains` 逗號分隔詞，`max_results` 限制回傳量；輸出階層路徑、body 數與子元件數。 |
| `open_component_export.py`、`export_opened_components.py` | `scripts/open_component_export.py` | 傳 `component_path` JSON 字串陣列及絕對 `output_path`；精確階層定位，遇歧義或同名檔就停止。 |
| `export_active_design_step.py` | `ansys-spaceclaim/scripts/export_active_design_step.py` | 傳 host、port、既有輸出目錄；匯出作用中整份設計。 |
| `verify_roundtrip.py`、`finalize_verification.py` | [verification.md](verification.md) | 已抽象成可重用驗證準則；保留逐元件／逐子樹覆蓋要求，不把 Godzilla 的排序位置、名稱及 5% 容差寫成通用通過旗標。 |
| `check_sp7_groups.py` | [verification.md](verification.md) 的 body 數變更處理 | 可借用逐子樹面積覆蓋方法；需按新模型建立來源到匯入群組對應。 |
| `check_standoff_master.py`、`fix_standoff_frame.py` | [verification.md](verification.md) 的座標框架說明 | 保留「master 本地幾何與 occurrence 位置需分開」的判斷；不重用固定 STANDOFF 名稱或假設。 |

執行既有 gRPC 原生腳本範例：

```text
python scripts/run_live_script.py --port 50051 --script scripts/inventory_components.py --args-json '{"name_contains":"FAN,HEATSINK","max_results":"200"}'
python scripts/run_live_script.py --port 50051 --script scripts/open_component_export.py --args-json '{"component_path":"[\"TopAssembly\",\"PartA\"]","output_path":"D:\\Exports\\PartA.step"}'
```

`component_path` 每一段都必須是 GUI／元件索引確認的完整名稱。若同一父元件下同名元件超過一個，腳本會停止；先擴充選擇鍵（例如 occurrence index 或內部 ID）再另存，不能任選第一筆。

## 僅保留為 API 探索記錄

`probe_selection.py`、`probe_metrics.py` 是一次性型別／成員探針。它們沒有穩定輸入介面，回傳 `dir()` 也會依 SpaceClaim 版本改變，故不放入正式執行工具。遇到未知 API 時，先在小型副本查證版本，再把已驗證且可重複的行為納入對應參考。

原始 Godzilla 腳本中的硬編碼工作目錄、元件名稱、body 數、輸出 JSON 欄位索引及 `records[0]`／`records[3]` 都是案例狀態。不要將它們複製成其他裝配體的預設值。逐件結果須獨立判定；body 數變化時要求完整覆蓋證據，而不是只調低檢查標準。
