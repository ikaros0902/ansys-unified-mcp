# Reaction／CHEMKIN／Model Fuel Library 知識字典

> 2026-11-02 核讀：本機來源是 **Model Fuel Library 2024 Validation Manual**，共 269 個實頁，文件編號 `MFL-EMF-2024ER-2025-RPT-1`；產品 release metadata 保持 unknown。本輪另核讀公開的 CHEMKIN／Reaction Workbench v261 HTML（頁尾 Release 2026 R1），只保存下列摘要；官方線上全文未快取。本機 MFL 文件標示 Confidential and Proprietary，團隊分享須遵守原來源使用條件。

## 來源範圍與產品分工

CHEMKIN 文件涵蓋反應器專案、chemistry set、反應輸入及計算；Reaction Workbench 提供機制比較、檢查與縮減等工具；MFL Validation Manual 則記錄 MFL 機制與實驗資料的比較。三者的資料用途與驗證對象應分開追蹤。

本機 MFL PDF 及逐頁 Markdown 已保留。CHEMKIN Getting Started、Input Manual 與 Reaction Workbench 官方 HTML 現可公開讀取，故原「完全找不到 CHEMKIN 使用指南」缺口已縮小；本機仍沒有這三套官方指南的離線全文，也未逐章整理全部 reactor／API／keyword。

來源：[MFL PDF](<../ANSYS_Document/Reaction_Chemkin/unknown/manuals/Model Fuel Library Validation Manual.pdf>)、[MFL 逐頁 Markdown](<../ANSYS_Document/Reaction_Chemkin/unknown/manuals/Model Fuel Library Validation Manual.md>) · `ansys_cbdd3112768d39b43cd253f9`；[Getting Started](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/chemkin_gs/chemkin_gs.html) · `official_chemkin_getting_started_v261`；[Input Manual](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/chemkin_in/chemkin_in.html) · `official_chemkin_input_v261`；[Reaction Workbench](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/reaction_util/reaction_util.html) · `official_reaction_workbench_v261`。

## 1. MFL 2024 評級與驗證範圍

MFL 實頁 20 的 Component Mechanism Ratings 使用 **A／B／C**，沒有 Tier 1／Tier 2 分級：

| 評級 | Table 1 的意義摘要 |
|---|---|
| A | 預測良好至優良，落在實驗誤差或不確定性內 |
| B | 可接受至良好；差異可能來自實驗模擬表示，或機制適用範圍有限 |
| C | 趨勢一致但定量有差異，仍需改進 |

同一文件存在評級矛盾：實頁 20 的敘述稱 PAH emissions 機制為 C；實頁 23 的 Table 2 卻將 `PAH formation` 列為 B。兩處的名稱也不完全相同，本頁保留此差異，不能據以對全部 PAH／soot 功能給單一等級。

實頁 20 記錄 77 個 components；實頁 24 記錄本章討論 140 個驗證案例、48 個純燃料與 25 個混合燃料。實頁 27 的共同做法包含 shock-tube batch-reactor 建模，以及氫氣採 multicomponent、其他燃料通常採 mixture-averaged transport 的火焰速度案例設定。實驗條件應逐案回查 Table 3（實頁 28–35），不把其範圍當成所有組分的有效域或通用誤差門檻。

