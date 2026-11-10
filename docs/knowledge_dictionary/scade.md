# Ansys SCADE 知識字典

> 本目錄含 SCADE 語言、SCADE Suite、SCADE Python／Java-Tcl API，以及 Rapid Prototyper 文件；這些內容並非同一子產品。SCADE One 快捷鍵文件列入來源清冊，但不與 SCADE Suite 語言文件合併。各 PDF 原件保留，逐頁 Markdown 抽取與 PDF page 標記已供索引定位。

## 語言模型：同步資料流與 Clocks

SCADE Language Primer 的 dataflow model 把 flow（stream）定義為指定型別的值序列；每個值對應一個離散 instant。以下詞條整理 Primer physical PDF Pages 13–17 的 flows、temporal operations 與 clocks；state machines、operators 和 array semantics 不在本項完成範圍。

| 概念 | 手冊描述 | 查閱時的重點 |
| --- | --- | --- |
| Flow | 具型別的時間序列，以 instant 索引各時刻的值。 | 確認輸入／輸出型別及 flow 的 clock。 |
| `pre` | 取前一個 instant 的值，形成 one-step delay。 | 首個 instant 沒有前值，因此結果是 undefined；不能把它當作有效初始值。 |
| `->` | flow initialization：第一個 instant 取左運算式，之後取右運算式。 | 常與 `pre` 組合，定義初始值並填補初始 undefined。 |
| `fby(b; n; a)` | 手冊用它表示前述 initialization pattern 的重複形式。 | 範例先輸出 `a` 的初值 n 次，再接上 `b` 的 flow；核對 n 與初始化需求。 |
| `when c` | 以 Boolean clock `c` 從較快 flow 取樣，產生較慢 sub-flow。 | 取樣後的 flow 只在 `c` 為 true 的 instants 有值。 |
| Clock discipline | Point-wise operators 僅能組合同一 clock 的 flows；不同 clock 的值不會被隱式略過或緩衝。 | 要明確表示 sampling；base clock 永遠為 true，base-clock flow 每個 cycle 都存在。 |
| Complementary-flow merge | 可將互補 clocks（例如 `c` 和 `not c`）上的較慢 flows 合併為較快 flow。 | 手冊說明此 primitive 的 clock 引數限 clock identifiers。 |

