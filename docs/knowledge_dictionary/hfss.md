# HFSS 知識字典

本頁整理五份本機 HFSS PDF 與六個官方 HFSS Help HTML 的可定位主題。五份 PDF 封面均標示 **Release 2026 R1／January 2026（v261）**，合計 4,430 實頁；頁碼均從封面起算，與章內印刷頁不同。內容是文件摘要與原文差異記錄，未執行 AEDT、PyAEDT 或求解。

## 1. HFSS scripting environments

| 環境 | 文件描述的入口與限制 |
| --- | --- |
| Desktop IronPython | Tools 的 Command Window／Run Script、產品命令列或 External Tools；提供 `oDesktop`、`ScriptArgument`。該版說明為 Python 2.7／.NET Framework 4.0，含 C extension 的 NumPy／SciPy 不在預期可直接使用範圍。 |
| Standalone IronPython | 使用安裝目錄 `common/IronPython/ipy64.exe`，經 COM 取得 app；文件說其功能少於 Desktop 內腳本，僅完整支援 COM functions。外部路徑、初始化與結束需按該版 ScriptEnv 說明。 |
| CPython | `ansysedt` 是 gRPC server，CPython script engine 是 client。`Connect`、`InitializeNew`、`Initialize` 作用不同，不能與 PyAEDT 各版本的 client 生命週期直接合併。 |

CPython server 預設由 port 50051 起找可用 port；`-grpcsrv` 可指定單一 port 或範圍。`Connect(projectPath)` 能連至已開啟專案，必要時本機啟動並開啟；不存在專案則錯誤。遠端 project path 必須是 network path，且需要對應既有專案。`InitializeNew()` 一律建立新 instance，其 Machine 在此版限空字串／本機；`Initialize()` 優先連接指定 listener，必要時啟動。多腳本連續使用時 `Shutdown()` 只放最後一支腳本。

指南將 `-features=beta -ng -runscriptandexit` 標成 beta，且該段限 HFSS／3D Layout；不省略適用限制或推定所有腳本能無頭運作。

