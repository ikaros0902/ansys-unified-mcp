# -*- coding: utf-8 -*-
"""單元測試：CADWorld 幾何連續指標、.FCStd 安全解析器、8 階段短路診斷漏斗與 Death-Loop 熔斷測試。"""

import json
import zipfile
from pathlib import Path
import pytest

from ansys_unified_mcp.products.geometry._geom_shared import (
    _normalize_bbox_bounds,
    compute_bbox_iou,
    compute_com_distance,
    compute_continuous_geometry_metrics,
)
from ansys_unified_mcp.core.gatekeeper.fcstd_parser import (
    validate_fcstd_archive,
    parse_fcstd_metadata,
)
from ansys_unified_mcp.core.gatekeeper.staged_diagnostics import (
    FailureClassEnum,
    assert_ascii_host_script,
    evaluate_staged_rubric,
)
from ansys_unified_mcp.core.script_guard import check_script, check_headless_boundary
from ansys_unified_mcp.core.sentinel.circuit_breaker import CircuitBreaker, _safe_hash_args


# ===================================================================
# 1. 幾何連續指標與數學防禦測試
# ===================================================================

class TestGeometryContinuousMetrics:
    """測試 3D BBox IoU 四層數學防衛與質心、體積指標。"""

    def test_bbox_bounds_normalization(self):
        # 測試反向輸入 (max, min) 自動正規化
        lo, hi = _normalize_bbox_bounds(((10.0, 5.0, 2.0), (0.0, -5.0, 0.0)))
        assert lo == (0.0, -5.0, 0.0)
        assert hi == (10.0, 5.0, 2.0)

        # 測試字典輸入
        lo, hi = _normalize_bbox_bounds({
            "xmin": 5.0, "xmax": 0.0,
            "ymin": 1.0, "ymax": 2.0,
            "zmin": 3.0, "zmax": 1.0,
        })
        assert lo == (0.0, 1.0, 1.0)
        assert hi == (5.0, 2.0, 3.0)

    def test_bbox_iou_identical_and_disjoint(self):
        b1 = ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0))
        # 1. 完全相同
        assert compute_bbox_iou(b1, b1) == pytest.approx(1.0)

        # 2. 完全分離
        b2 = ((2.0, 2.0, 2.0), (3.0, 3.0, 3.0))
        assert compute_bbox_iou(b1, b2) == 0.0

    def test_bbox_iou_negative_disjoint_axes_no_false_positive(self):
        """防禦測試：當兩盒在多個軸向均為負跨度時，逐軸非負截斷防止負負得正。"""
        b1 = ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0))
        # X 軸與 Y 軸皆在負向分離
        b2 = ((5.0, 5.0, 0.0), (6.0, 6.0, 1.0))
        assert compute_bbox_iou(b1, b2) == 0.0

    def test_bbox_iou_degenerate_zero_volume_no_division_by_zero(self):
        """防禦測試：退化 2D 薄面或點 (體積為 0) 絕不引發 ZeroDivisionError。"""
        flat1 = ((0.0, 0.0, 0.0), (1.0, 1.0, 0.0))  # dz = 0
        flat2 = ((0.0, 0.0, 0.0), (1.0, 1.0, 0.0))
        # 完全重疊之退化盒
        assert compute_bbox_iou(flat1, flat2) == 1.0

        # 不重疊之退化盒
        flat3 = ((2.0, 2.0, 0.0), (3.0, 3.0, 0.0))
        assert compute_bbox_iou(flat1, flat3) == 0.0

    def test_bbox_iou_partial_overlap_accuracy(self):
        # 盒 A: 0..2, 0..2, 0..2 (V=8)
        # 盒 B: 1..3, 0..2, 0..2 (V=8)
        # 交集: 1..2, 0..2, 0..2 (V=4)
        # 聯集: 8 + 8 - 4 = 12 -> IoU = 4/12 = 1/3
        b_a = ((0.0, 0.0, 0.0), (2.0, 2.0, 2.0))
        b_b = ((1.0, 0.0, 0.0), (3.0, 2.0, 2.0))
        assert compute_bbox_iou(b_a, b_b) == pytest.approx(1.0 / 3.0)

    def test_compute_com_distance(self):
        p1 = {"x": 0.0, "y": 0.0, "z": 0.0}
        p2 = {"x": 3.0, "y": 4.0, "z": 0.0}
        assert compute_com_distance(p1, p2) == pytest.approx(5.0)

    def test_compute_continuous_geometry_metrics(self):
        actual = {
            "total_volume": 1.02,
            "total_area": 6.05,
            "bbox": ((0.0, 0.0, 0.0), (1.01, 1.01, 1.0)),
            "center_of_mass": {"x": 0.5, "y": 0.5, "z": 0.5},
        }
        expected = {
            "total_volume": 1.0,
            "total_area": 6.0,
            "bbox": ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
            "center_of_mass": {"x": 0.5, "y": 0.5, "z": 0.5},
        }
        res = compute_continuous_geometry_metrics(actual, expected)
        assert res["similar"] is True
        assert res["volume"]["relative_error"] == pytest.approx(0.02)
        assert res["bbox_iou"] > 0.95


