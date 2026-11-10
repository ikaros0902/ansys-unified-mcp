# ANSYS domain skills：來源與能力對照

此文件記錄 skills 可依據的本機文件、版本標記與 MCP 支援邊界。文件檔名或安裝目錄不等於產品已安裝、授權可用或真機驗收通過。版本欄中的 2026 R1 對應 v261；v251/v252/v261 應各自查證，不以其中一版推定其他版本。

## 判斷規則分級

- **必要條件**：缺少即無法依目標物理問題建立可解模型，例如必要材料參數、載荷單位、有效 scoping、有效結果檔；錯誤須阻止或分類為不可驗證。
- **官方建議**：只在對應產品版本、分析類型、單元、材料和適用條件下採用，記錄手冊章節；不可擴大成跨分析硬門檻。
- **專案經驗值**：標為 heuristic，說明其適用模型、關注量、調整紀錄；不得偽裝成官方規範。

## 領域來源與能力矩陣

本機 ANSYS 文件根目錄以 `ANSYS_DOCS_ROOT` 指定。下列路徑相對於該根目錄；套件快照位於 repo 的 `docs/api_inventory/`。這些來源標記只代表已記錄的材料，不代表版本、授權或 runtime 已驗證。

| 優先級／領域 | 文件與 API 來源 | 現行技能路徑 | MCP 支援邊界／證據狀態 |
|---|---|---|---|
| P1 Mechanical | `Documentation_md/Ansys_Mechanical_Users_Guide.md`、`Ansys_Scripting_in_Mechanical_Guide.md`；repo 的 Mechanical v251 快照 | [Mechanical](../../agents/skills/structural-mechanics/ansys-mechanical/SKILL.md)、[PyMechanical](../../agents/skills/structural-mechanics/pymechanical-operations/SKILL.md) | 依現有 controller/session 能力判定；API 名稱不證明參數簽名或真機行為。產品與 SDK 版本分開記錄。 |
| P1 Mesh | `Documentation_md/Ansys_Mechanical_Users_Guide.md`、`Ansys_Scripting_in_Mechanical_Guide.md` | [Mesh](../../agents/skills/geometry-meshing/ansys-mesh/SKILL.md)、[Geometry router](../../agents/skills/domains/ansys-geometry-meshing/SKILL.md) | 指標須註明定義、單元、分析與求解器適用性；不把局部品質指標當成通用阻斷門檻。 |
| P1 SpaceClaim | `Documentation_md/SpaceClaim_Documentation.md`；repo 的 SpaceClaim v251 快照與 REA 證據 | [SpaceClaim](../../agents/skills/geometry-meshing/ansys-spaceclaim/SKILL.md)、[Geometry router](../../agents/skills/domains/ansys-geometry-meshing/SKILL.md) | v251 snapshot-only overload 不代表官方支援簽名；交換檔仍需檢查幾何、單位與特徵。 |
| P1 LS-DYNA | `Documentation_md/LS-DYNA_Users_Guide.md`、`LS-DYNA_Implicit_Analysis_Guide.md`；來源清冊記錄 Keyword and Theory Manuals 取得入口 | [LS-DYNA](../../agents/skills/structural-mechanics/ansys-lsdyna/SKILL.md)、[Shock workflow](../../agents/skills/structural-mechanics/shock-analysis-workflow/SKILL.md) | Keyword deck、Mechanical 整合與 PyDYNA 是不同介面；取得入口不等於完整手冊卷冊。 |
| P1 LS-PrePost | `Documentation_md/Ansys_LS-PrePost_Users_Guide.md` | [LS-PrePost](../../agents/skills/structural-mechanics/ansys-ls-prepost/SKILL.md) | Python/DataCenter、SCL 與 cfile 是不同介面；結果需標示 state、實體、座標系、欄位與單位。 |
| P1 Random Vibration | `Documentation_md/Ansys_Mechanical_Users_Guide.md`、`Ansys_Scripting_in_Mechanical_Guide.md` | [Random vibration](../../agents/skills/structural-mechanics/ansys-random-vibration/SKILL.md)、[Mechanical](../../agents/skills/structural-mechanics/ansys-mechanical/SKILL.md) | PSD、阻尼、模態充分性及 RMS 必須對應目標設定；文件範例不建立獨立 MCP connector。 |
| P2 Thermal／PCB | Mechanical User's Guide、Scripting Guide；repo 的 Mechanical API 快照 | [Thermal analysis](../../agents/skills/thermal-cooling/ansys-thermal-analysis/SKILL.md)、[PCB warpage](../../agents/skills/materials-reliability/pcb-warpage-analysis/SKILL.md) | 穩態／暫態熱、熱應力與耦合映射分開；估算結果需標記，不得當成 solver result。 |
| P2 optiSLang | repo 的 optiSLang API 快照與技能 references；執行 API 依安裝 SDK/release 確認 | [optiSLang](../../agents/skills/systems-coupling/ansys-optislang/SKILL.md) | DoE 樣本數、TSI、CoP、VIF 門檻依案例判定，不是通用硬門檻。失敗點不得填零參與最佳解排序。 |
| P2 Sherlock | 來源清冊記錄的 v261 Sherlock API reference；版本依來源 metadata 確認 | [Sherlock](../../agents/skills/materials-reliability/ansys-sherlock/SKILL.md) | 目前提供文件與 PCB 可靠度工作流知識；不宣稱 MCP Sherlock connector 或求解支援。 |
| P2 Icepak | `ANSYS_DOCS_ROOT` 下的 Icepak scripting guide 與 training/tutorial；文件版本待核 | [Icepak](../../agents/skills/thermal-cooling/ansys-icepak/SKILL.md)、[Thermal router](../../agents/skills/domains/ansys-thermal-cooling/SKILL.md) | driver 是能力骨架；產生腳本或 CSV 不等於溫度場或已求解結果。 |
| P1 MAPDL | `docs/knowledge_dictionary/mapdl.md`、`docs/api_inventory/curated/sdk/mapdl.md`；APIKB mapdl 快照 | [MAPDL](../../agents/skills/structural-mechanics/ansys-mapdl/SKILL.md) | 支援 launch_mapdl、APDL wrapper、gRPC 串流與 run_mapdl_input 工具。 |
| P1 Workbench | `docs/knowledge_dictionary/workbench.md`、`docs/api_inventory/curated/sdk/workbench.md` | [Workbench](../../agents/skills/systems-coupling/ansys-workbench/SKILL.md) | 支援 25+ Workbench MCP 工具、.wbjn 日誌執行與 DesignPoint 批次更新。 |
| P2 Chemkin | `docs/knowledge_dictionary/reaction_chemkin.md`、`docs/api_inventory/curated/sdk/reaction_chemkin.md` | [Chemkin](../../agents/skills/fluids-cfd/ansys-chemkin/SKILL.md) | 支援 0D/1D 反應器動力學、Arrhenius 速率計算與 MFL 燃料機制對齊。 |
| P2 Discovery | `docs/knowledge_dictionary/discovery.md`、`curated/protocols/discovery_protocol.md` | [Discovery](../../agents/skills/geometry-meshing/ansys-discovery/SKILL.md) | 支援 Discovery Document/Window gRPC 容器與 Live Physics 探索。 |
| P2 EnSight / ADR | `docs/knowledge_dictionary/ensight.md`、`docs/knowledge_dictionary/adr.md` | [EnSight ADR](../../agents/skills/documentation/ansys-ensight-adr/SKILL.md) | 支援 PyEnSight 3D 場後處理與 PyDynamicReporting 本地報告伺服器。 |
| P2 SimAI | `docs/knowledge_dictionary/simai.md` (12 主題)、`ansys-simai-core` 0.4.8 | [SimAI](../../agents/skills/optimization-surrogates/ansys-simai/SKILL.md) | 支援 GeomAI MER 品質檢查與非同步推論生命週期。 |
| P3 Speos／Illumination | `ANSYS_DOCS_ROOT` 下的 Speos 文件；client API 版本按文件 metadata 記錄 | [Speos](../../agents/skills/optical-engineering/ansys-speos/SKILL.md)、[Optical router](../../agents/skills/domains/ansys-optical-engineering/SKILL.md) | Speos client/RPC/NX API 依宿主與版本分流；目前沒有 MCP 產品 controller。 |
| P3 Zemax | `ANSYS_DOCS_ROOT` 下的 ZOS-API 文件；ZOSPy 是獨立套件／介面 | [Zemax](../../agents/skills/optical-engineering/ansys-zemax/SKILL.md)、[Optical router](../../agents/skills/domains/ansys-optical-engineering/SKILL.md) | 區分 OpticStudio 序列／非序列、ZOS-API 主控／附掛及 ZOSPy；不宣稱 MCP connector。 |
| P3 Lumerical | `ANSYS_DOCS_ROOT` 下的 lumapi 與 scripting language 文件；版本依文件 metadata 記錄 | [Lumerical](../../agents/skills/optical-engineering/ansys-lumerical/SKILL.md)、[Optical router](../../agents/skills/domains/ansys-optical-engineering/SKILL.md) | FDTD、MODE、INTERCONNECT 各自依 source、monitor、mesh 與結果型態分流；不宣稱 MCP connector。 |