來源：[HFSS scripting 實頁 62–68](../ANSYS_Document/_catalog/pdf_text_v4/c13dd9213c3841394ef42ef2298f26e1dcf877083937180f60fc6888c9654f73.md#pdf-page-62)、[104–108](../ANSYS_Document/_catalog/pdf_text_v4/c13dd9213c3841394ef42ef2298f26e1dcf877083937180f60fc6888c9654f73.md#pdf-page-104)；[來源列](sources.csv#ansys_e0fa0d611694014d037709e8)。

## 2. HFSS 3D Layout scripting

本機 3D Layout Scripting Guide 同時包含共用 AEDT 物件、3D Modeler、Layout、Definition Manager 與專用 setup／excitation 命令；看到共用章節不代表任意命令可用於每一個 design。應按 command 的設計、module、參數與回傳型別判斷。

原文實頁 122 的 PyAEDT 介紹標示 Beta，並連到 stable 線上文件；這只記錄該 PDF 的用語，不能由其推定最新 PyAEDT SDK 版本、`Hfss3dLayout` 每個方法簽章或安裝相容性。先前字典的建層、50-ohm 走線、edge port、sweep 與自動求解程式沒有由本機手冊逐項核對，已移除；走線寬度亦不構成已驗證的 50-ohm 結論。

來源：[3D Layout 實頁 122–123](../ANSYS_Document/_catalog/pdf_text_v4/185f7860fb2b1add529281f7af26ae076468f5cca7856effbee800a9079c8294.md#pdf-page-122)；[來源列](sources.csv#ansys_120f3bead55153540a17eaea)。

## 3. HFSS 3D Layout scripting environments and layer semantics

GUI 的 active layer 用於新增／放置操作，但不保證一定存在；GUI 操作必要時可改 active layer 並提示。**Script adding operations 不使用 GUI active layer**，必須確保指定的 layer 存在且符合該操作所需類型。原文對不合規 layer 的措辭是「操作不執行」，並未在這段保證固定 exception 型別或必然拋錯。

Locked layer 禁止直接或透過 script 編輯、刪除、新增其物件及變更物件 property；但參數改動仍可能改變 locked layer 上的物件。這是來源描述的例外，不推定成任意參數掃描一定重新生成拓撲。

來源：[3D Layout 實頁 121–123](../ANSYS_Document/_catalog/pdf_text_v4/185f7860fb2b1add529281f7af26ae076468f5cca7856effbee800a9079c8294.md#pdf-page-121)。環境與 gRPC 入口需查該書共用 scripting 章；實頁 121–123 不是完整連線章，也不是全部 command reference。

## 4. Waveguide Combiner

v261 教學的 WR42 四埠合波器截面為 420 mil × 170 mil；以頂面 Perfect E symmetry 建立半模型，並將 port impedance multiplier 設為 2。側面／底面指定 aluminum finite conductivity，四端面分別設 wave port；此對稱與補償是案例設定，不能套成任意模型規則。

案例 adaptive setup 名為 `20GHz`，頻率 20 GHz、最多 15 passes、Maximum Delta S 0.005；其 interpolating sweep 指定 19.5–20.4 GHz、step 0.01 GHz。說明文字計為 91 點，但實頁 68 步驟又要求 table title 顯示 `[10 points defined]`；實頁 65–66 的交叉參照還稱 Discrete sweep。這些原文差異保留，不以圖說／表題覆蓋實際設定值。

結果章在約 19.94 GHz 述及 S12／S14 約 −3.09 dB。這是教材結果，不是本機重算結果或一般設計驗收門檻。

來源：[教學 PDF](../ANSYS_Document/HFSS/v261/manuals/HFSS%2020%20GHz%20Waveguide%20Combiner.pdf)、[實頁 9](../ANSYS_Document/_catalog/pdf_text_v4/7a986d5506ccb4a1352f46e5f35ca6ce59b671bafe49a7b51d9ebc4f6ff1a8db.md#pdf-page-9)、[50–53](../ANSYS_Document/_catalog/pdf_text_v4/7a986d5506ccb4a1352f46e5f35ca6ce59b671bafe49a7b51d9ebc4f6ff1a8db.md#pdf-page-50)、[65–68](../ANSYS_Document/_catalog/pdf_text_v4/7a986d5506ccb4a1352f46e5f35ca6ce59b671bafe49a7b51d9ebc4f6ff1a8db.md#pdf-page-65)、[81](../ANSYS_Document/_catalog/pdf_text_v4/7a986d5506ccb4a1352f46e5f35ca6ce59b671bafe49a7b51d9ebc4f6ff1a8db.md#pdf-page-81)；[來源列](sources.csv#ansys_69e3c6a74b6b1f3f17c54452)。

## 5. Waveguide T-Junction

教材用三段 waveguide 及 inductive septum 比較 Port1 對 Port2／Port3 的分配；`Offset` 控制 septum 的 Y 位置，0 in 是居中，0.2 in 向 Port2 移動。wave port 的 integration line 用以保持場型方向一致，複製模型時需留意一起複製的激發。

範例採 modal solution、adaptive frequency 10 GHz、Maximum Delta S 0.01、預設最多 6 passes，另以 8–10 GHz／0.05 GHz sweep 比較 S 參數。教材實頁 12 把預期值歸於先前模擬與產品檢視；實頁 51 的 0.2 in 案例述及 S12 約 0.42、S13 約 0.9、S11 約 0.07。只作教材趨勢與報告量定位，不作誤差或收斂門檻。

來源：[原 PDF](../ANSYS_Document/HFSS/v261/manuals/HFSS%20Tee%20Waveguide%20Junction.pdf)、[實頁 12](../ANSYS_Document/_catalog/pdf_text_v4/f5839e7c5e3ea0de2041b63ed9317a15e513edb845ec670b083c10e2eba1451b.md#pdf-page-12)、[42–44](../ANSYS_Document/_catalog/pdf_text_v4/f5839e7c5e3ea0de2041b63ed9317a15e513edb845ec670b083c10e2eba1451b.md#pdf-page-42)、[51](../ANSYS_Document/_catalog/pdf_text_v4/f5839e7c5e3ea0de2041b63ed9317a15e513edb845ec670b083c10e2eba1451b.md#pdf-page-51)；[來源列](sources.csv#ansys_aa54af061b844b2177c6a190)。

## 6. T-Junction optimization

此教學以完成的 T-Junction 為前置，用 parametric sweep 觀察 Offset，再以 Quasi Newton 做最佳化。輸出量是 `Power11=mag(S(Port1,Port1))^2`、`Power21=mag(S(Port2,Port1))^2`、`Power31=mag(S(Port3,Port1))^2`；目標 `Power31-2*Power21=0` 表示 Port3 功率為 Port2 兩倍。教材搜尋界線 0–0.2 in、起點約 0.1 in、Max Iterations 1000，僅屬該案例。

**來源限制保留：**實頁 35／41 說 acceptable cost 0.001，實頁 36／39 則是 3e-4，p36 還列 noise 5e-5。來源沒有在本輪消解這兩組門檻；不能任選一組當唯一正確值。書名提及 SpaceClaim Link，目錄與正文未提供對應操作章。本輪沒有重新視覺核對圖中最適 Offset 的精確數字，因此不沿用先前的 image-only 精確值。

來源：[原 PDF](../ANSYS_Document/HFSS/v261/manuals/HFSS%20Tee%20Waveguide%20Optimization.pdf)、[功率定義實頁 21–22](../ANSYS_Document/_catalog/pdf_text_v4/dcc51711798f7a264c468fb704c39d71aea6c4f8dd98dd440ba55318d538f2e8.md#pdf-page-21)、[35–39](../ANSYS_Document/_catalog/pdf_text_v4/dcc51711798f7a264c468fb704c39d71aea6c4f8dd98dd440ba55318d538f2e8.md#pdf-page-35)、[41](../ANSYS_Document/_catalog/pdf_text_v4/dcc51711798f7a264c468fb704c39d71aea6c4f8dd98dd440ba55318d538f2e8.md#pdf-page-41)；[來源列](sources.csv#ansys_0d65e57b02fbbcdc29893cd9)。本父題維持 `source_limited`。

## 7. HFSS v261 Maximum Delta S 與停止條件

有 ports 的設計以相鄰 adaptive passes 的 S-parameter complex delta 監控變化，包含幅值與相位；不是量測相對誤差的通用百分比。來源說明會在滿足 delta 條件或用完要求 passes 時停止，所以「求解停止」不等於指定收斂條件已達成。Delta S 使用 deembed、renormalize 後適用的 modal／terminal S 參數，與未處理 S 的比較條件要分清。

來源：[Maximum Delta S](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/HFSS/Content/HFSS/MaximumDeltaS.htm)，[來源列](sources.csv#official_hfss_delta_s_v261)。來源矩陣方程是圖片，未在此重新抄寫。

## 8. HFSS v261 excitation 對應的收斂量與儲存場

有 ports 可用 Maximum Delta S 或 matrix convergence；電壓／電流源、incident wave、magnetic bias 或 characteristic mode 情境涉及 Maximum Delta Energy；Eigenmode 則用 Maximum Delta Frequency，不能只用同一 Delta S 門檻評斷所有 solution type。Minimum Passes／Minimum Converged Passes、refinement 等是另外的 adaptive controls。

要產生場 overlay、near／far-field 報告或 port field display，需依來源設定保存 fields。此頁沒有指定統一儲存量、數值門檻或求解器選擇。

來源：[Adaptive analysis parameters](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/HFSS/Content/HFSS/SettingAdaptiveAnalysisParametersforHFSS.htm)，[來源列](sources.csv#official_hfss_adaptive_parameters_v261)。

## 9. HFSS v261 Single、Broadband 與 Multi-Frequencies adapt

Single 在指定頻率 adapt；Broadband 及 Multi-Frequencies 限 modal／terminal。Broadband 讓工具在指定頻帶選適應頻率，至少三點；額外點與 HPC／資源條件有關，不能推定所有 license 都可增點。該頁用各頻率 Delta S 的加權平均描述 Broadband；Multi-Frequencies 則要求每個指定頻率達其各別 target。

Broadband 會帶出相同範圍的 interpolating sweep，但來源說適應頻率不能直接查看 fields；可另建含那些頻率的 discrete sweep 取得對應資料。這兩種「adapt frequency」與「顯示／sweep frequency」應分別記錄。

來源：[Adaptive meshing methods](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/HFSS/Content/HFSS/AdaptiveMeshingMethodsInHFSS.htm)，[來源列](sources.csv#official_hfss_adaptive_methods_v261)。

## 10. HFSS v261 Driven sweep 類型與限制

| 類型 | 此官方頁的使用界線 |
| --- | --- |
| Fast | 對頻帶內急遽共振／行為變化提供 full-field solution；存在 anisotropic boundary 時禁用。 |
| Interpolating | 估計整段頻帶，適用較寬且平滑的響應或 Fast 記憶體需求過大時；TDR 圖依此來源需用 interpolating。 |
| Discrete | 在指定頻點產生場解，適用只需少數頻點的情況。 |

這是 Driven solution types 的選擇說明，不構成其他 solution type 的支援矩陣或效能排名。

來源：[Selecting sweep type](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/HFSS/Content/HFSS/SelectingtheSweepType.htm)，[來源列](sources.csv#official_hfss_sweep_type_v261)。

## 11. HFSS v261 Interpolating sweep 的 mesh、場與完成條件

Interpolating sweep 使用 adaptive solution frequency 已 refine 的 mesh；沒有 adaptive 時用 initial mesh，sweep 自身不再 refinement。它依 error tolerance 或最大 solutions 數停止，兩者需分別檢查。該頁指出 S-parameters 保存於每個已解頻點，而 full-field 預設只留最後計算的頻率；不能由頻率曲線存在推定每個頻率都有可用場資料。

來源：[Interpolating frequency sweeps](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/HFSS/Content/HFSS/InterpolatingFrequencySweepsinHFSS.htm)，[來源列](sources.csv#official_hfss_interpolating_v261)。

## 12. HFSS v261 Modal、Terminal 與 Eigenmode 的報告量

Driven Modal 以 waveguide modes 的入射／反射功率表示 modal S-matrix；Driven Terminal 以單／多導體 terminal 的電壓電流表示 terminal S-matrix。Eigenmode 尋找結構的共振頻率及其 fields，且來源不允許設計中有依頻率變動的參數（例：frequency-dependent impedance boundary）。選擇 solution type 時需先確定物理激發與報告量，不能僅依 GUI 名稱替換。

來源：[Solution types](https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v261/en/Subsystems/HFSS/Content/HFSS/SolutionTypesinHFSS.htm)，[來源列](sources.csv#official_hfss_solution_types_v261)。其他 transient、SBR+、CMA／hybrid 的完整規範未在此整理。

## 13. HFSS v261 本機手冊導覽與轉換可追溯性

| 本機 PDF | 實頁 | 來源 ID |
| --- | ---: | --- |
| HFSS Scripting Guide | 2210 | [ansys_e0fa0d611694014d037709e8](sources.csv#ansys_e0fa0d611694014d037709e8) |
| HFSS 3D Layout Scripting Guide | 2024 | [ansys_120f3bead55153540a17eaea](sources.csv#ansys_120f3bead55153540a17eaea) |
| 20 GHz Waveguide Combiner | 89 | [ansys_69e3c6a74b6b1f3f17c54452](sources.csv#ansys_69e3c6a74b6b1f3f17c54452) |
| Waveguide T-Junction | 61 | [ansys_aa54af061b844b2177c6a190](sources.csv#ansys_aa54af061b844b2177c6a190) |
| T-Junction Optimization | 46 | [ansys_0d65e57b02fbbcdc29893cd9](sources.csv#ansys_0d65e57b02fbbcdc29893cd9) |

兩份大型 scripting 手冊的部分章節入口：[HFSS 3D Modeler p510](../ANSYS_Document/_catalog/pdf_text_v4/c13dd9213c3841394ef42ef2298f26e1dcf877083937180f60fc6888c9654f73.md#pdf-page-510)、[Boundary／Excitation p962](../ANSYS_Document/_catalog/pdf_text_v4/c13dd9213c3841394ef42ef2298f26e1dcf877083937180f60fc6888c9654f73.md#pdf-page-962)、[Analysis Setup p1194](../ANSYS_Document/_catalog/pdf_text_v4/c13dd9213c3841394ef42ef2298f26e1dcf877083937180f60fc6888c9654f73.md#pdf-page-1194)；[Layout Simulation Setup p1226](../ANSYS_Document/_catalog/pdf_text_v4/185f7860fb2b1add529281f7af26ae076468f5cca7856effbee800a9079c8294.md#pdf-page-1226)、[Excitations p1272](../ANSYS_Document/_catalog/pdf_text_v4/185f7860fb2b1add529281f7af26ae076468f5cca7856effbee800a9079c8294.md#pdf-page-1272)、[Layout Scripting p1304](../ANSYS_Document/_catalog/pdf_text_v4/185f7860fb2b1add529281f7af26ae076468f5cca7856effbee800a9079c8294.md#pdf-page-1304)。這些是目錄導航，並非整章 API 已完成語意覆核。

五份 PDF 都有既有同名 Markdown 及 canonical v4，每份各自保留連續頁標題，沒有必要重轉；五本的 4,430 原始頁不能因文字副本重複計數。本機沒有額外 HTML 輸入；六頁線上 HTML 只留字典摘要，完整 Help、其他版本、圖表公式、API／實際 client 行為仍有覆蓋限制。

相關字典：[AEDT](aedt.md)、[Circuit](circuit.md)、[EMIT](emit.md)、[AnsysEM](ansysem.md)。

## 14. HFSS Scripting Guide chapter coverage

The v261 scripting guide contents span 31 chapters and 1,704 entries; this is a navigation inventory, not semantic review. Selected pages were reviewed only for the five chapters below. Other chapters remain pending. See the [chapter-by-chapter inventory](../maintenance/knowledge_dictionary_passes/2026-11-02/hfss_scripting_guide_chapter_coverage_20261103.csv).

| Chapter | Contents heading | Printed start | TOC entries | Review scope |
|---:|---|---:|---:|---|
| 1 | Introduction to Scripting | 1-1 | 93 | 62–68, 104–108 |
| 2 | Object-Oriented Scripting | 2-1 | 39 | 109–125, 136 |
| 3 | Application Object Script Commands | 3-1 | 1 | Pending source review |
| 4 | Desktop Object Script Commands | 4-1 | 108 | 262 |
| 5 | Running Instances Manager Script Commands | 5-1 | 3 | Pending source review |
| 6 | Project Object Script Commands | 6-1 | 64 | Pending source review |
| 7 | Design Object Script Commands | 7-1 | 127 | Pending source review |
| 8 | Model Setup Script Commands | 8-1 | 13 | Pending source review |
| 9 | 3D Modeler Editor Script Commands | 9-1 | 218 | 592–593 |
| 10 | Output Variable Script Commands | 10-1 | 9 | Pending source review |
| 11 | Reporter Editor Script Commands | 11-1 | 108 | 945–949 |
| 12 | Boundary and Excitation Module Script Commands | 12-1 | 144 | Pending source review |
| 13 | MeshSetup Module Script Commands | 13-1 | 38 | Pending source review |
| 14 | Analysis Setup Module Script Commands | 14-1 | 38 | Pending source review |
| 15 | Optimetrics Module Script Commands | 15-1 | 88 | Pending source review |
| 16 | Solutions Module Script Commands | 16-1 | 47 | Pending source review |
| 17 | Field Overlays Module Script Commands | 17-1 | 64 | Pending source review |
| 18 | Fields Calculator Script Commands | 18-1 | 35 | Pending source review |
| 19 | Radiation Module Script Commands | 19-1 | 48 | Pending source review |
| 20 | Radiation Setup Manager Module Script Commands | 20-1 | 8 | Pending source review |
| 21 | User-Defined Document Script Commands | 21-1 | 14 | Pending source review |
| 22 | User-Defined Solutions Commands | 22-1 | 5 | Pending source review |
| 23 | Network Data Explorer Script Commands | 23-1 | 43 | Pending source review |
| 24 | CompInstance Script Commands | (multiple) | 7 | Pending source review |
| 25 | Simulation Setup Commands | 25-1 | 16 | Pending source review |
| 26 | 2.5D Via Commands | 26-1 | 0 | Pending source review |
| 27 | Layout Scripting | 27-1 | 117 | Pending source review |
| 28 | Schematic Scripting | 28-1 | 87 | Pending source review |
| 29 | Definition Manager Script Commands | 29-1 | 109 | Pending source review |
| 30 | Core Global Script Context Commands | 30-1 | 6 | Pending source review |
| 31 | Example Scripts | 31-1 | 7 | Pending source review |

The five source PDFs contain 4,430 physical pages total. [PDF conversion inventory](../maintenance/knowledge_dictionary_passes/2026-11-02/hfss_conversion_inventory_20261103.csv) records catalog SHA matches, contiguous physical page markers, and per-file conversion status. This does not verify every figure, formula, or table. HFSS source PDFs are proprietary/confidential under their notice; follow the applicable license before sharing original text.


## 15. HFSS v261 Project Object 與 script object 路徑（有界核讀）

Project Object 是 Property Object 的子類。指南指出它沒有自己的 properties，因此手冊所列 `GetPropNames(bIncludeReadOnly)` 回傳空陣列；不過可從 project 物件呼叫 `GetPropValue(path)`／`SetPropValue(path, value)` 存取子物件屬性，例如設計內變數或結果報告屬性。`GetChildTypes()` 回傳 `Design` 和 `Variable`，用 `GetChildNames(type)` 分別列出設計或專案變數，再用 `GetChildObject(path)` 取得子物件。切勿將「Project Object 沒有自己的屬性」誤讀成不能透過它操作子物件。

相鄰的 Design Object 也沒有自己的 properties，但其子類型包括 `Module`、`Editor`、`Variable`；可沿 `Results/...` 路徑存取報告，或沿變數路徑讀寫設計變數。可用 Module 名稱依 design／solution 類型而異；指南另舉 HFSS、HFSS 3D Layout、Maxwell、Q3D、Icepak 等設計所暴露模組的差異。不能把某一 design 的模組樹推廣至全部 Ansys Electronics 設計。

以上摘要僅核對 v261 scripting guide 實體 PDF 頁 152–153，未逐項整理 Project Object 全部路徑語法或其他 Scripting Guide 命令條目；未執行腳本。

來源：[跨設計 Module 清單，實頁 137–140](../ANSYS_Document/_catalog/pdf_text_v4/c13dd9213c3841394ef42ef2298f26e1dcf877083937180f60fc6888c9654f73.md#pdf-page-137)；[Project／Design Object 實頁 152–153](../ANSYS_Document/_catalog/pdf_text_v4/c13dd9213c3841394ef42ef2298f26e1dcf877083937180f60fc6888c9654f73.md#pdf-page-152)；[本機 PDF](../ANSYS_Document/HFSS/v261/manuals/HFSSScriptingGuide.pdf)。來源 ID `ansys_e0fa0d611694014d037709e8`。


## 2026-11-04：Wave 7 本機來源盤點與限制說明

清冊的 11 筆來源包含 5 份 v261 PDF 與 6 筆官方線上摘要。PDF 原件、canonical 轉換稿與鄰接 Markdown 已核對雜湊。五份 PDF 共 4,430 實頁，兩套 Markdown 的頁標各自連續。線上摘要無本機正文，本批未擷取清冊所列 10 個網址。PDF 頁內讀序、圖表、公式與未核讀命令仍待核對。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/hfss_module_conversion_report_20261104.md)。
