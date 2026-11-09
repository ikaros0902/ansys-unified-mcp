# LS-PrePost 知識字典

本頁以本機 **LS-PrePost User’s Guide, Release 2026 R1（v261）** 為主，並對照七個已核讀的 v252 官方 HTML。PDF 共 1,070 個實體頁；引用使用 PDF physical page，與正文印刷頁相差 28 頁。PDF／Markdown 的來源 ID 分別為 `ansys_66862a9147907f1b7d6eb8f1`／`ansys_cb764e941f021993991af6a3`；catalog／SQLite 目前均歸 `lsdyna`，可用來源 ID 精確回取。除另註外，以下 v261 主題皆依這兩份本機來源，不能由字典 product 篩選未命中推定正文缺檔。

目前 PDF、同名 Markdown 及 catalog text sidecar 均存在；兩套 Markdown 各有連續 1,070 頁標記，格式分別是 `## PDF Page N` 與 `<!-- page N -->`。來源 SHA-256 與 catalog 相符；extraction manifest 記錄同名 Markdown 為 `existing_different_preserved`，不把兩套文字當成位元相同。原件授權文字仍保留；本頁供本機查閱，團隊分享依來源條款確認。

## v261 CFile 重播、-nographics 與 runc 的界線

GUI 的多數互動會產生命令並記入 `lspost.cfile`；離開後可將該檔另存名稱重播。v261 的三種入口不可混用：

| 入口 | 文件所述行為 | 限制 |
|---|---|---|
| `LS-PrePost c=commandfile -nographics` | 不顯示 GUI，並自動執行命令檔。 | **仍需內部 graphics support，不是真正 headless batch。** |
| `LS-PrePost runc=commandfile` | 不開啟 GUI，在 fully headless batch 環境執行。 | 只支援 non-graphical commands；display、rendering、window manipulation 等圖形操作不支援。 |
| `File → Open → Command File` | 以檔案選擇視窗開啟命令檔，顯示 CFile Dialog。 | 屬 GUI 操作路徑。 |

`-nographics` 不能單憑「沒有視窗」就推定可在沒有圖形支援的主機出圖。執行前仍需核對輸入檔、命令副作用與產品版本；本輪只核對文件，沒有執行命令檔。

v252 §10.1 將 `-nographics` 限於不需要圖形的資料擷取，該頁未列 `runc`；v261 明列 `runc` 與內部 graphics support 的差異。這是兩版文件表述的差別，不能據此判定功能首次出現版本。對照：[v252 Commands](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/lsdyna_prepost/lspp_ug_cmd_index_command.html)。

來源：v261 §10.1，PDF physical **1061**／印刷 1033 頁：[PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=1061)／[逐頁 Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-1061)。`ansys_66862a9147907f1b7d6eb8f1`、`ansys_cb764e941f021993991af6a3`。

## v261 命令檔控制流程與錄製內容

| 命令／設定 | 來源所述用途 |
|---|---|
| `interactive` | 暫交控制權給互動操作。 |
| `resume`／`r`／`esc` | 從互動操作返回命令檔。 |
| `skip` … `endskip` | 略過兩者之間的命令，於 `endskip` 恢復執行。 |
| `cfile pausetime 0.1` | 範例將播放間隔設為 0.1 秒；不是所有流程的建議等待時間。 |
| `Record_orient` | 預設會錄製旋轉等 orientation commands；可在 `Setting → Configuration Settings` 篩除。 |

Command Line 左側可輸入命令，右側顯示上次命令；雙擊可看歷史。手冊的 Basic Command 清單明示只是基本子集，其他語法需查看 GUI 產生的 `lspost.cfile` 與 message window，不宜由選單文字猜命令 token。

來源：v261 §10.2–10.4，PDF physical **1062–1063**／印刷 1034–1035 頁：[PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=1062)／[Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-1062)。來源 ID 同上。

## v261 輸入格式與 Save 覆寫界線

File Open 分別提供 binary plot（`d3plot`、`d3eigv`）、keyword（`*.k`、`*.key`、`*.dyn`）、time history（`d3thdt`）、command（`*.cfile`、`*.ses`、`*.cmd`）、Post.db 與 project 等入口。`LS_DYNA Keyword+D3plot` 會以多選方式同時開啟 keyword 與 d3plot；這些入口處理不同資料，不應把結果檔、模型檔與命令檔混為同一輸入。

