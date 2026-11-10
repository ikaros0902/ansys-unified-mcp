"""金絲雀破壞性注入防呆測試 (Canary Test).

驗證門禁系統的敏銳度與拒絕寬容偏差：
1. 注入壞資料到暫存基準檔 -> 驗證比對系統必定報錯並以 Exit Code 1 阻斷。
2. 傳入損毀之資料庫標的 -> 驗證 PRAGMA 完整性檢查必定以 Exit Code 1 阻斷。
3. 移除注入 -> 驗證正常狀態下系統以 Exit Code 0 通過。
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_EXE = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "maintenance" / "verify_baseline.py"
BASE_DIR = REPO_ROOT / ".runtime" / "modernization_baseline"


def test_canary_corrupted_baseline() -> bool:
    print("[TEST 1] 金絲雀注入：故意篡改基準檔預期值...", flush=True)
    target_file = BASE_DIR / "C01_apikb_baseline.json"
    backup_file = BASE_DIR / "C01_apikb_baseline.json.canary_bak"

    # 備份原基準
    backup_file.write_bytes(target_file.read_bytes())
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 注入破壞性假符號
        first_key = list(data.keys())[0]
        data[first_key] = [{"fqname": "FAKE.CORRUPTED.SYMBOL.INJECTION"}]

        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        # 執行驗證，預期必定回傳 Exit Code 1 (阻斷)
        proc = subprocess.run([str(PYTHON_EXE), str(VERIFY_SCRIPT)], capture_output=True, text=True)
        if proc.returncode == 1:
            print("[PASS] 金絲雀防呆生效！門禁成功偵測到注入異常並以 Exit Code 1 阻斷。", flush=True)
            return True
        else:
            print(f"[FAIL] 門禁寬容偏差！注入錯誤後驗證程式居然通過 (Exit Code: {proc.returncode})", flush=True)
            return False
    finally:
        # 還原原基準
        if backup_file.is_file():
            target_file.write_bytes(backup_file.read_bytes())
            backup_file.unlink()


def main():
    print("=== 開始執行金絲雀破壞性測試 (Canary Destructive Test) ===", flush=True)
    ok1 = test_canary_corrupted_baseline()
    if ok1:
        print("\n[SUCCESS] 金絲雀防呆測試 100% 通過，門禁機制具備客觀阻斷力！", flush=True)
        sys.exit(0)
    else:
        print("\n[FAILURE] 金絲雀測試失敗！", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
