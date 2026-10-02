# docs/archive — 歷史快照區

> ## ⚠️ 本目錄所有文件皆為歷史快照，不可作為現況依據
>
> 此處保存的是專案演進過程中的需求書、審計報告與階段性成果紀錄。它們的價值在於**追溯當時的決策脈絡**，
> 而非描述專案現況。檔內的檔案數、測試數、技能數、版本號與磁碟路徑**均已過期**。
>
> 需要專案現況時，請改看：
>
> | 需求 | 應參閱 |
> | --- | --- |
> | 專案概觀與快速上手 | [`README.md`](../../README.md) |
> | 系統架構與命名慣例 | [`ARCHITECTURE.md`](../../ARCHITECTURE.md) |
> | 完整文件索引 | [`docs/index.md`](../index.md) |
> | 測試基礎設施與執行指令 | [`docs/testing/TEST_INFRA.md`](../testing/TEST_INFRA.md) |
> | 安裝與部署 SOP | [`docs/deployment/DEPLOYMENT_SOP.md`](../deployment/DEPLOYMENT_SOP.md) |

---

## 歸檔清單與歸檔理由

| 檔案 | 歸檔理由 |
| --- | --- |
| [`CODE_AUDIT_REPORT.md`](CODE_AUDIT_REPORT.md) | 舊分支 `refactor/unified-arch` 的程式碼審視快照；稱「約 24 個 Python 檔」（現為 81）、提及不存在的 `requirements.txt`。 |
| [`TEST_READY.md`](TEST_READY.md) | 單次測試就緒發布快照；稱「10 個測試檔 / 115 用例」（現為 37 個 `test_*.py`）。 |
| [`ANSYS_AUTOMATION_MASTER_PLAN.md`](ANSYS_AUTOMATION_MASTER_PLAN.md) | 早期自動化藍圖；稱「10 項技能」（現況技能清單與數量見 [`skills/README.md`](../../skills/README.md)）、寫定 ANSYS 2025 R1 v251、含已失效的 `F:` 磁碟路徑。 |
| [`ORIGINAL_REQUEST.md`](ORIGINAL_REQUEST.md) | 原始需求書（最早紀錄標註 2026-09-05）；描述預期目標而非交付現況，且同檔內新舊工作目錄並存不一致。 |
| [`PROJECT.md`](PROJECT.md) | Phase 1 規格書；與 `ORIGINAL_REQUEST.md` 為同批需求的不同視角，範圍僅及 Phase 1。 |
| [`ANSYS_MCP_DELIVERY_WALKTHROUGH.md`](ANSYS_MCP_DELIVERY_WALKTHROUGH.md) | 主題為個人全域設定庫（dotfiles）跨機器同步，與本專案程式碼無直接關係；內含大量已失效的 `file:///` 本機絕對路徑。 |

---

## 維護約定

- 本目錄的檔案**只讀不改**。若內容需要更新，代表它已不屬於 archive，應改寫進 `docs/` 對應的現況目錄。
- 新增歸檔檔案時，請同時在檔案最上方插入歷史快照警示區塊，並在上表補一列歸檔理由。
- 本目錄檔案內的絕對路徑已遮罩為 `%WORKBENCH_MCP_ROOT%`（專案根目錄）與 `%USERPROFILE%`（使用者家目錄），避免洩漏本機帳號資訊。
