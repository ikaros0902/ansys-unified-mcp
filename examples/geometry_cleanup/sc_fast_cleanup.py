import traceback

result = {}
try:
    root = GetRootPart()
    
    # 1. Target component names to delete
    targets = [
        "JVHDW1075483", "JVHDW1077654", "JVDCM1080419",
        "JVHDW1054818", "JVMIS1075491", "JVMIS1075492",
        "JVDCM1081529", "JVDCM1081530", "JVDCM1083989",
        "JVCBL1075407", "JVCBL1075408", "JVHDW1081109",
        "RM13925-2_5-HDD-TRAY-LESS", "251_HDD_TRAY", "251_HDD_TRAY-CAM"
    ]
    
    # Get all components before deletion
    all_comps = list(root.GetAllComponents())
    
    deleted_comps = []
    deleted_comp_count = 0
    
    for c in all_comps:
        cname = c.GetName()
        if any(t in cname for t in targets):
            try:
                c.Delete()
                deleted_comps.append(cname)
                deleted_comp_count += 1
            except Exception:
                pass

    # 2. Get all remaining bodies and delete zero-volume surface bodies
    remaining_bodies = list(root.GetAllBodies())
    deleted_surfaces_count = 0
    remaining_solids_count = 0
    
    for b in remaining_bodies:
        try:
            vol = b.Shape.Volume
            if vol == 0.0 or vol is None:
                b.Delete()
                deleted_surfaces_count += 1
            else:
                remaining_solids_count += 1
        except Exception:
            pass

    # 3. Count final structure
    final_comps = list(root.GetAllComponents())
    final_bodies = list(root.GetAllBodies())

    result["status"] = "success"
    result["deleted_components_count"] = str(deleted_comp_count)
    result["deleted_components_sample"] = str(list(set(deleted_comps)))
    result["deleted_surface_bodies_count"] = str(deleted_surfaces_count)
    result["final_components_count"] = str(len(final_comps))
    result["final_bodies_count"] = str(len(final_bodies))
    
except Exception as e:
    result["status"] = "error"
    result["error"] = str(e)
    result["traceback"] = traceback.format_exc()
