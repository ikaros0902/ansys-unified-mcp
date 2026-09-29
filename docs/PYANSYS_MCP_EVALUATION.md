# 官方 PyAnsys MCP 評估報告 (PyAnsys MCP Evaluation)

> **評估目標**：針對 ANSYS 官方釋出的 PyAnsys MCP Server 系列（如 `pyansys-common-mcp`、`pyaedt-mcp` 等），評估其功能定位以及與本專案 (`ANSYS-unified-MCP`) 未來整合或取用的可能性。

---

## 1. 官方 PyAnsys MCP 生態概況

根據針對 `Cai-aa/CAE-Agent-Hub` 內嵌的 PyAnsys 目錄（源自官方上游 2026-09 快照）分析，ANSYS 官方的 MCP 架構呈現以下特徵：

1. **Micro-Server 拓撲**：官方採取「一個產品一個 MCP Server」的策略（如 pyaedt-mcp, pydpf-mcp）。
2. **依賴基礎共用模組**：建立了一個 `pyansys-common-mcp`，負責處理共用的連線設定、日誌與基礎資料模型。
3. **原生 gRPC 優先**：底層高度依賴 PyAnsys 系列函式庫（PyMechanical、PyFluent），預設以 gRPC 進行全雙工通訊。

## 2. 與 ANSYS-unified-MCP 的架構對比

| 面向 | 官方 PyAnsys MCP | 我們的 ANSYS-unified-MCP |
|------|-----------------|------------------------|
| **部署模式** | 每個產品獨立啟動不同的 Server | 單一統一入口 (`FastMCP("ansys-unified-mcp")`)，以 `ANSYS_MCP_PROFILE` 動態載入 |
| **通訊容錯 (Transport)** | 強依賴 gRPC / 本機連線 | **Dual Transport**：支援 Socket 即時通訊與 File-IPC (Queue) 批次降級，適應授權卡死或遠端無頭環境 |
| **安全與驗證 (Gatekeeper)**| 僅具備基本的 Python Exception 處理 | 具備 **9 大前檢物理閘門** (如落摔速度、模態質量、Evidence Hash 等)，阻斷無效求解 |
| **非同步佇列管理** | 無 | 具備 `SentinelQueue`、`Watchdog`、`CircuitBreaker` |

## 3. 評估結論與後續建議

### 結論：不建議全盤替換，但可考慮依賴引入
我們的 `ANSYS-unified-MCP` 在 **「AI Agent 自動化流程的安全護欄（Gatekeeper）」** 以及 **「多重通訊降級模式（Dual Transport）」** 上，遠比目前官方初期的 MCP 實作來得強大且適合長篇幅的 LLM 規劃。

然而，官方 MCP 對於特定軟體（例如 AEDT, DPF）的 API 封裝可能更具權威性與版本相容性。

### Phase 5 (未來展望) 建議行動：
1. **保留主控權**：繼續維持 `ANSYS-unified-MCP` 作為主 Router 與安全閘門的角色。
2. **引入 `pyansys-common-mcp` 作為底層庫**：未來可以將官方的 `pyansys-common-mcp` 作為 pip 依賴引入，替代掉我們內部自行維護的部分資料傳輸 DTO 與日誌抽象。
3. **工具代理 (Tool Proxying)**：對於我們尚未深度實作的產品（如 AEDT、Motor-CAD），可以直接在我們的 `tools/*_tools.py` 中將請求透明轉發 (Proxy) 給官方對應的 MCP Server，達成優勢互補。
