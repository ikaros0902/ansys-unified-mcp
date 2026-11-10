# 官方 Workbench 範例指南 (Official Verified Examples)

> [!NOTE]
> 本參考手冊彙整官方 PyAnsys 與 ANSYS 權威驗證範例。
> 提供標準化輸入檔案下載、核心腳本步驟、預期收斂驗收標準與版本資訊。

## 範例 1：Automated design point update and multi-system coupling journal

- **官方文檔來源**：[Automated design point update and multi-system coupling journal](https://workbench.docs.pyansys.com/version/stable/examples/parametric_journal.html)
- **開源倉庫與授權**：`https://github.com/ansys/ansys-workbench-core`（授權：`MIT`）
- **幾何與輸入資源**：`demo_project.wbpz`

### 核心實施步驟

1. 啟動 Workbench headless journal: RunScript(script_file)
2. 連線 Analysis System (Thermal + Static Structural)
3. 批次更新 5 個 Design Points (幾何長度與載荷大小)
4. 匯出 DesignPoint status 與輸出參數 CSV 報告

### 客觀驗收條件 (Verification Condition)

- **收斂與指標驗證**：所有 Design Points 求解狀態標記為 UpToDate，CSV 數值導出完整。

## 取得紀錄與版本控管說明

1. **官方下載原則**：輸入檔案一律優先透過官方 `download_file()` API 或快取取得，嚴禁將二進位二進制檔案硬編碼塞入技能庫。
2. **雜湊校驗**：下載之資源檔案必須以 `SHA-256` 進行完整性驗證。
3. **授權分離**：程式碼依 MIT / Apache-2.0 授權使用，ANSYS 求解器執行需遵循本機合法商業授權；無授權環境自動降級至雙軌數值/解析基準測試。