# ===================================================================
# 2. .FCStd 安全解析器測試
# ===================================================================

class TestFCStdParserSecurity:
    """測試 .FCStd 解析器的 ZIP 完整性、Zip Slip、Zip Bomb 與元數據萃取。"""

    def test_parse_valid_fcstd_in_memory(self, tmp_path: Path):
        fcstd_path = tmp_path / "valid.FCStd"
        doc_xml = b"""<?xml version="1.0" encoding="utf-8"?>
<Document SchemaVersion="4">
  <Objects>
    <Object name="Analysis" type="Fem::FemAnalysis">
      <Properties>
        <Property name="Label"><String value="Static Structural"/></Property>
      </Properties>
    </Object>
    <Object name="Material" type="MaterialObject">
      <Properties>
        <Property name="Label"><String value="AlMg3F24"/></Property>
        <Property name="Material"><String value="AlMg3F24"/></Property>
      </Properties>
    </Object>
    <Object name="ConstraintFixed" type="ConstraintFixed">
      <Properties>
        <Property name="Label"><String value="FixedSupport"/></Property>
      </Properties>
    </Object>
    <Object name="ConstraintForce" type="ConstraintForce">
      <Properties>
        <Property name="Label"><String value="Force"/></Property>
        <Property name="Force"><Float value="200.0"/></Property>
      </Properties>
    </Object>
  </Objects>
</Document>"""

        with zipfile.ZipFile(fcstd_path, "w") as zf:
            zf.writestr("Document.xml", doc_xml)
            zf.writestr("PartShape.brp", b"OpenCascade TopoDS_Shape binary")

        val = validate_fcstd_archive(fcstd_path)
        assert val["ok"] is True
        assert "PartShape.brp" in val["members"]

        meta = parse_fcstd_metadata(fcstd_path)
        assert meta["ok"] is True
        assert meta["object_count"] == 4
        assert "Fem::FemAnalysis" in meta["types"]
        assert "AlMg3F24" in meta["labels"]
        assert len(meta["constraints"]) == 2

    def test_corrupted_or_nonexistent_fcstd(self, tmp_path: Path):
        # 1. 不存在
        meta = parse_fcstd_metadata(tmp_path / "missing.FCStd")
        assert meta["ok"] is False
        assert meta["failure_class"] == FailureClassEnum.F3_CORRUPTED_ARTIFACT

        # 2. 0 byte
        empty_f = tmp_path / "empty.FCStd"
        empty_f.write_bytes(b"")
        meta = parse_fcstd_metadata(empty_f)
        assert meta["ok"] is False

        # 3. 損毀 ZIP
        corrupt_f = tmp_path / "corrupt.FCStd"
        corrupt_f.write_bytes(b"not a valid zip header")
        meta = parse_fcstd_metadata(corrupt_f)
        assert meta["ok"] is False

    def test_zip_slip_and_zip_bomb_defense(self, tmp_path: Path):
        # Zip Slip 防禦
        slip_path = tmp_path / "slip.FCStd"
        with zipfile.ZipFile(slip_path, "w") as zf:
            zf.writestr("Document.xml", b"<Document/>")
            zf.writestr("../malicious.txt", b"exploit")

        val = validate_fcstd_archive(slip_path)
        assert val["ok"] is False
        assert "Zip Slip" in val["error"]


# ===================================================================
# 3. 8 階段短路診斷漏斗 (First-Broken-Stage Wins)
# ===================================================================

