# Ansys Granta EduPack 知識字典

> 2026-11-02 核讀：本機 CHM 解包筆記的產品 release 為 unknown；另核讀公開 Granta EduPack Help v261（頁尾 Release 2026 R1）。本頁保留可回查摘要，官方線上 Help 全文未本機快取；CHM 的全量技術內容尚未逐篇核讀。

## 1. 本機來源、轉換與索引狀態

[EduPack 清冊](../ANSYS_Document/edupack/README.md) 現行列出 1,491 個 canonical 來源項目、1,490 個正文。原主題列的「1 個檔案、0 個正文」是過期狀態。

| 層次 | 本輪核對結果 |
|---|---|
| CHM 原件 | `en.com.attributenotes.chm` 保留為 1 個 attachment；原 CHM 本身不直接進 FTS |
| 解包 HTML 路徑 | 1,491 個非空 HTML／HTM；Attribute Notes 為英文，Science Notes 有 en／fr／es／pt 路徑 |
| HTML conversion manifest | 1,381 converted、109 plain_text_fallback、1 reused_existing_markdown；1,491 個輸出檔的 SHA-256 均與 manifest 相符 |
| canonical catalog 正文 | 1,490 body_present，來源與 Markdown text_path 全部存在；另 1 個 CHM attachment |

Water absorption 的一條解包路徑重用相同內容的 canonical Markdown，因此路徑數、轉換方法數和 canonical 正文數不能互換。`plain_text_fallback` 表示保留可辨識文字，並非品質評分。這些檔案／雜湊檢查不證明每頁技術內容、表格及圖片已驗收。

來源：[CHM 原件](../ANSYS_Document/edupack/unknown/manuals/en.com.attributenotes.chm) · `ansys_6e45e2e894201b79e8607c64`；轉換清冊 `_catalog/html_conversion_manifest.json`、文件清冊 `_catalog/documents.json`。CHM notes 頁尾有 ©2026，但不能由版權年份推定產品 release。

## 2. Selection data、資料庫等級與版本界線

Selection data 用於跨材料家族比較；標準規格、廠商 datasheet、研究試驗資料與經統計分析的 design data 有各自用途。官方區分的資料類型不應被概括為同一種設計許用值。Level 1／2 把多種 grade 彙整為概覽；Level 3 需依實際 database 和 record 的來源判讀。

v261 的 Available data 列出 Introductory 包含 Level 1、2 及標準 Level 3，Full Edition 另含 advanced Level 3。標準 Level 3 在該頁描述為 generic material classes，並非所有資料都等於供應商牌號或 safety-critical design data。本頁移除舊稿未固定來源範圍的材料數量、特定牌號參數及「升級等級即可直接用於 FEA」敘述。

來源：[Types of data](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Edu_Pack_Help/sel_edu/types_of_data.html) · `official_edupack_data_types_v261`；[Available data](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Edu_Pack_Help/sel_edu/summary_available_data.html) · `official_edupack_available_data_v261`。

## 3. Selection Table、篩選階段與製程選擇

Database 由彼此連結的 tables 組成；每個 project 一次只對一個 Selection Table 執行選擇，例如 MaterialUniverse 或 ProcessUniverse。Subset 縮小可用 records。Chart、Limit、Tree stages 是可以組合的篩選工具，官方沒有要求固定依 Tree→Limit→Chart 順序操作。

Process selection 教學先選 `ProcessUniverse: Shaping`，以 Limit Stage 設定形狀、質量、斷面厚度、製程類型及 Economic batch size，再用 Tree Stage 關聯 thermoplastics。教學中的輸入值與範例結果只適用該練習，不能當成通用製造門檻。

來源：[Databases, tables, and subsets](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Edu_Pack_Help/sel_edu/database_and_tables.html) · `official_edupack_database_tables_v261`；[Filtering and screening](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Edu_Pack_Help/sel_edu/filtering_and_screening.html) · `official_edupack_filtering_v261`；[Process selection](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Edu_Pack_Help/sel_edu/process_selection.html) · `official_edupack_process_selection_v261`。

## 4. 工具與 advanced Level 3 條件

Select、Chart 與 Eco Audit 是工具入口。v261 tools 頁將 Enhanced Eco Audit、Synthesizer、Engineering Solver、Find Similar、Comparison Tables、Selection Reports 列為 advanced Level 3 database 功能，並明確排除一般標準 Level 3。因此不能只看「Level 3」名稱就推定全部工具可用；以目前開啟的 database 與工具狀態為準。

