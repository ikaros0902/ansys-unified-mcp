# ANSYS-unified-MCP 架構優化與重構總計畫

> 基於 `Cai-aa/CAE-Agent-Hub` 三個 ANSYS MCP 目錄的源碼精讀，與本專案 `ANSYS-unified-MCP` 的自我檢視。

---

## 一、架構對比總覽

### 1.1 外部參照：CAE-Agent-Hub 的 ANSYS MCP 實作

| MCP 目錄 | 通訊模式 | 核心特色 |
|---------|---------|---------|
| **Fluent MCP** | PyFluent 原生 gRPC | 獨立 `FastMCP("Ansys Fluent MCP")`；內建 `INSTRUCTIONS` 教 Agent 使用順序 |
| **Workbench MCP** | 三種並存（subprocess / File-IPC / TCP Socket），Agent 可選 | `SUPPORTED_TRANSPORTS = {"queue", "socket"}`；`mechanical_socket_timer_v7.py` 是跑在 Mechanical ACT 內的 IronPython Socket Listener |
| **PyAnsys** | ANSYS 官方 PyAnsys MCP 倉庫的鏡像快照（2026-09-04） | 6 個產品 MCP + `pyansys-common-mcp` 公共基礎庫 |

**他們的三層分離架構：**
```
server.py              → Layer 1: 薄皮 @mcp.tool 註冊，每個 Tool 一行委派
tools/*_bridge.py      → Layer 2: 通訊層（subprocess / File-IPC / TCP Socket）
tools/*_workflows.py   → Layer 3: 業務邏輯（匯入幾何、求解、匯出 Evidence）
workbench_plugin/      → 部署到 CAE 軟體內部的 IronPython ACT 腳本
```

### 1.2 我們的優勢（不需改的部分）

| 模組 | 說明 | CAE-Agent-Hub 有嗎？ |
|------|------|---------------------|
| `sentinel/queue.py`（507 行） | 非同步作業佇列 + Watchdog + CircuitBreaker + 沙盒 | ❌ |
| `gatekeeper/`（8 條物理規則） | 落摔速度、CTE 非零、模態截止頻率等前檢 + 自愈處方箋 | ❌ |
| `script_guard.py` | Import 黑名單 + 危險模式 regex + 審計日誌 | ❌ |
| `drivers/base.py` | 統一求解器抽象基類（生命週期合約） | ❌ |
| `jobs/manager.py` + `sandbox.py` | 集中式作業管理 + 路徑穿越防護 | ❌ |
| `as_envelope()` | 全局 `{"ok": true/false}` 統一信封格式 | ❌ |

### 1.3 我們需要補的

| 缺口 | 來源 |
|------|------|
| TCP Socket Bridge（Mechanical 即時通訊） | 參照 `mechanical_socket_timer_v7.py` |
| Dual Transport 選擇機制 | 參照 `SUPPORTED_TRANSPORTS` |
| Evidence Gate（階段間 Hash + Semantic ID 驗證） | 參照 `mechanical_export_evidence` |
| Tool Namespace Lazy Loading | 參照他們的 Micro-MCP 拆分思路 |
| Agent INSTRUCTIONS 內嵌 | 參照 Fluent MCP 的 `INSTRUCTIONS` 字串 |
| Skill Phase Gate（requires/produces 約定） | 參照 FEP Agent Hub 的 Phase-based Skill |

### 1.4 現有 Model Tree 的結構性問題

1. **`tools/` 是雜物間**：`workbench_filebridge.py`（1303 行）和 `mechanical.py`（1487 行）各自混合了通訊層、業務邏輯和 Tool 註冊
2. **同一產品散落三處**：Mechanical 的邏輯分散在 `tools/`、`products/`、`drivers/` 三個目錄
3. **`bridges/` 只有一個檔案**：真正的 Bridge（File-IPC）卻放在 `tools/` 裡
4. **根層級散落雜物**：`connection_manager.py`、`docs/` 模組位置不恰當
5. **Lazy Loading 只實作了一半**：`sim_tools.py` 有 `ANSYS_MCP_PROFILE` 條件載入，但其他模組沒有

---

## 二、統一重構計畫

### Phase 1：通訊層重構 + TCP Socket Bridge

**目標**：拆解 `workbench_filebridge.py` 巨石，建立乾淨的通訊層目錄，並導入 TCP Socket Bridge。

#### 目錄搬遷