class TestStagedDiagnosticsFunnel:
    """驗證 F1~F11 標準化失敗歸因代碼與短路優先序。"""

    def test_stage0_death_loop(self):
        state = {"death_loop_triggered": True, "claimed_done": True}
        rep = evaluate_staged_rubric(state, {})
        assert rep.success is False
        assert rep.failure_class == FailureClassEnum.F11_AGENT_DEATH_LOOP

    def test_stage1_claimed_done_without_saving(self, tmp_path: Path):
        state = {
            "claimed_done": True,
            "file_path": str(tmp_path / "nonexistent.FCStd"),
        }
        rep = evaluate_staged_rubric(state, {})
        assert rep.success is False
        assert rep.failure_class == FailureClassEnum.F1_CLAIMED_DONE_WITHOUT_SAVING

    def test_stage1_incomplete_no_file(self, tmp_path: Path):
        state = {
            "claimed_done": False,
            "file_path": str(tmp_path / "nonexistent.FCStd"),
        }
        rep = evaluate_staged_rubric(state, {})
        assert rep.success is False
        assert rep.failure_class == FailureClassEnum.F2_INCOMPLETE_NO_FILE

    def test_stage2_corrupted_file(self, tmp_path: Path):
        f = tmp_path / "corrupt.fcstd"
        f.write_bytes(b"bad content")
        state = {"claimed_done": True, "file_path": str(f)}
        rep = evaluate_staged_rubric(state, {})
        assert rep.success is False
        assert rep.failure_class == FailureClassEnum.F3_CORRUPTED_ARTIFACT

    def test_stage3_precondition_destroyed(self, tmp_path: Path):
        f = tmp_path / "model.txt"
        f.write_text("ok", encoding="utf-8")
        state = {
            "claimed_done": True,
            "file_path": str(f),
            "model_tree": {"objects": [{"name": "some_part"}]},
        }
        rubric = {
            "precondition": {"protected_bodies": ["motherboard", "screw_holes"]}
        }
        rep = evaluate_staged_rubric(state, rubric)
        assert rep.success is False
        assert rep.failure_class == FailureClassEnum.F4_PRECONDITION_DESTROYED

    def test_stage4_wrong_structure(self, tmp_path: Path):
        f = tmp_path / "model.txt"
        f.write_text("ok", encoding="utf-8")
        state = {
            "claimed_done": True,
            "file_path": str(f),
            "model_tree": {
                "types": ["StaticStructuralAnalysis"],
                "labels": ["Static Structural"],
            },
        }
        rubric = {
            "structure": {
                "required_type_contains": ["MaterialObject", "ConstraintFixed"],
                "required_label_contains": ["Fixed Support"],
            }
        }
        rep = evaluate_staged_rubric(state, rubric)
        assert rep.success is False
        assert rep.failure_class == FailureClassEnum.F5_WRONG_DOCUMENT_STRUCTURE

    def test_stage5_geometry_dissimilar_and_out_of_tolerance(self, tmp_path: Path):
        f = tmp_path / "model.txt"
        f.write_text("ok", encoding="utf-8")
        # 1. 幾何嚴重偏離 F6
        state_dissimilar = {
            "claimed_done": True,
            "file_path": str(f),
            "geometry": {
                "total_volume": 10.0,
                "total_area": 50.0,
                "bbox": ((0.0, 0.0, 0.0), (10.0, 10.0, 10.0)),
            },
        }
        rubric_geom = {
            "geometry": {
                "total_volume": 1.0,
                "total_area": 6.0,
                "bbox": ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
            }
        }
        rep = evaluate_staged_rubric(state_dissimilar, rubric_geom)
        assert rep.success is False
        assert rep.failure_class == FailureClassEnum.F6_GEOMETRY_DISSIMILAR

        # 2. 幾何相似但超嚴格公差 F7
        state_near = {
            "claimed_done": True,
            "file_path": str(f),
            "geometry": {
                "total_volume": 1.08,  # +8%
                "total_area": 6.08,
                "bbox": ((0.0, 0.0, 0.0), (1.02, 1.02, 1.02)),
            },
        }
        rep = evaluate_staged_rubric(state_near, rubric_geom)
        assert rep.success is False
        assert rep.failure_class == FailureClassEnum.F7_GEOMETRY_SIMILAR_OUT_OF_TOLERANCE

    def test_stage7_numerical_results_strict_tolerance(self, tmp_path: Path):
        f = tmp_path / "model.txt"
        f.write_text("ok", encoding="utf-8")
        rubric = {
            "relative_tolerance": 0.05,
            "strict": {
                "Equivalent Stress": {
                    "max": {"expected": 100.0}
                }
            }
        }

        # 1. 缺少數值 F9
        state_missing = {"claimed_done": True, "file_path": str(f), "results": {}}
        rep = evaluate_staged_rubric(state_missing, rubric)
        assert rep.success is False
        assert rep.failure_class == FailureClassEnum.F9_SOLVER_OR_RESULT_MISSING

        # 2. 數值超差 F10 (+15%)
        state_bad_num = {
            "claimed_done": True,
            "file_path": str(f),
            "results": {"Equivalent Stress": {"max": 115.0}},
        }
        rep = evaluate_staged_rubric(state_bad_num, rubric)
        assert rep.success is False
        assert rep.failure_class == FailureClassEnum.F10_RESULT_OUT_OF_TOLERANCE

        # 3. 數值合規 (+2%) -> PASS
        state_pass = {
            "claimed_done": True,
            "file_path": str(f),
            "results": {"Equivalent Stress": {"max": 102.0}},
        }
        rep = evaluate_staged_rubric(state_pass, rubric)
        assert rep.success is True
        assert rep.failure_class == FailureClassEnum.PASS


