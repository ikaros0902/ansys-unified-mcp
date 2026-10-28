# PyAnsys Source Intelligence

## Scope

This inventory covers the current `ansys-unified-mcp` checkout and its `.venv` only. It does not cover every PyAnsys repository or ANSYS installation on this machine.

No upstream PyAnsys SDK source checkout has been confirmed. The sibling project `F:\Ming_python\pyansys-common-mcp` is a separate MCP project. Its name does not prove that it is an upstream SDK repository.

## Current evidence

| Evidence | Current state | Limit |
| --- | --- | --- |
| CodeGraph | Full index rebuilt on 2026-10-29. It indexed 469 files, 7,633 nodes, and 17,271 edges. | The graph covers this checkout. It does not include external SDK repositories. |
| Serena | Connected in this session. It returned current symbols from the active checkout. | A symbol lookup does not prove complete repository coverage. |
| codebase-memory-mcp | One project has 9,272 nodes and 23,992 edges. Its index date is 2026-10-21. Watch is disabled. | The index predates current files. Three files are partially parsed, and five directories are excluded by design. No re-index operation is available in the exposed tools. |
| Graphify | A local report dated 2026-10-26 records 746 files, 8,745 nodes, and 16,102 edges. | This is an older local report. Do not use it as current graph coverage. |
| SDK dictionaries | Ten versioned package snapshots are listed in the local-only `docs/api_inventory/curated/sdk/index.md`. | A captured package version does not identify an ANSYS product release or prove runtime behavior. |
| Installed packages | The current `.venv` has 49 `ansys-*` or `pyaedt` distributions. Fifteen of the 25 SDK package names in the product manifest are installed. | This is a project environment inventory. It does not describe global Python or other ANSYS installations. |

The local package and dependency inventory is in the ignored file `.audit/repo-restructure/pyansys-source-intelligence/current_environment.json`. It records distribution versions, declared requirements, 142 dependency edges between installed ANSYS packages, and the 25 manifest SDK package names. Keep this inventory local until its publication scope is approved.

## Versioned SDK snapshots

| Source key | Distribution | Captured version |
| --- | --- | --- |
| `dpf` | `ansys-dpf-core` | `0.16.1` |
| `fluent` | `ansys-fluent-core` | `0.42.1` |
| `geometry_core` | `ansys-geometry-core` | `0.17.1` |
| `mapdl` | `ansys-mapdl-core` | `0.74.1` |
| `mechanical_core` | `ansys-mechanical-core` | `0.13.2` |
| `optislang_core` | `ansys-optislang-core` | `1.6.0` |
| `primemesh` | `ansys-meshing-prime` | `0.10.5` |
| `pydyna` | `ansys-dyna-core` | `0.12.1` |
| `sound` | `ansys-sound-core` | `0.3.0` |
| `workbench` | `ansys-workbench-core` | `0.14.0` |

Other installed distributions, including Sherlock and Rocky, do not have SDK member dictionaries in this index. Their installed state is not evidence that their APIs have been captured.

## Dependency and source map

`pyproject.toml` groups optional SDK dependencies by product domain. `uv.lock` records resolved package versions. The local JSON inventory records package metadata and dependency edges. The SDK dictionary index records the ten captured public-symbol snapshots. These are separate evidence layers:

1. Project dependency declarations show intended optional package groups.
2. Lock entries show resolved dependency versions.
3. Installed distribution metadata shows what is present in this `.venv`.
4. SDK snapshots show symbols captured by the existing extractors.
5. Upstream source repositories and product-host behavior remain separate and are not covered by this map.

## Remaining work

- Identify which upstream PyAnsys repositories belong in scope. Do not treat every sibling MCP project as an SDK checkout.
- Add source checkout references and commit IDs after those repositories are available and their use is authorized.
- Generate module and symbol graphs from those source checkouts. Keep one graph per repository and record its source revision.
- Refresh codebase-memory before relying on its graph. It was read-only in this session and its exposed watch is disabled.
- Add a versioned SDK snapshot only when the extractor can capture that package without starting an ANSYS host or solver.

Stage 3 is in progress. This report documents the current local package and graph evidence. It does not claim a complete PyAnsys source graph.
