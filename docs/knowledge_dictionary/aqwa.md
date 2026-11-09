# ANSYS AQWA 知識字典

本頁依公開可讀的 Ansys Help **Release 2026 R1（v261）** 章節整理。2026-11-05 已保存 935 份官方 HTML、1 份 234 頁 Theory PDF 的原件與逐頁文字轉換，並納入本機 DocSearch；同日新增 mass／CG、單位、平衡、纜索、Response 與 RAO 的有界入口。圖表語意、掃描/OCR、完整操作驗收與分享權限仍有明列缺口。

## 文件組成與查閱範圍

v261 文件集將 Workbench 操作、直接 solver 輸入與理論分別交給 User’s、Reference、Theory Manual；AQL、Graphical Supervisor、Aqwa2Neut、AqwaReader、AqwaFlow、AqwaWave 另有手冊。v261 User’s Manual 目錄可導向 geometry、connections、analysis settings、environment、results 與 hydrodynamic add-ons；目錄存在不代表其全部章節已核讀。

來源：[v261 Documentation Set](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/ai_sinfo/aqwa_intro.html)（`official_aqwa_docset_v261`）、[User’s Manual 目錄](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/wb_aqwa.html)（`official_aqwa_user_v261`）、[Theory HTML 目錄](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/aqwa_thy/aqwa_thy.html)（`official_aqwa_theory_html_v261`）、[Reference HTML 目錄](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/aqwa_ref/aqwa_ref.html)（`official_aqwa_reference_v261`）。先前 v2611 文件集來源列保留，未據此推定兩版內容相同。

## v261 Project Schematic、mesher 與資料庫重用界線

Hydrodynamic systems 不支援 Project Schematic 的 Duplicate／Reset；與其他類型 analysis system 共享資料時，只有 Geometry cell 可共享。外部網格流程先建立獨立 Mesh 與 Hydrodynamic Diffraction systems，再手動將 Mesh cell 接到 Model cell；Aqwa 內的網格成為唯讀，修改須回上游 Mesh component。內建 mesher 對簡單模型可能足夠，外部 Meshing 可提供更多控制。

Hydrodynamic Diffraction 可只做 Hydrostatics（stages 1、2）或完整 hydrodynamic results。完整分析建立包含 RAO／QTF 的係數資料庫；某些只改變 RAO／QTF、未改變 wave loads、frequency-dependent added mass／radiation damping 的變更，可部分重用既有資料庫，Messages 會提示。此條件不是任意模型可跳過重新求解的保證。

來源：§4 [Workflow and Systems](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/aqwa_workflow.html)（`official_aqwa_workflow_v261`）、§4.1 [Diffraction Workflows](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/aqwa_hydro_dif_workflows.html)（`official_aqwa_dif_workflows_v261`）、§4.2 [Diffraction System](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/AQWA_HD_Analysis.html)（`official_aqwa_dif_system_v261`）、§5.1 [Create System](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/aqwawb_create_system.html)（`official_aqwa_create_system_v261`）。

## v261 Geometry 座標、對稱與分析適用性

靜水面位於全域 XY、Z 向上、海平面 Z=0；水深是 diffraction 的海床邊界條件。Water Size X／Y 只改圖形顯示範圍。全域對稱面可選 XZ、YZ 或兩者，建模需配合半／四分之一幾何及 Part Transform；不能把局部座標對稱直接視為全域對稱。

| Geometry 選項 | 來源明列的適用範圍 |
|---|---|
| Tube Drag Coefficients／Scale Factor for Model Test Simulation | Stability／Time Response；不適用 Hydrodynamic Diffraction 或 Frequency Statistical。 |
| Seabed Inline／Lateral Friction | 使用 Cable Dynamics 的 Time Response。 |
| Composite Cable Seabed | 用於特定 Nonlinear Catenary Cable；不使用於 Hydrodynamic Diffraction。動態與非動態 cable 的接觸規則須分開查原節。 |

來源：§5.2.2 [Configuring the Geometry](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/AQWA_Geometry.html)（`official_aqwa_geometry_v261`）。公式以圖片呈現的部分未轉錄。

## v261 Mesh 唯讀狀態與 failure 分類

