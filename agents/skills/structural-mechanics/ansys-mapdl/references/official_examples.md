# 官方 Mapdl 範例指南 (Official Verified Examples)

> [!NOTE]
> 本參考手冊彙整官方 PyAnsys 與 ANSYS 權威驗證範例。
> 提供標準化輸入檔案下載、核心腳本步驟、預期收斂驗收標準與版本資訊。

## 範例 1：Cantilever beam with end load

- **官方文檔來源**：[Cantilever beam with end load](https://mapdl.docs.pyansys.com/version/stable/examples/technology_showcase/example_01_cantilever.html)
- **開源倉庫與授權**：`https://github.com/ansys/pymapdl`（授權：`MIT`）
- **幾何與輸入資源**：`None (Parametric APDL)`

### 核心實施步驟

1. 使用 launch_mapdl() 初始化 MAPDL gRPC 連線
2. 使用 /PREP7 定義 BEAM188 元素與斷面特性
3. 施加根部全拘束 D, 1, ALL 與自由端集中力 F, 2, FY, -1000
4. 呼叫 /SOLU 與 SOLVE 求解
5. 透過 /POST1 與 mapdl.post_processing 提取樑端撓度

### 客觀驗收條件 (Verification Condition)

- **收斂與指標驗證**：樑端撓度與材料力學解析解 PL^3/(3EI) 相符（相對誤差 < 0.5%）。

## 範例 2：Shaft vibration modal extraction

- **官方文檔來源**：[Shaft vibration modal extraction](https://mapdl.docs.pyansys.com/version/stable/examples/modal_analysis.html)
- **開源倉庫與授權**：`https://github.com/ansys/pymapdl`（授權：`MIT`）
- **幾何與輸入資源**：`None`

### 核心實施步驟

1. 設定 MODOPT, LANB, 10 進行 Block Lanczos 特徵值求解
2. 定義兩端簡支拘束並執行求解
3. 透過 mapdl.modal_analysis 讀取固有頻率列表

### 客觀驗收條件 (Verification Condition)

- **收斂與指標驗證**：前三階固有頻率與理論解析解吻合。

## 取得紀錄與版本控管說明

1. **官方下載原則**：輸入檔案一律優先透過官方 `download_file()` API 或快取取得，嚴禁將二進位二進制檔案硬編碼塞入技能庫。
2. **雜湊校驗**：下載之資源檔案必須以 `SHA-256` 進行完整性驗證。
3. **授權分離**：程式碼依 MIT / Apache-2.0 授權使用，ANSYS 求解器執行需遵循本機合法商業授權；無授權環境自動降級至雙軌數值/解析基準測試。
