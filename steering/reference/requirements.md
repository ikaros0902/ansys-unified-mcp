# Requirements Document

## Introduction

本規格定義一套與具體 AI coding agent 工具解耦的「Loop Engineering 框架」。核心概念參考自 `reference-loop-engineering.md`：不再逐條手動提示 AI 代理，而是設計一個能自動「發現工作 → 分配任務 → 檢查結果 → 記錄狀態 → 決定下一步」的閉環系統（Loop），並讓此閉環能自動重複執行。

本框架的交付物為「方法論規格 + 可執行 kit」雙重層次：

1. **方法論規格文件（規格層）**：以工具無關的抽象語言，定義 Loop 的六大組件（Automation_Trigger、Isolated_Workspace、Skill_Document、Connector、Sub_Agent_Role、Memory_File）、設計原則、反模式與成本風控標準。此層完全通用，不特化任何單一工具；文件中若出現特定工具的對應語法，僅作為「參考範例」標註，不構成規格要求。

2. **可套用樣板集與可執行 kit（實作層）**：一組獨立的 Markdown 樣板檔案，以及一組可執行的落地元件，讓使用者能把規格層的抽象概念直接落地到專案中。實作層包含：
   - 一份可攜的循環定義格式 `loop.yaml`（以宣告式描述閉環六階段 + 成本上限），工具無關。
   - 一支可執行的 `Validator`，驗證 `loop.yaml` 的結構完整性與反模式防護規則。
   - 為 Kiro、Claude Code、OpenAI Codex 各一份 `Adapter_Mapping`，把 `loop.yaml` 六階段對應到各工具原生原語並記錄落差。
   - 一支 Windows PowerShell `Scaffolder`，一鍵在專案內產生範例 `loop.yaml` 與 Memory / Skill / Sub_Agent_Role 範本。

規格層描述「應該長什麼樣」，實作層提供「可直接跑起來的最小落地物」。兩層共用同一套術語與同一組閉環六階段，確保「無論坐在哪個工具裡都能工作的循環」。

## Glossary

- **Loop_Engineering_Framework**：本次交付的整體框架，涵蓋方法論規格層與可執行 kit 實作層。
- **Loop_Engineering_Specification**：框架的方法論規格文件本身，定義 Loop 的組成、原則與標準。
- **Loop**：使用者依本規格設計的閉環自動化流程單元，具備發現工作、分配任務、檢查結果、記錄狀態、決定下一步的能力，並可重複執行。
- **Loop_Definition**：Loop 的可攜宣告式檔案，具體為 `loop.yaml`，以工具無關詞彙描述閉環六階段（trigger、discover、classify、assign、verify、record）與成本上限（budget）。
- **loop.yaml**：Loop_Definition 的檔案格式，頂層恰好包含 `trigger`、`discover`、`classify`、`assign`、`verify`、`record` 六個階段欄位與 `budget` 欄位。
- **Automation_Trigger**：驅動 Loop 開始執行的機制，分為定時觸發（Schedule-based）與事件觸發（Event-based）兩類；於 `loop.yaml` 對應 `trigger` 欄位。
- **Isolated_Workspace**：讓多個 Sub_Agent_Role 並行工作而不互相干擾的隔離工作空間機制，為 Git worktree 概念的工具無關等價抽象。
- **Skill_Document**：以文件形式編碼專案知識與慣例，供 AI 代理在 Loop 執行時載入的文件，採漸進式披露（Progressive Disclosure）原則；其可執行範本為含 `name`/`description` YAML front matter 的 `SKILL.md`。
- **Connector**：讓 Loop 存取外部系統（如問題追蹤系統、CI 系統、通訊工具）的機制，以 MCP（Model Context Protocol）為主要參考標準。
- **Sub_Agent_Role**：Loop 中分工的代理角色，區分為製造者角色（產出結果）與檢查者角色（審查結果）；預設四類為 Explorer、Implementer、Tester、Reviewer。
- **Memory_File**：以 Markdown 或等價格式記錄 Loop 跨會話狀態的持久檔案（如 AGENTS.md、TODO.md、PROGRESS.md）。
- **Verification_Condition**：用於客觀判定 Loop 任務是否完成或應停止的條件；於 `loop.yaml` 對應 `verify` 欄位內的停止條件。
- **Anti_Pattern**：Loop 設計中應避免的常見錯誤模式（Loop 過度複雜、Verification_Condition 過弱、忽視成本管理）。
- **Example_Loop**：本規格附帶的具體 Loop 案例，供使用者參考與修改，非強制流程。
- **Template_Set**：本規格交付的一組可直接套用到任何專案的獨立 Markdown 樣板檔案集合。
- **Adapter_Mapping**：把 Loop_Definition 六個階段欄位對應到特定 Target_Tool 原生原語的對照文件，含落差記錄與已驗證版本號。
- **Target_Tool**：可執行 kit 支援的目標 AI coding agent，初期為 Kiro、Claude Code、OpenAI Codex 三者。
- **Validator**：可執行的檢查器，驗證 Loop_Definition 的結構完整性與反模式防護規則。
- **Scaffolder**：以 Windows PowerShell 提供的 scaffolding 指令，在專案內產生範例 Loop_Definition 與範本檔。
- **budget**：`loop.yaml` 中指定成本上限或頻率上限的欄位，須為大於 0 的數值。
- **Author**：使用本框架設計 Loop 的人。

