import inspect
import sys
from pathlib import Path

# 將專案 src 加入路徑
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from ansys_unified_mcp.products.mechanical.facade import MechanicalController, controller, PRODUCT
from ansys_unified_mcp.core.sessions import registry

print("MODULE FILE:", inspect.getfile(MechanicalController))
print("PRODUCT:", PRODUCT)
print("STATUS:", controller.status())
print("IS_CONNECTED:", controller.is_connected())

class MockSession:
    def __init__(self):
        self.ran = []
    def run_python_script(self, code):
        self.ran.append(code)
        # 執行 wrapper 代碼以模擬真實行為
        exec(code, globals())

mock_sess = MockSession()
registry.put(PRODUCT, "test_port", mock_sess)

res = controller.run_script("print(123 + 456)", key="test_port")
print("RUN_SCRIPT RESULT:", res)
assert res == "579", f"Expected 579, got {res}"

# 驗證 session probe 與 is_connected
assert controller.is_connected(key="test_port") is True
controller.disconnect(key="test_port")
assert controller.is_connected(key="test_port") is False

print("ALL EXECUTION TRACES VERIFIED CLEAN!")
