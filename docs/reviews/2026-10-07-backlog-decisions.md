# 2026-10-07 Backlog 技術決策記錄

本檔固化兩項「有意識暫緩」的技術決策，附實際引用鏈與觸發條件，供日後接手免重新盤查。兩項皆非遺漏，系統功能正常、全量 pytest 全綠。

對應使用者決策：**1=a（暫不移除 fallback bridge）**、**2=a（任務 7 以 D+A 結案，方案 C 列 backlog）**。

---

## Backlog 1：移除舊 Workbench fallback bridge

**狀態**：暫緩（2026-10-07）。
**暫緩理由**：PyWorkbench（gRPC 主力）僅通過單次 smoke test（見 `2026-10-07-pyworkbench-verification-done.md`）。file-IPC / socket 為 gRPC 授權失敗時的退路，拆除等於賭 PyWorkbench 穩定。

### 活引用鏈（不能直接刪）

| 檔案 | 內容 |
| --- | --- |
| `bridges/workbench_filequeue.py` | 檔案 IPC bridge 實作 |
| `bridges/workbench_socket.py` | socket 傳輸實作 |
| `bridges/transport.py` | 第 5-6 行 import 上述兩者；`send_command` 依序嘗試 socket → filequeue |
| `products/workbench/tools.py` | 第 25、34 行 import filequeue 與 transport；提供 `start_workbench_bridge`（第 80 行）／`stop_workbench_bridge`（第 132 行）兩個 MCP 工具 |

### 糾纏點（移除時須保留，不可一起砍）

`bridges/workbench_batch.py` 的 `detect_workbench_environment` / `find_workbench_exe` 是**環境偵測**（非 fallback 傳輸），被以下活引用：
- `tools/connection_tools.py` 第 128、138 行
- `products/workbench/tools.py` 第 17 行（`workbench_detect_tool`）

移除 fallback 時，環境偵測需保留或搬家（例如移至 `core/paths.py` 或獨立模組）。

### 觸發條件（何時可做）

PyWorkbench 累積多次穩定實機使用後，確認可取代 fallback，才執行：移除 file-IPC/socket bridge、`transport.py`、`start/stop_workbench_bridge` 工具；保留環境偵測。屬破壞性重構，需 reviewer 把關 + 全量 pytest 驗證。

---

## Backlog 2：任務 7 多工作區隔離——OS 級隔離（方案 C）

**狀態**：D+A 已結案（2026-10-07），方案 C 列 backlog。
**暫緩理由**：D+A 對「降低 context 占用、避免 session 間工具污染」已足夠。方案 C 成本高一個量級（多進程管理、IPC、進程生命週期），只在「同機多專案需要作業系統級強隔離」才值得。

### 已實作（方案 D + A）

| 機制 | 位置 |
| --- | --- |
| 方案 A：SessionRegistry workspace 維度（多 workspace 完全隔離，`current` 依 (workspace, product) 追蹤） | `core/sessions.py` 第 29-34 行 |
| 方案 D：per-session 工具可見性 middleware（協議層 `on_list_tools`，依 session 偏好收斂工具可見集） | `core/visibility.py` + `shared.py` 第 262-267 行 |
| `ans_session_set_workspace` MCP 工具（session 宣告可見 product 集） | `tools/session_manager_tools.py` 第 101 行 |

`core/visibility.py` docstring 第 6 行明載設計取捨：「不需要多進程、不需要為每個 workspace mount 子 server」——刻意以輕量 in-process 隔離取代 OS 級隔離。

### 未實作（方案 C）

OS 級隔離：每個 workspace 獨立子進程 + 檔案系統登錄表。

### 觸發條件（何時可做）

出現同機多專案需要作業系統級強隔離的真實產品需求時，才評估方案 C。方案對比詳見 `2026-10-05-workspace-session-isolation-options.md`。

---

## 判讀準則

兩項皆為「技術決策暫緩」，非技術債遺漏：
- 系統功能正常、全量 pytest 全綠、ruff 零錯誤。
- 推進前請先確認觸發條件成立，避免無需求的過度工程（參見 `00-behavior.md` Lazy Senior 原則）。
