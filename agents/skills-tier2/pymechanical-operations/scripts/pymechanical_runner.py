# -*- coding: utf-8 -*-
"""
PyMechanical Remote Operations & Session Helper.
"""
def launch_pymechanical_session(port=10000):
    """
    使用 ansys.mechanical.core 建立與連線 PyMechanical 實例。
    """
    try:
        from ansys.mechanical.core import connect_to_mechanical
        mc = connect_to_mechanical(port=port)
        print("成功建立 PyMechanical 會話，服務連線埠: {}".format(port))
        print("Mechanical API 版本: {}".format(mc.version))
        return mc
    except Exception as e:
        print("PyMechanical 會話連線失敗: {}".format(e))
        return None

if __name__ == "__main__":
    launch_pymechanical_session()