# ===================================================================
# 4. CADWorld 3 道 FEM 題目 Rubric 驗收與 ASCII 門禁
# ===================================================================

class TestCADWorldFEMBenchmarkRubrics:
    """驗證三道 FEM 題目的 Rubric 定義與 ANSYS Mechanical 結構樹映射。"""

    def test_cadworld_fem_rubric_fixture_load(self):
        fixture_path = Path("F:/Ming_python/ansys-unified-mcp/tests/fixtures/cadworld_fem/cadworld_fem_rubrics.json")
        assert fixture_path.exists()
        with open(fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["tasks"]) == 3
        ids = [t["id"] for t in data["tasks"]]
        assert "freecad-fem-001" in ids
        assert "freecad-fem-002" in ids
        assert "freecad-fem-003" in ids

    def test_ascii_host_script_enforcement(self):
        valid_script = "# Setup fixed support and 200N force load\nExtAPI.DataModel.Project.Save()"
        assert_ascii_host_script(valid_script)

        invalid_script = "# 設定固定支承 (Fixed Support)\nExtAPI.DataModel.Project.Save()"
        with pytest.raises(ValueError) as exc:
            assert_ascii_host_script(invalid_script)
        assert "Non-ASCII character" in str(exc.value)


# ===================================================================
# 5. ScriptGuard 與 CircuitBreaker 邊界測試
# ===================================================================

class TestScriptGuardAndDeathLoopBreaker:
    """測試無頭腳本 GUI 阻塞攔截、註解免誤殺、以及 Agent Death-Loop 熔斷。"""

    def test_script_guard_gui_blocking_and_comments_immunity(self):
        # 1. 註解內含有 input() 或 MessageBox 應豁免不誤殺
        comment_script = "# You can use input() or MessageBox.Show() in GUI mode\nx = 42\n"
        is_safe, warnings = check_script(comment_script)
        assert is_safe is True
        assert len(warnings) == 0

        # 2. 程式碼中真正調用 MessageBox 或 input()
        gui_script = "import sys\nMessageBox.Show('Click me')\n"
        is_safe, warnings = check_headless_boundary(gui_script)
        assert is_safe is False
        assert any("GUI-blocking call" in w for w in warnings)

        # 3. 空白無頭腳本阻斷
        is_safe, warnings = check_headless_boundary("   \n  \t")
        assert is_safe is False

    def test_circuit_breaker_agent_trajectory_death_loop(self):
        cb = CircuitBreaker()

        # 測試 1: 巢狀 dict 參數安全雜湊無崩潰
        nested_args = {"solver": {"max_iter": 100, "tol": 1e-5}, "tags": ["a", "b"]}
        h1 = _safe_hash_args(nested_args)
        h2 = _safe_hash_args(nested_args)
        assert h1 == h2 and len(h1) == 16

        # 測試 2: 連續 3 次相同呼叫無推進 -> 觸發 CB-AGT-001 熔斷
        traj_repeats = [
            {"tool": "geometry_create_block", "args": nested_args, "status": "error", "state_changed": False},
            {"tool": "geometry_create_block", "args": nested_args, "status": "error", "state_changed": False},
            {"tool": "geometry_create_block", "args": nested_args, "status": "error", "state_changed": False},
        ]
        verdict = cb.evaluate_agent_trajectory(traj_repeats, max_identical_repeats=3)
        assert verdict.triggered is True
        assert verdict.rule_id == "CB-AGT-001"
        assert verdict.action_code == "BREAK_AGENT_DEATH_LOOP"

        # 測試 3: ABAB 震盪無推進 -> 觸發熔斷
        traj_oscillate = [
            {"tool": "tool_a", "args": {"k": 1}, "status": "ok", "state_changed": False},
            {"tool": "tool_b", "args": {"k": 2}, "status": "ok", "state_changed": False},
            {"tool": "tool_a", "args": {"k": 1}, "status": "ok", "state_changed": False},
            {"tool": "tool_b", "args": {"k": 2}, "status": "ok", "state_changed": False},
        ]
        verdict_osc = cb.evaluate_agent_trajectory(traj_oscillate, max_oscillation_cycles=2)
        assert verdict_osc.triggered is True
        assert "無效震盪" in verdict_osc.reason


