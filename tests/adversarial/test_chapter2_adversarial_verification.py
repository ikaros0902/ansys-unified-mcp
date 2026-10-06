# -*- coding: utf-8 -*-
"""Adversarial verification test suite for Chapter 2 of Architecture & Specification Report."""

import ast
import os
import re
import sys
import subprocess
from pathlib import Path
import pytest

repo_root = Path(__file__).resolve().parent.parent.parent
src_root = repo_root / "src"
python_exe = sys.executable


class TestChapter2CodebaseFacts:
    """Adversarial verification of Chapter 2 cited facts."""

    def test_sim_tools_decorator_and_envelope(self):
        """1.1 驗證 fluent_tools.py 已確認為與 products/fluent/tools.py 逐行一致之重複死代碼並移除。

        原始斷言鎖定 tools/fluent_tools.py 存在且不含 @aliased_tool（對應白皮書第二章所述
        0% alias 覆蓋率事實）。2026-10-02 稽核確認該檔案與 products/fluent/tools.py 完全
        重複、且無任何模組或測試 import 它（__main__.py 僅載入 products/fluent/tools.py），
        故依 Phase 1 止血計畫刪除。本測試更新為驗證「重複檔案已不存在，且正本仍在原位」。
        """
        duplicate_path = src_root / "ansys_unified_mcp" / "tools" / "fluent_tools.py"
        canonical_path = src_root / "ansys_unified_mcp" / "products" / "fluent" / "tools.py"

        assert not duplicate_path.exists(), "tools/fluent_tools.py 應已被移除（確認為重複死代碼）"
        assert canonical_path.exists(), "products/fluent/tools.py（正本）必須存在"

        content = canonical_path.read_text(encoding="utf-8")
        assert "from ansys_unified_mcp.shared import" in content
        assert "as_envelope as _envelope" in content or "as_envelope" in content
        assert "@aliased_tool" not in content, "products/fluent/tools.py 不得含有 @aliased_tool（Fluent 工具不走別名機制）"

    def test_drop_test_glstat_generation(self):
        """1.2 驗證 drop_test.py 內部沙盒的虛擬 glstat 生成邏輯。"""
        file_path = src_root / "ansys_unified_mcp" / "workflows" / "drop_test.py"
        assert file_path.exists(), "drop_test.py 必須存在"
        content = file_path.read_text(encoding="utf-8")

        assert 'glstat_file = sandbox.workspace_dir / "glstat"' in content
        assert 'with open(glstat_file, "w", encoding="utf-8") as f:' in content
        assert "kinetic energy =" in content
        assert "internal energy =" in content
        assert "hourglass energy =" in content

    def test_icepak_driver_fake_csv(self, tmp_path: Path):
        """1.3 驗證 icepak_driver.py 徹底移除 85.4 硬編碼，且在無求解器且未授權 synthetic 時嚴格拒絕執行。"""
        from ansys_unified_mcp.drivers.icepak_driver import IcepakDriver
        from ansys_unified_mcp.drivers.base import SolverDriverError

        file_path = src_root / "ansys_unified_mcp" / "drivers" / "icepak_driver.py"
        assert file_path.exists(), "icepak_driver.py 必須存在"
        content = file_path.read_text(encoding="utf-8")

        assert "temperature_field.csv" in content
        assert "85.4" not in content, "icepak_driver.py 源碼中不得含有 85.4 硬編碼"

        driver = IcepakDriver(solver_bin=None)
        orig_avail = driver.is_available
        try:
            driver.is_available = lambda: False
            # 1. 未授權 allow_synthetic 時必須拋出 SolverDriverError 嚴格拒絕執行
            with pytest.raises(SolverDriverError):
                driver.prepare_job(tmp_path, {"ambient_temperature_c": 25.0, "chip_power_w": 50.0})

            # 2. 授權 allow_synthetic 時生成之檔案內容亦不得含有 85.4
            script_path = driver.prepare_job(
                tmp_path,
                {"ambient_temperature_c": 25.0, "chip_power_w": 50.0, "allow_synthetic": True},
            )
            script_content = script_path.read_text(encoding="utf-8")
            assert "85.4" not in script_content, "生成的腳本檔案中不得含有 85.4！"

            # 3. 提取產物並檢驗生成之 CSV 檔案中不得含有 85.4，且顯式標記 mock_reason
            results = driver.extract_artifacts(tmp_path)
            assert results.get("is_synthetic") is True
            assert results.get("mock_reason") == "NO_ICEPAK_SOLVER_DETECTED"
            csv_path = tmp_path / "workspace" / "temperature_field.csv"
            if csv_path.exists():
                csv_content = csv_path.read_text(encoding="utf-8")
                assert "85.4" not in csv_content, "生成的 CSV 數據中不得含有 85.4！"
        finally:
            driver.is_available = orig_avail

    def test_extapi_act_string_concatenation(self):
        """1.4 驗證 ExtAPI ACT 字串拼接在 products/mechanical/facade.py 與 products/mechanical/tools.py 中的存在。"""
        mech_prod = src_root / "ansys_unified_mcp" / "products" / "mechanical" / "facade.py"
        legacy_prod = src_root / "ansys_unified_mcp" / "products" / "mechanical.py"
        mech_wf = src_root / "ansys_unified_mcp" / "products" / "mechanical" / "tools.py"

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

    def test_prime_and_sherlock_zero_references_in_src(self):
        """2.1 驗證 src/ 目錄中 Prime 與 Sherlock 為 0 引用。"""
        prime_refs = []
        sherlock_refs = []

        for p in src_root.rglob("*.py"):
            text = p.read_text(encoding="utf-8", errors="ignore")
            if "ansys.meshing.prime" in text or "from ansys.meshing import prime" in text or "ansys-meshing-prime" in text:
                prime_refs.append(str(p))
            if "ansys.sherlock.core" in text or "import ansys.sherlock" in text or "ansys-sherlock-core" in text:
                sherlock_refs.append(str(p))

        assert len(prime_refs) == 0, f"src/ 中不得有 Prime 引用，發現: {prime_refs}"
        assert len(sherlock_refs) == 0, f"src/ 中不得有 Sherlock 引用，發現: {sherlock_refs}"

        # 檢驗 pyproject.toml
        pyproject = repo_root / "pyproject.toml"
        if pyproject.exists():
            py_text = pyproject.read_text(encoding="utf-8")
            assert "ansys-meshing-prime" not in py_text
            assert "ansys-sherlock-core" not in py_text

    def test_tool_count_136_ast_verification(self):
        """3.1 驗證 tools/*.py 與 products/*/tools.py 中 AST 定義之工具函數總數為 138 個。"""
        package_dir = src_root / "ansys_unified_mcp"
        tools_dir = package_dir / "tools"
        products_dir = package_dir / "products"
        tool_counts = {}
        unique_tools = {}

        # 掃描 tools/*.py 以及 products/*/tools.py（如 geometry 與 optislang 等產品工具）
        target_files = sorted(set(list(tools_dir.glob("*.py")) + list(products_dir.glob("*/tools.py"))))

        for p in target_files:
            if p.name in ("__init__.py", "connection_doctor.py"):
                continue
            tree = ast.parse(p.read_text(encoding="utf-8"))
            funcs = 0
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for dec in node.decorator_list:
                        dec_str = ast.unparse(dec)
                        if any(k in dec_str for k in ["aliased_tool", "mcp.tool", "tool_fluent", "tool_geometry"]):
                            funcs += 1
                            unique_tools[node.name] = str(p.relative_to(package_dir))
                            break
            rel_name = str(p.relative_to(package_dir))
            tool_counts[rel_name] = funcs

        total_funcs = len(unique_tools)
        # Chapter 2 基線 136 個工具 + R5 新增之 DPF 工具 (2 個) + Phase 3 新增之 session_manager (4 個) 與 geometry_list_named_selections (1 個) = 143 個
        assert total_funcs == 143, f"AST 解析工具總數應為 143，實測: {total_funcs} (各模組: {tool_counts})"

    def test_tool_count_102_mechanical_profile(self):
        """3.2 驗證 mechanical profile 動態路由下 FastMCP 暴露之工具總數。

        R4 工具面剪枝後，deprecated alias 預設不暴露：
        - ANSYS_MCP_EXPOSE_ALIASES=0（預設）：61 個 canonical 工具
          （57 基線 + 4 個跨產品統一 session 管理工具 ans_session_connect/
          launch/status/disconnect，無條件載入於所有 profile）。
        - ANSYS_MCP_EXPOSE_ALIASES=1（相容模式）：108 個（61 canonical + 47 alias）。
        """
        script = """
import os, asyncio
from ansys_unified_mcp.shared import mcp
import ansys_unified_mcp.__main__

async def main():
    tools = await mcp.list_tools()
    print(f"COUNT:{len(tools)}")

asyncio.run(main())
"""

        def _count(expose_aliases: str) -> int:
            env = os.environ.copy()
            env["ANSYS_MCP_PROFILE"] = "mechanical"
            env["ANSYS_MCP_EXPOSE_ALIASES"] = expose_aliases
            env.pop("ANSYS_MCP_PRUNE_ALIASES", None)
            env["PYTHONPATH"] = str(src_root)
            res = subprocess.run([python_exe, "-c", script], env=env, capture_output=True, text=True)
            assert res.returncode == 0, f"子行程異常結束: {res.stderr}"
            match = re.search(r"COUNT:(\d+)", res.stdout)
            assert match is not None, f"未能解析工具計數: {res.stdout}"
            return int(match.group(1))

        pruned_count = _count("0")
        assert pruned_count == 61, (
            f"R4 剪枝預設下 mechanical profile 工具總數應為 61 個 canonical"
            f"（57 基線 + 4 個 ans_session_* session 管理工具），實測: {pruned_count}"
        )

        exposed_count = _count("1")
        assert exposed_count == 108, (
            f"相容模式下 mechanical profile 工具總數應為 108（含 alias），實測: {exposed_count}"
        )

    def test_alias_coverage_distribution(self):
        """3.3 驗證各模組別名覆蓋率數據之真實性。

        2026-10-02 更新：原始斷言的 sim_tools.py（即 tools/fluent_tools.py）已確認為
        products/fluent/tools.py 的重複死代碼並移除，改以正本驗證同一事實（0% alias 覆蓋率）。
        2026-10-05 更新：tools/workbench_tools.py 與 tools/mechanical_tools.py 確認為
        products/workbench/tools.py 與 products/mechanical/tools.py 的完全重複死代碼並移除，
        斷言改指正本路徑。
        """
        # 依據報告 2.6.1：
        # mechanical.py (39), mechanical_workflows.py (3), optislang.py (5), intent_tools.py (5) 具備 100% aliased_tool
        # fluent（products/fluent/tools.py）與 workbench_filebridge.py 為 0%
        sim_file = src_root / "ansys_unified_mcp" / "products" / "fluent" / "tools.py"
        wb_file = src_root / "ansys_unified_mcp" / "products" / "workbench" / "tools.py"
        mech_file = src_root / "ansys_unified_mcp" / "products" / "mechanical" / "tools.py"

        sim_text = sim_file.read_text(encoding="utf-8")
        wb_text = wb_file.read_text(encoding="utf-8")
        mech_text = mech_file.read_text(encoding="utf-8")

        assert "@aliased_tool" not in sim_text
        assert wb_text.count("@aliased_tool") == 6
        assert mech_text.count("@aliased_tool") == 42
