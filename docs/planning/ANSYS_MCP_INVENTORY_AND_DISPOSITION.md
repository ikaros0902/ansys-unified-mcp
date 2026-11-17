# ANSYS MCP 工具與 Skill 逐項清冊

基準日為 2026-11-17（台北），本機 HEAD 為 `130208d`。這份表列出本次 Codex 工具目錄與本機 Python 裝飾器靜態掃描共同確認的 **218 個主要工具名稱**。掃描涵蓋 `src/ansys_unified_mcp/products`、`src/ansys_unified_mcp/tools` 的工具入口；核對結果為 218 對 218，差集皆為空，每個名稱對應一個原始碼位置。舊別名與僅經內部／動態路由可見的能力另按 [主計畫](ANSYS_MCP_EVOLUTION_PLAN.md) 驗收。工具可見僅表示可被發現。

每列是規劃建議，尚未變更工具。P0 先核對運行後端，P1 精簡入口，P2 試點官方 Mechanical，P3 更新工程流程與 Skill，P4 評估其他官方產品。「標記後端」要求先查清楚實際執行路徑，每個工具各自驗證，不預先判定整個產品都走基準引擎。跨域用法由主計畫的產品矩陣補充。

| 建議處置 | 工具數 |
| --- | ---: |
| P3 · 按需 | 91 |
| P1 · 保留 | 42 |
| P1 · 整併 | 4 |
| P1 · 管理用途 | 1 |
| P3 · Skill 主導 | 23 |
| P0 · 標記後端 | 30 |
| P4 · 官方候選 | 19 |
| P2 · 官方試點 | 8 |
| 合計 | 218 |