`Save Keyword` 及 `Save Project` 會覆寫既有檔；`Save Keyword As`／`Save Project As` 提供另存路徑。來源亦列 `Save Config` 寫 `.lspostrc`，不能由此推定它與其他章節的所有 GUI 設定檔相同。此子題只整理檔案選單契約，未測試檔案相容性或保存／還原結果。

來源：v261 §3.1.1、§3.1.3–3.1.4，PDF physical **43、46**／印刷 15、18 頁：[File Open PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=43)／[Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-43)；[Save PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=46)。來源 ID 同上。

## v261 Fringe 積分點選擇與跨 state 範圍

FriComp 可顯示應變、應力等 scalar component。殼與梁在厚度／截面方向可能有多個 integration points；選分量後可再用 `Low/Mid/Upp/Max/Ave/Min/IPt/BPt` 選資料。來源明示預設 fringe 取可用 integration-point 資料的最大值，因此預設雲圖不能直接當成某一指定層的值。

| Fringe Range | 範圍計算 |
|---|---|
| `Dynamic` | 每個 time state 各算 min/max。 |
| `Static` | 用全部 time states 計算共同的固定 min/max。 |
| `User` | 由使用者輸入 min/max。 |

比較不同 state 的顏色時需先記錄 Range 模式；Dynamic 的同色不代表不同 state 的數值相同。以上只確認資料選擇與顯示範圍，沒有驗證模型結果、單位、材料座標轉換或峰值是否具工程意義。

來源：v261 §6.4.1、§6.4.2.1，PDF physical **661、666**／印刷 633、638 頁：[FriComp PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=661)／[Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-661)；[Range PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=666)。來源 ID 同上。

## v261 Section Plane 的追蹤方式與截面量條件

| 模式 | 幾何追蹤行為 |
|---|---|
| `FixS` | 定義後固定在空間中。 |
| `FixM` | 固定在模型；定義用節點移動時截面可跟著移動。 |
| `Lagr` | 先切出一組單元，再追蹤同一組單元；模型變形後不受限於固定平面。文件稱其最接近 `*DATABASE_CROSS_SECTION`。 |

Section Force 介面可互動定義截面。LS-PrePost 計算截面量需要 d3plot 內的 **shell resultants**；來源說通常有寫入，除非 `*DATABASE_EXTENT_BINARY` 選項將其關閉。這是資料前置條件，不保證任意模型、單元或截面均有可用結果，也不能由「介面可開啟」推定截面力已正確輸出。

來源：v261 §6.2.7.1、§6.2.7.8，PDF physical **551、559**／印刷 523、531 頁：[模式 PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=551)／[Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-551)；[Force PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=559)。來源 ID 同上。

## v261 Separation 的參考 part、投影與殼厚

Measure Distance 範例以**第一個選取的 part** 為參考，將其節點投影至第二個 part。勾選 `Axial` 時沿 x/y/z 軸方向投影；其他方向需輸入並選擇 local system。未勾 `Axial` 時取參考節點至第二 part 的最近投影點。不要把所有模式都簡化成固定沿全域軸投影。

殼模型可用 `T1`／`T2` 納入殼厚，未勾時距離以 mid-surface 計算；`Tracer` 可畫投影線，協助查看投影是否落到預期部位。d3plot 改變 state 時會重新計算 separation。這是文件範例的定義，未在本機量測或核對接觸／穿透結果。

來源：v261 §6.5.4 Sample_3，PDF physical **739**／印刷 711 頁：[PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=739)／[Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-739)。來源 ID 同上。

## v261 設定檔位置與個人偏好

`Settings → Configuration Settings` 管理一般偏好，來源列出 `lsppconf`、`lspplasttouch` 存在 Linux 的使用者 `home/LSTC/LS-PrePost`，或 Windows 的 `%appdata%/LSTC/LS-PrePost`。Toolbar Manager 另管理右方／底部工具列。這兩個檔名不應與 File → Save Config 的 `.lspostrc` 合併成同一設定契約；本頁不推定各檔全部欄位或跨版本可攜性。v252 §2.5 的路徑描述相同。

來源：v261 §2.5，實頁 **39**／印刷 11：[PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=39)／[Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-39)；[v252 Configurations](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/lsdyna_prepost/lspp_ug_ui_configurations.html)。

## v261 General Selection 的範圍與 buffer

選取模式可以是 Pick、Area、Poly、Box、Sphe、Prox、Circ、Frin 或 Plan；`In/Out` 決定區域內／外，`Add/Rm` 決定加入／移除。`Sel1` 只保留一個選取實體；`ID` 接受 node／element／part ID。