外部 Mesh system 或特定 `.DAT` 匯入流程會令 Aqwa Mesh 唯讀；suppressed parts／bodies 不產生網格，也不出現在 mesh-based results。`Display Mesh Metric = Failing Panels` 顯示失敗分類；有 fatal element 時不能執行 Hydrodynamic Diffraction。

| 檢查 | v261 此頁所列界線 |
|---|---|
| Aspect ratio／相鄰元素面積比／shape factor | 分別為 `< 0.333`、`> 3`、`< 0.2` 時失敗。 |
| Warping factor | `>= 0.1` 產生 warning，不計入 Minor Failure Rate。 |
| Centroid proximity | 一般界線為任一元素 effective radius；fatal 界線為其 `0.1` 倍。 |
| Element–seabed proximity | 小於半個 effective radius 為 fatal。 |
| Mesh connectivity／fluid surface crossing | 邊由多於兩個元素共享，或 diffracting element 穿越水線／適用 tank fluid level，為 fatal。 |

這些是該版本的模型檢查，不能替代網格收斂或工程結果驗證。

來源：§5.3 [Mesh](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/AQWA_Mesh.html)（`official_aqwa_mesh_v261`）。

## v261 Wave Directions、對稱與 Forward Speed

Wave Directions 可定義單一方向或方向範圍；Forward Speed 沿正 X。方向範圍由全域對稱設定限制：

| Symmetric Planes | Wave Range |
|---|---|
| None | -180° 到 +180° |
| XZ | 0° 到 180° |
| YZ | -90° 到 +90° |
| XZ 與 YZ | 0° 到 90° |

方向總上限是每個 structure 41 個，包含對稱方向；單／雙對稱對應頁面列的 21／11 個方向。Forward Speed 的 Froude number 估計須先產生網格，多 part 時取最小 part，估計值大於 0.3 會警告精度可能受影響；此警告值不是跨案例的工程驗收門檻。

來源：§5.12.2 [Wave Directions](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/AQWA_Wave_Directions.html)（`official_aqwa_wave_directions_v261`）。

## v261 Wave Frequencies 與 Convolution 前置條件

Program Controlled frequency range 的下限依水深與 0.1 rad/s 取較大值，上限依網格；間距可按 frequency 或 period。Manual Definition 可改單一頻率或範圍；重複頻率會移除，增加頻率數會線性增加求解時間。後續 Hydrodynamic Response 若使用 Convolution，前置 diffraction／radiation 至少需要 5 個 wave frequencies，且範圍須足夠涵蓋 radiation force 計算。

來源：§5.12.3 [Wave Frequencies](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/AQWA_Wave_Frequencies.html)（`official_aqwa_wave_frequencies_v261`）。該頁頻率下限公式為圖像，本輪未轉錄公式。

## v261 Diffraction Settings 的輸出與 Moonpool 條件

| 設定 | 來源所述用途或限制 |
|---|---|
| Generate Wave Grid Pressures | Wave Surface Elevation／Air Gap contour 需要此選項；Standard／Fine wave grid 為 81×51／161×101 nodes。 |
| Calculate Extreme Low/High Frequencies | active Moonpools 必須啟用，否則錯誤並停止求解。 |
| Ignore Modeling Rule Violations | 來源只建議用於 minor 且難修正的違規；不代表可略過 fatal mesh 或物理查核。 |
| ASCII Hydrodynamic Database | 將 `.HYD` 輸出成 compact ASCII `.AH1`。 |
| MCOL Hydrodynamic Database | 輸出 `.mco`；不含 internal tank 對 hydrostatic stiffness 的影響。 |

Analysis Settings／Ocean Environment 的可用欄位與物件依 Diffraction／Response 及 computation type 改變，不應把上表套到所有 system。

來源：§5.11.2 [Hydrodynamic Diffraction Settings](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/AQWA_analysis_options_HD.html)（`official_aqwa_diffraction_settings_v261`）；父節 [Analysis Settings](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/aqwa_est_analysis_settings.html)（`official_aqwa_analysis_settings_v261`）、[Ocean Environment and Forces](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/AQWA_Analysis.html)（`official_aqwa_environment_v261`）。

## v261 結果失效與 Co-simulation 匯入界線

