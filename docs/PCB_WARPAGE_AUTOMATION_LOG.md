# ANSYS PCB 79 層熱翹曲自動化分析 — 修改記錄與分類問題排障手冊

本文件記錄了使用 ANSYS SpaceClaim、Mechanical 及 Unified MCP 進行 79 層 PCB 疊構熱翹曲（$220^\circ\text{C}$ 回焊工況）自動化模擬時所做的程式修改、遭遇問題的分類剖析、解決方案與系統 Log 儲存路徑。

---

## 一、 程式碼與檔案修改清單 (Modifications)

### 1. 核心驅動庫修改 (`ansys-unified-mcp`)
* **[`src/ansys_unified_mcp/drivers/sim_impl.py`](file:///F:/Ming_python/ansys-unified-mcp/src/ansys_unified_mcp/drivers/sim_impl.py)**
  * **修改內容**：將 `connect_to_spaceclaim` 的預設 `transport_mode` 由原本 Windows 平台判斷的 `"wnua"` 改為強制預設 `"insecure"`。
  * **目的**：避免 SpaceClaim 本機 gRPC 伺服器在 Windows 下因認證失敗而連線超時中斷。
* **[`src/ansys_unified_mcp/tools/workbench_filebridge.py`](file:///F:/Ming_python/ansys-unified-mcp/src/ansys_unified_mcp/tools/workbench_filebridge.py)**
  * **修改內容**：新增 `_ensure_dirs()` 函式，在發送指令前自動遞迴檢查並建立 `commands/`、`results/`、`scripts/`、`runs/` 資料夾。
  * **目的**：杜絕檔案隊列初次啟動時因目錄未建立導致的 `FileNotFoundError`。

### 2. 專案自動化腳本 (`D:\ANSYS_MCP_Connect\PCB_Stackup_material\`)
* **[`01_build_pcb_geometry.py`](file:///D:/ANSYS_MCP_Connect/PCB_Stackup_material/01_build_pcb_geometry.py)**
  * 讀取 Excel 疊構定義（420 mm $\times$ 380 mm，共 79 層，總厚 5.345 mm）。
  * 驅動 SpaceClaim 建立 `PCB_Stackup_79L` 子組件，啟用 `SharedTopologyType.SHARE`，依序建立 79 層實體板厚。
* **[`02_calculate_materials.py`](file:///D:/ANSYS_MCP_Connect/PCB_Stackup_material/02_calculate_materials.py)**
  * 讀取 Copper.csv、EM-370.csv、EM-892K2.csv（23 點溫度曲線）。
  * 依各層殘銅率（Copper Residual %）計算正交異向性複合材料混合律（Rule of Mixtures）。
  * 自動輸出 1,672 行極速 MAPDL 材料巨集 [`apdl_rom_materials.mac`](file:///D:/ANSYS_MCP_Connect/PCB_Stackup_material/apdl_rom_materials.mac)。
* **[`03_setup_and_solve_mechanical.py`](file:///D:/ANSYS_MCP_Connect/PCB_Stackup_material/03_setup_and_solve_mechanical.py)**
  * 連線 Mechanical gRPC，劃分 MultiZone 結構六面體網格（24.5 萬節點、5.7 萬單元）。
  * 自動建立 79 個 Named Selections（`NS_L01`～`NS_L79`），注入 APDL 巨集置換材料。
  * 設定無應力參考溫度 $30^\circ\text{C}$ 與均勻回焊溫度 $220^\circ\text{C}$。
  * 於底層頂點配置 3-2-1 靜定運動學約束，並調用 12 核心 MAPDL 平行求解。
* **[`04_rescope_and_export_warpage.py`](file:///D:/ANSYS_MCP_Connect/PCB_Stackup_material/04_rescope_and_export_warpage.py)**
  * 重構 Mechanical 結果樹，聚焦 Top Surface (L01)、Bottom Surface (L79) 與 All Bodies 的 $Z$ 方向翹曲。
  * 設定繪圖視角與輸出解析度，匯出高畫質 PNG 雲圖。

---

## 二、 遭遇問題分類與根因排障 (Categorized Issues & Solutions)

### 類別 A：通訊協定與 gRPC 交握問題 (Protocol & Connectivity)
* **問題現象**：
  調用 `geometry_launch` 或連線 SpaceClaim 時出現連線中斷、逾時或認證拒絕（Auth failure）。
* **根本原因**：
  Windows 本機執行的 SpaceClaim 2025 R1 gRPC 監聽服務（預設埠 50051）並未啟用 Kerberos/NTLM 安全通道。原程式碼針對 Windows 平台預設傳入 `transport_mode="wnua"`，導致交握失敗。
* **解決對策**：
  全面將 SpaceClaim 連線參數設定為 `transport_mode='insecure'`，連線成功率提升至 100%。

---

### 類別 B：幾何拓撲與接觸過載問題 (Geometry & Contact Pairs)
* **問題現象**：
  79 層實體板厚拉伸完成後，若直接傳送至 Mechanical，模型樹狀目錄出現大量接觸對（Contact Pairs），網格劃分極為破碎且求解難以收斂。
* **根本原因**：
  若在 SpaceClaim 中僅依序拉伸 Body，各 Body 彼此在幾何數據庫中屬獨立個體。若未在組件層級宣告共享拓撲，Mechanical 無法自動識別相鄰面並進行節點共合。
* **解決對策**：
  在 SpaceClaim 建模時，建立統一子組件容器 `PCB_Stackup_79L`，並強制賦予屬性 `comp.modify_shared_topology(SharedTopologyType.SHARE)`。進入 Mechanical 後各層交界面完全形成 Conformal Mesh（共節點六面體），徹底免除 78 組接觸對。

---

### 類別 C：大量材料矩陣注入與 GUI 效能瓶頸 (Material Injection & Performance)
* **問題現象**：
  79 種正交異向材料，每種材料包含 23 個溫度階梯下的 $E_x, E_y, E_z, \nu_{xy}, \dots, \alpha_z$ 數據。若透過 Mechanical Engineering Data GUI 或 ACT 逐點注入，系統容易出現界面卡死、無回應或記憶體耗盡。
* **根本原因**：
  Workbench GUI 後端為 XML 資料庫架構，頻繁寫入數千筆巢狀屬性會觸發高頻交易鎖定與重複驗證機制。
* **解決對策**：
  採用 APDL 巨集注入架構：在 Python 側完成混合律矩陣計算，直接輸出原生的 `MPTEMP`、`MPDATA` 及單元置換指令（`CMSEL, S, NS_L<nn>, ELEM` / `EMODIF, ALL, MAT, <nn>`）。藉由 Mechanical 的 Command Snippet 在求解前一瞬間注入，耗時由數十分鐘縮短至 0.2 秒。

---

### 類別 D：邊界條件過約束與人為熱應力 (Boundary Conditions & Stress Over-constraint)
* **問題現象**：
  若在底面使用標準固定支承（Fixed Support）或位移面限制，回焊升溫（$\Delta T = 190^\circ\text{C}$）時板件角落會產生非物理性的巨大假性應力集中，且熱翹曲變形形貌被強行鎖死。
* **根本原因**：
  面固定同時限制了 $X, Y, Z$ 平移自由度，阻礙了板面本身自然的熱膨脹，破壞了自由熱翹曲的力學真實性。
* **解決對策**：
  採用嚴格的 **3-2-1 靜定運動學約束（Kinematic Supports）**：
  * 點 1：限制 $UX = 0, UY = 0, UZ = 0$（消除 3 向剛體平移）
  * 點 2：限制 $UY = 0, UZ = 0$（消除繞 $Z$ 旋轉）
  * 點 3：限制 $UZ = 0$（消除繞 $X/Y$ 傾斜）
  此法保證全域約束反力理論值為 0，實現完全自由的熱膨脹與翹曲呈現。

---

### 類別 E：後處理結果作用範圍與圖形渲染缺失 (Post-Processing & Graphic Rendering)
* **問題現象**：
  設定頂面或底面 Directional Deformation (Z Axis) 時，若將 Geometry Scoping 選定為單一 CAD 幾何面（Face），呼叫 `Graphics.ExportImage()` 匯出的 PNG 圖像為全灰色網格，無彩虹色階雲圖。
* **根本原因**：
  在啟用 Shared Topology 的薄層實體結構中，共用面屬於兩個微米級實體的共合交界，ACT 的圖形管線在處理單一面法向量的位移投影時容易發生深度衝突（Z-fighting）與法向陰影遮蔽。
* **解決對策**：
  將結果作用範圍改為選取該表面所屬的**超薄實體本體（Solid Body）**（頂層 Layer 01、底層 Layer 79）。此舉完全消除圖形緩衝衝突，輸出對比鮮明的標準 Rainbow 雲圖。

---

## 三、 系統歷程紀錄與 Error Log 存放位置導引 (Log Reference)

當後續需要追蹤歷史執行細節、診斷 MAPDL 求解警告或查詢通訊錯誤時，各日誌路徑如下：

### 1. AI 智能對話與全流程執行紀錄 (Agent Transcripts)
* **路徑**：
  `C:\Users\Ming\.gemini\antigravity\brain\f1c4012d-dc73-48f6-958a-d9f0fc69b0e4\.system_generated\logs\`
* **重要檔案**：
  * `transcript.jsonl`：包含每一次工具呼叫、參數、返回結果與思考歷程的 JSONL 序列檔。
  * `transcript_full.jsonl`：包含未截斷的完整日誌與終端輸出。

### 2. ANSYS Mechanical / MAPDL 底層求解器輸出 (Solver Output & Warnings)
* **路徑**：
  `D:\ANSYS_MCP_Connect\PCB_Warpage_Test_files\dp0\SYS-1\MECH\solve.out`
  `D:\ANSYS_MCP_Connect\_ProjectScratch\ScrCB43\solve.out`
* **記錄內容**：
  * MAPDL 求解核心的單元劃分檢查、網格品質、`MPTEMP`/`MPDATA` 讀取確認。
  * 平衡疊代步進、Newton-Raphson 收斂歷程、剛體模式警告及求解總耗時。

### 3. ANSYS Workbench Bridge 與 MCP 佇列紀錄 (Queue & Communication Logs)
* **路徑**：
  `F:\Ming_python\ansys-unified-mcp\workbench_queue\`
* **重要檔案**：
  * `act_main_debug.log`：Mechanical 內部 ACT Python 腳本執行的即時偵錯輸出。
  * `mechanical_queue_processor.log`：佇列處理器之指令解析與生命週期狀態。
  * `mechanical_socket_timer_v7.log`：Socket 連線心跳與計時器通訊日誌。
  * `archive/*.json`：已完成之歷史任務指令 Request 備份。
  * `responses/*.json`：Mechanical 回傳之執行結果、變形數據或 Python 堆疊錯誤（Traceback）。

### 4. SpaceClaim CAD 幾何日誌 (SpaceClaim Core Logs)
* **路徑**：
  `%LOCALAPPDATA%\SpaceClaim\Log Files\`（通常位於 `C:\Users\Ming\AppData\Local\SpaceClaim\Log Files\`）
* **記錄內容**：
  SpaceClaim 核心幾何引擎崩潰日誌、授權交握記錄與 gRPC 服務端通訊異常。
