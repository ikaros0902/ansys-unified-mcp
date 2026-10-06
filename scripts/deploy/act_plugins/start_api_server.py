# SpaceClaim startup script - auto-starts the gRPC API Server (port 50051) in the background.
# This script is auto-copied by setup.ps1 to %APPDATA%\SpaceClaim\Published Scripts\
# Configure this script as the SpaceClaim startup macro:
#   File > SpaceClaim Options > File Options > Startup macro > point to this file
#
# Path resolution: does not assume ANSYS is installed at the default
# "C:\Program Files\ANSYS Inc". Instead, it tries the AWP_ROOT<ver> environment
# variable (always set correctly by the ANSYS installer) first, then falls
# back to common install locations, so the DLL is still found when ANSYS is
# installed on a non-default drive (e.g. D:).

import os
import System.Reflection
import System

# Candidate versions in preference order; the first one with an existing DLL wins.
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
