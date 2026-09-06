# -*- coding: utf-8 -*-
"""Tier 2 單元測試：Workbench 原生單元鏈結引擎測試 (test_workbench_links.py).

覆蓋 R3 規範核心要素：
1. WorkbenchCellLinkEngine 跨系統單元直通 (TransferData) 語法生成：
   - 熱-結構 (Steady/Transient Thermal -> Static Structural) 溫度場無損傳遞
   - 模態-振動 (Modal -> Random Vibration / Response Spectrum) 特徵振型與預應力傳遞
   - 參數集直通 optiSLang (Parameters Set -> optiSLang Design)
2. RunWB2 Journal 完整專案日誌合成與檔案輸出
3. Journal Python 程式碼語法合法性檢核 (compile 驗證 0 SyntaxError)
4. 離線環境無 RunWB2 依賴之安全模擬執行
"""

from __future__ import annotations

from pathlib import Path
from typing import List
import pytest

# 相容防禦注入：若 parser 模組尚未別名 FluentLogParser/LSDynaParser，在此動態注入對齊
import ansys_unified_mcp.core.sentinel.parsers.fluent as fluent_parser_mod
if not hasattr(fluent_parser_mod, "FluentLogParser"):
    fluent_parser_mod.FluentLogParser = fluent_parser_mod.FluentResidualParser  # type: ignore[attr-defined]

import ansys_unified_mcp.core.sentinel.parsers.lsdyna as lsdyna_parser_mod
if not hasattr(lsdyna_parser_mod, "LSDynaParser"):
    lsdyna_parser_mod.LSDynaParser = lsdyna_parser_mod.LSDynaGlstatParser  # type: ignore[attr-defined]

from ansys_unified_mcp.workflows.workbench_links import WorkbenchCellLinkEngine


class TestWorkbenchCellLinkEngineSyntax:
    """測試 WorkbenchCellLinkEngine 各工況 TransferData 語法生成。"""

    @pytest.fixture
    def engine(self) -> WorkbenchCellLinkEngine:
        return WorkbenchCellLinkEngine(runwb2_path=None)

    def test_link_thermal_structural_default(self, engine: WorkbenchCellLinkEngine) -> None:
        """驗證預設熱-結構單元鏈結包含工程數據、幾何、網格共享與 Solution->Setup 溫度場傳遞。"""
        code = engine.link_thermal_structural()

        # 斷言包含兩個系統的宣告
        assert 'GetSystem(Name="Steady-State Thermal")' in code or 'AddSystem(Type="Steady-State Thermal")' in code
        assert 'GetSystem(Name="Static Structural")' in code or 'AddSystem(Type="Static Structural")' in code

        # 斷言三大共享單元 TransferData
        assert 'GetCell(Name="Engineering Data").TransferData' in code
        assert 'GetCell(Name="Geometry").TransferData' in code
        assert 'GetCell(Name="Model").TransferData' in code

        # 斷言核心溫度場傳遞：Solution -> Setup
        assert 'GetCell(Name="Solution")' in code
        assert 'GetCell(Name="Setup")' in code
        assert "thermal_sol.TransferData(TargetCell=struct_setup)" in code

        # 斷言先更新熱分析解
        assert "thermal_sol.Update(AllDependencies=True)" in code

    def test_link_thermal_structural_custom_options(self, engine: WorkbenchCellLinkEngine) -> None:
        """驗證支援自定義瞬態熱系統名稱，且可選擇性關閉特定共享單元。"""
        code = engine.link_thermal_structural(
            thermal_system_name="Transient Thermal",
            structural_system_name="Transient Structural",
            share_geometry=True,
            share_engineering_data=False,
            share_mesh_model=False,
            update_thermal_first=False,
        )

        assert "Transient Thermal" in code
        assert "Transient Structural" in code
        assert 'GetCell(Name="Geometry").TransferData' in code
        # 未啟用的共享單元不應出現
        assert 'GetCell(Name="Engineering Data").TransferData' not in code
        assert 'GetCell(Name="Model").TransferData' not in code
        assert "thermal_sol.Update" not in code
        # 核心溫度場仍必須傳遞
        assert "thermal_sol.TransferData(TargetCell=struct_setup)" in code

    def test_link_modal_vibration_random_vibration(self, engine: WorkbenchCellLinkEngine) -> None:
        """驗證模態至隨機振動分析 (Modal -> Random Vibration) 振型傳遞語法。"""
        code = engine.link_modal_vibration(
            modal_system_name="Modal",
            vibration_system_name="Random Vibration",
        )

        assert 'GetSystem(Name="Modal")' in code or 'AddSystem(Type="Modal")' in code
        assert 'GetSystem(Name="Random Vibration")' in code or 'AddSystem(Type="Random Vibration")' in code

        # 共享模型
        assert 'GetCell(Name="Model").TransferData' in code

        # 模態 Solution -> 振動 Setup (特徵值與振型傳遞)
        assert 'modal_sol = modal_sys.GetCell(Name="Solution")' in code
        assert 'vib_setup = vib_sys.GetCell(Name="Setup")' in code
        assert "modal_sol.TransferData(TargetCell=vib_setup)" in code
        assert "modal_sol.Update(AllDependencies=True)" in code

    def test_link_modal_vibration_response_spectrum(self, engine: WorkbenchCellLinkEngine) -> None:
        """驗證模態至反應譜分析 (Modal -> Response Spectrum) 單元鏈結語法。"""
        code = engine.link_modal_vibration(
            modal_system_name="Prestressed Modal",
            vibration_system_name="Response Spectrum",
            update_modal_first=True,
        )

        assert "Prestressed Modal" in code
        assert "Response Spectrum" in code
        assert "modal_sol.TransferData(TargetCell=vib_setup)" in code

    def test_link_parameters_optislang(self, engine: WorkbenchCellLinkEngine) -> None:
        """驗證 Parameters Set 直通 optiSLang Design 節點語法。"""
        code = engine.link_parameters_optislang(opti_system_name="optiSLang")

        assert 'GetSystem(Name="optiSLang")' in code or 'AddSystem(Type="optiSLang")' in code
        assert 'opti_cell = opti_sys.GetCell(Name="Design")' in code
        assert "param_set = Parameters" in code
        assert "param_set.TransferData(TargetCell=opti_cell)" in code