來源：[Granta EduPack tools and features](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Edu_Pack_Help/sel_edu/about_granta_edupack.html) · `official_edupack_tools_v261`。

## 5. Performance Index Finder 與 index/display lines

PIF 在圖上以 combined property 繪出 performance index；v261 Exercise 12 說明其僅在 Level 3 databases 啟用。這是該工具頁的條件，與前節 advanced Level 3 工具表分開保留。

Performance index 由 function/loading、limiting constraint、objective、free variable 四項定義。Index line 會參與選擇，display-only line 只供顯示。當幾何完全固定、沒有 free variable 時，官方要求使用另一種方法；不能直接套用可變厚度案例的指標。PIF 教學中 X/Y 軸已採用特定 combined properties，不能將其 bottom-left 最佳的結果概括為所有 index chart 都朝同一方向最佳。

來源：[Exercise 12: PIF](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Edu_Pack_Help/sel_edu/advanced_selection_pif.html) · `official_edupack_pif_v261`；[Adding index lines and box selections](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Edu_Pack_Help/sel_edu/index_lines_box.html) · `official_edupack_index_lines_v261`。

## 6. Estimated、Not Applicable 與篩選預設

Estimated 值以 `*` 標記；Not Applicable 與缺資料是不同狀態。Functional attribute 的 Out Of Range 在 selection 中按 Not Applicable 處理，預設會使依該 attribute 篩選的 record 失敗。

| v261 安裝預設 | 值 |
|---|---|
| Pass records with no data | Off |
| Fail estimated records | Off |
| Include generic records in selection | Off |
| Pass when any part of record within selection | On |

使用者設定會跨 session 保留，所以查核專案時應讀取實際設定，不能僅引用安裝預設。

來源：[Estimated and Not-Applicable Attributes](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Edu_Pack_Help/sel_edu/estimated_attributes.html) · `official_edupack_estimated_attributes_v261`；[Default application settings](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Edu_Pack_Help/sel_edu/default_application_settings.html) · `official_edupack_default_settings_v261`。

## 7. Eco Audit 資料與保存

Eco Audit 對 material、manufacture、transport、use、end-of-life 階段估算 energy usage 與 climate-change impact，並以 Summary chart／Detailed report 協助辨識主要階段。部分選項和 cost analysis 需特定 advanced Level 3 database。輸入詳盡程度會影響報告；本頁未將該工具描述為已驗證的完整 LCA。

Product definition 保存為 `*.prd`，與 selection project 分別儲存。計算、cost audit 與減量策略的詳細 EduPack Reference 頁面標示須有 Ansys ID 的客戶存取；本輪未登入取得。

來源：[Creating an Eco Audit project](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Edu_Pack_Help/sel_edu/eco_audit_tool.html) · `official_edupack_eco_audit_v261`。

## 8. 力學 notes 核讀樣本

| 屬性 | 原文定義與判讀邊界 |
|---|---|
| Density | 單位體積質量；原 note 用空氣與已知密度流體的稱重說明測量 |
| Young's modulus | 拉伸初始線彈性段斜率；Attribute Note 的各向異性複材值代表面內主要方向，不能假設為每方向保守值 |
| Yield strength (elastic limit) | 金屬使用 0.2% offset；聚合物為第一個應力峰值；陶瓷通常用 tensile strength at break 作 elastic limit |
| Fracture toughness | 抵抗裂紋傳播；與能量型 Toughness (G) 需區別，原 note 的關係式含圖像，應回原頁讀取 |

Young's modulus／Yield strength 的 Science Notes 另討論測量方法及材料類別差異。本頁不從未核讀的標準原文推出 ASTM／ISO 版本，也不把一份教學定義轉作多軸或動態失效準則。