| 操作 | 範圍或副作用 |
|---|---|
| `Whole`／`Visible` | 分別選全部實體／目前可見實體，兩者不等價。 |
| `Clear`／`Deselect` | 清全部選取／取消最後選取實體。 |
| `Save`／`Load` | 把選取存到 buffer／從 buffer 載入。 |
| `Reverse` | 反向選取。 |
| `3DSurf` | 僅供 solid elements 的外表面選取。 |

來源：v261 §7.1，實頁 **773–775**：[PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=773)／[Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-773)。這是 GUI selection buffer 的說明，未推定 DataCenter API 的 active／selected 欄位相同。

## v261 Keyword Editing 的 Accept、刪除與 RefBy

Keyword Manager 的卡片表單可建立、修改及刪除 keyword data；欄位說明不包含 Keyword Manual 的全部 extended remarks。藍色 heading 可顯示說明；紅色 dynamic heading 可能在指定值後展開額外卡片。

| 表單操作 | 文件契約 |
|---|---|
| `Accept` | 將變更提交至資料庫；不能把尚未 Accept 的欄位視為已保存。 |
| `Delete/UnDelete` | 標記／取消標記該 card 的刪除狀態。 |
| `NewID`／`Add` | 前者以現有 card 內容和預設值開始新 ID，後者以預設值開始新增。 |
| `RefBy` | 在可用表單查看引用目前 keyword 的 parts；不是所有 card 都有同一入口。 |
| `*Use PARAMETER` | 檢視／指定 keyword 欄位參數；後續求解語義仍需 Keyword Manual。 |

來源：v261 §7.8，實頁 **790–796**：[PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=790)／[Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-790)。

## v261 Renumber 的前處理界線與參照更新

Renumber 只供前處理，可對整體模型、keyword 類型、parts 或指定 node／shell／part 選取進行 Renumber、Offset 或 Fit-in-Range。來源說重編／位移時會更新參照資料；操作前仍需核對選取、from/to range 與 Start ID，並可保存 renumbering log。這不表示既有外部檔案、其他應用程式或未載入模型也會同步更新。

來源：v261 §6.2.6，實頁 **548–550**：[PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=548)／[Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-548)。

## v261 History 的時間解析度與資料選擇

History 顯示 binary results 的時間序列，可選 Global、Nodal、Element、Int Pt、Part、R-Nodal、Scalar 等；可用分量隨載入檔案改變。由 d3plot 畫出的 history 只具有已保存 states 的時間解析度；高解析度應查對應 d3thdt、binout 或 ASCII 輸出是否真的存在，不能從動畫插值補造求解輸出。殼結果還需記錄 `E-Axes`、`Surface` 與 integration point 選擇。

來源：v261 §6.4.3，實頁 **669–671**：[PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=669)／[Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-669)。

## v261 ASCII 與 BinOut 的資料入口

ASCII 介面讀取 nodout、secforc 等由 LS-DYNA 寫出的時間序列；BinOut 則用分支樹瀏覽二進位 database，並可開多檔比較。手冊的 SMP／MPP 檔名例子帶歷史 solver 說明，不能當成所有版本的固定檔案組成。

BinOut 的 `Plot` 畫到目前 XY window，`New` 開新窗，`Padd` 加到目前窗；`Info` 顯示目前選取資訊。Output options 的 `All/None` 管理待寫出分支清單，不代表重新計算或補出不存在的 database branch。

來源：v261 §6.4.5–6.4.6，實頁 **678–679、685–686、695**：[ASCII Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-678)／[BinOut PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=685)／[BinOut Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-685)。

## v261 Output 的範圍、ID、state 與格式限制

Output 可從結果 state 輸出整體／局部模型或指定資料；流體表面輸出要求 d3plot 有 ALE fluid data。下列選項會改變輸出內容，應與檔案一起記錄。

| 選項 | 來源定義 |
|---|---|
| `Active Parts Only`／`Entire Model` | 僅 active parts/elements／整體模型。 |
| `Int.ID`／`User ID` | 輸出 internal／user node、element ID。 |
| `Append`、`St No`、`Curr` | 附加既有檔、指定 state 序列（例 `1:5:2`）、只寫目前 state。 |
| `Scale Factor` | node coordinates／displacements 縮放；僅 Keyword 輸出可用。 |
| `Exclude strain and stress`、`Solid ortho` | 來源列為 dynain ASCII 格式限定；不能套到所有輸出格式。 |

