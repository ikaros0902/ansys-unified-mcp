# SpaceClaim 主題字典

本頁按主題說明常見操作與查核重點，供工程師快速定位手冊。已對照 SpaceClaim v251（2025 R1）與 v261（2026 R1）手冊中引用的段落；有差異的項目在主題內標明版本。腳本擴充另有 v261 ACT Customization Guide。

## 主題導覽

### 1. 幾何建模：草圖與約束

草圖約束用來維持幾何關係，例如平行、垂直、相切、等長、對稱或固定。多數約束要選兩個幾何物件：第一個是可能移動的目標，第二個是通常保持位置的錨定物件；水平、垂直和固定約束只需選一個物件。

**操作順序**

1. 在 2D 草圖模式建立幾何，再加入所需約束。
2. 檢查約束的目標與錨定物件，避免不想移動的幾何被當成目標。
3. 若後續要切換成 3D，先保留草圖或另存副本。

草圖約束只在 2D 草圖模式有效；切換到 3D 會刪除既有約束資料。`Retain Sketch` 可保留原草圖，避免草圖被 3D 幾何消耗。這是影響可編輯性的操作條件，不是幾何外觀檢查可以取代的。

v251 與 v261 列出的約束類型及 target／anchor 選取原則相同；手冊內容因排版調整，v251 的約束清單與選取說明分別在第 172–173 頁，v261 在第 171–172 頁。

