# FENSAP-ICE 知識字典

本頁依 Ansys Help **v242（2024 R2）** Tutorial／Workbench Guide 與 **v261（2026 R1）** User Manual 整理。沿用先前 14 個官方 HTML 頁的有界摘要；2026-11-02 本次另核讀 10 個 v261 官方 HTML 頁，補上 DROP3D／ICE3D 的輸入、模型、輸出與限制。原文、圖表與附件未存成本機副本；RAG 收錄本頁摘要。兩版本分開使用，不推定跨版本相容。

## v242 Project／Run 與 Fluent 匯入

Project 建立時指定單位系統；Run 分別管理輸入、設定／執行與輸出。教程用 FENSAP airflow → DROP3D droplets → ICE3D icing 串接，拖放設定只複製共通參數，下游仍需模組專屬設定與已存在的上游結果。

Fluent 匯入要同目錄、同名的 `.cas(.h5)`／`.dat(.h5)` 才能同時轉成 airflow solution，否則可能只有 grid；網格座標需為公尺。邊界 tag 必須核對，v242 分別列入口、牆、出口、一般／軸向對稱、actuator disk 與 non-conformal interface。收斂需同時看殘差與整體量；DROP3D 特別以 Total Beta 及其變化追蹤進展，不能只憑平均殘差判定。

來源：[Tutorial 第 1 章](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/fensap_tut/ch01.html)（`official_fensap_tutorial_ch01_v242`，§1.1–1.3、1.7）。案例設定不是通用物理驗收門檻。

## v242 Workbench Update 的依存範圍與 Reset 資料刪除

| 操作 | 文件所述範圍 |
|---|---|
| Cell 的 `Update` | 更新該 cell 與使它有效所需的 upstream cells，先傳入新的上游資料。 |
| System 的 `Update` | 更新該 system 過期的 cells，以及必要的上游 systems。 |
| Project／Toolbar 的 `Update` | 更新專案內所有過期 cells。 |
| Setup cell 的 `Reset` | 移除 mesh reference、刪除設定檔、將 cell properties 回復預設。 |
| Solution cell 的 `Reset` | 刪除相關 solution／output files，並回復 cell properties。 |

Update Solution 會啟動對應 FENSAP／DROP3D／ICE3D 並計算；Reset 會影響已保存資料。v242 頁面另註 Reset 功能有限，需配合該版 Release Notes；本輪沒有執行以上操作。

來源：[Using the Update Command](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/fensap_wb/ch02s02.html)（`official_fensap_wb_update_v242`）、[Deleting Solution and Setup Cell Data](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/fensap_wb/ch02s03.html)（`official_fensap_wb_reset_v242`）。

## v242 Transfer Data、Shared Data 與 Mesh Import

Workbench 將「相同 cell 類型共用同一資料」稱為 shared data connection，將一個 cell 的輸出作為另一 cell 輸入稱為 transfer data connection。但 v242 FENSAP-ICE 頁明載 **FENSAP-ICE based systems 不支援 shared data connections**，transfer 功能亦有限，不能只由 Project Schematic 出現可連接目標就推定完整工作流程有效。

Mesh／ICEM CFD 的 Mesh／Model cell 可經 Mesh Import component 接到多個 Setup Flow cells；來源指定上游輸出 Fluent `.msh`，再轉為 FENSAP `.grid`。從 Solution 向新 Setup transfer 的例子只傳 mesh，不傳 settings。仍需核對連接的實際資料與版本限制。

來源：[Connecting Systems in Workbench](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/fensap_wb/ch02s06.html)（`official_fensap_wb_connections_v242`，§2.6–2.6.1）。圖示與所有拖放組合未目視或實測。

## v242 Design Point 的 Retain 與結果保存

建立 input／output parameters 後，Workbench 加入 Parameters cell 與 Parameter Set；可在 Design Points table 指定輸入並更新單一或全部 design points。預設只保存 `Current` 列的計算資料。若要後處理其他 design point，應在更新前勾其 `Retain`；之後可 `Set as Current` 存取或匯出為獨立專案。這是資料保存契約，不能由 output parameter 已有數值推定全部場結果都仍在專案。

