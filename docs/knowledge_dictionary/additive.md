# Ansys Additive 知識字典

本頁依 2026-11-02 可公開讀取的官方文件整理，主要範圍為 Mechanical／Workbench 中的 PBF 模擬，來源頁尾標示 Release 2026 R1（v261）。本機 Additive 目錄仍沒有技術手冊正文；以下是可追溯摘要，官方 HTML／PDF 全文尚未快取或加入本機索引。本輪命令列 curl 因 DNS 無法解析 `ansyshelp.ansys.com` 而失敗；其後主流程透過網頁工具取得兩個官方頁面的快取文字，未保存官方全文，也沒有產生轉換檔。Additive Print／Science 與 Mechanical PBF 的介面及版本應分別查閱。

## Mechanical PBF 範圍與 super layer 抽象

Mechanical 的 AM 模擬用來評估零件巨觀變形、殘留應力及支撐配置趨勢。模型以分層網格與元素生死模擬逐層成形，將多個實際粉層合併為有限元素 **super layer**；熱分析先行，溫度歷程再供結構分析使用。這些抽象不足以解析微觀組織或精細局部熱循環。支撐可用均質化固體表示，周圍粉末的熱損失可簡化為邊界對流。

來源：[Additive Simulation in the Mechanical Application，§2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/add_ag/add_ag_AM_in_WB.html) · `official_additive_mechanical_v261`。製程名稱與支撐用途另見 [Introduction，§1](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/add_ag/add_ag_intro.html) · `official_additive_intro_v261`。

## PBF Setup Wizard 與專案樹資料流

載入 PBF Process Add-on 後開啟精靈。`Apply Changes` 將輸入寫入專案樹，`Read from Tree` 將標準樹物件設定讀回精靈；實際求解使用專案樹設定。`Exit` 保留已套用動作，`Finish` 重新執行各步，包含網格生成。進階自訂網格／接觸設定宜在離開精靈後調整。先關閉精靈再求解，避免事後按完成清除既有結果。預設精靈不支援 Linux；該平台使用 Legacy LPBF Setup Wizard。

來源：[Using the PBF Setup Wizard，§4](https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/add_ag/add_ag_workflow_with_wizard.html) · `official_additive_wizard_v261`。

## Model Setup／STL 支撐與網格限制

先辨識零件、支撐與底板，再指定材料及網格；成形方向採全域 +Z。STL 支撐的長度單位須為 mm。生成網格前先套用幾何與網格設定。

| 項目 | v261 來源所述界線 |
|---|---|
| Generated Supports | 從既有零件網格向下生成元素；先建立零件網格 |
| 多實體生成支撐 | 實體間須有 shared topology |
| Layered Tetrahedral | 可以分層貼合幾何，但不能搭配 Generated Supports |
| 模板 | 保存設定，未保存幾何選取；載入後仍須套用 |

來源：[Wizard Step 1: Model Setup，§4.1](https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/add_ag/add_ag_wiz_model.html) · `official_additive_model_v261`。

## Inherent Strain 定義與 SSF／ASC 校正

Inherent Strain 系統直接建立結構分析，不需熱結果，且沒有 cooldown 步驟。其 Strain Scaling Factor（SSF）需依機台與材料組合校正；原文關係為應變等於 SSF 乘降伏強度再除彈性模數。

Build Settings 提供等向、全域方向異向、掃描方向及機器學習熱應變定義。後兩者的 ASC 依掃描平行／垂直及成形方向區分；預設值可用於相對趨勢探索，不能代表已完成實驗校正。機器學習預測另需 Structures AI+ 授權，載入應變用的 ML 材料模型與結構分析的 Engineering Data 材料資料應分別核對。

來源：[Using the Inherent Strain Method，§6.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/add_ag/add_ag_adv_top_inherentstrain.html) · `official_additive_inherent_v261`；[Build Settings for Inherent Strain，§4.2](https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/add_ag/add_ag_wiz_build_set.html) · `official_additive_is_settings_v261`。

## Thermal-Structural 加熱、停留與邊界條件

