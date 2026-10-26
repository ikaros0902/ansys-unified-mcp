# GUI 結果檢視 SOP (`gui_result_review_sop.md`)

LS-PrePost GUI 開啟 d3plot、檢視變形/應力、量測與截面切割的標準流程。本手冊補充 GUI 選單操作，與 `states_and_results.md`（SCL/DataCenter 程式化查詢）互補；兩者可搭配：GUI 用於互動檢視與出圖，SCL/Python 用於批次自動化提取。

> 出處一律標註官方手冊章節，以 `search_ansys_docs(doc="Ansys_LS-PrePost_Users_Guide")` 可查到原文。本檔未標出處的細節一律視為「未驗證」，不可照抄執行；若需要可執行的 cfile 範本，先用 GUI 操作一次並提供錄製的 `lspost.cfile`。

## 一、載入結果（手冊 §3.1 File Menu / §3.1.1 File Open）

- `File → Open → LS_DYNA Binary Plot`：開啟 d3plot / d3eigv 結果檔。
- `LS_DYNA Keyword+D3plot`：同時多選 keyword 與 d3plot 檔案一起載入。局部/材料/使用者座標系的應力顯示（`d3plot/Elem/Glob/Mtrl/User` 切換）需要兩者都載入，只開 d3plot 看不到。
- `Update`：求解進行中可刷新 d3plot（不用重新開檔）。
- 從 LS-Run 的 Job Table 選一個輸出檔案、點 LSPP 按鈕，可直接開啟對應結果。

## 二、Fringe（手冊 §6.4.1 FriComp / §6.4.1.1 Basic / §6.4.2 Range）

- `Post → Fringe Component`：選分量。殼單元沿厚度方向有多個積分點時，**預設取所有積分點資料的最大值**（原文：「By default LS-PrePost will fringe the maximum of all integration point data available.」，chunk #299）；若要看特定層（Low/Mid/Upp/Max/Ave/Min/IPt/BPt），用分量旁的選取widget另外指定。
- 應力/應變預設以寫入 d3plot 時的座標系顯示（通常是 global），要看 Element/Material/User 座標系需要同時載入 keyword 檔（見第一節）。
- `Fringe Range`（§6.4.2.1 Basic）：
  - **Dynamic**：每個 state 各自算一組 min/max。
  - **Static**：所有 state 共用同一組 min/max，跨 state 比較用這個。
  - **User**：自訂範圍。
- 引用數值前先確認圖例單位，單位制跟隨 LS-DYNA 輸入模型，不是 LS-PrePost 自己定義的。

## 三、Displacement Scale Factor（手冊 §6.4.15 Post Settings / §6.4.15.1，`Ansys_LS-PrePost_Users_Guide` chunk #330）

> 原文：「6.4.15. Post Settings — This interface is used to organize personal post-processing display preferences... Displacement Scale Factor — Open displacement scale factor interface.」

`Displacement Scale Factor` 是 `Post Settings`（§6.4.15）底下的子功能（§6.4.15.1），跟同在 §6.4.14 General Settings 底下、分別控制殼厚度與 fringe 顏色映射的 `Thickness Scale Factor`（§6.4.14.3）、`Fringe Scale Factor`（§6.4.14.4）是三個不同介面，容易混淆。GUI 可對位移顯示設定縮放係數，純粹是視覺效果，不影響實際計算值。**量測或擷取報告用圖前，記得把 Displacement Scale Factor 設回 1.0**，否則讀到的是視覺放大後的幾何，不是真實變形量。本次查證只確認該介面存在與所屬章節，介面內的具體子選項（Whole/Part、X/Y/Z 等）未逐一核對，使用前建議在 GUI 操作確認。

## 四、量測（手冊 §6.3.10 Measure / §6.3.10.1 Basic，`Ansys_LS-PrePost_Users_Guide` chunk #284）

> 原文：「6.3.10. Measure — This interface is used to make measurements of various aspects of the model and to create local coordinate systems. ... If post-processing files are loaded, measured quantities will be XY plotted.」

量測清單（`Element Tools → Measure`，§6.3.10.1 Basic）第一批項目含 Coordinate、Dist N2N 等；完整清單（含 Separation、Dist Node to Surf、Dist Part to Surf、Dist Segm to Segm、Dist SALE Points、Min Area Passage/Throat）出自 chunk #285（§6.3.10.1 Basic 清單延續段）。

