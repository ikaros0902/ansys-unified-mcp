# SpaceClaim 啟動腳本 — 自動在背景開啟 gRPC API Server (port 50051)
# 此腳本由 setup.ps1 自動複製至 %APPDATA%\SpaceClaim\Published Scripts\
# 請在 SpaceClaim 中設定此腳本為啟動腳本：
#   File > SpaceClaim Options > File Options > Startup macro > 指向此檔案
#
# 路徑解析：不假設 ANSYS 安裝在預設的 "C:\Program Files\ANSYS Inc"，改為
# 依序嘗試 AWP_ROOT<ver> 環境變數（ANSYS 安裝程式本身會設定，永遠正確）與
# 常見安裝位置，避免在非預設磁碟機（如 D:）安裝時找不到 DLL。

import os
import System.Reflection
import System

# 依偏好順序列出候選版本；找到第一個實際存在 DLL 的版本就使用它。
_CANDIDATE_VERSIONS = ["251", "252", "261", "242", "241"]
_STANDARD_ROOTS = [r"C:\Program Files\ANSYS Inc", r"D:\ANSYS Inc"]


def _resolve_assembly_path():
    for ver in _CANDIDATE_VERSIONS:
        awp_root = os.environ.get("AWP_ROOT" + ver)
        if awp_root:
            candidate = os.path.join(awp_root, "Addins", "ApiServer", "Presentation.ApiServerAddIn.dll")
            if os.path.isfile(candidate):
                return candidate
        for base in _STANDARD_ROOTS:
            candidate = os.path.join(base, "v" + ver, "Addins", "ApiServer", "Presentation.ApiServerAddIn.dll")
            if os.path.isfile(candidate):
                return candidate
    return None


try:
    assembly_path = _resolve_assembly_path()
    if assembly_path is None:
        print("[MCP] Warning: Could not locate Presentation.ApiServerAddIn.dll under any known ANSYS install root.")
    else:
        asm = System.Reflection.Assembly.LoadFrom(assembly_path)
        addin_type = asm.GetType("Presentation.ApiServerAddIn.ApiServerAddIn")
        addon = System.Activator.CreateInstance(addin_type)
        addon.Initialize()
        addon.Connect()
        print("[MCP] SpaceClaim gRPC API Server started on port 50051 (" + assembly_path + "). AI can now connect!")
except Exception as e:
    print("[MCP] Warning: Could not start API Server:", str(e))
