# DPF 高速場數據提取與形函數空間插值 (dpf_interpolation.md)

本手冊說明如何使用 PyAnsys DPF (`ansys.dpf.core`) 進行結果場串流提取與有限元形函數空間座標插值 (`on_coordinates`)。

---

## 一、DPF 高速結果場提取 (Displacement & Von-Mises Stress)

```python
# ==============================================================================
# 功能描述: 使用 PyAnsys DPF 毫秒級流式提取位移場與 Von-Mises 等效應力極值
# 執行環境: Python 3.10+ (ansys-dpf-core)
# ==============================================================================

import os
from ansys.dpf import core as dpf

def extract_field_results(rst_file_path, time_step_index=1):
    """讀取 RST 結果檔並高速提取位移場與等效應力場。"""
    if not os.path.exists(rst_file_path):
        raise FileNotFoundError(f"找不到指定的 RST 檔案: {rst_file_path}")

    # 1. 建立 DPF 資料來源並載入模型
    data_sources = dpf.DataSources(rst_file_path)
    model = dpf.Model(data_sources)
    mesh = model.metadata.meshed_region

    # 2. 建立位移算子
    disp_op = dpf.operators.result.displacement(data_sources=data_sources)
    disp_op.inputs.time_scoping.connect([time_step_index])
    disp_fields_container = disp_op.outputs.fields_container()

    # 計算全場最大位移合量 (Norm)
    norm_op = dpf.operators.math.norm_fc(fields_container=disp_fields_container)
    disp_norm_field = norm_op.outputs.fields_container()[0]
    max_disp_val = max(disp_norm_field.data)

    # 3. 建立 Von-Mises 應力算子 (節點平均化)
    stress_op = dpf.operators.result.stress_von_mises(
        data_sources=data_sources,
        requested_location=dpf.locations.nodal
    )
    stress_op.inputs.time_scoping.connect([time_step_index])
    stress_fields_container = stress_op.outputs.fields_container()

    min_max_op = dpf.operators.min_max.min_max_fc(fields_container=stress_fields_container)
    max_stress_val = min_max_op.outputs.field_max().data[0]

    return {
        "model": model,
        "mesh": mesh,
        "displacement_fc": disp_fields_container,
        "stress_fc": stress_fields_container,
        "max_displacement": float(max_disp_val),
        "max_stress_pa": float(max_stress_val)
    }
```

---

## 二、有限元形函數空間場插值器 (`dpf.operators.mapping.on_coordinates`)

在全域-局部子模型方法中，子模型邊界切面上的節點密度遠高於粗網格全域模型。透過 DPF 的 `mapping.on_coordinates`，可直接讀取全域有限元模型的形函數幾何矩陣，將全域位移場精確內插至子模型的切面節點上。

```python
import numpy as np
from ansys.dpf import core as dpf

def interpolate_cut_boundary_displacements(global_rst_path, cut_node_coords_dict):
    """將全域模型位移場精確插值至子模型切面節點。
    
    參數:
        global_rst_path (str): 全域粗網格模型結果檔路徑。
        cut_node_coords_dict (dict): 子模型切面邊界節點字典 {node_id: [x, y, z]}。
        
    傳回:
        dict: 各切面節點插值位移向量 {node_id: [ux, uy, uz]}。
    """
    data_sources = dpf.DataSources(global_rst_path)
    global_model = dpf.Model(data_sources)
    global_mesh = global_model.metadata.meshed_region

    disp_op = dpf.operators.result.displacement(data_sources=data_sources)
    global_disp_fc = disp_op.outputs.fields_container()

    node_ids = list(cut_node_coords_dict.keys())
    coords_list = [cut_node_coords_dict[nid] for nid in node_ids]

    target_coords_field = dpf.fields_factory.create_3d_vector_field(
        num_entities=len(node_ids),
        location=dpf.locations.nodal
    )
    target_coords_field.scoping.ids = node_ids
    target_coords_field.data = np.array(coords_list, dtype=np.float64)

    # 調用有限元空間形函數映射算子
    mapping_op = dpf.operators.mapping.on_coordinates(
        fields_container=global_disp_fc,
        coordinates=target_coords_field,
        mesh=global_mesh
    )
    interpolated_field = mapping_op.outputs.fields_container()[0]

    interpolated_results = {}
    for i, nid in enumerate(node_ids):
        ux, uy, uz = interpolated_field.data[i]
        interpolated_results[nid] = [float(ux), float(uy), float(uz)]

    return interpolated_results
```
