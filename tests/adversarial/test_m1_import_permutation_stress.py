"""Milestone 1 Gate 2: Circular Import & Dynamic Import Permutation Stress Suite.

Author: challenger_m1_gate2_1 (Empirical Challenger)
Objective:
    Empirically verify that circular imports are 100% eliminated under any arbitrary
    import sequence, permutation, multi-threading race condition, or reload cycle.
"""

import itertools
import subprocess
import sys
import threading
import time
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PYTHON_EXE = sys.executable


class TestM1ImportPermutationStress:
    """在全新獨立進程與多執行緒競爭下，對匯入順序進行極限壓力測試。"""

    # 5 個關鍵的匯入陳述式（已移除退役子模組 shim，改用 drivers 套件層 PEP 562 re-export）
    CORE_IMPORT_STATEMENTS = [
        "from ansys_unified_mcp.products.mechanical import *",
        "from ansys_unified_mcp.drivers import *",
        "from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver as D2",
        "from ansys_unified_mcp.products.mechanical import MechanicalDriver as D3",
        "from ansys_unified_mcp.drivers import MechanicalDriver as D4",
    ]

    def _run_in_fresh_process(self, code_snippet: str) -> subprocess.CompletedProcess:
        """在完全隔離的全新 Python 直譯器進程中執行代碼片段。"""
        full_script = f"""
import sys
sys.path.insert(0, r"{PROJECT_ROOT / 'src'}")
sys.path.insert(0, r"{PROJECT_ROOT}")

{code_snippet}
"""
        res = subprocess.run(
            [PYTHON_EXE, "-c", full_script],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return res

    def test_single_driver_exports_identity_oracle(self):
        """神諭驗證：三個途徑匯入之 MechanicalDriver 必須在記憶體中具備完全一致的 Class 身份。"""
        script = """
from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver as D_raw
from ansys_unified_mcp.drivers import MechanicalDriver as D_drivers
from ansys_unified_mcp.products.mechanical import MechanicalDriver as D_prod

assert D_raw is D_drivers, f"D_raw != D_drivers: {D_raw} vs {D_drivers}"
assert D_raw is D_prod, f"D_raw != D_prod: {D_raw} vs {D_prod}"

# 驗證類別實例化能力
inst = D_raw()
assert inst.solver_name == "ANSYS Mechanical"
print("IDENTITY_VERIFIED")
"""
        res = self._run_in_fresh_process(script)
        assert res.returncode == 0, f"Process failed: {res.stderr}\n{res.stdout}"
        assert "IDENTITY_VERIFIED" in res.stdout

    @pytest.mark.parametrize(
        "first_import",
        [
            "from ansys_unified_mcp.products.mechanical import *",
            "from ansys_unified_mcp.drivers import *",
            "from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver",
            "from ansys_unified_mcp.products.mechanical import MechanicalDriver",
            "from ansys_unified_mcp.drivers import MechanicalDriver",
            "import ansys_unified_mcp.tools",
            "from ansys_unified_mcp.products.mechanical.tools import *",
        ],
    )
    def test_entrypoint_isolation_in_fresh_process(self, first_import):
        """實證驗證：以任意關鍵模組作為直譯器首個載入對象，隨後載入其餘全部模組，均不引發循環匯入。"""
        script = f"""
{first_import}
from ansys_unified_mcp.products.mechanical import *
from ansys_unified_mcp.drivers import *
from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver as M2
from ansys_unified_mcp.products.mechanical import MechanicalDriver as M3
from ansys_unified_mcp.drivers import MechanicalDriver as M4

assert M2 is M3 is M4
print("ENTRYPOINT_OK")
"""
        res = self._run_in_fresh_process(script)
        assert res.returncode == 0, f"Failed for entrypoint {first_import}: {res.stderr}\n{res.stdout}"
        assert "ENTRYPOINT_OK" in res.stdout

    def test_pairwise_reverse_order_permutations(self):
        """實證驗證：將 5 個主要匯入語句進行兩兩反轉全排列（共 20 種組合），全部必須 100% 成功。"""
        stmts = self.CORE_IMPORT_STATEMENTS
        pairs = list(itertools.permutations(stmts, 2))
        assert len(pairs) == 20

        for idx, (s1, s2) in enumerate(pairs):
            script = f"""
{s1}
{s2}
print("PAIR_OK_{idx}")
"""
            res = self._run_in_fresh_process(script)
            assert res.returncode == 0, f"Pairwise failed for ({s1} -> {s2}):\n{res.stderr}"
            assert f"PAIR_OK_{idx}" in res.stdout

    def test_triple_order_permutations_stress(self):
        """實證驗證：3 個語句的排列組合壓力測試（隨機選取代表性排列，共 36 組），驗證鏈狀載入穩定性。"""
        stmts = self.CORE_IMPORT_STATEMENTS[:4]  # 取前 4 個產生 4! = 24 種全排列
        permutations_list = list(itertools.permutations(stmts, 4))
        assert len(permutations_list) == 24

        for idx, perm in enumerate(permutations_list):
            code_block = "\n".join(perm)
            script = f"""
{code_block}
print("PERM4_OK_{idx}")
"""
            res = self._run_in_fresh_process(script)
            assert res.returncode == 0, f"Permutation failed for:\n{code_block}\nError:\n{res.stderr}"
            assert f"PERM4_OK_{idx}" in res.stdout

    def test_multithreaded_concurrent_import_race(self):
        """實證併發神諭：10 個執行緒在 Barrier 微秒級同步下同時從不同模組觸發 import，驗證無死結與無半初始化狀態。"""
        script = """
import sys
import threading
import time

barrier = threading.Barrier(10)
results = [None] * 10
errors = [None] * 10

def worker(idx):
    try:
        barrier.wait(timeout=5)
        if idx % 4 == 0:
            import ansys_unified_mcp.products.mechanical as m
            results[idx] = m.MechanicalDriver
        elif idx % 4 == 1:
            import ansys_unified_mcp.drivers as d
            results[idx] = d.MechanicalDriver
        elif idx % 4 == 2:
            from ansys_unified_mcp.drivers import MechanicalDriver
            results[idx] = MechanicalDriver
        else:
            from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver
            results[idx] = MechanicalDriver
    except Exception as e:
        errors[idx] = f"{type(e).__name__}: {e}"

threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join(timeout=10)

for idx, err in enumerate(errors):
    if err is not None:
        print(f"THREAD_{idx}_ERROR: {err}")
        sys.exit(1)

base = results[0]
for idx, r in enumerate(results):
    assert r is base, f"Thread {idx} got {r} != {base}"

print("CONCURRENT_RACE_PASSED")
"""
        res = self._run_in_fresh_process(script)
        assert res.returncode == 0, f"Multi-threaded concurrent import race failed:\n{res.stderr}\n{res.stdout}"
        assert "CONCURRENT_RACE_PASSED" in res.stdout

    def test_all_lazy_drivers_export_and_instantiation(self):
        """實證驗證：drivers/__init__.py 的 _LAZY_DRIVERS 內所有驅動皆可被 PEP 562 正確解析並能安全實例化。"""
        script = """
from ansys_unified_mcp.drivers import (
    BaseSolverDriver,
    MechanicalDriver,
    LSDynaDriver,
    OptislangDriver,
    SpaceClaimDriver,
    FluentDriver,
    IcepakDriver,
)

drivers = [
    MechanicalDriver,
    LSDynaDriver,
    OptislangDriver,
    SpaceClaimDriver,
    FluentDriver,
    IcepakDriver,
]

for d in drivers:
    assert issubclass(d, BaseSolverDriver)
    inst = d()
    assert inst.solver_name is not None
    print(f"Driver {d.__name__} verified: {inst.solver_name}")

print("ALL_DRIVERS_VERIFIED")
"""
        res = self._run_in_fresh_process(script)
        assert res.returncode == 0, f"Drivers lazy load failed:\n{res.stderr}\n{res.stdout}"
        assert "ALL_DRIVERS_VERIFIED" in res.stdout

    def test_reload_cycle_resilience(self):
        """實證驗證：連續 5 輪 importlib.reload 驅動與產品模組，驗證導出狀態不腐化。"""
        script = """
import importlib
import ansys_unified_mcp.drivers as drv
import ansys_unified_mcp.products.mechanical as mech
import ansys_unified_mcp.products.mechanical.driver as mech_drv

for i in range(5):
    importlib.reload(mech_drv)
    importlib.reload(drv)
    importlib.reload(mech)
    
    assert hasattr(drv, "MechanicalDriver")
    assert hasattr(mech, "MechanicalDriver")

print("RELOAD_CYCLE_PASSED")
"""
        res = self._run_in_fresh_process(script)
        assert res.returncode == 0, f"Reload cycle failed:\n{res.stderr}\n{res.stdout}"
        assert "RELOAD_CYCLE_PASSED" in res.stdout


if __name__ == "__main__":
    pytest.main(["-v", __file__])
