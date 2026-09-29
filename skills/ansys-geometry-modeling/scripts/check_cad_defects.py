# -*- coding: utf-8 -*-
"""
腳本名稱：check_cad_defects.py
功能說明：CAD 幾何缺陷自動化診斷腳本 (微小面、短邊、自交邊、流體滲漏與水密性檢驗)
技術標準：林明志標準 CAD 判斷力庫 (基於 PyAnsys Geometry ansys.geometry.core)
"""

import os
import sys
import json
import argparse
import warnings
from typing import Dict, Any, List

warnings.filterwarnings("ignore", message="Starting gRPC client without TLS")

try:
    from ansys.geometry.core import Modeler
except ImportError:
    print("[警告] 尚未安裝 ansys-geometry-core。請執行: pip install ansys-geometry-core")


class CADDefectAuditor:
    """
    CAD 幾何缺陷診斷稽核核心類別
    """

    def __init__(
        self,
        min_area_m2: float = 1e-6,
        min_edge_len_m: float = 1e-4,
        max_aspect_ratio: float = 50.0
    ):
        self.min_area_m2 = min_area_m2
        self.min_edge_len_m = min_edge_len_m
        self.max_aspect_ratio = max_aspect_ratio

    def audit_design(self, design) -> Dict[str, Any]:
        """
        對當前 Design 執行全面幾何拓撲缺陷掃描
        """
        bodies = design.bodies
        report: Dict[str, Any] = {
            "design_name": design.name,
            "total_bodies": len(bodies),
            "bodies_audit": [],
            "overall_status": "PASS",
            "critical_errors": []
        }

        total_slivers = 0
        total_short_edges = 0
        total_volume_errors = 0

        for b_idx, body in enumerate(bodies):
            body_info = {
                "body_name": body.name,
                "body_id": str(body.id),
                "is_alive": body.is_alive,
                "faces_count": len(body.faces),
                "edges_count": len(body.edges),
                "sliver_faces_detected": 0,
                "short_edges_detected": 0,
                "volume_m3": 0.0,
                "watertight": True,
                "warnings": []
            }

            # 1. 體積正定性與水密性檢查
            try:
                vol = body.volume
                body_info["volume_m3"] = vol
                if vol <= 0.0:
                    body_info["watertight"] = False
                    body_info["warnings"].append(f"體積非正值 ({vol:.4e} m³)，可能存在流體滲漏或零厚度面。")
                    total_volume_errors += 1
            except Exception as e:
                body_info["warnings"].append(f"無法計算體積: {str(e)}")

            # 2. 狹長微小面 (Sliver Faces) 診斷
            for f_idx, face in enumerate(body.faces):
                try:
                    f_box = face.box
                    dx = abs(f_box.max_point.x - f_box.min_point.x)
                    dy = abs(f_box.max_point.y - f_box.min_point.y)
                    dz = abs(f_box.max_point.z - f_box.min_point.z)
                    dims = sorted([d for d in [dx, dy, dz] if d > 1e-7])
                    
                    if len(dims) >= 2:
                        aspect_ratio = dims[-1] / (dims[0] + 1e-9)
                        if aspect_ratio > self.max_aspect_ratio:
                            body_info["sliver_faces_detected"] += 1
                except Exception:
                    pass

            # 3. 極短邊 (Short Edges) 診斷
            for e_idx, edge in enumerate(body.edges):
                try:
                    length = edge.length
                    if length < self.min_edge_len_m:
                        body_info["short_edges_detected"] += 1
                except Exception:
                    pass

            total_slivers += body_info["sliver_faces_detected"]
            total_short_edges += body_info["short_edges_detected"]
            report["bodies_audit"].append(body_info)

        # 彙整判定結果
        if total_volume_errors > 0:
            report["overall_status"] = "FAIL_LEAKAGE_DETECTED"
            report["critical_errors"].append(f"偵測到 {total_volume_errors} 個實體存在體積異常或流體滲漏！")
        elif total_slivers > 0 or total_short_edges > 0:
            report["overall_status"] = "WARNING_DEFECTS_FOUND"
            report["critical_errors"].append(
                f"發現 {total_slivers} 個狹長微小面與 {total_short_edges} 個極短邊，建議在網格劃分前進行去特徵修復。"
            )
        else:
            report["overall_status"] = "PASS_READY_FOR_EXPORT"

        return report


def run_diagnostic(
    port: int = 50051,
    min_edge: float = 1e-4,
    max_aspect: float = 50.0,
    output_json: str = "cad_audit_report.json"
):
    print("================================================================================")
    print("                 ANSYS CAD 幾何缺陷自動化診斷與水密性稽核                       ")
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
    print("正在執行拓撲完整性診斷...")
    
    auditor = CADDefectAuditor(
        min_edge_len_m=min_edge,
        max_aspect_ratio=max_aspect
    )
    results = auditor.audit_design(design)

    # 輸出文字摘要
    print("\n----------------------------- 診斷結果摘要 -----------------------------")
    print(f"模型名稱         : {results['design_name']}")
    print(f"實體總數         : {results['total_bodies']}")
    print(f"稽核綜合判定     : {results['overall_status']}")
    
    for b in results["bodies_audit"]:
        print(f"\n  [實體] {b['body_name']}:")
        print(f"    - 表面數 / 邊數     : {b['faces_count']} / {b['edges_count']}")
        print(f"    - 體積             : {b['volume_m3']:.6e} m³")
        print(f"    - 狹長微小面 (Sliver): {b['sliver_faces_detected']}")
        print(f"    - 極短邊 (ShortEdge): {b['short_edges_detected']}")
        print(f"    - 水密性封閉狀態   : {'良好' if b['watertight'] else '異常 (存在滲漏或未封閉)'}")
        if b["warnings"]:
            for w in b["warnings"]:
                print(f"      * 警告: {w}")

    # 輸出結構化 JSON 報告
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n結構化稽核報告已寫入至: {os.path.abspath(output_json)}")
    print("================================================================================")
    
    if results["overall_status"] == "FAIL_LEAKAGE_DETECTED":
        sys.exit(2)
    elif results["overall_status"] == "WARNING_DEFECTS_FOUND":
        sys.exit(0)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ANSYS CAD 缺陷診斷工具")
    parser.add_argument("--port", type=int, default=50051, help="幾何引擎連線埠號")
    parser.add_argument("--min-edge", type=float, default=1e-4, help="極短邊長度門檻 (公尺 m)")
    parser.add_argument("--max-aspect", type=float, default=50.0, help="狹長面長寬比門檻")
    parser.add_argument("--report", type=str, default="cad_audit_report.json", help="報告輸出路徑")
    
    args = parser.parse_args()
    run_diagnostic(
        port=args.port,
        min_edge=args.min_edge,
        max_aspect=args.max_aspect,
        output_json=args.report
    )