來源：[MFL 實頁 20](<../ANSYS_Document/Reaction_Chemkin/unknown/manuals/Model Fuel Library Validation Manual.pdf#page=20>)、[實頁 23](<../ANSYS_Document/Reaction_Chemkin/unknown/manuals/Model Fuel Library Validation Manual.pdf#page=23>)、[實頁 24–27 起點](<../ANSYS_Document/Reaction_Chemkin/unknown/manuals/Model Fuel Library Validation Manual.pdf#page=24>) · `ansys_cbdd3112768d39b43cd253f9`。

## 2. Chemistry set：輸入資料的配套關係

Chemistry set 可包含熱化學、氣相反應、表面反應及氣相輸運資料。機制通常與特定 thermochemical data 一起開發，替換其中一份資料時須重新確認一致性。Getting Started §3 的 Table 3.1 以 R／O／X 表示不同 reactor model 的必要、選用與不使用資料；例如 PSR 的 transport data 為 X，Pre-Mixed Burner 則為 R，不能用單一檔案清單套到所有模型。

來源：[Acquiring Chemical Data，§3／Table 3.1](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/chemkin_gs/pgfId-106906720394863.html) · `official_chemkin_chemistry_set_v261`。

## 3. 前處理、Working Directory 與 Mechanism Viewer

新專案先定義 chemistry set 並執行 Pre-Processing，才進入後續 reactor／inlet 設定。Working Directory 是產生計算輸入／輸出的目錄，chemistry set 檔案可位於別處。前處理確認資料一致性與完整性；預設的格式檢查與選用的 Inspect Mechanism 是不同檢查。

Mechanism Viewer 可查看熱力學、輸運與氣相／表面反應資料。其壓力相依反應圖只繪 high-pressure-limit rate constants；反向速率常數圖還需要有效 Chemkin KINetics API license。前處理通過不等同模型已經實驗驗證。

來源：[Pre-Processing，§2.2.2–2.2.2.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/chemkin_gs/i91327s.html) · `official_chemkin_preprocessing_v261`。

## 4. 專案檔、chemistry set 與封存

| 副檔名 | 內容／用途 |
|---|---|
| `.ckprj` | 專案設定、連接及 chemistry set／profile 指標 |
| `.cks` | chemistry set 的機制輸入檔路徑定義 |
| `.ckmrt` | Reaction Workbench 縮減專案 |
| `.ckcsv` | 從解檔抽出的 CSV 資料 |
| `.ckzip` | 可移轉／還原的專案封存 |

Archive 預設只打包輸入，可選擇納入輸出與解檔。若專案引用檔案缺失，工具會報錯，但使用者仍可選擇產生不完整封存；副檔名本身無法證明封存完整。Unarchive 將內容放入所選的新 Working Directory。

來源：[File Extensions，§2.7](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/chemkin_gs/ch02s07.html) · `official_chemkin_file_extensions_v261`；[Archiving，§2.4](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/chemkin_gs/i95508.html) · `official_chemkin_archive_v261`。

## 5. 氣相反應輸入語法與錯誤診斷

Gas-phase reaction 行包含反應式與三個 Arrhenius 係數，係數間以空白分隔；`!` 後為註解。`=`／`<=>` 表示可逆，`=>` 表示不可逆。未另指定時活化能以 cal/mole，前因子使用反應級數相應的 cgs 單位。`+M` 與 `(+M)` 對應不同第三體／壓力相依表示，不能只替換符號而省略所需輔助資料。

Pre-processor 遇錯仍會繼續診斷，並在 linking file 寫入 error flag；此時 `CKINIT` 不初始化 work arrays。應回查診斷輸出並修正缺失的 thermo data、反應分隔符或係數等問題，不能以「讀完整個檔案」判定通過。

來源：[Reaction Data，§3.6.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/chemkin_in/pgfId-1072114.html) · `official_chemkin_reaction_data_v261`；[Error Checks，§3.6.4](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/chemkin_in/pgfId-1072818.html) · `official_chemkin_error_checks_v261`。

## 6. Mechanism Merge／Compare 的物種配對

兩套機制所有物種均有 canonical SMILES 時，以 SMILES 配對；任一物種缺少時，整個配對選項改以 symbolic species name 識別，像 OH／HO 會被當成不同物種。跨來源合併須特別檢查命名與熱力學／輸運／rate-data 衝突。Full mechanism 提供衝突預設值，使用者可逐項或依資料類型覆寫；comparison tolerance 的用途是忽略指定大小的資料差異，並非實驗驗證標準。

來源：[Mechanism Merge／Compare，§2.1.1](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/reaction_util/i650456865014558154.html) · `official_reaction_merge_v261`。

## 7. Mechanism Inspector 的檢查範圍

Inspector 檢查熱力學資料不連續、過高正／反向 rate constants、活化能與反應熱的可疑關係，以及選用的零／負 pre-exponential factor。需指定 working directory 與 chemistry set，預設溫度範圍和門檻可調。這些是潛在問題提示；仍須確認來源資料與反應模型，不能把沒有警告解讀為所有實驗條件均有效。

來源：[Mechanism Inspector，§2.1.4](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/reaction_util/ckrwb_sec_mechinspec.html) · `official_reaction_inspector_v261`。

## 8. Guided Mechanism Reduction 的目標誤差

DRG／DRGEP／DRGPFA 等方法依目標輸出與容差反覆調整縮減程度。其 error 是相對 **unreduced full mechanism 的 Target project 計算**，與完整機制本身的實驗驗證分開。使用者按 ignition delay、flame speed、NOx 等目標分別設定相對／絕對容差及 profile／endpoint／maximum；官方沒有要求一律 5%，也未要求固定剩餘 species 數。

Normalized maximum error 小於 1 表示選定目標符合已設定容差。若用 ignition-delay target，來源另提醒可選只比較最後主要點火事件，避免把前期小事件當成縮減目標。縮減結果的適用範圍須與選定條件一起保存，不能由 species 數推導 CFD 加速倍數。

來源：[Guided Mechanism Reduction，§2.3](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/reaction_util/i89586334945638634656.html) · `official_reaction_reduction_v261`；[Controlling Target Error，§2.3.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/reaction_util/i35760513586650135865.html) · `official_reaction_target_error_v261`。

## 尚未覆蓋與回查路徑

本頁未逐章核讀 MFL 的全部 140 案例，也未取得 CHEMKIN 三套指南的本機全文。所有 reactor keyword、surface chemistry、API／user routines、Fluent 匯入流程與跨版本相容性均未全面整理；本輪未執行反應器、縮減或 CFD。表格／圖像與原頁的參數條件仍需按具體任務回查。

- [來源清冊](sources.csv)／[主題清冊](topics.csv)：由主代理整合上述來源 ID 與狀態。
- [Fluent 字典](fluent.md)：另查 Fluent 模型與資料格式；本頁不提供通用 EDC 設定或物種數／誤差門檻。


## 2026-11-04：Wave 8 本機來源盤點與限制說明

本批完成 reaction_chemkin 模組既有本機 catalog 文件（共 1 筆）與 sources 清冊（共 14 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/reaction_chemkin_module_conversion_report_20261104.md)。
