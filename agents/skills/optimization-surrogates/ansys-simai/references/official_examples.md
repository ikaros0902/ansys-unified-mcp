# 官方 Simai 範例指南 (Official Verified Examples)

> [!NOTE]
> 本參考手冊彙整官方 PyAnsys 與 ANSYS 權威驗證範例。
> 提供標準化輸入檔案下載、核心腳本步驟、預期收斂驗收標準與版本資訊。

## 範例 1：Vehicle aerodynamic drag surrogate evaluation via PySimAI

- **官方文檔來源**：[Vehicle aerodynamic drag surrogate evaluation via PySimAI](https://simai.docs.pyansys.com/version/stable/examples/aerodynamics.html)
- **開源倉庫與授權**：`https://github.com/ansys/pysimai`（授權：`MIT`）
- **幾何與輸入資源**：`car_surface.stl`

### 核心實施步驟

1. 初始化 PySimAI Client 並認證 API 金鑰
2. 上傳 STL 表面幾何並進行 GeomAI MER 品質檢查
3. 呼叫訓練完畢之空氣動力學預測模型
4. 非同步等待預測完成並下載表面壓力與阻力係數 Cd

### 客觀驗收條件 (Verification Condition)

- **收斂與指標驗證**：推論耗時 < 1 秒，阻力係數與 3D 完整 CFD 誤差在工程容許範圍內。

## 取得紀錄與版本控管說明

1. **官方下載原則**：輸入檔案一律優先透過官方 `download_file()` API 或快取取得，嚴禁將二進位二進制檔案硬編碼塞入技能庫。
2. **雜湊校驗**：下載之資源檔案必須以 `SHA-256` 進行完整性驗證。
3. **授權分離**：程式碼依 MIT / Apache-2.0 授權使用，ANSYS 求解器執行需遵循本機合法商業授權；無授權環境自動降級至雙軌數值/解析基準測試。
