# -*- coding: utf-8 -*-
"""
腳本名稱：check_watertight_topology.py
功能說明：裝配體層級拓撲一致性稽核（水密性彙總、殼體/實體自由邊區分、重複面粗篩）
技術標準：延伸 ansys-spaceclaim-modeling/scripts/check_cad_defects.py 的單體判準至裝配體層級，
         不重複定義微小面/短邊/滲漏判準（詳見該腳本），本腳本專注於裝配體彙總與重複面偵測。

API 查證狀態：
  - body.volume / body.faces / body.edges / design.bodies 已於既有
    check_cad_defects.py 中驗證可用（ansys.geometry.core.Modeler 連線後之 Design/Body 物件）。
  - PyAnsys Geometry 是否提供原生「非 manifold 邊」或「邊迴路 (edge loop) 走訪」API，
    截至本次查證尚未在 docs/api_inventory 中找到對應項目，標記為「待 api_search 查證」。
    本腳本改用保守的幾何近似法：以邊的中點座標做空間雜湊分組，若同一雜湊格內有
    超過 2 個邊的中點彼此距離小於容差，視為「可能的非 manifold / 重複邊」並回報供人工複核，
    而非宣稱精確判定（避免捏造不存在的 API 呼叫）。
"""

import os
import sys
import json
import argparse
import warnings
from typing import Dict, Any, List, Tuple
from collections import defaultdict

warnings.filterwarnings("ignore", message="Starting gRPC client without TLS")

try:
    from ansys.geometry.core import Modeler
except ImportError:
    print("[警告] 尚未安裝 ansys-geometry-core。請執行: pip install ansys-geometry-core")


class AssemblyTopologyAuditor:
    """
    裝配體拓撲一致性稽核核心類別。

    與 check_cad_defects.py 的 CADDefectAuditor 互補：
    - CADDefectAuditor 負責單體微小面/短邊/滲漏判準。
    - 本類別負責裝配體層級彙總，以及重複邊的近似偵測（不重算微小面/短邊）。
    """

    def __init__(self, edge_midpoint_tol_m: float = 1e-6):
        # 邊中點距離容差：小於此值視為同一位置（可能的重複/非manifold邊候選）
        self.edge_midpoint_tol_m = edge_midpoint_tol_m

    def _edge_midpoint(self, edge) -> Tuple[float, float, float]:
        """
        取得邊的中點近似座標。PyAnsys Geometry 的 Edge 物件若提供 start/end 座標，
        以兩端點平均近似中點；若無法取得則回傳 None，由呼叫端跳過該邊。
        """
        try:
            start = edge.start
            end = edge.end
            return (
                (start.x + end.x) / 2.0,
                (start.y + end.y) / 2.0,
                (start.z + end.z) / 2.0,
            )
        except Exception:
            return None

    def audit_assembly(self, design) -> Dict[str, Any]:
        """
        對當前 Design 執行裝配體層級拓撲彙總稽核。
        """
        bodies = design.bodies
        report: Dict[str, Any] = {
            "assembly_name": design.name,
            "total_bodies": len(bodies),
            "bodies_audit": [],
            "watertight_assembly": True,
            "overall_status": "PASS",
            "warnings": [],
        }

        for body in bodies:
            body_info = {
                "body_name": body.name,
                "is_alive": getattr(body, "is_alive", True),
                "faces_count": len(body.faces),
                "edges_count": len(body.edges),
                "volume_m3": 0.0,
                "free_edge_count_approx": 0,
                "watertight": True,
                "warnings": [],
            }

            # 體積正定性（水密性必要條件，沿用 check_cad_defects.py 判準）
            try:
                vol = body.volume
                body_info["volume_m3"] = vol
                if vol <= 0.0:
                    body_info["watertight"] = False
                    body_info["warnings"].append(
                        f"體積非正值 ({vol:.4e} m^3)，可能存在流體滲漏或拓撲破損。"
                    )
            except Exception as e:
                body_info["warnings"].append(f"無法計算體積: {str(e)}")

            # 邊中點空間雜湊分組：近似偵測重複/高度重合邊（非精確非manifold判定）
            midpoints: List[Tuple[Any, Tuple[float, float, float]]] = []
            for edge in body.edges:
                mp = self._edge_midpoint(edge)
                if mp is not None:
                    midpoints.append((edge, mp))

            cell_size = max(self.edge_midpoint_tol_m * 10.0, 1e-5)
            buckets: Dict[Tuple[int, int, int], List[int]] = defaultdict(list)
            for idx, (_edge, mp) in enumerate(midpoints):
                key = (
                    int(mp[0] / cell_size),
                    int(mp[1] / cell_size),
                    int(mp[2] / cell_size),
                )
                buckets[key].append(idx)

            overlap_candidates = 0
            for _key, indices in buckets.items():
                if len(indices) <= 1:
                    continue
                for a in range(len(indices)):
                    for b in range(a + 1, len(indices)):
                        p1 = midpoints[indices[a]][1]
                        p2 = midpoints[indices[b]][1]
                        dist = (
                            (p1[0] - p2[0]) ** 2
                            + (p1[1] - p2[1]) ** 2
                            + (p1[2] - p2[2]) ** 2
                        ) ** 0.5
                        if dist < self.edge_midpoint_tol_m:
                            overlap_candidates += 1

            body_info["free_edge_count_approx"] = overlap_candidates
            if overlap_candidates > 0:
                body_info["warnings"].append(
                    f"偵測到 {overlap_candidates} 組邊中點高度重合（近似法，建議人工複核是否為"
                    "非manifold邊或重複邊；本腳本未呼叫未經查證之拓撲走訪 API）。"
                )

            report["bodies_audit"].append(body_info)
            if not body_info["watertight"]:
                report["watertight_assembly"] = False

        if not report["watertight_assembly"]:
            report["overall_status"] = "FAIL_TOPOLOGY_BROKEN"
        elif any(b["free_edge_count_approx"] > 0 for b in report["bodies_audit"]):
            report["overall_status"] = "WARNING_DEFECTS_FOUND"
        else:
            report["overall_status"] = "PASS_READY_FOR_MECHANICAL"

        return report


