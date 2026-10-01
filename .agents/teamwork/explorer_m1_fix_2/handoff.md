# Handoff Report — test_chapter2 舊檔斷言殘留與 CLI 執行錯誤修復策略調研

- **Agent**: `explorer_m1_fix_2` (teamwork_preview_explorer)
- **Handoff Type**: Hard (調研完成，提供完備落地策略與 Patch)
- **Recipient**: `b64f9ba5-0d28-4ac0-a95d-862e7b398eaf` (parent)
- **Target Task**: 探查與制定 test_chapter2 舊檔斷言殘留及 test_final_stress_harness CLI 執行錯誤的修復策略

---

## 1. Observation (觀察事實)

### 1.1 `test_chapter2_adversarial_verification.py` 舊檔斷言上下文與報錯事實
- **檔案路徑**：`tests/adversarial/test_chapter2_adversarial_verification.py`
- **受測函數與行號**：行 84–98，`TestChapter2CodebaseFacts.test_extapi_act_string_concatenation`
- **原始代碼**：
  ```python
  84:     def test_extapi_act_string_concatenation(self):
  85:         """1.4 驗證 ExtAPI ACT 字串拼接在 products/mechanical.py 與 tools/mechanical_workflows.py 中的存在。"""
  86:         mech_prod = src_root / "ansys_unified_mcp" / "products" / "mechanical.py"
  87:         mech_wf = src_root / "ansys_unified_mcp" / "tools" / "mechanical_workflow_tools.py"
  88:         assert mech_prod.exists() and mech_wf.exists()
  89: 
  90:         content_prod = mech_prod.read_text(encoding="utf-8")
  91:         assert "ExtAPI.DataModel.Project.Model" in content_prod
  92:         assert "mech.connect_to_mechanical" in content_prod
  93:         assert "mech.launch_mechanical" in content_prod
  94: 
  95:         content_wf = mech_wf.read_text(encoding="utf-8")
  96:         assert 'script = f"""' in content_wf
  97:         assert "model = ExtAPI.DataModel.Project.Model" in content_wf
  ```
- **執行測試實測**：
  - 執行指令：`.venv\Scripts\pytest.exe tests/adversarial/test_chapter2_adversarial_verification.py::TestChapter2CodebaseFacts::test_extapi_act_string_concatenation`
  - 報錯結果：
    ```text
    FAILED tests/adversarial/test_chapter2_adversarial_verification.py::TestChapter2CodebaseFacts::test_extapi_act_string_concatenation - AssertionError: assert (False)
     +  where False = exists()
     +    where exists = WindowsPath('F:/Ming_python/ansys-unified-mcp/src/ansys_unified_mcp/products/mechanical.py').exists
    ```
- **新架構對應檔案狀態**：
  - 實測指令：`.venv\Scripts\python.exe -c "from pathlib import Path; print(Path('src/ansys_unified_mcp/products/mechanical/facade.py').exists())"`
  - 輸出結果：`True`
  - 在 `src/ansys_unified_mcp/products/mechanical/facade.py` 中，行 100 含有 `mech.connect_to_mechanical`、行 106 含有 `"model = ExtAPI.DataModel.Project.Model\n"`、行 121 含有 `mech.launch_mechanical`。

### 1.2 `test_final_stress_harness.py` 直接以 CLI 執行報錯事實
- **檔案路徑**：`tests/adversarial/test_final_stress_harness.py`
- **執行指令**：`.venv\Scripts\python.exe tests/adversarial/test_final_stress_harness.py`
- **終端輸出**：
  - 5 項實證檢驗（14 個工具入口極限壓力、夾心日誌攔截、無 ok 鍵字典信封標準化、布林型別轉換、全量 78 個工具審計）**全部列印 `[PASS]`**。
  - 末尾卻輸出：
    ```text
    =================================================================
      【挑戰結論】實證測試發現破口！存在假陽性或型別錯誤！              
      判定結果: DISPROVED                                            
    =================================================================
    ```
  - 進程退出代碼：`1`。
- **代碼行號觀察**：
  - 該測試入口 `main()`（行 331–354）：
    ```python
    336:     success1 = test_section_1_fourteen_tools_stress()
    337:     success2 = test_section_2_safe_json_sandwich_logs()
    338:     success3 = test_section_3_missing_ok_dict()
    339:     success4 = test_section_4_strict_boolean_type()
    340:     success5 = test_section_5_all_78_tools_complete_audit()
    341: 
    342:     if success1 and success2 and success3 and success4 and success5:
    ...
    347:         return 0
    348:     else:
    ...
    353:         return 1
    ```
  - 但檢視 `test_section_1`（行 58–139）、`test_section_2`（行 142–199）、`test_section_3`（行 201–235）、`test_section_4`（行 237–281）、`test_section_5`（行 283–329），所有 5 個測試函數在執行完畢後**均沒有寫 `return True`**。