| 動作 | 原始位置 | 新位置 |
|------|---------|-------|
| 改名 | `bridges/workbench_bridge.py` | `bridges/workbench_batch.py` |
| 拆出通訊邏輯 | `tools/workbench_filebridge.py` 的 File-IPC 部分 | `bridges/workbench_filequeue.py` |
| 拆出 Tool 註冊 | `tools/workbench_filebridge.py` 的 `@mcp.tool` 部分 | `tools/workbench_tools.py` |
| 合併入 | `tools/workbench.py` | `tools/workbench_tools.py` |
| 合併入 | `tools/workbench_pyworkbench.py` | `tools/workbench_tools.py` |
| 搬入 | `connection_manager.py`（根層） | `bridges/connection_manager.py` |

#### 新增檔案

| 檔案 | 內容 |
|------|------|
| `bridges/workbench_socket.py` | TCP Socket 客戶端，null-terminated JSON 協議，連接 localhost:9885 |
| `bridges/transport.py` | Transport 選擇器：`auto`（先 Socket 失敗降級 File-IPC）/ `socket` / `queue` |
| `plugins/mechanical_socket_listener.py` | IronPython ACT Plugin，參照 `mechanical_socket_timer_v7.py`。.NET `JavaScriptSerializer`、`__builtin__` 狀態持久化、background daemon thread |

#### 修改檔案

| 檔案 | 改動 |
|------|------|
| `shared.py` | 在 `FastMCP()` 初始化加入 `instructions` 參數 |
| `tools/workbench_tools.py`（新） | 委派到 `bridges/transport.py`，支持 `transport` 參數 |

#### 結果

```
bridges/                         # 所有通訊層集中
├── workbench_batch.py           # subprocess 批次啟動
├── workbench_filequeue.py       # File-IPC（REQUEST_DIR / RESPONSE_DIR）
├── workbench_socket.py          # [新] TCP Socket 客戶端
├── transport.py                 # [新] Transport 選擇器
└── connection_manager.py        # [搬入]

plugins/                         # [新目錄] 部署到 CAE 內部的腳本
└── mechanical_socket_listener.py
```

**預估**：新增 4 檔 + 修改/搬遷 5 檔。`workbench_filebridge.py`（1303 行）被拆為 2 個職責清晰的檔案。

---

### Phase 2：Tool 層瘦身 + 產品分離

**目標**：將 `tools/` 從「什麼都塞的雜物間」變成「只做薄皮註冊的 Layer 1」。

#### 拆解 `tools/mechanical.py`（1487 行）

| 動作 | 內容 |
|------|------|
| 業務邏輯下沉 | 提取到 `products/mechanical.py`（已有 facade） |
| Tool 瘦身 | `tools/mechanical_tools.py` 每個 `@mcp.tool` 只留 1-3 行委派 |
| 改名 | `tools/mechanical_workflows.py` → `tools/mechanical_workflow_tools.py` |

#### 拆分 `tools/sim_tools.py`（504 行）

| 動作 | 內容 |
|------|------|
| 拆出 | Fluent 相關 Tool → `tools/fluent_tools.py` |
| 拆出 | SpaceClaim 相關 Tool → `tools/geometry_tools.py` |
| 提升 | `ANSYS_MCP_PROFILE` 條件載入邏輯 → `shared.py`（全局 profile 機制） |

#### 統一命名

| 原始 | 新名稱 |
|------|-------|
| `tools/optislang.py` | `tools/optislang_tools.py` |
| `tools/connection_doctor.py` | `tools/connection_tools.py` |

#### 結果

```
tools/                           # Layer 1: 薄皮 @mcp.tool 註冊
├── mechanical_tools.py          # [瘦身] 原 1487 行 → ~200 行委派
├── mechanical_workflow_tools.py
├── workbench_tools.py           # [Phase 1 產物]
├── fluent_tools.py              # [拆出]
├── geometry_tools.py            # [拆出]
├── dpf_tools.py
├── optislang_tools.py           # [改名]
├── sentinel_tools.py
├── connection_tools.py          # [改名]
├── intent_tools.py
└── docs_tools.py
```

**預估**：`mechanical.py`（1487 行）瘦身為 ~200 行。`sim_tools.py` 拆為 2 個獨立模組。

---

### Phase 3：Evidence Gate + Gatekeeper 擴充

**目標**：在現有 8 條物理規則之上，加入階段間資料完整性驗證。

#### 新增檔案

