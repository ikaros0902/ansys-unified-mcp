# 官方 Discovery 範例指南 (Official Verified Examples)

> [!NOTE]
> 本參考手冊彙整官方 PyAnsys 與 ANSYS 權威驗證範例。
> 提供標準化輸入檔案下載、核心腳本步驟、預期收斂驗收標準與版本資訊。

## 範例 1：Interactive generative design and live flow exploration

- **官方文檔來源**：[Interactive generative design and live flow exploration](https://discovery.docs.pyansys.com/version/stable/examples/interactive_flow.html)
- **開源倉庫與授權**：`https://github.com/ansys/discovery-examples`（授權：`MIT`）
- **幾何與輸入資源**：`manifold.dsco`

### 核心實施步驟

1. 透過 Discovery gRPC protocol 初始化 Document 容器與 Window 載入
2. 建立幾何幾何拓撲並指定入口流速
3. 啟動 GPU Live Physics 即時求解並監測壓力流場分佈

### 客觀驗收條件 (Verification Condition)

- **收斂與指標驗證**：即時物理場收斂並回傳即時速度向量流線。

## 取得紀錄與版本控管說明

1. **官方下載原則**：輸入檔案一律優先透過官方 `download_file()` API 或快取取得，嚴禁將二進位二進制檔案硬編碼塞入技能庫。
2. **雜湊校驗**：下載之資源檔案必須以 `SHA-256` 進行完整性驗證。
3. **授權分離**：程式碼依 MIT / Apache-2.0 授權使用，ANSYS 求解器執行需遵循本機合法商業授權；無授權環境自動降級至雙軌數值/解析基準測試。
