# SpaceClaim / PyGeometry 錯誤紀錄

---

## ERR-SC-001: gRPC TLS 警告

**觸發場景**: 使用 PyGeometry 連線 SpaceClaim 時收到警告。

**警告訊息**:
```
UserWarning: Starting gRPC client without TLS on 127.0.0.1:50051. 
This is INSECURE. Consider using a secure connection.
```

**根因**: 本機開發環境使用 `transport_mode='insecure'`，PyGeometry 預設會發出 TLS 警告。

**處理**: 本機環境可安全忽略。若需消除警告：

```python
import warnings
warnings.filterwarnings("ignore", message="Starting gRPC client without TLS")

from ansys.geometry.core import Modeler
m = Modeler(port=50051, transport_mode='insecure')
```

## ERR-SC-002: `rename_object` 不直接支援 Body 重新命名

**觸發場景**: 嘗試透過 PyGeometry `rename_object` 重新命名 Body 但行為不如預期。

**根因**: PyGeometry 的 `geometry_commands.rename_object()` 可能不支援所有物件類型的
重新命名，或需要特定的 object identifier 格式。

**解決方案**: 使用 `design.name` 或直接修改 body 屬性：

```python
design = m.read_existing_design()
if design.bodies:
    body = design.bodies[0]
    # 根據 API 版本嘗試不同方式
    try:
        body.name = "PCB"
    except Exception:
        # 透過 geometry_commands
        m.geometry_commands.rename_object(body.id, "PCB")
```

---

## ERR-SC-003: `read_existing_design` 回傳空設計

**觸發場景**: 連線 SpaceClaim 後呼叫 `m.read_existing_design()` 但沒有任何幾何。

**可能根因**:
1. SpaceClaim 中沒有開啟任何設計
2. 幾何尚未從 Workbench 同步到 SpaceClaim
3. 連線到錯誤的 SpaceClaim 實例

**解決方案**: 確認 SpaceClaim 中有活動的設計，且幾何已匯入。


---

# 原生 SpaceClaim Scripting API（`SpaceClaim.Api.V251`，IronPython 2.7）

以下 ERR-SC-004 起適用於 `/RunScript` 或 ACT 內的原生 API，不是 PyAnsys Geometry。
來源：標準件替換工具開發（2026-10-19）。

## ERR-SC-004: `DesignBody.Name = "x"` 失敗（唯讀屬性）

**解決方案**: 用命令物件改名。
```python
RenameObject.Execute(Selection.Create(body), "NewName")
```
Component、Group 同理。

## ERR-SC-005: `ComponentHelper.SetActiveComponent` 不存在

**錯誤訊息**: `AttributeError: 'type' object has no attribute 'SetActiveComponent'`

**解決方案**:
```python
ComponentHelper.SetActive(comp, None)   # 啟用元件
ComponentHelper.SetRootActive(None)     # 回到根部
```
`comp.SetActive()` 可作為備援。

## ERR-SC-006: `Selection.Empty` 當參數傳入報型別錯誤

**錯誤訊息**: `TypeError: expected ISelection, got builtin_function_or_method`

**根因**: `Selection.Empty` 是方法，沒有加括號就傳入的是函式物件。

**解決方案**: 使用 `Selection.Empty()` 或 `Selection.Create()`。

## ERR-SC-007: `MoveBodiesToComponent` 傳入 Python list 靜默失敗

**現象**: `Selection.Create([b1, b2])` 不報錯，但實體沒有被搬移。

**解決方案**: 逐個 body 呼叫。
```python
for b in bodies:
    ComponentHelper.MoveBodiesToComponent(Selection.Create(b), target_comp)
```

## ERR-SC-008: `BlockBody.Create` 結果沒有 `.Success`

**現象**: 以 `getattr(res, 'Success', False)` 判斷成功，結果永遠為 False，
導致後續流程誤判「BlockBody creation failed」。

**解決方案**: 直接取回傳物件的 `CreatedBody`，其次 `Body`，最後才退回 `root.GetAllBodies()[-1]`。
```python
res = BlockBody.Create(p0, p1)
body = getattr(res, 'CreatedBody', None) or getattr(res, 'Body', None)
```

## ERR-SC-009: `NamedSelection.Create(sel, Selection.Create())` 多載歧義

**錯誤訊息**: `Multiple targets could match: Create(Array[IDocObject]), Create(Array[IScriptSmartVariable]) ...`

**解決方案**: 使用三參數版本，同時指定名稱，不要事後再 rename。
```python
NamedSelection.Create(Selection.Create(bodies), Selection.Empty(), "NS_Std_DIMM_Bodies")
```

## ERR-SC-010: `comp.GetAllBodies()` 回傳空清單

**根因**: Shared / Template 元件的實體掛在 `Template` 下。

**解決方案**: 依序嘗試四種來源，取第一個非空者。
```python
for getter in (lambda: comp.GetAllBodies(),
               lambda: comp.Template.GetAllBodies(),
               lambda: comp.Template.Bodies,
               lambda: comp.Bodies):
    try:
        bodies = list(getter())
    except Exception:
        bodies = []
    if bodies:
        break
```

## ERR-SC-011: 程序在工作管理員看得到，螢幕上卻看不到 SpaceClaim 視窗

**觸發場景**: 由 AI 終端機或背景程序（`Start-Process`、`CreateProcess`、WMI、`.bat`）啟動 SpaceClaim。

