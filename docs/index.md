# ANSYS Unified MCP 文件索引

專案入口見 [README](../README.md)，安裝與連線步驟見 [部署手冊](deployment/DEPLOYMENT_SOP.md)。

## 架構與計畫

- [現況分層與程式慣例](architecture/ARCHITECTURE.md)
- [架構與規格評估白皮書](architecture/ANSYS_UNIFIED_MCP_ARCHITECTURE_AND_SPECIFICATION_REPORT.md)
- [技能知識匯入計畫](planning/skills_knowledge_ingestion_plan.md)：計畫不代表已實作。
- ANSYS API 字典、REA 組件證據及本機 RAG 資料目前保存在被 Git 忽略的 `docs/api_inventory/`；公開散布權尚未確認，因此本索引不連結這些本機檔案。

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
