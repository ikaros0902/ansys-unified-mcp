"""共用 DPF 服務端摘要；只有縮減後的純量會傳回客戶端。"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def release_streams(model):
    """釋放失敗不得遮蔽原始解析錯誤。"""
    if model is not None:
        try:
            model.metadata.release_streams()
        except Exception as exc:
            logger.warning("DPF release_streams 失敗: %s", exc)


def _reduce(dpf, fc, scales):
    records = []
    for index in range(len(fc)):
        field = fc[index]
        count = field.elementary_data_count
        if not count:
            continue
        if field.unit not in scales:
            raise ValueError(f"Unknown DPF unit: {field.unit!r}")
        factor = scales[field.unit]
        extrema = dpf.operators.min_max.min_max(field=field, server=field._server)
        total = dpf.operators.math.accumulate(fieldA=field, server=field._server)
        records.append({
            "min": float(extrema.outputs.field_min().data[0]) * factor,
            "max": float(extrema.outputs.field_max().data[0]) * factor,
            "sum": float(total.outputs.field().data[0]) * factor,
            "count": count,
            "set_id": fc.get_label_space(index).get("time"),
            "location": field.location,
        })
    if not records:
        return {"status": "empty", "min": None, "max": None, "avg": None,
                "set_ids": [], "locations": []}
    return {
        "status": "available",
        "min": min(r["min"] for r in records),
        "max": max(r["max"] for r in records),
        "avg": sum(r["sum"] for r in records) / sum(r["count"] for r in records),
        "set_ids": sorted({r["set_id"] for r in records if r["set_id"] is not None}),
        "locations": sorted({r["location"] for r in records}),
    }


def extract_summary(model, dpf):
    """摘要最後結果集，保留實際位置與結果集識別。"""
    available = {r.name for r in model.metadata.result_info.available_results}
    tfs = model.metadata.time_freq_support
    times = tfs.time_frequencies if tfs is not None else None
    set_ids = list(times.scoping.ids) if times is not None else []
    selection = {"time_scoping": [set_ids[-1]]} if set_ids else {}
    result = {}
    for name, native, unit, scales in (
        ("stress_von_mises", "stress", "Pa", {"Pa": 1.0, "MPa": 1e6}),
        ("displacement", "displacement", "m", {"m": 1.0, "mm": 1e-3}),
    ):
        if native not in available:
            result[name] = {"status": "missing", "unit": unit, "max": None,
                            "min": None, "avg": None, "set_ids": [], "locations": []}
            continue
        op = getattr(model.results, native)(**selection)
        fc = op.outputs.fields_container()
        if native == "stress":
            fc = dpf.operators.invariant.von_mises_eqv_fc(
                fields_container=fc, server=model._server
            ).outputs.fields_container()
        else:
            vectors = fc
            fc = dpf.operators.math.norm_fc(
                fields_container=fc, server=model._server
            ).outputs.fields_container()
        summary = _reduce(dpf, fc, scales)
        summary["unit"] = unit
        if native == "displacement":
            summary["total_max"] = summary["max"]
            for component, key in enumerate(("ux_max", "uy_max", "uz_max")):
                selected = dpf.operators.logic.component_selector_fc(
                    fields_container=vectors, component_number=component, server=model._server
                ).outputs.fields_container()
                bounds = _reduce(dpf, selected, scales)
                summary[key] = (max(abs(bounds["min"]), abs(bounds["max"]))
                                if bounds["status"] == "available" else None)
        result[name] = summary
    result["displacement"].setdefault("total_max", None)
    result["time_freq_sets"] = [float(v) for v in times.data] if times is not None else []
    if result["time_freq_sets"]:
        result["modal"] = {"frequencies": result["time_freq_sets"]}
    return result
