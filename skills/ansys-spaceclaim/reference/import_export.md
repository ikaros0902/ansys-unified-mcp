# Import / Export — condensed API

CAD exchange for the geometry path. Verified from the project's geometry tools.

## Import CAD

```
geometry_import_file(file_path)      # import a CAD file into the active design
```

Supported formats follow the geometry service's importer (STEP, IGES, and native
CAD). After import, list what came in with `geometry_list_bodies()`.

## Export

```
geometry_export(file_path, format="step")   # format: "step" | "iges"
```

- `format="step"` (default) or `"iges"`.
- `file_path` is the output path on the machine running the geometry service.

## Notes

- Prefer STEP for downstream Mechanical/meshing unless IGES is required.
- Import/export go through the geometry service, so a modeler must be connected
  (`geometry_launch`) and a design active (`geometry_create_design`) first.

## MCP tools that use this

`geometry_import_file`, `geometry_export`.