來源：[v251 手冊，第 4.2.12 節，PDF 第 171–173 頁](../ANSYS_Document/SpaceClaim/v251/manuals/SpaceClaim_Documentation.pdf#page=171)；[v261 手冊，第 4.2.12 節，PDF 第 171–172 頁](../ANSYS_Document/SpaceClaim/v261/manuals/SpaceClaim_Documentation.pdf#page=171)。

### 2. 直接建模：Pull 工具

`Pull` 依選取的面、邊或工具導引執行偏移、圓角、旋轉或定向拉伸。`Select` 導引可偏移面或表面邊，也可對實體邊建立圓角；`Direction` 導引可用直線、邊、軸、原點軸、平面或平面面設定拉伸方向。

**操作順序**

1. 選取目標面、邊或物件。
2. 選擇合適的工具導引；需要固定方向時指定方向參考物件。
3. 在選項面板檢查 `Add`、`Cut` 或 `No Merge` 等行為，再確認結果。

`Add` 只在增加材料時生效；`Cut` 只在移除材料時生效。若拉伸方向與預期相反，先檢查方向導引和預覽結果，再接受操作。

所引用的 Pull guides 與 options 段落在兩版的 PDF 第 234–235 頁逐字一致。

來源：[v251 手冊，第 4.4.2.2–4.4.2.3 節，PDF 第 234–235 頁](../ANSYS_Document/SpaceClaim/v251/manuals/SpaceClaim_Documentation.pdf#page=234)；[v261 手冊，同節，PDF 第 234–235 頁](../ANSYS_Document/SpaceClaim/v261/manuals/SpaceClaim_Documentation.pdf#page=234)。

#### v251／v261 Move 工具導引與 Move Handle

`Move` 的 `Select` 導引預設啟用；`Move Direction` 可指定參考點、線、軸或平面，先定向 Move Handle，但選取參考物件本身不會立即移動幾何。`Anchor` 用來指定 Move Handle 的錨定位置；`Fulcrum` 可讓其他物件繞選定物件移動；`Move radially about axis` 會以所選軸為基準重定向手柄並作徑向移動。

`Move Along Trajectory` 沿選取的線或邊移動，手冊建議分小段操作；若目標是凸起特徵，工具會先分離再重新接合，並自動移除圓角。`Up To` 在選取手柄軸時沿該方向移至參照；沒有選軸時，移動至手柄中心對齊參照。雙擊 `Up To` 可保持導引作用，期間會複製面或表面而非移動它們。`Orient to Object` 則將所選手柄軸旋轉至與參照物件對齊。

手柄直線軸拖曳可平移，弧形旋轉軸拖曳可旋轉；雙擊旋轉軸會旋轉 90°。按住 Ctrl 拖曳可複製再移動；按住 Alt 可顯示手柄間的平面區域供平面內自由移動。中心球或 `Anchor` 可重新定位手柄，旋轉軸上的小球可重定向手柄；按住 Alt 點選點／線也可使最近的直線軸朝向該點或沿該線排列。

**版本核對：**v251 與 v261 第 4.4.3.2–4.4.3.4 節上述 Move guides、options 與手柄操作內容一致，PDF physical pages 均為 289–293；本詞條不涵蓋全部 Move options、patterns 或 beam 專用流程。操作後仍須檢查幾何是否如預期移動、複製或重新接合，特別是 trajectory 操作自動移除 rounds 的情況。

來源：[v251 SpaceClaim Documentation，第 4.4.3.2–4.4.3.4 節，PDF physical pages 289–293](../ANSYS_Document/SpaceClaim/v251/manuals/SpaceClaim_Documentation.pdf#page=289)；[v261 SpaceClaim Documentation，同節，PDF physical pages 289–293](../ANSYS_Document/SpaceClaim/v261/manuals/SpaceClaim_Documentation.pdf#page=289)。

### 3. 布林與流體包絡

`Combine` 以目標物件和切割物件分割或扣除區域。建立外部流體域時，`Enclosure` 會在選取物件外建立帶有間距的實體；手冊列出的形狀包括方盒、圓柱和球體，並指出可用於分析中的流體模擬。

**建立包絡**

1. 在 `Prepare` 頁籤選取 `Enclosure`，再選要包住的實體或 facet body。
2. 設定預設 cushion。它是包絡最小尺寸的百分比，用來決定包絡面與物件的初始距離。
3. 視需要調整方向、各側間距或 `Create share topology`，完成後檢查包絡是否完整包住目標。

`Combine` 可用於建立封閉體積的扣除，也可分割實體。使用 `Make all regions` 時，目標與切割物件必須同為實體或同為表面；先檢查產生的區域，再選要刪除的區域。包絡距離沒有在本文中推定通用倍數，應依分析域、邊界條件及實際模型設定決定。

**版本差異：**v261 的 Combine 工作步驟增加 `Combine tolerance` 設定；v251 對應段落沒有這個步驟。需依目標版本確認可用選項與容差設定。

來源：[v251 Combine 第 4.5.2 節，PDF 第 367–368 頁](../ANSYS_Document/SpaceClaim/v251/manuals/SpaceClaim_Documentation.pdf#page=367)；[v261 Combine 同節，第 368–369 頁](../ANSYS_Document/SpaceClaim/v261/manuals/SpaceClaim_Documentation.pdf#page=368)；[v251 Enclosure 第 13.1.6 節，第 888–889 頁](../ANSYS_Document/SpaceClaim/v251/manuals/SpaceClaim_Documentation.pdf#page=888)；[v261 Enclosure 同節，第 894–895 頁](../ANSYS_Document/SpaceClaim/v261/manuals/SpaceClaim_Documentation.pdf#page=894)。

### 4. 幾何簡化與網格 defeaturing

`Defeature size` 是網格設定。網格產生時，小於或等於此尺寸的特徵會被忽略；這不等同於從 CAD 模型永久刪除幾何。SpaceClaim 也提供 `Delete` 工具，在 blocking 前後抑制選取的邊或頂點。

**使用前檢查**

- 先確認小特徵不影響接觸、流道、薄壁、熱傳路徑或局部應力等分析目標。
- 調整 defeature 或局部抑制後，重新檢查幾何連通性與網格結果。
- 手冊提醒，尖角上的邊或頂點不建議抑制；網格器可能無法可靠移除這類特徵。

`Element size` 是欲生成元素的最大尺寸；`Defeature size` 決定網格時忽略的小特徵尺度，兩者用途不同。不要把其中一個值當成另一個的替代設定。

兩版都說明小於或等於 `Defeature size` 的特徵會在產生網格時忽略，且容差過大可能造成實體無法妥善網格化；引用段落一致，頁碼不同。

來源：[v251 手冊，第 15.4.5 節，PDF 第 977–978 頁](../ANSYS_Document/SpaceClaim/v251/manuals/SpaceClaim_Documentation.pdf#page=977)；[v261 手冊，同節，PDF 第 983–984 頁](../ANSYS_Document/SpaceClaim/v261/manuals/SpaceClaim_Documentation.pdf#page=983)。

### 5. 干涉與幾何檢查

`Measure > Interference` 可檢查物件相交情況。`Curves` 顯示實體交線；`Volumes` 顯示相交體積。需要保留干涉區域作後續檢查時，可用 `Create Volume` 將選取的干涉區建立為新實體。

**檢查順序**

1. 選取要比較的物件。
2. 先看交線，確認干涉位置；再看交集體積，判斷是否需要建立區域實體。
3. 對螺紋等特殊接觸幾何另外核對；手冊明確指出螺紋交集不會回報。

干涉工具只報告幾何交集；沒有交集結果不能單獨證明模型在物理或裝配上正確。

v251 與 v261 都指出螺紋交集不會回報，所引用的 Interference guides 說明相同；頁碼由 v251 的 684–685 移至 v261 的 688–689。

來源：[v251 手冊，第 9.3 節，PDF 第 684–685 頁](../ANSYS_Document/SpaceClaim/v251/manuals/SpaceClaim_Documentation.pdf#page=684)；[v261 手冊，第 9.3 節，PDF 第 688–689 頁](../ANSYS_Document/SpaceClaim/v261/manuals/SpaceClaim_Documentation.pdf#page=688)。

### 6. Python 腳本與擴充

SpaceClaim 內建 Python Script Editor，可用於重複操作。手冊列出 `.scscript` 與 `.py` 檔案；`Record` 可把可腳本化操作寫入編輯器，並支援執行、逐行除錯及輸出視窗中的錯誤／警告訊息。API 細節應查目前安裝版本附帶的 Class Library。

**執行前確認**

- 核對目標 SpaceClaim/SCDM 版本與對應 API 文件；不要把單一版本範例當成跨版本保證。
- 確認腳本使用的長度尺度。手冊列出 Standard、Small、Large 對應的內部長度尺度分別為 m、mm、km。
- 先在副本或可復原的模型上執行會修改幾何的腳本，再檢查輸出視窗與模型差異。

ACT 外掛和內建 Python 腳本是不同擴充途徑；ACT 的事件、載入方式及 API 需另查對應版本的 ACT Customization Guide。

v251 與 v261 對 Script Editor、Smart Variable 選取及 Debug／Run 行為的引用段落一致，頁面位置略有變動。ACT Customization Guide 目前只有 v261 來源，本文不推定 v251 ACT 擴充行為相同。

來源：[v251 手冊，第 4.11.2 節，PDF 第 428–430 頁](../ANSYS_Document/SpaceClaim/v251/manuals/SpaceClaim_Documentation.pdf#page=428)；[v261 手冊，第 4.11.2 節，PDF 第 430–432 頁](../ANSYS_Document/SpaceClaim/v261/manuals/SpaceClaim_Documentation.pdf#page=430)；[v261 ACT Customization Guide](sources.csv#ansys_d0a70592d79d218c1f22ef47)。

#### v261 ACT Extension 載入與 SpaceClaim Wizard 回呼

stand-alone SpaceClaim 可從 Prepare 工具列開啟 ACT Start Page。含 SpaceClaim wizard 的 extension 可放在 `%ANSYSversion_DIR%\scdm\Addins`，或放在 Extension Manager 以齒輪設定加入的其他資料夾；再由 Extension Manager 載入，並從 Wizard launcher 啟動 wizard。若 SpaceClaim 是在 Workbench 中開啟，SpaceClaim 內的 ACT Start Page 沒有 Extension Manager 圖示，extension 管理需改從 Workbench 的 ACT Start Page 進入。

v261 `WizardDemos` 的 `CreateBridge` 範例把 SpaceClaim wizard 定義為兩個 step：`DeckSC` 和 `SupportsSC`；各自的 `onupdate` callback 呼叫 `UpdateDeckSC` 與 `UpdateSupportsSC` 建立甲板和支柱。文件指出 graphics window 會在該 step 的 callbacks 執行後更新。此例說明 extension UI、step 屬性與 callback 的關聯，不代表完整 ACT API 教學；其他 API 變更及限制需查 ACT Developer’s Guide。本指南此處沒有示範在 Workbench 中由 SpaceClaim 頁面管理 extension 的替代操作細節。

來源：v261 *ACT Customization Guide for SpaceClaim*，印刷頁 1、3–5（PDF physical pages 5、7–9）；[本機 PDF](../ANSYS_Document/SpaceClaim/v261/manuals/ACT_Customization_Guide_for_SpaceClaim.pdf#page=5)；[來源清冊](sources.csv#ansys_d0a70592d79d218c1f22ef47)。

## 版本與來源限制

上述主題已對照 v251 與 v261 的引用段落；Combine tolerance 是已確認的版本差異。腳本與擴充中的 ACT 部分只有 v261 指南來源。PDF 頁碼使用原始頁序。完整來源網址、版本和檔案狀態見 [sources.csv](sources.csv)。幾何簡化是否可接受仍取決於模型用途，本文不提供通用尺寸門檻。


## 網格腳本中的 blocking 與 mesh 驗證範例（v261）

SpaceClaim Documentation 實體頁 443 的 Scripting for Meshing 說明網格操作可與幾何操作一起錄製，並建議檢視與修改錄製的腳本。下一頁是圖片而非文字；依頁面圖片目視，範例分別呼叫 `ValidateBlocking.Execute` 與 `ValidateMesh.Execute`，前者傳入 blocking selection、區塊／邊／面／節點／元素計數、quality 與 tolerance，後者傳入 mesh selection、節點與元素計數、quality 與 tolerance。這只描述該圖中的範例；數值不是通用驗證標準，方法簽章與回傳語意尚未以 API 文件或執行確認。

來源：[原 PDF 實體頁 444](../ANSYS_Document/SpaceClaim/v261/manuals/SpaceClaim_Documentation.pdf#page=444)、[前頁 PDF](../ANSYS_Document/SpaceClaim/v261/manuals/SpaceClaim_Documentation.pdf#page=443)，`sources.csv#ansys_b8ba3fd19acac9b1cb341fd0`。原圖中的完整程式未轉寫，未執行。


## 本機 PDF／Markdown 轉換覆核（2026-11-04）

本機 SpaceClaim catalog 固定 8 筆來源：4 個 PDF 與 4 個既有 Markdown，沒有 HTML 或程式附件。8 個原件 bytes SHA-256、索引來源路徑、產品標籤及正值 chunk_count 全部核對；來源清冊共有 9 列，包含 8 個現行 catalog ID 與 1 個保留的 ACT Markdown 歷史 ID。

| 來源 | release 標記 | PDF 實際頁數 | 來源清冊 |
| --- | --- | ---: | --- |
| [Add-in Style Guide](../ANSYS_Document/SpaceClaim/legacy/manuals/Add-in_Style_Guide_2014-11.pdf#page=1) | legacy；封面 November 2014 | 19 | sources.csv#ansys_ec3c93f63a4f5a4dd04bf614 |
| [SpaceClaim Documentation](../ANSYS_Document/SpaceClaim/v251/manuals/SpaceClaim_Documentation.pdf#page=1) | v251；Release 2025 R1 | 1198 | sources.csv#ansys_add762624b7b8137c09a84de |
| [ACT Customization Guide](../ANSYS_Document/SpaceClaim/v261/manuals/ACT_Customization_Guide_for_SpaceClaim.pdf#page=1) | v261 | 18 | sources.csv#ansys_20d7d714e859e82a4f4edd1c |
| [SpaceClaim Documentation](../ANSYS_Document/SpaceClaim/v261/manuals/SpaceClaim_Documentation.pdf#page=1) | v261；Version 2026 R1 | 1205 | sources.csv#ansys_b8ba3fd19acac9b1cb341fd0 |

四份 PDF 共 2,440 頁；cache 的逐頁註記與既有同名 Markdown 的 PDF Page 標題均完整連續。四份既有 Markdown 與 cache 的 bytes 均不同，兩者保留原樣，沒有重轉或覆寫。這只驗證頁碼與來源可追溯；圖片、掃描頁、表格、公式及整份文件的操作／工程語義尚未逐頁驗收，頁碼完整不能取代這些檢查。 cache 文字少於 100 字元的頁面是 legacy 第 1 頁與 v261 Documentation 第 444、926 頁；這是低文字量篩查，不判定它們都是掃描頁。第 444 頁已有上節圖片範例記錄，其餘仍需對照原 PDF。

ACT Markdown 現行 ID 為 `ansys_d0a70592d79d218c1f22ef47`；清冊保留舊 ID `ansys_1e57d29161584cb3b4fc5ea5` 的歷史對照，兩者指向同一路徑，現行索引 hash 與原件相同。這是來源身分對照，不是新增版本。

### 網址清冊與缺口

本機 Markdown 與清冊明列 23 個絕對網址：2 個 Ansys PDF 已有本機原件及 hash；其餘 21 個僅列清冊，包含 4 個舊 HTTP SpaceClaim／Ansys 入口和第三方授權、圖示或資料表來源。沒有找到尚未下載且符合既有官方 fetch allowlist 的技術 HTML 頁面，因此本輪沒有新增網路下載。2 個 PDF 文字抽取網址有句末黏連疑義，未推定更正網址或發送請求；未擷取不等於網站存取失敗。

來源：[本輪來源核對](../maintenance/knowledge_dictionary_passes/2026-11-04/spaceclaim_source_conversion_audit_20261104.csv)、[PDF／既有 Markdown 頁碼核對](../maintenance/knowledge_dictionary_passes/2026-11-04/spaceclaim_pdf_existing_markdown_review_20261104.csv)、[網址清冊](../maintenance/knowledge_dictionary_passes/2026-11-04/spaceclaim_markdown_urls_20261104.csv)。原件、既有轉檔及 CAD 操作均未執行或修改；舊字典工程結論仍須逐條來源覆核。
