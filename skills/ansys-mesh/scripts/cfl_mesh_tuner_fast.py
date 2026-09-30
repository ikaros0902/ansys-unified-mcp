# -*- coding: utf-8 -*-
"""
Fast CFL Timestep Mesh Tuner for ANSYS Mechanical & LS-DYNA.
Features:
- Group Batching: Chunks assembly into small batches to prevent UI freeze and memory exhaustion.
- Option B Dynamic Isolation: Locks size and suppresses bodies immediately once CFL target is met.
- Single TimeStepCalc Object Reuse: High-speed evaluation without COM object thrashing.
- Exploration Modes: Floating Range (Default, +/- offset), Fixed Range, Percentage Range.
- Automatic Cleanup: Guarantees full unsuppression rollback upon completion or error.
- Dual Reporting: Terminal summary card + Automatic CSV report export.
- Compatible with IronPython 2.7 (Mechanical ACT) and CPython 3.x (PyMechanical).
"""

import sys
import time
import datetime
import os
import csv

def run_fast_cfl_tuner(target_cfl=9.0e-7, batch_size=3, mode="Floating Range",
                       offset_up=1.0, offset_down=1.0, delta_size=0.5,
                       output_csv_dir=None):
    """
    Main entry point for fast CFL mesh tuning.
    Args:
        target_cfl (float): Criteria for minimum CFL timestep in seconds (default: 0.9 microseconds).
        batch_size (int): Number of bodies to process per isolated batch (default: 3).
        mode (str): 'Floating Range', 'Fixed Range', or 'Percentage Range'.
        offset_up (float): Upward offset for Floating Range in mm.
        offset_down (float): Downward offset for Floating Range in mm.
        delta_size (float): Step delta for size candidate exploration in mm.
        output_csv_dir (str, optional): Target directory for CSV export.
    """
    start_time = time.time()

    try:
        model = ExtAPI.DataModel.Project.Model
        mesh = model.Mesh
    except NameError:
        print("[Error] ExtAPI or DataModel is not available. Please run in ANSYS Mechanical ACT.")
        return False

    print("==================================================")
    print("Starting Fast CFL Timestep Mesh Tuner (Option B)")
    print("Target CFL: {:.2e} s | Batch Size: {} | Mode: {}".format(target_cfl, batch_size, mode))
    print("==================================================")

    # 1. Collect and classify unsuppressed bodies
    all_bodies = []
    solid_bodies = []
    shell_bodies = []

    for b in model.Geometry.GetChildren(DataModelObjectCategory.Body, True):
        if not getattr(b, "Suppressed", False):
            all_bodies.append(b)
            t_str = b.GetGeoBody().BodyType.ToString()
            if t_str == "GeoBodySolid":
                solid_bodies.append(b)
            elif t_str in ["GeoBodySheet", "GeoBodySurface"]:
                shell_bodies.append(b)

    total_bodies = len(all_bodies)
    print("[Topology] Collected {} active bodies ({} Solids, {} Shells).".format(
        total_bodies, len(solid_bodies), len(shell_bodies)))

    if total_bodies == 0:
        print("[Warning] No active bodies found to tune.")
        return False

    # Helper: Find Sizing control attached to body
    def get_body_sizing(body):
        geo_id = body.GetGeoBody().Id
        for child in mesh.Children:
            try:
                if isinstance(child, Ansys.ACT.Automation.Mechanical.MeshControls.Sizing):
                    if child.Location and hasattr(child.Location, "Ids") and geo_id in child.Location.Ids:
                        return child
            except Exception:
                pass
        return None

    # Helper: Fast CFL evaluation reusing single object
    def evaluate_cfl_fast(group):
        cfl_res = []
        try:
            cfl_obj = ExtAPI.DataModel.CreateObject("TimeStepCalc", "LSDYNA")
            cfl_obj.Properties["Time Step Safety Factor"].Value = 0.90
            cfl_obj.Properties["Linear Viscosity Coefficient"].Value = 0.06
            sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)

            for b in group:
                if b.ObjectState != ObjectState.Meshed:
                    cfl_res.append(0.0)
                    continue
                try:
                    sel.Ids = [b.GetGeoBody().Id]
                    cfl_obj.Properties["Geometry/DefineBy/Geo"].Value = sel
                    cfl_obj.Activate()
                    cfl_obj.NotifyChange()
                    cfl_obj.Import()
                    val = cfl_obj.Properties["Minimum CFL value"].Value
                    cfl_res.append(float(val) if val is not None else 0.0)
                except Exception:
                    cfl_res.append(0.0)

            with Transaction(True):
                try:
                    DataModel.Remove(cfl_obj)
                except Exception:
                    pass
        except Exception as ex:
            print("[Warning] Fast CFL evaluation exception: {}".format(ex))
            cfl_res = [0.0] * len(group)
        return cfl_res

    # Helper: Suppress others except active group
    def suppress_others(group):
        with Transaction(True):
            for b in all_bodies:
                b.Suppressed = (b not in group)

    # Result recording containers
    results_record = [] # list of dicts for reporting and CSV

    # 2. Process bodies in batches (Chunking)
    def chunk_list(lst, n):
        return [lst[i:i + n] for i in range(0, len(lst), n)]

    body_batches = chunk_list(all_bodies, batch_size)
    print("[Batching] Split into {} batches of up to {} parts.".format(len(body_batches), batch_size))

    try:
        for b_idx, batch in enumerate(body_batches):
            print("\n--- Processing Batch {}/{} ({} parts) ---".format(b_idx + 1, len(body_batches), len(batch)))

            # Step A: Suppress others, keep only batch
            suppress_others(batch)

            # Step B: Prepare sizings & candidate sizes
            sizings = [get_body_sizing(b) for b in batch]
            candidates = []

            for idx, b in enumerate(batch):
                sz_ctrl = sizings[idx]
                cur_sz = 2.0
                if sz_ctrl and sz_ctrl.ElementSize:
                    try:
                        cur_sz = float(sz_ctrl.ElementSize.Value if hasattr(sz_ctrl.ElementSize, "Value") else sz_ctrl.ElementSize)
                    except Exception:
                        cur_sz = 2.0

                # Generate candidates based on mode
                c_list = []
                if mode == "Floating Range":
                    v = cur_sz + offset_up
                    min_v = max(cur_sz - offset_down, delta_size)
                    while v >= min_v - 1e-6:
                        if v > 0:
                            c_list.append(round(v, 4))
                        v -= delta_size
                elif mode == "Fixed Range":
                    v = 3.0
                    while v >= 1.0:
                        c_list.append(round(v, 4))
                        v -= delta_size
                else: # Percentage
                    for pct in [1.5, 1.25, 1.0, 0.85, 0.7]:
                        c_list.append(round(cur_sz * pct, 4))

                if not c_list:
                    c_list.append(round(cur_sz, 4))
                candidates.append(c_list)

            # Step C: Initial baseline evaluation
            with Transaction(True):
                mesh.ClearGeneratedData()
                mesh.GenerateMesh()
            base_cfls = evaluate_cfl_fast(batch)

            # Per-body status in batch
            done_flags = [False] * len(batch)
            best_sizes = [None] * len(batch)
            best_cfls = list(base_cfls)

            for idx in range(len(batch)):
                if base_cfls[idx] >= target_cfl:
                    done_flags[idx] = True
                    best_sizes[idx] = "Baseline"
                    print("  [Converged] Body '{}' met target at baseline (CFL: {:.2e} s)".format(
                        batch[idx].Name, base_cfls[idx]))

            # Step D: Option B Dynamic Isolation Sweep
            max_rounds = max([len(c) for c in candidates]) if candidates else 0
            for r in range(max_rounds):
                # Stop if all bodies in this batch met target
                if all(done_flags):
                    break

                # Determine active bodies still not done
                active_in_round = [b for i, b in enumerate(batch) if not done_flags[i]]

                # Isolate active bodies: suppress already done bodies (Option B)
                suppress_others(active_in_round)

                # Apply candidate size for active bodies
                with Transaction(True):
                    for i, b in enumerate(batch):
                        if not done_flags[i] and sizings[i]:
                            c_sz = candidates[i][min(r, len(candidates[i]) - 1)]
                            try:
                                sizings[i].ElementSize = Quantity(c_sz, "mm")
                            except Exception:
                                pass

                # Mesh only active bodies
                with Transaction(True):
                    mesh.ClearGeneratedData()
                    mesh.GenerateMesh()

                # Evaluate active bodies
                new_cfls = evaluate_cfl_fast(batch)

                # Check convergence & lock best
                for i in range(len(batch)):
                    if not done_flags[i]:
                        cur_applied = candidates[i][min(r, len(candidates[i]) - 1)]
                        cfl_val = new_cfls[i]
                        if cfl_val > best_cfls[i]:
                            best_cfls[i] = cfl_val
                            best_sizes[i] = cur_applied

                        if cfl_val >= target_cfl:
                            done_flags[i] = True
                            print("  [Option B Locked] Body '{}' met target at size {:.2f} mm (CFL: {:.2e} s)".format(
                                batch[i].Name, cur_applied, cfl_val))

            # Record batch results
            for i, b in enumerate(batch):
                results_record.append({
                    "Name": b.Name,
                    "BodyType": b.GetGeoBody().BodyType.ToString(),
                    "Initial_CFL": base_cfls[i],
                    "Optimized_CFL": best_cfls[i],
                    "Final_Size_mm": best_sizes[i] if best_sizes[i] else "Unchanged",
                    "Target_Met": done_flags[i]
                })

    finally:
        # Guarantee cleanup: unsuppress all bodies
        print("\n[Cleanup] Unsuppressing all bodies back to original state...")
        with Transaction(True):
            for b in all_bodies:
                b.Suppressed = False
        mesh.ClearGeneratedData()
        mesh.GenerateMesh()

    elapsed = time.time() - start_time

    # 3. Export CSV Report
    if output_csv_dir is None:
        try:
            output_csv_dir = DataModel.Project.SaveDirectory
        except Exception:
            output_csv_dir = os.getcwd()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = "MeshTuner_Report_{}.csv".format(timestamp)
    csv_path = os.path.join(output_csv_dir, csv_filename)

    try:
        with open(csv_path, "wb" if sys.version_info[0] < 3 else "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Body_Name", "Body_Type", "Initial_CFL_sec", "Optimized_CFL_sec", "Final_Size_mm", "Target_Met"])
            for r in results_record:
                writer.writerow([r["Name"], r["BodyType"], "{:.4e}".format(r["Initial_CFL"]),
                                 "{:.4e}".format(r["Optimized_CFL"]), r["Final_Size_mm"], r["Target_Met"]])
        print("[CSV Export] Saved tuning report to: {}".format(csv_path))
    except Exception as ex:
        print("[Warning] Could not export CSV report: {}".format(ex))

    # 4. Summary Card Output
    met_count = sum(1 for r in results_record if r["Target_Met"])
    print("\n" + "=" * 50)
    print("         FAST CFL MESH TUNER RESULTS")
    print("=" * 50)
    print("Total Bodies Processed : {}".format(len(results_record)))
    print("CFL Target Met         : {} / {} ({:.1f}%)".format(met_count, len(results_record), met_count * 100.0 / len(results_record) if results_record else 0))
    print("Total Elapsed Time     : {:.1f} seconds ({:.2f} mins)".format(elapsed, elapsed / 60.0))
    print("CSV Report Path        : {}".format(csv_path))
    print("=" * 50)
    return True

if __name__ == "__main__":
    run_fast_cfl_tuner()
