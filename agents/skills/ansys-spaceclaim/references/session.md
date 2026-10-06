# Session & Connect — condensed API

How to reach a live modeler/design, and the two scripting paths. Verified from
the project's geometry driver (`ansys.geometry.core`).

## MCP tools (simplest path)

- `geometry_launch(port?, host, transport_mode, connect_timeout)` — launch or connect to a Geometry/SpaceClaim service.
- **嚴禁調用 `geometry_create_design()`**：不要創建新設計或開啟新分頁，直接使用當前現有的 Design 進行建模。
- `geometry_list_bodies()` — list bodies in the active design.
- `geometry_status()` / `geometry_close()` — connection status / shutdown.

## PyAnsys Geometry objects (for execute-style scripting)

```python
# 嚴禁調用 modeler.create_design() 創建新設計分頁！
# 直接取得當前使用中的 Design:
design = modeler.active_design or modeler.get_active_design()
```

- 一律在現有/當前的 `Design` 上直接繪製草圖與建立實體。
- Bodies are created by extruding/revolving sketches on the current design (see `modeling.md`).

## Native SpaceClaim Python path

`execute_spaceclaim_script_live(script, system_name="", timeout_seconds=120)`
sends a **SpaceClaim Python** script to the live SpaceClaim window through the
Workbench bridge. This is the SpaceClaim recorded-script API (different from
PyAnsys Geometry). For its exact calls, search `SpaceClaim_Documentation`:

```
search_ansys_docs("<operation>", scope="all")   # e.g. "component", "named selection"
```

## MCP tools that use this

`geometry_launch`, `geometry_create_design`, `geometry_status`,
`geometry_close`, `geometry_list_bodies`, `execute_spaceclaim_script_live`.
