# ANSYS Documentation Skills Index

Per-product skills over the ANSYS documentation. Each skill is a lightweight
**outline (`SKILL.md`) + a `reference/` folder of condensed, function-organized
API files**. The agent loads only the one `reference/<function>.md` it needs, so
it never has to read the multi-MB source guides.

- **Category granularity** follows how PyAnsys organizes its libraries
  (PyMechanical / PyAnsys Geometry / PyDYNA / PyOptiSLang).
- **API content** is the native API the ANSYS MCP actually dispatches (ACT for
  Mechanical, PyAnsys Geometry / native SpaceClaim, native optiSLang Python,
  LS-DYNA `*KEYWORD` deck, LS-PrePost SCL/cfile/Python).
- Each reference file cross-references the **MCP tools** that use that API, and
  falls back to `search_ansys_docs` / `get_ansys_doc_chunk` for anything not
  condensed.

## Skills & their reference categories

| Skill | Product | reference/ files |
|---|---|---|
| `ansys-mechanical` | mechanical (ACT) | act_scripting_foundation, geometry_and_selections, mesh, mesh_controls_advanced, materials, connections_and_contacts, boundary_conditions_and_loads, construction_geometry, analysis_setup, meshdata_and_elements, results_and_postprocessing, lsdyna_via_mechanical |
| `ansys-spaceclaim` | spaceclaim / geometry | PyAnsys Geometry: session, sketching, modeling, design_and_bodies, import_export · Native V2x: native_session_and_versions, native_selection, native_commands, native_sketch_and_geometry, native_helpers_and_transaction |
| `ansys-optislang` | optislang | session_and_project, nodes_and_actors, parameters_and_responses, algorithms, designs_and_results |
| `ansys-lsdyna` | lsdyna (keyword deck) | materials, elements_sections_parts, contact_and_constraints, loads_and_initial, control_and_output, specialized_solvers |
| `ansys-ls-prepost` | ls-prepost (SCL/cfile/Python) | session_and_cfile, model_query, states_and_results, model_build, output_export, python_module_interface |
| `act-extension-development` | ACT plugin dev (實戰) | *(inline)* IronPython quirks, FileSystemWatcher pattern, Wizard API, WPF Dispatcher |
| `pymechanical-operations` | PyMechanical gRPC (實戰) | *(inline)* gRPC connect, remote script, Scoping API, Mesh automation |
| `ansys-error-catalog` | 錯誤分類目錄 (實戰) | workbench_act, mechanical_scripting, spaceclaim_pygeometry, ironpython_general |

## ACT extensions (Mechanical/SpaceClaim)

ACT is not a separate skill — an ACT extension is just a workflow that strings
these product APIs together behind an XML wizard. The APIs its Python callbacks
use live in the product skills:

- Mechanical ACT callbacks (`onupdateStep(step)`, `ExtAPI`/`DataModel`/`Model`,
  selection, mesh controls, remote points, construction geometry, LS-DYNA-via-
  Mechanical) → `ansys-mechanical` (start at `act_scripting_foundation.md`).
- SpaceClaim ACT callbacks (native `SpaceClaim.Api.V<ver>`) → `ansys-spaceclaim`
  `native_*` files.
- The XML wizard/step/property/callback packaging itself is workflow glue, not an
  API; the authoritative reference is the ACT Customization/API/XML guides (not in
  the MCP index; available under `ACT_Test/3.documents/md`).
- **ACT 外掛開發的實戰陷阱**（IronPython 閉包限制、模組 reload、WPF Dispatcher）
  → `act-extension-development` skill。

## API layer per product (what the MCP dispatches)

- **ansys-mechanical** — ACT scripting (`ExtAPI`, `DataModel`, `Model.Add*`), run
  via `run_mechanical_script` / `execute_mechanical_script_live` and the
  `add_*` / `generate_mesh` / `solve_analysis` convenience tools.
- **ansys-spaceclaim** — PyAnsys Geometry (`ansys.geometry.core`: `Sketch`,
  `extrude_sketch`, `revolve_sketch`) via the `geometry_*` tools; plus native
  SpaceClaim Python via `execute_spaceclaim_script_live`.
- **ansys-optislang** — native optiSLang Python (`actors.*`, `add_actor`) run
  through `run_optislang_script`; session via `connect_optislang` /
  `start_optislang_project`.
- **ansys-lsdyna** — LS-DYNA `*KEYWORD` deck. No MCP dispatch tool; pure
  documentation reference (build in LS-PrePost, launch with LS-Run).
- **ansys-ls-prepost** — LS-PrePost SCL / cfile / Python data-center API. No MCP
  dispatch tool; pure documentation reference.

## How categories were derived

Categories were aligned with the PyAnsys project organization:

- **PyMechanical** — simulation workflow (geometry → mesh → materials →
  connections → loads/BCs → analysis → results).
- **PyAnsys Geometry** — getting started / sketching / modeling / design I/O.
- **PyOptiSLang** — session / actors (nodes) / parameters & responses /
  algorithms / designs.
- **PyDYNA** — keyword families (consolidated: Mat, Element/Section/Part,
  Contact/Constrained/Boundary, Load/Initial, Control/Database, specialized
  solvers).
- **LS-PrePost** — no PyAnsys equivalent; categories derived from the
  `lsppscripting` doc workflow.

## Underlying doc index

- Raw markdown: `Documentation_md/<name>.md`.
- Cleaned/indexed copies: `Documentation_clean/` with the FTS5 index at
  `Documentation_clean/docs_index.sqlite` (classified by `product` and
  `category`: `api_reference`, `api_scripting`, `guide`, `tutorial`).
- MCP doc tools: `list_ansys_docs`, `search_ansys_docs(query, scope, doc, top_k)`,
  `get_ansys_doc_chunk(doc, chunk_id, context)`.
- FTS is keyword/substring — use single, exact API tokens; multi-word
  natural-language queries often return nothing.

## Other skills in this workspace

- `pdf-to-md` — convert source PDFs (`Documentation/`) to markdown
  (`Documentation_md/`). Upstream of the doc-index pipeline.
- `act-extension-development` — ACT 外掛開發實戰知識：IronPython 陷阱、
  FileSystemWatcher 非同步架構、ACT Wizard 程式化呼叫。
- `pymechanical-operations` — PyMechanical gRPC 遠端操作：連線、Scoping API、
  Mesh 控制自動化。
- `ansys-error-catalog` — 錯誤分類目錄：按模組（Workbench/Mechanical/SpaceClaim/IronPython）
  和 function 分類的錯誤紀錄與解決方案。
