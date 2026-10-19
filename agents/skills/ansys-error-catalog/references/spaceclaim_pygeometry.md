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