### 1.3 全專案 `products/mechanical.py` 實體檔案斷言掃描結果
- **搜尋範圍**：全庫 `tests/` 與 `src/`。
- **正面斷言（assert exists）**：全專案僅有 `tests/adversarial/test_chapter2_adversarial_verification.py:88` 一處。
- **負面防禦斷言（assert not exists）**：`tests/adversarial/test_m1_facade_adversarial_challenge.py:43`：
  ```python
  legacy_file = PROJECT_ROOT / "src" / "ansys_unified_mcp" / "products" / "mechanical.py"
  assert not legacy_file.exists(), f"Legacy file still exists: {legacy_file}"
  ```
  此處為符合重構規範的正確負面防禦斷言。
- **文檔或註解提及**：如 `agents/contexts/context.md`、`docs/architecture/`、`test_mechanical_controller.py:1`（docstring）、`test_sessions.py:3`（docstring），僅為文字備註，無任何可執行斷言。

---

## 2. Logic Chain (推導邏輯鏈)

1. **從觀察 1.1 推導出斷言失敗原因與架構演進衝突**：
   - `test_chapter2_adversarial_verification.py` 撰寫於 Chapter 2 報告審核階段，其設計初衷是驗證報告中提及的「歷史事實」（即 codebase 內手動字串拼接 ACT 腳本之特徵）。
   - 在 Milestone 1 (R1) 中，重構核心任務明確要求「物理刪除舊版 `src/ansys_unified_mcp/products/mechanical.py`，消除代碼重複，並統一由 `products/mechanical/facade.py` 接管 Mechanical 控制」。
   - 當實作者執行物理刪除後，舊檔 `mechanical.py` 已不復存在；但該測試仍保留 `assert mech_prod.exists()`，造成「重構目標要求舊檔不存在，而舊測試卻要求舊檔必須存在」的邏輯矛盾。
2. **推導最佳測試調整方案**：
   - 若將斷言標的改為重構後的 `src/ansys_unified_mcp/products/mechanical/facade.py`，並確認原先檢查的 ExtAPI 拼接特徵（`ExtAPI.DataModel.Project.Model`、`mech.connect_to_mechanical`、`mech.launch_mechanical`）在 `facade.py` 內均完好無損，即可完全延續 Chapter 2 的事實審計目的。
   - 更進一步，在測試中加入對舊版 `products/mechanical.py` 的負面斷言（`assert not legacy_prod.exists()`），能與 `test_m1_facade_adversarial_challenge.py` 形成雙重鎖定，確保未來不會意外復辟舊檔案。
3. **從觀察 1.2 推導出 CLI 執行失敗原因**：
   - 在 Python 中，函數若無顯式 `return` 語句，預設返回 `None`。
   - `test_final_stress_harness.py` 的各 section 函數均以 `assert` 作為校驗手段，未定義返回值。
   - 當由 pytest 運行時，pytest 僅檢測有無拋出例外，因此返回 `None` 不影響 pytest 判定為 PASSED；
   - 但直接以 CLI 執行 `python test_final_stress_harness.py` 時，`main()` 透過 `if success1 and success2 ...` 判定整體是否通過。因所有函數回傳 `None`（falsy），布林評估結果必定為 `False`，觸發 `else` 分支印出 `DISPROVED` 並拋出 exit code 1。
   - 因此，在各 section 函數末尾顯式補上 `return True`，即可徹底解決 CLI 執行報錯。

---

## 3. Caveats (限制與注意事項)

1. **唯讀探查原則**：本 Explorer 嚴格遵循唯讀探查規範，未對 `tests/adversarial/` 下之原始碼進行直接修改。所有修正方案均以標準 `.patch` 形式存放於工作目錄，供 Worker 實作落地。
2. **歷史債務 `test_tool_count_136_ast_verification`**：
   - 在 `test_chapter2_adversarial_verification.py` 中，另有一項 `test_tool_count_136_ast_verification` 失敗（預期 138，實測 121），此為歷史架構切片導致的工具計數變更，Reviewer 已明確標註為累積歷史債務，不屬於本次 Milestone 1 的變更範疇。

---

## 4. Conclusion (結論與行動建議)

### 結論總結
1. `test_chapter2_adversarial_verification.py:86` 之斷言失敗源於舊檔物理刪除與歷史測試斷言的標的脫節，應將斷言標的更新為 `products/mechanical/facade.py`，並增補舊檔消除斷言。
2. `test_final_stress_harness.py` 在 CLI 下報錯非業務邏輯缺陷，純粹為 5 個測試函數結尾漏寫 `return True` 導致 `main()` 判定失敗，補上 `return True` 即可全綠燈通過。
3. 全專案無其他測試或代碼正面斷言舊版 `products/mechanical.py` 存在。

---

### Worker 直接落地指引 (Actionable Patch Specification)

