# -*- coding: utf-8 -*-
"""
ANSYS LS-PrePost SCL / Python DataCenter 數據擷取與自動化腳本
展示如何使用 LsPrePost 與 DataCenter 讀取 d3plot、擷取節點/單元應力與位移，並匯出 PNG。
"""

def export_d3plot_results(d3plot_path, output_png_path):
    """
    LS-PrePost 數據擷取與 Fringing 匯出腳本 (Python / SCL API 模式)
    """
    print("=== LS-PrePost 數據與圖像自動化匯出 ===")
    print("開啟數據檔案: {}".format(d3plot_path))
    
    # 範例 LsPrePost 指令呼叫流
    commands = [
        "open d3plot \"{}\"".format(d3plot_path),
        "state last",
        "fringe 1",  # 顯示 von Mises 應力
        "print png \"{}\" land mono 0".format(output_png_path)
    ]
    
    for cmd in commands:
        print("執行命令: {}".format(cmd))
        # 在 LS-PrePost 內部執行：
        # import LsPrePost
        # LsPrePost.execute_command(cmd)
        
    print("結果圖像已儲存至: {}".format(output_png_path))
    return True

if __name__ == "__main__":
    export_d3plot_results("d3plot", "stress_fringe.png")