Solution 可在求解前後新增 result object。輸入變更會使既有結果標為過期且暫不可用，但 solver files 仍保留，除非執行 Clear Generated Data；改圖的 Axes Selection 也需更新結果。Co-simulation 匯入的檔案必須源自所選 Hydrodynamic Response 產生的 Aqwa-FMU package，且生成後模型／設定不能改動。匯入會複製對應結果檔並採用 co-simulation 時間設定；重新開啟 editor 後再評估。active Moonpool 模型只提供 Hydrodynamic Diffraction 類結果。

來源：§5.13 [Solution](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/AQWA_Results.html)（`official_aqwa_solution_v261`）。未匯入檔案或執行 Clear Generated Data。

## v261 Geometry 的 body 類型與 surface normals

Aqwa 水動力系統處理 Line Bodies 與 Surface Bodies；每個 vessel／structure 應組成一個 Part。水線在 XY 的 Z=0、Z 向上。外表面 normal 向外；Internal Tank 與 Moonpool 牆面向包圍的流體，Moonpool 孔口匹配面及自由面向上。Line Body 的截面支援 tubular；其他截面須補定義 Aqwa 所需資料。

來源：[User’s §5.2.1](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/AQWA_Modelling.html)（`official_aqwa_modeling_requirements_v261`）。

## v261 Point Mass、CG 與 inertia 必填資料

Surface Body 本身不直接帶 mass，需用 Point Mass 等物件表達。Manual 要輸入質量與位置；Program Controlled 依網格及既有質量／浮力物件求質量與水平位置，使總質量對應排水量、CG 與浮心位於同垂線。Z 位置與 inertia／radius of gyration 始終由使用者提供；不能由「自動質量」推成已驗證壓載及慣量。

來源：[User’s §5.5.3](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/AQWA_Elem_PMass.html)（`official_aqwa_point_mass_v261`）。

## v261 一致單位、波向與 phase lag

Reference Manual 要求整套長度、力、質量及密度一致；旋轉 motion 輸出為 degrees，而 stiffness／damping 的旋轉項以 radians 表達。這不是匯入其他單位數據時可省略轉換的保證。

Wave／wind／current 的方向從全域 +X 朝傳播方向、俯視逆時針量測；沿 +X 為 0°、沿 +Y 為 90°。正 phase 表示參數峰值落後波峰通過結構 CG。Theory §1.3 變數說明將 phase angle 列為 rad/s，與同頁角度描述及 Reference §1.2.3 的 degrees 不一致；本頁採 lag 定義並保留單位疑義，不轉錄該圖片公式。

來源：[Reference §1.4](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/aqwa_ref/aqwaref_unitsconv.html)（`official_aqwa_units_v261`）、[Reference §1.2.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/aqwa_ref/aqwaref_intro_wwc_direction.html)（`official_aqwa_direction_v261`）、[Reference §1.2.3](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/aqwa_ref/aqwaref_intro_phaseangle.html)（`official_aqwa_phase_v261`）、[Theory §1.3](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/aqwa_thy/aqwathy_dirandangle_conv.html)（`official_aqwa_theory_direction_phase_v261`）。

## v261 Hydrostatic Equilibrium 與結果查閱

頻域小振幅運動以平衡浮態為基準。只受重力與靜水壓的自由浮體需重量等於浮力（buoyancy）、力矩合為零，CG 與浮心同垂線；有額外靜力時不能直接套用這個簡化條件。非平衡的指定位置會輸出不平衡力／矩，不能只看幾何姿態視為收斂。

Hydrostatic Results 在 hydrostatic／hydrodynamic solve 後顯示 CG、浮心與漂浮中心；詳細資料在 Properties。Moonpool 另顯示其自由面位置／面積與 pressure-mode stiffness。來源未給通用百分比驗收門檻。

來源：[Theory §3.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/aqwa_thy/aqwathy_hydro_eqlib.html)（`official_aqwa_theory_equilibrium_v261`）、[User’s §5.13.1](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/AQWA_Results_Hydrostatics.html)（`official_aqwa_hydrostatic_results_v261`）。

## v261 Additional Stiffness／Damping 矩陣輸入

Additional Hydrodynamic Stiffness 是線性靜水恢復力的附加矩陣，與 diffraction 定義位置有關；後續 motion 初始位置不同可產生使結構返回該位置的恢復力，應檢查所得力是否符合意圖。CSV 必須 6×6；匯入單位預設跟專案顯示單位一致，另可指定匯入長度／力／旋轉單位。

