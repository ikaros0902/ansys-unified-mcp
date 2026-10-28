# PCB 熱翹曲範例

此目錄保留 PCB 熱翹曲工作流的自動化紀錄與相容啟動入口。腳本實作集中在 [pcb-warpage-analysis 技能](../../../agents/skills/materials-reliability/pcb-warpage-analysis/SKILL.md) 的 `scripts/`；本目錄的同名 `.py` 檔只轉交命令列參數，不另存一份實作。

執行前，請設定 `PCB_STACKUP_DIR` 指向包含 `MCP_Test.xlsx` 的疊構資料目錄，再執行 `run_full_warpage_workflow.py`。也可直接傳入資料目錄作為第一個參數。單獨使用建模或材料腳本時，請沿用技能文件列出的參數與 ANSYS 環境需求。

本範例不會自動求解；Mechanical 設定腳本的執行與實際求解仍依技能文件的安全及驗收要求進行。
