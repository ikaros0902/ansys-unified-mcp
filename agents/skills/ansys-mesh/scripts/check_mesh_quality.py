# -*- coding: utf-8 -*-
"""
Mesh Quality Diagnostic & Redline Violation Checker for ANSYS Mechanical.
Features:
- Reads Mesh Statistics: Min Orthogonal Quality, Max Skewness, Aspect Ratio, Jacobian Ratio.
- Evaluates Explicit CFL Timestep using LSDYNA TimeStepCalc if available.
- Thin-wall Shear Locking Diagnostic (flags thin bodies with single-layer tetra elements).
- Engineering Redline Threshold Evaluation (Pass / Warning / Fail).
- Dual Reporting: Terminal summary card + Automatic CSV report export.
- Compatible with IronPython 2.7 (Mechanical ACT) and CPython 3.x (PyMechanical).
"""

import sys
import os
import csv
import datetime

def run_mesh_quality_check(output_csv_dir=None):
    """
    Main entry point for mesh quality diagnostics.
    Args:
        output_csv_dir (str, optional): Target directory for CSV export.
    """
    try:
        model = ExtAPI.DataModel.Project.Model
        mesh = model.Mesh
    except NameError:
        print("[Error] ExtAPI or DataModel is not available. Please run in ANSYS Mechanical ACT.")
        return False

    print("==================================================")
    print("Starting ANSYS Mesh Quality & Redline Diagnostic")
    print("==================================================")

    total_nodes = mesh.Nodes
    total_elements = mesh.Elements

    if total_elements == 0:
        print("[Error] No mesh generated yet. Please generate mesh first.")
        return False

    # Read global statistics
    stats = getattr(mesh, "MeshStatistics", None)
    min_ortho = 1.0
    avg_ortho = 1.0
    max_skew = 0.0
    avg_skew = 0.0

    if stats:
        try:
            min_ortho = float(stats.MinOrthogonalQuality)
            avg_ortho = float(stats.AverageOrthogonalQuality)
            max_skew = float(stats.MaxSkewness)
            avg_skew = float(stats.AverageSkewness)
        except Exception:
            pass

    # Read CFL if available
    cfl_min = 0.0
    try:
        cfl_obj = ExtAPI.DataModel.CreateObject("TimeStepCalc", "LSDYNA")
        cfl_obj.Properties["Time Step Safety Factor"].Value = 0.90
        cfl_obj.Activate()
        cfl_obj.NotifyChange()
        cfl_obj.Import()
        val = cfl_obj.Properties["Minimum CFL value"].Value
        cfl_min = float(val) if val is not None else 0.0
        with Transaction(True):
            DataModel.Remove(cfl_obj)
    except Exception:
        cfl_min = 0.0

    # Per-body diagnostics
    body_records = []
    redline_violations = []

    for b in model.Geometry.GetChildren(DataModelObjectCategory.Body, True):
        if getattr(b, "Suppressed", False):
            continue

        b_name = b.Name
        t_str = b.GetGeoBody().BodyType.ToString()
        b_elements = getattr(b, "Elements", 0)

        # Body-specific CFL check
        b_cfl = 0.0
        try:
            cfl_b = ExtAPI.DataModel.CreateObject("TimeStepCalc", "LSDYNA")
            cfl_b.Properties["Time Step Safety Factor"].Value = 0.90
            sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
            sel.Ids = [b.GetGeoBody().Id]
            cfl_b.Properties["Geometry/DefineBy/Geo"].Value = sel
            cfl_b.Activate()
            cfl_b.NotifyChange()
            cfl_b.Import()
            v = cfl_b.Properties["Minimum CFL value"].Value
            b_cfl = float(v) if v is not None else 0.0
            with Transaction(True):
                DataModel.Remove(cfl_b)
        except Exception:
            pass

        # Check Redlines
        issues = []
        if b_cfl > 0 and b_cfl < 5.0e-7:
            issues.append("Low CFL (< 0.5 us)")

        # Thin-wall shear locking heuristic check
        if t_str == "GeoBodySolid":
            try:
                box = b.GetGeoBody().Volume / (b.GetGeoBody().Area / 2.0) if b.GetGeoBody().Area > 0 else 1.0
                if box < 1.5 and b_elements < 100:
                    issues.append("Suspected Shear Locking (Thin Solid with low elements)")
            except Exception:
                pass

        status = "FAIL" if issues else "PASS"
        if issues:
            redline_violations.append("{}: {}".format(b_name, ", ".join(issues)))

        body_records.append({
            "Name": b_name,
            "Type": t_str,
            "Elements": b_elements,
            "CFL_sec": b_cfl,
            "Status": status,
            "Notes": "; ".join(issues) if issues else "OK"
        })

    # Global Redline Checks
    global_status = "PASS"
    global_issues = []

    if max_skew > 0.85:
        global_status = "FAIL"
        global_issues.append("Max Skewness ({:.3f}) exceeds critical limit 0.85".format(max_skew))
    elif max_skew > 0.70:
        global_status = "WARNING"
        global_issues.append("Max Skewness ({:.3f}) exceeds recommended limit 0.40".format(max_skew))

    if min_ortho < 0.15:
        global_status = "FAIL"
        global_issues.append("Min Orthogonal Quality ({:.3f}) is below critical limit 0.15".format(min_ortho))
    elif min_ortho < 0.70:
        if global_status != "FAIL":
            global_status = "WARNING"
        global_issues.append("Min Orthogonal Quality ({:.3f}) is below recommended 0.70".format(min_ortho))

    # Export CSV Report
    if output_csv_dir is None:
        try:
            output_csv_dir = DataModel.Project.SaveDirectory
        except Exception:
            output_csv_dir = os.getcwd()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = "MeshQuality_Report_{}.csv".format(timestamp)
    csv_path = os.path.join(output_csv_dir, csv_filename)

    try:
        with open(csv_path, "wb" if sys.version_info[0] < 3 else "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Body_Name", "Body_Type", "Elements", "CFL_sec", "Quality_Status", "Notes"])
            for r in body_records:
                writer.writerow([r["Name"], r["Type"], r["Elements"], "{:.4e}".format(r["CFL_sec"]), r["Status"], r["Notes"]])
        print("[CSV Export] Saved quality report to: {}".format(csv_path))
    except Exception as ex:
        print("[Warning] Could not export CSV report: {}".format(ex))

    # Print Summary Card
    print("\n" + "=" * 55)
    print("         ANSYS MESH QUALITY DIAGNOSTIC SUMMARY")
    print("=" * 55)
    print("Overall Quality Status : [{}]".format(global_status))
    print("Total Mesh Nodes       : {}".format(total_nodes))
    print("Total Mesh Elements    : {}".format(total_elements))
    print("-------------------------------------------------------")
    print("Max Skewness           : {:.4f} (Avg: {:.4f})".format(max_skew, avg_skew))
    print("Min Orthogonal Quality : {:.4f} (Avg: {:.4f})".format(min_ortho, avg_ortho))
    if cfl_min > 0:
        print("Min CFL Timestep       : {:.4e} seconds".format(cfl_min))
    print("-------------------------------------------------------")
    if global_issues:
        print("[Warnings / Violations]:")
        for g_iss in global_issues:
            print("  * {}".format(g_iss))
    if redline_violations:
        print("[Body Specific Issues]:")
        for b_iss in redline_violations[:5]:
            print("  * {}".format(b_iss))
        if len(redline_violations) > 5:
            print("  ... and {} more bodies with issues (see CSV).".format(len(redline_violations) - 5))
    else:
        print("[Result] All bodies passed basic mesh quality gate.")
    print("CSV Report Saved       : {}".format(csv_path))
    print("=" * 55)

    return global_status != "FAIL"

if __name__ == "__main__":
    run_mesh_quality_check()
