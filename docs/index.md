# ANSYS Unified MCP 文件索引

專案入口見 [README](../README.md)，安裝與連線步驟見 [部署手冊](deployment/DEPLOYMENT_SOP.md)。

## 架構與計畫

- [現況分層與程式慣例](architecture/ARCHITECTURE.md)
- [架構與規格評估白皮書](architecture/ANSYS_UNIFIED_MCP_ARCHITECTURE_AND_SPECIFICATION_REPORT.md)
- [技能知識匯入計畫](planning/skills_knowledge_ingestion_plan.md)：計畫不代表已實作。
- [ANSYS API 快照目錄與範圍](api_inventory/API_CATALOG.md)：列出目前索引的產品、版本與工具。
- [gRPC/protobuf 協定字典](api_inventory/curated/protocols/index.md)：列出 11 份協定快照的人讀 RPC 與欄位字典。
- [全產品 API 來源與缺口索引](api_inventory/PRODUCT_API_MATRIX.md)：以人讀表格呈現直接快照、REA 組件證據與待補來源。
- [ANSYS API 產品覆蓋清冊](api_inventory/api_coverage.json)：分開列出直接 API 快照與本機文件語料版本／缺口，不表示 API 完整度。
- [ANSYS API 與文件檢索指南](api_inventory/API_RAG_GUIDE.md)：說明 APIKB、文件搜尋和來源證據的使用方式。
- [本機 Python SDK 安裝快照](api_inventory/sdk_environment.json)：記錄 repo `.venv` 對來源清冊 SDK 套件名稱的精確版本配對；缺少套件不代表產品沒有 SDK/API。
- [REA v251 組件證據](api_inventory/REA_EVIDENCE.md)：Mechanical、SpaceClaim 與 AnsysEM 本機 managed 組件的靜態 metadata 摘要；AnsysEM 尚未映射到特定產品。
- [REA managed snapshot 索引](api_inventory/curated/rea/index.md)：列出 42 份快照的來源鍵、組件身分與 metadata 計數。

## 部署與測試

- [部署標準作業](deployment/DEPLOYMENT_SOP.md)
- [MCP 工具範圍設定](deployment/MCP_TOOL_SCOPING_GUIDE.md)
- [測試基礎設施](testing/TEST_INFRA.md)
- [評測定義與執行器](../tests/evaluations/)
- [既有 Stage 5 報告](../tests/evaluations/reports/verification_report_stage5.json)：包含本地數值引擎結果，不能當成真實 ANSYS 求解驗收。

## 工程實例與操作筆記

- [衝擊分析管線](examples/shock_analysis/README.md)
- [幾何清理](examples/geometry_cleanup/README.md)
- [網格排障](examples/mesh_debug/README.md)
- [網格分類候選規則](examples/mesh_debug/mesh_classification_heuristics.md)：保留 Shadow Mode 狀態。
- [PCB 熱翹曲工作流](examples/pcb_warpage/README.md)
- [PCB 熱翹曲自動化紀錄](examples/pcb_warpage/AUTOMATION_LOG.md)

## 維護與來源

- [目錄分工與回復方式](maintenance/FOLDER_STRUCTURE.md)
- [根目錄檔案搬移清單（來源雜湊與目的路徑）](maintenance/ROOT_REORGANIZATION_MAP.json)
- [技能目錄搬移清單（路徑、搬移前 SHA-256、位元組數）](maintenance/SKILL_MIGRATION_MAP.json)
- [工作區與 ANSYS 文件庫整理結果](maintenance/FOLDER_CLEANUP_REPORT.md)
- [官方文件維護命令](maintenance/ANSYS_DOCUMENT_MAINTENANCE.md)
- [Session 經驗與排障](maintenance/session_learnings_and_troubleshooting.md)
- [ANSYS 來源盤點](maintenance/ANSYS_SOURCE_INVENTORY.md)
- [外部來源採用記錄](maintenance/EXTERNAL_SOURCE_ADOPTION.md)
- [領域來源與能力邊界](skills/DOMAIN_SOURCE_AND_SUPPORT.md)
- 本機 ANSYS 官方文件庫位於 `ANSYS_Document/INDEX.md`；文件原件不納入版本庫。
- [模組技能庫](../agents/skills/README.md)：技能依 ANSYS 模組分類，並以 `SKILL.md` 作為入口。

## 歷史資料

- [審查記錄](reviews/)：保留當時原文，現況請使用本索引。
- [歷史快照](archive/README.md)：不可作為現況或驗收結果。