## Requirements

### Requirement 1: 方法論規格文件總覽與結構標準

**User Story:** As a 想在自己的 AI coding agent 專案套用 Loop Engineering 的使用者, I want 一份總覽方法論規格文件, so that 我能快速理解框架全貌並知道如何找到各組件的細節與對應樣板。

#### Acceptance Criteria

1. THE Loop_Engineering_Specification SHALL 定義 Loop 的六大組件：Automation_Trigger、Isolated_Workspace、Skill_Document、Connector、Sub_Agent_Role、Memory_File
2. THE Loop_Engineering_Specification SHALL 以工具無關的抽象語言描述每個組件，不將任何組件的定義綁定於特定 AI coding agent 的專屬語法
3. WHERE Loop_Engineering_Specification 中出現特定工具的對應範例, THE Loop_Engineering_Specification SHALL 將該範例標記為參考範例，並與規格要求的段落分開呈現
4. THE Loop_Engineering_Specification SHALL 包含一份目錄，列出 Template_Set 中每個樣板檔案的用途與建議存放位置
5. THE Loop_Engineering_Specification SHALL 將設計原則檢查清單與反模式檢查清單納入文件結構中

### Requirement 2: Automation_Trigger 觸發抽象標準

**User Story:** As a 框架使用者, I want 一套描述 Loop 觸發時機的抽象標準, so that 我可以在任何具備排程或事件機制的工具中設計 Loop 的自動化觸發。

#### Acceptance Criteria

1. THE Loop_Engineering_Specification SHALL 定義 Automation_Trigger 的兩種類型：定時觸發與事件觸發
2. WHEN 使用者為某個 Loop 定義 Automation_Trigger 時, THE Loop_Engineering_Specification SHALL 要求記錄該 Loop 的觸發類型、觸發條件與執行頻率
3. THE Loop_Engineering_Specification SHALL 不規定任何特定工具的排程語法或指令格式作為 Automation_Trigger 的定義方式
4. THE Template_Set SHALL 包含一份 Automation_Trigger 定義樣板檔案，供使用者填寫觸發類型、觸發條件與執行頻率

### Requirement 3: Isolated_Workspace 等價隔離機制標準

**User Story:** As a 需要並行運行多個 AI 代理的使用者, I want 一套工具無關的隔離工作空間標準, so that 多個 Sub_Agent_Role 可以並行工作而不互相覆蓋彼此的變更。

#### Acceptance Criteria