## API 知識庫（8）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`ans_search_official_examples`](../../src/ansys_unified_mcp/tools/apikb_tools.py#L145) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`api_cross_bridge`](../../src/ansys_unified_mcp/tools/apikb_tools.py#L314) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`api_federated_path`](../../src/ansys_unified_mcp/tools/apikb_tools.py#L230) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`api_federated_search`](../../src/ansys_unified_mcp/tools/apikb_tools.py#L272) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`api_get`](../../src/ansys_unified_mcp/tools/apikb_tools.py#L46) | P1 · 保留 | 日常或相關產品公開 |
| [`api_path`](../../src/ansys_unified_mcp/tools/apikb_tools.py#L97) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`api_search`](../../src/ansys_unified_mcp/tools/apikb_tools.py#L23) | P1 · 保留 | 日常或相關產品公開 |
| [`api_validate_script`](../../src/ansys_unified_mcp/tools/apikb_tools.py#L120) | P1 · 保留 | 日常或相關產品公開 |

## 版本與安裝（3）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`ans_list_installed_versions`](../../src/ansys_unified_mcp/tools/connection_tools.py#L83) | P1 · 保留 | 日常或相關產品公開 |
| [`ans_set_active_version`](../../src/ansys_unified_mcp/tools/connection_tools.py#L116) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`check_ansys_installation`](../../src/ansys_unified_mcp/tools/connection_tools.py#L47) | P1 · 整併 | 保留舊呼叫相容；日常只呈現主要入口 |

## 文件檢索（5）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`ans_get_knowledge_dictionary`](../../src/ansys_unified_mcp/tools/docs_tools.py#L143) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`get_ansys_doc_chunk`](../../src/ansys_unified_mcp/tools/docs_tools.py#L111) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`list_ansys_docs`](../../src/ansys_unified_mcp/tools/docs_tools.py#L28) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`rebuild_ansys_docs_index`](../../src/ansys_unified_mcp/tools/docs_tools.py#L130) | P1 · 管理用途 | 維護用入口；預設工程工作階段收起 |
| [`search_ansys_docs`](../../src/ansys_unified_mcp/tools/docs_tools.py#L67) | P1 · 保留 | 日常或相關產品公開 |

## 工程工作流程（5）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`workflow_run_drop_test`](../../src/ansys_unified_mcp/tools/intent_tools.py#L43) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`workflow_run_random_vibration`](../../src/ansys_unified_mcp/tools/intent_tools.py#L155) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`workflow_run_shock_analysis`](../../src/ansys_unified_mcp/tools/intent_tools.py#L105) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`workflow_run_thermal_warpage`](../../src/ansys_unified_mcp/tools/intent_tools.py#L211) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`workflow_train_surrogate_model`](../../src/ansys_unified_mcp/tools/intent_tools.py#L259) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |

## 工具路由（2）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`ans_call_domain_tool`](../../src/ansys_unified_mcp/tools/meta_router_tools.py#L782) | P1 · 保留 | 日常或相關產品公開 |
| [`ans_list_domain_tools`](../../src/ansys_unified_mcp/tools/meta_router_tools.py#L693) | P1 · 保留 | 日常或相關產品公開 |

## 作業管理（4）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`abort_simulation_job`](../../src/ansys_unified_mcp/tools/sentinel_tools.py#L90) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`get_simulation_status`](../../src/ansys_unified_mcp/tools/sentinel_tools.py#L59) | P1 · 保留 | 日常或相關產品公開 |
| [`submit_simulation_job`](../../src/ansys_unified_mcp/tools/sentinel_tools.py#L36) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`tail_simulation_log`](../../src/ansys_unified_mcp/tools/sentinel_tools.py#L74) | P1 · 保留 | 日常或相關產品公開 |

## 工作階段管理（6）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`ans_session_connect`](../../src/ansys_unified_mcp/tools/session_manager_tools.py#L115) | P1 · 保留 | 日常或相關產品公開 |
| [`ans_session_diagnose`](../../src/ansys_unified_mcp/tools/session_manager_tools.py#L35) | P1 · 保留 | 日常或相關產品公開 |
| [`ans_session_disconnect`](../../src/ansys_unified_mcp/tools/session_manager_tools.py#L161) | P1 · 保留 | 日常或相關產品公開 |
| [`ans_session_launch`](../../src/ansys_unified_mcp/tools/session_manager_tools.py#L134) | P1 · 保留 | 日常或相關產品公開 |
| [`ans_session_set_workspace`](../../src/ansys_unified_mcp/tools/session_manager_tools.py#L185) | P1 · 保留 | 日常或相關產品公開 |
| [`ans_session_status`](../../src/ansys_unified_mcp/tools/session_manager_tools.py#L149) | P1 · 保留 | 日常或相關產品公開 |

## 聲學計算（3）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`sound_calculate_sharpness`](../../src/ansys_unified_mcp/tools/sound_tools.py#L189) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`sound_calculate_sound_pressure_level`](../../src/ansys_unified_mcp/tools/sound_tools.py#L63) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`sound_calculate_zwicker_loudness`](../../src/ansys_unified_mcp/tools/sound_tools.py#L114) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |

## AEDT（4）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`aedt_check_connection`](../../src/ansys_unified_mcp/products/aedt/tools.py#L13) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`aedt_extract_rlcg`](../../src/ansys_unified_mcp/products/aedt/tools.py#L114) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`aedt_solve_hfss`](../../src/ansys_unified_mcp/products/aedt/tools.py#L27) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`aedt_solve_maxwell`](../../src/ansys_unified_mcp/products/aedt/tools.py#L75) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |

## AQWA（2）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`aqwa_check_connection`](../../src/ansys_unified_mcp/products/aqwa/tools.py#L13) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`aqwa_solve_heave_oscillation`](../../src/ansys_unified_mcp/products/aqwa/tools.py#L27) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |

## Chemkin（2）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`chemkin_check_connection`](../../src/ansys_unified_mcp/products/chemkin/tools.py#L13) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`chemkin_solve_0d_reactor`](../../src/ansys_unified_mcp/products/chemkin/tools.py#L27) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |

## DPF（2）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`dpf_extract_structural_results`](../../src/ansys_unified_mcp/products/dpf/tools.py#L15) | P1 · 保留 | 日常或相關產品公開 |
| [`dpf_get_model_summary`](../../src/ansys_unified_mcp/products/dpf/tools.py#L29) | P1 · 保留 | 日常或相關產品公開 |

## LS-DYNA（7）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`dyna_create_keyword_deck`](../../src/ansys_unified_mcp/products/dyna/tools.py#L18) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`dyna_export_keyword_file`](../../src/ansys_unified_mcp/products/dyna/tools.py#L34) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`dyna_list_keyword_types`](../../src/ansys_unified_mcp/products/dyna/tools.py#L51) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`dyna_run_prepost`](../../src/ansys_unified_mcp/products/dyna/tools.py#L100) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`dyna_solve`](../../src/ansys_unified_mcp/products/dyna/tools.py#L60) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`lsdyna_setup_drop_test`](../../src/ansys_unified_mcp/products/dyna/tools.py#L158) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`lsdyna_setup_shock_analysis`](../../src/ansys_unified_mcp/products/dyna/tools.py#L129) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |

## Fluent（19）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`fluent_exit`](../../src/ansys_unified_mcp/products/fluent/tools.py#L222) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`fluent_get_mapping_report`](../../src/ansys_unified_mcp/products/fluent/tools.py#L238) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`fluent_get_residuals`](../../src/ansys_unified_mcp/products/fluent/tools.py#L139) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`fluent_get_script`](../../src/ansys_unified_mcp/products/fluent/tools.py#L230) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`fluent_hook_udf`](../../src/ansys_unified_mcp/products/fluent/tools.py#L191) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`fluent_initialize`](../../src/ansys_unified_mcp/products/fluent/tools.py#L117) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`fluent_iterate`](../../src/ansys_unified_mcp/products/fluent/tools.py#L128) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`fluent_launch`](../../src/ansys_unified_mcp/products/fluent/tools.py#L21) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`fluent_list_udfs`](../../src/ansys_unified_mcp/products/fluent/tools.py#L211) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`fluent_load_udf`](../../src/ansys_unified_mcp/products/fluent/tools.py#L177) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`fluent_read_case`](../../src/ansys_unified_mcp/products/fluent/tools.py#L47) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`fluent_read_mesh`](../../src/ansys_unified_mcp/products/fluent/tools.py#L58) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`fluent_reset_mapper`](../../src/ansys_unified_mcp/products/fluent/tools.py#L246) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`fluent_save`](../../src/ansys_unified_mcp/products/fluent/tools.py#L147) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`fluent_set_boundary`](../../src/ansys_unified_mcp/products/fluent/tools.py#L86) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`fluent_set_material`](../../src/ansys_unified_mcp/products/fluent/tools.py#L103) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`fluent_set_solver`](../../src/ansys_unified_mcp/products/fluent/tools.py#L69) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`fluent_status`](../../src/ansys_unified_mcp/products/fluent/tools.py#L169) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`fluent_tui`](../../src/ansys_unified_mcp/products/fluent/tools.py#L158) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |

## Geometry／SpaceClaim（27）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`geometry_close`](../../src/ansys_unified_mcp/products/geometry/tools.py#L680) | P1 · 整併 | 保留舊呼叫相容；日常只呈現主要入口 |
| [`geometry_create_bga_array`](../../src/ansys_unified_mcp/products/geometry/tools.py#L374) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`geometry_create_block`](../../src/ansys_unified_mcp/products/geometry/tools.py#L74) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`geometry_create_cylinder`](../../src/ansys_unified_mcp/products/geometry/tools.py#L103) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`geometry_create_design`](../../src/ansys_unified_mcp/products/geometry/tools.py#L63) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`geometry_create_enclosure`](../../src/ansys_unified_mcp/products/geometry/tools.py#L181) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`geometry_create_hole_groups`](../../src/ansys_unified_mcp/products/geometry/tools.py#L432) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`geometry_create_sphere`](../../src/ansys_unified_mcp/products/geometry/tools.py#L129) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`geometry_defeature_features`](../../src/ansys_unified_mcp/products/geometry/tools.py#L340) | P1 · 保留 | 日常或相關產品公開 |
| [`geometry_execute_batch`](../../src/ansys_unified_mcp/products/geometry/tools.py#L689) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`geometry_export`](../../src/ansys_unified_mcp/products/geometry/tools.py#L562) | P1 · 保留 | 日常或相關產品公開 |
| [`geometry_get_bounding_box`](../../src/ansys_unified_mcp/products/geometry/tools.py#L602) | P1 · 保留 | 日常或相關產品公開 |
| [`geometry_import_file`](../../src/ansys_unified_mcp/products/geometry/tools.py#L661) | P1 · 保留 | 日常或相關產品公開 |
| [`geometry_imprint_contacts`](../../src/ansys_unified_mcp/products/geometry/tools.py#L414) | P1 · 保留 | 日常或相關產品公開 |
| [`geometry_launch`](../../src/ansys_unified_mcp/products/geometry/tools.py#L41) | P1 · 整併 | 保留舊呼叫相容；日常只呈現主要入口 |
| [`geometry_list_bodies`](../../src/ansys_unified_mcp/products/geometry/tools.py#L594) | P1 · 保留 | 日常或相關產品公開 |
| [`geometry_list_named_selections`](../../src/ansys_unified_mcp/products/geometry/tools.py#L632) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`geometry_midsurface`](../../src/ansys_unified_mcp/products/geometry/tools.py#L310) | P1 · 保留 | 日常或相關產品公開 |
| [`geometry_run_script`](../../src/ansys_unified_mcp/products/geometry/tools.py#L612) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`geometry_screenshot`](../../src/ansys_unified_mcp/products/geometry/tools.py#L512) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`geometry_simplify_heatsink`](../../src/ansys_unified_mcp/products/geometry/tools.py#L268) | P1 · 保留 | 日常或相關產品公開 |
| [`geometry_simplify_ram`](../../src/ansys_unified_mcp/products/geometry/tools.py#L219) | P1 · 保留 | 日常或相關產品公開 |
| [`geometry_simplify_ram_batch`](../../src/ansys_unified_mcp/products/geometry/tools.py#L243) | P1 · 保留 | 日常或相關產品公開 |
| [`geometry_sketch_and_extrude`](../../src/ansys_unified_mcp/products/geometry/tools.py#L152) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`geometry_status`](../../src/ansys_unified_mcp/products/geometry/tools.py#L672) | P1 · 整併 | 保留舊呼叫相容；日常只呈現主要入口 |
| [`geometry_suppress_and_hide`](../../src/ansys_unified_mcp/products/geometry/tools.py#L576) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`spaceclaim_run_script`](../../src/ansys_unified_mcp/products/geometry/tools.py#L708) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |

## Granta（4）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`granta_check_connection`](../../src/ansys_unified_mcp/products/granta/tools.py#L13) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`granta_evaluate_compliance`](../../src/ansys_unified_mcp/products/granta/tools.py#L49) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`granta_get_temperature_curve`](../../src/ansys_unified_mcp/products/granta/tools.py#L72) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`granta_search_material`](../../src/ansys_unified_mcp/products/granta/tools.py#L26) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |

## Icepak（2）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`icepak_check_connection`](../../src/ansys_unified_mcp/products/icepak/tools.py#L17) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`icepak_solve`](../../src/ansys_unified_mcp/products/icepak/tools.py#L31) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |

## MAPDL（3）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`mapdl_check_connection`](../../src/ansys_unified_mcp/products/mapdl/tools.py#L18) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`mapdl_run_apdl`](../../src/ansys_unified_mcp/products/mapdl/tools.py#L104) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`mapdl_solve_input`](../../src/ansys_unified_mcp/products/mapdl/tools.py#L32) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |

## Mechanical（46）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`mechanical_add_directional_deformation`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L362) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_add_displacement`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L290) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_add_equivalent_stress`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L355) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_add_fixed_support`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L187) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_add_force`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L193) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_add_frictionless_support`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L284) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_add_moment`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L343) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_add_pressure`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L205) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_add_principal_stress`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L370) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_add_reaction_force`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L382) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_add_remote_displacement`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L303) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_add_remote_force`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L331) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_add_standard_gravity`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L319) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_add_stress_tool`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L376) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_add_total_deformation`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L235) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_add_total_deformation_all_modes`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L229) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_assign_material`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L151) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_assign_materials_from_bom`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L683) | P1 · 保留 | 日常或相關產品公開 |
| [`mechanical_check_connection`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L121) | P2 · 官方試點 | 相同版本、連線和輸出驗收後才收起；試點前使用原工具 |
| [`mechanical_connect`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L84) | P2 · 官方試點 | 相同版本、連線和輸出驗收後才收起；試點前使用原工具 |
| [`mechanical_convert_part_to_point_mass`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L397) | P1 · 保留 | 日常或相關產品公開 |
| [`mechanical_convert_prefix_to_point_mass`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L388) | P1 · 保留 | 日常或相關產品公開 |
| [`mechanical_create_joints_from_groups`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L698) | P1 · 保留 | 日常或相關產品公開 |
| [`mechanical_delete_named_selection`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L265) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_diagnose_model_health`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L620) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_disconnect`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L111) | P2 · 官方試點 | 相同版本、連線和輸出驗收後才收起；試點前使用原工具 |
| [`mechanical_generate_mesh`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L171) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_generate_report`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L247) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_get_mesh_statistics`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L181) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_get_modal_frequencies`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L241) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_get_model_info`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L131) | P2 · 官方試點 | 相同版本、連線和輸出驗收後才收起；試點前使用原工具 |
| [`mechanical_get_solve_status`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L223) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_get_tree_hierarchy`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L672) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_launch`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L98) | P2 · 官方試點 | 相同版本、連線和輸出驗收後才收起；試點前使用原工具 |
| [`mechanical_list_boundary_conditions`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L211) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_list_instances`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L74) | P2 · 官方試點 | 相同版本、連線和輸出驗收後才收起；試點前使用原工具 |
| [`mechanical_list_materials`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L141) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_list_named_selections`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L259) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_list_point_masses`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L278) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_run_script`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L253) | P2 · 官方試點 | 相同版本、連線和輸出驗收後才收起；試點前使用原工具 |
| [`mechanical_set_mesh_element_size`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L161) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_setup_and_solve_modal`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L538) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`mechanical_setup_and_solve_static_structural`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L419) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`mechanical_solve_analysis`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L217) | P2 · 官方試點 | 相同版本、連線和輸出驗收後才收起；試點前使用原工具 |
| [`mechanical_suppress_bodies`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L271) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_tune_cfl_mesh`](../../src/ansys_unified_mcp/products/mechanical/tools.py#L713) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |

## Motor-CAD（2）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`motorcad_check_connection`](../../src/ansys_unified_mcp/products/motorcad/tools.py#L13) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`motorcad_solve_efficiency_point`](../../src/ansys_unified_mcp/products/motorcad/tools.py#L27) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |

## Optics（4）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`optics_check_connection`](../../src/ansys_unified_mcp/products/optics/tools.py#L14) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`optics_evaluate_speos_photometry`](../../src/ansys_unified_mcp/products/optics/tools.py#L92) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`optics_solve_lumerical_waveguide`](../../src/ansys_unified_mcp/products/optics/tools.py#L28) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`optics_trace_zemax_lens`](../../src/ansys_unified_mcp/products/optics/tools.py#L60) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |

## optiSLang（6）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`optislang_connect`](../../src/ansys_unified_mcp/products/optislang/tools.py#L20) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`optislang_disconnect`](../../src/ansys_unified_mcp/products/optislang/tools.py#L64) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`optislang_get_version`](../../src/ansys_unified_mcp/products/optislang/tools.py#L34) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`optislang_run_script`](../../src/ansys_unified_mcp/products/optislang/tools.py#L42) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`optislang_setup_mop`](../../src/ansys_unified_mcp/products/optislang/tools.py#L74) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`optislang_start_project`](../../src/ansys_unified_mcp/products/optislang/tools.py#L58) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |

## Rocky（2）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`rocky_check_connection`](../../src/ansys_unified_mcp/products/rocky/tools.py#L13) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`rocky_solve`](../../src/ansys_unified_mcp/products/rocky/tools.py#L27) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |

## Sherlock（3）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`sherlock_check_connection`](../../src/ansys_unified_mcp/products/sherlock/tools.py#L13) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`sherlock_run_thermal_fatigue_life`](../../src/ansys_unified_mcp/products/sherlock/tools.py#L27) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`sherlock_run_vibration_life`](../../src/ansys_unified_mcp/products/sherlock/tools.py#L65) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |

## Systems（3）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`systems_check_connection`](../../src/ansys_unified_mcp/products/systems/tools.py#L13) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`systems_run_twin_rom`](../../src/ansys_unified_mcp/products/systems/tools.py#L65) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |
| [`systems_solve_coupling_cht`](../../src/ansys_unified_mcp/products/systems/tools.py#L27) | P0 · 標記後端 | 預設按需；查核是否真實、基準或不可用 |

## Workbench（含 CFX 等）（44）

| 工具 | 建議處置 | 上線方式 |
| --- | --- | --- |
| [`check_workbench_connection`](../../src/ansys_unified_mcp/products/workbench/tools.py#L128) | P1 · 保留 | 日常或相關產品公開 |
| [`create_and_run_thermal_bar_demo`](../../src/ansys_unified_mcp/products/workbench/tools.py#L958) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`create_cfx_flow_system_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L537) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`create_fluent_flow_system_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L557) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`create_harmonic_response_system_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L477) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`create_modal_analysis_system_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L457) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`create_random_vibration_system_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L517) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`create_response_spectrum_system_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L497) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`create_static_structural_system_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L417) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`create_steady_state_thermal_system`](../../src/ansys_unified_mcp/products/workbench/tools.py#L728) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`create_steady_state_thermal_system_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L377) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`create_thermal_bar_demo_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L577) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`create_transient_structural_system_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L437) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`create_transient_thermal_system_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L397) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`create_workbench_analysis_system`](../../src/ansys_unified_mcp/products/workbench/tools.py#L612) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`create_workbench_analysis_system_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L340) | P3 · Skill 主導 | Skill 管規則與步驟；工具或版本化腳本按需呼叫 |
| [`execute_mechanical_script_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L196) | P1 · 保留 | 日常或相關產品公開 |
| [`execute_spaceclaim_script_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L153) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`execute_workbench_script`](../../src/ansys_unified_mcp/products/workbench/tools.py#L146) | P1 · 保留 | 日常或相關產品公開 |
| [`get_project_info`](../../src/ansys_unified_mcp/products/workbench/tools.py#L296) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`mechanical_run_batch_script`](../../src/ansys_unified_mcp/products/workbench/tools.py#L1087) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`open_project`](../../src/ansys_unified_mcp/products/workbench/tools.py#L303) | P1 · 保留 | 日常或相關產品公開 |
| [`probe_workbench_analysis_templates_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L329) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`run_cfx_solver`](../../src/ansys_unified_mcp/products/workbench/tools.py#L912) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`run_fluent_journal`](../../src/ansys_unified_mcp/products/workbench/tools.py#L851) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`run_mapdl_input`](../../src/ansys_unified_mcp/products/workbench/tools.py#L814) | P4 · 官方候選 | 留在相容模式；有工作負載後比較官方 |
| [`run_workbench_journal`](../../src/ansys_unified_mcp/products/workbench/tools.py#L587) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`save_project`](../../src/ansys_unified_mcp/products/workbench/tools.py#L310) | P1 · 保留 | 日常或相關產品公開 |
| [`start_workbench_bridge`](../../src/ansys_unified_mcp/products/workbench/tools.py#L56) | P1 · 保留 | 日常或相關產品公開 |
| [`stop_workbench_bridge`](../../src/ansys_unified_mcp/products/workbench/tools.py#L108) | P1 · 保留 | 日常或相關產品公開 |
| [`update_project`](../../src/ansys_unified_mcp/products/workbench/tools.py#L322) | P1 · 保留 | 日常或相關產品公開 |
| [`workbench_connect_server`](../../src/ansys_unified_mcp/products/workbench/tools.py#L1150) | P1 · 保留 | 日常或相關產品公開 |
| [`workbench_detect_environment`](../../src/ansys_unified_mcp/products/workbench/tools.py#L1070) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`workbench_disconnect_server`](../../src/ansys_unified_mcp/products/workbench/tools.py#L1195) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`workbench_download_archive`](../../src/ansys_unified_mcp/products/workbench/tools.py#L1189) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`workbench_get_job_log`](../../src/ansys_unified_mcp/products/workbench/tools.py#L1111) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`workbench_get_job_status`](../../src/ansys_unified_mcp/products/workbench/tools.py#L1105) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`workbench_launch_server`](../../src/ansys_unified_mcp/products/workbench/tools.py#L1123) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`workbench_list_jobs`](../../src/ansys_unified_mcp/products/workbench/tools.py#L1117) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`workbench_run_journal`](../../src/ansys_unified_mcp/products/workbench/tools.py#L1076) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`workbench_run_script_live`](../../src/ansys_unified_mcp/products/workbench/tools.py#L1161) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |
| [`workbench_server_status`](../../src/ansys_unified_mcp/products/workbench/tools.py#L1201) | P1 · 保留 | 日常或相關產品公開 |
| [`workbench_start_mechanical_server`](../../src/ansys_unified_mcp/products/workbench/tools.py#L1174) | P1 · 保留 | 日常或相關產品公開 |
| [`workbench_upload_file`](../../src/ansys_unified_mcp/products/workbench/tools.py#L1183) | P3 · 按需 | 按產品或任務公開；確認使用量與能力後再收斂 |

## 儲存庫內的 Skill（49）

以下為 `agents/skills` 的 49 個 `SKILL.md`，與 Git 追蹤數相符。用途分類依技能路徑與現有技能索引，更新欄是提案。這份清冊不把全域重複安裝或 Skill 附件算作新的專案 Skill。

| Skill | 分類目錄 | 建議處置 |
| --- | --- | --- |
| [`ansys-midsurface`](../../agents/skills/ansys-midsurface/SKILL.md) | ansys-midsurface | P3 優先更新：分開操作步驟、工具呼叫與驗收 |
| [`pr-review-zh`](../../agents/skills/development/pr-review-zh/SKILL.md) | development | 保留為開發審查技能 |
| [`ansys-electromagnetics`](../../agents/skills/domains/ansys-electromagnetics/SKILL.md) | domains | 保留領域分流，統一後端選擇與驗收入口 |
| [`ansys-fluids-cfd`](../../agents/skills/domains/ansys-fluids-cfd/SKILL.md) | domains | 保留領域分流，統一後端選擇與驗收入口 |
| [`ansys-geometry-meshing`](../../agents/skills/domains/ansys-geometry-meshing/SKILL.md) | domains | 保留領域分流，統一後端選擇與驗收入口 |
| [`ansys-materials-reliability`](../../agents/skills/domains/ansys-materials-reliability/SKILL.md) | domains | 保留領域分流，統一後端選擇與驗收入口 |
| [`ansys-mcp-foundation`](../../agents/skills/domains/ansys-mcp-foundation/SKILL.md) | domains | P1 優先更新：加上路由選擇、連線歸屬與可見性 |
| [`ansys-multibody-particles`](../../agents/skills/domains/ansys-multibody-particles/SKILL.md) | domains | 保留領域分流，統一後端選擇與驗收入口 |
| [`ansys-optical-engineering`](../../agents/skills/domains/ansys-optical-engineering/SKILL.md) | domains | 保留領域分流，統一後端選擇與驗收入口 |
| [`ansys-structural-mechanics`](../../agents/skills/domains/ansys-structural-mechanics/SKILL.md) | domains | 保留領域分流，統一後端選擇與驗收入口 |
| [`ansys-systems-coupling`](../../agents/skills/domains/ansys-systems-coupling/SKILL.md) | domains | 保留領域分流，統一後端選擇與驗收入口 |
| [`ansys-thermal-cooling`](../../agents/skills/domains/ansys-thermal-cooling/SKILL.md) | domains | 保留領域分流，統一後端選擇與驗收入口 |
| [`ansys-hfss`](../../agents/skills/electromagnetics/ansys-hfss/SKILL.md) | electromagnetics | P4 增列官方與自研入口選擇條件 |
| [`ansys-maxwell`](../../agents/skills/electromagnetics/ansys-maxwell/SKILL.md) | electromagnetics | P4 增列官方與自研入口選擇條件 |
| [`ansys-motorcad`](../../agents/skills/electromagnetics/ansys-motorcad/SKILL.md) | electromagnetics | P0 核對後端與授權前提；P3 補工程驗收 |
| [`ansys-q3d-siwave`](../../agents/skills/electromagnetics/ansys-q3d-siwave/SKILL.md) | electromagnetics | P4 增列官方與自研入口選擇條件 |
| [`ansys-cfx`](../../agents/skills/fluids-cfd/ansys-cfx/SKILL.md) | fluids-cfd | P4 增列官方與自研入口選擇條件 |
| [`ansys-chemkin`](../../agents/skills/fluids-cfd/ansys-chemkin/SKILL.md) | fluids-cfd | P0 核對後端與授權前提；P3 補工程驗收 |
| [`ansys-fluent`](../../agents/skills/fluids-cfd/ansys-fluent/SKILL.md) | fluids-cfd | P4 增列官方與自研入口選擇條件 |
| [`ansys-polyflow-icing`](../../agents/skills/fluids-cfd/ansys-polyflow-icing/SKILL.md) | fluids-cfd | 保留為產品操作與案例參考，校對目前入口 |
| [`act-extension-development`](../../agents/skills/geometry-meshing/act-extension-development/SKILL.md) | geometry-meshing | 保留為產品操作與案例參考，校對目前入口 |
| [`ansys-discovery`](../../agents/skills/geometry-meshing/ansys-discovery/SKILL.md) | geometry-meshing | 保留為產品操作與案例參考，校對目前入口 |
| [`ansys-mesh`](../../agents/skills/geometry-meshing/ansys-mesh/SKILL.md) | geometry-meshing | 保留為產品操作與案例參考，校對目前入口 |
| [`ansys-spaceclaim`](../../agents/skills/geometry-meshing/ansys-spaceclaim/SKILL.md) | geometry-meshing | P3 優先更新：分開操作步驟、工具呼叫與驗收 |
| [`ansys-acp-granta`](../../agents/skills/materials-reliability/ansys-acp-granta/SKILL.md) | materials-reliability | P0 核對後端與授權前提；P3 補工程驗收 |
| [`ansys-sherlock`](../../agents/skills/materials-reliability/ansys-sherlock/SKILL.md) | materials-reliability | P0 核對後端與授權前提；P3 補工程驗收 |
| [`pcb-warpage-analysis`](../../agents/skills/materials-reliability/pcb-warpage-analysis/SKILL.md) | materials-reliability | 保留為產品操作與案例參考，校對目前入口 |
| [`ansys-error-catalog`](../../agents/skills/mcp-foundation/ansys-error-catalog/SKILL.md) | mcp-foundation | 保留為產品操作與案例參考，校對目前入口 |
| [`ansys-motion`](../../agents/skills/multibody-particles/ansys-motion/SKILL.md) | multibody-particles | 保留為產品操作與案例參考，校對目前入口 |
| [`ansys-rocky-dem`](../../agents/skills/multibody-particles/ansys-rocky-dem/SKILL.md) | multibody-particles | P0 核對後端與授權前提；P3 補工程驗收 |
| [`ansys-aqwa-sound`](../../agents/skills/multiphysics/ansys-aqwa-sound/SKILL.md) | multiphysics | P0 核對後端與授權前提；P3 補工程驗收 |
| [`ansys-lumerical`](../../agents/skills/optical-engineering/ansys-lumerical/SKILL.md) | optical-engineering | P4 增列官方與自研入口選擇條件 |
| [`ansys-speos`](../../agents/skills/optical-engineering/ansys-speos/SKILL.md) | optical-engineering | P0 核對後端與授權前提；P3 補工程驗收 |
| [`ansys-zemax`](../../agents/skills/optical-engineering/ansys-zemax/SKILL.md) | optical-engineering | P0 核對後端與授權前提；P3 補工程驗收 |
| [`ansys-simai`](../../agents/skills/optimization-surrogates/ansys-simai/SKILL.md) | optimization-surrogates | 保留為產品操作與案例參考，校對目前入口 |
| [`ansys-ls-prepost`](../../agents/skills/structural-mechanics/ansys-ls-prepost/SKILL.md) | structural-mechanics | 保留為產品操作與案例參考，校對目前入口 |
| [`ansys-lsdyna`](../../agents/skills/structural-mechanics/ansys-lsdyna/SKILL.md) | structural-mechanics | 保留為產品操作與案例參考，校對目前入口 |
| [`ansys-mapdl`](../../agents/skills/structural-mechanics/ansys-mapdl/SKILL.md) | structural-mechanics | P4 增列官方與自研入口選擇條件 |
| [`ansys-mechanical`](../../agents/skills/structural-mechanics/ansys-mechanical/SKILL.md) | structural-mechanics | P3 優先更新：分開操作步驟、工具呼叫與驗收 |
| [`ansys-random-vibration`](../../agents/skills/structural-mechanics/ansys-random-vibration/SKILL.md) | structural-mechanics | P3 優先更新：分開操作步驟、工具呼叫與驗收 |
| [`ansys-submodeling-dpf`](../../agents/skills/structural-mechanics/ansys-submodeling-dpf/SKILL.md) | structural-mechanics | P3 優先更新：分開操作步驟、工具呼叫與驗收 |
| [`pymechanical-operations`](../../agents/skills/structural-mechanics/pymechanical-operations/SKILL.md) | structural-mechanics | P3 優先更新：分開操作步驟、工具呼叫與驗收 |
| [`shock-analysis-workflow`](../../agents/skills/structural-mechanics/shock-analysis-workflow/SKILL.md) | structural-mechanics | P3 優先更新：分開操作步驟、工具呼叫與驗收 |
| [`ansys-optislang`](../../agents/skills/systems-coupling/ansys-optislang/SKILL.md) | systems-coupling | P3 優先更新：分開操作步驟、工具呼叫與驗收 |
| [`ansys-system-coupling`](../../agents/skills/systems-coupling/ansys-system-coupling/SKILL.md) | systems-coupling | P0 核對後端與授權前提；P3 補工程驗收 |
| [`ansys-twin-scade`](../../agents/skills/systems-coupling/ansys-twin-scade/SKILL.md) | systems-coupling | P0 核對後端與授權前提；P3 補工程驗收 |
| [`ansys-workbench`](../../agents/skills/systems-coupling/ansys-workbench/SKILL.md) | systems-coupling | P3 優先更新：分開操作步驟、工具呼叫與驗收 |
| [`ansys-icepak`](../../agents/skills/thermal-cooling/ansys-icepak/SKILL.md) | thermal-cooling | P0 核對後端與授權前提；P3 補工程驗收 |
| [`ansys-thermal-analysis`](../../agents/skills/thermal-cooling/ansys-thermal-analysis/SKILL.md) | thermal-cooling | 保留為產品操作與案例參考，校對目前入口 |
