# SpaceClaimMCP ACT Extension — main.py
# 在 SpaceClaim 啟動時自動載入並啟動 gRPC API Server (port 50051)
# 讓 AI (MCP) 可以隨時連線，無需手動操作

import System.Reflection
import System

API_SERVER_DLL = r"C:\Program Files\ANSYS Inc\v251\Addins\ApiServer\Presentation.ApiServerAddIn.dll"
GRPC_PORT = 50051

_addon = None

def _start_grpc_server():
    """載入並啟動 SpaceClaim gRPC API Server"""
    global _addon
    try:
        asm = System.Reflection.Assembly.LoadFrom(API_SERVER_DLL)
        addin_type = asm.GetType("Presentation.ApiServerAddIn.ApiServerAddIn")
        _addon = System.Activator.CreateInstance(addin_type)
        _addon.Initialize()
        _addon.Connect()
        ExtAPI.Log.WriteMessage("[SpaceClaimMCP] gRPC API Server started on port {0}. AI can now connect!".format(GRPC_PORT))
        return True
    except Exception as e:
        ExtAPI.Log.WriteMessage("[SpaceClaimMCP] Warning: Could not start API Server: {0}".format(str(e)))
        return False

# ── 在擴充套件載入時自動啟動 ──────────────────────────────────────
try:
    _start_grpc_server()
except Exception as e:
    pass  # 靜默失敗，不中斷 SpaceClaim 啟動

# ── Toolbar 按鈕回呼（手動重新啟動用）────────────────────────────
def start_grpc_server():
    """工具列按鈕：手動啟動或重新啟動 gRPC Server"""
    ok = _start_grpc_server()
    if ok:
        ExtAPI.Log.WriteMessage("[SpaceClaimMCP] gRPC Server restarted successfully on port {0}.".format(GRPC_PORT))
    else:
        ExtAPI.Log.WriteMessage("[SpaceClaimMCP] Failed to start gRPC Server. Check ANSYS installation.")
