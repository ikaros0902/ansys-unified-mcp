"""
API 知識庫黃金查詢集客觀評估腳本 (Golden Evaluation Script)
測試 40 題涵蓋 Mechanical、SpaceClaim、optiSLang、LS-DYNA 之典型查詢，計算 Recall@5 與延遲。
"""
import time
from ansys_unified_mcp.analytics.apikb.query import search, path
from ansys_unified_mcp.analytics.apikb.validate import validate_script

GOLDEN_QUERIES = [
    # Mechanical (英文與中文)
    ("fixed support", "mechanical", "FixedSupport"),
    ("AddFixedSupport", "mechanical", "AddFixedSupport"),
    ("equivalent stress", "mechanical", "EquivalentStress"),
    ("AddEquivalentStress", "mechanical", "AddEquivalentStress"),
    ("frictionless support", "mechanical", "FrictionlessSupport"),
    ("remote displacement", "mechanical", "RemoteDisplacement"),
    ("standard gravity", "mechanical", "StandardEarthGravity"),
    ("mesh control", "mechanical", "MeshControl"),
    ("element size", "mechanical", "ElementSize"),
    ("contact region", "mechanical", "ContactRegion"),
    # SpaceClaim
    ("DatumPlane", "spaceclaim", "DatumPlane"),
    ("FixSimplify", "spaceclaim", "FixSimplify"),
    ("Midsurface", "spaceclaim", "Midsurface"),
    ("Part", "spaceclaim", "Part"),
    ("Component", "spaceclaim", "Component"),
    ("Selection", "spaceclaim", "Selection"),
    ("Extrude", "spaceclaim", "Extrude"),
    ("Body", "spaceclaim", "Body"),
    ("Face", "spaceclaim", "Face"),
    ("SketchCircle", "spaceclaim", "SketchCircle"),
    # optiSLang
    ("Optislang", "optislang", "Optislang"),
    ("create_node", "optislang", "create_node"),
    ("Sensitivity", "optislang", "Sensitivity"),
    ("add_parameter", "optislang", "add_parameter"),
    ("add_criterion", "optislang", "add_criterion"),
    ("start", "optislang", "start"),
    ("Project", "optislang", "Project"),
    ("RootSystem", "optislang", "RootSystem"),
    ("MOP", "optislang", "mop"),
    # LS-DYNA & LS-PrePost
    ("CONTROL_TERMINATION", "lsdyna", "CONTROL_TERMINATION"),
    ("CONTROL_ENERGY", "lsdyna", "CONTROL_ENERGY"),
    ("MAT_PIECEWISE_LINEAR_PLASTICITY", "lsdyna", "MAT_PIECEWISE_LINEAR_PLASTICITY"),
    ("DATABASE_BINARY_D3PLOT", "lsdyna", "DATABASE_BINARY_D3PLOT"),
    ("CONTACT_AUTOMATIC_SINGLE_SURFACE", "lsdyna", "CONTACT_AUTOMATIC_SINGLE_SURFACE"),
    ("get_data", "lsdyna", "get_data"),
    ("execute_command", "lsdyna", "execute_command"),
    ("cmd_result_get_value", "lsdyna", "cmd_result_get_value"),
    ("DataCenter", "lsdyna", "DataCenter"),
    ("LsPrePost", "lsdyna", "LsPrePost"),
]

def run_evaluation():
    print("=" * 60)
    print(f"開始執行 API 知識庫黃金查詢集評估 (共 {len(GOLDEN_QUERIES)} 題)...")
    print("=" * 60)

    hits_at_5 = 0
    latencies = []

    for q, prod, expected in GOLDEN_QUERIES:
        t0 = time.time()
        results = search(q, product=prod, top_k=5)
        dt = (time.time() - t0) * 1000.0
        latencies.append(dt)

        found = False
        for r in results:
            if expected.lower() in r["name"].lower() or expected.lower() in r["fqname"].lower():
                found = True
                break

        if found:
            hits_at_5 += 1
            status = "PASS"
        else:
            status = "FAIL"

        # print(f"[{status}] Query: '{q}' ({prod}) -> Expect: '{expected}' ({dt:.1f}ms)")

    recall = hits_at_5 / len(GOLDEN_QUERIES) * 100.0
    latencies.sort()
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95)]

    print(f"\n評估結果:")
    print(f"  - 總題數: {len(GOLDEN_QUERIES)}")
    print(f"  - Recall@5 命中率: {recall:.1f}% (命中 {hits_at_5}/{len(GOLDEN_QUERIES)})")
    print(f"  - P50 延遲: {p50:.2f} ms")
    print(f"  - P95 延遲: {p95:.2f} ms")

    # 驗證導航與校驗功能
    t0 = time.time()
    nav_paths = path("Analysis", "EquivalentStress")
    nav_dt = (time.time() - t0) * 1000.0
    print(f"  - 物件導航路徑測試: {'通過' if nav_paths else '未找到'} (耗時: {nav_dt:.2f} ms)")

    val_res = validate_script("x = analysis.AddFixedSupport()\ny = eqv.Maximum.Value", "mechanical")
    print(f"  - 腳本校驗器測試: {'通過' if val_res['valid'] else '失敗'}")
    print("=" * 60)

    assert recall >= 90.0, f"Recall@5 未達標: {recall}%"
    assert p95 < 150.0, f"P95 延遲超標: {p95} ms"

if __name__ == "__main__":
    run_evaluation()