來源：[Density](../ANSYS_Document/edupack/unknown/manuals/_en.com.attributenotes_decompiled/html/attributenotes/en/material/Density.html) · `ansys_461f4d56725f6995277c93fe`；[Young's modulus](../ANSYS_Document/edupack/unknown/manuals/_en.com.attributenotes_decompiled/html/attributenotes/en/material/Youngs_modulus.html) · `ansys_beed6935e26e1796a9e0f852`；[Yield strength](../ANSYS_Document/edupack/unknown/manuals/_en.com.attributenotes_decompiled/html/attributenotes/en/material/Yield_strength_elastic_limit.html) · `ansys_6767950f2551928093564023`；[Fracture toughness](../ANSYS_Document/edupack/unknown/manuals/_en.com.attributenotes_decompiled/html/attributenotes/en/material/Fracture_toughness.html) · `ansys_f48e758075467af2a5189df1`；[Young's modulus Science Note](../ANSYS_Document/edupack/unknown/manuals/_en.com.attributenotes_decompiled/html/sciencenotes/en/material/S03_Youngs_modulus.htm) · `ansys_32234460340bbc601f685397`；[Yield strength Science Note](../ANSYS_Document/edupack/unknown/manuals/_en.com.attributenotes_decompiled/html/sciencenotes/en/material/S04_Yield_strength.htm) · `ansys_cb4c7ed9f97ceebcf36605d4`。

## 9. 熱學 notes：溫度與 secant CTE

Thermal conductivity 的資料庫值代表約 23°C 室溫表現；不同操作溫度須取得相應資料。Thermal expansion with temperature curves 在 Attribute Note 中明定為 Mean (secant) CTE，reference temperature 由該曲線定義為零熱應變點。Science Note 提醒各向異性材料需多個係數；本頁沒有將圖像公式不完整的抽取文字補寫為確定公式，也不提供跨產品材料輸入規則。

來源：[Thermal conductivity](../ANSYS_Document/edupack/unknown/manuals/_en.com.attributenotes_decompiled/html/attributenotes/en/material/Thermal_conductivity.html) · `ansys_c535478d275173ec153f2836`；[Thermal expansion coefficient](../ANSYS_Document/edupack/unknown/manuals/_en.com.attributenotes_decompiled/html/attributenotes/en/material/Thermal_expansion_coefficient.html) · `ansys_a3bb27280016f107b4db9ce6`；[CTE Science Note](../ANSYS_Document/edupack/unknown/manuals/_en.com.attributenotes_decompiled/html/sciencenotes/en/material/S10_Thermal_expansion_coefficient.htm) · `ansys_cb556d2fd3b44a916d8ac278`。

## 10. Price 與製程 Relative cost index

Price note 的價格是高量向 primary producer 採購的近似排名資料；價格與匯率會隨軟體年度更新，不能將本機 unknown-release 快照當成目前採購報價。對固定體積設計，Price per unit volume 會使用 Price × Density；幾何尺寸可變時應依性能與目標比較。

Process Relative cost index 由 Process Cost Model 估算，範圍下端／上端分別對應較簡單／較複雜元件。它不是單一報價或固定驗收閾值。本頁移除舊稿沒有原文證據的材料案例數值與概念 Python 範例。

來源：[Price](../ANSYS_Document/edupack/unknown/manuals/_en.com.attributenotes_decompiled/html/attributenotes/en/material/Price.html) · `ansys_da5ad16b28877ec56f499c5d`；[Relative cost index](../ANSYS_Document/edupack/unknown/manuals/_en.com.attributenotes_decompiled/html/attributenotes/en/process/Relative_cost_index.html) · `ansys_8f9c4debeb6f409881680bc6`。

## 尚未覆蓋

1,490 canonical 正文已可索引不代表全數已逐篇技術驗證；本輪核讀 8 個 Attribute Notes、3 個 Science Notes。圖片方程、全部測試標準、各語言一致性、材料數據的實際版本與完整操作/API 尚未驗收。官方 Help v261 只做摘要核讀，完整原文及 Ansys ID 限制的 Reference 尚未離線收錄；未執行 EduPack GUI、選材或 Eco Audit。

[Granta MI 字典](granta_mi.md) · [Mechanical 字典](mechanical.md) · [來源清冊](sources.csv) · [主題清冊](topics.csv)


## 2026-11-04：Wave 6 本機來源盤點與限制說明

本批核對本機 catalog 1,491 筆（1,490 份正文、1 份 CHM attachment）的原件與文字 SHA-256、路徑及標籤。sources.csv 共 1,503 列，其中另有 12 筆 v261 線上摘要，沒有本機路徑或可核對的正文 hash。223 個 URL 均未擷取；受登入限制或未快取的 Help／Reference 內容保留為缺口，未推造 API。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/edupack_module_conversion_report_20261104.md)。