| 檔案 | 內容 |
|------|------|
| `gatekeeper/evidence.py` | `EvidenceManifest` 類：`file_path`, `sha256_hash`, `semantic_ids`（Named Selection 清單等）, `timestamp`。提供 `create_manifest()` / `verify_manifest()` |
| `gatekeeper/rules/evidence_rules.py` | `EvidenceIntegrityRule`：驗證前階段 manifest 的 Hash 是否吻合 |

#### 修改檔案

| 檔案 | 改動 |
|------|------|
| `gatekeeper/gatekeeper.py` | 在現有 8 條物理規則清單中加入 `EvidenceIntegrityRule` |
| `workflows/drop_test.py` 等 | 在幾何匯出後自動 `create_manifest()`，求解前自動 `verify_manifest()` |

#### 結果

```
gatekeeper/
├── gatekeeper.py                # 主引擎（9 條規則）
├── prescription.py
├── evidence.py                  # [新增]
└── rules/
    ├── drop_impact_rules.py
    ├── thermal_rules.py
    ├── vibration_rules.py
    ├── unit_consistency.py
    └── evidence_rules.py        # [新增]
```

**預估**：新增 2 檔 + 修改 2-3 檔。

---

### Phase 4：Lazy Loading + Skill Phase Gate + PyAnsys 評估

**目標**：降低 Agent 的 Token 負荷，強化技能引導，評估官方生態整合。

#### 4a. Tool Namespace Lazy Loading

| 檔案 | 改動 |
|------|------|
| `shared.py` | 將 `sim_tools.py` 既有的 `ANSYS_MCP_PROFILE` 提升為全局機制。根據 `ANSYS_MCP_PRODUCTS=mechanical,fluent` 環境變數，只 import 對應的 `tools/*_tools.py` 模組 |
| `__main__.py` | 加入產品篩選啟動邏輯 |

預設全部載入，完全向後相容。

#### 4b. Skill Phase Gate

修改 `SKILLs/` 下的 Markdown 技能手冊，在 YAML frontmatter 加入：

```yaml
phase_gate:
  requires: [geometry_manifest]   # 前一階段必須產出的 manifest
  produces: [mesh_manifest]       # 本階段完成後產出的 manifest
```

Phase Gate 的強制由 AI Client 端負責，符合 MCP 職責分離原則。

#### 4c. 官方 PyAnsys MCP 評估

產出 `docs/PYANSYS_MCP_EVALUATION.md`，評估 ANSYS 官方的 6 個 PyAnsys MCP Server（特別是 `pyansys-common-mcp` 基礎庫），判斷是否可直接整合或替代部分 driver 實作。

---

## 三、不做的事（及理由）

| 提議 | 為何不做 |
|------|---------|
| Fluent API / Builder Pattern | MCP 的消費者是 Agent 透過 JSON-RPC 呼叫離散 Tool，不是人類寫 Python 鏈式呼叫 |
| MCP Server 內建 Agent Orchestrator | 違反 MCP 職責分離。CAE-Agent-Hub 也沒做——編排留在 AI Client 端 |
| 拆成 Micro-MCP（多個獨立 Server） | 部署複雜度暴增。用 Lazy Loading 達到類似效果 |
| 重寫 sentinel/queue 或 gatekeeper | CAE-Agent-Hub 沒有這些模組，我們已經領先 |
| 刪除 drivers/ 目錄 | 核心領域邏輯層，穩定且職責清晰 |

---

## 四、最終 Model Tree（全部 Phase 完成後）