#### 修改 1：`tests/adversarial/test_chapter2_adversarial_verification.py`
- **目標位置**：行 84–98
- **具體代碼調整**：
```python
<<<<< BEFORE
    def test_extapi_act_string_concatenation(self):
        """1.4 驗證 ExtAPI ACT 字串拼接在 products/mechanical.py 與 tools/mechanical_workflows.py 中的存在。"""
        mech_prod = src_root / "ansys_unified_mcp" / "products" / "mechanical.py"
        mech_wf = src_root / "ansys_unified_mcp" / "tools" / "mechanical_workflow_tools.py"
        assert mech_prod.exists() and mech_wf.exists()

        content_prod = mech_prod.read_text(encoding="utf-8")
        assert "ExtAPI.DataModel.Project.Model" in content_prod
        assert "mech.connect_to_mechanical" in content_prod
        assert "mech.launch_mechanical" in content_prod

        content_wf = mech_wf.read_text(encoding="utf-8")
        assert 'script = f"""' in content_wf
        assert "model = ExtAPI.DataModel.Project.Model" in content_wf
=====
    def test_extapi_act_string_concatenation(self):
        """1.4 驗證 ExtAPI ACT 字串拼接在 products/mechanical/facade.py 與 tools/mechanical_workflows.py 中的存在。"""
        mech_prod = src_root / "ansys_unified_mcp" / "products" / "mechanical" / "facade.py"
        legacy_prod = src_root / "ansys_unified_mcp" / "products" / "mechanical.py"
        mech_wf = src_root / "ansys_unified_mcp" / "tools" / "mechanical_workflow_tools.py"

        # 驗證舊版單一檔案已被物理移除，且重構後的 Facade 與工作流檔案均存在
        assert not legacy_prod.exists(), f"舊版 products/mechanical.py 必須已被消除: {legacy_prod}"
        assert mech_prod.exists() and mech_wf.exists()

        content_prod = mech_prod.read_text(encoding="utf-8")
        assert "ExtAPI.DataModel.Project.Model" in content_prod
        assert "mech.connect_to_mechanical" in content_prod
        assert "mech.launch_mechanical" in content_prod

        content_wf = mech_wf.read_text(encoding="utf-8")
        assert 'script = f"""' in content_wf
        assert "model = ExtAPI.DataModel.Project.Model" in content_wf
>>>>> AFTER
```
*(對應 patch 檔案已存放於 `.agents/teamwork/explorer_m1_fix_2/patch_test_chapter2.patch`)*

#### 修改 2：`tests/adversarial/test_final_stress_harness.py`
- **目標位置**：各 section 函數末尾
- **具體代碼調整**：
  1. 行 139（`test_section_1_fourteen_tools_stress` 結尾）：
     ```python
         assert total_false_positives == 0, f"存在假陽性，總數: {total_false_positives}"
     +   return True
     ```
  2. 行 199（`test_section_2_safe_json_sandwich_logs` 結尾）：
     ```python
         assert all_passed, "夾心日誌測試存在未攔截的失敗！"
     +   return True
     ```
  3. 行 235（`test_section_3_missing_ok_dict` 結尾）：
     ```python
         assert all_passed, "字典信封標準化測試失敗！"
     +   return True
     ```
  4. 行 281（`test_section_4_strict_boolean_type` 結尾）：
     ```python
         assert all_passed, "布林型別轉換未達成嚴格 bool 保證！"
     +   return True
     ```
  5. 行 329（`test_section_5_all_78_tools_complete_audit` 結尾）：
     ```python
         print(f"[PASS] 全量 {c_empty} 個工具在空字串與 HTML 502 下假陽性數量 100% 歸零！")
     +   return True
     ```
*(對應 patch 檔案已存放於 `.agents/teamwork/explorer_m1_fix_2/patch_test_final_stress.patch`)*

---

## 5. Verification Method (獨立驗證方式)

實作者落地修改後，可執行以下指令進行精準驗證：

1. **驗證 `test_chapter2_adversarial_verification.py` 舊檔與 Facade 斷言通過**：
   ```powershell
   .venv\Scripts\pytest.exe tests/adversarial/test_chapter2_adversarial_verification.py::TestChapter2CodebaseFacts::test_extapi_act_string_concatenation -v
   ```
   *預期結果*：`PASSED`（Exit code: 0）。

2. **驗證 `test_final_stress_harness.py` CLI 直接執行通過**：
   ```powershell
   .venv\Scripts\python.exe tests/adversarial/test_final_stress_harness.py
   ```
   *預期結果*：
   終端輸出：
   ```text
   =================================================================
     【挑戰結論】實證測試全部通過！零假陽性，強型別信封保證確認！      
     判定結果: CONFIRMED                                            
   =================================================================
   ```
   進程返回代碼為 `0`（`$LASTEXITCODE` 等於 0）。

3. **驗證全套 adversarial 測試執行狀況**：
   ```powershell
   .venv\Scripts\pytest.exe tests/adversarial/test_final_stress_harness.py tests/adversarial/test_m1_facade_adversarial_challenge.py tests/adversarial/test_m1_alias_challenge.py tests/adversarial/test_m1_envelope_stress_challenge.py -v
   ```
   *預期結果*：所有測試 100% 通過。
