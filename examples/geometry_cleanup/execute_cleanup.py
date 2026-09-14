import time
from collections import defaultdict
from ansys.geometry.core import Modeler

def execute_cleanup():
    print("Connecting to SpaceClaim Modeler at 127.0.0.1:50051...")
    modeler = Modeler(host='127.0.0.1', port=50051, transport_mode='insecure')
    
    print("Reading active design...")
    design = modeler.read_existing_design()
    if not design:
        print("Error: Could not read active design.")
        return

    print(f"Active Design: {design.name}")

    target_names = ["JVHDW1075483", "JVHDW1077654", "JVDCM1080419"]
    broken_tray_names = ["RM13925-2_5-HDD-TRAY-LESS", "251_HDD_TRAY", "251_HDD_TRAY-CAM"]

    deleted_named_comps = 0
    deleted_tray_comps = 0
    deleted_surface_bodies = 0

    # 1. First pass: Find and delete specific named components and broken tray components
    # We do a bottom-up traversal or recursive search
    def cleanup_components(parent):
        nonlocal deleted_named_comps, deleted_tray_comps, deleted_surface_bodies
        
        # Make a copy of components list since we will delete from parent
        try:
            subcomps = list(parent.components)
        except Exception:
            subcomps = []

        for c in subcomps:
            c_name = c.name or ""
            # Check if matching user specified delete list
            if any(target in c_name for target in target_names):
                try:
                    print(f"Deleting target component: {c_name} (ID: {c.id})")
                    parent.delete_component(c)
                    deleted_named_comps += 1
                    continue
                except Exception as e:
                    print(f"Error deleting component {c_name}: {e}")

            # Check if matching broken tray components
            if any(tray in c_name for tray in broken_tray_names):
                try:
                    print(f"Deleting broken tray component: {c_name} (ID: {c.id}) with all surface bodies")
                    parent.delete_component(c)
                    deleted_tray_comps += 1
                    continue
                except Exception as e:
                    print(f"Error deleting broken tray {c_name}: {e}")

            # Recurse into children first
            cleanup_components(c)

            # Check remaining bodies in component for is_surface == True
            try:
                bodies = list(c.bodies)
            except Exception:
                bodies = []

            for b in bodies:
                try:
                    if getattr(b, 'is_surface', False):
                        c.delete_body(b)
                        deleted_surface_bodies += 1
                except Exception as e:
                    pass

        # Check bodies on parent itself
        try:
            p_bodies = list(parent.bodies)
        except Exception:
            p_bodies = []

        for b in p_bodies:
            try:
                if getattr(b, 'is_surface', False):
                    parent.delete_body(b)
                    deleted_surface_bodies += 1
            except Exception as e:
                pass

    print("\nExecuting cleanup on design components...")
    cleanup_components(design)

    print("\n--- Cleanup Results ---")
    print(f"Deleted specified components ({target_names}): {deleted_named_comps}")
    print(f"Deleted broken tray components ({broken_tray_names}): {deleted_tray_comps}")
    print(f"Deleted individual surface bodies: {deleted_surface_bodies}")

    # Re-read design to verify state
    print("\nRe-reading design after cleanup...")
    time.sleep(2)
    updated_design = modeler.read_existing_design()
    print(f"Updated Design: {updated_design.name}")
    print(f"Root components remaining: {len(updated_design.components)}")
    
    total_remaining_bodies = 0
    total_remaining_comps = 0
    remaining_surfaces = 0

    def count_remaining(comp):
        nonlocal total_remaining_bodies, total_remaining_comps, remaining_surfaces
        total_remaining_comps += 1
        for b in comp.bodies:
            total_remaining_bodies += 1
            if getattr(b, 'is_surface', False):
                remaining_surfaces += 1
        for sc in comp.components:
            count_remaining(sc)

    for c in updated_design.components:
        count_remaining(c)

    print(f"Total remaining components: {total_remaining_comps}")
    print(f"Total remaining bodies: {total_remaining_bodies} (Surfaces: {remaining_surfaces})")

if __name__ == "__main__":
    execute_cleanup()
