# 檢查 ANSYS 與 MCP 狀態工作流程

此工作流程用於一鍵診斷當前 CAE 執行環境：
1. 調用 ansys-unified-mcp 的 `check_ansys_installation` 工具檢查版本與安裝路徑。
2. 調用 `check_workbench_connection` 檢查 Workbench 與 Mechanical Bridge 連線狀態。
3. 輸出簡明健康報告給使用者。
