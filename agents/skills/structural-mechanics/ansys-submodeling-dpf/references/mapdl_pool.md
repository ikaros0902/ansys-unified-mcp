# MAPDL 併發求解池實作指引 (mapdl_pool.md)

本手冊說明如何使用 `ansys.mapdl.core.LocalMapdlPool` 併發啟動多個 MAPDL 求解實例，平行施加切面邊界約束並求解局部細緻子模型。

---

## 一、多進程求解池架構

```python
# ==============================================================================
# 功能描述: 使用 LocalMapdlPool 併發執行多個子模型切面約束施加與結構求解
# 執行環境: Python 3.10+ (ansys-mapdl-core)
# ==============================================================================

import os
from ansys.mapdl.core import LocalMapdlPool

def solve_submodels_in_pool(submodel_tasks, n_instances=4, working_dir="C:/Temp/SubmodelPool"):
    """使用 MAPDL 併發進程池平行求解多個局部子模型。
    
    參數:
        submodel_tasks (list): 任務設定列表，每項包含 cdb_path 與 cut_bcs 字典。
        n_instances (int): 併發啟動的 MAPDL 進程實例數量。
        working_dir (str): 平行運算基礎工作目錄。
    """
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    pool = LocalMapdlPool(
        n_instances=n_instances,
        run_location=working_dir,
        cleanup_on_exit=False,
        verbose=False
    )

    def _run_single_submodel(mapdl, task):
        sub_name = task["submodel_name"]
        cdb_path = task["cdb_path"]
        cut_bcs = task["cut_bcs"]  # {node_id: [ux, uy, uz]}

        mapdl.clear()
        mapdl.prep7()
        mapdl.cdread("DB", cdb_path)

        for nid, (ux, uy, uz) in cut_bcs.items():
            mapdl.d(nid, "UX", ux)
            mapdl.d(nid, "UY", uy)
            mapdl.d(nid, "UZ", uz)

        mapdl.finish()
        mapdl.slashsolu()
        mapdl.antype("STATIC")
        mapdl.solve()
        mapdl.finish()

        mapdl.post1()
        mapdl.set("LAST")
        max_eqv = mapdl.get_value("NODE", 0, "S", "EQV")
        
        rst_path = os.path.join(mapdl.directory, "file.rst")
        return {"submodel": sub_name, "max_stress_eqv": max_eqv, "rst_path": rst_path}

    try:
        results = pool.map(_run_single_submodel, submodel_tasks)
        return results
    finally:
        pool.exit()
```
