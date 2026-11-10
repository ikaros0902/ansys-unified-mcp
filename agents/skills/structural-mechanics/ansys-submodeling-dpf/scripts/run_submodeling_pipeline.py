"""
完整端到端子模型 (Submodeling) 與 DPF 自動化流程示範腳本。
執行環境: Python 3.10+ (需安裝 ansys-dpf-core 與 ansys-mapdl-core)
"""

import os
import numpy as np
from ansys.dpf import core as dpf
from ansys.mapdl.core import launch_mapdl

def run_full_submodeling_workflow(config):
    """執行完整端到端子模型自動化流程。"""
    global_rst = config["global_rst"]
    submodel_cdb = config["submodel_cdb"]
    submodel_work_dir = config.get("submodel_work_dir", "C:/Temp/Submodel_Run")
    cut_node_coords = config["cut_node_coords"]

    if not os.path.exists(submodel_work_dir):
        os.makedirs(submodel_work_dir)

    # 1. DPF 提取並插值
    global_data = dpf.DataSources(global_rst)
    global_model = dpf.Model(global_data)
    disp_op = dpf.operators.result.displacement(data_sources=global_data)
    global_disp_fc = disp_op.outputs.fields_container()

    node_ids = list(cut_node_coords.keys())
    coords_array = np.array([cut_node_coords[nid] for nid in node_ids], dtype=np.float64)

    target_field = dpf.fields_factory.create_3d_vector_field(len(node_ids), dpf.locations.nodal)
    target_field.scoping.ids = node_ids
    target_field.data = coords_array

    interp_op = dpf.operators.mapping.on_coordinates(
        fields_container=global_disp_fc,
        coordinates=target_field,
        mesh=global_model.metadata.meshed_region
    )
    cut_bcs_field = interp_op.outputs.fields_container()[0]

    # 2. MAPDL 求解子模型
    mapdl = launch_mapdl(run_location=submodel_work_dir, verbose=False)
    try:
        mapdl.clear()
        mapdl.prep7()
        mapdl.cdread("DB", submodel_cdb)

        for i, nid in enumerate(node_ids):
            ux, uy, uz = cut_bcs_field.data[i]
            mapdl.d(nid, "UX", float(ux))
            mapdl.d(nid, "UY", float(uy))
            mapdl.d(nid, "UZ", float(uz))

        mapdl.finish()
        mapdl.slashsolu()
        mapdl.antype("STATIC")
        mapdl.solve()
        mapdl.finish()
    finally:
        mapdl.exit()

    # 3. 聖維南連續性驗證
    submodel_rst = os.path.join(submodel_work_dir, "file.rst")
    sub_data = dpf.DataSources(submodel_rst)
    s_stress_op = dpf.operators.result.stress_von_mises(data_sources=sub_data, requested_location=dpf.locations.nodal)
    s_field = s_stress_op.outputs.fields_container()[0]

    g_stress_op = dpf.operators.result.stress_von_mises(data_sources=global_data, requested_location=dpf.locations.nodal)
    g_field = g_stress_op.outputs.fields_container()[0]
    peak_stress = max(g_field.data)

    diffs = []
    for nid in node_ids:
        try:
            s_val = s_field.get_entity_data_by_id(nid)[0]
            g_val = g_field.get_entity_data_by_id(nid)[0]
            diffs.append(abs(s_val - g_val) / peak_stress * 100.0)
        except Exception:
            continue

    max_err = float(np.max(diffs)) if diffs else 0.0
    return {
        "max_boundary_error_percent": max_err,
        "is_passed": max_err <= config.get("tolerance", 10.0),
        "submodel_rst": submodel_rst
    }