來源：v261 §6.4.13，實頁 **720–724**：[PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=720)／[Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-720)。本頁沒有執行 Write 或確認外部格式相容性。

## v261 XYPlot 保存、顯示與 FFT 視窗

XYPlot 的 `Save` 寫曲線資料；`Print` 是圖像輸出入口。`Close` 關閉 plot window，`Quit` 另將它自記憶體刪除。曲線 Scale 可改 offset／scale，Filter 可改濾波、時間單位與頻率；Save 另有輸出間隔、線性插值、點數及 clip 範圍。這些都是資料處理設定，不能當成原始結果取樣條件。

來源特別指出 `fft`／`fft_radix` **只處理 plot window 目前可見資料**，所以 zoom 會影響 FFT 結果；比較頻譜時應保存可見範圍及處理設定。

來源：v261 §7.11，實頁 **814–822**：[PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=814)／[Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-814)。

## v261 Keyword Check 與 Model Clean 的修改副作用

Keyword Check 可 Recheck、把資訊 Write 到檔案，或由項目打開 Keyword Input Form／Extended Information。`Model Clean` 包含清除 undefined／unreferenced keyword data 及自動可清理項目，`Apply Clean` 會套用清理；因此它屬模型修改，不能和唯讀檢查混為一談。本頁只整理介面行為，不由「檢查通過」推論模型具有物理正確性。

來源：v261 §8.3.1，實頁 **945–948**：[PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=945)／[Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-945)。

## v261 Contact Check、penetration 與 Lock Nodes

Contact Check 分 initial penetration／crossed-edge 與 tied contact；可按接觸定義或 ByParts 檢查。`Thickness` 未切換時採模型厚度；`Ignore` 可略過小於指定值的穿透；`Lock Nodes` 限制修補時不得移動的節點。`Fix` 修正 node-to-surface penetration 並有 Undo；`Flip Node` 是另一個有 Undo 的操作。不能把 GUI 的 Fix 視為接觸設定、網格或求解穩定性已通過驗證。

來源：v261 §8.3.2，實頁 **948–950**：[PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=948)／[Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-948)。

## v261 Run SCL 的檔案選擇與執行入口

§8.7 的 Run SCL 介面以 Script File 輸入路徑，或用 Load 瀏覽；`Run` 執行選定腳本；來源將 `Delete` 描述為刪除選定 scripting file，未實測它是否刪除磁碟原檔，不能推定只是移除清單項目。這一頁只證明 GUI 入口與按鈕行為，不定義 SCL 函式、Python binding 或任意腳本的安全性。

