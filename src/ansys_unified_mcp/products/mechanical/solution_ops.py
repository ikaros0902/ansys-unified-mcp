"""ANSYS Mechanical 求解、結果場評估與模型診斷模組 (Solution & Post-processing Operations).

提供求解執行、狀態查詢、變形/應力/反力後處理、報告生成、質點簡化 (Point Mass)、
樹狀結構診斷 (Model Tree Hierarchy)、BOM 材料批量指派與群組接頭自動化生成。
依循 Clean-Room 架構，所有操作均向 api 委派，內嵌腳本維持純 ASCII 英文。
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Optional

from ansys_unified_mcp.products.mechanical import api


def solve_analysis(analysis_index: int = 0, timeout_seconds: Optional[float] = 3600.0) -> dict:
    """執行指定分析系統之求解 (Solve)。"""
    err = api._check_connection()
    if err:
        return err
    script = (
        "analysis = ExtAPI.DataModel.Project.Model.Analyses[" + str(analysis_index) + "]\n"
        "analysis.Solution.Solve(True)\n"
        'print("Solve complete. Status: " + str(analysis.Solution.Status))\n'
    )
    result = api._run(script, timeout=timeout_seconds)
    if not result or not result.strip():
        return {"ok": False, "error": "Solve failed: empty output", "message": result}
    ok = (
        "solve complete" in result.lower()
        and "script error:" not in result.lower()
        and "failed" not in result.lower()
        and not api._is_error_output(result)
    )
    if not ok:
        return {"ok": False, "error": f"Solve failed: {result[:200]}", "message": result}
    return {"ok": True, "message": result}


def get_solve_status(analysis_index: int = 0) -> dict:
    """獲取指定分析系統之求解狀態 (Solve Status)。"""
    err = api._check_connection()
    if err:
        return err
    script = (
        "import json\n"
        "analysis = ExtAPI.DataModel.Project.Model.Analyses[" + str(analysis_index) + "]\n"
        'print(json.dumps({"status": str(analysis.Solution.Status), "name": str(analysis.Name), "type": str(analysis.AnalysisType)}))\n'
    )
    result = api._run(script)
    try:
        return {"ok": True, **json.loads(result)}
    except Exception:
        return api._parse_mechanical_output(result)


def add_total_deformation_all_modes(num_modes: int = 6, analysis_index: int = 0) -> dict:
    """在模態分析中為前 N 階模態批次加入總變形結果 (Total Deformation)。"""
    err = api._check_connection()
    if err:
        return err
    script = (
        "solution = ExtAPI.DataModel.Project.Model.Analyses[" + str(analysis_index) + "].Solution\n"
        "for i in range(1, " + str(num_modes + 1) + "):\n"
        "    td = solution.AddTotalDeformation()\n"
        "    td.Mode = i\n"
        "solution.EvaluateAllResults()\n"
        'print("Total Deformation added for ' + str(num_modes) + ' modes.")\n'
    )
    result = api._run(script)
    if not result or not result.strip():
        return {"ok": False, "error": "Failed to add deformation: empty output", "raw_output": result}
    if api._is_error_output(result):
        return {"ok": False, "error": f"Failed to add deformation: {result[:200]}", "raw_output": result}
    if "total deformation added" not in result.lower():
        return {"ok": False, "error": f"Failed to add deformation: {result[:200]}", "raw_output": result}
    return {"ok": True, "message": result}


def add_total_deformation(mode: int = 0, analysis_index: int = 0) -> dict:
    """加入總變形結果項目 (Total Deformation)，支援靜態分析與指定階數模態。"""
    err = api._check_connection()
    if err:
        return err
    mode_line = ("    td.Mode = " + str(mode) + "\n") if mode > 0 else ""
    script = (
        "solution = ExtAPI.DataModel.Project.Model.Analyses[" + str(analysis_index) + "].Solution\n"
        "td = solution.AddTotalDeformation()\n" + mode_line + "solution.EvaluateAllResults()\n"
        'print("Total Deformation added. Max: " + str(td.Maximum))\n'
    )
    result = api._run(script)
    if not result or not result.strip():
        return {"ok": False, "error": "Failed to add deformation: empty output", "raw_output": result}
    if api._is_error_output(result):
        return {"ok": False, "error": f"Failed to add deformation: {result[:200]}", "raw_output": result}
    if "total deformation added" not in result.lower():
        return {"ok": False, "error": f"Failed to add deformation: {result[:200]}", "raw_output": result}
    return {"ok": True, "message": result}


def get_modal_frequencies(analysis_index: int = 0) -> dict:
    """提取模態分析中所有階數的固有頻率 (Natural Frequencies, 單位: Hz)。"""
    err = api._check_connection()
    if err:
        return err
    script = (
        "import json\n"
        "solution = ExtAPI.DataModel.Project.Model.Analyses[" + str(analysis_index) + "].Solution\n"
        "frequencies = []\n"
        "for r in solution.Children:\n"
        '    if "TotalDeformation" in str(r.GetType().Name):\n'
        "        try:\n"
        '            frequencies.append({"mode": int(r.Mode), "frequency_hz": float(str(r.ReportedFrequency).split()[0])})\n'
        "        except:\n"
        "            pass\n"
        'frequencies.sort(key=lambda x: x["mode"])\n'
        'print(json.dumps({"frequencies": frequencies}))\n'
    )
    result = api._run(script)
    try:
        return {"ok": True, **json.loads(result)}
    except Exception:
        return api._parse_mechanical_output(result)


def generate_report(output_path: str, analysis_index: int = 0, fmt: str = "docx") -> dict:
    """生成結構模擬摘要報告 (支援 docx 與純文字 txt 格式)。"""
    err = api._check_connection()
    if err:
        return err
    script = (
        "import json\n"
        "model = ExtAPI.DataModel.Project.Model\n"
        "analysis = model.Analyses[" + str(analysis_index) + "]\n"
        "solution = analysis.Solution\n"
        "data = {}\n"
        'data["analysis_name"] = str(analysis.Name)\n'
        'data["analysis_type"] = str(analysis.AnalysisType)\n'
        'data["solution_status"] = str(solution.Status)\n'
        'data["bodies"] = [{"name": str(b.Name), "material": str(b.Material) if hasattr(b, "Material") else "N/A"} for b in model.Geometry.GetChildren(DataModelObjectCategory.Body, True)]\n'
        "mesh = model.Mesh\n"
        "try:\n"
        '    data["nodes"] = int(mesh.Nodes)\n'
        '    data["elements"] = int(mesh.Elements)\n'
        "except:\n"
        '    data["nodes"] = "N/A"\n'
        '    data["elements"] = "N/A"\n'
        'data["boundary_conditions"] = [str(c.Name) for c in analysis.Children]\n'
        "results = []\n"
        "for r in solution.Children:\n"
        "    try:\n"
        '        rd = {"name": str(r.Name)}\n'
        '        try: rd["max"] = str(r.Maximum)\n'
        "        except: pass\n"
        '        try: rd["mode"] = str(r.Mode); rd["freq"] = str(r.ReportedFrequency)\n'
        "        except: pass\n"
        "        results.append(rd)\n"
        "    except: pass\n"
        'data["results"] = results\n'
        "print(json.dumps(data))\n"
    )
    raw = api._run(script)
    try:
        data = json.loads(raw)
    except Exception:
        return {"ok": False, "error": "Failed to gather data", "raw": raw}
    out = Path(output_path)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return {"ok": False, "error": "Cannot create output directory: " + str(e)}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if fmt.lower() == "docx":
        try:
            from docx import Document
            from docx.enum.text import WD_ALIGN_PARAGRAPH

            doc = Document()
            t = doc.add_heading("ANSYS Mechanical Simulation Report", 0)
            t.alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph("Generated: " + now)
            doc.add_paragraph(
                "Analysis: "
                + data.get("analysis_name", "N/A")
                + " ("
                + data.get("analysis_type", "N/A")
                + ")"
            )
            doc.add_paragraph("Status: " + data.get("solution_status", "N/A"))
            doc.add_heading("1. Geometry", level=1)
            tbl = doc.add_table(rows=1, cols=2)
            tbl.style = "Table Grid"
            tbl.rows[0].cells[0].text = "Body"
            tbl.rows[0].cells[1].text = "Material"
            for b in data.get("bodies", []):
                row = tbl.add_row().cells
                row[0].text = b.get("name", "")
                row[1].text = b.get("material", "N/A")
            doc.add_heading("2. Mesh", level=1)
            doc.add_paragraph("Nodes: " + str(data.get("nodes", "N/A")))
            doc.add_paragraph("Elements: " + str(data.get("elements", "N/A")))
            doc.add_heading("3. Boundary Conditions", level=1)
            for bc in data.get("boundary_conditions", []):
                doc.add_paragraph(bc, style="List Bullet")
            doc.add_heading("4. Results", level=1)
            tbl2 = doc.add_table(rows=1, cols=4)
            tbl2.style = "Table Grid"
            tbl2.rows[0].cells[0].text = "Result"
            tbl2.rows[0].cells[1].text = "Mode"
            tbl2.rows[0].cells[2].text = "Frequency (Hz)"
            tbl2.rows[0].cells[3].text = "Max Value"
            for r in data.get("results", []):
                row = tbl2.add_row().cells
                row[0].text = r.get("name", "")
                row[1].text = r.get("mode", "-")
                row[2].text = r.get("freq", "-")
                row[3].text = r.get("max", "-")
            doc.save(str(out))
            return {"ok": True, "report_path": str(out)}
        except ImportError:
            return {"ok": False, "error": "python-docx not installed."}
    else:
        lines = [
            "ANSYS MECHANICAL SIMULATION REPORT",
            "Generated: " + now,
            "Analysis: "
            + data.get("analysis_name", "")
            + " ("
            + data.get("analysis_type", "")
            + ")",
            "Status: " + data.get("solution_status", ""),
            "",
            "GEOMETRY",
        ]
        for b in data.get("bodies", []):
            lines.append("  " + b.get("name", "") + " | " + b.get("material", "N/A"))
        lines += [
            "",
            "MESH",
            "  Nodes: " + str(data.get("nodes")),
            "  Elements: " + str(data.get("elements")),
            "",
            "BOUNDARY CONDITIONS",
        ]
        for bc in data.get("boundary_conditions", []):
            lines.append("  " + bc)
        lines += ["", "RESULTS"]
        for r in data.get("results", []):
            lines.append(
                "  "
                + r.get("name", "")
                + " | Mode: "
                + r.get("mode", "-")
                + " | Freq: "
                + r.get("freq", "-")
                + " | Max: "
                + r.get("max", "-")
            )
        out_txt = out.with_suffix(".txt")
        out_txt.write_text("\n".join(lines), encoding="utf-8")
        return {"ok": True, "report_path": str(out_txt)}


def add_equivalent_stress(named_selection: str = "", analysis_index: int = 0) -> dict:
    """加入等效應力 (von Mises Stress) 結果，可選指定具名選擇作用範圍。"""
    err = api._check_connection()
    if err:
        return err
    scope_lines = ""
    if named_selection:
        safe_ns = api._esc(named_selection)
        scope_lines = '_NS_NAME = "' + safe_ns + '"\n' + api._NS_LOOKUP + "if _ns: _r.Location = _ns\n"
    result = api._run(
        "import json\n"
        "_solution = ExtAPI.DataModel.Project.Model.Analyses["
        + str(analysis_index)
        + "].Solution\n"
        "_r = _solution.AddEquivalentStress()\n" + scope_lines + "_solution.EvaluateAllResults()\n"
        'print(json.dumps({"ok": True, "max": str(_r.Maximum), "min": str(_r.Minimum)}))\n'
    )
    try:
        return json.loads(result)
    except Exception:
        return api._parse_mechanical_output(result)


def add_directional_deformation(
    axis: str = "Y", named_selection: str = "", analysis_index: int = 0
) -> dict:
    """加入方向變形 (Directional Deformation) 結果 (X/Y/Z 軸)。"""
    err = api._check_connection()
    if err:
        return err
    axis_map = {
        "X": "NormalOrientationType.XAxis",
        "Y": "NormalOrientationType.YAxis",
        "Z": "NormalOrientationType.ZAxis",
    }
    axis_key = axis.upper() if axis.upper() in axis_map else "Y"
    axis_enum = axis_map[axis_key]
    scope_lines = ""
    if named_selection:
        safe_ns = api._esc(named_selection)
        scope_lines = '_NS_NAME = "' + safe_ns + '"\n' + api._NS_LOOKUP + "if _ns: _r.Location = _ns\n"
    result = api._run(
        "import json\n"
        "_solution = ExtAPI.DataModel.Project.Model.Analyses["
        + str(analysis_index)
        + "].Solution\n"
        "_r = _solution.AddDirectionalDeformation()\n"
        "_r.NormalOrientation = "
        + axis_enum
        + "\n"
        + scope_lines
        + "_solution.EvaluateAllResults()\n"
        'print(json.dumps({"ok": True, "axis": "'
        + axis_key
        + '", "max": str(_r.Maximum), "min": str(_r.Minimum)}))\n'
    )
    try:
        return json.loads(result)
    except Exception:
        return api._parse_mechanical_output(result)


def add_principal_stress(which: str = "max", analysis_index: int = 0) -> dict:
    """加入主應力 (Principal Stress) 結果 (max, mid, min)。"""
    err = api._check_connection()
    if err:
        return err
    method_map = {
        "max": "AddMaximumPrincipalStress",
        "mid": "AddMiddlePrincipalStress",
        "min": "AddMinimumPrincipalStress",
    }
    method = method_map.get(which.lower(), "AddMaximumPrincipalStress")
    result = api._run(
        "import json\n"
        "_solution = ExtAPI.DataModel.Project.Model.Analyses["
        + str(analysis_index)
        + "].Solution\n"
        "_r = _solution." + method + "()\n"
        "_solution.EvaluateAllResults()\n"
        'print(json.dumps({"ok": True, "type": "'
        + api._esc(which)
        + ' principal", "max": str(_r.Maximum), "min": str(_r.Minimum)}))\n'
    )
    try:
        return json.loads(result)
    except Exception:
        return api._parse_mechanical_output(result)


def add_stress_tool(analysis_index: int = 0) -> dict:
    """加入應力工具 (Stress Tool, 計算結構安全係數與應力比)。"""
    err = api._check_connection()
    if err:
        return err
    result = api._run(
        "import json\n"
        "_solution = ExtAPI.DataModel.Project.Model.Analyses["
        + str(analysis_index)
        + "].Solution\n"
        "_st = _solution.AddStressTool()\n"
        "_solution.EvaluateAllResults()\n"
        'print(json.dumps({"ok": True, "message": "Stress Tool added and evaluated"}))\n'
    )
    try:
        return json.loads(result)
    except Exception:
        return api._parse_mechanical_output(result)


def add_reaction_force(named_selection: str, analysis_index: int = 0) -> dict:
    """在指定具名選擇邊界處加入反力探針 (Force Reaction Probe)。"""
    err = api._check_connection()
    if err:
        return err
    result = api._run(
        "import json\n"
        '_NS_NAME = "' + api._esc(named_selection) + '"\n' + api._NS_LOOKUP + "if _ns is None:\n"
        '    print(json.dumps({"ok": False, "error": "Named selection not found"}))\n'
        "else:\n"
        "    _solution = ExtAPI.DataModel.Project.Model.Analyses["
        + str(analysis_index)
        + "].Solution\n"
        "    _r = _solution.AddForceReaction()\n"
        "    _r.Location = _ns\n"
        "    _solution.EvaluateAllResults()\n"
        '    print(json.dumps({"ok": True, "x": str(_r.XAxis), "y": str(_r.YAxis), "z": str(_r.ZAxis), "total": str(_r.Total)}))\n'
    )
    try:
        return json.loads(result)
    except Exception:
        return api._parse_mechanical_output(result)


def _build_pm_script(match_lines: str, ns_label: str, prox_mult: float = 3.0) -> str:
    """構建質點轉換與鄰近安裝面具名選擇之 IronPython 腳本 (純第一原理計算，無 ACT 擴充依賴)。"""
    return (
        "import math, json, binascii\n"
        "model = ExtAPI.DataModel.Project.Model\n"
        "all_bodies = model.Geometry.GetChildren(DataModelObjectCategory.Body, True)\n"
        + match_lines
        + "if not matched:\n"
        '    print(json.dumps({"ok": False, "error": "No unsuppressed bodies found"}))\n'
        "else:\n"
        "    # --- Step 1: record bounding box BEFORE suppression ---\n"
        "    eq_min = [1e18, 1e18, 1e18]\n"
        "    eq_max = [-1e18, -1e18, -1e18]\n"
        "    for _b in matched:\n"
        "        for _f in _b.GetGeoBody().Faces:\n"
        "            try:\n"
        "                _c = _f.Centroid\n"
        "                for _i in range(3):\n"
        "                    if _c[_i] < eq_min[_i]: eq_min[_i] = _c[_i]\n"
        "                    if _c[_i] > eq_max[_i]: eq_max[_i] = _c[_i]\n"
        "            except: pass\n"
        "    # --- Step 2: create Point Mass from first principles ---\n"
        "    _geometry = model.Geometry\n"
        "    _sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)\n"
        "    _sel.Ids = [_b.GetGeoBody().Id for _b in matched]\n"
        "    ExtAPI.SelectionManager.NewSelection(_sel)\n"
        "    _selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)\n"
        "    _selection.Ids = ExtAPI.SelectionManager.CurrentSelection.Ids\n"
        '    _PM_mass = Quantity("0 [kg]")\n'
        '    _PM_x    = Quantity("0 [m]")\n'
        '    _PM_y    = Quantity("0 [m]")\n'
        '    _PM_z    = Quantity("0 [m]")\n'
        '    _PM_Ixx  = Quantity("0 [kg m m]")\n'
        '    _PM_Iyy  = Quantity("0 [kg m m]")\n'
        '    _PM_Izz  = Quantity("0 [kg m m]")\n'
        "    _PM_vol  = 0.0\n"
        "    _n_bodies = 0\n"
        '    _len_unit  = "m"\n'
        '    _mass_unit = "kg"\n'
        "    _units_set = False\n"
        "    _pm = _geometry.AddPointMass()\n"
        "    ExtAPI.SelectionManager.ClearSelection()\n"
        "    for _entity in _selection.Entities:\n"
        "        _body = _geometry.GetBody(_entity)\n"
        '        if "Solid" not in str(_body.GetGeoBody().BodyType): continue\n'
        "        if not _units_set:\n"
        "            _len_unit = _body.CentroidX.Unit\n"
        "            _mass_unit = _body.Mass.Unit\n"
        "            _units_set = True\n"
        "        _bm  = _body.Mass\n"
        "        _bx  = _body.CentroidX\n"
        "        _by  = _body.CentroidY\n"
        "        _bz  = _body.CentroidZ\n"
        "        _bIx = _body.MomentOfInertiaIp1\n"
        "        _bIy = _body.MomentOfInertiaIp2\n"
        "        _bIz = _body.MomentOfInertiaIp3\n"
        '        _PM_vol += _body.Volume.ConvertUnit("m m m").Value\n'
        "        _nx = (_PM_x * _PM_mass + _bx * _bm) / (_PM_mass + _bm)\n"
        "        _ny = (_PM_y * _PM_mass + _by * _bm) / (_PM_mass + _bm)\n"
        "        _nz = (_PM_z * _PM_mass + _bz * _bm) / (_PM_mass + _bm)\n"
        "        _PM_Ixx = _PM_Ixx + _bIx + _bm*((_ny-_by)**2+(_nz-_bz)**2) + _PM_mass*((_ny-_PM_y)**2+(_nz-_PM_z)**2)\n"
        "        _PM_Iyy = _PM_Iyy + _bIy + _bm*((_nx-_bx)**2+(_nz-_bz)**2) + _PM_mass*((_nx-_PM_x)**2+(_nz-_PM_z)**2)\n"
        "        _PM_Izz = _PM_Izz + _bIz + _bm*((_nx-_bx)**2+(_ny-_by)**2) + _PM_mass*((_nx-_PM_x)**2+(_ny-_PM_y)**2)\n"
        "        _PM_mass = _PM_mass + _bm\n"
        "        _PM_x = _nx; _PM_y = _ny; _PM_z = _nz\n"
        "        _n_bodies += 1\n"
        "        _body.Suppressed = True\n"
        "    if _PM_mass.Value <= 0:\n"
        "        _pm.Delete()\n"
        '        print(json.dumps({"ok": False, "error": "No solid bodies found in selection"}))\n'
        "    else:\n"
        '        _pm_name = "%d bodies, %.5g %s" % (_n_bodies, round(_PM_mass.ConvertUnit(_mass_unit).Value, 5), _mass_unit)\n'
        "        _pinball_m = (3.0 * _PM_vol / (4.0 * math.pi)) ** (1.0 / 3.0)\n"
        "        _pm.Name = _pm_name\n"
        "        _pm.Mass = _PM_mass\n"
        "        _pm.InternalObject.LocationX = _PM_x.ConvertUnit(_len_unit).Value\n"
        "        _pm.InternalObject.LocationY = _PM_y.ConvertUnit(_len_unit).Value\n"
        "        _pm.InternalObject.LocationZ = _PM_z.ConvertUnit(_len_unit).Value\n"
        "        _pm.MassMomentOfInertiaX = _PM_Ixx\n"
        "        _pm.MassMomentOfInertiaY = _PM_Iyy\n"
        "        _pm.MassMomentOfInertiaZ = _PM_Izz\n"
        "        _pm.Activate()\n"
        "        # --- Step 3: PM CG in metres for face search ---\n"
        '        cx = _PM_x.ConvertUnit("m").Value\n'
        '        cy = _PM_y.ConvertUnit("m").Value\n'
        '        cz = _PM_z.ConvertUnit("m").Value\n'
        "        _pinball   = _pinball_m\n"
        "        _search_r  = _pinball * " + str(prox_mult) + "\n"
        "        _search_ftol = _pinball * 0.4\n"
        "        _SEED_TOL  = 0.005\n"
        "        _PLANE_TOL = 0.005\n"
        "        _FP_TOL    = 0.020\n"
        "        def _d2box_exact(c):\n"
        "            dx = max(eq_min[0]-c[0], 0.0, c[0]-eq_max[0])\n"
        "            dy = max(eq_min[1]-c[1], 0.0, c[1]-eq_max[1])\n"
        "            dz = max(eq_min[2]-c[2], 0.0, c[2]-eq_max[2])\n"
        "            return math.sqrt(dx*dx+dy*dy+dz*dz)\n"
        "        def _d2box_exp(c):\n"
        "            dx = max(eq_min[0]-_search_ftol-c[0], 0.0, c[0]-eq_max[0]-_search_ftol)\n"
        "            dy = max(eq_min[1]-_search_ftol-c[1], 0.0, c[1]-eq_max[1]-_search_ftol)\n"
        "            dz = max(eq_min[2]-_search_ftol-c[2], 0.0, c[2]-eq_max[2]-_search_ftol)\n"
        "            return math.sqrt(dx*dx+dy*dy+dz*dz)\n"
        "        # --- Step 4: seed face ON bbox boundary with best alignment to CG ---\n"
        "        _best_score = -1e18\n"
        "        _best_face  = None\n"
        "        for _body in model.Geometry.GetChildren(DataModelObjectCategory.Body, True):\n"
        "            if _body.Suppressed: continue\n"
        "            _gb = _body.GetGeoBody()\n"
        "            for _face in _gb.Faces:\n"
        "                try:\n"
        "                    c = _face.Centroid\n"
        "                    _dist_cg = math.sqrt((c[0]-cx)**2+(c[1]-cy)**2+(c[2]-cz)**2)\n"
        "                    if _dist_cg > _search_r: continue\n"
        "                    if _d2box_exp(c) > 0: continue\n"
        "                    if _d2box_exact(c) > _SEED_TOL: continue\n"
        "                    n = _face.NormalAtParam(0.5, 0.5)\n"
        "                    _dv = [cx-c[0], cy-c[1], cz-c[2]]\n"
        "                    if _dist_cg == 0: continue\n"
        "                    _align = (n[0]*_dv[0]+n[1]*_dv[1]+n[2]*_dv[2]) / _dist_cg\n"
        "                    if _align < 0.4: continue\n"
        "                    if _align > _best_score:\n"
        "                        _best_score = _align\n"
        "                        _best_face = (int(_face.Id), [c[0],c[1],c[2]], [n[0],n[1],n[2]])\n"
        "                except: pass\n"
        "        if _best_face is None:\n"
        '            print(json.dumps({"ok": False, "error": "No attachment face found on equipment boundary"}))\n'
        "        else:\n"
        "            _bf_id, _bf_c, _bf_n = _best_face\n"
        "            _bf_lvl = _bf_n[0]*_bf_c[0]+_bf_n[1]*_bf_c[1]+_bf_n[2]*_bf_c[2]\n"
        "            _abs_n  = [abs(_bf_n[0]), abs(_bf_n[1]), abs(_bf_n[2])]\n"
        "            _dom_ax = 0\n"
        "            for _i in range(1,3):\n"
        "                if _abs_n[_i] > _abs_n[_dom_ax]: _dom_ax = _i\n"
        "            _fp = [_i for _i in range(3) if _i != _dom_ax]\n"
        "            # --- Step 5: collect all coplanar faces within equipment footprint ---\n"
        "            _attach_ids = []\n"
        "            for _body in model.Geometry.GetChildren(DataModelObjectCategory.Body, True):\n"
        "                if _body.Suppressed: continue\n"
        "                _gb = _body.GetGeoBody()\n"
        "                for _face in _gb.Faces:\n"
        "                    try:\n"
        "                        c = _face.Centroid\n"
        "                        if math.sqrt((c[0]-cx)**2+(c[1]-cy)**2+(c[2]-cz)**2) > _search_r: continue\n"
        "                        if not (eq_min[_fp[0]]-_FP_TOL <= c[_fp[0]] <= eq_max[_fp[0]]+_FP_TOL): continue\n"
        "                        if not (eq_min[_fp[1]]-_FP_TOL <= c[_fp[1]] <= eq_max[_fp[1]]+_FP_TOL): continue\n"
        "                        n = _face.NormalAtParam(0.5, 0.5)\n"
        "                        if abs(n[0]*_bf_n[0]+n[1]*_bf_n[1]+n[2]*_bf_n[2]) < 0.9: continue\n"
        "                        _lvl = n[0]*c[0]+n[1]*c[1]+n[2]*c[2]\n"
        "                        if abs(_lvl - _bf_lvl) > _PLANE_TOL: continue\n"
        "                        _attach_ids.append(int(_face.Id))\n"
        "                    except: pass\n"
        "            # --- Step 6: create named selection and scope PM to it ---\n"
        "            _ns_sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)\n"
        "            _ns_sel.Ids = _attach_ids\n"
        "            _ns = model.AddNamedSelection()\n"
        '            _ns.Name = "NearestFace_' + ns_label + '"\n'
        "            _ns.Location = _ns_sel\n"
        "            _pm.Location = _ns\n"
        '            _pm.PinballRegion = Quantity("0 [mm]")\n'
        '            print(json.dumps({"ok": True,\n'
        '                "cg_mm": [round(cx*1000,1),round(cy*1000,1),round(cz*1000,1)],\n'
        '                "pinball": "0 [mm] (All)",\n'
        '                "bodies_matched": len(matched),\n'
        '                "attachment_faces": len(_attach_ids),\n'
        '                "named_selection": str(_ns.Name)}))\n'
    )


def _extract_json(raw: str) -> dict:
    """從原始輸出中擷取首行有效 JSON 物件。"""
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                data = json.loads(line)
                if isinstance(data, dict):
                    if "ok" not in data:
                        data["ok"] = True
                    return data
            except Exception:
                pass
    return {
        "ok": False,
        "error": f"Script execution failed: {raw[:200].strip()}",
        "raw_output": raw,
    }


def convert_prefix_to_point_mass(body_name_prefix: str, proximity_multiplier: float = 3.0) -> dict:
    """將匹配指定前綴之所有未抑制實體轉換為質點 (Point Mass)，並自動尋找鄰近接觸面。"""
    err = api._check_connection()
    if err:
        return err
    prefix_hex = body_name_prefix.encode("utf-8").hex()
    match = (
        "import binascii\n"
        '_PREFIX = binascii.unhexlify("' + prefix_hex + '").decode("utf-8")\n'
        "matched = [b for b in all_bodies if b.Name.startswith(_PREFIX) and not b.Suppressed]\n"
    )
    ns_label = (
        body_name_prefix[:40]
        .replace(" ", "_")
        .replace("\\", "_")
        .replace("/", "_")
        .replace('"', "_")
        .replace("\n", "")
        .replace("\r", "")
        .replace("\t", "")
    )
    raw = api._run(_build_pm_script(match, ns_label, proximity_multiplier))
    return api._parse_mechanical_output(raw)


def convert_part_to_point_mass(part_name: str, proximity_multiplier: float = 3.0) -> dict:
    """將指定多實體零件 (Part) 內部之所有實體轉換為質點 (Point Mass)。"""
    err = api._check_connection()
    if err:
        return err
    safe_part = api._esc(part_name)
    match = (
        '_PART = "' + safe_part + '"\n'
        "matched = [b for b in all_bodies if str(b.Parent.Name) == _PART and not b.Suppressed]\n"
    )
    ns_label = (
        part_name[:40]
        .replace(" ", "_")
        .replace("\\", "_")
        .replace("/", "_")
        .replace('"', "_")
        .replace("\n", "")
        .replace("\r", "")
        .replace("\t", "")
    )
    raw = api._run(_build_pm_script(match, ns_label, proximity_multiplier))
    return api._parse_mechanical_output(raw)


def get_model_tree_hierarchy(max_depth: int = 5) -> dict:
    """遞迴遍歷 Mechanical DataModel 樹狀階層結構，提取各節點名稱、類別、抑制狀態與健全度。"""
    err = api._check_connection()
    if err:
        return err

    script = f"""
