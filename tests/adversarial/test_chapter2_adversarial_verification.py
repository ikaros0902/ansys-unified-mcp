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
        """1.1 驗證 sim_tools.py 的自製裝飾器與 shared._envelope 使用。"""
        file_path = src_root / "ansys_unified_mcp" / "tools" / "sim_tools.py"
        assert file_path.exists(), "sim_tools.py 必須存在"
        content = file_path.read_text(encoding="utf-8")

        # 驗證已從 shared 匯入 _envelope，而非定義本地版本
        assert "from ansys_unified_mcp.shared import" in content
        assert "as_envelope as _envelope" in content or "as_envelope" in content
        assert "def tool_geometry(" in content
        assert "def tool_fluent(" in content
        assert "@aliased_tool" not in content, "sim_tools.py 不得含有 @aliased_tool (證實報告所指未採用別名裝飾器)"

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
        """1.4 驗證 ExtAPI ACT 字串拼接在 products/mechanical.py 與 tools/mechanical_workflows.py 中的存在。"""
        mech_prod = src_root / "ansys_unified_mcp" / "products" / "mechanical.py"
        mech_wf = src_root / "ansys_unified_mcp" / "tools" / "mechanical_workflows.py"
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
        """3.1 驗證 tools/*.py 中 AST 定義之工具函數總數為 136 個。"""
        tools_dir = src_root / "ansys_unified_mcp" / "tools"
        tool_counts = {}

        for p in sorted(tools_dir.glob("*.py")):
            if p.name == "__init__.py" or p.name == "connection_doctor.py":
                continue
            tree = ast.parse(p.read_text(encoding="utf-8"))
            funcs = 0
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for dec in node.decorator_list:
                        dec_str = ast.unparse(dec)
                        if any(k in dec_str for k in ["aliased_tool", "mcp.tool", "tool_fluent", "tool_geometry"]):
                            funcs += 1
                            break
            tool_counts[p.name] = funcs

        total_funcs = sum(tool_counts.values())
        # Chapter 2 基線 136 個工具 + R5 新增之 DPF 工具 (2 個: dpf_extract_structural_results, dpf_get_model_summary)
        assert total_funcs == 138, f"AST 解析工具總數應為 138，實測: {total_funcs} (各模組: {tool_counts})"

    def test_tool_count_102_mechanical_profile(self):
        """3.2 驗證 mechanical profile 動態路由下 FastMCP 暴露之工具總數。

        R4 工具面剪枝後，deprecated alias 預設不暴露：
        - ANSYS_MCP_EXPOSE_ALIASES=0（預設）：57 個 canonical 工具。
        - ANSYS_MCP_EXPOSE_ALIASES=1（相容模式）：104 個（57 canonical + 47 alias）。
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
        assert pruned_count == 57, (
            f"R4 剪枝預設下 mechanical profile 工具總數應為 57 個 canonical，實測: {pruned_count}"
        )

        exposed_count = _count("1")
        assert exposed_count == 104, (
            f"相容模式下 mechanical profile 工具總數應為 104（含 alias），實測: {exposed_count}"
        )

    def test_alias_coverage_distribution(self):
        """3.3 驗證各模組別名覆蓋率數據之真實性。"""
        # 依據報告 2.6.1：
        # mechanical.py (39), mechanical_workflows.py (3), optislang.py (5), intent_tools.py (5) 具備 100% aliased_tool
        # sim_tools.py (31) 與 workbench_filebridge.py (31) 為 0%
        sim_file = src_root / "ansys_unified_mcp" / "tools" / "sim_tools.py"
        wb_file = src_root / "ansys_unified_mcp" / "tools" / "workbench_filebridge.py"
        mech_file = src_root / "ansys_unified_mcp" / "tools" / "mechanical.py"

        sim_text = sim_file.read_text(encoding="utf-8")
        wb_text = wb_file.read_text(encoding="utf-8")
        mech_text = mech_file.read_text(encoding="utf-8")

        assert "@aliased_tool" not in sim_text
        assert "@aliased_tool" not in wb_text
        assert mech_text.count("@aliased_tool") == 39
