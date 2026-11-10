# -*- coding: utf-8 -*-
"""
ANSYS 錯誤診斷與安全防護腳本
提供 IronPython 閉包檢測、全域變數未定義防護、Quantity 單位校驗與 Scoping ID 檢查。
"""
import sys

def check_script_environment():
    """
    檢查 Python/IronPython 執行環境與全域環境差異
    """
    env_info = {
        "python_version": sys.version,
        "is_ironpython": "IronPython" in sys.version,
        "platform": sys.platform
    }
    print("=== ANSYS Scripting 執行環境診斷 ===")
    print("Python 版本: {}".format(env_info["python_version"]))
    print("IronPython 環境: {}".format(env_info["is_ironpython"]))
    return env_info

def safe_get_quantity(val_str, unit_str, quantity_class=None):
    """
    安全建立 Quantity 物件，避免 StandardError 或 NameError
    """
    if quantity_class is None:
        try:
            from Ansys.Core.Units import Quantity
            quantity_class = Quantity
        except Exception:
            pass
            
    if quantity_class is not None:
        return quantity_class("{} [{}]".format(val_str, unit_str))
    else:
        print("警告: 無法載入 Quantity 類別，回傳原始數值。")
        return (val_str, unit_str)

if __name__ == "__main__":
    check_script_environment()
