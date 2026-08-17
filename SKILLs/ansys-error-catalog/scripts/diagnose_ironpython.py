# -*- coding: utf-8 -*-
"""
IronPython 2.7 Compatibility & Diagnostics Checker.
"""
import sys

def check_environment():
    """
    診斷目前 Python 執行環境，檢測 IronPython 2.7 語法與載入相容性。
    """
    print("=== ANSYS IronPython 診斷檢查器 ===")
    print("Python 版本: {}".format(sys.version))
    
    # 1. 檢查 CLR 模組
    try:
        import clr
        print("[Status] CLR 模組: 已載入 (.NET Interop 可用)")
    except ImportError:
        print("[Status] CLR 模組: 未載入 (目前為原生 CPython 環境)")
        
    # 2. 檢查 exec 閉包限制
    try:
        exec("def _dummy(): pass")
        print("[Pass] exec 頂層定義語法測試通過")
    except Exception as e:
        print("[Fail] exec 測試例外: {}".format(e))
        
    print("\n常見陷阱提醒:")
    print(" 1. exec() 內部勿使用 nested closure/lambda。")
    print(" 2. mc.run_python_script() 執行時 __name__ 為 '<string>' 而非 '__main__'。")

if __name__ == "__main__":
    check_environment()