來源：[Working with Input and Output Parameters](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/fensap_wb/ch02s08.html)（`official_fensap_wb_parameters_v242`，§2.8）。

## v242 Setup／Solution 的匯入、保存與同步

FENSAP-ICE analysis system 的 mesh 應由 **Setup Flow** 定義，不從 Setup Droplets／Ice 定義。`Define from file...` 可選擇將 grid 存入專案或保留外部路徑；匯入 restart solution 視為 start-up data，不能將 Solution cell 當成已求得結果，文件預期狀態是 Update Required。

| 資料類別 | 文件定位與保存注意 |
|---|---|
| Setup data | 包含 mesh 與輸入設定，供從頭開始計算。圖形視窗用 `Save and Close` 保存；`Save` 同步設定至 Workbench Properties。 |
| Solution data | 包含計算結果及可作 restart 的資料。從 Solution cell 啟動會讀 mesh、輸入與 log；計算後的 solution 檔需另用 Viewmerical 載入查看。 |

若 FENSAP-ICE 圖形視窗已開啟，另從 Workbench Properties 修改設定，文件要求用 `Sync parameters` 同步。不要以兩處介面看似開啟就假定設定一致。

來源：[Importing FENSAP-ICE Files](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/fensap_wb/ch02s01.html)（`official_fensap_wb_import_v242`）、[Saving Your Work](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/fensap_wb/section_pbq_nw4_1y.html)（`official_fensap_wb_save_v242`）。

## v242 Interrupt／Abort 的原文限制與矛盾

§2.4 正文將 `Stop`／Workbench `Interrupt` 描述為等待可保存資料的時點；`Kill`／`Abort` 則立即中止。可是同頁 Caution 又說這些選項尚未完全穩定，只認定 Workbench Progress pane 的 Interrupt 可安全停止，且描述為完成該 cell 指定迭代後才停、不繼續下個 cell。前段說中斷後狀態為 Interrupted／Update Required，Caution 後又寫 Up-to-Date。

因此本頁只保留上述**同版來源差異**；不把按鈕名稱當作跨版本、立即停止或資料已保存的保證。`Accept Interrupted Solution as Up-to-Date` 是使用者接受 cell 狀態的操作，不是物理收斂證明。

來源：[Interrupting a Calculation](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/fensap_wb/ch02s04.html)（`official_fensap_wb_interrupt_v242`）。未啟動、停止或接受任何計算結果。

## v261 Grid Assignment 與一致的 Reference Conditions

輸入參數含 grid-dependent boundary conditions，應先指定 grid。Model panel 重新指定 grid 時只接受 FENSAP format，該路徑不會自動檢查格式並提示轉換；換成不同 grid 後需重查 boundary conditions。

FENSAP／DROP3D 以無因次形式求解，reference conditions 包含 characteristic length、velocity magnitude、static pressure、static temperature。結冰流程各 solver 應使用一致參考值；drag & drop 可傳遞它們。文件用這些值建立物性與 reference Reynolds／Mach，並寫入 log。這不代表只要參考值一致，模型或收斂就已獲驗證。

來源：[The Physical Model](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/fensap_manual/section_fpr_5jf_2w.html)（`official_fensap_physical_v261`，§4.1.1）、[Flow Conditions](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/fensap_manual/section_aqr_5jf_2w.html)（`official_fensap_conditions_v261`，§4.2–4.2.1）。公式與部分符號在原頁為圖片，本輪未轉錄。

## v261 Steady／Unsteady 與 CFL Relaxation

