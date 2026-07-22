#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ANSYS Unified MCP 連線體檢 (doctor)。

在 ANSYS 機的 .venv 下執行，逐一檢查六個模組能否連線與操作：
Mechanical、LS-DYNA、SpaceClaim、Workbench、optiSLang、Thermal。

用法：
  # Level 1：只檢查套件/執行檔是否就緒（快、免授權、不啟動 ANSYS）
  python check_connections.py

  # Level 2：實際啟動並連線（慢、需授權，會開 ANSYS 進程）
  python check_connections.py --live
  python check_connections.py --live --only optislang,mechanical

ponytail: Level 2 的 launch 很重（SpaceClaim 冷啟 30~50s、Mechanical/optiSLang 需授權）。
預設只跑 Level 1；要真連線才加 --live。
"""
from __future__ import annotations
import argparse
import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except Exception:
    pass

OK, FAIL, SKIP = "✅ OK", "❌ FAIL", "⏭  SKIP"


def _has(mod: str) -> bool:
    """套件是否可 import（不實際 import，避免副作用）。

    find_spec 在父套件缺失時會丟 ModuleNotFoundError，須吞掉回 False。
    """
    try:
        return importlib.util.find_spec(mod) is not None
    except ModuleNotFoundError:
        return False


def _exe(env_key: str) -> str | None:
    p = os.environ.get(env_key)
    return p if p and Path(p).exists() else None


# ── 各模組檢查：回 (status, 說明) ───────────────────────────────

def check_mechanical(live: bool):
    if not _has("ansys.mechanical.core"):
        return FAIL, "缺 ansys-mechanical-core (pip install ansys-mechanical-core)"
    if not live:
        exe = _exe("ANSYS_MECHANICAL")
        return OK, f"套件就緒；exe={'找到' if exe else '未設(.env ANSYS_MECHANICAL)'}"
    try:
        import ansys.mechanical.core as pymech
        app = pymech.App()  # embedded，較 launch 輕
        ver = app.version
        app.close()
        return OK, f"embedded App 連線成功，version={ver}"
    except Exception as e:
        return FAIL, f"連線失敗：{e}"


def check_lsdyna(live: bool):
    # LS-DYNA 無 gRPC；後處理靠 lasso 讀 d3plot，求解靠 solver exe/subprocess
    lasso = _has("lasso")
    solver = _exe("ANSYS_LSDYNA") or _find_lsdyna_exe()
    pydyna = _has("ansys.dyna.core")
    parts = [f"lasso(d3plot讀取)={'有' if lasso else '無'}",
             f"solver exe={'找到' if solver else '未找到'}",
             f"pydyna={'有' if pydyna else '無(選用)'}"]
    if not lasso and not solver:
        return FAIL, "；".join(parts) + " → 後處理與求解皆缺"
    return OK, "；".join(parts)


def _find_lsdyna_exe():
    root = os.environ.get("ANSYS_ROOT")
    if not root:
        return None
    for name in ("lsdyna_dp.exe", "lsdyna_sp.exe", "lsdyna.exe"):
        hit = list(Path(root).rglob(name))
        if hit:
            return str(hit[0])
    return None


def check_spaceclaim(live: bool):
    if not _has("ansys.geometry.core"):
        return FAIL, "缺 ansys-geometry-core"
    if not live:
        return OK, "套件就緒（live 會啟動 SpaceClaim，冷啟 30~50s）"
    try:
        from ansys.geometry.core import launch_modeler
        m = launch_modeler(mode="spaceclaim", timeout=180)
        m.close()
        return OK, "SpaceClaim 啟動並連線成功"
    except Exception as e:
        return FAIL, f"啟動失敗：{e}"


def check_workbench(live: bool):
    exe = _exe("ANSYS_RUNWB2")
    if not exe:
        try:
            from tools.workbench_bridge import find_workbench_exe
            found = find_workbench_exe()
            exe = str(found) if found else None
        except Exception:
            pass
    if not exe:
        return FAIL, "找不到 RunWB2.exe（設 .env ANSYS_RUNWB2）"
    if not live:
        return OK, f"RunWB2 就緒：{exe}"
    try:
        from tools.workbench_bridge import detect_workbench_environment
        return OK, f"環境偵測：{detect_workbench_environment()}"
    except Exception as e:
        return OK, f"RunWB2 存在但偵測函式未跑：{e}"


def check_optislang(live: bool):
    if not _has("ansys.optislang.core"):
        return FAIL, "缺 ansys-optislang-core (pip install ansys-optislang-core)"
    if not live:
        return OK, "套件就緒（live 需 optiSLang 授權）"
    try:
        from ansys.optislang.core import Optislang
        osl = Optislang(ini_timeout=90)
        ver = getattr(osl, "osl_version_string", None)
        ver = ver() if callable(ver) else (ver or "unknown")
        osl.dispose()
        return OK, f"optiSLang 連線成功，version={ver}"
    except Exception as e:
        return FAIL, f"連線失敗：{e}"


def check_thermal(live: bool):
    # Thermal 不是獨立連線，是 Mechanical/Workbench 內的分析類型
    mech_ok = _has("ansys.mechanical.core")
    wb_ok = _exe("ANSYS_RUNWB2") is not None
    if not (mech_ok or wb_ok):
        return FAIL, "thermal 依賴 Mechanical/Workbench，兩者皆未就緒"
    note = "thermal=Mechanical/WB 的分析類型；驗證方式=建立 Steady-State/Transient Thermal 系統"
    if not live:
        return OK, note
    # live 驗證留給 Workbench bridge 建立 thermal 系統（見 wb_bridge_tools）
    return SKIP, note + "（live 驗證請用 wb_bridge 建立 Steady-State Thermal 系統）"


CHECKS = {
    "mechanical": check_mechanical,
    "lsdyna": check_lsdyna,
    "spaceclaim": check_spaceclaim,
    "workbench": check_workbench,
    "optislang": check_optislang,
    "thermal": check_thermal,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="實際啟動並連線（需授權）")
    ap.add_argument("--only", default="", help="逗號分隔，只檢查指定模組")
    args = ap.parse_args()

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    targets = {k: v for k, v in CHECKS.items() if not only or k in only}

    print(f"Python {sys.version.split()[0]} | 模式={'LIVE' if args.live else 'imports-only'}")
    print(f"ANSYS_ROOT={os.environ.get('ANSYS_ROOT', '(未設)')}")
    print("-" * 72)
    results = {}
    for name, fn in targets.items():
        try:
            status, msg = fn(args.live)
        except Exception as e:
            status, msg = FAIL, f"檢查器例外：{e}"
        results[name] = status
        print(f"{status}  {name:12} {msg}")
    print("-" * 72)
    passed = sum(1 for s in results.values() if s == OK)
    print(f"通過 {passed}/{len(results)}")
    # 任一 FAIL → 非零 exit，方便當 Loop Verification_Condition
    sys.exit(0 if all(s != FAIL for s in results.values()) else 1)


if __name__ == "__main__":
    main()
