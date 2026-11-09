# 官方 Spaceclaim 範例指南 (Official Verified Examples)

> [!NOTE]
> 本參考手冊彙整官方 PyAnsys 與 ANSYS 權威驗證範例。
> 提供標準化輸入檔案下載、核心腳本步驟、預期收斂驗收標準與版本資訊。

## 範例 1：CAD defeaturing and mid-surface extraction

- **官方文檔來源**：[CAD defeaturing and mid-surface extraction](https://geometry.docs.pyansys.com/version/stable/examples/01_cad_defeaturing.html)
- **開源倉庫與授權**：`https://github.com/ansys/pyansys-geometry`（授權：`MIT`）
- **幾何與輸入資源**：`bracket_with_holes.scdoc`
- **下載 API 呼叫**：`ansys.geometry.core.examples.download_file('bracket_with_holes.scdoc')`

### 核心實施步驟

1. 使用 Modeler 連線 SpaceClaim / Geometry 引擎
2. 搜尋模型中小於指定半徑之圓角 (Round) 與細小通孔
3. 呼叫 Defeature 與 Midsurface 工具將薄壁實體抽取為中面
4. 輸出清潔幾何供網格生成

### 客觀驗收條件 (Verification Condition)

- **收斂與指標驗證**：特徵簡化後幾何拓撲無重疊面或未結合邊界 (Watertight)。

## 取得紀錄與版本控管說明

1. **官方下載原則**：輸入檔案一律優先透過官方 `download_file()` API 或快取取得，嚴禁將二進位二進制檔案硬編碼塞入技能庫。
2. **雜湊校驗**：下載之資源檔案必須以 `SHA-256` 進行完整性驗證。
3. **授權分離**：程式碼依 MIT / Apache-2.0 授權使用，ANSYS 求解器執行需遵循本機合法商業授權；無授權環境自動降級至雙軌數值/解析基準測試。
