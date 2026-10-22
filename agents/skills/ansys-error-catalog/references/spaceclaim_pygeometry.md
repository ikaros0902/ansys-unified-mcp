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

---

## ERR-SC-016: PyGeometry `Modeler.read_existing_design()` 大裝配體 gRPC 逾時

**觸發場景**: 透過 PyAnsys Geometry (`ansys.geometry.core.Modeler`) 連線至已開啟數千個幾何面（如 4~8 個整機薄板件、共 15,000+ 面）的 SpaceClaim 實例，呼叫 `m.read_existing_design()` 或透過 MCP 工具 `geometry_launch` 時。

**錯誤訊息**:
```
grpc._channel._InactiveRpcError: <_InactiveRpcError of RPC that terminated with:
    status = StatusCode.DEADLINE_EXCEEDED
    details = "Deadline Exceeded"
>
```

**根因**:
`read_existing_design()` 會嘗試將 SpaceClaim 記憶體中全部實體拓撲樹（Body、Face、Edge、BoxUV 等）進行完全序列化並透過 gRPC 串流拉回 Python 用戶端。在大型工業裝配體下，序列化與資料傳輸時間極易超過預設的 3 分鐘逾時門檻。

**解決方案**:
對大型模型進行前處理或中面運算時，**嚴禁呼叫 `read_existing_design()`**。改採「指令下發模式」：將 IronPython 腳本寫入暫存檔，直接呼叫 `modeler.run_script_file(script_path, import_design=False)`，在 SpaceClaim 本機記憶體內部完成計算並僅回傳精簡字典或文字摘要：
```python
from ansys.geometry.core import Modeler

m = Modeler(host="127.0.0.1", port=50051, transport_mode="insecure", timeout=30)
# 關鍵：import_design=False 防止同步重型拓撲樹
vals, _ = m.run_script_file("my_processing_script.py", import_design=False)
```

---

## ERR-SC-017: SpaceClaim `Direction` 結構體無 `.Dot()` 方法（法向篩選靜默穿透）

**觸發場景**: 在 SpaceClaim 原生腳本中使用 `DesignFaceExtensions.GetFaceNormal(face, 0.5, 0.5)` 計算對向面夾角，並嘗試呼叫 `.Dot()` 方法。

**錯誤訊息**:
```
AttributeError: 'Direction' object has no attribute 'Dot'
```

**根因**:
`GetFaceNormal()` 回傳的是 .NET 結構體 `SpaceClaim.Api.V***.Direction`，該型別並未實作 `.Dot()` 方法。若開發者將其置於 `try...except` 內且 fallback 為 `return True`：
```python
# 典型反模式 (Anti-pattern)：
try:
    return abs(first_normal.Dot(second_normal)) > 0.99
except:
    return True # 異常被靜默吞掉，法向檢查 100% 遭到穿透！
```
將導致任意同向、垂直或斜向表面均被判定為「平行對向面」，引起嚴重的幾何配對誤判。

**解決方案**:
強制使用分量展開計算向量純量積（Dot Product）：
```python
def are_normals_opposed(n1, n2):
    # n1, n2 為 Direction 或含有 X, Y, Z 的物件
    dot = n1.X * n2.X + n1.Y * n2.Y + n1.Z * n2.Z
    return dot <= -0.999  # 嚴格要求反向平行（180度）
```

---

## ERR-SC-018: `face.Shape.Geometry.Frame.DirZ` 幾何參數法向與有界拓撲向外法向反向陷阱

**觸發場景**: 嘗試透過底層幾何幀 `face.Shape.Geometry.Frame.DirZ` 取得平面的外法向向量，藉此計算兩平面間距與厚度。

**現象**:
計算出的對向距離出現負值或異常偏差；在同一薄板零件中，不同平面計票結果嚴重衝突。

