# ANSYS Unified MCP 重構大計畫 (Master Plan v4.0 - 官方架構對齊版)

## [Goal Description]
本計畫深度對標 ANSYS 官方最新開源專案（`ansys-mechanical-mcp`、`ansys-mapdl-mcp` 與 `pyansys` 官方生態），徹底解決：
1. **多實例 (Multiple Instances) Port 衝突與辨識問題**：官方生態為何無法自動遞增 Port，以及我們如何透過動態埠管理與伺服器實例化解決。
2. **SpaceClaim vs Mechanical 連線複雜度差異與統一**：釐清底層協定本質差異，並在 MCP 門面層（Facade）與腳本執行層完成體驗統一。
3. **消除巨石反模式**：順應官方「獨立產品獨立 MCP」架構，完成工作區隔離與漸進式揭露。

---

## 官方架構深入調研總結 (Official PyAnsys Architecture Insights)

### 1. 為何開兩個 SpaceClaim 只能偵測到一個？Port 會自動遞增嗎？其他模組會這樣嗎？
*   **官方底層機制**：
    *   **SpaceClaim / PyAnsys Geometry**：底層依賴 `ANSRV_GEO_PORT` 環境變數，預設強制綁定 `50051`。手動點擊桌面開啟多個 SpaceClaim 時，Windows **不會自動遞增 Port**，第二個實例無法綁定同一個 Port，因此 PyAnsys 客戶端永遠只能連線到佔用 `50051` 的第一台。
    *   **Mechanical / PyMechanical**：預設強制綁定 `10000`。手動多開同樣會發生衝突。
    *   **MAPDL / PyMAPDL**：預設強制綁定 `50052`。
*   **官方的解法**：
    *   官方 `ansys-mechanical-mcp` 與 `ansys-mapdl-mcp` **並沒有在單一伺服器內搞全域自動遞增**，而是將 `--port` 與 `--ip` 作為啟動參數。若要控制多個實例，官方做法是**啟動多個 MCP Server 程序**（例如實例 A 對應 Server A (Port 10000)，實例 B 對應 Server B (Port 10001)）。

### 2. SpaceClaim 與 Mechanical 連線複雜度差異，能否統一？
*   **本質差異**：
    *   **Mechanical** 是「遠端腳本執行引擎」：直接投遞 ACT Python 字串給唯一的 `ExtAPI`，通訊鏈路極短。
    *   **SpaceClaim (PyAnsys Geometry)** 是「細粒度 gRPC 物件映射器」：強制 Windows 安全認證握手（`transport_mode`）、畫布焦點確認，且幾何特徵全走細微 RPC。
*   **統一方案**：
    *   **通訊協定無法統一**（C++/C# 內核差異不可逆）。
    *   **MCP 介面層全面統一**：
        1. 建立統一的 `SessionManager`（輸入 `product` 與 `port`，封裝所有握手細節）。
        2. 為 SpaceClaim 導入**「批次腳本執行模式」**（利用 SpaceClaim 內建 Scripting 直通 ExtAPI，規避微觀 RPC 網路延遲），使其速度追平 Mechanical。

---

## User Review Required
> [!IMPORTANT] 多開與連線架構抉擇
> 是否同意對標官方架構：放棄「單一伺服器監聽所有模組」的巨石設計，改為「模組化獨立啟動 + 動態 Port 參數配置」？

---

## Proposed Changes: 重構三階段 (Phases)

### Phase 1: 止血與代碼去重複 (Detox) —— 立即執行
*   **[DELETE]** `src/ansys_unified_mcp/products/mechanical.py`（清理雙胞胎代碼）。
*   **[MODIFY]** `src/ansys_unified_mcp/tools.py`，全數引用 `mechanical.facade`。
*   **[MODIFY]** `scripts/` 目錄，將測試腳本遷移至 `examples/`。
*   **[MODIFY]** `skills/` 目錄，統一 YAML 規範與漸進式揭露。
*   **分工**：由 `system_one_judge` 進行快速替換，`loop_reviewer` 審查代碼與測試覆蓋。

### Phase 2: 對標官方的模組化拆分與多開支援 (Modular MCP Servers)
*   **[NEW]** 參考 `ansys-mechanical-mcp`，拆分獨立產品入口：`servers/mechanical.py`、`servers/geometry.py`、`servers/mapdl.py`。
*   **[NEW]** 導入 `--port` 與 `--host` 參數支援，支援多實例指定與自動空閒 Port 偵測。
*   **[NEW]** **Port 可視化與日誌反饋機制**：當任意 SpaceClaim 或 Mechanical 實例啟動/連線時，底層與 MCP Tools 必須在日誌（Log）與回傳文字（Messages）中顯式提示通訊埠與處理序資訊（例如：`[ANSYS Connection] Successfully connected to SpaceClaim on Port: 50051 (PID: 14220)`），杜絕黑盒子。
*   **[NEW]** 建立 `.mcp-workspaces/` 隔離工作區，阻斷 Context 污染。
*   **分工**：`ansys_cae_specialist` 主導伺服器拆分、多開參數支援與 Port 日誌回顯。

### Phase 3: 連線門面統一與資源化 (Unified Facade & Resources)
*   **[NEW]** 統一連線門面 `AnsSessionManager`，提供一致的 `connect(product, port)` 與 `launch(product, port)`。
*   **[MODIFY]** SpaceClaim 連線優化：提供批次腳本通道，解決微觀 RPC 緩慢問題。
*   **[NEW]** 實作 MCP Resources（模型樹、材料庫端點）。
*   **分工**：`ansys_cae_specialist` 優化 SpaceClaim 腳本引擎，`loop_reviewer` 驗收 Resources 響應。

---

## Verification Plan
1. **單元測試**：全專案 `pytest` 通過。
2. **多開驗證**：啟動兩個 Mechanical (Port 10000 / 10001) 與兩個 SpaceClaim (Port 50051 / 50052)，分別藉由參數連線成功。
3. **連線速度基準**：SpaceClaim 批次腳本執行延遲降低 70% 以上。
