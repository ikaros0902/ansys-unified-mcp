import traceback

result = {}
try:
    root = GetRootPart()
    
    # 1. Target component filters
    # User requested: RM21951J009-FRONT-PANEL, SI-0058-60H703000-904, and any component with "screw" in name
    
    all_comps = list(root.GetAllComponents())
    
    deleted_comps = []
    deleted_comp_count = 0
    
    for c in all_comps:
        cname = c.GetName()
        cname_lower = cname.lower()
        
        should_delete = False
        if "rm21951j009-front-panel" in cname_lower:
            should_delete = True
        elif "si-0058-60h703000-904" in cname_lower:
            should_delete = True
        elif "screw" in cname_lower:
            should_delete = True
            
        if should_delete:
            try:
                c.Delete()
                deleted_comps.append(cname)
                deleted_comp_count += 1
            except Exception:
                pass

    # 2. Delete zero-thickness / sliver bodies across all remaining bodies
    all_bodies = list(root.GetAllBodies())
    deleted_slivers = 0
    
    for b in all_bodies:
        try:
            vol = getattr(b.Shape, 'Volume', 0.0)
            area = getattr(b.Shape, 'SurfaceArea', 0.0)
            
            # Check if volume is essentially 0 or effective thickness is less than 0.001 mm
            eff_thickness = (2.0 * vol / area) if area > 0 else 0.0
            
            if vol < 1e-15 or eff_thickness < 1e-6:
                b.Delete()
                deleted_slivers += 1
        except Exception:
            pass

    # 3. Final count
    final_comps = list(root.GetAllComponents())
    final_bodies = list(root.GetAllBodies())

    result["status"] = "success"
    result["deleted_components_count"] = str(deleted_comp_count)
    result["deleted_components_unique"] = str(list(set(deleted_comps)))
    result["deleted_sliver_bodies_count"] = str(deleted_slivers)
    result["final_components_count"] = str(len(final_comps))
    result["final_bodies_count"] = str(len(final_bodies))

except Exception as e:
    result["status"] = "error"
    result["error"] = str(e)
    result["traceback"] = traceback.format_exc()
