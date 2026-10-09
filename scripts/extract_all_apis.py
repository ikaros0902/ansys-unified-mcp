"""
ANSYS 四大模組 API 一鍵批次萃取總控腳本
依序萃取 SpaceClaim、Mechanical、optiSLang、LS-DYNA 所有 Function / Class / Method 並產出結構化 JSON。
"""
import sys
import time
from pathlib import Path

# 加入當前 scripts 目錄
scripts_dir = Path(__file__).resolve().parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from extract_spaceclaim_api import extract_spaceclaim
from extract_mechanical_api import extract_mechanical
from extract_optislang_api import extract_optislang
from extract_lsdyna_api import extract_lsdyna

def main():
    print("=" * 60)
    print("開始執行 ANSYS 四大模組 API 一鍵全量萃取...")
    print("=" * 60)
    start_total = time.time()

    # 1. SpaceClaim
    print("\n[1/4] 萃取 SpaceClaim API (SpaceClaim.Api.V251.Scripting.dll)...")
    t0 = time.time()
    sc_res = extract_spaceclaim()
    print(f"SpaceClaim 萃取耗時: {time.time() - t0:.2f} 秒")

    # 2. Mechanical
    print("\n[2/4] 萃取 Mechanical ACT & DataModel API (ansys-mechanical-stubs)...")
    t0 = time.time()
    mech_res = extract_mechanical()
    print(f"Mechanical 萃取耗時: {time.time() - t0:.2f} 秒")

    # 3. optiSLang
    print("\n[3/4] 萃取 optiSLang API (ansys.optislang.core & scripting)...")
    t0 = time.time()
    osl_res = extract_optislang()
    print(f"optiSLang 萃取耗時: {time.time() - t0:.2f} 秒")

    # 4. LS-DYNA
    print("\n[4/4] 萃取 LS-DYNA & LS-PrePost API (Python, SCL, Keywords)...")
    t0 = time.time()
    dyna_res = extract_lsdyna()
    print(f"LS-DYNA 萃取耗時: {time.time() - t0:.2f} 秒")

    # 5. 重建 API 知識庫 SQLite
    print("\n[5/5] 建置 API 知識層 SQLite 索引庫 (api_kb.sqlite)...")
    t0 = time.time()
    try:
        from ansys_unified_mcp.analytics.apikb.build import build_database
        kb_res = build_database(force=True)
        print(f"API 知識庫建置完成，耗時: {time.time() - t0:.2f} 秒，統計: {kb_res.get('statistics')}")
    except Exception as exc:
        print(f"API 知識庫建置警告: {exc}")

    print("\n" + "=" * 60)
    print(f"[SUCCESS] 全部四大模組 API 抽取與知識庫建置完畢！總耗時: {time.time() - start_total:.2f} 秒")
    print(f"目錄位置: {Path(r'F:/Ming_python/ansys-unified-mcp/docs/api_inventory').resolve()}")
    print("=" * 60)

if __name__ == "__main__":
    main()