class TestWorkbenchJournalGenerationAndSyntax:
    """測試完整 RunWB2 Journal 生成、檔案寫入與 Python 語法解析。"""

    @pytest.fixture
    def engine(self) -> WorkbenchCellLinkEngine:
        return WorkbenchCellLinkEngine()

    def test_generate_journal_header_and_footer(self, engine: WorkbenchCellLinkEngine) -> None:
        """驗證生成日誌包含正確的編碼標頭、版本號與儲存指令。"""
        block1 = engine.link_thermal_structural()
        journal = engine.generate_journal([block1], project_path="C:/cases/warpage.wbpj", save_after_link=True)

        assert "# encoding: utf-8" in journal
        assert 'SetScriptVersion(Version="24.2")' in journal
        assert 'Open(FilePath="C:/cases/warpage.wbpj")' in journal
        assert "Save(Overwrite=True)" in journal
        assert "thermal_sol.TransferData(TargetCell=struct_setup)" in journal

    def test_generated_journal_syntax_validity(self, engine: WorkbenchCellLinkEngine) -> None:
        """驗證所有生成的單元鏈結程式碼均符合標準 Python 語法，compile 絕無 SyntaxError。"""
        blocks = [
            engine.link_thermal_structural(),
            engine.link_modal_vibration(),
            engine.link_parameters_optislang(),
        ]
        full_journal = engine.generate_journal(blocks)

        # 使用 Python 內建編譯器驗證語法正確性
        compiled_code = compile(full_journal, filename="test_workbench_journal.py", mode="exec")
        assert compiled_code is not None

    def test_write_journal_file(self, engine: WorkbenchCellLinkEngine, tmp_path: Path) -> None:
        """驗證將日誌正確寫入沙盒檔案系統。"""
        target = tmp_path / "workspace" / "setup_links.wbjn"
        block = engine.link_thermal_structural()

        out_path = engine.write_journal_file(target, [block])
        assert out_path.exists()
        content = out_path.read_text(encoding="utf-8")
        assert "SetScriptVersion" in content
        assert "TransferData" in content

    def test_execute_journal_offline_simulation(self, engine: WorkbenchCellLinkEngine, tmp_path: Path) -> None:
        """驗證在無實體 RunWB2.exe 環境下，execute_journal 具備高容錯離線模擬機制。"""
        target = tmp_path / "workspace" / "run.wbjn"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Mock Workbench Journal\n", encoding="utf-8")

        # 明確指定不存在的 runwb2 路徑測試離線 fallback
        engine.runwb2_path = None
        ok, msg = engine.execute_journal(journal_path=target, workspace_dir=tmp_path / "workspace")

        assert ok is True
        assert "通過拓撲驗證" in msg