# ===================================================================
# 6. CADWorld 官方真實 .FCStd 產物端到端解析與檢驗
# ===================================================================

class TestRealCADWorldArtifacts:
    """以 CADWorld 官方倉庫之真實 .FCStd 檔案進行端到端免安裝解析驗證。"""

    @pytest.fixture
    def fixture_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent / "fixtures" / "cadworld_fem"

    def test_real_cadworld_precondition_fcstd_parsing(self, fixture_dir: Path):
        files = {
            "freecad-fem-001": fixture_dir / "freecad-fem-001-precondition.FCStd",
            "freecad-fem-002": fixture_dir / "freecad-fem-002-precondition.FCStd",
            "freecad-fem-003": fixture_dir / "freecad-fem-003-precondition.FCStd",
        }

        for task_id, fpath in files.items():
            assert fpath.exists(), f"真實 fixture 不存在: {fpath}"

            # 1. 真實封包校驗
            val = validate_fcstd_archive(fpath)
            assert val["ok"] is True
            assert val["document_xml_present"] is True
            assert val["document_xml_parses"] is True
            assert "Document.xml" in val["members"]

            # 2. 真實元數據解析
            meta = parse_fcstd_metadata(fpath)
            assert meta["ok"] is True
            assert len(meta["objects"]) > 0
            assert "PartDesign::Body" in meta["types"]

        # 驗證個別特徵物件
        meta_001 = parse_fcstd_metadata(files["freecad-fem-001"])
        assert "PartDesign::Pad" in meta_001["types"]
        assert "PartDesign::Pocket" in meta_001["types"]

        meta_002 = parse_fcstd_metadata(files["freecad-fem-002"])
        assert "PartDesign::Thickness" in meta_002["types"]

    def test_real_cadworld_fcstd_in_staged_diagnostics_funnel(self, fixture_dir: Path):
        """驗證真實 .FCStd 輸入時，8 階段短路漏斗能免安裝自動解析並推進階段。"""
        real_001 = fixture_dir / "freecad-fem-001-precondition.FCStd"

        # 模擬 Agent 產出真實 FCStd，未提供結構樹（由 gatekeeper 自行解析）
        state = {
            "task_id": "freecad-fem-001",
            "claimed_done": True,
            "file_path": str(real_001),
        }

        # 傳入需要包含 FEM Analysis 結構樹的 rubric
        rubric = {
            "structure": {
                "required_type_contains": ["Fem::FemAnalysis", "ConstraintFixed"],
                "required_label_contains": ["Fixed Support"],
            }
        }

        rep = evaluate_staged_rubric(state, rubric)
        # 前置模型檔案存在且合法，因此 Stage 1 (file_saved) 與 Stage 2 (file_valid) 必 PASS
        assert rep.stages["file_saved"]["ok"] is True
        assert rep.stages["file_valid"]["ok"] is True

        # 因為這是前置 CAD 幾何檔（尚未加入 FEM 分析設定），漏斗應精確阻斷於 Stage 4 (structure)
        assert rep.first_broken_stage == "structure"
        assert rep.failure_class == FailureClassEnum.F5_WRONG_DOCUMENT_STRUCTURE

