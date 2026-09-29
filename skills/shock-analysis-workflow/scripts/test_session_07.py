# -*- coding: utf-8 -*-
"""
Standalone Validation Script for Session 07: Solve Dispatch & Energy Balance Monitor.
Tests offline glstat parser, energy ratio bounds (0.90 ~ 1.10), hourglass energy ratio (< 10%),
and abort mechanisms on artificial energy explosions, plus optional online connection to live Mechanical session.
"""
import sys
import os
from pathlib import Path

# 加入專案原始碼路徑以匯入 MechanicalController
_repo_src = str(Path(__file__).resolve().parents[3] / "src")
if _repo_src not in sys.path:
    sys.path.insert(0, _repo_src)
from ansys_unified_mcp.products.mechanical import MechanicalController

SAMPLE_NORMAL_GLSTAT = """
 time...................................  5.000000E-03
 kinetic energy.........................  1.200000E+04
 internal energy........................  4.000000E+03
 hourglass energy.......................  1.600000E+02
 total energy...........................  1.616000E+04
 energy ratio w/o eroded energy.........  1.002000E+00
"""

SAMPLE_EXPLOSION_GLSTAT = """
 time...................................  5.000000E-03
 kinetic energy.........................  8.200000E+04
 internal energy........................  5.000000E+04
 hourglass energy.......................  1.600000E+02
 total energy...........................  1.321600E+05
 energy ratio w/o eroded energy.........  1.250000E+00
"""

SAMPLE_HG_EXCESS_GLSTAT = """
 time...................................  5.000000E-03
 kinetic energy.........................  1.200000E+04
 internal energy........................  4.000000E+03
 hourglass energy.......................  8.000000E+02
 total energy...........................  1.680000E+04
 energy ratio w/o eroded energy.........  1.005000E+00
"""

def parse_and_audit_glstat(block_text):
    data = {}
    for line in block_text.strip().splitlines():
        if "kinetic energy" in line:
            data["kinetic"] = float(line.split()[-1])
        elif "internal energy" in line:
            data["internal"] = float(line.split()[-1])
        elif "hourglass energy" in line:
            data["hourglass"] = float(line.split()[-1])
        elif "total energy" in line:
            data["total"] = float(line.split()[-1])
        elif "energy ratio" in line:
            data["ratio"] = float(line.split()[-1])
            
    # 能量守恆門禁
    if "ratio" in data:
        r = data["ratio"]
        if r < 0.90 or r > 1.10:
            raise ValueError(f"Energy ratio violation: {r:.4f} outside [0.90, 1.10]")
            
    # 沙漏能佔比門禁
    if "hourglass" in data and "internal" in data and data["internal"] > 0:
        hg_ratio = data["hourglass"] / data["internal"]
        if hg_ratio > 0.10:
            raise ValueError(f"Hourglass energy ratio {hg_ratio*100:.2f}% exceeds 10% limit")
            
    return data

def verify_offline_energy_gatekeeper():
    print("==================================================")
    print("SESSION 07: ENERGY BALANCE & GATEKEEPER TEST")
    print("==================================================")
    
    # 1. 測試正常收斂數據
    res_normal = parse_and_audit_glstat(SAMPLE_NORMAL_GLSTAT)
    assert 0.90 <= res_normal["ratio"] <= 1.10, "Normal ratio check failed"
    hg_pct = res_normal["hourglass"] / res_normal["internal"]
    assert hg_pct <= 0.10, "Normal hourglass check failed"
    print(f"[1/3] Normal Convergence Block: PASS (Ratio={res_normal['ratio']:.3f}, HG={hg_pct*100:.1f}%)")
    
    # 2. 測試能量爆炸阻斷
    caught_explosion = False
    try:
        parse_and_audit_glstat(SAMPLE_EXPLOSION_GLSTAT)
    except ValueError as e:
        caught_explosion = True
        print(f"[2/3] Energy Explosion Gate: PASS (Successfully caught: {e})")
    assert caught_explosion, "Energy explosion gate failed to block!"
    
    # 3. 測試沙漏能超標阻斷
    caught_hg = False
    try:
        parse_and_audit_glstat(SAMPLE_HG_EXCESS_GLSTAT)
    except ValueError as e:
        caught_hg = True
        print(f"[3/3] Hourglass Excess Gate: PASS (Successfully caught: {e})")
    assert caught_hg, "Hourglass excess gate failed to block!"
    
    print("--------------------------------------------------")
    print("All Session 07 Physics Gates Passed 100%!")
    print("==================================================")
    return True

def main():
    verify_offline_energy_gatekeeper()
    
    print("\nAttempting connection to live ANSYS Mechanical instance (Port 10000)...")
    mc = MechanicalController()
    res = mc.connect(port=10000)
    if not res.get("ok"):
        print("[NOTICE] Mechanical gRPC Port 10000 offline. Offline physics validation passed 100%.")
        return True
        
    script = """
model = ExtAPI.DataModel.Project.Model
analysis = model.Analyses[0]
print("Session 07 Live Check -> Analysis Type: " + str(analysis.AnalysisType))
print("Session 07 Live Check -> Solution Status: " + str(analysis.Solution.Status))
"""
    out = mc.run_script(script)
    print(out)
    return True

if __name__ == "__main__":
    main()