Additional Damping 為全域方向、頻率無關的附加阻尼；每個 structure 同時只能有一個 active 定義，數值加到自動計算阻尼上。其 CSV 必須為 6×6（6x6），資料以逗號、tab 或單一空格分隔；匯入時預設採用專案顯示單位，也可指定匯入的長度、力及旋轉單位。這些欄位不是自動校準阻尼或剛度的工具。

來源：[User’s §5.5.9](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/AQWA_Elem_Stiff_Matrix.html)（`official_aqwa_stiffness_v261`）、[User’s §5.5.11](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/AQWA_Elem_Damping_Matrix.html)（`official_aqwa_damping_v261`）。矩陣公式圖片未轉錄。

## v261 Cable 類型、slack 與 catenary 節數

Cable 可選 Linear Elastic、Polynomial、Steel Wire 或 Catenary；同一根 cable 不能兩端都連到同一 structure。Linear Cable 是只受拉的 spring，鬆弛時 tension=0；剛度不能為零。Catenary 可由最多 10 段及 9 個 joints 組成。它的 cable dynamics 需全域分析選項與 cable 本身共同啟用；動態分析不使用 cable-specific seabed slope。

來源：[User’s §5.10.1](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/aqwa_cables.html)（`official_aqwa_cables_v261`）。滑輪與多項式圖片公式未轉錄。

## v261 Dynamic Catenary 的耦合與力項界線

動態複合纜以離散質量及力項求 cable／vessel 相互影響，納入質量、drag、軸向 tension 與 bending。此 Theory 章節假設海床水平平坦；不包含 cable 的 wave excitation force 或 torsional deformation。頻域非線性項會線性化，時間域才包含 seabed friction。不能把這些模型界線擴張成任意海床或高階纜索模型已驗證。

來源：[Theory §9.7](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/aqwa_thy/aqwathy_moorfend_dynamiccatenary.html)（`official_aqwa_dynamic_catenary_v261`），特別是 Table 9.1；未重建完整力矩陣或公式。

## v261 Tether／Riser 連接與軸向疑義

Tether/Riser 連固定點與 structure，可組成最多 24 sections、250 elements。User’s §5.10.2 先將 TLA Z 定在固定點朝結構的方向，後面卻把 axial stiffness 描述成 TLA X、rotations 為 Y/Z。Theory §10.1 區分 TEA 與 TLA，installed tether 的 TEA x 沿纜，TLA 軸由 TEA 重排；§10.2 以 TEA x 作 inline constraint。兩套敘述不能直接混用。

**原文交叉核對（v261）：**User’s 將 TLA Z 定義為從 Start Fixed Point 指向 End Connection Point，TLA X 位於 FRA XY 平面且垂直於 Z；同頁又稱端部 Axial Stiffness 沿 Local Tether/Riser X。Theory §10.1 對 installed tether 則定義 TEA x 從 anchor 指向 vessel，並明列 TLA x/y/z 分別沿 TEA y/z/x；Theory §10.2 把端部 inline stiffness／位移寫作 TEA x。這些文字在已核對章節中沒有明確說明 User’s 的「Axial Stiffness」欄位如何轉換到 Theory 的 TEA inline stiffness，也未解釋軸標記差異。

**使用界線：**可確認的是各頁原文的軸定義與標籤如上；不能據此宣稱 GUI 軸向已與 Theory 一致，也不能把理論章節中的 TEA inline 直接等同 GUI 欄位。設定或解讀前需依實際產品版本，在 Workbench Help／欄位說明或可追溯的 Ansys 支援答覆中確認映射。此來源疑義子題維持 `pending_source_review`，不是完整操作指引。

來源：[User’s §5.10.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/aqwa_tethers_risers.html)（`official_aqwa_tethers_v261`）、[Theory §10.1](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/aqwa_thy/aqwathy_tethers_stiffness.html)（`official_aqwa_tether_matrices_v261`）、[Theory §10.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/aqwa_thy/aqwathy_tethers_constraints.html)（`official_aqwa_tether_constraints_v261`）。

## v261 Hydrodynamic Response 連接與計算型態

首個 Response 必須連 upstream Diffraction，並共享其 Solution；內建網格共享 Geometry／Model／Solution，外部網格共享 Model／Solution。Stability 可接後續 Stability、Time 或 Frequency，Time 只能接 Time，Frequency 沒有 downstream Response。

