# 官方 System Coupling 範例指南 (Official Verified Examples)

> [!NOTE]
> 本參考手冊彙整官方 PyAnsys 與 ANSYS 權威驗證範例。
> 提供標準化輸入檔案下載、核心腳本步驟、預期收斂驗收標準與版本資訊。

## 範例 1：Fluid-Structure Interaction (FSI) with Fluent and Mechanical

- **官方文檔來源**：[Fluid-Structure Interaction (FSI) with Fluent and Mechanical](https://systemcoupling.docs.pyansys.com/version/stable/examples/oscillating_plate.html)
- **開源倉庫與授權**：`https://github.com/ansys/pysystem-coupling`（授權：`MIT`）
- **幾何與輸入資源**：`fsi_plate.scp`
- **下載 API 呼叫**：`pysystemcoupling.examples.download_file('fsi_plate.scp')`

### 核心實施步驟

1. 啟動 System Coupling 伺服器並加入 Fluent 與 Mechanical participants
2. 建立流固耦合介面 (Fluid-Solid Interface) 變數映射 (Force & Displacement)
3. 設定雙向交替耦合時間步長 (Two-way implicit coupling)
4. 求解並監控平板頂端位移震盪阻尼衰減歷程

### 客觀驗收條件 (Verification Condition)

- **收斂與指標驗證**：流體力與固體位移在每個時間步內達到雙向收斂，位移週期與文獻相符。

## 取得紀錄與版本控管說明

1. **官方下載原則**：輸入檔案一律優先透過官方 `download_file()` API 或快取取得，嚴禁將二進位二進制檔案硬編碼塞入技能庫。
2. **雜湊校驗**：下載之資源檔案必須以 `SHA-256` 進行完整性驗證。
3. **授權分離**：程式碼依 MIT / Apache-2.0 授權使用，ANSYS 求解器執行需遵循本機合法商業授權；無授權環境自動降級至雙軌數值/解析基準測試。
