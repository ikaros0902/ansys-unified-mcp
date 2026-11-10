# -*- coding: utf-8 -*-
"""
Stage 2 單元測試：Meta-Router、扁平 Schema 驗證、DAMG 狀態機與 Phase 4 標量評估套件。

驗證範圍：
1. common_envelope.py：標準成功回傳信封、Pagination 分頁模型與 ASD-STE100 錯誤信封生成。
2. tool_annotations.py 與 domain_inputs.py：
   - 4-Key ToolAnnotations 結構校準 (readOnlyHint, destructiveHint, idempotentHint, openWorldHint)。
   - @validate_flat_pydantic 裝飾器：合法參數通過、型別自動轉換、缺漏必填項拋錯、傳入額外參數觸發 extra='forbid' 驗證錯誤。
   - domain_inputs.py 各物理域 Pydantic 模型驗證與 extra='forbid' 邊界防禦。
3. meta_router_tools.py：
   - ans_list_domain_tools：跨領域工具清單查詢、虛擬暫存工具暴露與 Schema 輸出。
   - ans_call_domain_tool：動態分發調用、虛擬暫存工具校驗、已註冊工具調用與錯誤處理 (TOOL_NOT_FOUND, INVALID_ARGUMENTS)。
4. damg_state_machine.py 與 @enforce_damg_precondition：
   - DAMG DAG 初始化與拓撲合法性。
   - 節點狀態轉換、前置依賴檢查。
   - 上游節點變更時，下游節點自動標記為 DIRTY 的 BFS 傳播。
   - 前置未滿足時，裝飾器 0 秒精準攔截並回傳 DAMG_PRECONDITION_VIOLATION。
5. run_mcp_evaluation.py 與 tests/evaluations/ansys_mcp_eval.xml：
   - 10 題確定性標量 XML 解析、比對邏輯 (Direct String Comparison, 數值, 大小寫, 符號剝離) 與報告生成。
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

# 1. 通用信封與分頁模型
from ansys_unified_mcp.schemas.common_envelope import (
    create_response_envelope,
    create_error_envelope,
    PaginationParams,
    PaginatedResponse,
    paginate_list,
)

# 2. 工具註記與扁平驗證裝飾器
from ansys_unified_mcp.schemas.tool_annotations import (
    ToolAnnotations,
    create_tool_annotations,
    validate_flat_pydantic,
)
from ansys_unified_mcp.schemas.domain_inputs import (
    StaticStructuralSolveInput,
    SteadyThermalSolveInput,
    MechanicalMeshInput,
    MechanicalBoundaryConditionInput,
    FluentBoundaryConditionInput,
    FluentSolverSettingsInput,
    HFSSAdaptiveMeshInput,
    MaxwellSetupInput,
    OpticsSimulationInput,
    GeometryCreateBlockInput,
    MultibodyJointInput,
)

# 3. Meta-Router 工具
from ansys_unified_mcp.tools.meta_router_tools import (
    ans_list_domain_tools,
    ans_call_domain_tool,
    normalize_domain,
    ensure_domain_loaded,
)
from ansys_unified_mcp.shared import mcp, aliased_tool

# 4. DAMG 狀態機與前置門禁裝飾器
from ansys_unified_mcp.core.damg.damg_state_machine import (
    DAMGStateMachine,
    NodeStatus,
    NodeDefinition,
    NodeState,
)
from ansys_unified_mcp.core.damg.damg_decorators import (
    enforce_damg_precondition,
    DAMG_ERROR_CODE_PRECONDITION_VIOLATION,
    build_precondition_violation_envelope,
)

# 5. Phase 4 標量評測套件
from tests.evaluations.run_mcp_evaluation import (
    load_evaluation_xml,
    compare_scalar,
    run_evaluation,
    clean_scalar_token,
    EvaluationSummary,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EVAL_XML = REPO_ROOT / "tests" / "evaluations" / "ansys_mcp_eval.xml"


# ============================================================================
# 1. 測試 common_envelope.py (標準回傳信封、分頁模型與 ASD-STE100 錯誤信封)
# ============================================================================

class TestCommonEnvelope:
    """測試通用信封與分頁契約。"""

    def test_create_response_envelope_basic(self):
        """驗證標準成功信封基礎欄位結構。"""
        payload = {"mesh_nodes": 1250, "elements": 800}
        env = create_response_envelope(
            data=payload,
            summary="網格生成成功",
            execution_time_ms=45.2,
        )
        assert env["ok"] is True
        assert env["status"] == "success"
        assert env["summary"] == "網格生成成功"
        assert env["data"] == payload
        assert env["execution_time_ms"] == 45.2
        assert "file_path" not in env
        assert "sha256" not in env

    def test_create_response_envelope_with_artifacts_and_extra(self):
        """驗證帶有檔案路徑、校驗雜湊與自訂中繼資料的成功信封。"""
        env = create_response_envelope(
            data={"modes": [10.5, 25.1, 44.8]},
            summary="模態求解完成",
            file_path="C:/tmp/result.rst",
            sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            execution_time_ms=120.0,
            solver_type="DirectSparse",
            license_checked_out="meba",
        )
        assert env["ok"] is True
        assert env["file_path"] == "C:/tmp/result.rst"
        assert env["sha256"].startswith("e3b0c442")
        assert env["solver_type"] == "DirectSparse"
        assert env["license_checked_out"] == "meba"

    def test_pagination_params_validation(self):
        """驗證分頁查詢參數之邊界值與 extra='forbid' 約束。"""
        # 合法參數
        p1 = PaginationParams(limit=50, offset=100)
        assert p1.limit == 50
        assert p1.offset == 100

        # 預設值
        p_def = PaginationParams()
        assert p_def.limit == 20
        assert p_def.offset == 0

        # 違反應約束 (limit < 1 或 offset < 0)
        with pytest.raises(ValidationError):
            PaginationParams(limit=0)

        with pytest.raises(ValidationError):
            PaginationParams(offset=-1)

        # 額外未宣告欄位應被 forbid 攔截
        with pytest.raises(ValidationError):
            PaginationParams(limit=20, offset=0, page_number=5)

    def test_paginate_list_slicing_and_metadata(self):
        """驗證自記憶體串列進行分頁切片與中繼資料計算。"""
        items = list(range(105))  # 105 個元素

        # 第 1 頁 (0~20)
        res1 = paginate_list(items, limit=20, offset=0)
        assert isinstance(res1, PaginatedResponse)
        assert len(res1.items) == 20
        assert res1.items[0] == 0
        assert res1.items[-1] == 19
        assert res1.total == 105
        assert res1.limit == 20
        assert res1.offset == 0
        assert res1.has_more is True

        # 末頁 (100~105)
        res_last = paginate_list(items, limit=20, offset=100)
        assert len(res_last.items) == 5
        assert res_last.items == [100, 101, 102, 103, 104]
        assert res_last.has_more is False

        # 超出範圍 (offset > total)
        res_overflow = paginate_list(items, limit=20, offset=200)
        assert len(res_overflow.items) == 0
        assert res_overflow.has_more is False

    def test_create_error_envelope_asd_ste100(self):
        """驗證 ASD-STE100 規範之標準錯誤信封與向後相容欄位。"""
        err_env = create_error_envelope(
            status="error",
            error_code="DAMG_PRECONDITION_VIOLATION",
            message="Geometry must be imported before generating mesh.",
            recovery_action="Execute geometry_create_block or geometry_import_file first.",
            target_node="STRUCTURAL_MESH_GENERATED",
        )
        assert err_env["ok"] is False
        assert err_env["status"] == "error"
        assert err_env["error_code"] == "DAMG_PRECONDITION_VIOLATION"
        assert err_env["message"] == "Geometry must be imported before generating mesh."
        # 確保向後相容：同時提供 error 字串與 suggested_actions 陣列
        assert err_env["error"] == err_env["message"]
        assert err_env["recovery_action"] == "Execute geometry_create_block or geometry_import_file first."
        assert err_env["suggested_actions"] == [err_env["recovery_action"]]
        assert err_env["target_node"] == "STRUCTURAL_MESH_GENERATED"


# ============================================================================
# 2. 測試 tool_annotations.py 與 domain_inputs.py
# ============================================================================

class TestToolAnnotationsAndDomainInputs:
    """測試 4-Key ToolAnnotations 與 @validate_flat_pydantic 裝飾器。"""

    def test_tool_annotations_4key_structure(self):
        """驗證 4-Key ToolAnnotations 結構、工廠方法與序列化。"""
        ann = ToolAnnotations.create(read_only=True, destructive=False, idempotent=True, open_world=False)
        assert ann.readOnlyHint is True
        assert ann.destructiveHint is False
        assert ann.idempotentHint is True
        assert ann.openWorldHint is False

        d = ann.to_dict()
        assert d == {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }

        # 測試預設工廠方法
        ro = ToolAnnotations.read_only()
        assert ro.readOnlyHint is True and ro.openWorldHint is False

        mut = ToolAnnotations.mutation(destructive=True, idempotent=False)
        assert mut.readOnlyHint is False and mut.destructiveHint is True and mut.openWorldHint is False

        ext = ToolAnnotations.external(destructive=False, idempotent=True)
        assert ext.readOnlyHint is False and ext.openWorldHint is True

        # 測試輔助函式 create_tool_annotations
        helper_dict = create_tool_annotations(read_only=True, idempotent=True)
        assert helper_dict["readOnlyHint"] is True
        assert helper_dict["idempotentHint"] is True

    def test_tool_annotations_forbid_extra(self):
        """驗證 ToolAnnotations 禁止額外欄位 (ConfigDict(extra='forbid'))。"""
        with pytest.raises(ValidationError):
            ToolAnnotations(readOnlyHint=True, unexpected_field="bad")

    def test_validate_flat_pydantic_success_and_coercion(self):
        """驗證 @validate_flat_pydantic 裝飾器正常通過與自動型別轉換。"""
        class SimpleInput(BaseModel):
            model_config = ConfigDict(extra="forbid")
            x: int = Field(..., gt=0)
            factor: float = Field(default=1.5, gt=0.0)
            tag: str = Field(default="test")

        @validate_flat_pydantic(SimpleInput)
        def my_tool(x: int, factor: float = 1.5, tag: str = "test") -> dict:
            return {"ok": True, "computed": x * factor, "tag": tag}

        # 1. 正常呼叫
        res1 = my_tool(x=10, factor=2.0, tag="calc")
        assert res1["ok"] is True
        assert res1["computed"] == 20.0
        assert res1["tag"] == "calc"

        # 2. 自動型別轉換 (字串 '5' -> int 5, 字串 '2.5' -> float 2.5)
        res2 = my_tool(x="5", factor="2.5")
        assert res2["ok"] is True
        assert res2["computed"] == 12.5

        # 3. 採用預設值
        res3 = my_tool(x=4)
        assert res3["ok"] is True
        assert res3["computed"] == 6.0
        assert res3["tag"] == "test"

    def test_validate_flat_pydantic_async_support(self):
        """驗證 @validate_flat_pydantic 支援非同步 (async) 函式。"""
        class AsyncInput(BaseModel):
            model_config = ConfigDict(extra="forbid")
            name: str
            count: int

        @validate_flat_pydantic(AsyncInput)
        async def my_async_tool(name: str, count: int) -> dict:
            await asyncio.sleep(0.001)
            return {"ok": True, "result": f"{name}_{count}"}

        res = asyncio.run(my_async_tool(name="test", count="3"))
        assert res["ok"] is True
        assert res["result"] == "test_3"

    def test_validate_flat_pydantic_missing_required_field(self):
        """驗證缺漏必填參數時，精準回傳 VALIDATION_ERROR 信封而不拋出例外。"""
        class RequiredInput(BaseModel):
            model_config = ConfigDict(extra="forbid")
            required_key: str
            value: float

        @validate_flat_pydantic(RequiredInput)
        def my_tool(required_key: str, value: float) -> dict:
            return {"ok": True}

        # 缺漏 required_key
        res = my_tool(value=10.0)
        assert res["ok"] is False
        assert res["status"] == "error"
        assert res["error_code"] == "VALIDATION_ERROR"
        assert "required_key" in res["error"]

    def test_validate_flat_pydantic_extra_forbidden(self):
        """驗證傳入未定義的未知參數時，觸發 extra='forbid' 驗證錯誤。"""
        class StrictInput(BaseModel):
            model_config = ConfigDict(extra="forbid")
            valid_param: str

        @validate_flat_pydantic(StrictInput)
        def my_tool(valid_param: str) -> dict:
            return {"ok": True}

        # 傳入未知參數 extra_junk
        res = my_tool(valid_param="ok", extra_junk=123)
        assert res["ok"] is False
        assert res["status"] == "error"
        assert res["error_code"] == "VALIDATION_ERROR"
        assert "extra_junk" in res["error"]
        assert "Extra inputs are not permitted" in res["error"]

    def test_domain_inputs_models_schema_integrity(self):
        """驗證 domain_inputs.py 中 9 大物理域 Pydantic 模型的型別約束。"""
        # 1. 結構力學模型驗證
        mech_valid = StaticStructuralSolveInput(
            analysis_name="Cantilever_Static",
            large_deflection=False,
            num_modes=6,
        )
        assert mech_valid.analysis_name == "Cantilever_Static"
        assert mech_valid.large_deflection is False

        with pytest.raises(ValidationError):
            # 額外未知欄位禁止
            StaticStructuralSolveInput(analysis_name="Test", unexpected_param=123)

        # 2. 流體邊界條件模型驗證
        cfd_bc = FluentBoundaryConditionInput(
            zone_name="inlet",
            bc_type="velocity_inlet",
            velocity_magnitude=5.0,
            temperature_k=300.0,
            turbulent_intensity=0.05,
        )
        assert cfd_bc.velocity_magnitude == 5.0

        with pytest.raises(ValidationError):
            # 速度超出合理範圍 (gt=0.0)
            FluentBoundaryConditionInput(zone_name="inlet", velocity_magnitude=-10.0)

        # 3. 高頻電磁 HFSS 模型驗證
        hfss = HFSSAdaptiveMeshInput(
            freq_ghz=2.45,
            max_delta_s=0.015,
            max_passes=12,
            min_passes=1,
            min_converged_passes=1,
        )
        assert hfss.freq_ghz == 2.45

        with pytest.raises(ValidationError):
            # 頻率不可 <= 0
            HFSSAdaptiveMeshInput(freq_ghz=-1.0)

        # 4. 光學模擬模型驗證
        optics = OpticsSimulationInput(
            source_type="CollimatedBeam",
            ray_count=1000000,
            wavelength_nm=550.0,
        )
        assert optics.ray_count == 1000000

        # 5. 幾何區塊模型驗證
        block = GeometryCreateBlockInput(
            x_length=100.0,
            y_length=50.0,
            z_length=20.0,
            name="ChassisPlate",
        )
        assert block.x_length == 100.0

        # 6. 多體關節模型驗證
        joint = MultibodyJointInput(
            joint_type="revolute",
            reference_body="Ground",
            mobile_body="ControlArm",
        )
        assert joint.joint_type == "revolute"


# ============================================================================
# 3. 測試 meta_router_tools.py (ans_list_domain_tools & ans_call_domain_tool)
# ============================================================================

class TestMetaRouterTools:
    """測試萬能路由 Meta-Tools 之工具發現與動態調用。"""

    def test_ans_list_domain_tools_structural(self):
        """驗證 ans_list_domain_tools 查詢 structural 領域，回傳完備之工具清單與 Schema。"""
        res = asyncio.run(ans_list_domain_tools(domain="structural"))
        assert res["ok"] is True
        assert res["status"] == "success"
        data = res["data"]
        assert data["domain"] == "structural"
        assert data["tool_count"] > 0
        tools = data["tools"]

        # 驗證每個工具包含必要欄位：name, description, annotations, parameters
        for tool_info in tools:
            assert "name" in tool_info
            assert "description" in tool_info
            assert "annotations" in tool_info
            assert "parameters" in tool_info

            # 驗證 annotations 包含 4-key 布林值
            ann = tool_info["annotations"]
            assert "readOnlyHint" in ann
            assert "destructiveHint" in ann
            assert "idempotentHint" in ann
            assert "openWorldHint" in ann

    def test_ans_list_domain_tools_virtual_staging(self):
        """驗證 ans_list_domain_tools 支援 electromagnetics 與 optics 虛擬暫存工具。"""
        em_res = asyncio.run(ans_list_domain_tools(domain="electromagnetics"))
        assert em_res["ok"] is True
        em_names = [t["name"] for t in em_res["data"]["tools"]]
        assert "hfss_setup_adaptive_mesh" in em_names
        assert "maxwell_setup_solver" in em_names

        opt_res = asyncio.run(ans_list_domain_tools(domain="optics"))
        assert opt_res["ok"] is True
        opt_names = [t["name"] for t in opt_res["data"]["tools"]]
        assert "optics_ray_trace_simulation" in opt_names

    def test_ans_list_domain_tools_unknown_domain_returns_empty(self):
        """驗證查詢不存在的未知領域時，優雅回傳空工具清單而不崩潰。"""
        res = asyncio.run(ans_list_domain_tools(domain="nonexistent_physics_domain"))
        assert res["ok"] is True
        assert res["data"]["tool_count"] == 0
        assert res["data"]["tools"] == []

    def test_ans_call_domain_tool_staging_success(self):
        """驗證 ans_call_domain_tool 動態調用虛擬暫存工具 (合法參數)。"""
        args = {
            "freq_ghz": 5.0,
            "max_delta_s": 0.02,
            "max_passes": 10,
        }
        res = asyncio.run(ans_call_domain_tool(
            domain="electromagnetics",
            tool_name="hfss_setup_adaptive_mesh",
            arguments=args,
        ))
        assert res["ok"] is True
        assert res["status"] == "success"
        assert res["data"]["status"] == "validated_staging"
        assert res["data"]["tool"] == "hfss_setup_adaptive_mesh"
        assert res["data"]["parameters"]["freq_ghz"] == 5.0

    def test_ans_call_domain_tool_staging_validation_error(self):
        """驗證 ans_call_domain_tool 調用虛擬暫存工具 (非法參數) 回傳 VALIDATION_ERROR。"""
        args = {
            "freq_ghz": -2.5,  # 違規負頻率
        }
        res = asyncio.run(ans_call_domain_tool(
            domain="electromagnetics",
            tool_name="hfss_setup_adaptive_mesh",
            arguments=args,
        ))
        assert res["ok"] is False
        assert res["status"] == "error"
        assert res["error_code"] == "VALIDATION_ERROR"
        assert "freq_ghz" in res["error"]

    def test_ans_call_domain_tool_tool_not_found(self):
        """驗證調用不存在的工具名稱時，回傳 TOOL_NOT_FOUND 錯誤信封。"""
        res = asyncio.run(ans_call_domain_tool(
            domain="structural",
            tool_name="totally_fake_solver_tool",
            arguments={},
        ))
        assert res["ok"] is False
        assert res["status"] == "error"
        assert res["error_code"] == "TOOL_NOT_FOUND"
        assert "totally_fake_solver_tool" in res["error"]
        assert "suggested_actions" in res

    def test_ans_call_domain_tool_registered_tool_execution(self):
        """驗證調用真實已註冊工具 (例如 check_ansys_installation)。"""
        res = asyncio.run(ans_call_domain_tool(
            domain="common",
            tool_name="check_ansys_installation",
            arguments={},
        ))
        # 即使本地無 ANSYS，工具亦應回傳格式合法之信封 dict
        assert isinstance(res, dict)
        assert "ok" in res


# ============================================================================
# 4. 測試 damg_state_machine.py 與 @enforce_damg_precondition
# ============================================================================

class TestDAMGStateMachineAndPrecondition:
    """測試 DAMG 會話級狀態機、Dirty 失效 BFS 傳播與前置門禁。"""

    def test_damg_dag_initialization_and_acyclic(self):
        """驗證 DAMGStateMachine 正確載入 resources/manifests/damg_rules.yaml 且為無環圖 (DAG)。"""
        sm = DAMGStateMachine(session_id="test_dag_init")
        assert len(sm.nodes) >= 15, "DAMG 規則應包含各領域主要因果節點"

        # 驗證重要結構節點存在
        assert "STRUCTURAL_GEOMETRY_READY" in sm.nodes
        assert "STRUCTURAL_MATERIALS_ASSIGNED" in sm.nodes
        assert "STRUCTURAL_MESH_GENERATED" in sm.nodes
        assert "STRUCTURAL_SOLUTION_SOLVED" in sm.nodes

        # 初始狀態全為 UNSATISFIED
        for nid in sm.nodes:
            assert sm.get_node_status(nid) == NodeStatus.UNSATISFIED

    def test_damg_prerequisite_check_and_satisfaction(self):
        """驗證節點前置依賴檢查邏輯。"""
        sm = DAMGStateMachine(session_id="test_prereq")

        # STRUCTURAL_MESH_GENERATED 需要前置依賴
        missing = sm.check_prerequisites("STRUCTURAL_MESH_GENERATED")
        assert len(missing) > 0

        # 將前置全部手動標記為 SATISFIED
        for prereq in missing:
            sm.mark_node_satisfied(prereq)

        # 再次檢查 STRUCTURAL_MESH_GENERATED 前置應已完全滿足
        rem_missing = sm.check_prerequisites("STRUCTURAL_MESH_GENERATED")
        assert len(rem_missing) == 0

    def test_damg_dirty_bfs_propagation(self):
        """驗證上游節點變更時，下游依賴節點沿著 DAG 自動被標記為 DIRTY 的 BFS 傳播。"""
        sm = DAMGStateMachine(session_id="test_dirty_bfs")

        # 1. 設置一條典型因果鏈並滿足
        sm.mark_node_satisfied("STRUCTURAL_CONTEXT_INITIALIZED")
        sm.mark_node_satisfied("STRUCTURAL_GEOMETRY_READY")
        sm.mark_node_satisfied("STRUCTURAL_MATERIALS_ASSIGNED")
        sm.mark_node_satisfied("STRUCTURAL_BOUNDARIES_APPLIED")
        sm.mark_node_satisfied("STRUCTURAL_MESH_GENERATED")
        sm.mark_node_satisfied("STRUCTURAL_SOLVER_CONFIGURED")
        sm.mark_node_satisfied("STRUCTURAL_SOLUTION_SOLVED")

        assert sm.get_node_status("STRUCTURAL_SOLUTION_SOLVED") == NodeStatus.SATISFIED

        # 2. 修改上游幾何 (調用 invalidate_node_and_downstream)
        invalidated = sm.invalidate_node_and_downstream("STRUCTURAL_GEOMETRY_READY")

        # 3. 驗證所有下游依賴節點均被傳播污染為 DIRTY
        assert "STRUCTURAL_GEOMETRY_READY" in invalidated
        assert "STRUCTURAL_MESH_GENERATED" in invalidated
        assert "STRUCTURAL_SOLUTION_SOLVED" in invalidated

        assert sm.get_node_status("STRUCTURAL_GEOMETRY_READY") == NodeStatus.DIRTY
        assert sm.get_node_status("STRUCTURAL_MESH_GENERATED") == NodeStatus.DIRTY
        assert sm.get_node_status("STRUCTURAL_SOLUTION_SOLVED") == NodeStatus.DIRTY

    def test_enforce_damg_precondition_blocks_unsatisfied(self):
        """驗證 @enforce_damg_precondition 在前置未滿足時 0 秒攔截並回傳 DAMG_PRECONDITION_VIOLATION。"""
        sm = DAMGStateMachine.get_instance(session_id="test_decorator_block")
        sm.reset_state()  # 確保清空為 UNSATISFIED

        execution_flag = {"called": False}

        @enforce_damg_precondition(
            required_nodes=["STRUCTURAL_GEOMETRY_READY", "STRUCTURAL_MATERIALS_ASSIGNED"],
            target_node="STRUCTURAL_MESH_GENERATED",
            state_machine=sm,
        )
        def generate_mesh_mock(session_id: str = "test_decorator_block") -> dict:
            execution_flag["called"] = True
            return {"ok": True, "mesh": "done"}

        # 執行前置未滿足的工具呼叫
        res = generate_mesh_mock(session_id="test_decorator_block")

        # 驗證被裝飾器完全攔截，底層業務函式未被執行
        assert execution_flag["called"] is False
        assert res["ok"] is False
        assert res["error_code"] == DAMG_ERROR_CODE_PRECONDITION_VIOLATION
        assert "DAMG precondition check failed" in res["error"] or "blocked" in res["error"].lower() or "missing" in res["error"].lower()
        assert "STRUCTURAL_GEOMETRY_READY" in res["missing_prerequisites"]
        assert "STRUCTURAL_MATERIALS_ASSIGNED" in res["missing_prerequisites"]
        assert "suggested_actions" in res
        assert len(res["suggested_actions"]) >= 2

    def test_enforce_damg_precondition_passes_when_satisfied(self):
        """驗證前置滿足後，裝飾器順暢放行並標記目標節點為 SATISFIED。"""
        sm = DAMGStateMachine.get_instance(session_id="test_decorator_pass")
        sm.reset_state()

        # 滿足前置
        sm.mark_node_satisfied("STRUCTURAL_GEOMETRY_READY")
        sm.mark_node_satisfied("STRUCTURAL_MATERIALS_ASSIGNED")

        @enforce_damg_precondition(
            required_nodes=["STRUCTURAL_GEOMETRY_READY", "STRUCTURAL_MATERIALS_ASSIGNED"],
            target_node="STRUCTURAL_MESH_GENERATED",
            state_machine=sm,
        )
        def generate_mesh_mock(session_id: str = "test_decorator_pass") -> dict:
            return {"ok": True, "elements": 5000}

        res = generate_mesh_mock(session_id="test_decorator_pass")
        assert res["ok"] is True
        assert res["elements"] == 5000

        # 目標節點自動標記為 SATISFIED
        assert sm.get_node_status("STRUCTURAL_MESH_GENERATED") == NodeStatus.SATISFIED

    def test_damg_session_isolation(self):
        """驗證不同會話 (session_id) 間的狀態機完全隔離、互不污染。"""
        sm_a = DAMGStateMachine.get_instance(session_id="session_alpha")
        sm_b = DAMGStateMachine.get_instance(session_id="session_beta")

        sm_a.reset_state()
        sm_b.reset_state()

        sm_a.mark_node_satisfied("STRUCTURAL_GEOMETRY_READY")

        assert sm_a.get_node_status("STRUCTURAL_GEOMETRY_READY") == NodeStatus.SATISFIED
        assert sm_b.get_node_status("STRUCTURAL_GEOMETRY_READY") == NodeStatus.UNSATISFIED


# ============================================================================
# 5. 測試 run_mcp_evaluation.py 與 tests/evaluations/ansys_mcp_eval.xml
# ============================================================================

class TestEvaluationSuiteAndScalarXML:
    """測試 mcp-builder Phase 4 確定性標量評測套件與 XML 規格。"""

    def test_ansys_mcp_eval_xml_parsing_and_10_questions(self):
        """驗證 XML 檔案存在且完整解析出 10 道跨物理域標量問答。"""
        assert EVAL_XML.exists(), f"找不到評估 XML 檔: {EVAL_XML}"
        suite_name, items = load_evaluation_xml(EVAL_XML)
        assert suite_name == "ansys_mcp_eval"
        assert len(items) == 10

        # 逐題比對第 1~10 題之領域與確定性標量答案
        expected = [
            ("1", "Structural", "2"),
            ("2", "Fluids", "coupled"),
            ("3", "EM", "1"),
            ("4", "Optics", "ZOSAPI.Editors.LDE"),
            ("5", "Thermal", "Celsius"),
            ("6", "Multibody", "2"),
            ("7", "System Coupling", "Heat Rate"),
            ("8", "Materials", "Tsai-Wu"),
            ("9", "Meshing", "SKEWNESS"),
            ("10", "Governance", "DAMG_PRECONDITION_VIOLATION"),
        ]
        for item, (exp_id, exp_domain, exp_ans) in zip(items, expected):
            assert item.id == exp_id
            assert item.domain == exp_domain
            assert item.expected == exp_ans
            assert len(item.question.strip()) > 10

    def test_compare_scalar_all_matching_modes(self):
        """驗證標量字串比對演算法：精確、反引號剝離、大小寫、數值等價與 strict 模式。"""
        # 1. 精確相等
        p, m, _ = compare_scalar("coupled", "coupled")
        assert p and m == "EXACT"

        # 2. Markdown 反引號與雙引號剝離
        p, m, _ = compare_scalar("coupled", "`coupled`")
        assert p and m == "EXACT"

        p, m, _ = compare_scalar("Tsai-Wu", "\"Tsai-Wu\"")
        assert p and m == "EXACT"

        # 3. 大小寫不敏感
        p, m, _ = compare_scalar("Celsius", "celsius", strict=False)
        assert p and m == "CASE_INSENSITIVE"

        # 4. strict=True 下嚴格大小寫
        p, m, _ = compare_scalar("Celsius", "celsius", strict=True)
        assert not p and m == "MISMATCH"

        # 5. 數值等價
        p, m, _ = compare_scalar("2", "2.0")
        assert p and m == "NUMERIC"

        # 6. 空白或缺失
        p, m, _ = compare_scalar("SKEWNESS", "")
        assert not p and m == "MISSING"

    def test_run_evaluation_self_test_100_percent_pass(self):
        """驗證黃金基準自檢 (self_test=True) 達到 100% 通過率且具備延遲度量。"""
        summary = run_evaluation(xml_path=EVAL_XML, self_test=True)
        assert isinstance(summary, EvaluationSummary)
        assert summary.total_questions == 10
        assert summary.passed_questions == 10
        assert summary.failed_questions == 0
        assert summary.pass_rate_pct == 100.0
        assert summary.average_latency_ms >= 0.0
        assert summary.total_duration_ms > 0.0

        # 驗證輸出字典可 JSON 序列化
        d = summary.to_dict()
        assert d["suite_name"] == "ansys_mcp_eval"
        assert d["pass_rate_pct"] == 100.0

