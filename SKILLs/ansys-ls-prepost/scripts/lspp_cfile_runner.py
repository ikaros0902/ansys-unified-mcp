# -*- coding: utf-8 -*-
"""
LS-PrePost CFile Command Runner Script.
"""
import subprocess
import os

def run_lspp_cfile(lspp_executable, cfile_path, batch_mode=True):
    """
    呼叫 LS-PrePost 執行指定 CFile 命令批次檔。
    """
    if not os.path.exists(cfile_path):
        print("錯誤: 找不到 CFile 腳本檔案: {}".format(cfile_path))
        return False
        
    cmd = [lspp_executable, "c={}".format(cfile_path)]
    if batch_mode:
        cmd.append("-nographics")
        
    print("發送命令至 LS-PrePost: {}".format(" ".join(cmd)))
    try:
        retcode = subprocess.call(cmd)
        print("LS-PrePost 執行結束，Exit Code: {}".format(retcode))
        return retcode == 0
    except Exception as e:
        print("無法啟動 LS-PrePost 處理程序: {}".format(e))
        return False

if __name__ == "__main__":
    print("LS-PrePost CFile 批次腳本執行器就緒。")