這些是語言模型與時間取樣規則，不是工程採樣頻率或即時執行效能保證。實際 flow clock、初始化與 node activation 還須按完整 Primer 及目標編譯環境核對。來源：[Language Primer，PDF physical Pages 13–17（printed pages 2-3–2-7）](../ANSYS_Document/SCADE/unknown/archives/LanguagePrimer_SCS-PM-25.pdf#page=13)／[逐頁 Markdown：PDF Page 13](../ANSYS_Document/SCADE/unknown/archives/LanguagePrimer_SCS-PM-25.md#pdf-page-13) · `ansys_b314e9de57e5ed43b09cfe04`。注意官方 SCADE 入口將 `LanguagePrimer_SCS-PM-25.pdf` 鏈結標成「2026 R1」，但 PDF 內版權頁標示 Published October 2024；故本字典依原件日期描述文件，不把入口連結標籤當成該 PDF 的版本，也不推定適用產品 release。

### State machines 與 transitions

SCADE state machine 由 states 組成；每個 state 有自己的 equation set，並為 machine 的 flows 定義該模式下的值。Primer 說明每個 cycle 只有一個 active state。`initial` 標記起始 state；沒有初始狀態的設計不能由這段語法摘要推定其啟動行為。

| Transition | 語法位置與 cycle 語意 | 進入目標 state |
|---|---|---|
| Strong preemption（`unless`） | 寫在 source state body 前；guard 成立時，當前 cycle 的計算改由目標 state 決定。 | `resume` 保留目標 state 內部狀態；`restart` 重設目標 state 的內容，包括 dataflow initialization 與其中的 state machines。 |
| Weak preemption（`until`） | 寫在 source state body 後；source state 先完成當前 cycle，guard 成立則在下一 cycle 切換。 | 同樣可選 `resume` 或 `restart`，其差別是是否保留目標 state 的內部狀態。 |

Primer 另指出同一 state 同時有 strong／weak transitions 時，strong transition 優先，且每 cycle 最多觸發一個 transition。閱讀範例時要分清 `selected state`（檢查 outgoing strong transitions 的 state）與 `active state`（該 cycle 實際生效的 state）；weak 後接 strong 的情況可能使中間 state 未被 activate。這裡僅整理狀態與 transition 時序，未涵蓋 shared memories、pure signals、composition、synchronization、forks 或 transition 上 flow definitions。[Language Primer，PDF physical Pages 37–53（printed Pages 3–27–3–43）](../ANSYS_Document/SCADE/unknown/archives/LanguagePrimer_SCS-PM-25.pdf#page=37)／[逐頁 Markdown：PDF Pages 37–53](../ANSYS_Document/SCADE/unknown/archives/LanguagePrimer_SCS-PM-25.md#pdf-page-37) · `ansys_b314e9de57e5ed43b09cfe04`。產品 release 維持 unknown；例句與時序語意以 Primer 為依據，非目標版本編譯器的執行測試。

### Nodes、functions 與重設實例

Primer 將 node 定義為 SCADE 程式的基本結構單位：介面列出具型別的 inputs／outputs，每個 output flow 由 equation 或 state machine 定義，也可用 local flows 輔助。若定義不引用過去值（例如不含 temporal operators 或 state machines），可宣告為 `function`；這種 combinatorial 性質必須與實際定義一致。使用者自訂 node／function 可以像 primitive 一樣被實例化。

`restart N every c` 會在條件 `c` 成立時重設被實例化 node 及其內部 node instances 的記憶狀態。Primer 指出，node 的第一個 instant 一律視為發生 reset，因此 initialization operator `->` 會先採用其第一個參數；`restart` 對無記憶的 function 沒有作用。這是語言手冊描述，實際程式仍須依完整語法與目標版本檢查。[Language Primer，PDF physical Pages 18–21](../ANSYS_Document/SCADE/unknown/archives/LanguagePrimer_SCS-PM-25.pdf#page=18)／[逐頁 Markdown](../ANSYS_Document/SCADE/unknown/archives/LanguagePrimer_SCS-PM-25.md#pdf-page-18) · `ansys_b314e9de57e5ed43b09cfe04`。

### Node clocks 與 activation

Primer 以三種 activation 行為區分「停用時輸出如何處理」：

| 寫法 | 手冊所述輸出行為 | 查閱重點 |
|---|---|---|
| `(activate N every c initial default d)(e)` | 在未啟動時保留（memorize）前次輸出；首個 cycle 可由 `initial default` 指定值。 | 輸出仍需在每個 local cycle 有值，需有記憶回路。 |
| `(activate N every c default d)(e)` | 未啟動時使用指定 default flows，包括初始 instant。 | 不應誤認為保留前次輸出；條件為 false 時輸出 default。 |
| `(activate N every c)(e)` | 僅在 `c` 為 true 的 clock 上提供輸出。 | 若結果要接到較快 clock 的 flow，必須補全其他 instant，例如用 `merge`。 |

一般 node instance 的 inputs／outputs 須符合 clock discipline；宣告 clock 後，node instance 的執行 clock 依其最快 input clock 決定。`restart` 條件與 node instance clock 不必相同，手冊稱其具有一定程度的 asynchronous reset 語意。以上為 Primer 的構造差異摘要，未在執行環境編譯驗證。[Language Primer，PDF physical Pages 23–28](../ANSYS_Document/SCADE/unknown/archives/LanguagePrimer_SCS-PM-25.pdf#page=23)／[逐頁 Markdown](../ANSYS_Document/SCADE/unknown/archives/LanguagePrimer_SCS-PM-25.md#pdf-page-23) · `ansys_b314e9de57e5ed43b09cfe04`。

### Groups 與外部程式碼

`group` 可讓一個識別名稱代表多個 flows 的型別清單；巢狀 group 展開後，依結構型別比較是否等價。Primer 特別區分 group 與 structured type：implicit grouping 中的 flows 可各自屬於不同 clocks，且不因此建立相依；structured value 則要求各 flows 同一 clock。明確命名的 group 也要求成員 flows 同一 clock；group 不能直接用來定義新的 type。[Language Primer，PDF physical Pages 29–31](../ANSYS_Document/SCADE/unknown/archives/LanguagePrimer_SCS-PM-25.pdf#page=29)／[逐頁 Markdown](../ANSYS_Document/SCADE/unknown/archives/LanguagePrimer_SCS-PM-25.md#pdf-page-29) · `ansys_b314e9de57e5ed43b09cfe04`。

Primer 將 imported code 分成 combinatorial 與 sequential：前者每次對相同當前 input vector 必須回傳相同 output vector；若 C implementation 使用 globals 或 static locals，可能破壞此性質。Sequential imported operator 須可被多個 instances 分別實例化，並可重設；其 instance memory 不應以共享 globals／static variables 實作。整合介面與程序依工具而異，故這些條件是保持確定性與同步語意的設計要求摘要，非本機編譯器檢查結果。[Language Primer，PDF physical Pages 32–33](../ANSYS_Document/SCADE/unknown/archives/LanguagePrimer_SCS-PM-25.pdf#page=32)／[逐頁 Markdown](../ANSYS_Document/SCADE/unknown/archives/LanguagePrimer_SCS-PM-25.md#pdf-page-32) · `ansys_b314e9de57e5ed43b09cfe04`。

## 函式庫與模型設計

SCADE Suite Libraries Manual（Published January 2026）提供隨 SCADE Suite 安裝、可供 SCADE Suite projects 使用的 library operators 概覽。以下分類來自手冊 Fundamentals 章節，適合用來找到後續 operator reference；不代表已列出全部 operator 或其完整 signature。

| Library | 手冊概述的用途 |
| --- | --- |
| `libdigital` | Boolean／數位邏輯運算，例如 edge、flip-flop、truth table。 |
| `libimpl` | 標準整數型別與整數運算；提供多種 integer implementation。 |
| `liblinear` | 線性函數與 filter，例如 derivative、gain、memory、integrator。 |
| `libmath` | 基本數學，以及 vector／matrix operators。 |
| `libmathext` | 三角函數與 power-based operators。 |
| `libpwlinear` | 分段線性函數／filter、counter、dead band、hysteresis、rate limiter 與 lookup table。 |
| `libsmlk` | 依 SCADE Suite formalism 重現 Simulink block 行為，支援 Simulink model import。 |
| `libverif` | 以 SCADE nodes 表達待驗證 properties 的 verification operators。 |

有幾項選用限制要先確認：`libsmlk` 只在安裝 SCADE Suite Simulink Importer 時提供；`libverif` 需要 Design Verifier。手冊說明模型本身 target-independent，資料型別的 implementation choice 在 code build 時才決定；`libimpl` 提供整數型別／函式的多種 implementation。部分 library function 以 C code 實作，手冊以 `libimpl`、`libmathext` 為例提醒可能有 platform dependency。標準安裝路徑為 `<SCADESuiteInstallDirectory>\libraries`。

手冊提醒：若在 qualified／certified context 使用 libraries，end user 仍須依適用 Safety standard 執行所要求的 documentation、verification 和 validation；library 隨產品提供不等於該 library 已自動滿足特定專案認證要求。實際 operator 的型別、clock 和使用條件仍應回到對應 library 章節查核。

來源：[Libraries Manual，PDF physical Pages 22–25（printed pages 1–5）](../ANSYS_Document/SCADE/unknown/archives/LibrariesManual_SCS-LM-26.pdf#page=22)／[逐頁 Markdown](../ANSYS_Document/SCADE/unknown/archives/LibrariesManual_SCS-LM-26.md#pdf-page-22) · `ansys_0dd0b464ab6f67a26baa69dd`。產品 release 仍標示 unknown；文件發布日期不推定成產品版本。

## Python、Java/Tcl APIs 與 Metamodels

三份文件共同提供 API 選路的入口；它們的內容是不同語言及產品的介面導覽，不表示功能完全等價。

| 文件／介面 | 文件目錄明示的範圍 | 適合先查的情況 |
|---|---|---|
| Python API Guide | Python 執行環境與 script setup、ETP 專案內容、Architect／Suite／Display／ARINC 661／Test 模型資料、traceability、code-integration mapping files、專用 SCADE activities、scripting commands、extensions | 以 Python 存取專案或模型資料、執行 SCADE script，或處理文件列出的生成資料／mapping file。先依產品章節核對 API building blocks 與 access mode。 |
| Java API Guide | Eclipse 環境設定；以 Java 讀寫 Architect、Suite、Test、Display、A661 等模型或 procedure，建立元素並儲存 project；Display KCG mapping-file API | 要從 Eclipse-based application 整合或以 EMF model-manipulation tools 操作模型時。依手冊列出的 Eclipse／EMF dependencies 配置；不可從 2026 文件的歷史相依描述推定新版 Eclipse 相容性。 |
| Tcl API Guide | 專用 Tcl commands；依 metamodel diagrams 的 script commands；Script Wizard；手冊另列 predefined operators、feedback、API、GUI-display 與 checker 相關命令 | 需要在相應 SCADE 環境執行 Tcl automation 時。命令名稱和可用產品須回到對應章節確認。 |

Metamodels Technical Reference Card 以 UML 圖列出各產品 model 結構，供進階使用者整合自訂工具。其 overview 指出：部分 Python／Tcl API 可在 GUI（操作記憶體中的 model）或 batch 環境使用；Java API 遵循 Eclipse Modeling Framework（EMF），可供 EMF 層級的通用模型工具操作。圖表按 Architect、Suite（Python／Tcl／Java）、Display、UA Page Creator、Test 與 Traceability 分部；先選產品與語言，再查相應 API Guide 的操作與限制。這些資料未證明三種語言有相同功能、相同寫入語意或可互換的部署方式。

來源：[Python API Guide，PDF Pages 5、7–8、目錄所列各產品章節](../ANSYS_Document/SCADE/unknown/manuals/PythonAPIGuide_SCF-APG-26.pdf#page=7)／[逐頁 Markdown](../ANSYS_Document/SCADE/unknown/manuals/PythonAPIGuide_SCF-APG-26.md#pdf-page-7) · `ansys_ea47e7a9de89d8288997d1c8`；[Java/Tcl API Guide，PDF Pages 5、7–8](../ANSYS_Document/SCADE/unknown/manuals/JavaTclAPIGuide_SCF-APG-26.pdf#page=7)／[逐頁 Markdown](../ANSYS_Document/SCADE/unknown/manuals/JavaTclAPIGuide_SCF-APG-26.md#pdf-page-7) · `ansys_95248193ab7edefdef64fb02`；[Metamodels Reference，PDF Pages 2–4](../ANSYS_Document/SCADE/unknown/manuals/Metamodels_SCF-API-TRC-26.pdf#page=2)／[逐頁 Markdown](../ANSYS_Document/SCADE/unknown/manuals/Metamodels_SCF-API-TRC-26.md#pdf-page-2) · `ansys_c85bf88bf7c65ae1360073d9`。上述手冊均標示 SCADE 2026 Products Family，發布日期為 January 2026；這不能據以推定產品 release 或新版 Eclipse 相容性。

## 軟體設計標準與專案裁剪

SCADE Suite Application Software Design Standard（文件識別 `SCS-SDS 2024-03-20`）旨在支援 software completeness、accuracy、consistency、verifiability、traceability 與 maintainability。文件明示 Ansys 提供的是 template，使用者須按專案修改；其中有待替換的文件參照與依安全標準裁剪的說明文字。因此它是制定專案 model design rules 的起點，不能未經適用性審查便當成已核准的組織規範或完整合規證據。

| 標準章節 | 可用來查找的設計議題 | 讀者應核對的內容 |
|---|---|---|
| Model elements categorization、LLR definition and identification | Architecture、low-level requirements（LLRs）、derived LLRs 與 non-contributing model elements 的分類及識別 | 依專案生命週期與安全標準確認模型元素如何連到 requirements；不能把文件模板中的示例標籤直接當成專案核准規則。 |
| Naming、data typing and data-flow structuring | 命名、literal values、root／imported operator interface types，以及資料流結構 | 依專案命名規範與目標介面檢查型別；若涉及物理量，另核對 units、range、resolution 欄位及其一致性。 |
| Readability and complexity、libraries、robustness | 模型可讀性與複雜度、library 使用、robustness 設計 | 手冊提供設計規則框架；具體門檻和允許的 library／錯誤處理方式需由專案裁定。 |
| Clocked flows、tool limitations and defects、imported code | clocked-flow 使用、工具限制／缺陷相關補充規則、匯入程式碼 | 按實際 SCADE 工具版本、target 與專案驗證流程確認適用規則；不要只依模板推定工具行為。 |

手冊目錄涵蓋上述主題（PDF physical Pages 7–24）；本詞條是章節導覽，不是逐條規則的翻譯或符合性檢查表。文件的 `shall` 慣例及規則識別方式亦應連同專案裁剪後的版本閱讀。來源：[Software Design Standard，PDF Pages 4、7–24](../ANSYS_Document/SCADE/unknown/manuals/DesignStandard-SCS-SDS.pdf#page=4)／[逐頁 Markdown：PDF Page 4](../ANSYS_Document/SCADE/unknown/manuals/DesignStandard-SCS-SDS.md#pdf-page-4) · `ansys_fb281b3fb1a6b55208b87c4b`。文件識別日期不是產品 release；字典不推定產品版本，也未將此 template 當成任何特定專案的核准標準。

## 安裝與產品詞彙

Installation Guidelines 面向站點系統與授權管理者。依其 overview／目錄，安裝前可按下表定位應查章節；表格是手冊導覽，不列任何已驗證的當前硬體需求或授權政策。

| 管理問題 | Installation Guidelines 章節位置 |
|---|---|
| 安裝媒體、產品套件與附加資源包含什麼？ | Chapter 1：產品發行與資源，含 SCADE Product Family、ARINC 661 及 Packages distribution。 |
| 目標機器是否符合需求？ | Chapter 2：System and Hardware Requirements。須以目標 OS、產品組件及文件版本核對實際規格。 |
| 授權如何配置？ | Chapter 3：Ansys Shared Web Licensing、On-Premises License Server、SCADE token license system。 |
| 如何安裝、啟動或維護？ | Chapter 4：interactive／silent installation、安裝設定、Rapid Prototyper for Twin Builder、啟動與維護。 |
| 如何與既有工具整合？ | Appendices：IBM DOORS 9.x installation 與外部工具 interoperability。 |

同一文件提醒，沒有有效授權時，產品可能以 Viewer mode 啟動，部分功能不可用；某些模組可能需在安裝前先具備授權。這是該版指南中的行為說明，部署前仍應依現行授權指南與實際產品組件確認。Getting Started with Rapid Prototyper 的 panel／simulation 教學已另列於上方 Rapid Prototyper 詞條，不把它當成通用安裝步驟。

SCADE Products Glossary 是 2026 Products Family 詞彙卡。每個詞條會以 category（如 Design、Verification、Generation）及 product tags 限定語境；標籤包括 `SUITE`、`DISPLAY`、`ARCHITECT`、`LIFECYCLE`、`ARINC661`、`TEST`、`RAPIDPROTO`，且可能合併多產品標籤。例如 `Active state` 標為 Design／SUITE；`Absolute Position Management` 標為 DISPLAY／RAPIDPROTO。查同名詞時先看標籤，不應直接把單一子產品定義泛化到整個 SCADE family。

以下詞條可作為查閱字典和原手冊時的入口；它們是 Glossary 的短定義整理，不能取代對應語言或產品手冊中的完整語意：

| 詞條 | Glossary 的範圍與意思 | 閱讀時的連結 |
|---|---|---|
| `Clocked flow` | Design／SUITE：只在選定 instants 定義或啟動的 flow；clock 指出 flow 可用的 instants。 | 對照本字典「同步資料流與 Clocks」，再按 Primer 的 clock discipline 核對組合條件。 |
| `SCADE State Machine (SSM)` | Design／SUITE：以 control flow 和 decision logic 表示行為的階層式 state machine；state 依訊號和 transitions 作反應，transition priority 用來確保模型 determinism。 | 對照本字典「State machines 與 transitions」；Glossary 的定義不足以描述 strong／weak transition 的 cycle 時序。 |
| `Function` | Design／SUITE：不含內部記憶的 stateless operator，可用 graphical 或 textual diagrams 定義。 | 與本字典「Nodes、functions 與 restart」的 node/function 條件一併閱讀。 |
| `Control formalism` | Design／SUITE：以 SSM、If blocks、When blocks 等 control statements 支援 imperative programming。 | 詞條是在描述語言建模形式，不是將整個 SCADE flow model 改稱 imperative program。 |
| `Architecture design` | System／SUITE：為發展 SCADE Low Level Requirements（LLR）奠定基礎；Glossary 以資料型別、top-level operators 和連結舉例說明架構組成。 | 與本字典「軟體設計標準與專案裁剪」分讀；該標準仍需按專案修改。 |

這些詞條都以 Glossary 的分類與標籤為準；physical PDF Pages 3、7、9、15、29 對應 `Architecture design`、`Clocked flow`、`Control formalism`、`Function` 與 `SCADE State Machine`。詞條是家族層級參考卡，版本標籤為 SCADE 2026 Products Family，不用它推斷安裝版本或特定專案的合規狀態。

來源：[Installation Guidelines，PDF Pages 5、7、9–10](../ANSYS_Document/SCADE/unknown/manuals/InstallationGuidelines-SCF-IG-26.pdf#page=7)／[逐頁 Markdown：PDF Page 7](../ANSYS_Document/SCADE/unknown/manuals/InstallationGuidelines-SCF-IG-26.md#pdf-page-7) · `ansys_de8cb5852b4c4e7a097dd555`；[SCADE Products Glossary，PDF Pages 1–3、7、9、15、29](../ANSYS_Document/SCADE/unknown/manuals/Glossary_SCF-GLO-QRC-26.pdf#page=29)／[逐頁 Markdown：PDF Page 29](../ANSYS_Document/SCADE/unknown/manuals/Glossary_SCF-GLO-QRC-26.md#pdf-page-29) · `ansys_0f4d4ff41c047f9053634e74`。兩份手冊標示 SCADE 2026 Products Family、Published January 2026；文件日期不代表當前產品 release。未安裝 SCADE 或驗證現行系統需求／授權。

## Rapid Prototyper 圖形面板、模型模擬與產生應用程式

Rapid Prototyper 是 SCADE Test 開發環境的延伸，用預定義 Widget Library 建立互動式 simulation control cockpit。Getting Started 的目錄與 overview 顯示一條由 graphical panel 建置延伸至模型模擬及應用程式產生的教學路徑：

1. 建立 project 和 graphical panel，從 Widget Library 配置元件，設定 Knob／LED 等 widget 屬性。
2. 定義 widget inputs／outputs，將 panel I/O 接到 SCADE Suite model I/O，設定並啟動互動模擬。
3. 若接外部 FMI-compliant 工具，依教學產生 FMU、加入 Twin Builder model，再執行模擬；這是與 SCADE Suite 直接連接不同的路徑。
4. 另一條輸出路徑是把 SCADE Suite operator 與 graphical panel 一起產生為 standalone executable；Getting Started 的練習明示 Windows standalone executable。文件 overview 另列 Windows、Android、iOS 的互動應用程式產生能力，具體平台與打包步驟須依相應章節及產品版本核對。

User Manual 進一步分列 editor、project、panel、widget、model editing、simulation 與 application generation；本詞條只整理入門流程圖，不取代各 widget 屬性、命令列、平台產生或故障排除步驟。Rapid Prototyper 是獨立 UI／模擬工作流，不能與 SCADE Suite 語言規則或 PyScadeOne API 混為一談。[Getting Started，PDF Pages 5、7–13](../ANSYS_Document/SCADE/unknown/manuals/GettingStarted_SRP-GS-26.pdf#page=7)／[逐頁 Markdown：PDF Pages 7、10、13](../ANSYS_Document/SCADE/unknown/manuals/GettingStarted_SRP-GS-26.md#pdf-page-7) · `ansys_668dcad43de29080ad5d1e6d`；[Rapid Prototyper User Manual，PDF Pages 5、7–9，contents](../ANSYS_Document/SCADE/unknown/manuals/UserManual_SRP-UM-26.pdf#page=7) · `ansys_11f334f610aec47f17b4ce9a`。

Rapid Prototyper manual 發布於 December 2025，Rapid Prototyper 快捷鍵卡標示 Ansys SCADE Rapid Prototyper 2026；快捷鍵仍只適用該 UI。[Rapid Prototyper Shortcuts](../ANSYS_Document/SCADE/unknown/manuals/Shortcuts_SRP-KEY-QRC-26.pdf#page=1) · `ansys_24c1155533d8e09a74df7a0a`。`RPManuals.pdf` 仍只有 255 字目錄型正文，不能取代上述 user manual。

## 版本與限制

檔名含 `SCS-PM-25`、`...-26` 等文件識別；部分正文標示 2026、Jan 2026 或 Dec 2025。SQLite 的產品 `release` 仍為 unknown，不把文件日期直接推定成產品發行版本。多份文件標示授權使用限制；團隊分享前需逐份核對授權條款。


## 2026-11-04：Wave 10 本機來源盤點與限制說明

本批完成 scade 模組既有本機 catalog 文件（共 16 筆）與 sources 清冊（共 13 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/scade_module_conversion_report_20261104.md)。
