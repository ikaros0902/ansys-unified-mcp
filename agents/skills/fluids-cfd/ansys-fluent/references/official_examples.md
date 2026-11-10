# 官方 Fluent 範例指南 (Official Verified Examples)

> [!NOTE]
> 本參考手冊彙整官方 PyAnsys 與 ANSYS 權威驗證範例。
> 提供標準化輸入檔案下載、核心腳本步驟、預期收斂驗收標準與版本資訊。

## 範例 1：Mixing elbow turbulent flow and temperature mixing

- **官方文檔來源**：[Mixing elbow turbulent flow and temperature mixing](https://fluent.docs.pyansys.com/version/stable/examples/00_fluent/mixing_elbow.html)
- **開源倉庫與授權**：`https://github.com/ansys/pyfluent`（授權：`MIT`）
- **幾何與輸入資源**：`mixing_elbow.cas.h5`
- **下載 API 呼叫**：`ansys.fluent.core.examples.download_file('mixing_elbow.cas.h5', 'pyfluent/mixing_elbow')`

### 核心實施步驟

1. 啟動 Fluent Solver session: launch_fluent(precision='double', processor_count=4)
2. 讀取 Case 檔案: solver.file.read_case(file_name=cas_path)
3. 啟用 Realizable k-epsilon 紊流模型與能量方程式
4. 設定主入口冷水流速 0.4 m/s (293 K) 與支管熱水流速 1.2 m/s (313 K)
5. 初始化 (Standard / Hybrid) 並迭代求解 150 步
6. 提取出口混合溫度與壓力降監視器

### 客觀驗收條件 (Verification Condition)

- **收斂與指標驗證**：連續方程式與能量方程式殘差均下降至 1e-4 以下，出口均勻溫度吻合質量加權平均守恆。

## 取得紀錄與版本控管說明

1. **官方下載原則**：輸入檔案一律優先透過官方 `download_file()` API 或快取取得，嚴禁將二進位二進制檔案硬編碼塞入技能庫。
2. **雜湊校驗**：下載之資源檔案必須以 `SHA-256` 進行完整性驗證。
3. **授權分離**：程式碼依 MIT / Apache-2.0 授權使用，ANSYS 求解器執行需遵循本機合法商業授權；無授權環境自動降級至雙軌數值/解析基準測試。
