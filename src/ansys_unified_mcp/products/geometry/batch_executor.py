"""SpaceClaim / Geometry 批次執行模式 (Batch Executor).

對同一個已連線的 Geometry（SpaceClaim / Discovery）gRPC session，依序批次執行
多個幾何操作（create_block、create_enclosure、export 等），並將逐步結果聚合
為單一回傳信封，省去呼叫端逐一處理每個工具呼叫的往返開銷。

設計原則（不重寫 gRPC）：
- 不建立新的連線邏輯，直接委派既有 products/geometry/call_dispatch.py 的 call_tool() 分派器。
- call_tool() 內部已統一捕捉例外並回傳純字串（成功或 "錯誤 [...]: ..." 開頭），
  本模組透過 shared.looks_like_error() 沿用既有的失敗標記判定慣例，
  不另行定義判斷規則，避免與既有 as_envelope() 行為產生分歧。
- 單步失敗不中斷整批，predetermined 之後續步驟仍會嘗試執行，
  最終信封同時回報哪些步驟成功、哪些失敗，供呼叫端自行決定是否重試。

成敗判定補強（避免漏報失敗）：
- geometry_* 分支在 session 未連線或無作用中設計時，會回傳不含任何
  shared._ERROR_MARKERS 標記的純提示字串（例如「Geometry 未連線，請先執行
  geometry_launch」、「無法取得 SpaceClaim 當前作用中設計」），導致
  looks_like_error() 誤判為成功。這類前置條件缺失訊息為 call_dispatch.py 既有、
  穩定的字面文案，本模組在此額外攔截，避免整批對未連線 session 的操作
  被全數回報為「成功」的假性成功信封。
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from ansys_unified_mcp.products.geometry import call_dispatch as sim_impl
from ansys_unified_mcp.shared import looks_like_error

logger = logging.getLogger("ansys-unified-mcp.geometry.batch_executor")

# call_dispatch.py 既有的「前置條件缺失」短路提示文案，不含任何 _ERROR_MARKERS 標記，
# 但實質代表該步驟並未真正執行（漏報失敗風險），批次執行須額外攔截為失敗。
_PRECONDITION_FAILURE_MARKERS: tuple[str, ...] = (
    "geometry 未連線，請先執行 geometry_launch",
    "無法取得 spaceclaim 當前作用中設計",
)


def _is_step_failure(text: str) -> bool:
    """判定單步結果字串是否代表失敗，涵蓋既有錯誤標記與 geometry 前置條件缺失訊息。"""
    if looks_like_error(text):
        return True
    lowered = (text or "").lower()
    return any(marker in lowered for marker in _PRECONDITION_FAILURE_MARKERS)


async def execute_batch(
    operations: List[Dict[str, Any]],
    stop_on_error: bool = False,
) -> Dict[str, Any]:
    """依序批次執行多個 geometry 操作於同一 Geometry session。

    :param operations: 操作清單，每筆格式為 ``{"operation": <工具名稱>, "args": {...}}``。
        工具名稱須為 products/geometry/call_dispatch.call_tool 已支援的 geometry_* 名稱
        （例如 geometry_create_block、geometry_create_enclosure、geometry_export）。
    :param stop_on_error: 若為 True，遇到第一個失敗步驟即中止後續操作；
        預設 False（寬容執行，蒐集所有步驟結果後一次回報）。
    :return: 聚合結果信封：
        ``{"ok": bool, "batch_id": str, "total_operations": int,
           "succeeded": int, "failed": int, "results": [...],
           "execution_time_ms": float}``
    """
    batch_id = str(uuid.uuid4())
    results: List[Dict[str, Any]] = []
    succeeded = 0
    failed = 0

    if not operations:
        return {
            "ok": True,
            "batch_id": batch_id,
            "total_operations": 0,
            "succeeded": 0,
            "failed": 0,
            "results": [],
            "execution_time_ms": 0.0,
            "note": "操作清單為空，無任何步驟執行。",
        }

    start = time.perf_counter()

    for step_index, op in enumerate(operations, start=1):
        op_name = op.get("operation")
        op_args = op.get("args") or {}

        if not op_name:
            results.append(
                {
                    "step": step_index,
                    "operation": op_name,
                    "ok": False,
                    "error": "操作項目缺少 'operation' 欄位。",
                }
            )
            failed += 1
            if stop_on_error:
                break
            continue

        try:
            # 委派既有分派器，不重寫 gRPC 連線邏輯。
            content_list = await sim_impl.call_tool(op_name, op_args)
            text = "\n".join(c.text for c in content_list) if content_list else ""
            step_ok = not _is_step_failure(text)
        except Exception as exc:  # noqa: BLE001 - 批次執行須隔離單步例外，不中斷整批
            logger.exception(f"批次第 {step_index} 步 [{op_name}] 執行發生未捕捉例外")
            text = str(exc)
            step_ok = False

        results.append(
            {
                "step": step_index,
                "operation": op_name,
                "ok": step_ok,
                "result": text,
            }
        )

        if step_ok:
            succeeded += 1
        else:
            failed += 1
            if stop_on_error:
                break

    elapsed_ms = (time.perf_counter() - start) * 1000.0

    return {
        "ok": failed == 0,
        "batch_id": batch_id,
        "total_operations": len(operations),
        "succeeded": succeeded,
        "failed": failed,
        "results": results,
        "execution_time_ms": round(elapsed_ms, 2),
    }