1. THE Loop_Engineering_Specification SHALL 定義 Isolated_Workspace 概念，列出實現該概念所需具備的特性，至少包含檔案系統隔離與可合併回主線兩項特性
2. THE Loop_Engineering_Specification SHALL 列出至少三種可實現 Isolated_Workspace 的具體機制類型，並說明其與該概念的等價關係
3. IF 一個 Loop 中有多個 Sub_Agent_Role 同時修改同一組檔案, THEN THE Loop_Engineering_Specification SHALL 要求該 Loop 為每個 Sub_Agent_Role 指派獨立的 Isolated_Workspace
4. THE Loop_Engineering_Specification SHALL 定義將 Isolated_Workspace 中的變更合併回主線之前必須完成的驗證步驟

### Requirement 4: Skill_Document 漸進式披露標準

**User Story:** As a 需要讓 AI 代理理解專案慣例的使用者, I want 一套 Skill_Document 的標準結構, so that AI 代理每次啟動都能以最少的上下文成本載入必要的專案知識。

#### Acceptance Criteria

1. THE Loop_Engineering_Specification SHALL 定義 Skill_Document 的標準結構，包含名稱、描述、適用條件與詳細內容四個欄位
2. THE Loop_Engineering_Specification SHALL 要求 Skill_Document 的載入遵循漸進式披露原則：預設僅提供名稱與描述，僅在適用條件成立時載入詳細內容
3. THE Template_Set SHALL 包含一份 Skill_Document 樣板檔案，涵蓋 metadata 區塊、適用場景、專案慣例與常見陷阱四個章節，且該樣板須含 `name` 與 `description` 的 YAML front matter
4. WHERE 使用者的專案含有多個 Skill_Document, THE Loop_Engineering_Specification SHALL 要求建立一份索引清單，記錄每個 Skill_Document 的名稱與適用場景
5. IF 專案含有多個 Skill_Document 但索引清單缺失, THEN THE Loop_Engineering_Specification SHALL 判定 Skill_Document 功能不得運作，直到索引清單建立完成
6. IF 一份 Skill_Document 缺少 `name` 或 `description` front matter 欄位, THEN THE Validator SHALL 將該 Skill_Document 標記為無效，且無論缺少欄位名稱是否成功回報皆維持無效標記
7. WHERE Skill_Document 因缺少 front matter 欄位被 Validator 標記為無效, THE Loop_Engineering_Framework SHALL 阻止 AI 代理載入該 Skill_Document

### Requirement 5: Connector 使用決策標準

**User Story:** As a 需要讓 Loop 存取專案外部系統的使用者, I want 一套判斷何時需要 Connector 以及如何記錄 Connector 的標準, so that Loop 能安全且可追溯地接入外部工具。

#### Acceptance Criteria

1. THE Loop_Engineering_Specification SHALL 定義判斷 Loop 是否需要 Connector 的標準：Loop 需要存取其自身無法直接讀寫的外部資料來源或系統時，須使用 Connector
2. THE Loop_Engineering_Specification SHALL 以 MCP 作為 Connector 的主要參考標準，並明確標註 MCP 為建議採用而非強制採用的協議
3. WHILE 使用者實際使用非 MCP 的 Connector 機制, THE Loop_Engineering_Specification SHALL 要求在該 Connector 可被使用之前，同時記錄其能力清單與存取範圍兩者，不接受僅記錄其中一項的部分文件
4. THE Template_Set SHALL 包含一份 Connector 清單樣板檔案，記錄每個 Connector 的名稱、用途、存取範圍與所屬 Loop

### Requirement 6: Sub_Agent_Role 分工標準

**User Story:** As a 設計 Loop 的使用者, I want 一套 Sub_Agent_Role 的分工標準, so that 產出結果的代理與審查結果的代理彼此分離，避免自我審查的寬容偏差。

#### Acceptance Criteria