import json

def get_node_category(node):
    try:
        return str(node.DataModelObjectCategory)
    except:
        return str(node.GetType())

def get_node_state(node):
    try:
        return str(node.ObjectState)
    except:
        return "Unknown"

def get_node_suppression(node):
    try:
        return bool(node.Suppressed)
    except:
        return False

def traverse_tree(node, current_depth, max_d):
    node_data = {{
        "name": str(node.Name),
        "category": get_node_category(node),
        "state": get_node_state(node),
        "suppressed": get_node_suppression(node),
        "children": []
    }}
    if current_depth < max_d:
        try:
            for child in node.Children:
                node_data["children"].append(traverse_tree(child, current_depth + 1, max_d))
        except:
            pass
    return node_data

model = ExtAPI.DataModel.Project.Model
if model is None:
    print(json.dumps({{"ok": False, "error": "No active Model found"}}))
else:
    tree = traverse_tree(model, 1, {max_depth})
    print(json.dumps({{"ok": True, "tree": tree}}))
"""
    raw = api._run(script)
    return api._parse_mechanical_output(raw)


def assign_materials_from_bom(bom_items: list[dict] | None = None, csv_path: str = "") -> dict:
    """根據 BOM 映射清單或 CSV 檔案為實體批量指派材料。"""
    err = api._check_connection()
    if err:
        return err

    items = list(bom_items) if bom_items else []
    if csv_path:
        import csv

        p = Path(csv_path)
        if not p.is_file():
            return {"ok": False, "error": f"CSV file not found: {csv_path}"}
        with p.open(mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                low_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
                b_name = (
                    low_row.get("bodyname")
                    or low_row.get("body_name")
                    or low_row.get("body")
                    or ""
                )
                m_name = (
                    low_row.get("material")
                    or low_row.get("materialname")
                    or low_row.get("mat")
                    or ""
                )
                rho_val = low_row.get("density") or low_row.get("rho") or None
                if b_name and m_name:
                    item_dict = {"body_name": b_name, "material_name": m_name}
                    if rho_val:
                        try:
                            item_dict["density"] = float(rho_val)
                        except ValueError:
                            pass
                    items.append(item_dict)

    if not items:
        return {"ok": False, "error": "No BOM items provided in parameters or CSV file."}

    serialized_items = json.dumps(items)
    script = f"""
