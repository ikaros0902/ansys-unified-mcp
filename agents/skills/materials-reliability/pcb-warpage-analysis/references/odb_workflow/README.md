# Track 2 ODB++ 熱翹曲快照環境說明

本目錄為 `pcb-warpage-analysis` 技能 **Track 2（有 ODB++ 路線）** 的工作流說明與檢查點文件。

## 目錄與路徑邊界

1. **`TOOL_DIR` 唯讀對應**：
   - 上游執行腳本與 `odbtool` 套件之唯讀快照位於 `agents/skills/materials-reliability/pcb-warpage-analysis/scripts/odb_workflow`。
   - 任何專案執行時均不得寫入或修改 `TOOL_DIR` 內之腳本、範本與文件；快照完整性由 `scripts/verify_upstream_snapshot.py` 與 `scripts/UPSTREAM_MANIFEST.json` 透過 SHA-256 驗證。
2. **`PROJECT_DIR` 外部隔離**：
   - `PROJECT_DIR`（含專案輸入檔、設定 JSON、`runs/` 與 `project_log.md`）**必須置於 `ANSYS-unified-MCP` 倉庫與 `TOOL_DIR` 之外**，嚴禁將專案實例資料寫入倉庫。
   - 同一 `PROJECT_DIR` 內須區隔兩軌輸出：`Track 1` 置於 `runs/track1_rom/`，`Track 2` 置於 `runs/track2_odb/`。
3. **專案 JSON `output.root` 設定**：
   - 建立 Track 2 專案設定 JSON 時，必須明確設定 `output.root = "runs/track2_odb"`。
   - 不得直接改動上游範本 `scripts/odb_workflow/4_config/project_config.template.json`。
4. **未隨快照提供之項目**：
   - 上游文件中提及的「上游範例目錄（未隨快照提供）」、內部簡報、現場照片與材料庫 XML（`PCB_Material_Library.xml`）均未納入本倉庫快照。
   - 執行 Track 2 時，材料庫 XML 路徑須由工程師於外部 `PROJECT_DIR` 專案 JSON 中自行指定。

## 執行環境與參考入口

- **純本機環境**：未連線 `ansys-unified-mcp` 時，可使用 `scripts/odb_workflow/setup_env.ps1` 建立之獨立虛擬環境（`%USERPROFILE%\.venvs\pcb_thermal_warpage`）執行完整流程。
- **核心參考文件**：
  - Track 2 九步操作主手冊：[`TRACK2_SKILL.md`](./TRACK2_SKILL.md)
  - GUI-to-MCP 交接與檢查點協議：[`mcp_hybrid_checkpoint.md`](./mcp_hybrid_checkpoint.md)
