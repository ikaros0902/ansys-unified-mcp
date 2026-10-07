# PyWorkbench 通道實機驗證任務卡（待排程 / UNVERIFIED）

**狀態**：✅ 已驗證 @2026-10-07。launch → run_script（template probe）→ exit 雙向通道通過。
**驗證證據**：底層 `launch_workbench(show_gui=True)` 成功（server_version=261），冷啟動耗時 192.1s；
journal `GetTemplate(TemplateName='Static Structural', Solver='ANSYS')` 回傳
`wb_script_result = {"template": "/Schematic/Template:Static Structural (ANSYS)"}`，確認雙向通道正常；`wb.exit()` 關閉 server 無殘留進程。
**路徑修正**：原任務卡所述 `products/workbench.py` / `tools/workbench_pyworkbench.py` 於目錄重構後已收斂為
`src/ansys_unified_mcp/products/workbench/{facade,tools}.py`；3 處 `STATUS: UNVERIFIED` 註記已清除改標 VERIFIED。
**已知事項**：WB 冷啟動約 3 分鐘，超過 controller `DEFAULT_SCRIPT_TIMEOUT=60s`（該 timeout 僅套用於 run_script，不套 launch）；長時 journal 需注意。
**執行時機**：此驗證會啟動 Workbench server（屬連線動作），需本機已安裝並可授權 Ansys Workbench，故不納入自動化 CI。
**對應決策**：本任務卡對應使用者決策「3=b」（PyWorkbench 驗證排程待實機），由主線任務收斂時建立。

---

## 一、為何需要這一步

`products/workbench.py` 的 `WorkbenchController` 與 `tools/workbench_pyworkbench.py` 的 8 個
PyWorkbench 工具已寫好，但從未實機連線驗證。Phase 1 的後續清理（移除舊 file-IPC bridge、
改寫既有 bridge 工具、`workbench_bridge.py` → `job_launcher.py` 改名）全部卡在此驗證通過之前，
不得先行，以免在未驗證的通道上拆除可用的 fallback。

---

## 二、前置檢查

- `.venv` 已安裝 PyWorkbench：
  ```powershell
  .venv\Scripts\python.exe -m pip show ansys-workbench-core
  ```
  應顯示 `Version: 0.14.0`（已確認安裝）。
- 本機已安裝且可授權 Ansys Workbench（PyWorkbench 需在有 WB 的機器啟動 server）。

---

## 三、驗證方式 A：直接用 PyWorkbench（.venv）

無副作用冒煙測試（只探測 template，不建系統、不求解）：

```python
from ansys.workbench.core import launch_workbench
wb = launch_workbench(show_gui=True)          # 啟動 WB server + client（連線動作）
print("server_version:", wb.server_version)   # 有版本字串 = 連上了
print(wb.run_script_string(
    "import json\n"
    "tpl = GetTemplate(TemplateName='Static Structural', Solver='ANSYS')\n"
    "wb_script_result = json.dumps({'template': str(tpl)})"))
wb.exit()                                     # 關閉 server（PyWorkbench 慣例）
```

---

## 四、驗證方式 B：透過本專案的 MCP 工具

1. `workbench_launch_server`（或對已開的 server 用 `workbench_connect_server(port=...)`）
   → 回 `{"ok": true, "key": ..., "server_version": ...}` 即連上。
2. `workbench_server_status` → `{"connected": true, "sessions": [...], "current": ...}`。
3. `workbench_run_script_live(script="import json\nwb_script_result=json.dumps({'ping':1})")`
   → 回 `{"ok": true, "output": ...}`。
4. `workbench_disconnect_server` 結束（只離線，不關 server）。

---

## 五、連上 vs 沒連上 判讀

| 現象 | 判讀 |
|---|---|
| `server_version` 有值 / 工具回 `ok:true` 且含 `server_version` | 已連上 |
| `run_script_string` 能回傳 `wb_script_result` 內容 | 雙向通道正常 |
| 連續下多個 journal 全程不閃退 | 穩定（勝過手刻 batch 的 `0xC000013A`） |
| `ok:false`，error 提及連線/逾時/找不到 WB | 未連上（查 WB 安裝、授權、port） |
| `Error: Not connected to Workbench.` | 尚未 launch/connect，先做第三或第四節第 1 步 |

---

## 六、驗證通過後的動作（解鎖 Phase 1 收尾）

1. 移除 `products/workbench.py`、`tools/workbench_pyworkbench.py` 的 `STATUS: UNVERIFIED` 註記
   （改為「已驗證 @日期」）。
2. 進 Phase 1 收尾：移除舊 file-IPC bridge、改寫既有 bridge 工具、`workbench_bridge.py`
   → `job_launcher.py` 改名、清 `tools/` 殘留執行期資料、佔位檔歸位。

---

## 七、來源

本卡整合自 `agents/contexts/pyansys-mapping-and-roadmap.md` 第 5 節（如何驗證 PyWorkbench 連線）
與第 4 節 Phase 1 收尾清單，獨立成卡以便實機驗證時直接照跑，不需回溯長文。