| 模式 | 原文工作方式與區分 |
|---|---|
| `Steady` | 用與局部網格相關的時間推進取得穩態；達最大步數或 residual criterion 即停。遇到數值不穩可檢查 CFL，但仍須核對網格與邊界條件。 |
| `Unsteady – Constant time step` | 指定秒為單位的 time step／total time；每個 time step 做 Newton linearization。 |
| `Unsteady – Dual time stepping` | physical time step 內另以 pseudo-time iterations 收斂；兩種迭代尺度不能混為同一物理時間。 |

Variable relaxation 會把 CFL 從 1 漸增到設定值；相同條件 restart 時文件建議關閉，避免再次由 1 起跑，邊界條件改變時仍可能需要。頁中預設值與收斂條件屬 v261 solver 設定，未當成所有結冰案例的通用驗收值。

來源：[Solver Parameters](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/fensap_manual/section_err_5jf_2w.html)（`official_fensap_solver_v261`，§4.5.1–4.5.2）。

## v261 模組角色與單參數重算表

`FENSAP` 提供氣流，`DROP3D` 是 Eulerian 水滴／冰晶撞擊模組，`ICE3D` 計算冰成長與水膜回流；`OptiGrid` 用於網格適應，`CHT3D`／`C3D` 處理耦合熱傳／固體導熱。DROP3D 提供濃度、速度、collection efficiency、shadow zone 與 impingement limits；不能把技能中的 droplet trajectories 一詞直接解讀為必須使用 Lagrangian 注入追蹤。

User Manual Table 1.4 對未保護表面的單一參數變動列出以下重算範圍：

| 只改變此參數 | FENSAP External | DROP3D | ICE3D |
|---|---|---|---|
| Incidence、TAS、Altitude | 重算 | 重算 | 重算 |
| OAT | 表中未勾選 | 表中未勾選 | 重算 |
| MVD | 表中未勾選 | 重算 | 重算 |
| LWC | 表中未勾選 | 表中未勾選 | 重算 |

此表假設其他條件不變；若變動同時影響其他物理量，須一起判斷，不將表格當成任意重用氣流解的保證。

來源：[FENSAP-ICE System §1.4／Table 1.4](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/fensap_manual/section_vcr_zmc_px.html)（`official_fensap_system_v261`）。

## v261 DROP3D 的 Grid／Air Solution 輸入

DROP3D 除 grid 外還需要 air solution。文件建議將 FENSAP configuration 拖到 DROP3D configuration，以帶入檔案與 reference flow conditions；也可由 Input files 重新指定。讀取 grid 會辨識 boundary conditions，換 grid 後必須重新檢查對應邊界參數，不能只沿用先前設定。

來源：[Assigning Grid and Air Solution Files §5.1](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/fensap_manual/section_bq5_lkf_2w.html)（`official_fensap_drop_inputs_v261`）。

## v261 LWC、MVD 與 Droplet Distribution

`LWC` 是空氣中水滴的密度；球形單一粒徑通常取樣本分布的 `MVD`，Droplet diameter 單位為 microns。`Monodisperse` 用單一直徑；Langmuir B–E 或 Custom distribution 分別計算各粒徑後做質量加權。Custom 的 cumulative diameter 按由大到小輸入，各權重合計 100%。

§5.4 的 segregated 模式先解氣流再解粒子，考慮氣流影響粒子；這段說明不能用來否定第 11 章另述的 coupled multiphase workflows。粒子與氣流的 reference Reynolds／Mach 等條件須相符。

來源：[Particle Conditions §5.4.1–5.4.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/fensap_manual/section_nq5_lkf_2w.html)（`official_fensap_particles_v261`）。

## v261 ICE3D 的 Glaze、Rime 與 Water Film

| Ice–Water Model | 文件所述工作範圍與必要輸入 |
|---|---|
| `Glaze - Advanced` | 可切換 film-only、glaze 與 dry-ice 狀態；需有效 heat flux、shear stress。Adiabatic air solution 需先算 EID。 |
| `Rime` | 低溫或低 water catch 的簡化；全部撞擊水凍結、無 runback、不解能量方程。即使可用 inviscid air solution，忽略黏性仍可能改變停滯點與 collection efficiency。 |
| `Water Film` | 無水滴凍結、只有表面水流回流的情況。 |