**根因**: 程序落在隔離桌面（桌面名稱形如 `exebox-...`），不是使用者的 `WinSta0\Default`。
在這個環境下 `MainWindowHandle = 0`、`EnumWindows` 空白，**不代表視窗不存在**。

**無效做法**: `SetForegroundWindow`、`ShowWindow`、指定 `lpDesktop`、產生 `.bat`。

**解決方案**: 用工作排程器互動模式啟動，詳見
[`ansys-spaceclaim/references/native_session_and_versions.md`](../../ansys-spaceclaim/references/native_session_and_versions.md)
的「GUI 啟動與桌面隔離」。

---

## ERR-SC-012: `UnicodeEncodeError: ('unknown', '\x00', 0, 1, '')`（中文環境物件名稱轉型崩潰）

**觸發場景**: 在中文 Windows / 中文版 SpaceClaim 下，執行腳本時對預設生成的物件名稱（如「設計1」、「實體」、「連接拓撲」）調用 `str(obj.Name)`、`print(obj.Name)` 或未以 UTF-8 寫檔。

**錯誤訊息**:
```
UnicodeEncodeError: ('unknown', '\x00', 0, 1, '')
```

**根因**: IronPython 2.7 內部以 .NET String (UTF-16) 表示字串，當對非 ASCII 物件名稱調用 Python 2 的 `str()` 時，系統會以預設 ASCII 編碼器轉型，遇到中文字元立即丟出 `UnicodeEncodeError`。

**解決方案**:
1. 嚴禁使用 `str(obj.Name)`，改用 `unicode(obj.Name.ToString())` 或封裝安全的字串轉換函式：
   ```python
   def safe_str(val):
       if val is None:
           return u""
       try:
           return unicode(val.ToString())
       except:
           return unicode(str(val))
   ```
2. 寫入日誌檔時必須強制使用 `codecs.open(..., "w", encoding="utf-8")`：
   ```python
   import codecs
   with codecs.open(log_path, "w", encoding="utf-8") as f:
       f.write(safe_str(obj.Name) + u"\r\n")
   ```
3. 物件命名底線：ACT / SpaceClaim 內部所有變數、註解、實體名稱一律強制使用 ASCII/英文。

---

## ERR-SC-013: `BlockBody.Create` 在 Component 環境下的建立與捕捉陷阱

**觸發場景**: 在特定 Component 為 Active 的環境下呼叫 `BlockBody.Create(p0, p1)`，回傳的 `BlockBodyResult.CreatedBody` 為 None，且 `GetRootPart().GetAllBodies()` 只會讀取 Root 層級實體，導致差集捕捉落空。

**根因**:
1. SpaceClaim 在特定上下文下以非同步或事件方式提交實體，`CreatedBody` 屬性不一定即時填充。
2. 若新建立的方塊與既有實體相交或接合，SpaceClaim 預設可能觸發自動布林合併。
3. `GetRootPart().GetAllBodies()` 只取根部 Bodies，子組件內的實體無法藉此比對。

**解決方案**: 採用「確定性建構模式 (Deterministic Construction Pattern)」：
```python
# 1. 先清理根目錄臨時體
for b in list(root.Bodies):
    Delete.Execute(Selection.Create(b))

# 2. 在根部直接建立方塊
BlockBody.Create(p0, p1)

# 3. 立即從 root.Bodies 取出剛建立的唯一實體（此時 root.Bodies 恰好只有 1 個）
new_body = list(root.Bodies)[0]

# 4. 立即將實體移入目標 Component
ComponentHelper.MoveBodiesToComponent(Selection.Create(new_body), target_comp)
```
此模式 100% 確定可重複，不依賴不穩定的 active context。

---

## ERR-SC-014: `Combine.Merge` 合併後賦值 `b.Name = "..."` 報唯讀錯誤

**觸發場景**: 對布林合併 (Combine) 後產生的實體直接修改名稱 `body.Name = "NewName"`。

**錯誤訊息**:
```
AttributeError: can't assign to read-only property Name of type 'DesignBodyGeneral'
```

**根因**: 布林合併後回傳的 `DesignBodyGeneral` 物件，其 .NET 屬性 `Name` 在 IronPython 2.7 映射為唯讀。

**解決方案**: 嚴格使用 SpaceClaim 命令物件重新命名：
```python
RenameObject.Execute(Selection.Create(body), "NewName")
```

---

## ERR-SC-015: SpaceClaim 中文語系「連接拓撲」自動化命名與 Mechanical ACT 契約橋接

**觸發場景**: 使用 `ShareTopologyNamedSelection.FindAndFix(options)` 自動搜尋接觸面時，中文版 SpaceClaim 生成的 Named Selection 命名為「連接拓撲1/2/3」。

**根因**: 下游 Mechanical ACT（如 `Mech_bonded.py`、`bonded_contact_creator.py`）只比對全英文 ASCII 字串 `"Connect Topology"`，且嚴格要求 `len(Location.Ids) == 2`（2-face 契約）。中文「連接拓撲」會被下游直接忽略。

**解決方案**: 幾何建立後自動遍歷 `Window.ActiveWindow.Groups`，將中文名稱重命名為標準 ASCII `Connect Topology <N>`：
```python
ct_index = 1
for g in Window.ActiveWindow.Groups:
    gname = unicode(g.Name.ToString())
    if u"Connect Topology" in gname or u"連接拓撲" in gname or u"拓撲" in gname:
        if len(list(g.Members)) == 2:
            new_name = "Connect Topology " + str(ct_index)
            RenameObject.Execute(Selection.Create(g), new_name)
            ct_index += 1
```

