# Geometry Cleanup Examples (SpaceClaim & PyAnsys Geometry)

This directory contains automated CAD preprocessing scripts for defeaturing and cleaning complex CAD assemblies in ANSYS SpaceClaim before structural or shock simulation.

## Overview of Scripts

1. **`execute_cleanup.py`**
   - **Engine**: PyAnsys Geometry Modeler (`ansys.geometry.core.Modeler`)
   - **Connection**: gRPC `127.0.0.1:50051`
   - **Operations**: Hierarchical traversal of the design tree, deleting target non-structural hardware components, broken drive trays, and isolated surface bodies.

2. **`sc_fast_cleanup.py`**
   - **Engine**: Native SpaceClaim Scripting (IronPython API)
   - **Operations**: Rapid deletion of specified hardware parts (`JVHDW*`, `JVCBL*`, `RM13925*`), and automated removal of zero-volume surface bodies across the entire model.

3. **`sc_delete_screws_and_panels.py`**
   - **Engine**: Native SpaceClaim Scripting (IronPython API)
   - **Operations**: Regex-based component filtering (deleting front panels, chassis brackets, and all screw fasteners) and sliver/zero-thickness body purging based on effective thickness threshold (`2 * vol / area < 1e-6`).

## Usage

### PyAnsys Geometry Automation
```powershell
python examples/geometry_cleanup/execute_cleanup.py
```

### SpaceClaim Native Script Execution
Load `sc_fast_cleanup.py` or `sc_delete_screws_and_panels.py` directly into the SpaceClaim Script Editor or run via ANSYS Unified MCP SpaceClaim tools.