Grid／air／droplet／crystal solution 應先於 grid-dependent 邊界設定指定。旋轉域輸入向量按 inertial／absolute frame 儲存；第三方解若使用不同座標框架，須先核對。

來源：[Model Setup §6.2.1–6.2.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/fensap_manual/section_igl_nkf_2w.html)（`official_fensap_ice_model_v261`）。

## v261 Reference Air Temperature 與 Icing Air Temperature

ICE3D 的 characteristic length、reference velocity／pressure／temperature 應與輸入氣流及粒子解相同，用於熱通量與 heat-transfer coefficient 的換算。實際結冰雲溫是 `Icing air temperature`，可與原氣流 reference temperature 分開；偏離原溫度過大會忽略 Mach 等改變，原文要求謹慎，內流／渦輪機也不建議用此方式掃描結冰條件。

LWC 在其他氣流條件相同時可作降低 LWC 的 scaling factor；這不是對任意增幅或耦合條件的重用驗證。Droplet diameter 在本節只用於 beading nucleation 初始化，與 DROP3D 中粒徑影響撞擊解的用途不同。

來源：[Icing Conditions §6.3.1–6.3.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/fensap_manual/section_xgl_nkf_2w.html)（`official_fensap_ice_conditions_v261`）。

## v261 DROP3D Output 的覆寫與 SLD 中間解

Output 可只存 Final solution，或每 N 次 iteration 存檔；後者可選 `Overwrite` 覆寫或 `Do not overwrite` 編號保存。原文的建議保存間隔不是通用收斂門檻。SLD 的 By body force 模式在 activation／delay 條件達到時，另存各粒徑的 `droplet.primary`，表示施加 body force 前的解，可用於 restart 或比較撞擊分布。

來源：[DROP3D Output §5.7](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/fensap_manual/section_jr5_lkf_2w.html)（`official_fensap_drop_output_v261`）。

## v261 ICE3D Output 與 IPS Load 的資料差異

| 檔案 | 有界用途 |
|---|---|
| `swim.log`／`iceconv.dat` | 條件、迭代與 mass／energy balance；film height、溫度及冰成長歷程。 |
| `map.grid`／`ice.grid` | 起始／結冰後 flattened surface grid，disabled walls 不在其中。 |
| `swimsol` | film height、ice growth／thickness 等解，搭配表面 grid 載入。 |
| `timebc.dat`／`roughness.dat` | ALE 位移資料／後續 shot 使用的表面粗糙度。 |
| `ice.tin`／`ice.stl` | 結冰表面的 CAD／remeshing 幾何。 |

編號輸出保留六位數尾碼，未編號檔仍代表最新狀態。Grid displacement 可選 ALE、Fluent Meshing 或 Custom。啟用 `Compute IPS load conditions` 時，`swimsol` 改存 running-wet／fully-evaporative 所需熱負載，不含一般 ice growth 欄位，且不寫 `ice.grid`；不可當成一般結冰結果後處理。

來源：[ICE3D Out §6.6.1–6.6.3](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/fensap_manual/section_qhl_nkf_2w.html)（`official_fensap_ice_output_v261`）。

## v261 Fluent Icing 的 Workbench Extension 入口

Workbench 的 `Fluid Flow - Icing (Fluent)` system 連接 Fluent component airflow，並用 DROP3D／ICE3D 設定水滴與結冰，可將結冰後網格供後續步驟與 CFD-Post／Viewmerical 查看。Toolbox 入口要求先從安裝目錄的 `v261\fensapice\workbench` 安裝 `FENSAPICE-WB` extension，再透過 Extension Manager 載入。這是 v261 文件的入口契約，未執行安裝或更新。

來源：[Fluid Flow - Icing (Fluent)](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb2_help/wb2h_FFIfluent.html)（`official_fensap_wb_fluent_v261`）。