加熱方式可選熔點溫度或功率。功率模式再選按掃描時間施熱，或短暫脈衝；吸收率須在 0–1 之間。Dwell Time 表示層間等待，Dwell Time Multiple 可代表未建模的相同零件或對稱扇區；多熱源數量會縮短掃描層時間。Build、cooldown 與底板表面的熱邊界應分別檢查，包含氣體／粉末溫度、對流及輻射選項。這些輸入是模型設定，不是通用製程推薦值。

來源：[Build Settings for Thermal-Structural，§4.3](https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/add_ag/add_ag_wiz_build_set_ts.html) · `official_additive_ts_settings_v261`。

## 後處理步驟與 PBF 結果時間語意

精靈可加入底板鬆栓、熱處理、支撐移除及底板切除；要改變先後次序，離開精靈後編輯 AM Process Sequence。結果項須在求解時儲存所需資料，事後評估只能取回已求解／儲存的項目。

| 結果 | 解讀範圍 |
|---|---|
| Hotspot | 僅適用熱結構模擬，檢查局部過熱 |
| Recoater Interference | 觀察各層在下一層加入前的 Z 變形，非冷卻結束的最終變形 |
| High Strain | 標示成形歷程中較高應變區域，門檻須按材料與目標判讀 |

來源：[Postprocessing Options，§4.4](https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/add_ag/add_ag_wiz_post.html) · `official_additive_post_v261`；[Review Results，§5.17](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/add_ag/review_results_wowiz.html) · `official_additive_results_v261`。

## AM Process 收斂排查提示

官方排查頁建議依失敗情境檢查移除步驟的剛體運動、直接求解器（Direct Solver）、熔點附近材料強度及 STL 網格品質。薄壁件若出現挫曲形狀，可能需要大變形及足夠的網格解析度；不能一律以關閉大變形處理。這些是診斷候選項，須按模型確認原因。

來源：[Troubleshooting，§6.15](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/add_ag/add_ag_adv_top_convergence.html) · `official_additive_troubleshoot_v261`。

## Tutorials v261 可讀範圍與版本邊界

官方 Tutorials PDF 共 78 個實頁，封面標示 2026 R1。可見章節涵蓋 LPBF Bracket 與 DED Racetrack；Double Arches 校正及 Printed Bridge 燒結章節的後續內容明示需具授權的 Ansys 登入憑證，不能視為已讀完整教學。數值與時間均為教學案例，不作通用門檻。

來源：[Additive Manufacturing Tutorials v261，實頁 1、7、9、77](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/pdf/Additive_Manufacturing_Tutorials.pdf) · `official_additive_tutorial_v261`。

## 本機來源缺口

[本機清冊](../ANSYS_Document/Additive/README.md) 仍無 Additive 技術正文。本輪已讀 11 個官方 HTML 與 Tutorials PDF 的公開範圍；全文未落地，RAG 整合後可檢索本頁摘要，不能宣稱可回取完整官方正文。

v251 [Additive Print and Science User’s Guide](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/pdf/Additive_Print_and_Science_Users_Guide.pdf) · `official_additive_user_v251` 仍因擷取工具回報 13,204,800 bytes 大小限制而未讀。完整 Print／Science 功能、跨版本介面差異、受限校正／燒結教學及圖表仍待取得可用來源。沒有執行 Workbench／Mechanical、教學求解或外部登入；團隊分享仍應遵循各來源授權條款。

## 2026-11-03 本機轉換與檢索狀態

本機 Additive 目錄只有 README（0 個來源檔、0 正文）。逐來源 13 筆狀態見[Additive 來源與轉換清冊](../maintenance/knowledge_dictionary_passes/2026-11-02/additive_sources_review_20261103.csv)：12 筆 v261 官方頁為 summary-only，1 筆 v251 Print／Science 手冊未取得；目前沒有 Additive 原件可轉成 Markdown。RAG 搜尋目前可回到本字典摘要；指定官方來源 ID 尚無可檢索正文。


## 2026-11-04：Wave 5 本機來源盤點與限制說明

本批完成 additive 模組既有本機 catalog 文件（共 0 筆）與 sources 清冊（共 13 筆）之完整雜湊、正文路徑與標籤結構核對。本機未快取或具備企業授權/登入限制之線上主題誠實標記為缺口（保持現有非 complete 狀態），未擅自虛構未核實之線上 API 簽名或執行求解運算。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/additive_module_conversion_report_20261104.md)。