- **Dist N2N**：點選或輸入兩個節點 ID，量兩點距離。
- **Separation**：量「part 對 part」的分離距離，細節見第六節。
- 若有載入後處理檔（d3plot），量測結果會畫成 XY 曲線（原文：「If post-processing files are loaded, measured quantities will be XY plotted.」）；可選取 History 清單中的分量、點 `Plot` 繪圖（`New` 開新視窗、`Padd` 疊加到當前視窗，來源：chunk #334 Step 3，屬 §6.5 Sample 範例章節的操作示範，不是 §6.3.10 本體）。

## 五、Section Plane（手冊 §6.2.7.1，`Ansys_LS-PrePost_Users_Guide` chunk #242）

> 原文：「FixS: Fixed in space means that the section plane will not move once defined. FixM: Fixed to Model means that the section plane can move if the nodes used to define it move. Lagr: Lagrangian means that a group of elements is cut initially, and then those same elements are tracked throughout the animation... This option is most similar to *DATABASE_CROSS_SECTION.」

- **FixS**：固定在空間中，定義後不隨模型移動。
- **FixM**：固定在模型上，若定義用的節點移動，截面也跟著動。
- **Lagr**：Lagrangian，先切一組單元，之後動畫過程追蹤同一組單元（不受限於固定平面），最接近 `*DATABASE_CROSS_SECTION` 的行為。
- 四種定義方式：`1p+NL`（1 點+法向量）、`N1-N2`（節點 1 在面上、節點 2 指示法向）、`3Nds`（3 個節點）、`2Nds+D`（2 節點+方向餘弦）。
- `Project View`：視角轉為垂直於截面；`Clipping Mode`：`Off`/`Clip+`/`Clip-`，隱藏截面一側的模型；`Meas`：截面量測子功能；`Force`（§6.2.7.8，chunk #246）：LS-DYNA 透過 `*DATABASE_CROSS_SECTION` 輸出截面力，LS-PrePost 計算截面變數需 d3plot 內有殼單元合力（shell resultants）資料，此資料通常預設寫出，除非被 `*DATABASE_EXTENT_BINARY` 選項關閉（原文：「LS-PrePost computes the section quantities if shell resultants are available in d3plot files. Generally this data is available in d3plot files unless it is turned off by the use of *DATABASE_EXTENT_BINARY options.」）。

## 六、量測間隙 Separation（手冊 §6.5.4 Sample_3，`Ansys_LS-PrePost_Users_Guide` chunk #335）

> 原文：「The first part picked is used as the reference part, and the software takes all the nodal points for the part and projects them to the second part.」

第一個選取的 part 是參考 part，軟體把該 part 所有節點投影到第二個 part 上計算距離；預設沿全域方向投影，勾選 `Axial` 可改為沿指定軸向（x/y/z）投影。

## 七、輸出（手冊 §3.1 File Menu）

- `Print...`：開啟列印對話框輸出目前畫面。
- `Movie...`：輸出動畫。
- `Save As`：可存 keyword、project、**Post.db**、geometry 等檔案；`Save`（不加 As）會覆寫既有檔案。

## 八、GUI → 可執行腳本對照（只列已在 repo 中實際用過的指令）

以下指令曾在 `agents/skills/ansys-ls-prepost/scripts/lspp_mvp_post_bga_eps.py` 與 `references/python_module_interface.md` 中出現，是唯一目前可信的 cfile/SCL 範本來源：

| 指令 | 用途 |
|---|---|
| `genselect target part` | 選取目標 part |
| `genselect allvis` | 選取所有可見元素 |
| `print png ... LANDSCAPE nocompress` | 輸出 PNG 截圖 |
| `range userdef` | 設定使用者自訂 fringe 範圍 |
| `range fringelimit` | 設定 fringe 上下限 |
| `range pal hue max` | 設定色階 |
| `range identmax` | 標示最大值位置 |
| `xyplot` | 開 XY 曲線視窗 |

第一到七節提到的其他 GUI 動作（開檔、Fringe Component 選單路徑、Measure 對話框、Section Plane 介面）目前沒有對應的 cfile 指令可以照抄，寫自動化腳本前要先用 `dyna_run_prepost(dry_run=True)` 驗證命令組裝，或請人用 GUI 操作一次錄製 `lspost.cfile`。