## v261 Remeshing Script 與 Queued License 限制

Known Limitations 指出 ICE3D 的 `Remeshing - Fluent Meshing` scripts 不可直接跨平台移植；須轉換 `custom_remeshing.sh` 的文字格式或重新載入平台範本。GUI 在 queued job 執行前關閉也可能使原 license-sharing context 失效；文件列出 queue header／`NTI_NO_LICENSE_SHARING` 的處理方式。此處只記錄限制及查閱入口，不執行環境設定或排程。

來源：[Known Limitations in 2026 R1 §1.8](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/fensap_manual/ch01s08.html)（`official_fensap_limitations_v261`）。

## 來源盤點與未完成範圍

本機 `_catalog/documents.json` 以 product／title／path／URL 全域搜尋 `fensap`、`DROP3D`、`ICE3D`，沒有官方原件；`product=fensap_ice` 的 SQLite 只有內部 icing note 與本字典。以下是線上核讀摘要，官方 HTML 正文、圖片、教學 ZIP 與 PDF 均未快取或加入全文索引。

章節入口：[Tutorial Guide v242](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/fensap_tut/fensap_tut.html)（`official_fensap_tutorial_v242`）、[Workbench Guide v242](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/fensap_wb/fensap_wb.html)（`official_fensap_workbench_v242`）、[Flow Solution v261](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/fensap_manual/chapter_fjr_5jf_2w.html)（`official_fensap_manual_v261_ch4`）。

| 來源範圍 | 本輪存取狀態 | 仍缺內容 |
|---|---|---|
| v242 Tutorial index／第 1 章 | 公開 HTML 可讀。 | 全部進階教程、案例輸入與圖像未核讀。 |
| v242 Workbench index／7 個子頁 | 公開 HTML 可讀；頁尾有 proprietary／confidential 權利聲明。 | 所有 system-specific 設定、Release Notes 限制與跨版本行為。 |
| v261 Flow Solution／Physical Model／Flow Conditions／Solver Parameters | 正規 `Views/Secured` URL 可讀；舊小寫路徑曾回 cache miss。 | Boundary Conditions／Domains／Output、圖像公式與全部物理模型。 |
| 內部 icing skill／note | 本機可讀，非官方規格。 | 本次已對應 v261 LWC／MVD、Eulerian impingement 與 rime／glaze 有界定義；完整模型、驗證案例及公式仍未覆核。 |

原「技能列出的飛機結冰主題」已以本次 v261 官方來源對應指定術語，列為有界完成；兩個 `source_online_partial` 父題保留。新舊有界子題都只表示本頁指定章節已核讀，不表示 FENSAP-ICE 全模組或所有結冰物理均已整理完成。手冊其他章節入口可查 [v261 User Manual 目錄](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/fensap_manual/fensap_manual.html)（`official_fensap_manual_index_v261`）。

內部參考：[Polyflow／FENSAP-ICE Skill](../../agents/skills/fluids-cfd/ansys-polyflow-icing/SKILL.md)（`agents_skills_fluids-cfd_ansys-polyflow-icing_SKILL`）、[Icing setup note](../../agents/skills/fluids-cfd/ansys-polyflow-icing/references/icing_physics_setup.md)（`agents_skills_fluids-cfd_ansys-polyflow-icing_references_icing_physics_setup`）。本輪未重新轉檔、執行產品或觸及 REA 萃取內容。


## 2026-11-04：Wave 6 本機來源盤點與限制說明

本批核對本機 catalog 0 筆；`sources.csv` 的 25 列由 14 筆 v261、10 筆 v242 線上摘要與 1 筆內部 note 組成。24 筆線上摘要沒有本機正文或可驗證的正文 hash；僅內部 note 有本機路徑、115 字元及來源 SHA-256。線上未快取或具登入／授權限制的主題保留為缺口，未推造未核實的 API 簽名或執行求解。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/fensap_ice_module_conversion_report_20261104.md)。
