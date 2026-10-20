# 工作階段與獨立元件匯出

以下 API 路徑於 2026-10-20 的 SpaceClaim V251 GUI 與 PyAnsys Geometry 客戶端實測；不同版本要重新核對。

## 以實際模型驗證連線

曾發生 MCP 回報 Discovery v242／Godzilla 2,546 bodies，但目前埠實際屬於 V251，已載入 Interstellar 5,123 bodies。`geometry_launch` 的重新連線又回報 `'str' object has no attribute 'text'`，舊清單仍存在。這些是當時包裝層的觀察，不代表所有版本都有相同缺陷。

先以既有工具查詢；有矛盾時使用全新客戶端查作用中原生文件。Windows 可唯讀核對 `Get-NetTCPConnection` 的 `OwningProcess`，再讀 `Win32_Process` 的執行檔路徑。受限沙箱曾讓 CIM 查詢失敗與本機連線逾時；在允許的執行上下文查詢即成功，不能據此推論服務位於另一個網路 namespace。

原生最小探針：

```python
root = GetRootPart()
result = {
    "root": root.GetName(),
    "api_type": str(root.GetType()),
    "bodies": str(root.GetAllBodies().Count),
    "top_components": ";".join(c.GetName() for c in root.Components)
}
```

`Document.Path` 在已載入的 STEP 曾為空值，須用 root、元件階層等證據共同確認來源。`component.Name` 也可能是空字串，當時 `component.GetName()` 才回傳正確名稱；`Content` 可為 `PartGeneral`，未必具有 `.Name`。

## 大型訊息與腳本傳輸

Godzilla 整機 STEP 回傳曾觸發 `427748193 vs. 268435456` 的 gRPC 接收限制。可在客戶端匯入 `ansys.geometry.core` **之前**設定 `PYGEOMETRY_MAX_MESSAGE_LENGTH`，但這不會修改已建立的 MCP 客戶端，也不是無限制提高上限的理由。優先改傳小型腳本及結構摘要，避免整機 payload。

附帶的 CPython helper 可連線使用者指定埠：

```text
python scripts/run_live_script.py --port 50051 --script <absolute-native-script.py>
python scripts/run_live_script.py --port 50051 --script <absolute-native-script.py> --args-json '{"key":"value"}'
```

Windows 預設編碼若為 CP950，讀取繁中 UTF-8 技能或輸出中文說明時，可使用 `python -X utf8 ...`，避免把解碼錯誤誤判為技能內容或連線失敗。

`Modeler(host=..., port=..., transport_mode="insecure", timeout=...)` 連到既有服務；`modeler.run_script_file(path, script_args=..., import_design=False)` 回傳原生 `result` 字典。`import_design=False` 避免為了取小型結果而重新同步整個模型。依版本確認 `run_script_file`；較舊套件可能只有已棄用別名 `run_discovery_script_file`。

helper 的退出碼 0 只代表客戶端呼叫完成；原生腳本若自行捕捉例外，仍可能回傳包含失敗的字典。必須檢查回傳內容與產物驗證，不能以退出碼取代幾何驗收。

若要 secure transport，使用該服務相應的客戶端設定；附帶 helper 僅重現本次已驗證的本機 insecure 連線，不應直接當作遠端服務部署設定。

## 掃描與另存

先從作用中的組立保存 `source_root`，在同一腳本內完成解析，不依賴前一次腳本留下的變數。以元件階層路徑識別代表件；以下 `component` 必須是由完整索引確認的那個元件。

```python
# Run in the native scripting context with a verified component and output path.
import os
source_count = component.GetAllBodies().Count
ComponentHelper.OpenComponentDocument(ComponentSelection.Create(component), None)
opened_bodies = list(GetRootPart().GetAllBodies())
if len(opened_bodies) != source_count:
    raise Exception("Unexpected active part; do not save")
if os.path.exists(output_path):
    raise Exception("Output exists; inspect before replacing")
DocumentSave.Execute(output_path)
```

在本次 V251 中，`ExportComponent.Execute(selection, fileName)` 的 API 確實存在，但使用 general、master 與不同 selection 仍回報 `holders.Count == 0`。改用開啟元件再另存 STEP 才成功；此失敗不能推論 API 在其他情境不可用。

圖片預覽在本次需顯式匯入：

```python
from SpaceClaim.Api.V251 import WindowExportFormat
ViewHelper.ZoomToEntity(BodySelection.Create(GetRootPart().GetAllBodies()))
Window.ActiveWindow.Export(WindowExportFormat.Png, image_path)
```

API 版本須符合已確認的實際服務。GUI 預覽可支持外形分類，但中空五金的照片不足以分辨支柱、壓鉚螺母或精確規格。

## IronPython 執行上下文

ANSYS 內嵌腳本與註解保持 ASCII。回傳字典 `result` 的鍵值使用字串，複雜資料可 `json.dumps` 為值。

此次原生環境遇到兩個作用域問題：

- 在 dict comprehension 中，再用 generator 捕捉其迴圈變數曾得到 `NameError: global name 'term' is not defined`。對搜尋迴圈改用明確的 `for`，避免不同直譯器的巢狀作用域差異。
- `execfile` 載入的檔案曾無法看見頂層可用的 .NET extension methods。改由 `run_script_file` 直接執行頂層腳本。這類 `AttributeError` 不能立即當成 API 類別本身沒有該方法。

## 原生格式的範圍檢查

此次對獨立元件視圖要求另存 `.scdoc`，實際寫出約 924 MB 的 `.scdocx`，包含來源組立資料；回傳成功及目前只顯示一個元件都不足以證明隔離成功。應檢查真正產物、根階層與完整 body 範圍。

`.pmdb` 的可用性／隔離元件寫入在本次沒有完成驗證，不能記錄成「不支援」。需要該格式時另做小型實測。原生另存失敗不改變已成功 STEP 元件擷取的證據。