1. THE Loop_Engineering_Specification SHALL 定義 Sub_Agent_Role 的分類標準，至少包含製造者角色與檢查者角色兩類
2. WHERE AC1 的 Sub_Agent_Role 分類標準已建立, IF 一個 Loop 同時包含產出結果與審查結果兩種任務, THEN THE Loop_Engineering_Specification SHALL 要求該 Loop 將產出任務與審查任務指派給不同的 Sub_Agent_Role 實例，且允許同一角色類型於不同實例下分別承擔產出與審查工作
3. THE Loop_Engineering_Specification SHALL 針對每個 Sub_Agent_Role 要求記錄職責範圍、輸入與輸出、以及存取權限（唯讀或可寫）
4. THE Template_Set SHALL 包含一份 Sub_Agent_Role 定義樣板檔案，供使用者填寫角色名稱、職責範圍、存取權限與製造者或檢查者分類，且該樣板至少提供 Explorer、Implementer、Tester、Reviewer 四個預設角色
5. THE Sub_Agent_Role 樣板 SHALL 將 Explorer 與 Reviewer 角色標示為唯讀存取權限，且其工作僅限讀取與回報發現，不得修改程式碼

### Requirement 7: Memory_File 持久記憶格式標準

**User Story:** As a 需要讓 Loop 跨會話保留狀態的使用者, I want 一套 Memory_File 的標準格式, so that AI 代理即使在新會話中失去上下文，仍能從檔案讀取先前的進度。

#### Acceptance Criteria

1. THE Loop_Engineering_Specification SHALL 定義 Memory_File 的標準 Markdown 結構，包含進行中事項、已完成事項、待分類事項三個區塊
2. WHEN 一個 Loop 完成一輪任務執行, THE Loop_Engineering_Specification SHALL 要求該 Loop 將任務狀態更新至對應的 Memory_File
3. THE Loop_Engineering_Specification SHALL 針對 Memory_File 中每個進行中事項要求記錄負責的 Sub_Agent_Role、所屬 Isolated_Workspace（若有使用）與目前的 Verification_Condition 達成狀態
4. THE Template_Set SHALL 包含 `AGENTS.md`、`TODO.md`、`PROGRESS.md` 三份 Memory_File 樣板檔案，其中 TODO.md 以 Markdown 任務清單語法（`- [ ]`、`- [x]`）標示工作項目，PROGRESS.md 每筆紀錄以 ISO 8601 時間戳開頭並依時間由新到舊逆序排列
5. WHEN 循環於會話開始讀回某個 Memory_File 且該檔案存在並可讀取, THE Loop_Engineering_Framework SHALL 將該檔案的章節內容載入為當前上下文狀態
6. IF 循環讀回某個 Memory_File 時該檔案不存在或無法讀取, THEN THE Loop_Engineering_Framework SHALL 以該 Memory_File 的空白範本（僅含章節結構）續行，並回報一則指出受影響檔名的錯誤訊息
7. WHERE Memory_File 存在且可讀取, THE Loop_Engineering_Framework SHALL 僅在檔案不存在或無法讀取時回報錯誤，不因既存可讀檔案的格式或內容問題而回報錯誤

### Requirement 8: Verification_Condition 客觀化標準

**User Story:** As a 需要確保 Loop 產出可信的使用者, I want 一套讓完成條件保持客觀可驗證的標準, so that Loop 不會僅依主觀判斷宣告任務完成。

#### Acceptance Criteria

1. THE Loop_Engineering_Specification SHALL 要求每個 Loop 定義至少一個 Verification_Condition 作為任務完成或停止的判定依據
2. IF 一個 Verification_Condition 的描述僅為主觀判斷而非可客觀檢查的標準, THEN THE Loop_Engineering_Specification SHALL 判定該條件不合規，並要求改寫為可客觀驗證的條件
3. THE Loop_Engineering_Specification SHALL 提供可客觀驗證條件的範例類型清單，至少包含測試全部通過、靜態檢查無錯誤、指標達到指定門檻、檢查者角色核准四種類型
4. THE Loop_Engineering_Specification SHALL 要求負責檢查 Verification_Condition 的 Sub_Agent_Role 與負責產出待驗證結果的 Sub_Agent_Role 不可為同一角色

