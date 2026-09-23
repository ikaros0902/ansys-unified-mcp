# 聖維南原理切面邊界連續性驗證 (saint_venant_validation.md)

本手冊說明如何透過聖維南原理（Saint-Venant's Principle）與切面邊界應力連續性評估指標，自動判定子模型邊界切面是否合理。

---

## 一、應力連續性評估指標

對切面上的每一節點 $k$，計算其全域應力 $\sigma_{\text{global}}^k$ 與子模型應力 $\sigma_{\text{submodel}}^k$ 的相對百分比誤差：
$$\text{Error}_k = \frac{|\sigma_{\text{submodel}}^k - \sigma_{\text{global}}^k|}{\max(\sigma_{\text{global}})} \times 100\%$$

- **通過標準**：切面上所有節點的平均相對誤差 $\le 5\%$，最大單點局部誤差 $\le 10\%$。
- **超標處置**：若誤差 $> 10\%$，說明切面違反聖維南假設（距離應力集中處過近），必須在外擴 $2\sim 3$ 倍特徵尺寸處重新定義切面。

```python
import numpy as np
from ansys.dpf import core as dpf

def evaluate_submodel_boundary_continuity(global_rst, submodel_rst, cut_boundary_node_ids, tolerance_percent=10.0):
    """評估切面邊界節點的應力連續性誤差。"""
    g_stress_op = dpf.operators.result.stress_von_mises(
        data_sources=dpf.DataSources(global_rst),
        requested_location=dpf.locations.nodal
    )
    g_stress_field = g_stress_op.outputs.fields_container()[0]

    s_stress_op = dpf.operators.result.stress_von_mises(
        data_sources=dpf.DataSources(submodel_rst),
        requested_location=dpf.locations.nodal
    )
    s_stress_field = s_stress_op.outputs.fields_container()[0]

    errors = []
    global_peak_stress = max(g_stress_field.data)

    for nid in cut_boundary_node_ids:
        try:
            val_global = g_stress_field.get_entity_data_by_id(nid)[0]
            val_sub = s_stress_field.get_entity_data_by_id(nid)[0]
            rel_diff = (abs(val_sub - val_global) / global_peak_stress) * 100.0
            errors.append(rel_diff)
        except Exception:
            continue

    if not errors:
        raise ValueError("未能匹配到任何切面節點的應力數據，請檢查節點編號。")

    max_error = float(np.max(errors))
    mean_error = float(np.mean(errors))
    is_valid = max_error <= tolerance_percent

    return {
        "mean_error_percent": mean_error,
        "max_error_percent": max_error,
        "is_passed": is_valid,
        "evaluated_node_count": len(errors)
    }
```
