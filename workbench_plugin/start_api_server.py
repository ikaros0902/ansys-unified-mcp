# SpaceClaim 啟動腳本 — 自動在背景開啟 gRPC API Server (port 50051)
# 此腳本由 setup.ps1 自動複製至 %APPDATA%\SpaceClaim\Published Scripts\
# 請在 SpaceClaim 中設定此腳本為啟動腳本：
#   File > SpaceClaim Options > File Options > Startup macro > 指向此檔案

import System.Reflection
import System

try:
    asm = System.Reflection.Assembly.LoadFrom(
        r"C:\Program Files\ANSYS Inc\v251\Addins\ApiServer\Presentation.ApiServerAddIn.dll"
    )
    addin_type = asm.GetType("Presentation.ApiServerAddIn.ApiServerAddIn")
    addon = System.Activator.CreateInstance(addin_type)
    addon.Initialize()
    addon.Connect()
    print("[MCP] SpaceClaim gRPC API Server started on port 50051. AI can now connect!")
except Exception as e:
    print("[MCP] Warning: Could not start API Server:", str(e))