### Requirement 9: 設計原則檢查清單

**User Story:** As a 設計新 Loop 的使用者, I want 一份設計原則檢查清單, so that 我在導入自動化的同時，仍保有對產出的驗證責任與理解力。

#### Acceptance Criteria

1. THE Loop_Engineering_Specification SHALL 提供設計原則檢查清單，至少包含驗證責任歸屬於人、保持對產出的理解力、避免認知投降三項原則
2. THE Loop_Engineering_Specification SHALL 針對設計原則檢查清單中的每項原則提供至少一個可供使用者自我檢查的判斷問題
3. THE Template_Set SHALL 包含一份設計原則檢查清單樣板檔案，供使用者在設計新 Loop 時逐項確認

### Requirement 10: 反模式檢查清單

**User Story:** As a 審查既有 Loop 的使用者, I want 一份常見反模式檢查清單, so that 我能在 Loop 造成實際損害前發現並修正設計缺陷。

#### Acceptance Criteria

1. THE Loop_Engineering_Specification SHALL 提供反模式檢查清單，至少包含 Loop 過度複雜、Verification_Condition 過弱、忽視成本管理三項 Anti_Pattern
2. THE Loop_Engineering_Specification SHALL 針對反模式檢查清單中的每項 Anti_Pattern 描述可觀察的症狀與對應的改善建議
3. THE Template_Set SHALL 包含一份反模式檢查清單樣板檔案，供使用者在審查既有 Loop 時逐項比對

### Requirement 11: 成本與風險控管標準

**User Story:** As a 需要控制 AI 代理執行成本的使用者, I want 一套成本與風險控管標準, so that Loop 在自動重複執行時不會產生失控的執行次數或費用。

#### Acceptance Criteria

1. THE Loop_Engineering_Specification SHALL 定義模型分層策略，依 Sub_Agent_Role 的任務性質建議對應的模型量級：輕量模型、主力模型、強推理模型三個層級
2. THE Loop_Engineering_Specification SHALL 要求每個 Automation_Trigger 記錄其執行頻率，並建議以低頻率起步後依產出品質調整頻率
3. WHERE 使用者為 Loop 設定執行成本或 Token 用量上限, THE Loop_Engineering_Specification SHALL 要求記錄該上限數值與超出上限時的處理方式
4. THE Loop_Engineering_Specification SHALL 建議優先採用事件觸發而非固定高頻率排程，以降低無變化時的空轉執行
5. THE Template_Set SHALL 包含一份成本與風險控管樣板檔案，記錄模型分層設定、執行頻率、成本上限與觸發方式

### Requirement 12: 範例 Loop 樣板

**User Story:** As a 剛開始設計 Loop 的使用者, I want 幾個具體的範例 Loop 案例, so that 我可以參考完整案例並改寫成適合自己專案的 Loop。

#### Acceptance Criteria

1. THE Loop_Engineering_Specification SHALL 提供二至三個 Example_Loop 案例，且每個 Example_Loop 須涵蓋六大組件中至少四項的實際應用方式
2. THE Loop_Engineering_Specification SHALL 針對每個 Example_Loop 記錄其 Automation_Trigger、涉及的 Sub_Agent_Role、使用的 Memory_File 與 Verification_Condition
3. THE Loop_Engineering_Specification SHALL 將 Example_Loop 標註為可修改的參考案例，而非使用者必須照抄的固定流程

### Requirement 13: 可套用樣板集交付物

**User Story:** As a 想直接把框架套用到新專案的使用者, I want 一組獨立且無工具綁定的樣板檔案, so that 我可以直接複製到任何 AI coding agent 專案中開始使用，不需要额外改寫工具專屬語法。

#### Acceptance Criteria

