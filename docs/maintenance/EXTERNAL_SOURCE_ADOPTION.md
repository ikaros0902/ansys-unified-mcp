# 外部來源採用紀錄

外部專案只作設計參考；本輪沒有直接複製第三方程式或工程門檻。正式移植前須記錄固定 commit/tag、license 與實際讀取檔案，並回查官方文件。查閱日期以本次計畫調查為準；未能取得者明確留待核查。

| 來源 | URL | 查閱範圍／狀態 | 本輪用途與採用決定 | Commit／license |
|---|---|---|---|---|
| PyAnsys | https://github.com/ansys/pyansys | 官方 umbrella；依產品文件與範例回查 | 僅作官方套件路由入口；不從 umbrella 推演產品 API | 產品版本依官方文件；umbrella snapshot 未固定 |
| femis-skill | https://github.com/test1card/femis-skill | README、SKILL 與案例摘要可讀 | 借鑑關注量與證據鏈的組織方式；工程門檻不照搬 | commit/license 待補；無程式移植 |
| FEP-Agent-Hub | https://github.com/S2mon123/FEP-Agent-Hub | README 可讀 | 參考工作區與作業狀態/證據紀錄概念 | commit/license 待補；產品 API 不採用 |
| skill-freecad-engineering | https://github.com/AsterrZep/skill-freecad-engineering | 指定內容未成功直接核實 | 排除本輪依據，保留待查 | 未核實 |
| fluent-cfd-skill | https://github.com/cavoiie/fluent-cfd-skill | README 與部分 reference 可讀 | 參考漸進揭露與守恆監測量驗證；僅作 CFD 設計參考 | commit/license 待補；無程式移植 |
| ai-zemax-optical-design | https://github.com/Jerry-del975/ai-zemax-optical-design | README 可讀 | 參考分階段光學流程；API 需以 ZOS-API 官方文件核實 | commit/license 待補；無程式移植 |
| zemax-python-connect | https://github.com/Hao-xl/zemax-python-connect | README 可讀 | 參考附掛/啟動診斷分流；不代表本 MCP 有 Zemax connector | commit/license 待補；無程式移植 |
| doc-driven-engineering-software-skills | https://github.com/walterkken/doc-driven-engineering-software-skills | README 可讀 | 參考文件、介面與執行證據的鏈結方式 | commit/license 待補；無程式移植 |
| ansys-mcp-server | https://github.com/Bettertoo2/ansys-mcp-server | README 可讀 | 參考 session 就緒分層、錯誤分類與生命週期；自行核實本專案 API | commit/license 待補；無程式移植 |
| ANSYS_skill | https://github.com/12sqawdwq/ANSYS_skill | 僅間接 metadata，正文未直接確認 | 不採用內容 | 待直接讀取並查 license |
| hfss-api-skill | https://github.com/LZT001107/hfss-api-skill | README 可讀 | P4 能力路由對照，不宣稱本 MCP 有 HFSS connector | commit/license 待補；無程式移植 |
| ansys-local-workflows-skill | https://github.com/WILL12345tt/ansys-local-workflows-skill | ZIP 可見，內文與 license 未確認 | 不移植；保留待查 | 未核實 |
| FDTD-SiP-skill | https://github.com/Jerry-del975/FDTD-SiP-skill | 指定倉庫內容未確認 | 不採用，非倉庫不存在的判斷 | 未核實 |
| Fusion360-ANSYS-Designs | https://github.com/theakash07/Fusion360-ANSYS-Designs | 指定倉庫內容未確認 | 不採用，非倉庫不存在的判斷 | 未核實 |
| ansys-sim-skill | https://github.com/QiYa-whimsy/ansys-sim-skill | README 可讀 | 只作功能覆蓋對照；工程/API 規則逐項回查 | commit/license 待補；無程式移植 |

## 採用原則

- 官方 API 文件確認介面與版本；官方 example 提供可重現流程；第三方專案只提出候選設計。
- 本輪採用的是「證據分級、漸進揭露、連線診斷分層」等抽象設計概念，不含第三方原文或程式碼移植。
- License/commit 尚未核實的來源不作為可再散布程式碼的來源。未讀到的內容只標為待查，不推論其不存在。
