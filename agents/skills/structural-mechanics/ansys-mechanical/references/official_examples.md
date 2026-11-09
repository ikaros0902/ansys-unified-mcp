# 官方 Mechanical 範例指南 (Official Verified Examples)

> [!NOTE]
> 本參考手冊彙整官方 PyAnsys 與 ANSYS 權威驗證範例。
> 提供標準化輸入檔案下載、核心腳本步驟、預期收斂驗收標準與版本資訊。

## 範例 1：Static structural analysis of bracket

- **官方文檔來源**：[Static structural analysis of bracket](https://examples.mechanical.docs.pyansys.com/examples/00_basic/example_01_simple_structural_solve.html)
- **開源倉庫與授權**：`https://github.com/ansys/pymechanical-examples`（授權：`MIT`）
- **幾何與輸入資源**：`example_01_geometry.agdb`
- **下載 API 呼叫**：`ansys.mechanical.core.examples.download_file('example_01_geometry.agdb', 'pymechanical', '00_basic')`

### 核心實施步驟

1. 啟動 Mechanical 服務並載入模型與幾何
2. 設定單位系統為 Standard MKS
3. 建立 Fixed Support 支承與 1000 N 載荷
4. 執行網格劃分並評估網格品質指標
5. 求解並擷取 Total/Directional Deformation 與 Equivalent Stress

### 客觀驗收條件 (Verification Condition)

- **收斂與指標驗證**：最大位移約 0.104 m，求解收斂狀態 Exit Code 0，無未拘束自由度警告。

## 範例 2：Modal analysis of turbine blade

- **官方文檔來源**：[Modal analysis of turbine blade](https://examples.mechanical.docs.pyansys.com/examples/01_advanced/example_02_modal_analysis.html)
- **開源倉庫與授權**：`https://github.com/ansys/pymechanical-examples`（授權：`MIT`）
- **幾何與輸入資源**：`blade.step`
- **下載 API 呼叫**：`ansys.mechanical.core.examples.download_file('blade.step', 'pymechanical', '01_advanced')`

### 核心實施步驟

1. 建立 Modal Analysis 系統並關聯幾何
2. 對根部面建立 Fixed Support 邊界條件
3. 提取前 6 階固有頻率與相對應振型

### 客觀驗收條件 (Verification Condition)

- **收斂與指標驗證**：第一階模態頻率收斂於基準值 +-2% 範圍內。

## 取得紀錄與版本控管說明

1. **官方下載原則**：輸入檔案一律優先透過官方 `download_file()` API 或快取取得，嚴禁將二進位二進制檔案硬編碼塞入技能庫。
2. **雜湊校驗**：下載之資源檔案必須以 `SHA-256` 進行完整性驗證。
3. **授權分離**：程式碼依 MIT / Apache-2.0 授權使用，ANSYS 求解器執行需遵循本機合法商業授權；無授權環境自動降級至雙軌數值/解析基準測試。