**根因**:
`face.Shape.Geometry.Frame.DirZ` 代表的是該平面底層**未修剪無界參數曲面 (Untrimmed Parametric Surface)** 的局部坐標系 Z 軸，**並不保證指向有界幾何體的外部**。在具備複雜孔洞、折彎或倒角的實際鈑金零件上，**高達 80%~90% 的平面其 `Frame.DirZ` 與拓撲真實向外法向剛好相反（180 度翻轉）**。

**解決方案**:
嚴禁使用幾何幀的 `Frame.DirZ`。必須永遠使用帶有拓撲向外指向的 API：
```python
# 正確：取得拓撲有界面的向外法向向量
outward_normal = DesignFaceExtensions.GetFaceNormal(face, 0.5, 0.5)
```

---

## ERR-SC-019: `ThickenFaces` 偏移面提取機制與微圓角特徵 ($R < t/2$) 幾何自交

**觸發場景**: 為了抽取中曲面，將單側連續面集 `skin_a` 一次性複製為表面片體後，呼叫 `ThickenFaces.Execute(faces, dir_n, MM(-t/2), ThickenFaceOptions())` 進行法向偏移厚化。

**現象**:
- 對一般折彎鈑金件（折彎圓角 $R \ge t/2$），執行成功並生成封閉暫存實體（`Shape.IsClosed == True`），偏移後的完美中面被放置於 `Selection.GetActive()`。
- 對於表面包含微小圓角、沖壓導向斜錐面或小孔倒角（如散熱沖孔圓角 $R = 0.05\text{ mm} < t/2 = 0.5\text{ mm}$）的零件，`ThickenFaces` 回傳 `Success=True` 但未產生實體，`Selection.GetActive()` 亦為空。

**根因**:
當厚化偏移距離超過圓柱面或錐面的曲率半徑時（$\Delta d > R$），幾何內側會產生自相交（Self-intersection），SpaceClaim 內核會中止向內實體化以避免無效幾何。

**解決方案**:
採用**雙軌中面提取演算法 (Dual-Track Engine)**：
1. **Track 1（優先單側厚化提取）**：先嘗試執行 `ThickenFaces(-t/2)`。若 `Selection.GetActive()` 包含大於 80% 的原面數，直接 `Copy.Execute` 提取即獲得 100% 連續無縫單一中面（完美保留所有沖壓階梯與斷差，免除脆弱的布林 Combine）。
2. **Track 2（平滑降級與碎屑自愈）**：若因微特徵自交導致 Track 1 未產出有效面體，自動平滑降級至原生 `Midsurface` 命令。原生指令完成後，自動依表面積過濾清除 $< 20\text{ mm}^2$ 的數十個微小導柱/孔環碎屑面體，保留主要中面。

---

## ERR-SC-020: ACT Wizard 與 IronPython 獨立 Scope 遺失 `GetRootPart()` 與 `MM()` 全域識別碼

**觸發場景**: 腳本在 SpaceClaim 互動式 Script 視窗中執行完全正常，但移植為 ACT Wizard Step Callback（`onupdateStep`）或透過 `execfile()` / 外部模組載入時，拋出 NameError。

**錯誤訊息**:
```
NameError: global name 'GetRootPart' is not defined
NameError: global name 'MM' is not defined
```

**根因**:
`GetRootPart()` 與 `MM()` 是 SpaceClaim 內嵌終端機在全域 scope 中注入的便利巨集函式（Convenience Macro Functions）。在 ACT 外掛回呼或獨立模組命名空間中，這些符號並未自動宣告。

**解決方案**:
建立嚴謹的防禦性取得器（Defensive Getters）：
```python
def _get_root_part(api):
    try:
        return GetRootPart()
    except:
        try:
            # 透過 .NET API 獲取活動文件的主部件
            return api.Window.ActiveWindow.Document.MainPart
        except:
            return None

def _to_meters(val):
    try:
        return MM(val)
    except:
        return float(val) * 0.001
```