來源：v261 §8.7，實頁 **1003**：[PDF](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.pdf#page=1003)／[Markdown](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-1003)。

## v261 手冊章節導覽與轉換範圍

下表依 PDF bookmarks 列出全部十個技術章節入口；入口齊全不代表每章、公式、圖表或 API 均已整理。PDF 沒有少於 120 字元的頁面或無文字頁面；仍未逐圖／逐表核對辨識品質。

| 章節 | PDF physical page |
|---|---|
| 1. LS-PrePost Overview | [29](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-29) |
| 2. User Interface | [35](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-35) |
| 3. Menus | [41](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-41) |
| 4. Toolbar | [81](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-81) |
| 5. Geometry | [85](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-85) |
| 6. Finite Element | [263](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-263) |
| 7. General Tools | [773](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-773) |
| 8. Application Overview | [849](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-849) |
| 9. Explorer Overview | [1035](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-1035) |
| 10. Command Index | [1061](../ANSYS_Document/LS-DYNA/v261/manuals/Ansys_LS-PrePost_Users_Guide.md#pdf-page-1061) |

## SCL／Python 內部參考與官方文件缺口

Repository skill 將 SCL、`.cfile` 與 Python modules 分開；本機未找到 `lsppscripting` catalog 正文。官方 LSTC 的 [Scripting Command Language and Data Center PDF](https://ftp.lstc.com/anonymous/outgoing/lsprepost/SCLexamples/lsppscripting.pdf) 搜尋快取可讀，但本輪直接擷取回 403，未快取原件，release 未確認。

該快取的印刷頁 177–182 列 `LsPrePost.execute_command`、`switch_state`、`DataCenter.get_data`；state 從 1 起，SCL user/internal ID 轉換描述 internal ID 從 0 起。`cmd_result_get_value` 的 Python 結果封裝未明列，不推定 tuple 位置；`get_data` 的 integration-point 說明和 `Ipt` 列表名稱亦有差異。Python 3.6／3.10 配對是該未定版本文件的說明，不能當成 v261 的固定需求。來源不足時，保留原文差異而不由內部筆記補猜 API 契約。

[Skill](../../agents/skills/structural-mechanics/ansys-ls-prepost/SKILL.md)、[Session／CFile](../../agents/skills/structural-mechanics/ansys-ls-prepost/references/session_and_cfile.md)、[Python module](../../agents/skills/structural-mechanics/ansys-ls-prepost/references/python_module_interface.md)、[Model query](../../agents/skills/structural-mechanics/ansys-ls-prepost/references/model_query.md)、[States／results](../../agents/skills/structural-mechanics/ansys-ls-prepost/references/states_and_results.md)、[GUI SOP](../../agents/skills/structural-mechanics/ansys-ls-prepost/references/gui_result_review_sop.md)、[Model build](../../agents/skills/structural-mechanics/ansys-ls-prepost/references/model_build.md)、[Output／export](../../agents/skills/structural-mechanics/ansys-ls-prepost/references/output_export.md) 是內部來源，不能替代對應版本官方契約。

| 主題狀態 | 仍缺範圍 |
|---|---|
| 三種自動化路徑：`source_limited` | v261 CFile／Run SCL 入口已核實；完整 SCL／Python binding、宿主配對及錯誤契約仍缺可存取版本手冊。 |
| 模型與結果查詢：`source_limited` | 已整理有界 GUI History／ASCII／BinOut／Output；完整 DataCenter field、回傳封裝與版本差異仍未覆核。 |
| GUI 檢視與模型編輯：`source_limited` | 本頁 18 個 v261 有界主題不代表全部建模、幾何、圖表或應用範例覆核。 |
| 官方文件缺口：`source_online_partial` | v261 官方 PDF 已本機索引；七個 v252 HTML 已核讀，但全文未離線快取，scripting PDF 直接擷取仍 403。 |
| CFile 重播與命令列自動化：`complete` | 本輪限定為已核讀 v252 §10.1–10.4 與 v261 對應入口；未執行命令檔或將之擴大為完整 automation API。 |

## v252 官方 HTML 來源與本機索引定位

七個已核讀頁面頁尾均標 **Release 2025 R2**：[User’s Guide](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/lsdyna_prepost/lsdyna_prepost.html)、[Commands](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/lsdyna_prepost/lspp_ug_cmd_index_command.html)、[Command Files](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/lsdyna_prepost/lspp_ug_cmd_index_cmd_file.html)、[Command Line](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/lsdyna_prepost/lspp_ug_cmd_index_cmd_line.html)、[Basic Command](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/lsdyna_prepost/lspp_ug_cmd_index_basic_cmd.html)、[File Menu](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/lsdyna_prepost/lspp_ug_pd-file.html)、[Configurations](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/lsdyna_prepost/lspp_ug_ui_configurations.html)。本輪交付 upsert 恢復其 URL、release 與摘要狀態；沒有聲稱完整 HTML 已加入本機索引。

正式索引現有兩個 v261 官方正文 ID，product 仍為 `lsdyna`；`product=ls-prepost` 主要查本字典與八個內部 skill/reference。搜尋未命中時可用來源 ID 精確擷取。原始文件與 REA 萃取內容未修改；來源頁碼、GUI 文件核讀及 RAG 回取均不能代替產品／求解驗證。


## 2026-11-04：Wave 3 本機來源盤點與限制說明

本機 catalog 沒有 LS-PrePost 產品文件。`sources.csv` 的 17 筆來源中，9 筆有本機路徑；2026-11-07 已確認檔案存在並逐檔計算 SHA-256。其餘 8 筆只有線上摘要，未快取正文，沒有本機正文 hash。舊 source audit 只記來源列數，PDF／HTML 頁面稽核欄位為空，不能據此宣稱全 17 筆 hash 或頁面品質已驗收。詳見 [2026-11-07 來源稽核](../maintenance/knowledge_dictionary_passes/2026-11-07/ls-prepost_source_audit_20261107.json)。未快取或回傳 403 的文件仍列為來源缺口，未推測未核實的 API，也未執行求解。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/ls-prepost_module_conversion_report_20261104.md)。