```
src/ansys_unified_mcp/
├── __init__.py
├── __main__.py
├── config.py
├── shared.py                          # FastMCP + envelope + profile 載入 + INSTRUCTIONS
│
├── core/                              # 核心基礎設施（不動）
│   ├── paths.py
│   ├── sessions.py
│   ├── timeout.py
│   ├── script_guard.py
│   └── sentinel/
│       ├── queue.py                   # 507 行非同步佇列
│       ├── circuit_breaker.py
│       ├── daemon.py
│       ├── watchdog.py
│       └── parsers/{fluent,lsdyna,mechanical}.py
│
├── gatekeeper/                        # 安全閘門（Phase 3 擴充）
│   ├── gatekeeper.py                  # 9 條規則（+1 Evidence）
│   ├── prescription.py
│   ├── evidence.py                    # [Phase 3 新增]
│   └── rules/
│       ├── drop_impact_rules.py
│       ├── thermal_rules.py
│       ├── vibration_rules.py
│       ├── unit_consistency.py
│       └── evidence_rules.py          # [Phase 3 新增]
│
├── bridges/                           # Layer 2: 通訊層（Phase 1 重組）
│   ├── workbench_batch.py             # [改名] subprocess 批次
│   ├── workbench_filequeue.py         # [拆出] File-IPC
│   ├── workbench_socket.py            # [Phase 1 新增] TCP Socket
│   ├── transport.py                   # [Phase 1 新增] Transport 選擇器
│   └── connection_manager.py          # [搬入]
│
├── drivers/                           # 求解器進程管理（不動）
│   ├── base.py
│   ├── mechanical_driver.py
│   ├── fluent_driver.py
│   ├── lsdyna_driver.py
│   ├── spaceclaim_driver.py
│   ├── optislang_driver.py
│   ├── icepak_driver.py
│   ├── contour_helper.py
│   └── sim_impl.py
│
├── products/                          # Session Facade（不動，Phase 2 吸收業務邏輯）
│   ├── mechanical.py
│   ├── fluent.py
│   ├── geometry.py
│   ├── workbench.py
│   ├── optislang.py
│   └── dpf.py
│
├── tools/                             # Layer 1: 薄皮 @mcp.tool 註冊（Phase 1+2 瘦身）
│   ├── mechanical_tools.py            # [瘦身] ~200 行委派
│   ├── mechanical_workflow_tools.py
│   ├── workbench_tools.py             # [Phase 1 合併]
│   ├── fluent_tools.py                # [Phase 2 拆出]
│   ├── geometry_tools.py              # [Phase 2 拆出]
│   ├── dpf_tools.py
│   ├── optislang_tools.py             # [改名]
│   ├── sentinel_tools.py
│   ├── connection_tools.py            # [改名]
│   ├── intent_tools.py
│   └── docs_tools.py
│
├── workflows/                         # 端到端工作流（不動）
│   ├── drop_test.py
│   ├── shock_analysis.py
│   ├── random_vibration.py
│   ├── thermal_warpage.py
│   ├── surrogate_model.py
│   └── workbench_links.py
│
├── postprocessing/                    # 後處理（不動）
├── reporting/                         # 報告生成（不動）
├── jobs/                              # 作業管理（不動）
│
├── plugins/                           # [Phase 1 新增] CAE 內部部署腳本
│   └── mechanical_socket_listener.py
│
└── scripts/
    └── ansys_workbench_bridge.wbjn
```

---

## 五、改動影響總矩陣

| Phase | 核心改動 | 新增 | 搬遷/改名 | 修改 | 刪除 | 破壞性 |
|-------|---------|------|----------|------|------|--------|
| 1 通訊層重構 + TCP Socket | 拆解 `workbench_filebridge.py`（1303 行） | 4 檔 | 5 檔 | 2 檔 | 3 檔（合併後） | 無 |
| 2 Tool 瘦身 + 產品分離 | 瘦身 `mechanical.py`（1487 行）、拆分 `sim_tools.py` | 2 檔 | 2 檔改名 | 3 檔 | 2 檔（合併後） | 無 |
| 3 Evidence Gate | 擴充 Gatekeeper | 2 檔 | — | 2-3 檔 | — | 無 |
| 4 Lazy Loading + Skill Gate + PyAnsys | 全局 profile + Markdown frontmatter | 1 報告 | — | 2 檔 + Markdown | — | 無 |

**449 個現有測試在各階段完成後均應全數通過。**

---

## 六、調用鏈概覽（重構後）

```
Agent 發出 JSON-RPC 請求
    ↓
tools/*_tools.py          ← Layer 1: 薄皮 @mcp.tool 註冊，1-3 行委派
    ↓
products/*.py             ← Session Facade，管理 gRPC / 連線狀態
bridges/transport.py      ← 通訊選擇器 (auto → socket → filequeue fallback)
    ↓
drivers/*_driver.py       ← 求解器進程管理，BaseSolverDriver 生命週期
core/sentinel/queue.py    ← 非同步作業佇列 + Watchdog + CircuitBreaker
    ↓
gatekeeper/               ← 前檢閘門：8 條物理規則 + Evidence Hash 驗證
core/script_guard.py      ← 腳本安全掃描：import 黑名單 + regex + 審計
    ↓
plugins/                  ← 部署在 Mechanical 內部的 IronPython Socket Listener
```
