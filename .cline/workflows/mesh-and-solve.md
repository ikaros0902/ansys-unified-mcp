# 網格劃分與結構求解工作流程

標準 CAE 自動化步驟：
1. 確保已連接或啟動 Mechanical（調用 `launch_mechanical` 或 `connect_to_mechanical`）。
2. 調用 `set_mesh_element_size` 設定網格尺寸並執行 `generate_mesh`。
3. 調用 `get_mesh_statistics` 輸出網格節點與單元數以客觀驗證網格品質。
4. 檢查邊界條件，調用 `solve_analysis` 進行求解。
5. 調用 `get_solve_status` 確認收斂，並讀取變形與等效应力結果。
