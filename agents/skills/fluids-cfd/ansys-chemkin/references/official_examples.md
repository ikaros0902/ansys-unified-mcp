# 官方 Chemkin 範例指南 (Official Verified Examples)

> [!NOTE]
> 本參考手冊彙整官方 PyAnsys 與 ANSYS 權威驗證範例。
> 提供標準化輸入檔案下載、核心腳本步驟、預期收斂驗收標準與版本資訊。

## 範例 1：Constant volume 0D reactor autoignition delay calculation

- **官方文檔來源**：[Constant volume 0D reactor autoignition delay calculation](https://chemkin.docs.pyansys.com/version/stable/examples/0d_reactor_ignition.html)
- **開源倉庫與授權**：`https://github.com/ansys/ansys-chemkin-core`（授權：`MIT`）
- **幾何與輸入資源**：`gri30.chem.inp, gri30.therm.dat`
- **下載 API 呼叫**：`ansys.chemkin.core.examples.download_file('gri30.chem.inp')`

### 核心實施步驟

1. 載入 Arrhenius 機制文件與熱力學參數表
2. 建立封閉定容絕熱反應器 (Closed 0D Homogeneous Batch Reactor)
3. 給定初溫 T0 = 1200 K, P0 = 1 atm, 當量比 phi = 1.0 (CH4/Air)
4. 積分時間歷程直到溫度陡升點 (dT/dt 最大值)

### 客觀驗收條件 (Verification Condition)

- **收斂與指標驗證**：點火延遲時間 (Ignition Delay) 與 GRI-Mech 3.0 標準基準解偏差 < 1.0%。

## 取得紀錄與版本控管說明

1. **官方下載原則**：輸入檔案一律優先透過官方 `download_file()` API 或快取取得，嚴禁將二進位二進制檔案硬編碼塞入技能庫。
2. **雜湊校驗**：下載之資源檔案必須以 `SHA-256` 進行完整性驗證。
3. **授權分離**：程式碼依 MIT / Apache-2.0 授權使用，ANSYS 求解器執行需遵循本機合法商業授權；無授權環境自動降級至雙軌數值/解析基準測試。