1. THE Template_Set SHALL 以獨立的 Markdown 檔案形式交付，每個檔案對應 Loop_Engineering_Specification 中定義的一個組件或一份檢查清單
2. THE Loop_Engineering_Specification SHALL 提供 Template_Set 中所有檔案的清單，並說明每個檔案的使用時機，且此清單與說明允許在 Template_Set 檔案實際交付之前即先存在
3. WHEN 使用者將 Template_Set 中的樣板檔案複製到新專案, THE Template_Set SHALL 不包含任何綁定特定 AI coding agent 的專屬指令或語法

### Requirement 14: 可攜循環定義格式 loop.yaml

**User Story:** As a Author, I want 用單一宣告式檔案描述一個 Loop, so that 同一份定義能套用到不同 AI coding agent，而不必為每個工具重寫。

#### Acceptance Criteria

1. THE Loop_Engineering_Framework SHALL 定義一種名為 `loop.yaml` 的 Loop_Definition 檔案格式，且該檔案的頂層恰好包含 `trigger`、`discover`、`classify`、`assign`、`verify`、`record` 六個階段欄位，不多不少
2. THE loop.yaml SHALL 包含一個 `budget` 欄位，且該欄位指定一個大於 0 的數值成本上限或頻率上限
3. THE Loop_Definition SHALL 以工具無關的詞彙描述各階段，且不得包含任何特定 Target_Tool 的原生原語，禁用清單至少涵蓋工具專屬函式呼叫、工具專屬 SDK 或 API 名稱、工具專屬檔案路徑，以及工具專屬指令旗標
4. WHERE Loop_Definition 的 `trigger` 指定排程觸發, THE Loop_Definition SHALL 以恰好五欄位（分、時、日、月、星期）的 cron 標準運算式表示執行時間
5. WHEN 一次 Loop 完成記錄步驟, THE Loop_Definition SHALL 於 `record` 階段指定將結果寫入至少一個 Memory_File

### Requirement 15: Loop_Definition 驗證器（Validator）

**User Story:** As a Author, I want 在啟用循環前用一支可執行檢查器驗證定義, so that 我能在自動執行前及早發現結構錯誤與反模式。

#### Acceptance Criteria

1. WHEN Author 對一份 Loop_Definition 執行 Validator, THE Validator SHALL 完整執行結構完整性檢查（Requirement 14 的六個必要欄位）與反模式防護規則檢查（過弱驗證條件、Sub_Agent_Role 數量上限、budget 欄位），且不因任一類檢查失敗而略過另一類檢查
2. WHILE 執行檢查期間, THE Validator SHALL 不修改所驗證之 Loop_Definition 內容，且不啟用或觸發該循環
3. IF 指定的 Loop_Definition 內容無法解析為有效 YAML, THEN THE Validator SHALL 將該定義標記為無效、回報單一則指出解析失敗原因的錯誤，並不執行後續結構完整性與反模式防護規則檢查
4. IF Loop_Definition 缺少六個必要欄位中的任一欄位, THEN THE Validator SHALL 回報所有缺少欄位的名稱並將該定義標記為無效
5. IF 六個必要欄位中任一欄位存在但其值為空值（null、空字串或空集合）, THEN THE Validator SHALL 回報該空值欄位的名稱、附上「欄位不得為空」的錯誤指示，並將該定義標記為無效
6. IF Loop_Definition 中存在 cron 欄位且該 cron 運算式欄位數不等於五、或任一欄位值超出其合法範圍, THEN THE Validator SHALL 將該定義標記為無效，且無論 cron 格式錯誤指示是否成功回報皆維持無效標記
7. IF Loop_Definition 的 `verify` 欄位未包含任何 Verification_Condition, THEN THE Validator SHALL 回報一則指出缺少 Verification_Condition 的警示並標記 `verify` 欄位名稱，但不因此將該定義標記為無效
8. IF Loop_Definition 的 Verification_Condition 全體皆未包含（測試通過、lint 通過、可量測數值門檻）三者中任一項, THEN THE Validator SHALL 回報該 Verification_Condition 為過弱驗證條件、指出缺少的判準類型並將該 Loop_Definition 標記為無效
9. IF Loop_Definition 的 Sub_Agent_Role 數量超過 4, THEN THE Validator SHALL 回報該循環過於複雜、列出第 5 個起超出上限的角色名稱並建議精簡角色數量至 4 以內
10. IF Loop_Definition 缺少 `budget` 欄位或其值為無效值（非數值或小於等於 0）, THEN THE Validator SHALL 回報缺少成本上限或 budget 為無效值、將該定義標記為無效並保留原始內容不變
11. WHEN Loop_Definition 通過全部結構完整性與反模式防護規則檢查, THE Validator SHALL 回報驗證通過，並逐一列出 trigger、discover、classify、assign、verify、record 六個階段各自解析出的欄位值摘要
12. IF Loop_Definition 未通過任一項檢查, THEN THE Validator SHALL 回報所有失敗項目的清單，且每項含對應的規則識別、失敗的欄位名稱與失敗原因分類

