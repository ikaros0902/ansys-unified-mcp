"""ANSYS Unified MCP - 8 階段確定性診斷漏斗與 Rubric 驗收引擎 (Staged Diagnostics).

對齊 CADWorld (arXiv:2609.16251) diagnostics.py 與 Markov AI cad-1000-hours rubrics.json，
提供 8 階段短路漏斗 (First-broken-stage wins) 與 F1–F11 標準化失敗歸因代碼，
並實作 FreeCAD FEM ↔ ANSYS Mechanical 結構樹語義映射與 ACT 腳本純 ASCII 門禁檢核。
"""

from __future__ import annotations

import csv
import io
import math
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ansys_unified_mcp.core.gatekeeper.fcstd_parser import validate_fcstd_archive, parse_fcstd_metadata
from ansys_unified_mcp.products.geometry._geom_shared import compute_continuous_geometry_metrics


class FailureClassEnum(str, Enum):
    """標準化失敗歸因代碼 (對齊 CADWorld Table 7 F1–F11 + PASS)。"""
    PASS = "PASS"
    F1_CLAIMED_DONE_WITHOUT_SAVING = "claimed_done_without_saving"
    F2_INCOMPLETE_NO_FILE = "incomplete_no_file"
    F3_CORRUPTED_ARTIFACT = "corrupted_artifact"
    F4_PRECONDITION_DESTROYED = "precondition_destroyed"
    F5_WRONG_DOCUMENT_STRUCTURE = "wrong_document_structure"
    F6_GEOMETRY_DISSIMILAR = "geometry_dissimilar"
    F7_GEOMETRY_SIMILAR_OUT_OF_TOLERANCE = "geometry_similar_out_of_tolerance"
    F8_SHAPE_CORRECT_PROCESS_WRONG = "shape_correct_process_wrong"
    F9_SOLVER_OR_RESULT_MISSING = "solver_or_result_missing"
    F10_RESULT_OUT_OF_TOLERANCE = "result_out_of_tolerance"
    F11_AGENT_DEATH_LOOP = "agent_death_loop"


# FreeCAD FEM ↔ ANSYS Mechanical 結構樹物件類型語義映射表
FREECAD_TO_ANSYS_TYPE_MAP: Dict[str, str] = {
    "Fem::FemAnalysis": "StaticStructuralAnalysis",
    "MaterialObject": "MaterialAssignment",
    "ConstraintFixed": "FixedSupport",
    "ConstraintForce": "ForceBoundaryCondition",
    "FemMeshShapeBaseObject": "MeshSizing",
    "FemSolverObject": "SolverSetting",
    "FemResultObject": "SolutionResults",
    "FemPostPipeline": "PostProcessingPipeline",
    "FemPostWarpVectorFilter": "DirectionalDeformation",
    "TextDocument": "SolverLog",
}

# FreeCAD FEM ↔ ANSYS Mechanical 顯示標籤語義映射表
FREECAD_TO_ANSYS_LABEL_MAP: Dict[str, str] = {
    "Analysis": "Static Structural",
    "MaterialSolid": "Material Assignment",
    "ConstraintFixed": "Fixed Support",
    "ConstraintForce": "Force",
    "FEMMeshGmsh": "Mesh",
    "SolverCcxTools": "Solution",
    "CCX_Results": "Equivalent Stress",
    "Pipeline_CCX_Results": "Total Deformation",
    "WarpVector": "Directional Deformation",
    "ccx_dat_file": "Solver Output",
}


def assert_ascii_host_script(script_code: str) -> None:
    """檢查 ANSYS Mechanical / SpaceClaim 宿主內嵌腳本是否全為純 ASCII 英文註解。

    因 IronPython 2.7 ANSI 編碼限制，嚴禁非 ASCII 字元（中文註解與全形符號），
    違規立即拋出 ValueError 並標註字元與索引。
    """
    for idx, char in enumerate(script_code):
        if ord(char) > 127:
            raise ValueError(
                f"Non-ASCII character {char!r} (code {ord(char)}) found at index {idx} in host script. "
                f"All internal comments in ANSYS embedded scripts must be strictly ASCII English."
            )


