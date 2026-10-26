---
name: ansys-spaceclaim-component-library
description: 從已開啟的 SpaceClaim 或 Discovery 裝配體辨識標準件、另存獨立模型並驗證，適用大型裝配體子件擷取、BOM 對照與 Common Part 查表建庫。
---

# SpaceClaim 元件擷取與查表建庫

目標是產生有來源、分類依據與重新匯入驗證的獨立幾何檔案。從裝配體擷取、幾何簡化及建立求解器可用資料庫是不同階段；依使用者當次授權執行。

## 先決定交付範圍

- **擷取素材**：辨識實際存在的元件，另存至原始素材分類目錄，例如 `Complex_Model`。
- **建立可重用資料庫**：簡化一次、存成實際幾何檔，再以料號查表讀檔；參數化重建腳本不等於已存幾何資料庫。
- **執行期取代**：使用已驗證的料號規則與座標轉換插入存檔；不要因為建庫使用人工或 LLM 判讀，就把同樣流程強加到執行期。

## 執行流程

1. **確認真實工作階段**。以新連線的原生腳本查作用中 root、元件名稱與 body 數，必要時讀取監聽埠所屬程序及執行檔版本。MCP 狀態或名稱清單可能來自快取。保留目前模型；已有模型時不要重複建立 design 或重開整機。
2. **先建立完整索引**。保存元件階層、完整來源路徑及重複次數，也搜尋 body 名稱。需要在既有 gRPC session 盤點時，可用 [inventory_components.py](scripts/inventory_components.py)；用 `--args-json` 傳入 `name_contains` 篩選詞，回傳內容有筆數上限。將 MCAD 與 BOM 對照；BOM 列項不代表目前幾何包含該零件。未命中名稱只能支持「未找到對應命名模型」。
3. **確認分類**。料號、BOM 描述、尺寸與 GUI 預覽共同支持分類。插槽的 refdes 可能只是 `J33`；名稱不是 slot 也不代表它不是插槽。假 DIMM、風扇尺寸變體與五金候選要明確標識，不能硬塞入既有規格分類。
4. **擷取代表件**。依唯一模板與幾何變體選代表件；同名不保證相同幾何。需要每個 occurrence 時，保留其裝配位置與識別資訊。沿用使用者要求的 GUI 作業方式。
5. **另存獨立模型**。V251 已實測可用 `ComponentHelper.OpenComponentDocument(ComponentSelection.Create(component), None)` 後 `DocumentSave.Execute(step_path)`。可用 [open_component_export.py](scripts/open_component_export.py) 傳入完整元件階層名稱與輸出路徑；腳本會拒絕覆寫、確認開啟後 body 數、另存並檢查檔案。先確認新作用中 part 的 body 數與目標一致，再存檔。保存原裝配體的參考，勿依賴跨腳本的未宣告全域變數。
6. **重新匯入驗證**。檢查檔案實際存在、格式、大小及雜湊；重新開啟輸出，與來源比較 body 數、表面積、可計算體積及一致座標下的外形尺寸。容差依使用者與工程用途設定，本案例的 5% 不是所有 CAD 轉檔的通用標準。
7. **整理通過的素材**。只將已確認分類且驗證通過的檔案放入正式分類目錄；來源前綴與 manifest 保留追溯性。未確認或未通過的候選另放待確認區，不能用其他檔案成功概括整批通過。

## 非直覺限制

- 大型整機的 gRPC 匯入／匯出可能超過訊息限制。模型已在 GUI 記憶體中時，先查結構並擷取元件，不必再次傳輸整個檔案。
- 訊息上限只能解決 payload 問題；不能解決錯誤埠、沙箱連線限制或無回應的 bridge。無輸出也不等於沒有程序；先看退出碼與錯誤。
- `ExportComponent` API 存在，不保證指定選取或目前執行上下文可以成功匯出。對照錯誤與實際產物，不以 API 查詢結果宣稱完成。
- **原生另存不一定隔離元件**：本次 `.scdoc` 要求產生 `.scdocx`，包含整機資料。確認實際副檔名、根階層及幾何範圍；不要把一個元件的視圖當成獨立文件的證據。
- body 可能是實體或開放曲面。零體積不能直接判為遺失，也不能把曲面 CAD 宣稱為封閉可求解實體。體積計算失敗要記錄數量；可計算部分體積不等於總質量。
- STEP 重新匯入可能改變 body／face 分組。數量不一致時先保留未通過狀態，再用完整子樹覆蓋、逐組面積與尺寸等證據診斷；不要直接刪除數量檢查來取得綠燈。

## 按需讀取

- 連線、原生 API 與錯誤診斷：[session-and-export.md](references/session-and-export.md)。
- 重新匯入、座標框架與驗收紀錄：[verification.md](references/verification.md)。
- Godzilla 腳本的通用化對照、參數介面與不適合直接重用的探針：[godzilla-script-migration.md](references/godzilla-script-migration.md)。
- Godzilla／Interstellar 實測與 Common Part 維護界線：[case-notes.md](references/case-notes.md)。這些是特定案例資料，不能直接當作新專案的零件清單。
- 需要直接連線既有 gRPC 並執行原生腳本時，使用 [run_live_script.py](scripts/run_live_script.py)。它不啟動新 ANSYS 程序；執行的腳本仍須在當次使用者授權範圍內。