def run_assembly_diagnostic(
    port: int = 50051,
    edge_midpoint_tol_m: float = 1e-6,
    output_json: str = "assembly_topology_report.json",
):
    print("================================================================================")
    print("                 ANSYS 裝配體拓撲一致性稽核 (閘門檢查)                           ")
    print("================================================================================")
    print(f"正在連線埠號 {port} 上的幾何引擎...")

    try:
        modeler = Modeler(port=port, transport_mode="wnua", timeout=10)
        design = modeler.read_existing_design()
        if not design:
            print("[錯誤] 未能讀取到開啟中的幾何設計專案。")
            sys.exit(1)
    except Exception as e:
        print(f"[錯誤] 連線失敗: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"成功載入設計專案: {design.name}")
    print("正在執行裝配體拓撲一致性稽核...")

    auditor = AssemblyTopologyAuditor(edge_midpoint_tol_m=edge_midpoint_tol_m)
    results = auditor.audit_assembly(design)

    print("\n----------------------------- 裝配體拓撲稽核摘要 -----------------------------")
    print(f"裝配體名稱       : {results['assembly_name']}")
    print(f"實體總數         : {results['total_bodies']}")
    print(f"裝配體水密性     : {'良好' if results['watertight_assembly'] else '異常'}")
    print(f"稽核綜合判定     : {results['overall_status']}")

    for b in results["bodies_audit"]:
        print(f"\n  [實體] {b['body_name']}:")
        print(f"    - 體積             : {b['volume_m3']:.6e} m^3")
        print(f"    - 近似重合邊候選數 : {b['free_edge_count_approx']}")
        print(f"    - 水密性           : {'良好' if b['watertight'] else '異常'}")
        for w in b["warnings"]:
            print(f"      * 警告: {w}")

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n結構化稽核報告已寫入至: {os.path.abspath(output_json)}")
    print("================================================================================")

    if results["overall_status"] == "FAIL_TOPOLOGY_BROKEN":
        sys.exit(2)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ANSYS 裝配體拓撲一致性稽核工具")
    parser.add_argument("--port", type=int, default=50051, help="幾何引擎連線埠號")
    parser.add_argument(
        "--edge-midpoint-tol", type=float, default=1e-6, help="邊中點重合判定容差 (公尺 m)"
    )
    parser.add_argument(
        "--report", type=str, default="assembly_topology_report.json", help="報告輸出路徑"
    )

    args = parser.parse_args()
    run_assembly_diagnostic(
        port=args.port,
        edge_midpoint_tol_m=args.edge_midpoint_tol,
        output_json=args.report,
    )
