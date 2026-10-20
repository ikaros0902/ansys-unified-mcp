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

### Export the active design with PyAnsys Geometry

For a whole active design, read the service's current design with
`read_existing_design()` and use `Design.export_to_step(output_dir)`. This is a whole-design export; it does not
select one assembly component. The small CPython example
[`export_active_design_step.py`](../scripts/export_active_design_step.py)
accepts a host, port, and output directory and checks the returned file.

```python
modeler = Modeler(host=host, port=port, transport_mode="insecure", timeout=60)
design = modeler.read_existing_design()
if design is None or not design.is_active:
    raise RuntimeError("No active design on the connected service")
step_path = design.export_to_step(output_dir)
```

`Modeler` starts without a local `Design` object; call `read_existing_design()`
to read the service's current design. This helper attaches to an existing
service and does not close its session. Reading a very large design may
transfer substantial geometry data; use native component extraction when the
goal is a small subcomponent.

The SDK names the result `<design.name>.stp` inside `output_dir` and overwrites
that file if it already exists. The bundled CLI checks the derived path and
refuses to overwrite an existing file before calling the SDK.
Set `PYGEOMETRY_MAX_MESSAGE_LENGTH` before importing PyAnsys only when a
measured payload requires it; raising the limit does not fix a wrong endpoint.

## Notes

- Prefer STEP for downstream Mechanical/meshing unless IGES is required.
- 匯入／匯出前需確認 modeler 已連線，並有正確的作用中設計。若 GUI 已開啟模型，沿用該設計，不要再呼叫 `geometry_create_design`。
- `geometry_export` 的一般包裝不等於選取元件匯出。大型組立的獨立子件另存、訊息限制與重新匯入驗證，參閱 [元件擷取與查表建庫技能](../../ansys-spaceclaim-component-library/SKILL.md)。
- 元件樹盤點及單一元件另存工具亦收錄於 [元件擷取技能](../../ansys-spaceclaim-component-library/SKILL.md)；勿用整個作用中設計的匯出代替子件擷取。
- `.scdoc` 要求可能產生 `.scdocx` 並帶入整機資料；須查實際檔名與幾何範圍，不能僅以 Save 成功判定獨立元件已保存。

## MCP tools that use this

`geometry_import_file`, `geometry_export`.