import json

bom_items = json.loads({json.dumps(serialized_items)})
model = ExtAPI.DataModel.Project.Model
all_bodies = model.Geometry.GetChildren(DataModelObjectCategory.Body, True)

assigned = []
unmatched = []

for item in bom_items:
    target_name = item.get("body_name", "").strip().lower()
    mat_name = item.get("material_name", "").strip()
    found = False
    for body in all_bodies:
        b_name = body.Name.strip().lower()
        if target_name in b_name or b_name in target_name:
            try:
                body.Material = mat_name
                assigned.append({{"body": body.Name, "material": mat_name}})
                found = True
            except Exception as e:
                pass
    if not found:
        unmatched.append(target_name)

result = {{
    "ok": True,
    "assigned_count": len(assigned),
    "assigned": assigned,
    "unmatched": unmatched
}}
print(json.dumps(result))
"""
    raw = api._run(script)
    return api._parse_mechanical_output(raw)


def create_joints_from_groups(connection_type: str = "Fixed", group_prefix: str = "Joint_") -> dict:
    """自動為成對的具名選擇群組生成 Mechanical Joint 接頭連接。"""
    err = api._check_connection()
    if err:
        return err

    script = f"""
import json

prefix = {json.dumps(group_prefix)}
j_type = {json.dumps(connection_type)}

model = ExtAPI.DataModel.Project.Model
connections = model.Connections
all_ns = model.GetChildren(DataModelObjectCategory.NamedSelection, True)

matched_ns = [ns for ns in all_ns if ns.Name.startswith(prefix)]
created_joints = []

# Pair by base name or adjacent pairs
pairs = []
for i in range(0, len(matched_ns) - 1, 2):
    pairs.append((matched_ns[i], matched_ns[i+1]))

for ref_ns, mob_ns in pairs:
    try:
        joint = connections.AddJoint()
        joint.Name = "AutoJoint_" + ref_ns.Name.replace(prefix, "")
        joint.ConnectionType = getattr(JointScopingType, "BodyToBody", joint.ConnectionType)
        joint.SourceLocation = ref_ns
        joint.TargetLocation = mob_ns
        created_joints.append(joint.Name)
    except Exception as exc:
        pass

result = {{
    "ok": True,
    "created_count": len(created_joints),
    "created_joints": created_joints,
    "scanned_groups": len(matched_ns)
}}
print(json.dumps(result))
"""
    raw = api._run(script)
    return api._parse_mechanical_output(raw)
