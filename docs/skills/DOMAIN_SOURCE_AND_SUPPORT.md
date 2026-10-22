# ANSYS domain skills：來源與能力對照

此文件記錄 skills 可依據的本機文件、版本標記與 MCP 支援邊界。文件檔名或安裝目錄不等於產品已安裝、授權可用或真機驗收通過。版本欄中的 2026 R1 對應 v261；v251/v252/v261 應各自查證，不以其中一版推定其他版本。

## 判斷規則分級

- **必要條件**：缺少即無法依目標物理問題建立可解模型，例如必要材料參數、載荷單位、有效 scoping、有效結果檔；錯誤須阻止或分類為不可驗證。
- **官方建議**：只在對應產品版本、分析類型、單元、材料和適用條件下採用，記錄手冊章節；不可擴大成跨分析硬門檻。
- **專案經驗值**：標為 heuristic，說明其適用模型、關注量、調整紀錄；不得偽裝成官方規範。

## 領域來源與能力矩陣

| 優先級／領域 | 本機來源（實際核對路徑／版本） | skill 路由 | MCP 支援邊界／證據狀態 |
|---|---|---|---|
| P1 Mechanical | `D:\ansys-docs-local\Documentation_md\Ansys_Mechanical_Users_Guide.md`（2026 R1）；`Ansys_Scripting_in_Mechanical_Guide.md`（2026 R1）；專案 `docs/api_inventory/`（主要為 v251 快照） | `ansys-mechanical`、`ansys-mechanical-connections`、`ansys-material-assignment` | 依現有 controller/session 能力判定；API 名稱存在不代表參數簽名或真機行為已驗證。跨版結果須各自記錄。 |
| P1 Mesh | Mechanical User's Guide、Mechanical Scripting Guide（2026 R1）；專案 `agents/skills/ansys-mesh/references/` | `ansys-mesh` | 指標須記錄定義、單元/分析和求解器適用性；品質指標不可無條件作通用阻斷門檻。 |
| P1 SpaceClaim | `D:\ansys-docs-local\Documentation_md\SpaceClaim_Documentation.md`（2026 R1，API 章）；`D:\Ikaros\ACT_Test\3.documents\SpaceClaim\`（v251/v252/v261 名稱副本） | `ansys-spaceclaim` 及 defeature/modeling/interface-check | 三版同名指南曾核對到相同內容 hash，不能視為三版獨立驗證。匯出需重開實際交換檔並檢查功能面、孔、局部邊界、單位。 |
| P1 LS-DYNA | `D:\ansys-docs-local\Documentation_md\LS-DYNA_Users_Guide.md`（2026 R1）；`LS-DYNA_Implicit_Analysis_Guide.md`（2026 R1，§12.1）；`D:\Ikaros\ACT_Test\3.documents\LS-DYNA_Keyword_and_Theory_Manuals.md`（索引/下載入口，非完整 keyword volumes） | `ansys-lsdyna` | Mechanical 整合、PyDYNA/keyword deck 與 solver 版本須分開；按指定案例讀回輸入、終止狀態、能量與結果。DT2MS 語義按版本手冊核實。 |
| P1 LS-PrePost | `D:\ansys-docs-local\Documentation_md\Ansys_LS-PrePost_Users_Guide.md`（2026 R1，§8.5.4 Random Vibration） | `ansys-ls-prepost` | Python/DataCenter、SCL、cfile 是不同宿主/介面；確認結果 state、part/node/element、座標系、欄位與單位。 |
| P1 Random Vibration | Mechanical User's Guide（2026 R1，Random Vibration §5.6.6，印刷頁約 556）；Mechanical Scripting Guide（2026 R1，範例印刷頁約 402） | `ansys-random-vibration` → Mechanical + DPF | 文件示例以 Workbench 建立 Modal/Random Vibration 系統後操作；MCP 未因此取得獨立 connector。PSD、阻尼、模態充分性及 RMS 必須對應目標設定。 |
| P2 Thermal | Mechanical User's Guide、Scripting Guide（2026 R1）；專案 `docs/api_inventory/`（v251 為主） | `ansys-thermal-analysis`、`pcb-warpage-analysis` | 穩態/暫態熱、熱應力與耦合映射分開。公式估值標 `estimated`；只有 solver 狀態、日誌與輸出相符才標 `solver_result`。 |
| P2 optiSLang | 專案既有 `agents/skills/ansys-optislang/references/official_examples.md`、`docs/api_inventory/`；執行時 API 需按安裝 SDK/release 核對 | `ansys-optislang`、`ansys-parametric-study` | DoE 樣本數、TSI、CoP、VIF 門檻屬案例/模型選擇依據，不是通用硬門檻。失敗點不得填零參與最佳解排序。 |
| P2 Sherlock | `D:\Ikaros\ACT_Test\3.documents\Sherlock\api_reference\sherlock-apis-2026-r1`（2026 R1） | `ansys-sherlock` | 文件/API 路由與 PCB 可靠度模型知識；目前沒有宣稱 MCP Sherlock connector 或真機求解支援。 |
| P2 Icepak | `D:\Ikaros\ACT_Test\3.documents\AnsysEM\manuals_and_training\IcepakScriptingGuide.pdf`（手冊版本需由 PDF 內文/封面再確認）；同目錄 Icepak training/tutorial | `ansys-icepak` | 目前 driver 為能力骨架，不得將產生腳本/CSV 宣稱為溫度場或已求解結果；新 connector 待後續工作。 |
| P3 Speos / Illumination | `D:\Ikaros\ACT_Test\3.documents\AnsysEM\` 中 Speos 文件；已核對的 client API 標記 2026 R1 SP03 | `ansys-speos`、`ansys-optical-engineering` | Speos client/RPC/NX API 路徑需按目標宿主與版本分流；沒有本 MCP 產品 controller。 |
| P3 Zemax | `D:\Ikaros\ACT_Test\3.documents\Zemax\` ZOS-API 文件（2026 R1）；ZOSPy 為獨立包/介面 | `ansys-zemax`、`ansys-optical-engineering` | 區分 OpticStudio 序列/非序列、ZOS-API 主控/附掛、原生介面/ZOSPy；沒有 MCP connector。 |
| P3 Lumerical | `D:\Ikaros\ACT_Test\3.documents\Lumerical\` lumapi 與 scripting language 文件（版本依文件 metadata） | `ansys-lumerical`、`ansys-optical-engineering` | FDTD/MODE/INTERCONNECT solver 與 source/monitor/mesh 結果分流；沒有 MCP connector。 |

## 版本與證據聲明

- 產品 release、SDK version、宿主（CPython、Mechanical ACT、SpaceClaim embedded script、Workbench journal、LS-PrePost 等）需分欄記錄。v251、v252、v261 不互相代替。
- 文件證據、靜態 API 對照、mock、宿主讀回、真實求解是不同驗證層級。技能文件只提供流程與來源，不代表真機已驗收。
- `LS-DYNA_Keyword_and_Theory_Manuals.md` 僅為取得手冊入口；不可引用為其列出的完整卷冊內容。
- 文件/目錄/二進位存在不能證明授權可用。未探測的 license 狀態應標為 unknown。

## 官方與第三方來源採用

官方 PyAnsys umbrella repository 僅作產品套件入口；具體介面應回到各產品官方文件、API reference 和固定版本 examples。第三方倉庫僅提供候選工作流/UX 設計，不直接採納工程門檻或 API：`femis-skill`、`FEP-Agent-Hub`、`fluent-cfd-skill`、`ai-zemax-optical-design`、`zemax-python-connect`、`doc-driven-engineering-software-skills`、`ansys-mcp-server`、`hfss-api-skill`、`ansys-sim-skill`。對未能直接讀取或 license/commit 尚未核對的倉庫，不移植程式或文字；應在來源紀錄中標示待查，而非推定不存在或可用。
