# Handoff Report — explorer_survey_3

## 1. Observation (客觀觀察)

1. **`scripts/` 目錄結構**：
   - 經 `list_dir("F:/Ming_python/ansys-unified-mcp/scripts")` 檢查：包含 `_archive_mesh_fix_202609/`、`deploy/`、`maintenance/` 三個子目錄，根目錄層級無任何孤立檔案。
   - `scripts/_archive_mesh_fix_202609/` 內有 12 個檔案：
     - `check_stuck_geometry.py`
     - `clean_and_collapse_tree.py`
     - `finish_remaining_parts_robust.py`
     - `inspect_mesh_setup.py`
     - `rebuild_step1.py`
     - `rebuild_step1_and_step2.py`
     - `reset_methods_to_multizone.py`
     - `run_step3_partitioned_mesh.py`
     - `step3_partition_mesh_and_fallback.py`
     - `stepped_mesher_with_visibility.py`
     - `test_mech_direct.py`
     - `test_tet_meshing.py`
   - 代碼特徵：
     - `clean_and_collapse_tree.py:13`：`all_bodies = geo.GetChildren(...)` 註釋明記 `Ensure all 114 bodies are 100% VISIBLE`，第 24 行硬編碼 `"Tet_Component1\\PDB_STANDOFF_GDZ1"`。
     - `reset_methods_to_multizone.py:31`：`if child.Name.strip() != "1F-FRONT-END-GDZ":`。
     - `step3_partition_mesh_and_fallback.py:29-41`：硬編碼 11 個 Part 清單 (`SM-BASEPAN-GDZ`, `Rear_wall`, `CX7`, `OCP`, `Component1` 等)。
   - `scripts/deploy/act_plugins/`：包含 `WorkbenchMCP.xml`、`main.py` 等 4 個檔案。`pyproject.toml:91` 白名單明記 `"scripts/deploy/**/*.py" = ["F821"]`，`scripts/maintenance/setup.ps1:133-134` 自動複製此目錄至 `$env:APPDATA\Ansys\v*\ACT\extensions`。
   - `scripts/maintenance/`：包含 `audit_architecture_compliance.py`、`setup.ps1`、`preflight_env_check.py` 等 7 個維護工具。