### Requirement 16: 工具適配對照（Adapter_Mapping）

**User Story:** As a Author, I want 把一份循環定義套用到我目前使用的工具, so that 我在切換 Kiro、Claude Code、OpenAI Codex 時能保留同一套循環設計。

#### Acceptance Criteria

1. THE Loop_Engineering_Framework SHALL 為 Kiro、Claude Code、OpenAI Codex 各提供恰好一份 Adapter_Mapping，且每份 Adapter_Mapping 僅對應單一 Target_Tool
2. THE Adapter_Mapping SHALL 將 Loop_Definition 的六個階段欄位逐一對應，每筆對應記錄該階段欄位名稱與其在該 Target_Tool 的原生原語名稱，且六個欄位皆須有一筆對應記錄
3. WHERE 某 Target_Tool 缺乏對應某階段的原生原語, THE Adapter_Mapping SHALL 記錄該落差，落差內容須包含缺乏對應的階段欄位名稱與以 Memory_File 為基礎的替代做法
4. THE Adapter_Mapping SHALL 以版本編號記錄各 Target_Tool 已驗證對應的版本
5. WHEN Author 指定一個受支援的 Target_Tool 與一份已通過結構檢查的 Loop_Definition, THE Loop_Engineering_Framework SHALL 依對應的 Adapter_Mapping 產生該工具可執行的循環設定說明
6. IF Author 提出產生循環設定說明的請求但未指定任何 Target_Tool, THEN THE Loop_Engineering_Framework SHALL 允許該請求繼續，並套用預設 Target_Tool 或提示 Author 選擇 Target_Tool
7. IF Author 指定的 Target_Tool 非 Kiro、Claude Code、OpenAI Codex 之一, THEN THE Loop_Engineering_Framework SHALL 回傳指出該工具不受支援的錯誤指示，且僅回傳錯誤指示、不阻擋既已進行中的部分處理繼續完成
8. IF Author 指定的 Loop_Definition 未通過結構檢查, THEN THE Loop_Engineering_Framework SHALL 拒絕產生循環設定說明，並回傳指出結構檢查失敗的錯誤指示，且保留原 Loop_Definition 內容不變

### Requirement 17: Windows PowerShell Scaffolder

**User Story:** As a Windows 使用者, I want 用一個指令在專案內建立範例循環定義與範本, so that 我能快速開始設計 Loop，不必手動建檔。

#### Acceptance Criteria

1. THE Scaffolder SHALL 以 PowerShell 指令形式提供，可在 Windows 環境執行
2. WHEN Author 在目標專案目錄執行 Scaffolder, THE Scaffolder SHALL 產生一份範例 Loop_Definition（`loop.yaml`）、三個 Memory_File 範本、一個 Skill_Document 範本與四個 Sub_Agent_Role 範本
3. IF 目標專案目錄已存在同名檔案, THEN THE Scaffolder SHALL 保留既有檔案、將該檔案狀態設為 SKIPPED，並明確回報被略過的檔名
4. WHEN Scaffolder 完成, THE Scaffolder SHALL 回報已建立與已略過的檔案清單
