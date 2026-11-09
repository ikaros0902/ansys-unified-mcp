# ANSYS 執行期錯誤與除錯指引字典

此頁是**內部案例索引加官方語義核對**。四份案例筆記共有44個編號：IronPython7、Workbench/ACT6、Mechanical11、SpaceClaim/PyGeometry20；筆記沒有逐案連到完整repro、環境快照、測試輸出或官方issue，因此「筆記記載的根因／解法」不能當成跨版本已證實結論。原四個寬泛產品主題改列 `pending_source_review`，另以可核對的官方文件整理有界規則。

本批已保存16份官方HTML正文、2個CPython2.7.18原RST附件及四份內部Markdown的可追溯快照；沒有本模組PDF輸入。內部原筆記不改寫，行號仍是較早筆記快照位置；搜尋時先用案例ID、原始錯誤字串與host/API版本，再看完整來源及本頁後段來源導覽。官方文件語義不等於44個內部案例已逐案重現。


## 1. IronPython 通用限制

來源：[內部原文](../../agents/skills/mcp-foundation/ansys-error-catalog/references/ironpython_general.md)，[來源列](sources.csv#agents_skills_mcp-foundation_ansys-error-catalog_references_ironpython_general)。以下是案例索引與核對事項，均未在本輪重現host錯誤。

| 案例／原文行 | 筆記記載的現象 | 本字典的核對界線 |
| --- | --- | --- |
| `ERR-IP-001`，L8–49 | unqualified exec／free variables SyntaxError | 先分清未指定namespace的exec與qualified exec；來源沒有證明所有closure都禁止。 |
| `ERR-IP-002`，L50–67 | __name__入口未執行 | 記錄實際host與scope值；筆記的<string>不得套到全部版本／執行模式。 |
| `ERR-IP-003`，L68–84 | 組件引用異常 | 保留assembly identity、載入路徑及完整例外；不以吞掉所有例外當成功。 |
| `ERR-IP-004`，L85–117 | 改檔後仍見舊行為 | 核對模組實際路徑、舊reference及callback實例；reload不是完整重啟。 |
| `ERR-IP-005`，L118–141 | print輸出位置差異 | 核對stdout／host log／RPC回傳的不同通道；不是re flags案例。 |
| `ERR-IP-006`，L142–153 | __future__ import位置 | 核對整個模組開頭與docstring；實際host版本尚未重現。 |
| `ERR-IP-007`，L154–175 | re.sub flags關鍵字TypeError | 筆記未記IronPython精確build；CPython2.7官方簽章其實有flags。 |


## 2. Workbench／ACT

來源：[內部原文](../../agents/skills/mcp-foundation/ansys-error-catalog/references/workbench_act.md)，[來源列](sources.csv#agents_skills_mcp-foundation_ansys-error-catalog_references_workbench_act)。以下是案例索引與核對事項，均未在本輪重現host錯誤。

| 案例／原文行 | 筆記記載的現象 | 本字典的核對界線 |
| --- | --- | --- |
| `ERR-WB-001`，L5–29 | _PROJECT_ROOT NameError | 本專案初始化依賴案例；核對最早失敗點，不能當所有ACT的固定全域變數。 |
| `ERR-WB-002`，L30–60 | exec closure SyntaxError | 與IP001相關，先核對呼叫端namespace與實際編譯器錯誤。 |
| `ERR-WB-003`，L61–85 | Created／Changed重複觸發 | 多事件不等於多個完整命令；需核對commandID、檔案完成狀態及實際處理結果。 |
| `ERR-WB-004`，L86–106 | 跨thread存取UI | 先辨認物件owner與host允許的呼叫途徑；無GUI不代表可直接呼叫ACT API。 |
| `ERR-WB-005`，L107–118 | 長迴圈阻塞UI | 記錄哪個thread執行及完整堆疊；不把FileSystemWatcher當通用替代品。 |
| `ERR-WB-006`，L119–139 | target invocation通用外層錯誤 | 查InnerException／完整traceback，不能由文字直接判定NameError根因。 |


## 3. Mechanical scripting

來源：[內部原文](../../agents/skills/mcp-foundation/ansys-error-catalog/references/mechanical_scripting.md)，[來源列](sources.csv#agents_skills_mcp-foundation_ansys-error-catalog_references_mechanical_scripting)。以下是案例索引與核對事項，均未在本輪重現host錯誤。

| 案例／原文行 | 筆記記載的現象 | 本字典的核對界線 |
| --- | --- | --- |
| `ERR-MECH-001`，L5–26 | Sizing／Method為Under Defined | 核對控制項Scoping、實體型別與有效IDs；圖示本身不足以唯一判定原因。 |
| `ERR-MECH-002`，L27–41 | Quantity NameError | 依執行host／API版本確認名稱注入與import，不把一種namespace當普遍必需。 |
| `ERR-MECH-003`，L42–55 | SelectionTypeEnum NameError | 核對同版API namespace與實際可見symbol。 |
| `ERR-MECH-004`，L56–80 | connection refused | 先核對既定server、host、port、啟動日誌與readiness；不盲猜多個port。 |
| `ERR-MECH-005`，L81–100 | __main__ guard未執行 | __name__是筆記觀察，未驗證所有remote／embedded模式。 |
| `ERR-MECH-006`，L101–121 | Transaction import失敗 | 不以空context manager冒充transaction語義；先核對API版本與所需功能。 |
| `ERR-MECH-007`，L122–142 | 多個Mechanical實例難區分 | 依已授權連線取得product/session證據；port不等於分析系統識別。 |
| `ERR-MECH-008`，L143–154 | DataModel物件沒有Id | 區分幾何ID與樹物件識別；每個實際型別仍須查同版API。 |
| `ERR-MECH-009`，L155–166 | MethodType無QuadTri | 對Sheet／Solid與枚舉支援仍需版本驗證，未採用一律MultiZone規則。 |
| `ERR-MECH-010`，L167–180 | MeshData存取層級錯誤 | 核對接收物件與同版公開路徑，不盲試多條路徑。 |
| `ERR-MECH-011`，L181–193 | 新增控制項與資料夾結構 | 確認實際Parent／Tree後處理；未把筆記的folder API視為通用保證。 |


## 4. SpaceClaim／PyAnsys Geometry

來源：[內部原文](../../agents/skills/mcp-foundation/ansys-error-catalog/references/spaceclaim_pygeometry.md)，[來源列](sources.csv#agents_skills_mcp-foundation_ansys-error-catalog_references_spaceclaim_pygeometry)。以下是案例索引與核對事項，均未在本輪重現host錯誤。

| 案例／原文行 | 筆記記載的現象 | 本字典的核對界線 |
| --- | --- | --- |
| `ERR-SC-001`，L30–51 | insecure gRPC／TLS警告 | 警告表示transport條件；不以本機位址推定可安全忽略，也不先隱藏警告。 |
| `ERR-SC-002`，L52–74 | PyGeometry body改名不如預期 | 先分SDK版本、objectID及原生／client API；筆記有多種猜測，未晉升固定解法。 |
| `ERR-SC-003`，L75–93 | read_existing_design空回傳 | 核對活動design、同步及實例；空結果不證明唯一根因。 |
| `ERR-SC-004`，L94–101 | 原生DesignBody.Name不可指定 | 保留實際型別與API版本，RenameObject路徑為待同版驗證的內部案例。 |
| `ERR-SC-005`，L102–112 | SetActiveComponent不存在 | 核對同版ComponentHelper與方法簽章；不混用PyGeometry。 |
| `ERR-SC-006`，L113–120 | ISelection與method物件型別錯誤 | 辨認方法本身與呼叫結果，仍需確認正確多載。 |
| `ERR-SC-007`，L121–130 | MoveBodiesToComponent無實際搬移 | 核對selection元素、回傳與模型變更，不只看未拋錯。 |
| `ERR-SC-008`，L131–141 | BlockBody結果無Success | 核對回傳型別及CreatedBody／Body；不能任取root最後一個body當新結果。 |
| `ERR-SC-009`，L142–150 | NamedSelection多載歧義 | 保存實際argument型別與候選簽章，再查同版多載。 |
| `ERR-SC-010`，L151–168 | Component查body為空 | 區分instance/template/root範圍；空結果不證明無幾何。 |
| `ERR-SC-011`，L169–183 | process存在但GUI不可見 | 核對桌面／session／window evidence；不把MainWindowHandle=0當確定根因。 |
| `ERR-SC-012`，L184–215 | UnicodeEncodeError | 保存原Unicode與encoding路徑，避免無依據ASCII轉碼造成名稱資料損失。 |
| `ERR-SC-013`，L216–243 | BlockBody建構／active context異常 | 不沿用刪除全部root bodies的修復腳本；先保存模型與查實際結果。 |
| `ERR-SC-014`，L244–261 | Combine後Name唯讀 | 核對Combine結果型別及同版rename方法；不是所有body.name規則。 |
| `ERR-SC-015`，L262–281 | 中文Named Selection未被下游識別 | 這是特定下游名稱／2-face契約，不能推定所有共享拓撲規則。 |
| `ERR-SC-016`，L282–308 | 大型design DEADLINE_EXCEEDED | timeout只表示截止時間到期；三分鐘固定值與拓撲大小因果尚無重現證據。 |
| `ERR-SC-017`，L309–339 | Direction缺Dot | 保留實際型別／版本；不要用except-return-True跳過幾何檢查。 |
| `ERR-SC-018`，L340–358 | Frame.DirZ與拓撲法向疑義 | 核對面定向／評估API；筆記的80–90%比例不是通用統計或校準。 |
| `ERR-SC-019`，L359–376 | ThickenFaces成功旗標但缺結果 | 核對實際拓撲／selection及幾何有效性；R<t/2、80%面數、20mm²皆不可當普遍門檻。 |
| `ERR-SC-020`，L377–409 | GetRootPart／MM NameError | 核對host注入scope、API版本與單位；不把None或固定換算fallback當操作成功。 |


## 5. 查詢方式與可信度

先保存完整traceback（含InnerException）、host、產品release、SDK/assembly版本、呼叫的實際型別／方法簽章、已連線的實例及輸入檔狀態。相同錯誤文字可能有不同根因；「未拋例外」「回傳空字串」「Success=True」也各自需要對應的後置結果，不能互換。

此頁移除先前可執行修復範例：不吞掉所有AddReference錯誤，不用空Transaction或無GUI直接呼叫代替所需語義，不掃描猜測port，不刪除root幾何作為建構fallback，也不隱藏TLS警告作為安全判定。這些移除不改動原筆記，仍可從案例ID追查舊說法。`ERR-IP-005`實為print案例；re flags是`ERR-IP-007`。

來源完整性仍 `source_limited`：內部案例待同版repro；下列官方文件只證明自身平台的語義，不證明每個ANSYS host的實際行為。


## 6. Python 2.7 unqualified exec 與 namespace

CPython2.7.18 reference對含free variables的巢狀scope限制未指定namespace的exec；明確指定namespace是文件列出的例外。它不是「任何exec與任何nested function都衝突」的通則，也不能用現行CPython3的語法替IronPython2.7驗證。內部IP001/WB002若仍重現，應保存實際exec形式與host build再查。

來源：[CPython2.7.18原始文件](https://raw.githubusercontent.com/python/cpython/v2.7.18/Doc/reference/executionmodel.rst)，[來源列](sources.csv#official_error_python27_execution)。

## 7. Python 2.7 re flags 與實作版本

CPython2.7.18文件的`re.sub`簽章有`count=0, flags=0`，並記錄flags在2.7加入；`re.split`亦有相同版本說明。內部IP007的IronPython TypeError可能屬特定實作／build差異，但筆記未記足版本，不能改寫成「Python2.7都沒有flags」。行內flag或compiled pattern應按實際host最小案例核對，不在此宣稱通用修復已驗證。

來源：[CPython2.7.18 re文件](https://raw.githubusercontent.com/python/cpython/v2.7.18/Doc/library/re.rst)，[來源列](sources.csv#official_error_python27_re)。

## 8. Python 2.7 reload 的外部綁定與舊實例

`reload`重執行模組層級程式，但保留原module dictionary；新版未重新定義的舊名稱可能仍在。外部reference、`from module import name`取得的名稱及舊class instances不會自動改綁新物件。因此reload成功不能單獨證明所有callbacks／事件handlers已更新，也不是所有內建或extension module都適合重載。

來源：[Python2.7.18 reload](https://docs.python.org/2.7/library/functions.html#reload)，[來源列](sources.csv#official_error_python27_reload)。

## 9. FileSystemWatcher 多事件與遺漏事件

官方說明一般檔案操作可能產生多個Changed／Created等通知，其他軟體也可能增加通知；一個事件不能直接等同一個完成命令。短時間大量變更還可能使buffer overflow而遺漏事件；只有鎖加記憶體set的範例不足以證明exactly-once處理。核對實際完成／失敗結果及事件來源，並保留Error／overflow證據。

來源：[Changed remarks](https://learn.microsoft.com/en-us/dotnet/api/system.io.filesystemwatcher.changed?view=netstandard-2.0)、[FileSystemWatcher remarks](https://learn.microsoft.com/en-us/dotnet/api/system.io.filesystemwatcher?view=netframework-4.8)；[來源列](sources.csv#official_error_fsw_class)。

## 10. WPF owner Dispatcher 與同步等待

WPF DispatcherObject關聯建立它的thread／Dispatcher，背景工作不能任意直接改UI物件；官方列出Invoke同步與InvokeAsync非同步途徑，並警告對DispatcherOperation對應Task呼叫Task.Wait可能deadlock。這些WPF規則沒有替ACT指定唯一Dispatcher；更不能由Application.Current為None推定所有host API可在目前thread直接執行。

來源：[WPF threading model](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/advanced/threading-model)，[來源列](sources.csv#official_error_wpf_threading)。

## 11. TargetInvocationException 與 InnerException

此.NET例外包裝經reflection呼叫的方法所拋出的底層例外，底層exception位於InnerException。應保留完整chain、stacktrace和原始型別；僅有「Exception has been thrown by the target」字串不足以唯一判定是哪個NameError、AttributeError或其他host問題，也不能把所有StandardError都映射成同一原因。

來源：[TargetInvocationException](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.targetinvocationexception?view=netframework-4.8)，[來源列](sources.csv#official_error_targetinvocation)。

## 12. gRPC DEADLINE_EXCEEDED／UNAVAILABLE 與重試界線

DEADLINE_EXCEEDED表示截止時間前未完成回覆；會改變狀態的操作可能已在server完成，只是回覆太晚。UNAVAILABLE通常是暫時服務不可用，可評估backoff，但官方明說非idempotent操作未必能安全重試。狀態碼本身不證明固定三分鐘timeout、模型過大或port被佔用；先核對連線端點、deadline、server log及操作後狀態，避免重複建立／改動資料。

來源：[gRPC status codes](https://grpc.io/docs/guides/status-codes/)，[來源列](sources.csv#official_error_grpc_status)。

## 13. PyMechanical remote 回傳值與連線模式

目前stable API說`run_python_script`回傳最後執行statement可轉成字串的值，不能轉換時為空字串；assignment回傳空字串不代表沒有副作用，也不等同完整print輸出。應按API規約區分result、logging與exception details。

官方launch頁區分獨立server/gRPC的remote session與程序內Python.NET的embedding；示例的預設localhost／port10000不是所有已啟動host都共用的契約。先取得既定server的host／port／readiness，再判讀connection refused；不自動連到猜測port或執行未經授權的探測操作。stable網址及文件中的例示產品版本不拿來推定所有SDK／產品release；本批快照另記SDK宣告與原文hash。

來源：[Mechanical API](https://mechanical.docs.pyansys.com/version/stable/api/ansys/mechanical/core/mechanical/Mechanical.html)、[Launching PyMechanical](https://mechanical.docs.pyansys.com/version/stable/getting_started/running_mechanical.html)；[來源列](sources.csv#official_error_pymech_mechanical)。

相關字典：[Workbench](workbench.md)、[Mechanical](mechanical.md)、[SpaceClaim](spaceclaim.md)、[PyAnsys](pyansys.md)。


## 2026-11-04：Wave 1 本機來源盤點與限制說明

本批完成 ANSYS 錯誤目錄（Error Catalog）跨產品 14 筆 sources 清冊與 44 項錯誤模式（涵蓋 IronPython 2.7 陷阱、Workbench/ACT 多執行緒與 FileSystemWatcher、Mechanical 腳本 Scoping 與連線超時、SpaceClaim / PyGeometry 拓撲異常、TargetInvocationException 與 gRPC 狀態碼）之系統性盤點核對。各項錯誤排除條目均以具體例外日誌與代碼模式為準；本機未具備各專用 host 實體求解與即時 repro 之主題誠實標記為缺口（保留 5 項既有未完成主題，含 `pending_source_review` 與 `source_limited`），未擅自虛構未核實之錯誤碼或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/error_catalog_module_conversion_report_20261104.md)。


## 2026-11-05 官方正文與案例來源導覽

本批保留官方完整原文與轉換稿，並將四份內部筆記複製為有原始路徑／hash的來源快照。內部案例仍有4個廣泛主題待同版host/repro核對，來源可信度主題仍source_limited；下載成功沒有提升案例根因的證明力。

CPython來源明列2.7.18；PyMechanical兩個stable頁的docsearch:version為0.13.5；theme_version為0.23.0，是網站主題版本而非SDK版本。這些是擷取時文件metadata，未獨立確認為本機SDK或ANSYS產品release，因此索引SDK版本保持unknown。.NET文件的netframework-4.8／netstandard-2.0／windowsdesktop-9.0只是文件view，不能推定ACT host的實際runtime。gRPC網頁未標固定release，版本保留unknown。

| 來源 ID／版本界線 | 本機正文 | 官方 URL／原件 |
|---|---|---|
| `official_error_fsw_changed`／documentation view netstandard-2.0 | [FileSystemWatcher Changed](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_fsw_changed.md) | [官方](https://learn.microsoft.com/en-us/dotnet/api/system.io.filesystemwatcher.changed?view=netstandard-2.0)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_fsw_changed.html) |
| `official_error_fsw_class`／documentation view netframework-4.8 | [FileSystemWatcher class](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_fsw_class.md) | [官方](https://learn.microsoft.com/en-us/dotnet/api/system.io.filesystemwatcher?view=netframework-4.8)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_fsw_class.html) |
| `official_error_grpc_status`／unknown | [gRPC status codes](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_grpc_status.md) | [官方](https://grpc.io/docs/guides/status-codes/)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_grpc_status.html) |
| `official_error_pymech_launch`／unknown | [Launching PyMechanical stable](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_pymech_launch.md) | [官方](https://mechanical.docs.pyansys.com/version/stable/getting_started/running_mechanical.html)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_pymech_launch.html) |
| `official_error_pymech_mechanical`／unknown | [PyMechanical Mechanical stable API](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_pymech_mechanical.md) | [官方](https://mechanical.docs.pyansys.com/version/stable/api/ansys/mechanical/core/mechanical/Mechanical.html)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_pymech_mechanical.html) |
| `official_error_python27_execution`／CPython 2.7.18 | [CPython 2.7.18 execution model](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_python27_execution.md) | [官方](https://docs.python.org/2.7/reference/executionmodel.html)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_python27_execution.html) |
| `official_error_python27_re`／CPython 2.7.18 | [CPython 2.7.18 re.sub flags](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_python27_re.md) | [官方](https://docs.python.org/2.7/library/re.html)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_python27_re.html) |
| `official_error_python27_reload`／CPython 2.7.18 | [Python 2.7.18 reload](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_python27_reload.md) | [官方](https://docs.python.org/2.7/library/functions.html#reload)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_python27_reload.html) |
| `official_error_targetinvocation`／documentation view netframework-4.8 | [TargetInvocationException](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_targetinvocation.md) | [官方](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.targetinvocationexception?view=netframework-4.8)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_targetinvocation.html) |
| `official_error_wpf_threading`／unknown | [WPF threading model](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_wpf_threading.md) | [官方](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/advanced/threading-model)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_wpf_threading.html) |
| `official_error_grpc_deadlines`／unknown | [gRPC Deadlines](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_grpc_deadlines.md) | [官方](https://grpc.io/docs/guides/deadlines/)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_grpc_deadlines.html) |
| `official_error_grpc_retry`／unknown | [gRPC Retry](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_grpc_retry.md) | [官方](https://grpc.io/docs/guides/retry/)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_grpc_retry.html) |
| `official_error_fsw_error`／documentation view netframework-4.8 | [FileSystemWatcher Error event](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_fsw_error.md) | [官方](https://learn.microsoft.com/en-us/dotnet/api/system.io.filesystemwatcher.error?view=netframework-4.8)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_fsw_error.html) |
| `official_error_fsw_buffer`／documentation view netframework-4.8 | [FileSystemWatcher InternalBufferSize](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_fsw_buffer.md) | [官方](https://learn.microsoft.com/en-us/dotnet/api/system.io.filesystemwatcher.internalbuffersize?view=netframework-4.8)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_fsw_buffer.html) |
| `official_error_dispatcher_verifyaccess`／documentation view windowsdesktop-9.0 | [DispatcherObject VerifyAccess](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_dispatcher_verifyaccess.md) | [官方](https://learn.microsoft.com/en-us/dotnet/api/system.windows.threading.dispatcherobject.verifyaccess?view=windowsdesktop-9.0)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_dispatcher_verifyaccess.html) |
| `official_error_exception_inner`／documentation view netframework-4.8 | [Exception InnerException](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_exception_inner.md) | [官方](https://learn.microsoft.com/en-us/dotnet/api/system.exception.innerexception?view=netframework-4.8)；[原件](ANSYS_Document/Error_Catalog/official_body_20261105/official_error_exception_inner.html) |
| `agents_skills_mcp-foundation_ansys-error-catalog_references_ironpython_general`／內部案例；版本unknown | [IronPython 通用限制 internal case notes](ANSYS_Document/Error_Catalog/official_body_20261105/agents_skills_mcp-foundation_ansys-error-catalog_references_ironpython_general.md) | [內部原件](../../agents/skills/mcp-foundation/ansys-error-catalog/references/ironpython_general.md) |
| `agents_skills_mcp-foundation_ansys-error-catalog_references_mechanical_scripting`／內部案例；版本unknown | [Mechanical scripting internal case notes](ANSYS_Document/Error_Catalog/official_body_20261105/agents_skills_mcp-foundation_ansys-error-catalog_references_mechanical_scripting.md) | [內部原件](../../agents/skills/mcp-foundation/ansys-error-catalog/references/mechanical_scripting.md) |
| `agents_skills_mcp-foundation_ansys-error-catalog_references_spaceclaim_pygeometry`／內部案例；版本unknown | [SpaceClaim／PyAnsys Geometry internal case notes](ANSYS_Document/Error_Catalog/official_body_20261105/agents_skills_mcp-foundation_ansys-error-catalog_references_spaceclaim_pygeometry.md) | [內部原件](../../agents/skills/mcp-foundation/ansys-error-catalog/references/spaceclaim_pygeometry.md) |
| `agents_skills_mcp-foundation_ansys-error-catalog_references_workbench_act`／內部案例；版本unknown | [Workbench／ACT internal case notes](ANSYS_Document/Error_Catalog/official_body_20261105/agents_skills_mcp-foundation_ansys-error-catalog_references_workbench_act.md) | [內部原件](../../agents/skills/mcp-foundation/ansys-error-catalog/references/workbench_act.md) |

FileSystemWatcher的Error/緩衝區文件補足事件可能遺漏時的官方入口；WPF VerifyAccess與Exception.InnerException補足thread owner及底層例外鏈的來源，不指定ANSYS host唯一修復方法。gRPC的deadline與retry原文另存，可按實際操作是否改變狀態及server結果核對，不從狀態碼猜唯一根因。

原始HTML、RST、圖像及轉換稿保留在本機gitignored文件區；完整來源可由上表／sources.csv回溯。保留表格、sup/sub、程式碼及原文HTML fallback不代表圖表視覺語意或host範例已驗證。未執行diagnostic scripts、GUI、host、solver或案例重現。
