## 宿主腳本唯一來源

內嵌腳本以 `src/ansys_unified_mcp/products/` 為唯一維護來源；技能中的歷史副本不可當執行來源或另行修改。CPython／MCP 端以 `core.resources.load_embedded_script(product, name) -> str` 讀原文，或讀取白名單 MCP resource `ansys-script://{product}/{name}`，再將字串交給對應宿主執行器。ACT／SCDM 宿主不能 import `ansys_unified_mcp` 套件；宿主只接收原文與該腳本既有參數，保留校驗與錯誤處理。讀取資源本身不授權模型修改或求解。

| product | name | 唯一來源 |
|---|---|---|
| mechanical | material_assignment_engine | products/mechanical/plugins/material_assignment_engine.py |
| mechanical | rm_joint_creator | products/mechanical/plugins/rm_joint_creator.py |
| geometry | defeature | products/geometry/spaceclaim_scripts/defeature.ironpy |
| geometry | imprint_contacts | products/geometry/spaceclaim_scripts/imprint_contacts.ironpy |
| geometry | midsurface | products/geometry/spaceclaim_scripts/midsurface.ironpy |
| geometry | rm_group | products/geometry/spaceclaim_scripts/rm_group.ironpy |

