# 工程經驗沉澱 2026-10-05（通用法則，去專案特例）

本日透過多輪 workflow（haiku 調查 → sonnet 實作 → opus 審查 loop）完成架構清理，過程踩到數個可複用的通用教訓。

---

## 一、Python 同名 package 與 module 並存時的遮蔽規則

**法則**：當 `foo/`（含 `__init__.py` 的套件）與 `foo.py`（模組）同名並存於同一層，**package 優先**，`foo.py` 永遠被遮蔽、無法被 import 到。

**驗證手段（勝過靜態推理）**：
```python
import foo; print(foo.__file__)   # 實測解析到哪個檔
```
刪除「疑似死碼」前，不要只靠 grep 看引用字串——`from pkg.foo import x` 這種裸 import 表面像引用扁平檔，實際全打到目錄套件。用 `__file__` 實測是最硬的證據。

**延伸**：刪檔前的完整安全檢查清單——(1) grep 引用、(2) `__file__` 實測遮蔽、(3) 打包設定（hatchling/setuptools）有無逐檔白名單、(4) 字串/路徑形式的動態讀取、(5) 測試檔是否 import 或讀內容斷言。

---

## 二、FastMCP 工具簽名的硬限制（版本相依）

**法則**：FastMCP（實測 3.4.5）會把 `@mcp.tool()` 函式簽名轉成 JSON Schema，**不支援 `**kwargs` 型參數**——裝飾階段即拋 `ValueError`。

**後果嚴重性**：若該工具模組被 `__main__` 無條件 import，整個 server 進入點崩潰、全量測試 collection error。這類 **import-time 註冊失敗，靜態 AST 檢查攔不住**，只有實跑才抓得到。

**正解**：需要彈性參數時用單一結構化參數 `options: dict[str, Any] | None = None`，內部 `**(options or {})` 展開委派。

**延伸測試法則**：對「工具是否成功註冊」要寫 smoke test（`mcp.list_tools()` 斷言含目標工具名），不能只斷言「函式可被 AST 解析」——後者對 import-time 失敗完全無感。

---

## 三、git commit 的 stage 陷阱

**法則**：`git rm` 標記的刪除會進 staging，但同一批次中被子代理/編輯器改動的其他檔案若未 `git add`，`git commit -m` **不會帶上它們**。結果是 commit 內容與工作樹不一致——工作樹測試通過，但該 commit 單獨 checkout 會不自洽。

**防範**：commit 前一律 `git status --short` 核對 staged 清單，確認「預期要進 commit 的檔」全部是 staged（`M `/`A `/`D ` 在第一欄），而非 unstaged（第二欄 ` M`）。精確 stage 時逐檔列出路徑，不用 `git add .`。

---

## 四、PowerShell 下 git 的 exit code 假失敗

**現象**：git push/commit 把進度訊息寫到 stderr，PowerShell 的 `2>&1` 或管線會把它當錯誤流，導致回報 `exit code 1` 但實際操作成功。

**可靠驗證**：不信 exit code，改用 `git ls-remote <url> refs/heads/<branch>` 比對本機與遠端 SHA 是否一致。三邊（local/GitHub/GitLab）SHA 相同才是推送成功的鐵證。

**延伸**：PowerShell 管線接 `Select-String`/`findstr` 處理含中文的 git 輸出時常吞輸出或亂碼。穩定作法：`chcp 65001` 設 UTF-8、或輸出到暫存檔再讀、或用 `git --no-pager` 直接輸出。

---

## 五、製造/檢查分離在多代理 workflow 的實際價值

**本日三次驗證此原則擋下錯誤**：
1. 規劃段判「tools/ 三檔是零引用死碼」→ 審查段親自 grep 發現被 5 個測試引用，擋下破壞性刪除。
2. 實作段第一版工具用 `**kwargs` 簽名 → 審查段實跑發現 server 崩潰，逐輪逼出 `options: dict` 正解。
3. 規劃段判「工具過多因產品模組全載入」→ 審查段實測各 profile 工具數，否證並找到真因（transitive import）。

**法則**：規劃/實作段的「結論」在未經獨立實跑前都是假設。審查段的價值不在複述，而在**親自跑驗證、用證據推翻上游假設**。審查段必須有獨立執行能力（跑 pytest、grep、實測 API），否則退化為橡皮圖章。

**延伸**：子代理工具集受限時（如無刪檔/終端能力），不應偽裝完成，而應完成「安全性論證」後降級交付給有權限的主 agent 執行。主 agent 須親自複核 diff，不盲信子代理多輪往返的矛盾判決。

---

## 六、真實環境整合測試的破壞性副作用

**法則**：對「使用者手動開啟的」外部應用（SpaceClaim/Mechanical 等）寫整合測試時，teardown **絕不能呼叫 `close()`/`exit()` 這類會關閉使用者 session 的操作**——那會破壞使用者正在用的設計/專案。

**正解**：teardown 只清理測試自己的註冊狀態（`registry.drop` + 重置 module global），不觸碰 backend 實體。

**驗證冪等性**：整合測試要**連跑兩次**驗證——第一次過、第二次因自我污染而失敗，是 teardown 破壞性的典型信號。

**延伸——假性成功陷阱**：批次/委派型執行器的成敗判定，若只靠通用 `looks_like_error` 關鍵詞比對，會漏掉「未連線短路文案」這類不含錯誤標記卻實為失敗的回傳（例如「XX 未連線，請先執行 YY」）。對未連線 session 執行會回報「全部成功」卻零實際操作。需補前置條件失敗判定，攔截這類短路文案。耗時 0.08ms 這種異常低的執行時間本身就是「零 RPC 假性成功」的鐵證。

---

## 七、commit 訊息編碼損毀不可還原

**現象**：某 commit（b6dedd1）的中文訊息存入 git object 時編碼就已損毀，事後任何 `git show`/重新解碼都還原不回原文。

**法則**：這與終端顯示的 code page 問題不同——顯示亂碼可透過 `chcp 65001` 或正確解碼修復；但**存入 object 的 bytes 本身非法則永久損毀**。commit 當下就要確保環境 UTF-8 正確，事後無法補救。驗證：新 commit 後用 `git show -s --format=%B` 確認訊息可讀。