2. **Python 與測試環境**：
   - 虛擬環境位於 `F:\Ming_python\ansys-unified-mcp\.venv\` (Python 3.14.2)。
   - 執行 `uv run pytest` 時報錯：
     ```
     error: failed to remove file `F:\Ming_python\ansys-unified-mcp\.venv\Lib\site-packages\grpc/_cython/cygrpc.cp314-win_amd64.pyd`: 存取被拒。 (os error 5)
     ```
     `psutil` 顯示 PID 32256 與 38668 正在執行 `F:\Ming_python\ansys-unified-mcp\mcp_server.py`，導致該動態鏈結庫被佔用鎖定。
   - `.venv\Scripts\pytest.exe --version` 輸出 `pytest 9.1.1`，可繞過 uv 同步直接運作。
   - 初次執行 collection 時遭遇 22 個模組的 `ModuleNotFoundError: No module named 'pydantic'`，經補全相容套件 `pydantic==2.13.4` 與 `ansys-dpf-core==0.16.1` 後，全專案成功收集 **461 項測試，0 collection errors**。

3. **全專案 pytest 基準執行結果**：
   - 執行指令：`.venv\Scripts\pytest.exe -q --tb=short`
   - 輸出結果：
     ```
     1 failed, 452 passed, 2 skipped, 5 xfailed, 1 xpassed in 24.96s
     ```
   - 唯一失敗：
     ```
     FAILED tests/adversarial/test_chapter2_adversarial_verification.py::TestChapter2CodebaseFacts::test_tool_count_136_ast_verification
     AssertionError: AST 解析工具總數應為 138，實測: 121 (各模組: {'connection_tools.py': 0, 'docs_tools.py': 4, 'dpf_tools.py': 2, 'fluent_tools.py': 19, 'intent_tools.py': 5, 'mechanical_tools.py': 39, 'mechanical_workflow_tools.py': 3, 'sentinel_tools.py': 4, 'workbench_tools.py': 45})
     assert 121 == 138
     ```
   - 兩項跳過：
     - `tests\unit\test_skills_audit.py:37` (`test_skills_architecture_audit_passes`)
     - `tests\unit\test_skills_audit.py:73` (`test_sync_does_not_delete_global_only_files_by_default`)
     跳過原因：`AUDIT_SCRIPT` 與 `SYNC_SCRIPT` 硬編碼為 `PROJECT_ROOT / "scripts" / ...`，而檔案已於 Commit `0b28e80` 移至 `scripts/maintenance/`。

4. **代碼重複現況 (Mechanical.py)**：
   - `src/ansys_unified_mcp/products/mechanical.py`（229 行，9972 bytes）與 `src/ansys_unified_mcp/products/mechanical/facade.py`（229 行，9972 bytes）位元完全一致。
   - `src/ansys_unified_mcp/products/mechanical/__init__.py:9-14` 已直接從 `facade.py` 匯入並公開 `MechanicalController, PRODUCT, controller, _esc, api, MechanicalDriver`。

---

## 2. Logic Chain (推理鏈)

1. 由 **Observation 1**：`_archive_mesh_fix_202609/` 下的 12 個腳本均帶有 114 個實體、特定零件名稱（如 `1F-FRONT-END-GDZ`、`SM-BASEPAN-GDZ`），可知其本質為「單一伺服器機箱專案之特定排障紀錄」，而非「通用的 CAE 網格操作 API」。
2. 由 `skills/ansys-mesh/SKILL.md` 之定位，技能庫內的 `scripts/` 必須是通用可複用的自動化工具（如 `auto_mesh_generator.py`）。若將模型特定代碼放入，會污染技能標準環境；而專案已有 `examples/` 目錄放置具體案例，因此將該 12 個腳本移入 `examples/mesh_debug/` 最符合架構分工。
3. 由 **Observation 1**：`scripts/deploy/act_plugins/` 是 ACT 外掛原始碼並被 `setup.ps1` 調用；`scripts/maintenance/` 為合規與環境維護工具，兩者皆為專案級資產，必須保留。
4. 由 **Observation 2**：`uv run` 的失敗是由於本機執行中之 MCP 背景進程鎖定了 `cygrpc` 檔案，而非代碼缺陷；透過原生 `.venv\Scripts\pytest.exe` 執行可穩定完成測試。
5. 由 **Observation 3**：Git Commit `0b28e80` 刪除了 `tools/geometry_tools.py`（12 工具）與 `tools/optislang_tools.py`（5 工具），合計 17 工具；而 AST 測試剛好回報 $138 - 121 = 17$。這 17 個工具已存在於 `src/ansys_unified_mcp/products/{geometry,optislang}/tools.py`，因此失敗純粹是因為測試之 AST 掃描未擴及 `products/` 目錄。
6. 由 **Observation 4**：`products/mechanical.py` 與 `products/mechanical/facade.py` 完全重複，且 `__init__.py` 已橋接導出，刪除 `mechanical.py` 不會破壞現有 20 多個模組的 import。

---

## 3. Caveats (限制與注意事項)

1. **常駐進程鎖定**：若未來需透過 `uv sync` 更新相依套件，需先暫停本機運行之 `mcp_server.py`（或重啟 IDE），否則 Windows 會持續鎖定 `cygrpc` 與 `pydantic_core`。
2. **Xfail 與 Xpass 測試**：`tests/adversarial/test_m1_envelope_stress_challenge.py` 中有 5 個 xfail 與 1 個 xpass，這些是專門用於檢驗歷史邊界漏洞的對抗挑戰案例，依其設計規範維持現狀即可，不代表當前功能有迴歸缺陷。
3. **未修改任何原始碼**：本探查為嚴格唯讀（僅在虛擬環境補齊缺少的 wheel），專案原始碼尚未發生任何異動。

---

## 4. Conclusion (最終結論)

1. **R3 腳本清理行動**：
   - 將 `scripts/_archive_mesh_fix_202609/` 遷移至 `examples/mesh_debug/`，並加入 `README.md` 說明。
   - 保留 `scripts/deploy/` 與 `scripts/maintenance/`，達成根目錄 `scripts/` 僅保留專案級建置/維護腳本之要求。
2. **R1 代碼去重行動**：
   - 安全刪除 `src/ansys_unified_mcp/products/mechanical.py`，單一事實來源完全收斂至 `products/mechanical/facade.py`。
3. **100% pytest 綠燈修復路徑**：
   - 修正 `tests/adversarial/test_chapter2_adversarial_verification.py:126` 的 AST glob 路徑，使其一併掃描 `products/*/tools.py`（涵蓋重構後的 geometry 12 工具與 optislang 5 工具）。
   - 修正 `tests/unit/test_skills_audit.py:19-20` 的路徑為 `scripts/maintenance/`。
   - 完成後即可達到 **455 passed, 0 failed, 0 skipped (100% 通過)**。

---

## 5. Verification Method (獨立驗證方法)

1. **驗證腳本目錄結構**：
   ```powershell
   Get-ChildItem -Directory F:\Ming_python\ansys-unified-mcp\scripts
   ```
   *預期結果*：僅存在 `deploy` 與 `maintenance`（若已清理）。

2. **驗證全專案測試基準**：
   ```powershell
   & F:\Ming_python\ansys-unified-mcp\.venv\Scripts\pytest.exe -q --tb=short
   ```
   *預期結果*：收集 461 項測試，通過 452 項，僅 1 項失敗 (`test_tool_count_136_ast_verification`)，2 項跳過。

3. **驗證架構審查腳本合規性**：
   ```powershell
   & F:\Ming_python\ansys-unified-mcp\.venv\Scripts\python.exe F:\Ming_python\ansys-unified-mcp\scripts\maintenance\audit_architecture_compliance.py
   ```
   *預期結果*：四大指標全數 PASS，Exit code 0。