## 版本與證據聲明

- 產品 release、SDK version、宿主（CPython、Mechanical ACT、SpaceClaim embedded script、Workbench journal、LS-PrePost 等）需分欄記錄。v251、v252、v261 不互相代替。
- 文件證據、靜態 API 對照、mock、宿主讀回、真實求解是不同驗證層級。技能文件只提供流程與來源，不代表真機已驗收。
- `LS-DYNA_Keyword_and_Theory_Manuals.md` 僅為取得手冊入口；不可引用為其列出的完整卷冊內容。
- 文件/目錄/二進位存在不能證明授權可用。未探測的 license 狀態應標為 unknown。

## 官方與第三方來源採用

官方 PyAnsys umbrella repository 僅作產品套件入口；具體介面應回到各產品官方文件、API reference 和固定版本 examples。第三方倉庫僅提供候選工作流/UX 設計，不直接採納工程門檻或 API：`femis-skill`、`FEP-Agent-Hub`、`fluent-cfd-skill`、`ai-zemax-optical-design`、`zemax-python-connect`、`doc-driven-engineering-software-skills`、`ansys-mcp-server`、`hfss-api-skill`、`ansys-sim-skill`。對未能直接讀取或 license/commit 尚未核對的倉庫，不移植程式或文字；應在來源紀錄中標示待查，而非推定不存在或可用。