Computation Type 分 Stability、Time Response、Frequency Statistical。Stability 的 `Require Convergence for Subsequent Analysis` 可阻止未收斂結果往下傳。Frequency 分析若有 connections／joints，應先求平衡力；來源明示 Based on Geometry 需謹慎。Time 的 `Calculate Motions Using RAOs Only` 會抑制 RAO 以外運動，此時 wind、current、drift、mooring 不影響結構運動。

來源：[User’s §4.3](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/AQWA_HTR_Analysis.html)（`official_aqwa_response_system_v261`）、[User’s §5.11.3](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/aqwa_analysis_options_htr.html)（`official_aqwa_response_settings_v261`）。此處只整理連接與選項界線，未執行分析。

## v261 RAO 線性響應、作用點與圖形座標

RAO 描述 regular wave 下與波幅成比例的線性 harmonic response。多結構 motion equations 的 added mass／damping 可含結構間水動力耦合；該線性 hydrostatic stiffness 的結構間 off-diagonal blocks 為零。指定點的 RAO 可由 CG RAO 與 CG 到該點的向量換算，不能把不同作用點直接比較。

Workbench 圖可呈現 amplitude／phase 隨頻率及方向變化；圖形結果的座標方向需看所選結果類型，該頁說明其圖形輸出採 global axes。Stability 的非收斂迭代值沒有物理解讀依據，不能視為時域歷程。

來源：[Theory §4.4](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/aqwa_thy/aqwathy_SDM_RAOs.html)（`official_aqwa_theory_raos_v261`）、[User’s §5.13.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_aqwa/AQWA_Results_Graph.html)（`official_aqwa_results_graph_v261`）。未轉錄方程圖片，也未由 RAO 推算任意非線性載荷。

## 內部技能範圍與工程查核入口

AQWA／Sound 共用 skill 的 AQWA 段落列出 ballast／CG、diffraction／radiation、RAO、mooring／tether 與二階漂移力；其水動力 note 很短，不能用來補齊版本或參數。上列官方章節已提供這些概念的查閱入口，Sound 心理聲學流程仍屬另一領域。

工程查核可依本頁回到：Geometry normals 與水線；一致單位及 mass／CG／inertia；波向／頻率與座標；穩定平衡後的 Response starting position；線性 RAO、纜索與 damping 的適用範圍。這個清單的整理已完成，工程允收門檻與實際模型驗證仍依個案及有效參考，不套用統一百分比。

## 本輪存取與來源缺口

2026-11-02 此次公開 web 核讀為 **23 個 HTML 可讀、1 個 PDF 因工具大小限制未取得**；HTML 頁尾均列 Release 2026 R1。失敗項為 [Theory PDF](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/pdf/Aqwa_Theory_Manual.pdf)（`official_aqwa_theory_v261`）。2026-11-04 重讀 v261 Theory §10.2；該頁明確寫 installed tether 端部 inline stiffness 對應 TEA x，仍未說明 User’s GUI X 欄位到 TEA x 的映射，故 Tether/Riser 疑義縮小為「跨手冊欄位／軸對應未說明」，不以工程常識補足。Theory phase angle 單位疑義亦仍保留。

**2026-11-04 歷史盤點：**當時本機 `Aqwa` 目錄只有 README；舊 documents catalog 與 conversion manifests 沒有 AQWA 條目。該狀態已於 2026-11-05 更新：新增原始官方來源及轉換稿並索引；細節與限制見下方 2026-11-05 批次記錄。舊目錄狀態不代表目前仍未轉換。

兩個原 `source_limited` 題已收束為「內部技能範圍」與「有官方依據的工程查核入口」；只表示這兩個有界摘要核對完成。官方來源、整體 workflow／環境三個父題仍為 `source_online_partial`，Tether 軸向子題為 `pending_source_review`。完整公式、solver record、所有連接／載荷、圖表及跨版本對照未完成。未求解、操作 GUI、執行 tutorial、做收斂或物理驗證。

內部參考：[AQWA／Sound Skill](../../agents/skills/multiphysics/ansys-aqwa-sound/SKILL.md)（`agents_skills_multiphysics_ansys-aqwa-sound_SKILL`）、[Diffraction／Radiation note](../../agents/skills/multiphysics/ansys-aqwa-sound/references/aqwa_diffraction_radiation.md)（`agents_skills_multiphysics_ansys-aqwa-sound_references_aqwa_diffraction_radiation`）。內部筆記與官方章節的來源性質不同。