class StagedDiagnosticReport(BaseModel):
    """8 階段診斷綜合報告。"""
    task_id: str = Field(description="評測任務代號")
    success: bool = Field(description="是否全階段通過 (strict_score == 1.0)")
    failure_class: FailureClassEnum = Field(description="首個破壞階段之標準化失敗歸因")
    first_broken_stage: Optional[str] = Field(default=None, description="首個破壞階段名稱")
    stages: Dict[str, Any] = Field(default_factory=dict, description="各階段檢驗明細")
    continuous_metrics: Dict[str, Any] = Field(default_factory=dict, description="連續幾何指標")
    diagnosis: str = Field(description="診斷分析說明")
    prescription: Optional[str] = Field(default=None, description="自愈修復處方建議")


def _match_contains(haystack: List[str], needle: str) -> bool:
    """檢查清單中是否有任一元素包含 needle (不區分大小寫)。"""
    needle_lower = needle.lower()
    return any(needle_lower in h.lower() for h in haystack)


def evaluate_staged_rubric(
    artifact_state: Dict[str, Any],
    rubric: Dict[str, Any],
) -> StagedDiagnosticReport:
    """以 8 階段短路漏斗 (First-broken-stage wins) 嚴格評估工程產物。

    Args:
        artifact_state: 包含 agent 執行產物之狀態字典：
            - "task_id": str
            - "death_loop_triggered": bool (可選，Sentinel 回報)
            - "claimed_done": bool
            - "file_path": str | Path
            - "model_tree": dict (可選，包含 types, labels, objects)
            - "geometry": dict (可選，包含 total_volume, total_area, bbox, com)
            - "results": dict (可選，包含各物理量欄位之 min/max/mean)
            - "csv_content": str (可選，結果 CSV 文字內容)
        rubric: 評測標準 JSON (對齊 CADWorld expected.rules 與 cad-1000-hours rubrics.json)

    Returns:
        StagedDiagnosticReport: 結構化診斷報告
    """
    task_id = str(artifact_state.get("task_id", rubric.get("id", "task-001")))
    stages: Dict[str, Any] = {}

    # Stage 0: 檢查 Agent 是否陷入 Death-Loop
    if artifact_state.get("death_loop_triggered"):
        stages["death_loop"] = {"ok": False, "reason": "Agent repeated identical failed calls"}
        return StagedDiagnosticReport(
            task_id=task_id,
            success=False,
            failure_class=FailureClassEnum.F11_AGENT_DEATH_LOOP,
            first_broken_stage="death_loop",
            stages=stages,
            diagnosis="智能體調用工具陷入連續重複失敗或無效震盪死迴圈 (Death-Loop)。",
            prescription="停止在同一參數上重試，應依 ansys-error-catalog 排查前置條件或切換求解流程。",
        )
    stages["death_loop"] = {"ok": True}

    # Stage 1: completion & file_saved
    claimed_done = bool(artifact_state.get("claimed_done", False))
    file_path = artifact_state.get("file_path")
    file_exists = False
    if file_path:
        p = Path(file_path)
        file_exists = p.exists() and p.is_file()

    stages["completion"] = {"ok": claimed_done}
    stages["file_saved"] = {"ok": file_exists, "file_path": str(file_path) if file_path else None}

    if not file_exists:
        if claimed_done:
            return StagedDiagnosticReport(
                task_id=task_id,
                success=False,
                failure_class=FailureClassEnum.F1_CLAIMED_DONE_WITHOUT_SAVING,
                first_broken_stage="file_saved",
                stages=stages,
                diagnosis="智能體宣稱已完成任務 (claimed_done=True)，但指定產物檔案不存在於磁碟中。",
                prescription="檢查存檔路徑是否正確，並確保調用 save_project / geometry_export 且順利落盤。",
            )
        else:
            return StagedDiagnosticReport(
                task_id=task_id,
                success=False,
                failure_class=FailureClassEnum.F2_INCOMPLETE_NO_FILE,
                first_broken_stage="file_saved",
                stages=stages,
                diagnosis="任務未正常完成且未產出任何目標檔案 (incomplete / timeout)。",
                prescription="增加逾時預算或檢查初始模型載入是否有阻斷性錯誤。",
            )

    # Stage 2: file_valid
    p = Path(file_path)
    file_valid = True
    parse_detail: Dict[str, Any] = {}
    if p.suffix.lower() == ".fcstd":
        val_res = validate_fcstd_archive(p)
        file_valid = val_res["ok"]
        parse_detail = val_res
    elif p.stat().st_size == 0:
        file_valid = False
        parse_detail = {"error": "File size is 0 bytes"}

    stages["file_valid"] = {"ok": file_valid, "detail": parse_detail}
    if not file_valid:
        return StagedDiagnosticReport(
            task_id=task_id,
            success=False,
            failure_class=FailureClassEnum.F3_CORRUPTED_ARTIFACT,
            first_broken_stage="file_valid",
            stages=stages,
            diagnosis=f"產出檔案損毀或未通過完整性校驗: {parse_detail.get('error', 'invalid file')}",
            prescription="確保寫入行程已完全關閉且 flush，檔案非 0 byte 且 ZIP/XML 語法完整。",
        )

    # 若為 .FCStd 且 artifact_state 尚未提供 model_tree，自動流式解析提取
    model_tree = artifact_state.get("model_tree")
    if not model_tree and p.suffix.lower() == ".fcstd":
        fcstd_meta = parse_fcstd_metadata(p)
        if fcstd_meta["ok"]:
            model_tree = fcstd_meta

    # Stage 3: precondition (前置保護本體檢查)
    precondition_rules = rubric.get("precondition")
    if precondition_rules:
        protected_names = precondition_rules.get("protected_bodies", [])
        actual_names = [o.get("name") for o in (model_tree.get("objects", []) if model_tree else [])]
        missing_protected = [req for req in protected_names if req not in actual_names]
        if missing_protected:
            stages["precondition"] = {"ok": False, "missing": missing_protected}
            return StagedDiagnosticReport(
                task_id=task_id,
                success=False,
                failure_class=FailureClassEnum.F4_PRECONDITION_DESTROYED,
                first_broken_stage="precondition",
                stages=stages,
                diagnosis=f"前置模型中的關鍵保護本體遭意外刪除或破壞: {missing_protected}",
                prescription="在幾何前處理時，使用 _SIMPLIFIED_PROTECT 清單保護既有主機板與固定特徵。",
            )
    stages["precondition"] = {"ok": True}

    # Stage 4: structure (模型結構樹骨架檢核)
    struct_rules = rubric.get("structure", rubric.get("rules", {}))
    actual_types = model_tree.get("types", []) if model_tree else []
    actual_labels = model_tree.get("labels", []) if model_tree else []

    missing_types = []
    for req_t in struct_rules.get("required_type_contains", []):
        ansys_t = FREECAD_TO_ANSYS_TYPE_MAP.get(req_t, req_t)
        if not (_match_contains(actual_types, req_t) or _match_contains(actual_types, ansys_t)):
            missing_types.append(req_t)

    missing_labels = []
    for req_l in struct_rules.get("required_label_contains", []):
        ansys_l = FREECAD_TO_ANSYS_LABEL_MAP.get(req_l, req_l)
        if not (_match_contains(actual_labels, req_l) or _match_contains(actual_labels, ansys_l)):
            missing_labels.append(req_l)

    if missing_types or missing_labels:
        stages["structure"] = {"ok": False, "missing_types": missing_types, "missing_labels": missing_labels}
        return StagedDiagnosticReport(
            task_id=task_id,
            success=False,
            failure_class=FailureClassEnum.F5_WRONG_DOCUMENT_STRUCTURE,
            first_broken_stage="structure",
            stages=stages,
            diagnosis=f"結構樹骨架不符要求：缺少必要物件類型 {missing_types} 或標籤 {missing_labels}。",
            prescription="補齊模型樹缺少之材料指派、Fixed Support、Force 載荷或求解結果項。",
        )
    stages["structure"] = {"ok": True}

    # Stage 5: geometry (幾何連續指標與 IoU)
    geom_rules = rubric.get("geometry")
    continuous_metrics: Dict[str, Any] = {}
    if geom_rules and artifact_state.get("geometry"):
        act_geom = artifact_state["geometry"]
        continuous_metrics = compute_continuous_geometry_metrics(act_geom, geom_rules)
        similar = continuous_metrics.get("similar")
        if similar is False:
            stages["geometry"] = {"ok": False, "metrics": continuous_metrics}
            return StagedDiagnosticReport(
                task_id=task_id,
                success=False,
                failure_class=FailureClassEnum.F6_GEOMETRY_DISSIMILAR,
                first_broken_stage="geometry",
                stages=stages,
                continuous_metrics=continuous_metrics,
                diagnosis="產出幾何外型、體積或包圍盒與目標幾何嚴重不吻合 (similar=False)。",
                prescription="檢查建模草圖尺寸、拉伸方向及單位制（公尺 m 與毫米 mm 是否混淆）。",
            )
        # 若形狀相似但未達嚴格公差
        strict_geom_pass = True
        if "volume" in continuous_metrics:
            strict_geom_pass = strict_geom_pass and (continuous_metrics["volume"]["relative_error"] <= 0.05)
        if "bbox_iou" in continuous_metrics:
            strict_geom_pass = strict_geom_pass and (continuous_metrics["bbox_iou"] >= 0.85)

        if not strict_geom_pass:
            stages["geometry"] = {"ok": False, "metrics": continuous_metrics}
            return StagedDiagnosticReport(
                task_id=task_id,
                success=False,
                failure_class=FailureClassEnum.F7_GEOMETRY_SIMILAR_OUT_OF_TOLERANCE,
                first_broken_stage="geometry",
                stages=stages,
                continuous_metrics=continuous_metrics,
                diagnosis="幾何拓撲特徵相似，但尺寸、體積或 IoU 超出 ±5% 嚴格工程容差。",
                prescription="微調特徵尺寸參數，使其精確收斂於目標公差範圍內。",
            )
    stages["geometry"] = {"ok": True, "metrics": continuous_metrics}

    # Stage 6: process (材料、約束與網格製程設定)
    process_rules = rubric.get("process")
    if process_rules:
        # 檢驗材料名稱
        if "material" in process_rules and model_tree:
            req_mat = str(process_rules["material"]).lower()
            mats = [str(m.get("properties", {}).get("Material", m.get("label", ""))).lower() for m in model_tree.get("materials", [])]
            if not any(req_mat in m for m in mats):
                stages["process"] = {"ok": False, "missing_material": req_mat}
                return StagedDiagnosticReport(
                    task_id=task_id,
                    success=False,
                    failure_class=FailureClassEnum.F8_SHAPE_CORRECT_PROCESS_WRONG,
                    first_broken_stage="process",
                    stages=stages,
                    diagnosis=f"幾何構造正確，但材料指派錯誤（期望包含 {req_mat}）。",
                    prescription="調用 mechanical_assign_material 將材料正確指派至主體實體。",
                )
    stages["process"] = {"ok": True}

    # Stage 7: strict (最終數值結果驗收 ±5% 容差)
    strict_rules = rubric.get("strict", rubric.get("columns", {}))
    results_data = artifact_state.get("results", {})

    # 若有傳入 CSV 內容但無 results dict，嘗試解析 CSV
    if not results_data and artifact_state.get("csv_content"):
        try:
            reader = csv.DictReader(io.StringIO(artifact_state["csv_content"]))
            rows = list(reader)
            if rows:
                col_data: Dict[str, List[float]] = {}
                for r in rows:
                    for k, v in r.items():
                        try:
                            val = float(v)
                            col_data.setdefault(k, []).append(val)
                        except (ValueError, TypeError):
                            pass
                results_data = {
                    col: {"min": min(vals), "max": max(vals), "mean": sum(vals) / len(vals)}
                    for col, vals in col_data.items() if vals
                }
        except Exception:
            pass

    if strict_rules:
        if not results_data:
            stages["strict"] = {"ok": False, "reason": "No numerical results or CSV available"}
            return StagedDiagnosticReport(
                task_id=task_id,
                success=False,
                failure_class=FailureClassEnum.F9_SOLVER_OR_RESULT_MISSING,
                first_broken_stage="strict",
                stages=stages,
                diagnosis="模型設定完整，但未產出任何求解結果場數據或 CSV 報告。",
                prescription="確保調用 mechanical_solve_analysis 並以 DPF 提取等效應力與總變形量。",
            )

        rel_tol = float(rubric.get("relative_tolerance", 0.05))
        mismatches = []
        for col_name, expectations in strict_rules.items():
            # 尋找匹配欄位名稱（支援別名如 'Equivalent Stress' ↔ 'von Mises Stress'）
            matched_col = None
            for act_col in results_data.keys():
                if col_name.lower() in act_col.lower() or act_col.lower() in col_name.lower():
                    matched_col = act_col
                    break
                # 別名映射
                if "von mises" in col_name.lower() and "equivalent" in act_col.lower():
                    matched_col = act_col
                    break
                if "displacement" in col_name.lower() and "deformation" in act_col.lower():
                    matched_col = act_col
                    break

            if not matched_col:
                mismatches.append(f"Column '{col_name}' missing in results")
                continue

            summary = results_data[matched_col]
            for metric_type, rule_spec in expectations.items():
                expected_val = float(rule_spec.get("expected", rule_spec) if isinstance(rule_spec, dict) else rule_spec)
                actual_val = summary.get(metric_type)
                if actual_val is None:
                    mismatches.append(f"{col_name}.{metric_type} unavailable")
                    continue
                diff = abs(actual_val - expected_val)
                allowed = max(1e-9, abs(expected_val) * rel_tol)
                if diff > allowed:
                    err_pct = (diff / abs(expected_val)) * 100.0 if abs(expected_val) > 0 else 0.0
                    mismatches.append(f"{col_name}.{metric_type}: actual={actual_val:.4e}, expected={expected_val:.4e} (error={err_pct:.2f}% > {rel_tol*100:.1f}%)")

        if mismatches:
            stages["strict"] = {"ok": False, "mismatches": mismatches}
            return StagedDiagnosticReport(
                task_id=task_id,
                success=False,
                failure_class=FailureClassEnum.F10_RESULT_OUT_OF_TOLERANCE,
                first_broken_stage="strict",
                stages=stages,
                diagnosis=f"求解數值計算完成，但結果超出 ±{rel_tol*100:.1f}% 容差範圍: {'; '.join(mismatches)}",
                prescription="檢查網格劃分細緻度是否收斂、材料剛度彈性模數是否正確，或邊界支承面定義是否偏離。",
            )

    stages["strict"] = {"ok": True}
    return StagedDiagnosticReport(
        task_id=task_id,
        success=True,
        failure_class=FailureClassEnum.PASS,
        first_broken_stage=None,
        stages=stages,
        continuous_metrics=continuous_metrics,
        diagnosis="8 階段診斷漏斗全數通過 (PASS)：檔案完整、結構合規、幾何 IoU 達標、求解數值在 ±5% 容差內。",
        prescription=None,
    )
