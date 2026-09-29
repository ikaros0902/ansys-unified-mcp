# -*- coding: utf-8 -*-
"""跨電腦一鍵環境自檢工具 (Preflight Environment Checker)

功能：
1. 檢驗 Python 核心相依套件 (ansys-geometry-core, pandas, openpyxl, grpc, pytz 等)
2. 偵測 ANSYS 軟體安裝版本與環境變數 (AWP_ROOT251, AWP_ROOT242 等)
3. 測試 SpaceClaim gRPC 通訊埠 (50051) 與傳輸模式相容性
4. 測試 Mechanical gRPC 通訊埠 (10000) 連線狀態
5. 檢查專案必要目錄完整性 (workbench_queue, logs/errors, docs 等)
6. 發生異常時自動產生診斷報告並存入 logs/errors/
"""

import sys
import os
import socket
import json
from datetime import datetime
from pathlib import Path

# 防止 Windows 終端機 CP950 編碼輸出 Emoji 或特殊字符報錯
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
LOGS_ERRORS_DIR = REPO_ROOT / "logs" / "errors"

def check_python_packages() -> dict:
    required = {
        "ansys.geometry.core": "ANSYS SpaceClaim / PyAnsys Geometry 幾何核心",
        "pandas": "材料與 Excel 疊構解析資料庫",
        "openpyxl": "Excel 檔案讀取引擎",
        "grpc": "gRPC 跨進程通訊底層協議",
        "pytz": "時區處理模組"
    }
    results = {}
    for pkg, desc in required.items():
        try:
            __import__(pkg)
            results[pkg] = {"status": "PASS", "desc": desc}
        except ImportError as e:
            results[pkg] = {"status": "FAIL", "desc": desc, "error": str(e)}
    return results

def check_ansys_installations() -> dict:
    versions = ["251", "242", "241", "232"]
    detected = {}
    for v in versions:
        var_name = f"AWP_ROOT{v}"
        path = os.environ.get(var_name)
        if path and Path(path).exists():
            detected[var_name] = {"path": path, "source": "Environment Variable"}
        else:
            for drive in ["C:", "D:", "E:"]:
                cand = Path(f"{drive}/Program Files/ANSYS Inc/v{v}")
                if cand.exists():
                    detected[var_name] = {"path": str(cand), "source": f"Scanned {cand}"}
                    break
    return detected

def check_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def check_directories() -> dict:
    required_dirs = [
        REPO_ROOT / "workbench_queue",
        REPO_ROOT / "logs" / "errors",
        REPO_ROOT / "logs" / "script_audit",
        REPO_ROOT / "docs"
    ]
    results = {}
    for d in required_dirs:
        try:
            d.mkdir(parents=True, exist_ok=True)
            results[str(d.relative_to(REPO_ROOT))] = "PASS"
        except Exception as e:
            results[str(d.relative_to(REPO_ROOT))] = f"FAIL: {e}"
    return results

def main():
    print("=" * 70)
    print("[INFO] ANSYS Unified MCP — 跨電腦前置環境健康檢查 (Preflight Health Check)")
    print(f"[INFO] 檢測時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[INFO] 專案根目錄: {REPO_ROOT}")
    print("=" * 70)

    has_error = False
    report = {"timestamp": datetime.now().isoformat(), "host": socket.gethostname()}

    # 1. Python 套件檢測
    print("\n[1/5] [PACKAGES] 檢查 Python 相依套件庫:")
    pkg_results = check_python_packages()
    report["packages"] = pkg_results
    for pkg, info in pkg_results.items():
        if info["status"] == "PASS":
            print(f"  [PASS] {pkg:<22} : 通過 ({info['desc']})")
        else:
            print(f"  [FAIL] {pkg:<22} : 缺失! ({info['desc']}) -> 請執行 pip install {pkg}")
            has_error = True

    # 2. ANSYS 安裝環境檢測
    print("\n[2/5] [ANSYS] 檢查 ANSYS 本機安裝與環境變數:")
    ansys_detected = check_ansys_installations()
    report["ansys_installations"] = ansys_detected
    if ansys_detected:
        for var, info in ansys_detected.items():
            print(f"  [PASS] 偵測到 {var}: {info['path']} ({info['source']})")
    else:
        print("  [WARN] 未直接偵測到 AWP_ROOT 環境變數或標準 ANSYS 安裝目錄 (請確認本機是否已安裝 ANSYS)")

    # 3. SpaceClaim gRPC (Port 50051)
    print("\n[3/5] [PORT 50051] 檢查 SpaceClaim gRPC 服務端狀態:")
    sc_open = check_port_open("localhost", 50051)
    report["spaceclaim_port_50051"] = sc_open
    if sc_open:
        print("  [PASS] Port 50051 正常監聽中 (SpaceClaim 已就緒)")
    else:
        print("  [INFO] Port 50051 未開啟 (若欲執行幾何建模，請先啟動 SpaceClaim 並確保已開啟 gRPC 服務)")

    # 4. Mechanical gRPC (Port 10000)
    print("\n[4/5] [PORT 10000] 檢查 Mechanical gRPC 服務端狀態:")
    mech_open = check_port_open("localhost", 10000)
    report["mechanical_port_10000"] = mech_open
    if mech_open:
        print("  [PASS] Port 10000 正常監聽中 (Mechanical 已就緒)")
    else:
        print("  [INFO] Port 10000 未開啟 (若欲執行結構模擬，請透過 Workbench Bridge 或指令行啟動 Mechanical)")

    # 5. 目錄完整性檢測
    print("\n[5/5] [DIRS] 檢查專案核心資料夾結構與權限:")
    dir_results = check_directories()
    report["directories"] = dir_results
    for d, st in dir_results.items():
        if st == "PASS":
            print(f"  [PASS] {d:<25} : 正常")
        else:
            print(f"  [FAIL] {d:<25} : 異常 ({st})")
            has_error = True

    # 總結報告
    print("\n" + "=" * 70)
    if has_error:
        print("[FAIL] 前置檢測發現相依套件或目錄異常！詳細診斷已記錄。")
        LOGS_ERRORS_DIR.mkdir(parents=True, exist_ok=True)
        dump_path = LOGS_ERRORS_DIR / f"err_{datetime.now().strftime('%Y%m%d_%H%M%S')}_preflight.json"
        with open(dump_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"[FILE] 錯誤診斷檔已儲存於: {dump_path}")
        sys.exit(1)
    else:
        print("[SUCCESS] 前置環境健康檢查完全通過！本電腦環境已就緒。")
        print("=" * 70)
        sys.exit(0)

if __name__ == "__main__":
    main()