## 2026-11-04：Wave 1 本機來源盤點與限制說明

本批是 2026-11-04 的初始盤點快照：當時核對 39 筆 sources，線上 Help 正文尚未完整快取。2026-11-05 官方全文補存與索引後，這段來源狀態由下方新批次記錄取代；尚未核實的工程主題仍保留為待覆核，不推測參數或執行求解。

詳細稽核數據見 [本批轉換報告](../maintenance/knowledge_dictionary_passes/2026-11-04/aqwa_module_conversion_report_20261104.md)。


## 2026-11-05 官方全文與本機導覽更新

本頁較早段落所述『原始 HTML 未保存』及 Theory PDF『工具大小上限』是先前批次狀態；本批已透過直接官方 HTTP 擷取補齊本機原件。既有繁中概念摘要保留，以下補充可追溯全文入口與剩餘邊界。

- 保存 936 個官方文件：935 HTML 與 1 份 234 頁 Theory PDF；所有 PDF 頁均有文字及連續頁標，版本以封面 Release 2026 R1／各 URL 標籤分開記錄。
- v261 擴展限於官方十套手冊目錄明列章節；v2611 文件集另存，未推定跨版本內容等同。34 個正文頁保留原 HTML，以保住 code、路徑、下標、巢狀表格和公式關聯；其餘採 Markdown 並保留可確認的 sup/sub 與複雜表格 HTML。
- 3210/3210 個唯一公式或圖片資產已保存；文字與圖檔保存不等同公式、圖表版面或物理模型已逐項驗證。

| 官方手冊入口 | 本機正文 |
|---|---|
| Aqwa Reference Manual（v261） | [目錄與來源](ANSYS_Document/AQWA/official_body_20261105/official_aqwa_reference_v261.md) |
| Aqwa Theory Manual（v261） | [目錄與來源](ANSYS_Document/AQWA/official_body_20261105/official_aqwa_theory_html_v261.md) |
| Aqwa User's Manual（v261） | [目錄與來源](ANSYS_Document/AQWA/official_body_20261105/official_aqwa_user_v261.md) |
| Aqwa Release Notes（v261） | [目錄與來源](ANSYS_Document/AQWA/official_body_20261105/official_aqwa_manual_99452fe1f455fe05.md) |
| Aqwa AQL Manual（v261） | [目錄與來源](ANSYS_Document/AQWA/official_body_20261105/official_aqwa_manual_2e8a5f68e0422772.md) |
| Aqwa Graphical Supervisor User's Guide（v261） | [目錄與來源](ANSYS_Document/AQWA/official_body_20261105/official_aqwa_manual_bc394fe8e39871ed.md) |
| Aqwa2Neut Manual（v261） | [目錄與來源](ANSYS_Document/AQWA/official_body_20261105/official_aqwa_manual_a11c450ffb1fe1b7.md) |
| AqwaReader Manual（v261） | [目錄與來源](ANSYS_Document/AQWA/official_body_20261105/official_aqwa_manual_37f272467df1e621.md) |
| AqwaFlow Manual（v261） | [目錄與來源](ANSYS_Document/AQWA/official_body_20261105/official_aqwa_manual_a17f454818c4d9a9.md) |
| AqwaWave Manual（v261） | [目錄與來源](ANSYS_Document/AQWA/official_body_20261105/official_aqwa_manual_166a78eebcdcdfea.md) |

Theory 全文：[逐頁 Markdown](ANSYS_Document/AQWA/official_body_20261105/official_aqwa_theory_v261.md)；[官方 PDF 原件](ANSYS_Document/AQWA/official_body_20261105/official_aqwa_theory_v261.pdf)。PDF 表格保留抽取文字，未重建所有儲存格或 OCR。

Tether/Riser 的 TLA/TEA 軸向映射疑義維持待覆核；取得全文未解決 GUI 欄位與 Theory 敘述的差異。其餘原 `source_online_partial` 主題轉為待來源語意覆核，沒有以下載成功推定所有主題完成。全文與衍生內容保留本機，團隊分享前仍需核對來源適用權限。
